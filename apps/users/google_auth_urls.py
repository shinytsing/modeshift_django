"""
Google Auth 专用URL配置
提供直接的 /auth/google/ 路径，避免 /users/ 前缀
"""

from django.urls import path
from . import google_auth_proxy

app_name = "auth"

urlpatterns = [
    # Google Auth 代理
    path("", google_auth_proxy.GoogleAuthProxyView.as_view(), name="google_auth_proxy"),
    path("callback/", google_auth_proxy.GoogleAuthCallbackView.as_view(), name="google_auth_callback"),
    path("status/", google_auth_proxy.GoogleAuthStatusView.as_view(), name="google_auth_status"),
    path("api/initiate/", google_auth_proxy.google_auth_initiate, name="google_auth_initiate"),
]
