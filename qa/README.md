# QAToolBox quality-gate showcase

This isolated suite demonstrates shift-left testing with one reproducible command:

```bash
python3 -m pip install -r qa/requirements.txt
python3 -m playwright install chromium
python3 qa/scripts/run_suite.py
```

It starts Django, verifies the health contract, runs `pytest + requests` API contracts and
`pytest + Playwright` UI smoke checks, and rebuilds the evidence directory under `qa/artifacts/`.

### 本地与门禁使用同一套代码

GitHub 门禁使用 Python 3.11；本地也使用项目的 `.venv311/bin/python`，
不要混用系统 Python 或其他虚拟环境。依赖来源为 `requirements.txt` 和 `qa/requirements.txt`。
在已有本地 Django 服务运行时，以无头模式执行同一个门禁入口：

```bash
CI=true QA_START_SERVER=0 QA_BROWSER_CHANNEL=chrome .venv311/bin/python qa/scripts/run_suite.py
```

macOS 使用已安装的 Chrome，Linux CI 使用 Playwright 安装的 Chromium；
这是浏览器发行版的环境差异，不是两套测试代码。简历卡片执行的业务用例与门禁共用
`qa/ui/test_authenticated_bmi_flow.py`，不维护另一份注册、登录或 BMI 操作。
项目若位于 iCloud 同步的桌面目录，必须保证源码、模板和 `.env` 已下载并保留在本机，
云端占位文件会使文件读取和页面请求卡住；不要通过延长超时或删减断言掩盖问题。

To run only the read-only smoke subset against a dedicated deployed test environment, do not start Django locally:

```bash
BASE_URL=https://your-test-environment.example QA_START_SERVER=0 python3 qa/scripts/run_suite.py --smoke
```

Do not target production with the full-suite command. The runner rejects remote targets unless
`--smoke` is selected, because other tests can start test runs as well as register users.
Stateful registration tests run only on loopback:
they register uniquely labelled QA users and remove those exact identities in fixture teardown,
including after an assertion failure. `QA_ALLOW_AUTH_MUTATIONS` is not an override: the current
API has no safe remote account cleanup contract, so stateful cases are skipped on remote targets.

### Focused local runs

```bash
# requests API contracts only
python3 qa/run_api.py

# Playwright UI scenarios only
python3 qa/run_ui.py

# QA runs without an artificial delay; slow motion is only for the resume-page demo.
QA_HEADED=0 python3 qa/run_ui.py

# Only the complete stateful API + visible-browser journey
python3 qa/scripts/run_suite.py --e2e

# Fast read-only health/dashboard smoke subset
python3 qa/scripts/run_suite.py --smoke
```

All three commands use the same server lifecycle, `BASE_URL` contract, artifact location, and
Allure rendering. The full-suite command is the CI quality gate.

## Allure report

Open `qa/artifacts/allure-report/index.html` after a run. It contains both categories:

- **API 自动化 - requests**: health, response schema, timing, and CSRF negative-path evidence.
- **UI 自动化 - Playwright**: dashboard navigation, visible assertions, and a browser screenshot.

The suite contains API contracts (including CSRF, method boundaries, statistics, history,
result consistency, and an authentication/profile state machine) and UI scenarios. Parameterized
skill-card checks count as separate pytest cases. The testcase-generator UI scenario exercises model
selection, knowledge search, selected document IDs, and visible source attribution with stubbed
generation responses.
`--e2e` selects every test marked `e2e`, including the registered-user browser journeys.
The flagship path visibly performs **注册 → 退出 → 登录 → 受保护个人资料 → BMI 计算**;
the requests scenario carries the same session across **匿名拒绝 → 注册 → 登出 → 登录 →
资料更新 → BMI 接口 → 登出拒绝**. The unified runner verifies health before pytest starts.

## AI output quality (offline)

`qa/ai_eval/login_otp_expired.json` is a reviewed requirement sample. The tests in
`qa/api/test_ai_eval.py` check that a valid case passes and that duplicates, missing fields,
placeholders, or missing required concepts fail. To check a **saved real-model response**:

```bash
.venv311/bin/python -m qa.ai_eval.evaluate /path/to/model-output.md \
  --requirements qa/ai_eval/login_otp_expired.json
```

This is a deterministic structural/keyword gate, not a model-quality score. The browser test
for knowledge selection still stubs generation responses; it does not prove grounding,
factual correctness, or that a specific model produced the output. A reviewed real-model
sample and source-attribution checks are required before claiming those properties.

## 测试分层

- `qa/ui/pages/` 是 Python Playwright Page Object：封装页面定位和用户操作，不放业务断言。
- `qa/api/clients/` 是 requests 的 API 对应层：`ApiTransport` 统一 `BASE_URL`、超时和会话；
  `AuthApi`、`DashboardApi`、`FitnessApi`、`ResumeApi` 封装业务端点，不判断测试结果。
- `qa/api/conftest.py` 为每个测试建立独立的 HTTP Session，测试结束关闭；同一测试内保留
  Cookie/CSRF 连续状态。`qa/conftest.py` 统一 UI 和 API 的 `BASE_URL`。
- `qa/ui/test_*.py` 与 `qa/api/test_*.py` 保留场景编排、断言和 Allure 证据。简历卡片仍
  执行与 CI 相同的注册→登录→BMI 用例，演示慢动作不会影响质量门禁。

## Other evidence

- `junit.xml`: machine-readable CI result
- `report.html`: pytest execution report
- `allure-results/`: Allure source data
- `allure-report/`: rendered Allure HTML report for API and UI tests
- `playwright/`: failure-only screenshot, video, and trace evidence

The contracts and risk rationale live in [project context](../.agents/qa-project-context.md) and
the reusable API/UI agent workflows live under `.agents/skills/`.
