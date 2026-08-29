"""Requests-based contracts for public, read-only QAToolBox endpoints."""

from __future__ import annotations

import time

import allure
import pytest
import requests


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("部署健康契约")
def test_health_endpoint_returns_the_deployment_contract(
    base_url: str, http_session: requests.Session
) -> None:
    """A deployable instance exposes one exact, machine-readable health contract."""
    started_at = time.monotonic()
    with allure.step("请求健康检查接口"):
        response = http_session.get(f"{base_url}/health/", timeout=3)
    elapsed_seconds = time.monotonic() - started_at

    allure.attach(
        response.text,
        name="health-response.json",
        attachment_type=allure.attachment_type.JSON,
    )
    allure.attach(
        f"GET /health/ -> {response.status_code} in {elapsed_seconds:.3f}s",
        name="request-summary.txt",
        attachment_type=allure.attachment_type.TEXT,
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    assert elapsed_seconds < 1.0

    body = response.json()
    assert set(body) == {"status", "timestamp", "version"}
    assert body["status"] == "healthy"
    assert isinstance(body["timestamp"], float)
    assert isinstance(body["version"], str) and body["version"]


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试看板状态契约")
def test_test_status_endpoint_returns_a_complete_dashboard_state(
    base_url: str, http_session: requests.Session
) -> None:
    """The dashboard can render only when its status response keeps this shape."""
    with allure.step("请求测试看板状态"):
        response = http_session.get(f"{base_url}/api/tests/status/", timeout=3)

    allure.attach(
        response.text,
        name="dashboard-status-response.json",
        attachment_type=allure.attachment_type.JSON,
    )

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")

    body = response.json()
    assert set(body) == {"is_running", "progress", "current_test", "status", "timestamp"}
    assert body["is_running"] is False
    assert body["progress"] == 100
    assert body["current_test"] == "测试完成"
    assert body["status"] == "completed"
    assert isinstance(body["timestamp"], str) and body["timestamp"]


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("CSRF 负向安全边界")
def test_test_status_endpoint_rejects_post_requests_without_a_csrf_token(
    base_url: str, http_session: requests.Session
) -> None:
    """An unsafe request without a CSRF token must fail before it can change state."""
    with allure.step("提交不带 CSRF Token 的 POST 请求"):
        response = http_session.post(f"{base_url}/api/tests/status/", timeout=3)

    allure.attach(
        response.text,
        name="csrf-rejection-response.html",
        attachment_type=allure.attachment_type.HTML,
    )

    assert response.status_code == 403


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试结果统计契约")
def test_test_results_endpoint_keeps_totals_and_categories_consistent(
    base_url: str, http_session: requests.Session
) -> None:
    """The dashboard result cards must agree with the detailed category totals."""
    with allure.step("请求测试结果统计"):
        response = http_session.get(f"{base_url}/api/tests/results/", timeout=3)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    allure.attach(
        response.text,
        name="test-results-response.json",
        attachment_type=allure.attachment_type.JSON,
    )

    assert body["total"] == body["passed"] + body["failed"] + body["skipped"] + body["broken"]
    assert body["success_rate"] == 90.0
    assert set(body["categories"]) == {"functional", "api", "performance", "security"}
    for category in body["categories"].values():
        assert category["total"] == category["passed"] + category["failed"]


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试启动请求契约")
def test_run_tests_endpoint_echoes_the_selected_test_types(
    base_url: str, http_session: requests.Session
) -> None:
    """The UI-selected API/UI scope reaches the runner without being silently changed."""
    selected_test_types = ["api", "ui"]
    with allure.step("提交 API 与 UI 的测试启动请求"):
        response = http_session.post(
            f"{base_url}/api/tests/run/",
            json={"test_types": selected_test_types},
            timeout=3,
        )

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    allure.attach(
        response.text,
        name="run-tests-response.json",
        attachment_type=allure.attachment_type.JSON,
    )

    assert body["status"] == "started"
    assert body["message"] == "测试已启动"
    assert body["test_types"] == selected_test_types
    assert isinstance(body["timestamp"], str) and body["timestamp"]


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("看板统计聚合契约")
def test_test_stats_endpoint_keeps_global_and_category_totals_consistent(
    base_url: str, http_session: requests.Session
) -> None:
    """Dashboard summary cards must reconcile with the reported global test totals."""
    with allure.step("请求测试统计汇总"):
        response = http_session.get(f"{base_url}/api/tests/stats/", timeout=3)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    allure.attach(response.text, name="test-stats-response.json", attachment_type=allure.attachment_type.JSON)

    assert body["total_tests"] == body["passed_tests"] + body["failed_tests"]
    assert body["success_rate"] == 90.0
    assert set(body["categories"]) == {"functional", "api", "performance", "security", "ui"}
    assert sum(category["total"] for category in body["categories"].values()) == body["total_tests"]
    assert sum(category["passed"] for category in body["categories"].values()) == body["passed_tests"]
    assert sum(category["failed"] for category in body["categories"].values()) == body["failed_tests"]


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试历史分页契约")
def test_test_history_endpoint_returns_a_complete_first_page(
    base_url: str, http_session: requests.Session
) -> None:
    """History rows must be uniquely identified and internally consistent for dashboard pagination."""
    with allure.step("请求第一页测试历史"):
        response = http_session.get(f"{base_url}/api/tests/history/", timeout=3)

    assert response.status_code == 200
    body = response.json()
    allure.attach(response.text, name="test-history-response.json", attachment_type=allure.attachment_type.JSON)

    assert body["pagination"] == {"page": 1, "page_size": 10, "total_count": 10, "total_pages": 1}
    assert len(body["history"]) == 10
    assert [entry["id"] for entry in body["history"]] == list(range(1, 11))
    for entry in body["history"]:
        assert entry["total_tests"] == entry["passed"] + entry["failed"] + entry["skipped"] + entry["broken"]
        assert 0 <= entry["success_rate"] <= 100
        assert entry["duration"] > 0
        assert entry["test_types"] == ["functional", "api"]


@pytest.mark.api
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("API 自动化 - requests")
@allure.story("测试启动方法边界")
def test_run_tests_endpoint_rejects_get_requests(
    base_url: str, http_session: requests.Session
) -> None:
    """The runner endpoint accepts only an explicit POST command, never a browser GET request."""
    with allure.step("使用 GET 请求访问测试启动接口"):
        response = http_session.get(f"{base_url}/api/tests/run/", timeout=3)

    assert response.status_code == 405
    assert response.headers["Allow"] == "POST"
