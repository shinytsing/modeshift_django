#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控仪表板视图
"""

import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from apps.tools.services.cache_service import CacheManager
from apps.tools.models import SocialMediaNotification
from apps.tools.services.monitoring_service import DatabaseMonitor, SystemMonitor, monitoring_service


def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def monitoring_dashboard(request):
    """监控仪表板页面"""
    return render(request, "tools/monitoring_dashboard.html")


def _service(name, key, status, message, kind="runtime"):
    return {"key": key, "name": name, "status": status, "message": message, "kind": kind}


def _check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return _service("PostgreSQL 数据库", "database", "up", "连接正常")
    except Exception:
        return _service("PostgreSQL 数据库", "database", "down", "数据库连接失败")


def _check_cache():
    try:
        key = f"admin-service-health:{time.time_ns()}"
        cache.set(key, "ok", timeout=10)
        healthy = cache.get(key) == "ok"
        cache.delete(key)
        return _service("Redis 缓存", "cache", "up" if healthy else "down", "读写正常" if healthy else "读写失败")
    except Exception:
        return _service("Redis 缓存", "cache", "down", "缓存读写失败")


def _check_mcp():
    base_url = str(getattr(settings, "XHS_MCP_BASE_URL", "") or os.environ.get("XHS_MCP_BASE_URL", "")).strip()
    token = os.environ.get("XHS_MCP_TOKEN", "").strip()
    if not base_url or not token:
        return _service("小红书 MCP", "xiaohongshu_mcp", "down", "未配置 MCP 地址或 token", "integration")
    try:
        request = Request(f"{base_url.rstrip('/')}/health", headers={"Accept": "application/json"})
        with urlopen(request, timeout=2) as response:
            healthy = 200 <= response.status < 300
        return _service(
            "小红书 MCP",
            "xiaohongshu_mcp",
            "up" if healthy else "down",
            "健康检查通过" if healthy else "健康检查失败",
            "integration",
        )
    except (HTTPError, URLError, TimeoutError, OSError):
        return _service("小红书 MCP", "xiaohongshu_mcp", "down", "无法连接 MCP 健康检查", "integration")


def _check_celery():
    try:
        from config.celery import app as celery_app

        replies = celery_app.control.inspect(timeout=1).ping() or {}
        return _service(
            "定时任务 Worker", "scheduler", "up" if replies else "down", "Worker 已响应" if replies else "没有 Worker 响应"
        )
    except Exception:
        return _service("定时任务 Worker", "scheduler", "down", "Worker 未响应")


def _check_configuration():
    smtp_ready = all(
        getattr(settings, name, "")
        for name in ("EMAIL_HOST", "EMAIL_PORT", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD", "DEFAULT_FROM_EMAIL")
    ) and not str(getattr(settings, "EMAIL_BACKEND", "")).endswith("console.EmailBackend")
    deepseek_ready = bool(getattr(settings, "DEEPSEEK_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY"))
    return [
        _service(
            "邮件 SMTP",
            "email",
            "up" if smtp_ready else "down",
            "SMTP 已配置" if smtp_ready else "未配置 SMTP",
            "configuration",
        ),
        _service(
            "DeepSeek AI",
            "deepseek",
            "up" if deepseek_ready else "down",
            "API key 已配置" if deepseek_ready else "未配置 API key",
            "configuration",
        ),
    ]


@login_required
@user_passes_test(is_admin)
@require_GET
def get_service_status(request):
    """管理员只读查看线上部署依赖状态，不返回密钥或内部地址。"""
    services = [
        _service("Django Web", "web", "up", "当前管理页请求正常"),
        _check_database(),
        _check_cache(),
        _check_celery(),
        _check_mcp(),
        *_check_configuration(),
    ]
    up = sum(item["status"] == "up" for item in services)
    return JsonResponse(
        {
            "checked_at": time.time(),
            "status": "up" if up == len(services) else "down",
            "summary": {"up": up, "down": len(services) - up, "total": len(services)},
            "services": services,
        }
    )


@login_required
@user_passes_test(is_admin)
def get_monitoring_data(request):
    """获取监控数据API"""
    try:
        system = SystemMonitor.get_system_metrics()
        database = DatabaseMonitor.get_database_metrics()
        alerts = SystemMonitor.check_system_health() + DatabaseMonitor.check_database_health()
        today = timezone.localdate()
        dashboard_data = {
            "health_score": max(0, 100 - len(alerts) * 10),
            "metrics": {
                "system": {
                    "cpu": {"percent": system["cpu_percent"]},
                    "memory": {"percent": system["memory_percent"]},
                    "disk": {"percent": system["disk_percent"]},
                },
                "database": database,
                "application": {
                    "active_users_today": User.objects.filter(last_login__date=today).count(),
                    "messages_today": SocialMediaNotification.objects.filter(created_at__date=today).count(),
                },
                "performance": {},
            },
            "alerts": [
                {"level": "warning", "message": message, "timestamp": timezone.now().isoformat()} for message in alerts
            ],
        }
        return JsonResponse({"success": True, "data": dashboard_data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def get_system_metrics(request):
    """获取系统指标"""
    try:
        metrics = monitoring_service.collect_all_metrics()
        return JsonResponse({"success": True, "data": metrics})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def get_alerts(request):
    """获取告警信息"""
    try:
        alerts = monitoring_service.check_all_alerts()
        return JsonResponse({"success": True, "data": alerts})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def get_cache_stats(request):
    """获取缓存统计"""
    try:
        cache_stats = CacheManager.get_cache_stats()
        return JsonResponse({"success": True, "data": cache_stats})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def clear_cache(request):
    """清除缓存"""
    try:
        results = CacheManager.clear_all_cache()
        return JsonResponse({"success": True, "data": results})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def warm_up_cache(request):
    """预热缓存"""
    try:
        results = CacheManager.warm_up_cache()
        return JsonResponse({"success": True, "data": results})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class MonitoringAPIView(View):
    """监控API视图"""

    def get(self, request, *args, **kwargs):
        """获取监控数据"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"error": "权限不足"}, status=403)

        data_type = kwargs.get("type", "dashboard")

        try:
            if data_type == "dashboard":
                data = monitoring_service.get_dashboard_data()
            elif data_type == "metrics":
                data = monitoring_service.collect_all_metrics()
            elif data_type == "alerts":
                data = monitoring_service.check_all_alerts()
            elif data_type == "cache":
                data = CacheManager.get_cache_stats()
            else:
                return JsonResponse({"error": "未知的数据类型"}, status=400)

            return JsonResponse({"success": True, "data": data})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        """执行监控操作"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"error": "权限不足"}, status=403)

        action = kwargs.get("action")

        try:
            if action == "clear_cache":
                results = CacheManager.clear_all_cache()
            elif action == "warm_cache":
                results = CacheManager.warm_up_cache()
            else:
                return JsonResponse({"error": "未知的操作"}, status=400)

            return JsonResponse({"success": True, "data": results})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
