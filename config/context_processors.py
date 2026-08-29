from django.conf import settings


def site_flags(request):
    return {
        "auth_login_disabled": getattr(settings, "AUTH_LOGIN_DISABLED", False),
    }
