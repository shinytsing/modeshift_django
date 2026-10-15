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
| allauth `/accounts/signup/` + `/accounts/login/` | CSRF-backed registration and password login establish a session | broken authentication continuity |
| `/users/api/profile/` | anonymous reads are 401; the same session can read and update a profile | access control and session persistence |
| `/tools/fitness/tools/bmi-calculator/` + `POST /tools/api/fitness/bmi/` | an authenticated user can submit BMI inputs and see the result | protected feature/API integration |

## Commands

- Install: `python3 -m pip install -r qa/requirements.txt && python3 -m playwright install chromium`
- Local or CI server: `python3 qa/scripts/run_suite.py`
- Deployed test environment, read-only subset: `BASE_URL=https://example.test QA_START_SERVER=0 python3 qa/scripts/run_suite.py --smoke`
- Auth/API/UI continuous journey only: `python3 qa/scripts/run_suite.py --e2e`

## Evidence

Read `qa/artifacts/allure-report/index.html` after every run; it is the primary API/UI
showcase report. Keep `junit.xml`, `report.html`, `allure-results/`, and Playwright failure
traces/screenshots as supporting evidence. Never publish credentials, cookies, or production data.

The registration journey creates a uniquely labelled `qa-e2e-...@example.invalid` local user.
It is allowed only for loopback targets, and a fixture deletes that exact identity after the test.
Remote stateful QA remains disabled until a safe remote cleanup contract exists; never point the
mutation suite at production.
