"""Resume entry checks; the demonstrated business journey lives in the shared gate test."""

import re

import pytest
from playwright.sync_api import Page, expect

from qa.ui.pages.resume import ResumePage


@pytest.mark.ui
def test_resume_download_matches_supplied_pdf(page: Page, base_url: str, tmp_path):
    from pathlib import Path

    resume = ResumePage(page, base_url)
    resume.open()
    download = resume.download_pdf()
    assert download.suggested_filename == "高杰-测试开发工程师.pdf"
    target = tmp_path / "resume.pdf"
    download.save_as(target)
    original = Path(__file__).resolve().parents[2] / "docs/assets/gaojie-resume.pdf"
    assert target.read_bytes() == original.read_bytes()


@pytest.mark.ui
def test_automation_skill_opens_demo_dialog(page: Page, base_url: str):
    resume = ResumePage(page, base_url)
    resume.open()
    card = resume.automation_card
    resume.open_automation()
    dialog = page.get_by_role("dialog", name="UI 自动化展示")
    expect(dialog).to_be_visible()
    expect(dialog.get_by_text("共用用例：qa/ui/test_authenticated_bmi_flow.py", exact=False)).to_be_visible()
    resume.close_skill()
    expect(dialog).not_to_be_visible()
    card.focus()
    page.keyboard.press("Enter")
    expect(dialog).to_be_visible()
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible()


@pytest.mark.ui
@pytest.mark.parametrize(
    ("card_name", "detail"),
    [
        ("JMeter · Locust", "高途 Coding-Link WebSocket 音频会话"),
        ("Python · Django", "RAG 知识库"),
        ("GitHub Actions · QA Gate", "push main"),
        ("SQL · MySQL", "Postman/ES"),
        ("Linux · VMware", "单台 VMware Ubuntu"),
        ("Pytest · Allure", "JUnit、HTML、Allure"),
        ("需求评审 · 左移", "不能搜索、引用、下载他人文档"),
    ],
)
def test_each_other_skill_displays_its_own_project_context(page: Page, base_url: str, card_name: str, detail: str):
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_skill(card_name)
    dialog = resume.dialog
    expect(dialog).to_be_visible()
    expect(dialog.get_by_text(detail, exact=False).first).to_be_visible()
    expect(dialog.get_by_role("button", name="执行 UI 自动化")).not_to_be_visible()
    expect(dialog.get_by_text("测试步骤：")).to_be_visible()


@pytest.mark.ui
@pytest.mark.parametrize(
    ("card_name", "link_name", "href"),
    [
        (
            "Python · Django",
            "查看 ModeShift 产品说明",
            "https://github.com/shinytsing/modeshift_django/blob/main/docs/MODESHIFT_PRODUCT_GUIDE.md",
        ),
        (
            "GitHub Actions · QA Gate",
            "查看 GitHub QA 门禁",
            "https://github.com/shinytsing/modeshift_django/blob/main/.github/workflows/testing-system.yml",
        ),
        (
            "GitHub Actions · QA Gate",
            "查看成功流水线",
            "https://github.com/shinytsing/modeshift_django/actions/runs/37199597201",
        ),
        (
            "Linux · VMware",
            "查看单机部署说明",
            "https://github.com/shinytsing/modeshift_django/blob/main/docs/VMWARE_SINGLE_HOST_DEPLOYMENT.md",
        ),
    ],
)
def test_project_skill_links_to_its_real_evidence(page: Page, base_url: str, card_name: str, link_name: str, href: str):
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_skill(card_name)
    link = resume.dialog.get_by_role("link", name=link_name)
    expect(link).to_have_attribute("href", href)
    expect(link).to_have_attribute("target", "_blank")
    expect(link).to_have_attribute("rel", "noopener noreferrer")


@pytest.mark.ui
@pytest.mark.parametrize(
    ("card_name", "boundary"),
    [
        ("GitHub Actions · QA Gate", "QA job 失败会阻断 build_image/deploy"),
        ("SQL · MySQL", "Kafka 仅有历史环境配置记录"),
        ("Linux · VMware", "不回滚数据库迁移"),
        ("Pytest · Allure", "不能当作当前 CI 成绩"),
    ],
)
def test_skill_descriptions_keep_evidence_boundaries(page: Page, base_url: str, card_name: str, boundary: str):
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_skill(card_name)
    expect(resume.dialog.get_by_text(boundary, exact=False).first).to_be_visible()


