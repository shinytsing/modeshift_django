#!/bin/sh
set -e
cd /app

cat > /app/config/context_processors.py <<'EOF'
from django.conf import settings


def site_flags(request):
    return {
        "auth_login_disabled": getattr(settings, "AUTH_LOGIN_DISABLED", False),
    }
EOF

grep -q 'AUTH_LOGIN_DISABLED' /app/config/settings/production.py || cat >> /app/config/settings/production.py <<'EOF'

# 暂时关闭登录/注册，方便访客直接使用
AUTH_LOGIN_DISABLED = os.environ.get("AUTH_LOGIN_DISABLED", "true").lower() in ("1", "true", "yes")
TEMPLATES[0]["OPTIONS"]["context_processors"].append("config.context_processors.site_flags")
EOF

python - <<'PY'
from pathlib import Path
import re

apps_py = Path("/app/apps/users/apps.py")
text = apps_py.read_text()
patch = '''
        from django.conf import settings
        import apps.users.signals
        if getattr(settings, "AUTH_LOGIN_DISABLED", False):
            import django.contrib.auth.decorators as auth_decorators

            def _public_access(view_func=None, redirect_field_name="next", login_url=None):
                if view_func:
                    return view_func
                return lambda func: func

            auth_decorators.login_required = _public_access
'''
if "AUTH_LOGIN_DISABLED" not in text:
    if "import apps.users.signals" in text:
        text = text.replace(
            "    def ready(self):\n        import apps.users.signals",
            "    def ready(self):" + patch,
        )
    else:
        text = text.replace(
            "    def ready(self):\n        pass",
            "    def ready(self):" + patch,
        )
    apps_py.write_text(text)

tools_urls = Path("/app/apps/tools/urls.py")
tools_text = tools_urls.read_text()
if "AUTH_LOGIN_DISABLED" not in tools_text:
    tools_text = tools_text.replace(
        'def tools_index_view(request):\n    """工具主页面"""\n    # 快速检查用户登录状态，避免慢查询\n    if not request.user.is_authenticated:\n        from django.contrib.auth.views import redirect_to_login\n\n        return redirect_to_login(request.get_full_path())\n    return render(request, "tools/index.html")',
        'def tools_index_view(request):\n    """工具主页面"""\n    from django.conf import settings\n\n    if not getattr(settings, "AUTH_LOGIN_DISABLED", False):\n        if not request.user.is_authenticated:\n            from django.contrib.auth.views import redirect_to_login\n\n            return redirect_to_login(request.get_full_path())\n    return render(request, "tools/index.html")',
    )
    tools_urls.write_text(tools_text)

users_urls = Path("/app/apps/users/urls.py")
users_urls.write_text(
    users_urls.read_text()
    .replace('path("api/login/"', '# path("api/login/"')
    .replace('path("api/register/"', '# path("api/register/"')
)

views_py = Path("/app/views.py")
views_text = views_py.read_text()
if "AUTH_LOGIN_DISABLED" not in views_text:
    views_text = views_text.replace(
        "from functools import wraps",
        "from functools import wraps\nfrom django.conf import settings",
    )
    views_text = views_text.replace(
        'def login_required_modal(view_func):\n    """\n    自定义登录装饰器，未登录时重定向到主页\n    """\n    @wraps(view_func)',
        'def login_required_modal(view_func):\n    """\n    自定义登录装饰器，未登录时重定向到主页\n    """\n    if getattr(settings, "AUTH_LOGIN_DISABLED", False):\n        return view_func\n\n    @wraps(view_func)',
    )
    views_text = re.sub(
        r"@login_required_modal  # 使用自定义装饰器\ndef tool_view\(request\):\n    # 获取用户偏好模式\n    try:\n        from apps.users.models import UserModePreference\n\n        preferred_mode = UserModePreference.get_user_preferred_mode\(request.user\)\n    except Exception:\n        preferred_mode = \"work\"  # 默认极客模式",
        '@login_required_modal  # 使用自定义装饰器\ndef tool_view(request):\n    preferred_mode = "work"\n    if request.user.is_authenticated:\n        try:\n            from apps.users.models import UserModePreference\n\n            preferred_mode = UserModePreference.get_user_preferred_mode(request.user)\n        except Exception:\n            preferred_mode = "work"',
        views_text,
    )
    views_py.write_text(views_text)

urls_py = Path("/app/urls.py")
urls_text = urls_py.read_text()
urls_text = urls_text.replace('path("auth/google/"', '# path("auth/google/"')
urls_text = urls_text.replace('path("accounts/"', '# path("accounts/"')
urls_py.write_text(urls_text)
PY

sed -i 's/{% if user.is_authenticated %}/{% if user.is_authenticated or auth_login_disabled %}/' /app/templates/tool.html

python - <<'PY'
from pathlib import Path
path = Path("/app/templates/base.html")
text = path.read_text()
if "window.AUTH_LOGIN_DISABLED" not in text:
    text = text.replace(
        "    <script>\n        // 安全的DOM移除函数",
        "    <script>\n        window.AUTH_LOGIN_DISABLED = {{ auth_login_disabled|yesno:\"true,false\" }};\n        // 安全的DOM移除函数",
    )
    text = text.replace(
        "        function showLoginModal() {\n            if (typeof showGeekLoginModal",
        "        function showLoginModal() {\n            if (window.AUTH_LOGIN_DISABLED) {\n                return;\n            }\n            if (typeof showGeekLoginModal",
    )
    text = text.replace(
        "        function showRegisterModal() {\n            if (typeof showGeekLoginModal",
        "        function showRegisterModal() {\n            if (window.AUTH_LOGIN_DISABLED) {\n                return;\n            }\n            if (typeof showGeekLoginModal",
    )

login_block_old = '''                    {% else %}
                        <a href="{% url 'users:login' %}" class="btn btn-primary btn-custom" onclick="stopMedia()">
                            <i class="fas fa-sign-in-alt"></i> <span data-translate="登录">登录</span>
                        </a>
                        <a href="{% url 'users:register' %}" class="btn btn-secondary btn-custom" onclick="stopMedia()">
                            <i class="fas fa-user-plus"></i> <span data-translate="注册">注册</span>
                        </a>
                    {% endif %}'''
login_block_new = '''                    {% else %}
                        {% if not auth_login_disabled %}
                        <a href="{% url 'users:login' %}" class="btn btn-primary btn-custom" onclick="stopMedia()">
                            <i class="fas fa-sign-in-alt"></i> <span data-translate="登录">登录</span>
                        </a>
                        <a href="{% url 'users:register' %}" class="btn btn-secondary btn-custom" onclick="stopMedia()">
                            <i class="fas fa-user-plus"></i> <span data-translate="注册">注册</span>
                        </a>
                        {% endif %}
                    {% endif %}'''
if login_block_old in text:
    text = text.replace(login_block_old, login_block_new)

path.write_text(text)
PY

echo "Open access patch applied."
