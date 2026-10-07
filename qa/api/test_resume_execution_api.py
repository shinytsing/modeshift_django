"""The browser journey must require an explicit, CSRF-protected POST."""

import pytest

from qa.api.clients.resume import ResumeApi


@pytest.mark.api
def test_opening_execution_url_does_not_launch_browser(resume_api: ResumeApi):
    response = resume_api.execution_with_get()
    assert response.status_code == 405


@pytest.mark.api
def test_execution_without_csrf_token_is_rejected(resume_api: ResumeApi):
    response = resume_api.execution_without_csrf()
    assert response.status_code == 403
