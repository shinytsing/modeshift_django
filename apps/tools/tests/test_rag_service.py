from django.contrib.auth.models import User
from django.test import TestCase

from apps.tools.models.rag_models import RequirementChunk, RequirementDocument
from apps.tools.services.rag_service import (
    SITE_CAPABILITIES_TITLE,
    build_testcase_prompt,
    embed,
    search_chunks,
    search_documents,
    sync_site_capabilities,
)


class RagServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="rag-user", password="secret")
        document = RequirementDocument.objects.create(
            owner=self.user,
            title="登录需求.md",
            source_file="rag_requirements/login.md",
            source_type="md",
            extracted_text="登录支持验证码过期校验。",
        )
        RequirementChunk.objects.create(
            document=document,
            sequence=1,
            content="用户登录时验证码五分钟后失效，过期后必须提示重新获取。",
            vector=embed("用户登录时验证码五分钟后失效，过期后必须提示重新获取。"),
        )
        RequirementChunk.objects.create(
            document=document, sequence=2, content="个人资料可以更新昵称和头像。", vector=embed("个人资料可以更新昵称和头像。")
        )

    def test_search_returns_ranked_source_chunks(self):
        results = search_chunks(self.user, "登录验证码过期怎么测试")
        self.assertEqual(results[0]["sequence"], 1)
        self.assertIn("验证码", results[0]["content"])

    def test_search_chunks_is_limited_to_selected_documents(self):
        other = RequirementDocument.objects.create(
            owner=self.user,
            title="支付.md",
            source_file="rag_requirements/pay.md",
            source_type="md",
            extracted_text="验证码支付",
        )
        RequirementChunk.objects.create(
            document=other, sequence=1, content="登录验证码支付校验", vector=embed("登录验证码支付校验")
        )
        login_doc_id = RequirementDocument.objects.get(title="登录需求.md").id
        results = search_chunks(self.user, "登录验证码", document_ids=[login_doc_id])
        self.assertTrue(results)
        self.assertEqual({result["document_id"] for result in results}, {login_doc_id})

    def test_document_search_never_returns_another_users_private_document(self):
        other_user = User.objects.create_user(username="private-owner", password="secret")
        private_doc = RequirementDocument.objects.create(
            owner=other_user,
            title="私人登录.md",
            source_file="rag_requirements/private.md",
            source_type="md",
            extracted_text="登录验证码秘密",
        )
        RequirementChunk.objects.create(
            document=private_doc, sequence=1, content="登录验证码私密规则", vector=embed("登录验证码私密规则")
        )
        results = search_documents(self.user, "登录验证码", limit=10)
        self.assertNotIn(private_doc.id, {result["id"] for result in results})

    def test_prompt_keeps_document_and_chunk_provenance(self):
        source = search_chunks(self.user, "验证码过期")[0]
        prompt = build_testcase_prompt("生成登录异常用例", [source])
        self.assertIn("登录需求.md#分块1", prompt)

    def test_site_capabilities_are_searchable_by_every_user(self):
        sync_site_capabilities()
        another_user = User.objects.create_user(username="another-rag-user", password="secret")
        results = search_chunks(another_user, "API 自动化测试用例 HTTP 断言")
        self.assertTrue(results)
        self.assertEqual(results[0]["document"], "ModeShift / 极客模式 / 测试用例生成器 / API 自动化")

        module_docs = RequirementDocument.objects.filter(owner=None, title__startswith="ModeShift /")
        self.assertGreaterEqual(module_docs.count(), 20)
        self.assertFalse(RequirementDocument.objects.filter(owner=None, title=SITE_CAPABILITIES_TITLE).exists())

    def test_document_search_can_filter_to_one_mode(self):
        sync_site_capabilities()
        results = search_documents(self.user, "日记", limit=10, mode="生活模式")
        self.assertTrue(results)
        self.assertTrue(all(item["title"].startswith("ModeShift / 生活模式 /") for item in results))

    def test_document_search_prefers_exact_feature_card_over_parent_page(self):
        sync_site_capabilities()
        results = search_documents(self.user, "快速保存日记", limit=5, mode="生活模式")
        self.assertTrue(results)
        self.assertIn("diary_quick_save", results[0]["title"])
