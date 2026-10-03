import json
import os
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from apps.tools.models.rag_models import RequirementChunk, RequirementDocument
from apps.tools.services.rag_service import embed


class DocumentContextGenerationAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="generation-owner", password="secret")
        self.other_user = User.objects.create_user(username="generation-other", password="secret")
        self.client = APIClient()
        self.client.force_login(self.user)
        self.own_document = self._document(self.user, "自己的登录说明.md", "验证码五分钟后过期")
        self.private_document = self._document(self.other_user, "他人的私密文档.md", "不可泄漏的登录规则")
        self.shared_document = self._document(None, "共享规则.md", "共享登录规则")

    def _document(self, owner, title, content):
        document = RequirementDocument.objects.create(
            owner=owner,
            title=title,
            source_file=f"rag_requirements/{title}",
            source_type="md",
            extracted_text=content,
        )
        RequirementChunk.objects.create(document=document, sequence=1, content=content, vector=embed(content))
        return document

    def test_document_search_returns_only_owned_and_shared_documents(self):
        response = self.client.get("/tools/api/rag/documents/search/", {"q": "登录验证码规则"})
        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.json()["results"]}
        self.assertIn(self.own_document.id, ids)
        self.assertIn(self.shared_document.id, ids)
        self.assertNotIn(self.private_document.id, ids)

    def test_anonymous_document_search_is_rejected(self):
        self.client.logout()
        response = self.client.get("/tools/api/rag/documents/search/", {"q": "登录"})
        self.assertEqual(response.status_code, 401)

    @patch("apps.tools.async_test_cases_api.get_llm_service")
    @patch("apps.tools.async_test_cases_api.get_task_manager")
    def test_generation_rejects_another_users_document_before_task_creation(self, manager, llm):
        llm.return_value.resolve_model.return_value = ("deepseek", "deepseek-chat")
        response = self.client.post(
            "/tools/api/async/generate-testcases/",
            {
                "requirement": "登录",
                "prompt": "生成用例",
                "model_id": "deepseek:deepseek-chat",
                "knowledge_document_ids": [self.private_document.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        manager.return_value.create_task.assert_not_called()

    @patch("apps.tools.async_test_cases_api.get_llm_service")
    @patch("apps.tools.async_test_cases_api.get_task_manager")
    def test_generation_rejects_unconfigured_model_without_fallback(self, manager, llm):
        llm.return_value.resolve_model.side_effect = ValueError("not configured")
        response = self.client.post(
            "/tools/api/async/generate-testcases/",
            {"requirement": "登录", "prompt": "生成用例", "model_id": "fake:model", "knowledge_document_ids": []},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        manager.return_value.create_task.assert_not_called()

    @patch("apps.tools.async_test_cases_api.get_llm_service")
    @patch("apps.tools.async_test_cases_api.get_task_manager")
    def test_generation_passes_only_selected_authorized_evidence(self, manager, llm):
        llm.return_value.resolve_model.return_value = ("deepseek", "deepseek-chat")
        manager.return_value.create_task.return_value = "task-123"
        response = self.client.post(
            "/tools/api/async/generate-testcases/",
            {
                "requirement": "验证码过期",
                "prompt": "生成边界用例",
                "model_id": "deepseek:deepseek-chat",
                "knowledge_document_ids": [self.own_document.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        kwargs = manager.return_value.create_task.call_args.kwargs
        self.assertEqual(kwargs["model_id"], "deepseek:deepseek-chat")
        self.assertEqual({source["document_id"] for source in kwargs["evidence"]}, {self.own_document.id})
        self.assertEqual(kwargs["user_id"], f"user:{self.user.pk}")

    @patch("apps.tools.async_test_cases_api.get_llm_service")
    @patch("apps.tools.async_test_cases_api.get_task_manager")
    def test_generation_keeps_prompt_optional(self, manager, llm):
        llm.return_value.resolve_model.return_value = ("deepseek", "deepseek-chat")
        manager.return_value.create_task.return_value = "task-without-custom-prompt"
        response = self.client.post(
            "/tools/api/async/generate-testcases/",
            {"requirement": "登录", "prompt": "", "model_id": "deepseek:deepseek-chat", "knowledge_document_ids": []},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(manager.return_value.create_task.call_args.kwargs["user_prompt"], "")

    def test_task_status_rejects_another_users_task(self):
        task = {
            "task-foreign": {
                "id": "task-foreign",
                "user_id": f"user:{self.other_user.pk}",
                "status": "completed",
                "progress": 100,
                "created_at": "2026-01-01T00:00:00",
                "started_at": None,
                "completed_at": "2026-01-01T00:01:00",
                "result": "private result",
                "error": None,
            }
        }
        with tempfile.TemporaryDirectory() as storage:
            path = os.path.join(storage, "tasks.json")
            with open(path, "w", encoding="utf-8") as output:
                json.dump(task, output)
            fake_manager = type("TaskManager", (), {"storage_dir": storage})
            with patch("apps.tools.async_task_manager.AsyncTaskManager", fake_manager):
                response = self.client.get("/tools/api/async/task/task-foreign/")
        self.assertEqual(response.status_code, 403)

    def test_task_download_does_not_expose_another_users_private_result(self):
        task = {
            "task-download-private": {
                "id": "task-download-private",
                "user_id": f"user:{self.other_user.pk}",
                "status": "completed",
                "progress": 100,
                "created_at": "2026-01-01T00:00:00",
                "started_at": None,
                "completed_at": "2026-01-01T00:01:00",
                "result": "private source context",
                "error": None,
            }
        }
        with tempfile.TemporaryDirectory() as storage:
            with open(os.path.join(storage, "tasks.json"), "w", encoding="utf-8") as output:
                json.dump(task, output)
            fake_manager = type("TaskManager", (), {"storage_dir": storage})
            with patch("apps.tools.async_task_manager.AsyncTaskManager", fake_manager):
                response = self.client.get("/tools/api/async/task/task-download-private/download/txt/")
        self.assertEqual(response.status_code, 404)

    def test_task_list_does_not_return_another_users_requirement(self):
        data = {
            "mine": {
                "id": "mine",
                "user_id": f"user:{self.user.pk}",
                "requirement": "my req",
                "status": "pending",
                "progress": 0,
                "created_at": "2026-01-02T00:00:00",
            },
            "theirs": {
                "id": "theirs",
                "user_id": f"user:{self.other_user.pk}",
                "requirement": "secret req",
                "status": "pending",
                "progress": 0,
                "created_at": "2026-01-03T00:00:00",
            },
        }
        with tempfile.TemporaryDirectory() as storage:
            with open(os.path.join(storage, "tasks.json"), "w", encoding="utf-8") as output:
                json.dump(data, output)
            fake_manager = type("TaskManager", (), {"storage_dir": storage})
            with patch("apps.tools.async_task_manager.AsyncTaskManager", fake_manager):
                response = self.client.get("/tools/api/async/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([task["id"] for task in response.json()["tasks"]], ["mine"])
