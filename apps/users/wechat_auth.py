import hashlib
import secrets

import requests
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core import signing
from django.db import transaction
from django.http import JsonResponse
from django.utils.crypto import get_random_string

from .models import UserMembership, UserRole, UserStatus, WeChatMiniProgramIdentity

TOKEN_SALT = "peep-wechat-token"
TOKEN_MAX_AGE = 30 * 24 * 60 * 60


def issue_token(user):
    return signing.dumps({"uid": user.pk}, salt=TOKEN_SALT, compress=True)


def user_from_token(request):
    token = request.headers.get("X-Peep-Token", "")
    if not token:
        return None
    try:
        payload = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
        return User.objects.get(pk=payload["uid"], is_active=True)
    except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist, KeyError, TypeError):
        return None


def require_wechat_user(view):
    def wrapped(request, *args, **kwargs):
        user = user_from_token(request)
        if user is None:
            return JsonResponse({"error": "微信登录已失效，请重新登录"}, status=401)
        request.user = user
        return view(request, *args, **kwargs)

    return wrapped


def exchange_code(code):
    appid = getattr(settings, "WECHAT_MINIPROGRAM_APPID", "")
    secret = getattr(settings, "WECHAT_MINIPROGRAM_SECRET", "")
    if not appid or not secret:
        raise RuntimeError("WECHAT_MINIPROGRAM_APPID/SECRET 未配置")
    response = requests.get(
        "https://api.weixin.qq.com/sns/jscode2session",
        params={"appid": appid, "secret": secret, "js_code": code, "grant_type": "authorization_code"},
        timeout=8,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errcode") or not payload.get("openid"):
        raise ValueError(payload.get("errmsg") or "微信登录校验失败")
    return appid, payload["openid"], payload.get("unionid", "")


@transaction.atomic
def login_or_create_user(appid, openid, unionid=""):
    identity = WeChatMiniProgramIdentity.objects.select_related("user").filter(appid=appid, openid=openid).first()
    if identity:
        if unionid and identity.unionid != unionid:
            identity.unionid = unionid
            identity.save(update_fields=["unionid", "updated_at"])
        return identity.user, False
    digest = hashlib.sha256(f"{appid}:{openid}".encode()).hexdigest()[:20]
    username = f"wx_{digest}"
    user = User.objects.create_user(username=username, password=secrets.token_urlsafe(32), is_active=True)
    UserRole.objects.get_or_create(user=user, defaults={"role": "user"})
    UserStatus.objects.get_or_create(user=user, defaults={"status": "active"})
    UserMembership.objects.get_or_create(user=user, defaults={"membership_type": "free"})
    WeChatMiniProgramIdentity.objects.create(user=user, appid=appid, openid=openid, unionid=unionid)
    return user, True
