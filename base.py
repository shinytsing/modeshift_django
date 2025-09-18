"""
Django settings for QAToolBox project.
"""

import os
import sys
from pathlib import Path

import environ
from dotenv import load_dotenv

# 首先定义BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 添加apps目录到Python路径
sys.path.append(str(BASE_DIR / "apps"))

# 初始化environ
env = environ.Env(
    DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, "django-insecure-change-me-in-production"),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DB_NAME=(str, "qatoolbox"),
    DB_USER=(str, "qatoolbox"),
    DB_PASSWORD=(str, ""),
    DB_HOST=(str, "localhost"),
    DB_PORT=(int, 5432),
    REDIS_URL=(str, "redis://localhost:6379/0"),
)

# 加载环境变量
env_paths = [
    os.path.join(BASE_DIR, ".env"),
    os.path.join(os.path.dirname(__file__), ".env"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 将apps目录添加到Python路径
sys.path.append(str(BASE_DIR / "apps"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

# 允许的主机 - 基础配置，各环境可以覆盖
ALLOWED_HOSTS = env("ALLOWED_HOSTS") + ["testserver"]

# 文件上传设置
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # 用于CAPTCHA和allauth
    "captcha",
    "rest_framework",  # DRF框架
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    # Channels支持
    "channels",
    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # 自定义应用
    "apps.users",
    "apps.content",
    "apps.tools",
    "apps.share",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # allauth中间件
    "allauth.account.middleware.AccountMiddleware",
    # 会话持久化中间件 - 暂时禁用，避免Redis依赖问题
    # 'apps.users.middleware.SessionPersistenceMiddleware',
    "apps.users.middleware.SessionExtensionMiddleware",  # Session延长中间件
    # 性能监控中间件（已优化）
    "apps.tools.services.monitoring_service.PerformanceMonitoringMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"

# Channels配置
ASGI_APPLICATION = "asgi.application"

# Channel Layers配置（使用内存后端，生产环境建议使用Redis）
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# 数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django_db_connection_pool.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "qatoolbox"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "POOL_OPTIONS": {
                "POOL_SIZE": 20,
                "MAX_OVERFLOW": 30,
                "RECYCLE": 300,
            }
        },
    }
}

# Redis缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:redis123@127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
        },
        "KEY_PREFIX": "qatoolbox",
        "TIMEOUT": 300,
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:redis123@127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "session",
    },
}

# 会话配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "src/static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 登录配置
LOGIN_URL = "/"  # 重定向到主页，通过弹窗处理登录
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# 缓存配置已在上面定义，这里删除重复配置

# 会话配置 - 暂时使用数据库存储，避免Redis依赖问题
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30天（1个月）
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True  # 每次请求都保存session，延长过期时间
SESSION_COOKIE_SECURE = False  # 开发环境设为False，生产环境设为True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# 会话序列化器
SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"

# DRF配置
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle", "rest_framework.throttling.UserRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "1000/minute", "user": "1000/minute"},
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# 第三方API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 站点配置（用于captcha）
SITE_ID = 1

# Celery配置
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/3")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/3")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Shanghai"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# 缓存配置
CACHEOPS_REDIS = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/4")
CACHEOPS_DEFAULTS = {"timeout": 60 * 15}
CACHEOPS = {
    "auth.user": {"ops": "all", "timeout": 60 * 15},
    "tools.chatroom": {"ops": "all", "timeout": 60 * 10},
    "tools.chatmessage": {"ops": "all", "timeout": 60 * 5},
    "tools.timecapsule": {"ops": "all", "timeout": 60 * 20},
    "tools.heartlinkrequest": {"ops": "all", "timeout": 60 * 10},
}

# 性能监控
if DEBUG:
    INSTALLED_APPS += [
        # 'debug_toolbar',  # 暂时禁用以提升性能
        "django_extensions",
    ]

    # 暂时禁用Debug Toolbar以提升性能
    # MIDDLEWARE += [
    #     'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ]

    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
    }

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# IP黑名单配置
BLACKLISTED_IPS = [
    "183.94.33.160",  # 攻击IP
]

# 允许的引用域名
ALLOWED_REFERER_DOMAINS = [
    "shenyiqing.xin",
    "localhost",
    "127.0.0.1",
]

# 黑名单邮箱域名
BLACKLISTED_EMAIL_DOMAINS = [
    "temp-mail.org",
    "10minutemail.com",
    "guerrillamail.com",
]

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "https://shenyiqing.xin",
]
CORS_ALLOW_CREDENTIALS = True

# Crispy Forms配置
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# 日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "allauth": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.tools": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.users": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# 确保目录存在
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "pdf_inputs"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "word_outputs"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "avatars"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "tool_previews"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "tool_outputs"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "ai_links/icons"), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, "chat_images"), exist_ok=True)  # 添加聊天图片目录
os.makedirs(os.path.join(MEDIA_ROOT, "temp_audio"), exist_ok=True)  # 添加临时音频目录
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# django-allauth配置
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# allauth基本配置
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"  # 开发环境不验证邮箱
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"

# Google OAuth配置
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
    }
}

# 启用社交账户自动重定向
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# 站点ID（django-allauth需要）
SITE_ID = 1

# 站点URL配置 - 用于Google OAuth回调
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")
