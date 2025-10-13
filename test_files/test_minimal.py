"""
最小化测试配置 - 用于CI/CD测试
使用SQLite数据库，简化配置
"""

from .base import *

# 测试环境特定配置
DEBUG = True
SECRET_KEY = "test-secret-key-for-ci-cd-testing"

# 允许的主机
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# 使用SQLite数据库进行测试
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# 禁用HTTPS重定向
SECURE_SSL_REDIRECT = False

# 简化CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 简化缓存配置
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# 邮件后端
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# 静态文件配置
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 禁用调试工具栏
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [mw for mw in MIDDLEWARE if "debug_toolbar" not in mw]

# Celery配置 - 同步执行
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 简化日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# API限制
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "10000/minute", "user": "10000/minute"}
