"""
开发环境配置 - 与生产环境完全一致，都使用PostgreSQL数据库
"""

from .base import *

# 开发环境特定配置 - 只设置DEBUG为True
DEBUG = True

# 允许的主机 - 开发环境支持局域网访问
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver", "192.168.0.118", "172.16.0.1", "0.0.0.0", "*"]

# 数据库配置 - 开发环境使用PostgreSQL（与生产环境完全一致）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "qatoolbox_local"),
        "USER": os.environ.get("DB_USER", "gaojie"),  # macOS当前用户
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),  # 本地无密码
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": "prefer",
        },
    }
}

# 缓存配置 - 使用Redis缓存，解决多进程验证码问题
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": "qatoolbox_dev",
        "TIMEOUT": 60 * 60 * 24,  # 24小时
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "session_dev",
        "TIMEOUT": 60 * 60 * 24 * 30,  # 30天
    },
}

# 会话配置 - 与生产环境一致，使用数据库存储session
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_CACHE_ALIAS = "default"

# 静态文件配置 - 与生产环境一致
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 邮件配置 - 开发环境使用控制台后端
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS配置 - 与生产环境一致
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Celery配置 - 与生产环境一致
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = "django-db://"
CELERY_RESULT_BACKEND = "django-db"

# API限制配置 - 与生产环境一致
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "100/minute", "user": "1000/minute"}

# 安全配置 - 与生产环境一致
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

# 文件上传限制 - 与生产环境一致
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000

# 开发环境调试工具栏
if DEBUG:
    try:
        import debug_toolbar

        if "debug_toolbar" not in INSTALLED_APPS:
            INSTALLED_APPS += ["debug_toolbar"]
        if "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:
            MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
        INTERNAL_IPS = ["127.0.0.1", "localhost"]
    except ImportError:
        pass

# 添加django-extensions支持
if "django_extensions" not in INSTALLED_APPS:
    INSTALLED_APPS += ["django_extensions"]
