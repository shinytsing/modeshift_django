#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器分析服务
提供用户访问量和事务处理监控功能
仅管理员可见
"""

import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.http import HttpRequest
from django.utils import timezone

from apps.users.models import APIUsageStats, User, UserActivityLog, UserSessionStats

logger = logging.getLogger(__name__)


class ServerAnalyticsService:
    """服务器分析服务"""

    def __init__(self):
        self.cache_timeout = 300  # 5分钟缓存

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表盘数据"""
        cache_key = "server_analytics_dashboard"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data

        try:
            data = {
                "timestamp": timezone.now().isoformat(),
                "overview": self._get_overview_stats(),
                "user_activity": self._get_user_activity_stats(),
                "api_usage": self._get_api_usage_stats(),
                "system_metrics": self._get_system_metrics(),
                "database_stats": self._get_database_stats(),
                "hourly_trends": self._get_hourly_trends(),
                "top_endpoints": self._get_top_endpoints(),
                "error_analysis": self._get_error_analysis(),
            }
            
            cache.set(cache_key, data, timeout=self.cache_timeout)
            return data
            
        except Exception as e:
            logger.error(f"获取仪表盘数据失败: {e}")
            return {"error": str(e), "timestamp": timezone.now().isoformat()}

    def _get_overview_stats(self) -> Dict[str, Any]:
        """获取概览统计"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # 今日统计
        today_stats = {
            "total_users": User.objects.count(),
            "active_users": UserActivityLog.objects.filter(
                created_at__date=today
            ).values("user").distinct().count(),
            "total_sessions": UserSessionStats.objects.filter(
                session_start__date=today
            ).count(),
            "active_sessions": UserSessionStats.objects.filter(
                is_active=True,
                session_start__gte=timezone.now() - timedelta(minutes=30)
            ).count(),
            "api_calls": APIUsageStats.objects.filter(created_at__date=today).count(),
            "page_views": UserActivityLog.objects.filter(
                activity_type="page_view",
                created_at__date=today
            ).count(),
        }
        
        # 昨日统计（用于对比）
        yesterday_stats = {
            "active_users": UserActivityLog.objects.filter(
                created_at__date=yesterday
            ).values("user").distinct().count(),
            "api_calls": APIUsageStats.objects.filter(created_at__date=yesterday).count(),
            "page_views": UserActivityLog.objects.filter(
                activity_type="page_view",
                created_at__date=yesterday
            ).count(),
        }
        
        # 计算增长率
        def calculate_growth_rate(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 2)
        
        growth_rates = {
            "active_users": calculate_growth_rate(
                today_stats["active_users"], yesterday_stats["active_users"]
            ),
            "api_calls": calculate_growth_rate(
                today_stats["api_calls"], yesterday_stats["api_calls"]
            ),
            "page_views": calculate_growth_rate(
                today_stats["page_views"], yesterday_stats["page_views"]
            ),
        }
        
        return {
            "today": today_stats,
            "yesterday": yesterday_stats,
            "growth_rates": growth_rates,
        }

    def _get_user_activity_stats(self) -> Dict[str, Any]:
        """获取用户活动统计"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # 最近7天活跃用户趋势
        daily_active_users = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = UserActivityLog.objects.filter(
                created_at__date=date
            ).values("user").distinct().count()
            daily_active_users.append({
                "date": date.strftime("%Y-%m-%d"),
                "count": count
            })
        
        # 用户活动类型分布
        activity_types = UserActivityLog.objects.filter(
            created_at__date=today
        ).values("activity_type").annotate(
            count=Count("id")
        ).order_by("-count")
        
        # 地理位置分布（基于IP）
        geo_stats = UserActivityLog.objects.filter(
            created_at__date=today
        ).values("ip_address").annotate(
            count=Count("id")
        ).order_by("-count")[:10]
        
        return {
            "daily_active_users": list(reversed(daily_active_users)),
            "activity_types": list(activity_types),
            "geo_distribution": list(geo_stats),
        }

    def _get_api_usage_stats(self) -> Dict[str, Any]:
        """获取API使用统计"""
        today = timezone.now().date()
        
        # API调用统计
        api_stats = APIUsageStats.objects.filter(
            created_at__date=today
        ).aggregate(
            total_calls=Count("id"),
            avg_response_time=Avg("response_time"),
            max_response_time=Max("response_time"),
            min_response_time=Min("response_time"),
            total_request_size=Sum("request_size"),
            total_response_size=Sum("response_size"),
        )
        
        # 按端点统计
        endpoint_stats = APIUsageStats.objects.filter(
            created_at__date=today
        ).values("endpoint", "method").annotate(
            count=Count("id"),
            avg_response_time=Avg("response_time"),
            error_count=Count("id", filter=Q(status_code__gte=400))
        ).order_by("-count")[:10]
        
        # 按状态码统计
        status_stats = APIUsageStats.objects.filter(
            created_at__date=today
        ).values("status_code").annotate(
            count=Count("id")
        ).order_by("-count")
        
        # 响应时间分布
        response_time_ranges = [
            ("< 100ms", Q(response_time__lt=0.1)),
            ("100ms - 500ms", Q(response_time__gte=0.1, response_time__lt=0.5)),
            ("500ms - 1s", Q(response_time__gte=0.5, response_time__lt=1.0)),
            ("1s - 5s", Q(response_time__gte=1.0, response_time__lt=5.0)),
            ("> 5s", Q(response_time__gte=5.0)),
        ]
        
        response_time_distribution = []
        for label, query in response_time_ranges:
            count = APIUsageStats.objects.filter(
                created_at__date=today,
                **{query.lookup_name: query.rhs}
            ).count()
            response_time_distribution.append({
                "range": label,
                "count": count
            })
        
        return {
            "summary": api_stats,
            "endpoints": list(endpoint_stats),
            "status_codes": list(status_stats),
            "response_time_distribution": response_time_distribution,
        }

    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage("/")
            
            # 网络统计
            network = psutil.net_io_counters()
            
            # 进程信息
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 按CPU使用率排序
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "top_processes": processes[:10],
            }
            
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {"error": str(e)}

    def _get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计"""
        try:
            with connection.cursor() as cursor:
                # 数据库大小
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                db_size = cursor.fetchone()[0]
                
                # 表统计
                cursor.execute("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples,
                        n_dead_tup as dead_tuples
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                    LIMIT 10
                """)
                table_stats = cursor.fetchall()
                
                # 连接统计
                cursor.execute("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                """)
                connection_stats = cursor.fetchone()
                
                return {
                    "size": db_size,
                    "tables": [
                        {
                            "schema": row[0],
                            "table": row[1],
                            "inserts": row[2],
                            "updates": row[3],
                            "deletes": row[4],
                            "live_tuples": row[5],
                            "dead_tuples": row[6],
                        }
                        for row in table_stats
                    ],
                    "connections": {
                        "total": connection_stats[0],
                        "active": connection_stats[1],
                        "idle": connection_stats[2],
                    },
                }
                
        except Exception as e:
            logger.error(f"获取数据库统计失败: {e}")
            return {"error": str(e)}

    def _get_hourly_trends(self) -> Dict[str, Any]:
        """获取小时趋势数据"""
        today = timezone.now().date()
        
        # 今日每小时API调用趋势
        hourly_api_calls = []
        for hour in range(24):
            start_time = timezone.datetime.combine(today, timezone.datetime.min.time()) + timedelta(hours=hour)
            end_time = start_time + timedelta(hours=1)
            
            count = APIUsageStats.objects.filter(
                created_at__gte=start_time,
                created_at__lt=end_time
            ).count()
            
            hourly_api_calls.append({
                "hour": hour,
                "count": count
            })
        
        # 今日每小时活跃用户趋势
        hourly_active_users = []
        for hour in range(24):
            start_time = timezone.datetime.combine(today, timezone.datetime.min.time()) + timedelta(hours=hour)
            end_time = start_time + timedelta(hours=1)
            
            count = UserActivityLog.objects.filter(
                created_at__gte=start_time,
                created_at__lt=end_time
            ).values("user").distinct().count()
            
            hourly_active_users.append({
                "hour": hour,
                "count": count
            })
        
        return {
            "api_calls": hourly_api_calls,
            "active_users": hourly_active_users,
        }

    def _get_top_endpoints(self) -> List[Dict[str, Any]]:
        """获取热门端点"""
        today = timezone.now().date()
        
        top_endpoints = APIUsageStats.objects.filter(
            created_at__date=today
        ).values("endpoint").annotate(
            count=Count("id"),
            avg_response_time=Avg("response_time"),
            error_rate=Count("id", filter=Q(status_code__gte=400)) * 100.0 / Count("id")
        ).order_by("-count")[:20]
        
        return list(top_endpoints)

    def _get_error_analysis(self) -> Dict[str, Any]:
        """获取错误分析"""
        today = timezone.now().date()
        
        # 错误统计
        error_stats = APIUsageStats.objects.filter(
            created_at__date=today,
            status_code__gte=400
        ).values("status_code").annotate(
            count=Count("id")
        ).order_by("-count")
        
        # 错误端点
        error_endpoints = APIUsageStats.objects.filter(
            created_at__date=today,
            status_code__gte=400
        ).values("endpoint", "status_code").annotate(
            count=Count("id")
        ).order_by("-count")[:10]
        
        # 最近错误
        recent_errors = APIUsageStats.objects.filter(
            created_at__date=today,
            status_code__gte=400
        ).select_related("user").order_by("-created_at")[:20]
        
        recent_errors_data = []
        for error in recent_errors:
            recent_errors_data.append({
                "endpoint": error.endpoint,
                "method": error.method,
                "status_code": error.status_code,
                "user": error.user.username if error.user else "匿名",
                "ip_address": error.ip_address,
                "response_time": error.response_time,
                "created_at": error.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        return {
            "error_stats": list(error_stats),
            "error_endpoints": list(error_endpoints),
            "recent_errors": recent_errors_data,
        }

    def get_real_time_stats(self) -> Dict[str, Any]:
        """获取实时统计"""
        now = timezone.now()
        last_minute = now - timedelta(minutes=1)
        
        # 最近1分钟的统计
        recent_stats = {
            "api_calls": APIUsageStats.objects.filter(
                created_at__gte=last_minute
            ).count(),
            "active_users": UserActivityLog.objects.filter(
                created_at__gte=last_minute
            ).values("user").distinct().count(),
            "errors": APIUsageStats.objects.filter(
                created_at__gte=last_minute,
                status_code__gte=400
            ).count(),
        }
        
        return {
            "timestamp": now.isoformat(),
            "last_minute": recent_stats,
            "system_metrics": self._get_system_metrics(),
        }

    def export_analytics_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """导出分析数据"""
        try:
            data = {
                "export_info": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "exported_at": timezone.now().isoformat(),
                },
                "user_activity": list(
                    UserActivityLog.objects.filter(
                        created_at__gte=start_date,
                        created_at__lte=end_date
                    ).values(
                        "user__username",
                        "activity_type",
                        "ip_address",
                        "endpoint",
                        "status_code",
                        "created_at"
                    )
                ),
                "api_usage": list(
                    APIUsageStats.objects.filter(
                        created_at__gte=start_date,
                        created_at__lte=end_date
                    ).values(
                        "endpoint",
                        "method",
                        "user__username",
                        "ip_address",
                        "status_code",
                        "response_time",
                        "request_size",
                        "response_size",
                        "created_at"
                    )
                ),
                "sessions": list(
                    UserSessionStats.objects.filter(
                        session_start__gte=start_date,
                        session_start__lte=end_date
                    ).values(
                        "user__username",
                        "session_start",
                        "session_end",
                        "duration",
                        "ip_address",
                        "user_agent",
                        "is_active"
                    )
                ),
            }
            
            return data
            
        except Exception as e:
            logger.error(f"导出分析数据失败: {e}")
            return {"error": str(e)}


# 全局实例
server_analytics_service = ServerAnalyticsService()
