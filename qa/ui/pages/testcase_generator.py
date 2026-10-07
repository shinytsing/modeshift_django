"""Test-case generation page with knowledge selection controls."""

from __future__ import annotations

from playwright.sync_api import Locator

from qa.ui.pages.base import BasePage


class TestcaseGeneratorPage(BasePage):
    __test__ = False  # Page object, not a pytest test class.

    def open(self) -> None:
        self.navigate("/tools/test_case_generator/")

    @property
    def selected_model(self) -> Locator:
        return self.page.locator("#generationModel")

    @property
    def generate_button(self) -> Locator:
        return self.page.locator("#generateButton")

    @property
    def selected_documents(self) -> Locator:
        return self.page.locator("#selectedDocuments")

    @property
    def selected_count(self) -> Locator:
        return self.page.locator("#selectedCount")

    @property
    def knowledge_detail(self) -> Locator:
        return self.page.locator("#knowledgeDetailDialog")

    @property
    def knowledge_detail_content(self) -> Locator:
        return self.page.locator("#knowledgeDetailContent")

    @property
    def generation_status(self) -> Locator:
        return self.page.locator("#generationStatus")

    @property
    def result_meta(self) -> Locator:
        return self.page.locator("#resultMeta")

    @property
    def result_card(self) -> Locator:
        return self.page.locator("#resultCard")

    def search_knowledge(self, query: str) -> None:
        self.page.locator("#knowledgeQuery").fill(query)
        self.page.locator("#knowledgeSearchButton").click()

    def knowledge_result(self, document_id: int) -> Locator:
        return self.page.locator(f"#knowledgeResults article[data-open-doc='{document_id}']")

    def inspect_knowledge_result(self, document_id: int) -> None:
        # Click the card body rather than its nested add button.
        self.knowledge_result(document_id).click(position={"x": 20, "y": 20})

    def close_knowledge_detail(self) -> None:
        self.page.locator("#closeKnowledgeDetail").click()

    def add_knowledge_result(self, document_id: int) -> None:
        self.knowledge_result(document_id).get_by_role("button", name="添加到生成上下文").click()

    def generate(self, requirement: str, prompt: str) -> None:
        self.page.get_by_label("产品需求").fill(requirement)
        self.page.get_by_label("补充 Prompt").fill(prompt)
        self.generate_button.click()
