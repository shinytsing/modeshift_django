# QAToolBox QA project context

## Scope

Use this repository's `qa/` suite for the public, deterministic quality-gate demo.
The suite is intentionally independent of `tests/` and `test_files/` legacy suites.

## Supported contracts

| Route | Consumer contract | Risk covered |
|---|---|---|
| `GET /health/` | JSON health signal with a healthy status and numeric timestamp | deployment readiness and schema drift |
| `GET /api/tests/status/` | JSON execution state, progress, and current test | dashboard/API integration |
| `POST /api/tests/status/` without a CSRF token | rejected with HTTP 403 | unsafe-request protection |
| `/testing-dashboard/` | visible test dashboard title, heading, and loaded functional total | browser-visible regression |

## Commands

- Install: `python3 -m pip install -r qa/requirements.txt && python3 -m playwright install chromium`
- Local or CI server: `python3 qa/scripts/run_suite.py`
- Deployed environment: `BASE_URL=https://example.test QA_START_SERVER=0 python3 qa/scripts/run_suite.py`

## Evidence

Read `qa/artifacts/allure-report/index.html` after every run; it is the primary API/UI
showcase report. Keep `junit.xml`, `report.html`, `allure-results/`, and Playwright failure
traces/screenshots as supporting evidence. Never publish credentials, cookies, or production data.
