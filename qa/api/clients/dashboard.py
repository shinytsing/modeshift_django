"""Testing-dashboard API operations."""

from __future__ import annotations

import requests

from qa.api.clients.transport import ApiTransport


class DashboardApi:
    def __init__(self, transport: ApiTransport) -> None:
        self.http = transport

    def health(self) -> requests.Response:
        return self.http.get("/health/")

    def status(self) -> requests.Response:
        return self.http.get("/api/tests/status/")

    def status_without_csrf(self) -> requests.Response:
        return self.http.post("/api/tests/status/")

    def results(self) -> requests.Response:
        return self.http.get("/api/tests/results/")

    def run(self, test_types: list[str]) -> requests.Response:
        return self.http.post("/api/tests/run/", json={"test_types": test_types})

    def run_with_get(self) -> requests.Response:
        return self.http.get("/api/tests/run/")

    def stats(self) -> requests.Response:
        return self.http.get("/api/tests/stats/")

    def history(self) -> requests.Response:
        return self.http.get("/api/tests/history/")
