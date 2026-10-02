"""Browser contract for selecting local knowledge references before testcase generation."""

from __future__ import annotations

import os
import re

import allure
import pytest
from playwright.sync_api import Page, expect

from qa.support.auth import auth_mutations_are_allowed, new_qa_credentials


def _url(path: str) -> str:
    return f"{os.getenv('BASE_URL', 'http://127.0.0.1:8000').rstrip('/')}{path}"


@pytest.mark.ui
@pytest.mark.e2e
@allure.epic("QAToolBox 左移质量门禁")
@allure.feature("测试用例生成器")
@allure.story("选择知识库资料与模型并查看生成来源")
def test_user_selects_knowledge_and_model_for_testcase_generation(page: Page) -> None:
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    if not auth_mutations_are_allowed(base_url):
        pytest.skip("用例生成器要求登录；非本机目标需设置 QA_ALLOW_AUTH_MUTATIONS=1")

    credentials = new_qa_credentials()
    page.goto(_url("/accounts/signup/"), wait_until="domcontentloaded")
    page.get_by_label("电子邮件:").fill(credentials.email)
    page.get_by_label("密码:").fill(credentials.password)
    page.get_by_role("button", name=re.compile("注册")).click()
    expect(page).to_have_url(re.compile(r"/$"))

    page.route(
        "**/tools/api/llm/models/",
        lambda route: route.fulfill(status=200, json={"models": [{
            "id": "groq:test-model", "provider": "groq", "model": "test-model",
            "label": "groq / test-model", "available": True,
            "status": "configured_unverified", "description": "已配置，未在线验证",
        }]}),
    )
    page.route(
        "**/tools/api/rag/documents/search/**",
        lambda route: route.fulfill(status=200, json={"results": [{
            "id": 42, "title": "登录模块说明.md", "snippet": "验证码过期后需提示重新获取。",
            "score": 0.9, "source": "private",
        }]}),
    )
    page.route(
        "**/tools/api/rag/documents/42/",
        lambda route: route.fulfill(status=200, json={
            "id": 42, "title": "登录模块说明.md", "source": "private",
            "source_type": "markdown", "chunks": 1,
            "content": "验证码过期后需提示重新获取。",
        }),
    )
    submitted: dict = {}

    def create_task(route) -> None:
        submitted.update(route.request.post_data_json)
        route.fulfill(status=200, json={"success": True, "task_id": "qa-task", "message": "created"})

    page.route("**/tools/api/async/generate-testcases/", create_task)
    page.route(
        "**/tools/api/async/task/qa-task/",
        lambda route: route.fulfill(status=200, json={
            "success": True, "task_id": "qa-task", "status": "completed", "progress": 100,
            "created_at": "2026-01-01", "started_at": "2026-01-01", "completed_at": "2026-01-01",
            "result": "# 测试用例\n### TC-001 登录验证码过期", "sources": [{"document": "登录模块说明.md", "sequence": 1}],
            "selected_model": "groq:test-model",
        }),
    )

    page.goto(_url("/tools/test_case_generator/"), wait_until="domcontentloaded")
    expect(page.locator("#generationModel")).to_have_value("groq:test-model")
    expect(page.locator("#generateButton")).to_be_visible()
    page.locator("#knowledgeQuery").fill("登录验证码")
    page.locator("#knowledgeSearchButton").click()
    result_card = page.locator("#knowledgeResults article[data-open-doc='42']")
    expect(result_card).to_be_visible()

    # The card opens the document detail dialog; the add action is separate.
    result_card.click(position={"x": 20, "y": 20})
    expect(page.locator("#knowledgeDetailDialog")).to_be_visible()
    expect(page.locator("#knowledgeDetailContent")).to_contain_text("验证码过期")
    page.locator("#closeKnowledgeDetail").click()
    result_card.get_by_role("button", name="添加到生成上下文").click()
    expect(page.locator("#selectedDocuments")).to_contain_text("登录模块说明.md")
    expect(page.locator("#selectedCount")).to_contain_text("已选择 1 篇")

    page.get_by_label("产品需求").fill("验证码过期后提示重新获取")
    page.get_by_label("补充 Prompt").fill("只基于已选资料，覆盖 {requirement}")
    page.locator("#generateButton").click()

    expect(page.locator("#generationStatus")).to_contain_text("人工用例已生成", timeout=5_000)
    expect(page.locator("#resultMeta")).to_contain_text("模型：groq:test-model")
    expect(page.locator("#resultCard")).to_contain_text("API 自动化")
    assert submitted["model_id"] == "groq:test-model"
    assert submitted["knowledge_document_ids"] == [42]
    assert submitted["requirement"] == "验证码过期后提示重新获取"
    assert submitted["prompt"] == "只基于已选资料，覆盖 {requirement}"
    allure.attach(page.screenshot(full_page=True), name="testcase-knowledge-selection.png", attachment_type=allure.attachment_type.PNG)
