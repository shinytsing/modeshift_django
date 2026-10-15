"""Local learning page remains usable alongside the remote resume features."""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
def test_learning_paper_requires_answers_then_scores_and_resets(page: Page, base_url: str):
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{base_url}/testing-learning/")
    expect(page.get_by_role("heading", name="测试开发综合能力评估")).to_be_visible()
    submit = page.get_by_role("button", name="完成全部题目后提交", exact=False)
    expect(submit).to_be_disabled()
    questions = page.locator("article.question")
    expect(questions).to_have_count(12)
    for question in questions.all():
        question.get_by_role("button").first.click()
    submit = page.get_by_role("button", name="提交试卷并查看解析")
    expect(submit).to_be_enabled()
    submit.click()
    expect(page.locator("#result")).to_be_visible()
    expect(page.locator(".explain")).to_have_count(12)
    expect(page.locator("article.wrong").first).to_be_visible()
    assert 0 <= int(page.locator("#score").inner_text()) < 100
    page.get_by_role("button", name="重新开始").click()
    expect(page.locator("#result")).not_to_be_visible()
    expect(page.locator("#progressText")).to_have_text("0 / 12")
    expect(page.locator(".picked")).to_have_count(0)
    expect(page.locator("#submit")).to_be_disabled()
    assert errors == []
