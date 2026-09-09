"""Google OAuth 回调地址与 state 处理。

Google 控制台当前登记的是线上 redirect_uri。本地开发发起登录时
仍向 Google 发送该登记地址，由线上回调再安全跳回本机完成登录。
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.http import HttpRequest

GOOGLE_OAUTH_CALLBACK_PATH = "/auth/google/callback/"
GOOGLE_OAUTH_STATE_SALT = "google-oauth-return-origin"
GOOGLE_OAUTH_STATE_MAX_AGE = 600

_ALLOWED_RETURN_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://shenyiqing.xin",
    "https://www.shenyiqing.xin",
}


def get_registered_google_redirect_uri() -> str:
    """返回已在 Google 控制台登记的 redirect_uri。"""
    configured = (os.getenv("GOOGLE_OAUTH_REDIRECT_URI") or "").strip()
    if configured:
        return configured.rstrip("/") + "/"
    site_url = getattr(settings, "SITE_URL", "https://shenyiqing.xin").rstrip("/")
    return f"{site_url}{GOOGLE_OAUTH_CALLBACK_PATH}"


def get_request_origin(request: HttpRequest) -> str:
    """根据当前请求得到 origin（含端口）。"""
    host = request.get_host()
    hostname = host.split(":")[0].lower()
    forwarded = request.META.get("HTTP_X_FORWARDED_PROTO", "")
    scheme = forwarded.split(",")[0].strip() if forwarded else request.scheme
    if hostname in {"shenyiqing.xin", "www.shenyiqing.xin"}:
        return "https://shenyiqing.xin"
    return f"{scheme}://{host}"


def is_allowed_return_origin(origin: str) -> bool:
    """只允许跳回本机开发地址或正式站点，防止开放重定向。"""
    return origin.rstrip("/") in _ALLOWED_RETURN_ORIGINS


def ensure_session_key(request: HttpRequest) -> str:
    """确保 session 已创建并返回 session_key。"""
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    if not session_key:
        raise RuntimeError("无法创建登录 session")
    return session_key


def dump_google_oauth_state(request: HttpRequest) -> str:
    """生成带签名的 OAuth state，包含本机回跳 origin。"""
    payload: Dict[str, str] = {
        "sid": ensure_session_key(request),
        "return_origin": get_request_origin(request),
    }
    signer = TimestampSigner(salt=GOOGLE_OAUTH_STATE_SALT)
    return signer.sign(json.dumps(payload, separators=(",", ":")))


def load_google_oauth_state(signed_state: str) -> Dict[str, Any]:
    """校验并解析 OAuth state。"""
    signer = TimestampSigner(salt=GOOGLE_OAUTH_STATE_SALT)
    raw = signer.unsign(signed_state, max_age=GOOGLE_OAUTH_STATE_MAX_AGE)
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise BadSignature("OAuth state 格式无效")
    return payload


def build_google_callback_bounce_url(return_origin: str, query: Dict[str, str]) -> Optional[str]:
    """构造跳回本机回调的 URL；origin 不在白名单时返回 None。"""
    origin = return_origin.rstrip("/")
    if not is_allowed_return_origin(origin):
        return None
    return f"{origin}{GOOGLE_OAUTH_CALLBACK_PATH}?{urlencode(query)}"


def should_bounce_oauth_callback(request: HttpRequest, return_origin: str) -> bool:
    """当前请求不在发起登录的 origin 上时，需要跳回原站点。"""
    if not return_origin:
        return False
    current = get_request_origin(request).rstrip("/")
    target = return_origin.rstrip("/")
    return target != current and is_allowed_return_origin(target)
