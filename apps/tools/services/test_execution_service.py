"""Safe, declarative execution for LLM-generated test cases.

The LLM produces a JSON plan only. This module validates that plan and runs a
small allow-list of HTTP and Playwright actions; it never evaluates generated
Python or JavaScript.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from django.conf import settings

from .llm_service import get_llm_service

logger = logging.getLogger(__name__)

LOCAL_HOSTS = {"127.0.0.1", "localhost", "host.docker.internal"}
ALLOWED_HTTP_METHODS = {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"}
SAFE_POST_PATHS = {
    "/tools/api/fitness/bmi/",
    "/tools/api/fitness/heart-rate/",
    "/tools/api/fitness/calories/",
    "/tools/api/fitness/protein/",
    "/tools/api/fitness/water/",
    "/tools/api/fitness/rm/",
    "/tools/api/fitness/one-rm/",
    "/tools/api/fitness/predict-reps/",
    "/tools/api/fitness/pace/",
    "/tools/api/fitness/body-composition/",
}
API_PATH_PREFIXES = (
    "/api/",
    "/tools/api/",
    "/users/api/",
    "/content/api/",
    "/accounts/api/",
)
MAX_CASES = 30
MAX_RESPONSE_TEXT = 3000
MAX_GENERATED_CONTEXT = 60000


class ExecutionPlanError(ValueError):
    """A plan cannot be safely or deterministically executed."""


def _is_local_target(url: str) -> bool:
    hostname = (urlparse(url).hostname or "").lower()
    return hostname in LOCAL_HOSTS


def normalize_target_url(target_url: str) -> str:
    """Validate a local target and return a normalized base URL."""
    value = str(target_url or "").strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ExecutionPlanError("执行目标必须是完整的 http(s) 地址")
    if parsed.username or parsed.password:
        raise ExecutionPlanError("执行目标不能包含用户名或密码")
    if not _is_local_target(value):
        raise ExecutionPlanError("当前版本只允许执行本机或 Docker 内部目标（localhost、127.0.0.1、host.docker.internal）")
    return value.rstrip("/") or f"{parsed.scheme}://{parsed.netloc}"


def runtime_target_url(target_url: str) -> str:
    """Map the host-facing local port to Django's internal Docker port."""
    parsed = urlparse(target_url)
    base_dir = str(getattr(settings, "BASE_DIR", ""))
    if base_dir == "/app" and parsed.hostname in {"127.0.0.1", "localhost"} and parsed.port == 8081:
        return urlunparse(parsed._replace(netloc=f"{parsed.hostname}:8000"))
    return target_url


def _strip_json_fence(content: str) -> str:
    value = str(content or "").strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", value, re.IGNORECASE | re.DOTALL)
    return fenced.group(1).strip() if fenced else value


def _execution_source_context(content: str, max_chars: int = MAX_GENERATED_CONTEXT) -> str:
    """Keep both the first generated cases and the document tail for plan extraction."""
    value = str(content or "")
    if len(value) <= max_chars:
        return value
    head_chars = max_chars * 2 // 3
    tail_chars = max_chars - head_chars
    return (
        value[:head_chars]
        + "\n\n[中间部分过长，已截断；请优先解析开头的可执行用例，并将不完整内容标记为 manual。]\n\n"
        + value[-tail_chars:]
    )


