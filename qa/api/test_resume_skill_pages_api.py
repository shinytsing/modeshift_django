"""Public portfolio case notes must be factual and read-only."""

import pytest

from qa.api.clients.transport import ApiTransport


@pytest.mark.api
def test_performance_case_page_distinguishes_jmeter_result_from_empty_locust_snapshot(api_transport: ApiTransport):
    response = api_transport.get("/resume-3d/performance/")
    assert response.status_code == 200
    assert 'id="jmeter"' in response.text
    assert 'id="locust"' in response.text
    assert "JMeter 原始 Dashboard" in response.text
    assert "Locust 历史控制台" in response.text
    assert "Locust 暂无有效运行报告" in response.text
    assert "/static/resume-reports/gaotu-locust-console-original.png" in response.text
    assert 'id="replayLocust"' not in response.text
    assert "50 个样本" in response.text
    assert "369623 ms" in response.text
    assert "不是消息响应延迟" in response.text
    assert "0 用户、0 请求" in response.text
    assert "执行压测" not in response.text


@pytest.mark.api
def test_legacy_performance_dashboard_labels_illustrative_numbers(api_transport: ApiTransport):
    response = api_transport.get("/testing-performance/")
    assert response.status_code == 200
    assert "本页图表和数字是界面演示数据" in response.text
    assert 'href="/resume-3d/performance/"' in response.text


@pytest.mark.api
def test_original_jmeter_dashboard_and_its_assets_are_served(api_transport: ApiTransport):
    dashboard = api_transport.get("/static/resume-reports/gaotu-jmeter-20251127/index.html")
    script = api_transport.get("/static/resume-reports/gaotu-jmeter-20251127/content/js/dashboard.js")
    assert dashboard.status_code == 200
    assert "Apache JMeter Dashboard" in dashboard.text
    assert script.status_code == 200


@pytest.mark.api
def test_original_locust_console_screenshot_is_served_as_an_image(api_transport: ApiTransport):
    response = api_transport.get("/static/resume-reports/gaotu-locust-console-original.png")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
