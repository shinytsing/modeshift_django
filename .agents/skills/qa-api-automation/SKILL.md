---
name: qa-api-automation
description: Build, extend, and run QAToolBox API automation with pytest and requests. Use when adding REST endpoint checks, contract assertions, error-path coverage, local or deployed environment smoke tests, or API test reports in this repository.
---

# QAToolBox API automation

Read `.agents/qa-project-context.md` before writing tests.

## Workflow

1. Map each request to a consumer contract, a business risk, and one happy path plus one error path.
2. Add tests in `qa/api/`; use the `http_session` fixture and `BASE_URL`, never hardcoded hosts.
3. Assert exact status, JSON shape, field values/types, and response time. Do not accept broad status-code lists.
4. Run `python3 qa/scripts/run_suite.py`; use `QA_START_SERVER=0` with a non-production deployed test environment.
5. Review `qa/artifacts/allure-report/index.html` by API Feature/Story, including attached response evidence; turn every confirmed failure into a regression test.

## Guardrails

- Use `requests` only at the HTTP boundary; do not mock QAToolBox endpoints.
- Never run mutating checks against production.
- Add a timeout to every request through the shared fixture.
- Keep secrets in environment variables and exclude artifacts from Git.

See [API contract reference](references/contracts.md) for the initial routes and assertion rules.