def _json_value(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(path)
    return current


def _safe_case_id(value: str, index: int) -> str:
    clean = re.sub(r"[^A-Za-z0-9_-]+", "-", str(value or "")).strip("-")
    return clean[:80] or f"AI-{index:03d}"


def _same_origin_url(base_url: str, path_or_url: str) -> str:
    candidate = urljoin(base_url.rstrip("/") + "/", str(path_or_url or "").strip())
    base = urlparse(base_url)
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != base.netloc:
        raise ExecutionPlanError("执行步骤只能访问与目标地址同源的路径")
    return candidate


def classify_api_operation(method: str, path: str) -> str:
    """Classify a request using a server-owned allowlist, never model claims."""
    method = str(method or "GET").upper()
    if method in {"GET", "HEAD", "OPTIONS"}:
        return "read_only"
    parsed = urlparse(str(path or ""))
    normalized_path = parsed.path or str(path or "")
    if not normalized_path.startswith("/"):
        normalized_path = f"/{normalized_path}"
    if method == "POST" and normalized_path in SAFE_POST_PATHS:
        return "safe_post"
    return "write"


def _validate_api_step(step: dict[str, Any]) -> dict[str, Any]:
    action = step.get("action", "request")
    if action != "request":
        raise ExecutionPlanError(f"API 不支持动作：{action}")
    method = str(step.get("method", "GET")).upper()
    if method not in ALLOWED_HTTP_METHODS:
        raise ExecutionPlanError(f"不支持 HTTP 方法：{method}")
    path = str(step.get("path") or step.get("url") or "").strip()
    if not path:
        raise ExecutionPlanError("API 步骤缺少 path")
    parsed_path = urlparse(path).path or path
    if not parsed_path.startswith(API_PATH_PREFIXES):
        raise ExecutionPlanError(
            f"API path 必须是实际接口路径（以 {', '.join(API_PATH_PREFIXES)} 开头），不能使用页面地址：{path}"
        )
    headers = step.get("headers") or {}
    query = step.get("query") or {}
    if not isinstance(headers, dict) or not isinstance(query, dict):
        raise ExecutionPlanError("API headers/query 必须是对象")
    return {
        "action": "request",
        "method": method,
        "path": path,
        "headers": {str(key): str(value) for key, value in headers.items()},
        "query": query,
        "body": step.get("body"),
        "expect": step.get("expect") or {},
        "operation": classify_api_operation(method, path),
    }


def _validate_ui_step(step: dict[str, Any]) -> dict[str, Any]:
    action = str(step.get("action") or "").strip().lower()
    aliases = {"navigate": "open", "assert_text": "expect_text", "assert_visible": "expect_visible"}
    action = aliases.get(action, action)
    if action not in {"open", "click", "fill", "expect_text", "expect_visible", "screenshot"}:
        raise ExecutionPlanError(f"UI 不支持动作：{action}")
    if action == "open":
        value = str(step.get("path") or step.get("url") or "").strip()
        if not value:
            raise ExecutionPlanError("UI open 步骤缺少 path")
        return {"action": action, "path": value}
    if action == "screenshot":
        return {"action": action, "name": str(step.get("name") or "step")}
    locator = str(step.get("locator") or "").strip()
    if not locator:
        raise ExecutionPlanError(f"UI {action} 步骤缺少 locator")
    result = {"action": action, "locator": locator}
    if action in {"fill", "expect_text"}:
        field = "value" if action == "fill" else "text"
        if not str(step.get(field) or ""):
            raise ExecutionPlanError(f"UI {action} 步骤缺少 {field}")
        result[field] = str(step[field])
    return result


def normalize_execution_plan(raw_plan: str | dict[str, Any], requested_mode: str, max_cases: int) -> dict[str, Any]:
    """Parse and validate the model response before any network/browser work."""
    try:
        data = raw_plan if isinstance(raw_plan, dict) else json.loads(_strip_json_fence(raw_plan))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ExecutionPlanError("大模型没有返回有效的 JSON 执行计划") from exc
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ExecutionPlanError("执行计划必须包含 cases 数组")
    if requested_mode not in {"auto", "api", "ui"}:
        raise ExecutionPlanError("执行模式只能是 auto、api 或 ui")
    limit = max(1, min(int(max_cases or 10), MAX_CASES))
    normalized: list[dict[str, Any]] = []
    for index, raw_case in enumerate(data["cases"][:limit], start=1):
        if not isinstance(raw_case, dict):
            continue
        channel = str(raw_case.get("channel") or raw_case.get("mode") or "manual").lower()
        if channel == "mixed":
            channel = "manual"
        if channel not in {"api", "ui", "manual"}:
            raise ExecutionPlanError(f"用例 {index} 的执行通道无效：{channel}")
        if requested_mode in {"api", "ui"} and channel not in {requested_mode, "manual"}:
            channel = "manual"
        steps: list[dict[str, Any]] = []
        manual_reason = str(raw_case.get("manual_reason") or "")[:500]
        try:
            for raw_step in raw_case.get("steps") or []:
                if not isinstance(raw_step, dict):
                    continue
                steps.append(
                    _validate_api_step(raw_step)
                    if channel == "api"
                    else _validate_ui_step(raw_step) if channel == "ui" else {"action": "manual"}
                )
        except ExecutionPlanError as exc:
            manual_reason = f"自动化计划校验失败：{exc}"
            channel = "manual"
            steps = []
        if channel in {"api", "ui"} and not steps:
            channel = "manual"
            manual_reason = manual_reason or "模型没有生成可执行步骤"
        normalized.append(
            {
                "id": _safe_case_id(raw_case.get("id"), index),
                "title": str(raw_case.get("title") or f"AI 生成用例 {index}")[:240],
                "channel": channel,
                "confidence": str(raw_case.get("confidence") or "unknown")[:40],
                "manual_reason": manual_reason,
                "steps": steps,
            }
        )
    if not normalized:
        raise ExecutionPlanError("大模型没有生成可执行用例")
    return {"version": 1, "requested_mode": requested_mode, "cases": normalized}


def build_execution_plan(
    test_cases: str,
    target_url: str,
    mode: str,
    model_id: str,
    max_cases: int,
    requirement: str = "",
    user_prompt: str = "",
) -> dict[str, Any]:
    target = normalize_target_url(target_url)
    prompt = f"""把下面的 Markdown 测试用例转换为严格 JSON，不要输出 Markdown、解释或代码。

目标地址：{target}
执行模式：{mode}
最多转换：{max_cases} 条

规则：
1. 只能输出 JSON 对象：{{\"cases\":[...]}}。
2. 每条用例必须有 id、title、channel、confidence、steps。
3. channel 只能是 api、ui、manual。无法从原用例确定 endpoint、请求方法、参数、定位器或断言时，必须用 manual，并写 manual_reason，不得臆造。
4. API step 只能是 {{\"action\":\"request\",\"method\":\"GET|HEAD|OPTIONS|POST|PUT|PATCH|DELETE\",\"path\":\"/path\",\"headers\":{{}},\"query\":{{}},\"body\":null,\"expect\":{{\"status\":200}}}}。
5. UI step 只能是 open、click、fill、expect_text、expect_visible、screenshot；locator 必须是原用例明确给出的 CSS、text= 或可见语义定位器。无法确定就 manual。UI 执行会继承当前登录会话。
6. API 的 GET/HEAD/OPTIONS 是 read_only；只有服务端明确允许的计算型 POST 才是 safe_post；评分、随机记录、保存、上传、删除、更新和未知 POST/PUT/PATCH/DELETE 都是 write，不能仅凭模型把它们标成安全。
7. 只生成与目标地址同源的路径。不要输出任意 Python、JavaScript、shell、文件系统或跨域动作。

原始测试用例：
{_execution_source_context(test_cases)}

本次生成需求（仅用于理解上下文）：
{str(requirement or '')[-10000:]}

本次用户提示词（仅用于理解上下文）：
{str(user_prompt or '')[-10000:]}
"""
    if not model_id:
        raise ExecutionPlanError("请先选择执行模型")
    llm = get_llm_service()
    raw = llm.generate_structured_content(
        prompt,
        model_id=model_id,
        system_prompt="你是测试执行计划解析器。只返回可校验的 JSON；不确定就标记 manual，不得编造或输出代码。",
        max_tokens=6000,
        temperature=0.1,
    )
    plan = normalize_execution_plan(raw, mode, max_cases)
    plan["target_url"] = target
    plan["model_id"] = model_id
    return plan


def _assert_response(response: requests.Response, expect: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not isinstance(expect, dict):
        return failures
    if "status" in expect and response.status_code != int(expect["status"]):
        failures.append(f"状态码期望 {expect['status']}，实际 {response.status_code}")
    for expected in (
        expect.get("text_contains", [])
        if isinstance(expect.get("text_contains"), list)
        else ([expect["text_contains"]] if expect.get("text_contains") else [])
    ):
        if str(expected) not in response.text:
            failures.append(f"响应不包含文本：{expected}")
    if isinstance(expect.get("json"), dict):
        try:
            payload = response.json()
        except ValueError:
            failures.append("响应不是 JSON")
        else:
            for path, expected in expect["json"].items():
                try:
                    actual = _json_value(payload, str(path))
                except KeyError:
                    failures.append(f"JSON 缺少字段：{path}")
                else:
                    if actual != expected:
                        failures.append(f"JSON 字段 {path} 期望 {expected!r}，实际 {actual!r}")
    return failures


def _execute_api_case(
    case: dict[str, Any], target_url: str, allow_mutations: bool, browser_cookies: dict[str, str] | None = None
) -> dict[str, Any]:
    session = requests.Session()
    if browser_cookies:
        session.cookies.update(browser_cookies)
    csrf_name = getattr(settings, "CSRF_COOKIE_NAME", "csrftoken")
    csrf_token = (browser_cookies or {}).get(csrf_name)
    step_results: list[dict[str, Any]] = []
    started = time.monotonic()
    for index, step in enumerate(case["steps"], start=1):
        method = step["method"]
        operation = step.get("operation") or classify_api_operation(method, step.get("path", ""))
        if operation == "write" and not allow_mutations:
            return {
                "id": case["id"],
                "title": case["title"],
                "status": "skipped",
                "channel": "api",
                "reason": "包含真实写操作；请勾选允许 API 真正写操作后重试",
                "steps": step_results,
            }
        url = _same_origin_url(target_url, step["path"])
        request_started = time.monotonic()
        try:
            request_headers = dict(step["headers"])
            if method not in {"GET", "HEAD", "OPTIONS"} and csrf_token:
                request_headers.setdefault("X-CSRFToken", csrf_token)
            response = session.request(
                method, url, headers=request_headers, params=step["query"], json=step["body"], timeout=15
            )
            failures = _assert_response(response, step["expect"])
            step_results.append(
                {
                    "step": index,
                    "action": "request",
                    "method": method,
                    "operation": operation,
                    "url": url,
                    "status_code": response.status_code,
                    "duration_ms": round((time.monotonic() - request_started) * 1000, 2),
                    "response": response.text[:MAX_RESPONSE_TEXT],
                    "assertions": failures,
                }
            )
            if failures:
                return {
                    "id": case["id"],
                    "title": case["title"],
                    "status": "failed",
                    "channel": "api",
                    "reason": "; ".join(failures),
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    "steps": step_results,
                }
        except requests.RequestException as exc:
            step_results.append(
                {"step": index, "action": "request", "method": method, "operation": operation, "url": url, "error": str(exc)}
            )
            return {
                "id": case["id"],
                "title": case["title"],
                "status": "failed",
                "channel": "api",
                "reason": str(exc),
                "duration_ms": round((time.monotonic() - started) * 1000, 2),
                "steps": step_results,
            }
    return {
        "id": case["id"],
        "title": case["title"],
        "status": "passed",
        "channel": "api",
        "duration_ms": round((time.monotonic() - started) * 1000, 2),
        "steps": step_results,
    }


def _ui_locator(page: Any, value: str) -> Any:
    if value.startswith("text="):
        return page.get_by_text(value[5:], exact=False)
    if value.startswith("#") and value[1:].replace("_", "").isalnum():
        # Generated UI cases naturally reference the stable input IDs. The
        # food selector hides radio/checkbox inputs and exposes their labels as
        # the clickable surface, so redirect only those controls to label[for].
        input_type = page.locator(value).get_attribute("type")
        if input_type in {"radio", "checkbox"}:
            return page.locator(f"label[for='{value[1:]}']")
    return page.locator(value)


def _execute_ui_cases(
    cases: list[dict[str, Any]],
    target_url: str,
    artifact_dir: Path,
    browser_cookies: dict[str, str] | None = None,
    progress_callback: Callable[[int, str], None] | None = None,
) -> dict[str, dict[str, Any]]:
    from playwright.sync_api import sync_playwright

    results: dict[str, dict[str, Any]] = {}
    executable = shutil.which("chromium") or shutil.which("chromium-browser")
    launch_args = ["--no-sandbox", "--disable-dev-shm-usage"]
    with sync_playwright() as playwright:
        browser = (
            playwright.chromium.launch(headless=True, executable_path=executable, args=launch_args)
            if executable
            else playwright.chromium.launch(headless=True, args=launch_args)
        )
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        if browser_cookies:
            hostname = urlparse(target_url).hostname or "127.0.0.1"
            context.add_cookies(
                [
                    {"name": name, "value": value, "domain": hostname, "path": "/"}
                    for name, value in browser_cookies.items()
                    if name and value
                ]
            )
        page = context.new_page()
        try:
            for case_index, case in enumerate(cases):
                started = time.monotonic()
                step_results: list[dict[str, Any]] = []
                status = "passed"
                reason = ""
                try:
                    for index, step in enumerate(case["steps"], start=1):
                        action = step["action"]
                        if progress_callback:
                            completed_steps = case_index + (index - 1) / max(len(case["steps"]), 1)
                            progress_callback(
                                round(completed_steps / max(len(cases), 1) * 90),
                                f"执行 {case['id']}：{case['title']} · 步骤 {index}/{len(case['steps'])}：{action}",
                            )
                        if action == "open":
                            page.goto(_same_origin_url(target_url, step["path"]), wait_until="domcontentloaded", timeout=15000)
                        elif action == "click":
                            _ui_locator(page, step["locator"]).click(timeout=10000)
                        elif action == "fill":
                            _ui_locator(page, step["locator"]).fill(step["value"], timeout=10000)
                        elif action == "expect_text":
                            text = _ui_locator(page, step["locator"]).inner_text(timeout=10000)
                            if step["text"] not in text:
                                raise AssertionError(f"页面文本不包含：{step['text']}")
                        elif action == "expect_visible":
                            locator = _ui_locator(page, step["locator"])
                            locator.wait_for(state="visible", timeout=10000)
                        elif action == "screenshot":
                            screenshot = (
                                artifact_dir / f"{case['id']}-{index}-{re.sub(r'[^A-Za-z0-9_-]+', '-', step['name'])}.png"
                            )
                            page.screenshot(path=str(screenshot), full_page=True)
                            step_results.append(
                                {"step": index, "action": action, "status": "passed", "screenshot": screenshot.name}
                            )
                            continue
                        step_results.append({"step": index, "action": action, "status": "passed"})
                        # Keep a single fresh frame for the dedicated runner
                        # page. This makes the Playwright browser state visible
                        # while the current action is being executed.
                        try:
                            page.screenshot(path=str(artifact_dir / "live.png"), full_page=False)
                        except Exception:
                            pass
                    if progress_callback:
                        progress_callback(
                            round((case_index + 1) / max(len(cases), 1) * 90),
                            f"完成 {case['id']}：{case['title']}",
                        )
                except Exception as exc:  # Playwright exposes several concrete exception classes.
                    status = "failed"
                    reason = str(exc)
                    screenshot = artifact_dir / f"{case['id']}-failure.png"
                    try:
                        page.screenshot(path=str(screenshot), full_page=True)
                        reason = f"{reason}；截图：{screenshot.name}"
                    except Exception:
                        pass
                    error_step = {"step": len(step_results) + 1, "action": "error", "status": "failed", "error": str(exc)}
                    if screenshot.exists():
                        error_step["screenshot"] = screenshot.name
                    step_results.append(error_step)
                results[case["id"]] = {
                    "id": case["id"],
                    "title": case["title"],
                    "status": status,
                    "channel": "ui",
                    "reason": reason,
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    "steps": step_results,
                }
        finally:
            context.close()
            browser.close()
    return results


def execute_plan(
    plan: dict[str, Any],
    allow_mutations: bool,
    artifact_dir: str | Path,
    progress_callback: Callable[[int, str], None] | None = None,
    browser_cookies: dict[str, str] | None = None,
) -> dict[str, Any]:
    target_url = runtime_target_url(normalize_target_url(plan["target_url"]))
    cases = plan.get("cases", [])
    artifact_path = Path(artifact_dir)
    artifact_path.mkdir(parents=True, exist_ok=True)
    ui_cases = [case for case in cases if case["channel"] == "ui"]
    results_by_id = (
        _execute_ui_cases(ui_cases, target_url, artifact_path, browser_cookies, progress_callback) if ui_cases else {}
    )
    results: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        if progress_callback:
            progress_callback(round((index - 1) / max(len(cases), 1) * 100), f"执行 {case['id']}：{case['title']}")
        if case["channel"] == "manual":
            result = {
                "id": case["id"],
                "title": case["title"],
                "status": "skipped",
                "channel": "manual",
                "reason": case["manual_reason"] or "无法安全转换为可执行步骤",
                "steps": [],
            }
        elif case["channel"] == "api":
            result = _execute_api_case(case, target_url, allow_mutations, browser_cookies)
        else:
            result = results_by_id.get(
                case["id"],
                {
                    "id": case["id"],
                    "title": case["title"],
                    "status": "failed",
                    "channel": "ui",
                    "reason": "UI 执行器未返回结果",
                    "steps": [],
                },
            )
        results.append(result)
    summary = {
        "total": len(results),
        "passed": sum(item["status"] == "passed" for item in results),
        "failed": sum(item["status"] == "failed" for item in results),
        "skipped": sum(item["status"] == "skipped" for item in results),
    }
    if progress_callback:
        progress_callback(100, "执行完成")
    return {
        "version": 1,
        "target_url": target_url,
        "requested_mode": plan.get("requested_mode", "auto"),
        "model_id": plan.get("model_id"),
        "allow_mutations": allow_mutations,
        "summary": summary,
        "cases": results,
        "generated_at": datetime.now().isoformat(),
    }
