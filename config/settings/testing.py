"""
测试环境配置
"""

import os

from .base import *  # noqa: F403

# 测试环境配置
DEBUG = True
TESTING = True

# 确保测试环境中的应用正确配置
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "captcha",
    "rest_framework",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "channels",
    "apps.users",
    "apps.content",
    "apps.tools",
    "apps.share",
]

# 使用PostgreSQL测试数据库（与生产环境一致）
# 优先使用PostgreSQL，确保与生产环境一致
if os.environ.get("CI") or os.environ.get("POSTGRES_HOST") or os.environ.get("POSTGRES_USER"):
    # CI/CD环境或本地测试环境使用PostgreSQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "test_modeshift_django"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    }
else:
    # 回退到PostgreSQL（确保与生产环境一致）
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test_modeshift_django",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": "5432",
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    }

# 测试环境缓存配置
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    },
    "session": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-session-cache",
    },
}

# 测试环境会话配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"


# 测试环境迁移配置 - 允许迁移
# 确保测试环境能够正确运行数据库迁移
MIGRATION_MODULES = {}

# 测试环境密码验证器（简化）
AUTH_PASSWORD_VALIDATORS = []

# 测试环境邮件配置
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# 测试环境静态文件
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 测试环境媒体文件
MEDIA_ROOT = "/tmp/qatoolbox_test_media"

# 测试环境日志配置
LOGGING = LOGGING.copy()  # 从base.py继承LOGGING配置
LOGGING["handlers"]["file"]["filename"] = "/tmp/django_test.log"
LOGGING["loggers"]["django"]["level"] = "WARNING"
LOGGING["loggers"]["apps.tools"]["level"] = "WARNING"
LOGGING["loggers"]["apps.users"]["level"] = "WARNING"

# 测试环境Celery配置
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 禁用调试工具栏
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

# 测试环境CORS配置
CORS_ALLOW_ALL_ORIGINS = True

# 测试环境允许的主机
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# 测试环境文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
