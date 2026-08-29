# Project navigation

This repository contains active Django code alongside historical experiments and manually run
diagnostics. Use the following entry points for day-to-day development and quality validation.

| Area | Canonical location | Use it for |
| --- | --- | --- |
| Django application | `apps/`, `config/`, `templates/`, `manage.py` | Product code, settings, routes, templates, and local server startup |
| Deployment | `docker/`, `start-gunicorn.sh`, `start*.sh` | Container and server operations |
| Shift-left QA gate | `qa/` | Maintained pytest API contracts, Playwright UI scenarios, and Allure evidence |
| CI workflow | `.github/workflows/testing-system.yml` | Pull-request and branch quality gate |
| Product and operations docs | `docs/guides/`, `docs/deployment/`, `docs/testing/` | Setup, deployment, and presentation material |
| Historical tests and diagnostics | `tests/`, `test_files/`, `testing_system/`, root `test_*` files | Legacy/manual references; do not use as the CI entry point |

## Quality-gate commands

```bash
# Full API + UI suite; this is what GitHub Actions executes.
python3 qa/scripts/run_suite.py

# Focused suites for local debugging.
python3 qa/run_api.py
python3 qa/run_ui.py
```

Reports are generated under `qa/artifacts/` and intentionally excluded from Git. Open
`qa/artifacts/allure-report/index.html` after a run. For a deployed test environment, set
`BASE_URL` and `QA_START_SERVER=0`; never run these checks against production.

## Compatibility policy

Historical scripts have not been moved or deleted: they may still be used by personal workflows
or deployment operations. New QA work belongs in `qa/`; gradual migration from legacy tests should
be done one executable path at a time, with a passing replacement before removal.
