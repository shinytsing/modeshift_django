"""
URL configuration for ModeShift project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import time

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import include, path
from django.views.generic import RedirectView

# from apps.tools.views.health_views import DetailedHealthCheckView, HealthCheckView
from views import (
    custom_static_serve,
    help_page_view,
    home_view,
    secure_media_serve,
    theme_demo_view,
    tool_view,
    version_history_view,
    welcome_view,
)

# 导入测试展示相关视图
from testing_views import (
    testing_dashboard_view,
    testing_functional_view,
    testing_api_view,
    testing_performance_view,
    testing_security_view,
    run_tests_api,
    get_test_status_api,
    get_test_results_api,
    get_test_stats_api,
    get_test_history_api,
    get_test_report_api,
    stop_tests_api,
    allure_report_view,
)


def modern_demo_view(request):
    """现代化UI演示页面"""
    return render(request, "modern_demo.html")


def test_geek_login_view(request):
    """极客风格登录弹窗测试页面"""
    return render(request, "test_geek_login.html")


def terms_of_service_view(request):
    """服务条款页面"""
    return render(request, "legal/terms_of_service.html")


def privacy_policy_view(request):
    """隐私政策页面"""
    return render(request, "legal/privacy_policy.html")


def google_oauth_test_view(request):
    """Google OAuth测试页面"""
    import os
    context = {
        'google_client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
        'google_client_secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
    }
    return render(request, "google_oauth_test.html", context)

def error_animation_test_view(request):
    """错误动画测试页面"""
    return render(request, "test_error_animation.html")


def health_check_view(request):
    """健康检查视图"""
    from django.http import JsonResponse

    return JsonResponse({"status": "healthy", "timestamp": time.time(), "version": "1.0.0"})


urlpatterns = [
    path("health/", health_check_view, name="health_check"),
    # path("health/detailed/", DetailedHealthCheckView.as_view(), name="detailed_health_check"),
    path("", home_view, name="home"),
    path("welcome/", welcome_view, name="welcome"),
    path("theme-demo/", theme_demo_view, name="theme_demo"),
    path("modern-demo/", modern_demo_view, name="modern_demo"),
    path("test-geek-login/", test_geek_login_view, name="test_geek_login"),
    # 测试手法展示页面
    path("testing-dashboard/", testing_dashboard_view, name="testing_dashboard"),
    path("testing-functional/", testing_functional_view, name="testing_functional"),
    path("testing-api/", testing_api_view, name="testing_api"),
    path("testing-performance/", testing_performance_view, name="testing_performance"),
    path("testing-security/", testing_security_view, name="testing_security"),
    # 测试API接口
            path("api/tests/run/", run_tests_api, name="api_run_tests"),
            path("api/tests/status/", get_test_status_api, name="api_test_status"),
            path("api/tests/results/", get_test_results_api, name="api_test_results"),
            path("api/tests/stats/", get_test_stats_api, name="api_test_stats"),
            path("api/tests/history/", get_test_history_api, name="api_test_history"),
            path("api/tests/report/", get_test_report_api, name="api_test_report"),
            path("api/tests/stop/", stop_tests_api, name="api_stop_tests"),
            # Allure报告路径
            path("reports/allure-report/", allure_report_view, name="allure_report"),
            path("reports/allure-report/<path:path>", allure_report_view, name="allure_report_file"),
    path("terms/", terms_of_service_view, name="terms_of_service"),
    path("privacy/", privacy_policy_view, name="privacy_policy"),
        path("google-oauth-test/", google_oauth_test_view, name="google_oauth_test"),
        path("error-animation-test/", error_animation_test_view, name="error_animation_test"),
    path("version-history/", version_history_view, name="version_history"),
    path("help/", help_page_view, name="help_page"),
    path("admin/", admin.site.urls),
    # Trojan代理服务重定向（兼容性）
    path("trojan/", RedirectView.as_view(url="/tools/trojan/", permanent=False)),
    path("trojan/<path:path>", RedirectView.as_view(url="/tools/trojan/%(path)s", permanent=False)),
    # 工具主页面路由
    # 工具子路由（包含测试用例生成器等）
    path("tools/", include("apps.tools.urls", namespace="tools")),
    path("users/", include("apps.users.urls", namespace="users")),
    # 作业批改路由
    path("api/grading/", include("apps.grading.urls", namespace="grading")),
    # Google OAuth 直接路径（避免 /users/ 前缀）
    path("auth/google/", include("apps.users.google_auth_urls", namespace="auth")),
    # 登录按钮走 allauth 的 google_login 时，转到已登记 redirect_uri 的代理流程
    path(
        "accounts/google/login/",
        RedirectView.as_view(url="/auth/google/", query_string=True),
    ),
    path("content/", include("apps.content.urls", namespace="content")),
    path("share/", include("apps.share.urls", namespace="share")),
    # allauth 登录/注册
    path("accounts/", include("allauth.urls")),
    # Favicon路由
    path("favicon.ico", RedirectView.as_view(url="/static/favicon.ico", permanent=True)),
]

# 开发环境下提供媒体文件访问和debug_toolbar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 自定义静态文件服务，禁用缓存
    urlpatterns += [
        path("static/<path:path>", custom_static_serve, name="custom_static"),
    ]
    # 开发环境添加debug_toolbar
    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
else:
    # 生产环境使用安全的媒体文件服务
    urlpatterns += [
        path("media/<path:path>", secure_media_serve, name="secure_media"),
    ]

# 生产环境静态文件服务
if not settings.DEBUG:
    from django.views.static import serve
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
