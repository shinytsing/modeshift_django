"""HTTP API for chaining generated test cases into safe automation."""

from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .test_execution_manager import TestExecutionManager
from .services.test_execution_service import ExecutionPlanError


def _requester_id(request, create_session: bool = False) -> str:
    if request.user.is_authenticated:
        return f"user:{request.user.pk}"
    if create_session and not request.session.session_key:
        request.session.create()
    return f"anonymous:{request.session.session_key or ''}"


def _serialize_task(task: dict) -> dict:
    response = {
        "success": True,
        "execution_id": task["id"],
        "status": task["status"],
        "progress": task.get("progress", 0),
        "current_step": task.get("current_step"),
        "target_url": task.get("target_url"),
        "mode": task.get("mode"),
        "source_channel": task.get("source_channel"),
        "model_id": task.get("model_id"),
        "max_cases": task.get("max_cases"),
        "allow_mutations": task.get("allow_mutations", False),
        "plan_summary": task.get("plan_summary"),
        "created_at": task.get("created_at"),
        "started_at": task.get("started_at"),
        "completed_at": task.get("completed_at"),
    }
    if task.get("status") == "completed":
        response["report"] = task.get("report")
    if task.get("status") == "failed":
        response["error"] = task.get("error") or "自动化执行失败"
    return response


class ExecuteGeneratedTestCasesAPI(APIView):
    permission_classes = []

    def post(self, request):
        payload = request.data
        allow_mutations = payload.get("allow_mutations", False)
        if isinstance(allow_mutations, str):
            allow_mutations = allow_mutations.lower() in {"1", "true", "yes", "on"}
        try:
            source_channel = str(payload.get("source_channel", "")).strip().lower()
            mode = str(payload.get("mode", "")).strip().lower()
            if source_channel not in {"api", "ui"} or mode != source_channel:
                return Response(
                    {"success": False, "error": "只能从 API 或 UI 自动化工作区执行对应通道的用例"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cookie_names = {settings.SESSION_COOKIE_NAME, settings.CSRF_COOKIE_NAME}
            browser_cookies = {
                name: request.COOKIES[name]
                for name in cookie_names
                if name in request.COOKIES
            }
            task_id = TestExecutionManager().create_task(
                test_cases=str(payload.get("test_cases", "")),
                requirement=str(payload.get("requirement", "")),
                user_prompt=str(payload.get("prompt", "")),
                target_url=str(payload.get("target_url", "http://127.0.0.1:8081")),
                mode=mode,
                source_channel=source_channel,
                model_id=str(payload.get("model_id", "")),
                max_cases=int(payload.get("max_cases", 10)),
                allow_mutations=bool(allow_mutations),
                user_id=_requester_id(request, create_session=True),
                browser_cookies=browser_cookies,
            )
        except (ExecutionPlanError, ValueError) as exc:
            return Response({"success": False, "error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": True, "execution_id": task_id, "message": "自动化执行任务已创建"}, status=status.HTTP_202_ACCEPTED)


class ExecutionTaskStatusAPI(APIView):
    permission_classes = []

    def get(self, request, execution_id):
        task = TestExecutionManager().get_task(execution_id)
        if not task or task.get("user_id") != _requester_id(request):
            return Response({"success": False, "error": "执行任务不存在或无权访问"}, status=status.HTTP_404_NOT_FOUND)
        return Response(_serialize_task(task))


class StopExecutionTaskAPI(APIView):
    permission_classes = []

    def post(self, request, execution_id):
        requester_id = _requester_id(request)
        if not TestExecutionManager().cancel_task(execution_id, requester_id):
            return Response({"success": False, "error": "执行任务不存在、已结束或无权访问"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "message": "已请求停止自动化任务"})


class ExecutionArtifactAPI(APIView):
    """Serve a screenshot belonging to an execution task owned by the requester."""

    permission_classes = []
    allowed_suffixes = {".png", ".jpg", ".jpeg", ".webp"}

    def get(self, request, execution_id, filename):
        try:
            task_uuid = uuid.UUID(str(execution_id))
        except (TypeError, ValueError, AttributeError):
            return Response({"success": False, "error": "执行任务不存在"}, status=status.HTTP_404_NOT_FOUND)

        manager = TestExecutionManager()
        task = manager.get_task(str(task_uuid))
        if not task or task.get("user_id") != _requester_id(request):
            return Response({"success": False, "error": "执行任务不存在或无权访问"}, status=status.HTTP_404_NOT_FOUND)

        safe_name = Path(str(filename)).name
        if safe_name != str(filename) or Path(safe_name).suffix.lower() not in self.allowed_suffixes:
            return Response({"success": False, "error": "截图文件不存在"}, status=status.HTTP_404_NOT_FOUND)

        artifact = Path(manager.artifacts_dir) / str(task_uuid) / safe_name
        if not artifact.is_file():
            return Response({"success": False, "error": "截图文件不存在"}, status=status.HTTP_404_NOT_FOUND)
        content_type = mimetypes.guess_type(artifact.name)[0] or "application/octet-stream"
        return FileResponse(artifact.open("rb"), content_type=content_type)
