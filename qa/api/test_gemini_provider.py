"""Provider boundary contracts without network requests or paid model usage."""

from unittest.mock import Mock

import pytest

from apps.tools.services import llm_service


@pytest.mark.api
def test_gemini_without_a_key_rejects_generation(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    provider = llm_service.GeminiService()
    assert provider.is_available() is False
    with pytest.raises(ValueError, match="密钥未配置"):
        provider.generate_content("requirement")


@pytest.mark.api
def test_gemini_accepts_google_key_and_preserves_prompt_parts(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key-not-a-credential")
    response = Mock()
    response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "case "}, {"text": "one"}]}}]}
    post = Mock(return_value=response)
    monkeypatch.setattr(llm_service._global_session, "post", post)
    provider = llm_service.GeminiService()
    assert provider.is_available() is True
    assert provider.generate_content("requirement", system_prompt="instructions", max_tokens=42) == "case one"
    response.raise_for_status.assert_called_once()
    options = post.call_args.kwargs
    assert options["json"]["contents"][0]["parts"] == [{"text": "requirement"}]
    assert options["json"]["systemInstruction"]["parts"] == [{"text": "instructions"}]
    assert options["json"]["generationConfig"]["maxOutputTokens"] == 42
    assert options["timeout"] == 120


@pytest.mark.api
def test_gemini_empty_response_is_an_observable_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-a-credential")
    response = Mock()
    response.json.return_value = {}
    monkeypatch.setattr(llm_service._global_session, "post", Mock(return_value=response))
    with pytest.raises(ValueError, match="空内容"):
        llm_service.GeminiService().generate_content("requirement")
