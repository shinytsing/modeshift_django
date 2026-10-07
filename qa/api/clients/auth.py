"""Authentication and profile HTTP operations, without test assertions."""

from __future__ import annotations

import requests

from qa.api.clients.transport import ApiTransport


class AuthApi:
    def __init__(self, transport: ApiTransport) -> None:
        self.http = transport

    def signup_form(self) -> requests.Response:
        return self.http.get("/accounts/signup/")

    def signup(self, email: str, password: str, csrf_token: str) -> requests.Response:
        return self.http.post(
            "/accounts/signup/",
            data={"email": email, "password1": password, "csrfmiddlewaretoken": csrf_token},
            headers={"Referer": self.http.url("/accounts/signup/")},
            allow_redirects=False,
        )

    def login_form(self) -> requests.Response:
        return self.http.get("/accounts/login/")

    def login(self, email: str, password: str, csrf_token: str) -> requests.Response:
        return self.http.post(
            "/accounts/login/",
            data={"login": email, "password": password, "csrfmiddlewaretoken": csrf_token},
            headers={"Referer": self.http.url("/accounts/login/")},
            allow_redirects=False,
        )

    def profile(self) -> requests.Response:
        return self.http.get("/users/api/profile/")

    def update_profile(self, **fields: str) -> requests.Response:
        return self.http.post("/users/api/profile/", json=fields)

    def logout(self) -> requests.Response:
        return self.http.post("/users/api/logout/")

    def browser_auth(self, path: str, **payload: str) -> requests.Response:
        return self.http.post(path, json=payload)

    def register_json(self, username: str, password: str, email: str) -> requests.Response:
        return self.browser_auth("/users/api/register/", username=username, password=password, email=email)

    def login_json(self, username: str, password: str) -> requests.Response:
        return self.browser_auth("/users/api/login/", username=username, password=password)
