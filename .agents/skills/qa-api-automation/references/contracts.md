# API contract reference

`GET /health/` must return HTTP 200, JSON content, exactly `status`, `timestamp`, and
`version`, and the value `status: healthy`.

`GET /api/tests/status/` must return HTTP 200 and exactly `is_running`, `progress`,
`current_test`, `status`, and `timestamp`. `progress` is an integer in the inclusive
range 0 through 100.

`POST /api/tests/status/` without a CSRF token must return HTTP 403. This is the baseline
negative-path test and proves that an unsafe request cannot silently change test state.

`GET /api/tests/results/` must keep the overall total equal to passed + failed + skipped +
broken, and every category total equal to passed + failed. This catches dashboard-card drift.

`POST /api/tests/run/` with `{"test_types": ["api", "ui"]}` must return HTTP 200, `started`,
and echo the requested types in the same order. This catches a UI-to-runner request mapping bug.
