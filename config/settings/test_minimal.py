"""
最小化测试环境配置
用于本地CI/CD测试
"""

import os

from .base import *

# 测试环境配置
DEBUG = True
TESTING = True

# 使用SQLite内存数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "OPTIONS": {
            "init_command": "PRAGMA foreign_keys=OFF;",
        },
    }
}

# 简化缓存配置
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

# 会话配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# 简化密码验证器
AUTH_PASSWORD_VALIDATORS = []

# 邮件配置
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# 静态文件配置
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 媒体文件配置
MEDIA_ROOT = "/tmp/qatoolbox_test_media"

# Celery配置
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 允许的主机
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# 文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

# 禁用迁移以加速测试
MIGRATION_MODULES = {
    "auth": None,
    "contenttypes": None,
    "sessions": None,
    "users": None,
    "tools": None,
    "content": None,
    "share": None,
}

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
