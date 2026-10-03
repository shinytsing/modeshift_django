from unittest.mock import patch
import os
from requests.exceptions import ConnectionError

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from apps.tools.services.llm_service import LLMProvider, OllamaService, get_llm_service


class LLMModelCatalogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="model-user", password="secret")
        self.client = APIClient()
        self.client.force_login(self.user)
        self.manager = get_llm_service()
        for provider, service in self.manager.services.items():
            if hasattr(service, "api_key"):
                service.api_key = None
        self.manager.services[LLMProvider.OLLAMA].list_models = lambda: []

    def test_catalog_reports_configured_cloud_model_without_exposing_credential_or_calling_cloud(self):
        deepseek = self.manager.services[LLMProvider.DEEPSEEK]
        deepseek.api_key = "sk-test-secret-value"
        with patch("apps.tools.services.llm_service._global_session.post") as cloud_post:
            response = self.client.get("/tools/api/llm/models/")
        self.assertEqual(response.status_code, 200)
        model = next(item for item in response.json()["models"] if item["provider"] == "deepseek")
        self.assertEqual(model["status"], "configured_unverified")
        self.assertNotIn("sk-test-secret-value", response.content.decode())
        self.assertNotIn("api_key", model)
        self.assertEqual(model["label"], "DeepSeek / deepseek-chat")
        cloud_post.assert_not_called()

    def test_catalog_does_not_show_provider_that_is_not_usable(self):
        groq = self.manager.services[LLMProvider.GROQ]
        groq.api_key = "not-a-groq-key"
        response = self.client.get("/tools/api/llm/models/")
        self.assertNotIn("groq", {item["provider"] for item in response.json()["models"]})

    def test_catalog_includes_models_found_from_local_ollama_tags(self):
        self.manager.services[LLMProvider.OLLAMA].list_models = lambda: ["llama3:8b"]
        response = self.client.get("/tools/api/llm/models/")
        model = next(item for item in response.json()["models"] if item["provider"] == "ollama")
        self.assertEqual(model["model"], "llama3:8b")
        self.assertEqual(model["status"], "available_local")

    @patch("apps.tools.services.llm_service._global_session.get")
    def test_ollama_discovery_uses_configured_local_host_url(self, get):
        get.return_value.json.return_value = {"models": [{"name": "qwen2.5:7b"}]}
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://host.docker.internal:11434/"}):
            service = OllamaService()
        self.assertEqual(service.list_models(), ["qwen2.5:7b"])
        get.assert_called_once_with("http://host.docker.internal:11434/api/tags", timeout=1)

    def test_catalog_stays_healthy_when_ollama_is_offline(self):
        self.manager.services[LLMProvider.OLLAMA].list_models = lambda: (_ for _ in ()).throw(ConnectionError("offline"))
        response = self.client.get("/tools/api/llm/models/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["models"], [])

    def test_catalog_is_rejected_for_anonymous_users(self):
        self.client.logout()
        response = self.client.get("/tools/api/llm/models/")
        self.assertEqual(response.status_code, 403)

    def test_generation_uses_explicitly_selected_provider_and_model(self):
        selected = self.manager.services[LLMProvider.GROQ]
        selected.api_key = "gsk_configured-for-test"
        with patch.object(self.manager, "_generate_with_specific_service", return_value="# cases") as generate:
            with patch.object(self.manager, "_is_content_complete", return_value=True):
                result = self.manager.generate_test_cases("需求", "我的提示词", model_id=f"groq:{selected.model}")
        self.assertEqual(result, "# cases")
        self.assertEqual(generate.call_args.args[2], LLMProvider.GROQ)
        self.assertEqual(generate.call_args.kwargs["model"], selected.model)
        self.assertIn("我的提示词", generate.call_args.args[0])
        self.assertIn("资深测试工程师", generate.call_args.args[1])

    def test_every_continuation_call_keeps_the_selected_model_and_system_rules(self):
        selected = self.manager.services[LLMProvider.GROQ]
        selected.api_key = "gsk_configured-for-test"
        with patch.object(
            self.manager, "_generate_with_specific_service", side_effect=["partial cases", "continued cases"]
        ) as generate:
            with patch.object(self.manager, "_is_content_complete", side_effect=[False, True]):
                with patch.object(self.manager, "_clean_and_format_content", side_effect=lambda content: content):
                    self.manager.generate_test_cases("需求", "我的提示词 {requirement}", model_id=f"groq:{selected.model}")
        self.assertEqual(generate.call_count, 2)
        for invocation in generate.call_args_list:
            self.assertEqual(invocation.args[2], LLMProvider.GROQ)
            self.assertEqual(invocation.kwargs["model"], selected.model)
            self.assertIn("资深测试工程师", invocation.args[1])

    def test_unknown_model_is_rejected_instead_of_falling_back(self):
        with self.assertRaisesRegex(ValueError, "模型未配置"):
            self.manager.resolve_model("arbitrary-provider:arbitrary-model")
