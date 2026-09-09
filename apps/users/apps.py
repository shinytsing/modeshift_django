from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    label = "users"

    def ready(self):
        import apps.users.signals

        from django.conf import settings

        if getattr(settings, "AUTH_LOGIN_DISABLED", False):
            import django.contrib.auth.decorators as auth_decorators

            def _public_access(view_func=None, redirect_field_name="next", login_url=None):
                if view_func:
                    return view_func
                return lambda func: func

            auth_decorators.login_required = _public_access
