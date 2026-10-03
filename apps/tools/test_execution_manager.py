"""Background persistence and orchestration for generated-case execution."""

from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from datetime import datetime
from typing import Any

from .services.llm_service import get_llm_service
from .services.test_execution_service import ExecutionPlanError, build_execution_plan, execute_plan, normalize_target_url

logger = logging.getLogger(__name__)


class TestExecutionManager:
    """Run one generated test document in a durable, queryable background task."""

    def __init__(self) -> None:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.storage_dir = os.path.join(project_root, "task_storage")
        self.artifacts_dir = os.path.join(self.storage_dir, "executions")
        self.tasks_file = os.path.join(self.storage_dir, "execution_tasks.json")
        self.tasks: dict[str, dict[str, Any]] = {}
        # Runtime-only browser/API cookies. Never persist authentication material
        # in execution_tasks.json; the worker consumes and removes it once started.
        self.runtime_cookies: dict[str, dict[str, str]] = {}
        self.task_lock = threading.Lock()
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    self.tasks.update(loaded)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("加载自动化执行任务失败：%s", exc)

    def _save(self) -> None:
        temporary_file = f"{self.tasks_file}.tmp"
        with open(temporary_file, "w", encoding="utf-8") as handle:
            json.dump(self.tasks, handle, ensure_ascii=False, indent=2)
        os.replace(temporary_file, self.tasks_file)

    def create_task(
        self,
        *,
        test_cases: str,
        requirement: str,
        user_prompt: str,
        target_url: str,
        mode: str,
        source_channel: str,
        model_id: str,
        max_cases: int,
        allow_mutations: bool,
        user_id: str,
        browser_cookies: dict[str, str] | None = None,
    ) -> str:
        if not str(test_cases or "").strip():
            raise ExecutionPlanError("没有可执行的生成结果")
        if len(test_cases) > 100_000:
            raise ExecutionPlanError("生成结果过大，请先缩小用例范围")
        target = normalize_target_url(target_url)
        if mode not in {"api", "ui"} or source_channel != mode:
            raise ExecutionPlanError("执行通道必须是 API 或 UI，且只能执行当前通道文档")
        max_cases = max(1, min(int(max_cases or 10), 30))
        if not model_id:
            raise ExecutionPlanError("请先选择执行模型")
        get_llm_service().resolve_model(model_id)
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "user_id": user_id,
            "target_url": target,
            "mode": mode,
            "source_channel": source_channel,
            "model_id": model_id,
            "max_cases": max_cases,
            "allow_mutations": bool(allow_mutations),
            "test_cases": test_cases,
            "requirement": requirement,
            "user_prompt": user_prompt,
            "status": "pending",
            "progress": 0,
            "current_step": "等待执行",
            "plan_summary": None,
            "report": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
        }
        with self.task_lock:
            self.tasks[task_id] = task
            if browser_cookies:
                self.runtime_cookies[task_id] = {
                    str(name): str(value) for name, value in browser_cookies.items() if name and value
                }
            self._save()
        thread = threading.Thread(target=self._execute_task, args=(task_id,), daemon=True)
        thread.start()
        return task_id

    def _update(self, task_id: str, **updates: Any) -> None:
        with self.task_lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(updates)
                self._save()

    def _execute_task(self, task_id: str) -> None:
        try:
            with self.task_lock:
                task = self.tasks.get(task_id)
                if not task:
                    return
                task.update(
                    {
                        "status": "running",
                        "started_at": datetime.now().isoformat(),
                        "progress": 3,
                        "current_step": "让模型区分人工与自动化用例",
                    }
                )
                self._save()
            with self.task_lock:
                browser_cookies = self.runtime_cookies.pop(task_id, {})
            plan = build_execution_plan(
                task["test_cases"],
                task["target_url"],
                task["mode"],
                task["model_id"],
                task["max_cases"],
                requirement=task.get("requirement", ""),
                user_prompt=task.get("user_prompt", ""),
            )
            channel_counts = {
                channel: sum(case["channel"] == channel for case in plan["cases"]) for channel in ("api", "ui", "manual")
            }
            self._update(
                task_id,
                progress=10,
                current_step="执行自动化用例",
                plan_summary={"total": len(plan["cases"]), **channel_counts},
            )
            report = execute_plan(
                plan,
                task["allow_mutations"],
                os.path.join(self.artifacts_dir, task_id),
                progress_callback=lambda progress, step: self._update(
                    task_id, progress=10 + round(progress * 0.9), current_step=step
                ),
                browser_cookies=browser_cookies,
            )
            self._update(
                task_id,
                status="completed",
                progress=100,
                current_step="执行完成",
                report=report,
                completed_at=datetime.now().isoformat(),
            )
        except Exception as exc:
            logger.exception("自动化执行任务失败：%s", task_id)
            self._update(
                task_id, status="failed", current_step="执行失败", error=str(exc), completed_at=datetime.now().isoformat()
            )

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        self._load()
        with self.task_lock:
            task = self.tasks.get(task_id)
            return dict(task) if task else None

    def cancel_task(self, task_id: str, user_id: str) -> bool:
        with self.task_lock:
            task = self.tasks.get(task_id)
            if not task or task.get("user_id") != user_id or task.get("status") in {"completed", "failed", "cancelled"}:
                return False
            task.update({"status": "cancelled", "current_step": "用户已取消", "completed_at": datetime.now().isoformat()})
            self._save()
            return True
