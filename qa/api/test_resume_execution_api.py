"""The browser journey must require an explicit, CSRF-protected POST."""

import json
import os
from subprocess import CompletedProcess
from unittest.mock import patch

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


@pytest.mark.api
def test_public_demo_runs_read_only_playwright_without_pytest_or_auth_mutations():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    import django
    from django.test import Client

    django.setup()
    client = Client(enforce_csrf_checks=True)
    page = client.get("/resume-3d/")
    assert page.status_code == 200
    token = client.cookies["csrftoken"].value
    completed = CompletedProcess(
        args=[],
        returncode=0,
        stdout=json.dumps({"status": "passed", "steps": ["打开简历页"], "screenshot": "AA=="}),
        stderr="",
    )
    with patch("views.subprocess.run", return_value=completed) as runner:
        response = client.post("/resume-3d/run-ui/", HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 200
    assert response.json()["output"] == "打开简历页"
    assert response.json()["screenshot"] == "AA=="
    command = runner.call_args.args[0]
    assert command[-2:] == ["-m", "qa.ui.public_demo"]
    assert "pytest" not in command
    assert runner.call_args.kwargs["env"]["BASE_URL"].startswith("http://127.0.0.1:")
