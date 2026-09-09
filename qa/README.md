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

Do not target production with this command. The full suite now includes a registration journey
that creates a uniquely labelled `qa-e2e-...@example.invalid` user. It runs automatically on
localhost and CI; a dedicated deployed test environment additionally needs explicit opt-in:

```bash
BASE_URL=https://your-test-environment.example QA_START_SERVER=0 QA_ALLOW_AUTH_MUTATIONS=1 \
  python3 qa/scripts/run_suite.py
```

### Focused local runs

```bash
# requests API contracts only
python3 qa/run_api.py

# Playwright UI scenarios only
python3 qa/run_ui.py

# Local UI defaults to a visible Chromium window. Adjust or disable the delay as needed.
QA_SLOW_MO=500 python3 qa/run_ui.py
QA_HEADED=0 python3 qa/run_ui.py

# Only the complete stateful API + visible-browser journey
python3 qa/scripts/run_suite.py --e2e
```

All three commands use the same server lifecycle, `BASE_URL` contract, artifact location, and
Allure rendering. The full-suite command is the CI quality gate.

## Allure report

Open `qa/artifacts/allure-report/index.html` after a run. It contains both categories:

- **API 自动化 - requests**: health, response schema, timing, and CSRF negative-path evidence.
- **UI 自动化 - Playwright**: dashboard navigation, visible assertions, and a browser screenshot.

The showcase suite contains 14 independent tests: 9 API contracts (including CSRF, method-boundary,
statistics, history, result consistency, and an authentication/profile state machine) and 5 UI
scenarios. The flagship `--e2e` path visibly performs **注册 → 退出 → 登录 → 受保护个人资料 →
BMI 计算**, while the requests scenario carries the same session across **匿名拒绝 → 注册 → 登出 →
登录 → 资料更新 → BMI 接口 → 登出拒绝**. The unified runner verifies health before pytest starts.

## Other evidence

- `junit.xml`: machine-readable CI result
- `report.html`: pytest execution report
- `allure-results/`: Allure source data
- `allure-report/`: rendered Allure HTML report for API and UI tests
- `playwright/`: failure-only screenshot, video, and trace evidence

The contracts and risk rationale live in [project context](../.agents/qa-project-context.md) and
the reusable API/UI agent workflows live under `.agents/skills/`.
