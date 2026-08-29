"""
生产环境配置 - 与开发环境完全一致，都使用PostgreSQL数据库
"""

from .base import *

# 添加whitenoise到INSTALLED_APPS
INSTALLED_APPS = INSTALLED_APPS + ['whitenoise.runserver_nostatic']

# 添加whitenoise中间件，移除缓存中间件避免HttpResponse序列化问题
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'apps.users.middleware.SessionExtensionMiddleware',
    'apps.tools.services.monitoring_service.PerformanceMonitoringMiddleware',
]

# 生产环境特定配置 - 只设置DEBUG为False
DEBUG = False

# 暂时关闭登录/注册，方便访客直接使用
AUTH_LOGIN_DISABLED = os.environ.get("AUTH_LOGIN_DISABLED", "true").lower() in ("1", "true", "yes")

TEMPLATES[0]["OPTIONS"]["context_processors"].append("config.context_processors.site_flags")

# 允许的主机 - 生产环境域名和IP
ALLOWED_HOSTS = [
    "shenyiqing.xin",
    "www.shenyiqing.xin", 
    "47.103.143.152",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "*",  # 允许所有主机用于外网访问
]

# 数据库配置 - 生产环境使用PostgreSQL（与开发环境完全一致）
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "qatoolbox"),
        "USER": os.environ.get("DB_USER", "qatoolbox"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "qatoolbox123"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": "prefer",
        },
    }
}

# 缓存配置 - 暂时禁用缓存避免序列化问题
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "session": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "staticfiles": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

# 会话配置 - 使用数据库存储session
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30天
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = False  # 开发环境设为False，生产环境设为True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# 页面缓存配置 - 完全禁用
CACHE_MIDDLEWARE_ALIAS = None
CACHE_MIDDLEWARE_SECONDS = 0
CACHE_MIDDLEWARE_KEY_PREFIX = ""

# 数据库查询优化 - 使用默认PostgreSQL配置

# 静态文件缓存 - 使用简单存储避免manifest问题
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'bz2', 'tar', 'rar', '7z']

# 静态文件配置 - 生产环境优化
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# 静态文件压缩配置
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'bz2', 'tar', 'rar', '7z']
WHITENOISE_ADD_HEADERS_FUNCTION = 'whitenoise.storage.add_headers_function'

# 禁用静态文件缓存 - 解决训练计划显示问题
WHITENOISE_MAX_AGE = 0
WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: False

# 邮件配置 - 生产环境使用SMTP后端
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@qatoolbox.com")

# CORS配置 - 与开发环境一致
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

# Celery配置 - 与开发环境一致
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = "django-db://"
CELERY_RESULT_BACKEND = "django-db"

# API限制配置 - 与开发环境一致
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "100/minute", "user": "1000/minute"}

# 安全配置 - 与开发环境一致
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

# 文件上传限制 - 设置为10GB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000

# 站点URL配置 - 用于Google OAuth回调
SITE_URL = "https://shenyiqing.xin"
