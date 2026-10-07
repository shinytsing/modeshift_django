"""One configured HTTP transport per test; response assertions stay in tests."""

from __future__ import annotations

from typing import Any

import requests


class ApiTransport:
    def __init__(self, session: requests.Session, base_url: str, timeout: float = 3.0) -> None:
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(self.url(path), **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(self.url(path), **kwargs)
