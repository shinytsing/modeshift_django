"""Fitness API operations."""

from __future__ import annotations

import requests

from qa.api.clients.transport import ApiTransport


class FitnessApi:
    def __init__(self, transport: ApiTransport) -> None:
        self.http = transport

    def calculate_bmi(self, height: int, weight: int) -> requests.Response:
        return self.http.post("/tools/api/fitness/bmi/", json={"height": height, "weight": weight})