@pytest.mark.ui
@pytest.mark.parametrize(
    ("link_name", "anchor", "heading"),
    [
        ("打开历史性能案例", "jmeter", "JMeter：高途 Coding-Link WebSocket"),
        ("查看 Locust 原页面", "locust", "Locust：高途多用户音频会话"),
    ],
)
def test_performance_card_opens_read_only_case_notes(page: Page, base_url: str, link_name: str, anchor: str, heading: str):
    page_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_skill("JMeter · Locust")
    resume.dialog.get_by_role("link", name=link_name).click()
    expect(page).to_have_url(f"{base_url}/resume-3d/performance/#{anchor}")
    expect(page.get_by_role("heading", name=heading)).to_be_visible()
    expect(
        page.get_by_text("报告状态：已找到高途 JMeter 原始 Dashboard 和 Locust 历史控制台页面；Locust 暂无有效运行报告。")
    ).to_be_visible()
    expect(page.get_by_role("button", name="执行压测")).to_have_count(0)
    assert page_errors == []


@pytest.mark.ui
@pytest.mark.parametrize(
    ("card_name", "evidence"),
    [
        ("Python · Django", "status=healthy"),
        ("GitHub Actions · QA Gate", "未触发 GitHub Actions"),
        ("SQL · MySQL", "HTTP 401"),
        ("Linux · VMware", "status=healthy"),
        ("Pytest · Allure", "演示数据，并非真实 CI 成绩"),
        ("需求评审 · 左移", "HTTP 405"),
    ],
)
def test_each_skill_executes_a_read_only_project_check(page: Page, base_url: str, card_name: str, evidence: str):
    page_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_skill(card_name)
    resume.dialog.get_by_role("button", name="执行现场只读检查").click()
    output = resume.dialog.get_by_role("status")
    expect(output).to_contain_text("结果：通过")
    expect(output).to_contain_text(evidence)
    assert page_errors == []


@pytest.mark.ui
def test_skill_check_reports_a_failed_health_contract(page: Page, base_url: str):
    resume = ResumePage(page, base_url)
    resume.open()
    page.route(
        "**/health/", lambda route: route.fulfill(status=503, content_type="application/json", body='{"status":"down"}')
    )
    resume.open_skill("Python · Django")
    resume.dialog.get_by_role("button", name="执行现场只读检查").click()
    expect(resume.dialog.get_by_role("status")).to_contain_text("执行失败：健康契约不符合预期（HTTP 503）")


@pytest.mark.ui
def test_performance_replay_is_historical_and_opens_original_jmeter_dashboard(page: Page, base_url: str):
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_skill("JMeter · Locust")
    resume.dialog.get_by_role("button", name="执行历史报告回放").click()
    expect(page).to_have_url(f"{base_url}/resume-3d/performance/?play=jmeter#jmeter")
    expect(page.locator("#jmeterReplayOutput")).to_contain_text("不是消息级延迟")
    with page.expect_popup() as popup_info:
        page.get_by_role("link", name="打开当时生成的 Apache JMeter Dashboard").click()
    original = popup_info.value
    expect(original).to_have_url(re.compile(r"/static/resume-reports/gaotu-jmeter-20251127/index\.html$"))
    expect(original).to_have_title("Apache JMeter Dashboard")


@pytest.mark.ui
def test_locust_original_page_is_embedded_as_a_noninteractive_image(page: Page, base_url: str):
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_skill("JMeter · Locust")
    resume.dialog.get_by_role("link", name="查看 Locust 原页面").click()
    image = page.get_by_role("img", name="高途 Coding-Link Locust 历史控制台原貌")
    expect(image).to_be_visible()
    expect(image).to_have_attribute("src", "/static/resume-reports/gaotu-locust-console-original.png")
    assert image.evaluate("(image) => image.naturalWidth") == 1200
    expect(page.get_by_role("button", name="执行 Locust 脚本流程回放")).to_have_count(0)


@pytest.mark.ui
def test_execute_button_runs_real_browser_journey(page: Page, base_url: str):
    resume = ResumePage(page, base_url)
    resume.open()
    resume.open_automation()
    response = resume.run_ui_demo()
    assert response.status == 200
    result = response.json()
    assert result["status"] == "passed", result
    assert "1 passed" in result["output"]
    assert re.search(
        r"test_user_registers_logs_in_and_calculates_bmi_through_the_visible_ui\[chromium\]\s+PASSED",
        result["output"],
    ), result["output"]
    expect(resume.execution_status).to_have_text("演示通过")
    expect(resume.run_button).to_be_enabled()
