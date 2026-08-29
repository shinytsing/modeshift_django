# QAToolBox quality-gate showcase

This isolated suite demonstrates shift-left testing with one reproducible command:

```bash
python3 -m pip install -r qa/requirements.txt
python3 -m playwright install chromium
python3 qa/scripts/run_suite.py
```

It starts Django, verifies the health contract, runs `pytest + requests` API contracts and
`pytest + Playwright` UI smoke checks, and rebuilds the evidence directory under `qa/artifacts/`.

To run the same suite against a dedicated deployed test environment, do not start Django locally:

```bash
BASE_URL=https://your-test-environment.example QA_START_SERVER=0 python3 qa/scripts/run_suite.py
```

Do not target production with this command. The initial endpoints are read-only, but future test
cases may create test data.

### Focused local runs

```bash
# requests API contracts only
python3 qa/run_api.py

# Playwright UI scenarios only
python3 qa/run_ui.py

# Local UI defaults to a visible Chromium window. Adjust or disable the delay as needed.
QA_SLOW_MO=500 python3 qa/run_ui.py
QA_HEADED=0 python3 qa/run_ui.py
```

All three commands use the same server lifecycle, `BASE_URL` contract, artifact location, and
Allure rendering. The full-suite command is the CI quality gate.

## Allure report

Open `qa/artifacts/allure-report/index.html` after a run. It contains both categories:

- **API 自动化 - requests**: health, response schema, timing, and CSRF negative-path evidence.
- **UI 自动化 - Playwright**: dashboard navigation, visible assertions, and a browser screenshot.

The showcase suite contains 12 independent tests: 8 API contracts (including CSRF, method-boundary,
statistics, history, and result-consistency checks) and 4 UI scenarios. The unified runner also
verifies health before pytest starts.

## Other evidence

- `junit.xml`: machine-readable CI result
- `report.html`: pytest execution report
- `allure-results/`: Allure source data
- `allure-report/`: rendered Allure HTML report for API and UI tests
- `playwright/`: failure-only screenshot, video, and trace evidence

The contracts and risk rationale live in [project context](../.agents/qa-project-context.md) and
the reusable API/UI agent workflows live under `.agents/skills/`.
