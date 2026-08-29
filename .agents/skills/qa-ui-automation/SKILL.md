---
name: qa-ui-automation
description: Build, extend, and run QAToolBox UI automation with pytest and Playwright. Use when adding browser checks, stable user-facing locators, failure traces/screenshots, local or CI UI runs, or UI regression reports in this repository.
---

# QAToolBox UI automation

Read `.agents/qa-project-context.md` before writing tests.

## Workflow

1. Convert a user-visible requirement into one independently runnable scenario in `qa/ui/`.
2. Use `get_by_role`, `get_by_text`, or `get_by_label` before CSS selectors.
3. Assert visible outcomes with Playwright web-first assertions. Never use fixed sleeps.
4. Execute `python3 qa/scripts/run_suite.py`; Playwright stores trace and screenshot evidence on failure.
5. Inspect `qa/artifacts/allure-report/index.html`, including the Playwright screenshot and failure traces, before reporting a result.

## Guardrails

- Keep tests anonymous and independent; do not use production accounts or stored sessions.
- Mock only third-party boundaries, never the page behavior under test.
- Make selectors reflect user-visible semantics so UI refactors do not cause needless failures.
- Use `BASE_URL` for all navigation; no hardcoded server host or port.

See [UI scenario reference](references/scenarios.md) for the first left-shift smoke path.
