#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收集分析数据的管理命令
定时收集服务器分析数据并存储到数据库
"""

import logging
import psutil
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from apps.tools.models.analytics_models import (
    ApplicationMetrics,
    DatabaseMetrics,
    ServerMetrics,
    SystemHealthScore,
    UserBehaviorMetrics,
)
from apps.users.models import APIUsageStats, User, UserActivityLog, UserSessionStats

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '收集服务器分析数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='数据收集间隔（秒），默认300秒'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='只执行一次数据收集'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        once = options['once']
        
        self.stdout.write(
            self.style.SUCCESS(f'开始收集分析数据，间隔: {interval}秒')
        )
        
        if once:
            self.collect_data()
        else:
            self.collect_continuously(interval)

    def collect_continuously(self, interval):
        """持续收集数据"""
        while True:
            try:
                self.collect_data()
                self.stdout.write(
                    self.style.SUCCESS(f'数据收集完成: {timezone.now()}')
                )
                time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('数据收集已停止')
                )
                break
            except Exception as e:
                logger.error(f'数据收集失败: {e}')
                self.stdout.write(
                    self.style.ERROR(f'数据收集失败: {e}')
                )
                time.sleep(interval)

    def collect_data(self):
        """收集一次数据"""
        try:
            # 收集服务器指标
            self.collect_server_metrics()
            
            # 收集数据库指标
            self.collect_database_metrics()
            
            # 收集应用指标
            self.collect_application_metrics()
            
            # 收集用户行为指标
            self.collect_user_behavior_metrics()
            
            # 计算系统健康评分
            self.calculate_system_health_score()
            
        except Exception as e:
            logger.error(f'收集数据时发生错误: {e}')
            raise

    def collect_server_metrics(self):
        """收集服务器指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage("/")
            
            # 负载平均值
            load_avg = None
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                # Windows系统可能没有loadavg
                pass
            
            # 网络统计
            network = psutil.net_io_counters()
            
            # 保存到数据库
            ServerMetrics.objects.create(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=(disk.used / disk.total) * 100,
                load_average=load_avg,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
            )
            
            logger.info(f'服务器指标收集完成: CPU {cpu_percent}%, 内存 {memory.percent}%')
            
        except Exception as e:
            logger.error(f'收集服务器指标失败: {e}')
            raise

    def collect_database_metrics(self):
        """收集数据库指标"""
        try:
            with connection.cursor() as cursor:
                # 数据库大小
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                db_size = cursor.fetchone()[0]
                
                # 连接统计
                cursor.execute("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                """)
                connection_stats = cursor.fetchone()
                
                # 慢查询统计（查询时间超过1秒的）
                cursor.execute("""
                    SELECT count(*) FROM pg_stat_statements 
                    WHERE mean_exec_time > 1000
                """)
                slow_queries = cursor.fetchone()[0] or 0
                
                # 死元组统计
                cursor.execute("""
                    SELECT sum(n_dead_tup) FROM pg_stat_user_tables
                """)
                dead_tuples = cursor.fetchone()[0] or 0
                
                # 保存到数据库
                DatabaseMetrics.objects.create(
                    db_size=db_size,
                    total_connections=connection_stats[0],
                    active_connections=connection_stats[1],
                    idle_connections=connection_stats[2],
                    slow_queries=slow_queries,
                    dead_tuples=dead_tuples,
                )
                
                logger.info(f'数据库指标收集完成: 连接数 {connection_stats[0]}')
                
        except Exception as e:
            logger.error(f'收集数据库指标失败: {e}')
            raise

    def collect_application_metrics(self):
        """收集应用指标"""
        try:
            now = timezone.now()
            today = now.date()
            last_hour = now - timedelta(hours=1)
            
            # 最近1小时的请求统计
            recent_requests = APIUsageStats.objects.filter(
                created_at__gte=last_hour
            )
            
            total_requests = recent_requests.count()
            successful_requests = recent_requests.filter(status_code__lt=400).count()
            failed_requests = recent_requests.filter(status_code__gte=400).count()
            
            # 响应时间统计
            response_times = recent_requests.values_list('response_time', flat=True)
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            # 活跃用户数（最近1小时）
            active_users = UserActivityLog.objects.filter(
                created_at__gte=last_hour
            ).values('user').distinct().count()
            
            # 新用户数（今日）
            new_users = User.objects.filter(
                date_joined__date=today
            ).count()
            
            # 保存到数据库
            ApplicationMetrics.objects.create(
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                avg_response_time=avg_response_time,
                max_response_time=max_response_time,
                active_users=active_users,
                new_users=new_users,
            )
            
            logger.info(f'应用指标收集完成: 请求数 {total_requests}, 活跃用户 {active_users}')
            
        except Exception as e:
            logger.error(f'收集应用指标失败: {e}')
            raise

    def collect_user_behavior_metrics(self):
        """收集用户行为指标"""
        try:
            today = timezone.now().date()
            
            # 获取所有用户
            users = User.objects.all()
            
            for user in users:
                # 今日页面浏览量
                page_views = UserActivityLog.objects.filter(
                    user=user,
                    activity_type='page_view',
                    created_at__date=today
                ).count()
                
                # 今日会话时长
                sessions = UserSessionStats.objects.filter(
                    user=user,
                    session_start__date=today
                )
                session_duration = sum(s.duration or 0 for s in sessions)
                
                # 今日API调用次数
                api_calls = APIUsageStats.objects.filter(
                    user=user,
                    created_at__date=today
                ).count()
                
                # 今日登录次数
                login_count = UserActivityLog.objects.filter(
                    user=user,
                    activity_type='login',
                    created_at__date=today
                ).count()
                
                # 最后活动时间
                last_activity = UserActivityLog.objects.filter(
                    user=user
                ).order_by('-created_at').first()
                
                last_activity_time = last_activity.created_at if last_activity else timezone.now()
                
                # 更新或创建用户行为指标
                UserBehaviorMetrics.objects.update_or_create(
                    user=user,
                    date=today,
                    defaults={
                        'page_views': page_views,
                        'session_duration': session_duration,
                        'api_calls': api_calls,
                        'login_count': login_count,
                        'last_activity': last_activity_time,
                    }
                )
            
            logger.info(f'用户行为指标收集完成: {users.count()} 个用户')
            
        except Exception as e:
            logger.error(f'收集用户行为指标失败: {e}')
            raise

    def calculate_system_health_score(self):
        """计算系统健康评分"""
        try:
            # 获取最新的指标数据
            latest_server = ServerMetrics.objects.order_by('-timestamp').first()
            latest_app = ApplicationMetrics.objects.order_by('-timestamp').first()
            latest_db = DatabaseMetrics.objects.order_by('-timestamp').first()
            
            if not all([latest_server, latest_app, latest_db]):
                logger.warning('缺少必要的指标数据，跳过健康评分计算')
                return
            
            # 计算各项评分（0-100分）
            performance_score = self._calculate_performance_score(latest_server, latest_app)
            reliability_score = self._calculate_reliability_score(latest_app, latest_db)
            security_score = self._calculate_security_score(latest_app)
            user_experience_score = self._calculate_user_experience_score(latest_app)
            
            # 计算总体评分
            overall_score = (performance_score + reliability_score + security_score + user_experience_score) / 4
            
            # 保存评分
            SystemHealthScore.objects.create(
                overall_score=overall_score,
                performance_score=performance_score,
                reliability_score=reliability_score,
                security_score=security_score,
                user_experience_score=user_experience_score,
                details={
                    'cpu_percent': latest_server.cpu_percent,
                    'memory_percent': latest_server.memory_percent,
                    'disk_percent': latest_server.disk_percent,
                    'avg_response_time': latest_app.avg_response_time,
                    'error_rate': (latest_app.failed_requests / latest_app.total_requests * 100) if latest_app.total_requests > 0 else 0,
                    'active_users': latest_app.active_users,
                }
            )
            
            logger.info(f'系统健康评分计算完成: 总体 {overall_score:.1f}分')
            
        except Exception as e:
            logger.error(f'计算系统健康评分失败: {e}')
            raise

    def _calculate_performance_score(self, server_metrics, app_metrics):
        """计算性能评分"""
        score = 100
        
        # CPU使用率评分
        if server_metrics.cpu_percent > 80:
            score -= 20
        elif server_metrics.cpu_percent > 60:
            score -= 10
        
        # 内存使用率评分
        if server_metrics.memory_percent > 85:
            score -= 20
        elif server_metrics.memory_percent > 70:
            score -= 10
        
        # 磁盘使用率评分
        if server_metrics.disk_percent > 90:
            score -= 20
        elif server_metrics.disk_percent > 80:
            score -= 10
        
        # 响应时间评分
        if app_metrics.avg_response_time > 5:
            score -= 20
        elif app_metrics.avg_response_time > 2:
            score -= 10
        
        return max(0, score)

    def _calculate_reliability_score(self, app_metrics, db_metrics):
        """计算可靠性评分"""
        score = 100
        
        # 错误率评分
        if app_metrics.total_requests > 0:
            error_rate = (app_metrics.failed_requests / app_metrics.total_requests) * 100
            if error_rate > 10:
                score -= 30
            elif error_rate > 5:
                score -= 15
            elif error_rate > 1:
                score -= 5
        
        # 数据库连接评分
        if db_metrics.active_connections > db_metrics.total_connections * 0.8:
            score -= 10
        
        # 慢查询评分
        if db_metrics.slow_queries > 10:
            score -= 15
        elif db_metrics.slow_queries > 5:
            score -= 10
        
        return max(0, score)

    def _calculate_security_score(self, app_metrics):
        """计算安全性评分"""
        score = 100
        
        # 基于错误类型的安全评分（这里简化处理）
        # 实际应用中可以根据具体的错误类型进行更细致的评分
        
        return score

    def _calculate_user_experience_score(self, app_metrics):
        """计算用户体验评分"""
        score = 100
        
        # 响应时间评分
        if app_metrics.avg_response_time > 3:
            score -= 25
        elif app_metrics.avg_response_time > 1:
            score -= 15
        elif app_metrics.avg_response_time > 0.5:
            score -= 5
        
        # 活跃用户数评分（相对评分）
        if app_metrics.active_users > 0:
            # 这里可以根据历史数据计算相对活跃度
            pass
        
        return max(0, score)
