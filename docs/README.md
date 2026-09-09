# Documentation index

The repository keeps runnable Django and deployment entry points at the project root. Supporting
material is grouped here so that it does not obscure the day-to-day workflow.

| Location | Contents |
| --- | --- |
| [portfolio/](portfolio/) | Interview and project-presentation material |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Canonical application, QA, CI, and legacy-tool entry points |

## Current quality gate

The maintained test gate is `qa/`, not the historical diagnostic scripts at the repository root.

```bash
python3 qa/scripts/run_suite.py  # API + UI, reports to qa/artifacts/
python3 qa/run_api.py            # requests contracts only
python3 qa/run_ui.py             # Playwright UI only
```

Open `qa/artifacts/allure-report/index.html` after a run. Generated reports, local environments,
cookies, verification-code datasets, and backup files are intentionally excluded from Git.

Historical one-off scripts may exist under `scripts/manual/legacy/` on a developer workstation.
They are deliberately excluded from version control because they can contain local paths, external
service targets, or test credentials; they are not part of the maintained QA gate.
