"""Resume demo endpoint boundary operations."""

from __future__ import annotations

import requests

from qa.api.clients.transport import ApiTransport


class ResumeApi:
    def __init__(self, transport: ApiTransport) -> None:
        self.http = transport

    def execution_with_get(self) -> requests.Response:
        return self.http.get("/resume-3d/run-ui/")

    def execution_without_csrf(self) -> requests.Response:
        return self.http.post("/resume-3d/run-ui/")
