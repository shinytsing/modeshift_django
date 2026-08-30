from django.contrib.auth.models import User
from django.test import TestCase

from apps.tools.models.rag_models import RequirementChunk, RequirementDocument
from apps.tools.services.rag_service import build_testcase_prompt, embed, search_chunks


class RagServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="rag-user", password="secret")
        document = RequirementDocument.objects.create(
            owner=self.user, title="登录需求.md", source_file="rag_requirements/login.md", source_type="md", extracted_text="登录支持验证码过期校验。"
        )
        RequirementChunk.objects.create(document=document, sequence=1, content="用户登录时验证码五分钟后失效，过期后必须提示重新获取。", vector=embed("用户登录时验证码五分钟后失效，过期后必须提示重新获取。"))
        RequirementChunk.objects.create(document=document, sequence=2, content="个人资料可以更新昵称和头像。", vector=embed("个人资料可以更新昵称和头像。"))

    def test_search_returns_ranked_source_chunks(self):
        results = search_chunks(self.user, "登录验证码过期怎么测试")
        self.assertEqual(results[0]["sequence"], 1)
        self.assertIn("验证码", results[0]["content"])

    def test_prompt_keeps_document_and_chunk_provenance(self):
        source = search_chunks(self.user, "验证码过期")[0]
        prompt = build_testcase_prompt("生成登录异常用例", [source])
        self.assertIn("登录需求.md#分块1", prompt)
