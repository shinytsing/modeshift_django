#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析视图
提供服务器分析功能的API接口
仅管理员可见
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.tools.models.analytics_models import (
    AnalyticsReport,
    ApplicationMetrics,
    DatabaseMetrics,
    ErrorLog,
    PerformanceAlert,
    ServerMetrics,
    SystemHealthScore,
    UserBehaviorMetrics,
)
from apps.tools.services.server_analytics_service import server_analytics_service

logger = logging.getLogger(__name__)


def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_authenticated and user.is_staff


@method_decorator(csrf_exempt, name="dispatch")
class AnalyticsDashboardAPI(View):
    """分析仪表盘API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def get(self, request: HttpRequest):
        """获取仪表盘数据"""
        try:
            data = server_analytics_service.get_dashboard_data()
            return JsonResponse({"success": True, "data": data})
        except Exception as e:
            logger.error(f"获取仪表盘数据失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class RealTimeStatsAPI(View):
    """实时统计API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def get(self, request: HttpRequest):
        """获取实时统计"""
        try:
            data = server_analytics_service.get_real_time_stats()
            return JsonResponse({"success": True, "data": data})
        except Exception as e:
            logger.error(f"获取实时统计失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class HistoricalDataAPI(View):
    """历史数据API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def get(self, request: HttpRequest):
        """获取历史数据"""
        try:
            # 获取查询参数
            data_type = request.GET.get("type", "server_metrics")
            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")
            limit = int(request.GET.get("limit", 100))
            
            # 默认时间范围（最近7天）
            if not end_date:
                end_date = timezone.now()
            else:
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            
            if not start_date:
                start_date = end_date - timedelta(days=7)
            else:
                start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            
            data = []
            
            if data_type == "server_metrics":
                queryset = ServerMetrics.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).order_by("-timestamp")[:limit]
                
                for item in queryset:
                    data.append({
                        "timestamp": item.timestamp.isoformat(),
                        "cpu_percent": item.cpu_percent,
                        "memory_percent": item.memory_percent,
                        "disk_percent": item.disk_percent,
                        "load_average": item.load_average,
                        "network_bytes_sent": item.network_bytes_sent,
                        "network_bytes_recv": item.network_bytes_recv,
                    })
            
            elif data_type == "database_metrics":
                queryset = DatabaseMetrics.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).order_by("-timestamp")[:limit]
                
                for item in queryset:
                    data.append({
                        "timestamp": item.timestamp.isoformat(),
                        "db_size": item.db_size,
                        "total_connections": item.total_connections,
                        "active_connections": item.active_connections,
                        "idle_connections": item.idle_connections,
                        "slow_queries": item.slow_queries,
                        "dead_tuples": item.dead_tuples,
                    })
            
            elif data_type == "application_metrics":
                queryset = ApplicationMetrics.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).order_by("-timestamp")[:limit]
                
                for item in queryset:
                    data.append({
                        "timestamp": item.timestamp.isoformat(),
                        "total_requests": item.total_requests,
                        "successful_requests": item.successful_requests,
                        "failed_requests": item.failed_requests,
                        "avg_response_time": item.avg_response_time,
                        "max_response_time": item.max_response_time,
                        "active_users": item.active_users,
                        "new_users": item.new_users,
                    })
            
            elif data_type == "system_health":
                queryset = SystemHealthScore.objects.filter(
                    timestamp__gte=start_date,
                    timestamp__lte=end_date
                ).order_by("-timestamp")[:limit]
                
                for item in queryset:
                    data.append({
                        "timestamp": item.timestamp.isoformat(),
                        "overall_score": item.overall_score,
                        "performance_score": item.performance_score,
                        "reliability_score": item.reliability_score,
                        "security_score": item.security_score,
                        "user_experience_score": item.user_experience_score,
                        "details": item.details,
                    })
            
            return JsonResponse({"success": True, "data": data})
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ErrorAnalysisAPI(View):
    """错误分析API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def get(self, request: HttpRequest):
        """获取错误分析数据"""
        try:
            # 获取查询参数
            error_type = request.GET.get("error_type")
            severity = request.GET.get("severity")
            resolved = request.GET.get("resolved")
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 20))
            
            # 构建查询条件
            queryset = ErrorLog.objects.all()
            
            if error_type:
                queryset = queryset.filter(error_type=error_type)
            
            if severity:
                queryset = queryset.filter(severity=severity)
            
            if resolved is not None:
                queryset = queryset.filter(resolved=resolved.lower() == "true")
            
            # 分页
            paginator = Paginator(queryset.order_by("-timestamp"), page_size)
            page_obj = paginator.get_page(page)
            
            errors = []
            for error in page_obj:
                errors.append({
                    "id": error.id,
                    "timestamp": error.timestamp.isoformat(),
                    "error_type": error.error_type,
                    "error_type_display": error.get_error_type_display(),
                    "severity": error.severity,
                    "severity_display": error.get_severity_display(),
                    "message": error.message,
                    "user": error.user.username if error.user else None,
                    "ip_address": error.ip_address,
                    "endpoint": error.endpoint,
                    "resolved": error.resolved,
                    "resolved_at": error.resolved_at.isoformat() if error.resolved_at else None,
                    "resolved_by": error.resolved_by.username if error.resolved_by else None,
                })
            
            return JsonResponse({
                "success": True,
                "data": errors,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_count": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                }
            })
            
        except Exception as e:
            logger.error(f"获取错误分析数据失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def post(self, request: HttpRequest):
        """处理错误操作"""
        try:
            data = json.loads(request.body)
            action = data.get("action")
            error_id = data.get("error_id")
            
            if action == "resolve":
                error = ErrorLog.objects.get(id=error_id)
                error.resolved = True
                error.resolved_at = timezone.now()
                error.resolved_by = request.user
                error.save()
                
                return JsonResponse({"success": True, "message": "错误已标记为已解决"})
            
            elif action == "dismiss":
                error = ErrorLog.objects.get(id=error_id)
                error.resolved = True
                error.resolved_at = timezone.now()
                error.resolved_by = request.user
                error.save()
                
                return JsonResponse({"success": True, "message": "错误已忽略"})
            
            else:
                return JsonResponse({"success": False, "error": "未知操作"}, status=400)
                
        except Exception as e:
            logger.error(f"处理错误操作失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class PerformanceAlertsAPI(View):
    """性能告警API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def get(self, request: HttpRequest):
        """获取性能告警"""
        try:
            # 获取查询参数
            status = request.GET.get("status", "active")
            alert_type = request.GET.get("alert_type")
            severity = request.GET.get("severity")
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 20))
            
            # 构建查询条件
            queryset = PerformanceAlert.objects.all()
            
            if status:
                queryset = queryset.filter(status=status)
            
            if alert_type:
                queryset = queryset.filter(alert_type=alert_type)
            
            if severity:
                queryset = queryset.filter(severity=severity)
            
            # 分页
            paginator = Paginator(queryset.order_by("-timestamp"), page_size)
            page_obj = paginator.get_page(page)
            
            alerts = []
            for alert in page_obj:
                alerts.append({
                    "id": alert.id,
                    "timestamp": alert.timestamp.isoformat(),
                    "alert_type": alert.alert_type,
                    "alert_type_display": alert.get_alert_type_display(),
                    "status": alert.status,
                    "status_display": alert.get_status_display(),
                    "title": alert.title,
                    "message": alert.message,
                    "threshold_value": alert.threshold_value,
                    "actual_value": alert.actual_value,
                    "severity": alert.severity,
                    "severity_display": alert.get_severity_display(),
                    "acknowledged_by": alert.acknowledged_by.username if alert.acknowledged_by else None,
                    "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                })
            
            return JsonResponse({
                "success": True,
                "data": alerts,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_count": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                }
            })
            
        except Exception as e:
            logger.error(f"获取性能告警失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def post(self, request: HttpRequest):
        """处理告警操作"""
        try:
            data = json.loads(request.body)
            action = data.get("action")
            alert_id = data.get("alert_id")
            
            if action == "acknowledge":
                alert = PerformanceAlert.objects.get(id=alert_id)
                alert.status = "acknowledged"
                alert.acknowledged_by = request.user
                alert.acknowledged_at = timezone.now()
                alert.save()
                
                return JsonResponse({"success": True, "message": "告警已确认"})
            
            elif action == "resolve":
                alert = PerformanceAlert.objects.get(id=alert_id)
                alert.status = "resolved"
                alert.resolved_at = timezone.now()
                alert.save()
                
                return JsonResponse({"success": True, "message": "告警已解决"})
            
            elif action == "dismiss":
                alert = PerformanceAlert.objects.get(id=alert_id)
                alert.status = "dismissed"
                alert.save()
                
                return JsonResponse({"success": True, "message": "告警已忽略"})
            
            else:
                return JsonResponse({"success": False, "error": "未知操作"}, status=400)
                
        except Exception as e:
            logger.error(f"处理告警操作失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class AnalyticsReportsAPI(View):
    """分析报告API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def get(self, request: HttpRequest):
        """获取分析报告列表"""
        try:
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 20))
            report_type = request.GET.get("report_type")
            
            queryset = AnalyticsReport.objects.all()
            
            if report_type:
                queryset = queryset.filter(report_type=report_type)
            
            # 分页
            paginator = Paginator(queryset.order_by("-created_at"), page_size)
            page_obj = paginator.get_page(page)
            
            reports = []
            for report in page_obj:
                reports.append({
                    "id": report.id,
                    "report_type": report.report_type,
                    "report_type_display": report.get_report_type_display(),
                    "title": report.title,
                    "description": report.description,
                    "start_date": report.start_date.isoformat(),
                    "end_date": report.end_date.isoformat(),
                    "created_by": report.created_by.username,
                    "created_at": report.created_at.isoformat(),
                    "is_public": report.is_public,
                })
            
            return JsonResponse({
                "success": True,
                "data": reports,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_count": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                }
            })
            
        except Exception as e:
            logger.error(f"获取分析报告失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def post(self, request: HttpRequest):
        """创建分析报告"""
        try:
            data = json.loads(request.body)
            
            report = AnalyticsReport.objects.create(
                report_type=data.get("report_type"),
                title=data.get("title"),
                description=data.get("description"),
                start_date=datetime.fromisoformat(data.get("start_date").replace("Z", "+00:00")),
                end_date=datetime.fromisoformat(data.get("end_date").replace("Z", "+00:00")),
                data=data.get("data", {}),
                created_by=request.user,
                is_public=data.get("is_public", False),
            )
            
            return JsonResponse({
                "success": True,
                "message": "报告创建成功",
                "report_id": report.id
            })
            
        except Exception as e:
            logger.error(f"创建分析报告失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ExportDataAPI(View):
    """数据导出API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def post(self, request: HttpRequest):
        """导出分析数据"""
        try:
            data = json.loads(request.body)
            start_date = datetime.fromisoformat(data.get("start_date").replace("Z", "+00:00"))
            end_date = datetime.fromisoformat(data.get("end_date").replace("Z", "+00:00"))
            
            export_data = server_analytics_service.export_analytics_data(start_date, end_date)
            
            return JsonResponse({
                "success": True,
                "data": export_data
            })
            
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class UserBehaviorAPI(View):
    """用户行为分析API"""
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(is_admin))
    def get(self, request: HttpRequest):
        """获取用户行为分析"""
        try:
            # 获取查询参数
            user_id = request.GET.get("user_id")
            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 20))
            
            # 默认时间范围（最近30天）
            if not end_date:
                end_date = timezone.now().date()
            else:
                end_date = datetime.fromisoformat(end_date).date()
            
            if not start_date:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.fromisoformat(start_date).date()
            
            # 构建查询条件
            queryset = UserBehaviorMetrics.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            )
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            # 分页
            paginator = Paginator(queryset.order_by("-date", "-last_activity"), page_size)
            page_obj = paginator.get_page(page)
            
            behaviors = []
            for behavior in page_obj:
                behaviors.append({
                    "user_id": behavior.user.id,
                    "username": behavior.user.username,
                    "date": behavior.date.isoformat(),
                    "page_views": behavior.page_views,
                    "session_duration": behavior.session_duration,
                    "api_calls": behavior.api_calls,
                    "login_count": behavior.login_count,
                    "last_activity": behavior.last_activity.isoformat(),
                })
            
            return JsonResponse({
                "success": True,
                "data": behaviors,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": paginator.num_pages,
                    "total_count": paginator.count,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                }
            })
            
        except Exception as e:
            logger.error(f"获取用户行为分析失败: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
