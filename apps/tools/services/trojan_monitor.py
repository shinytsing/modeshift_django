"""
Trojan代理监控模块
负责代理使用情况的实时监控、统计和告警
"""

import json
import logging
import psutil
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .trojan_user_manager import TrojanUserConfig, TrojanUsageLog

logger = logging.getLogger(__name__)


class TrojanMonitor:
    """Trojan代理监控器"""
    
    def __init__(self):
        self.metrics_cache = {}
        self.alert_thresholds = {
            "cpu_usage": 80,  # CPU使用率阈值
            "memory_usage": 85,  # 内存使用率阈值
            "disk_usage": 90,  # 磁盘使用率阈值
            "connection_count": 1000,  # 连接数阈值
            "bandwidth_usage": 100 * 1024 * 1024 * 1024,  # 带宽使用阈值 (100GB)
        }
        self.alerts = deque(maxlen=100)  # 保留最近100条告警
    
    def get_system_metrics(self) -> Dict:
        """获取系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 网络统计
            net_io = psutil.net_io_counters()
            
            # 进程信息
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'trojan' in proc.info['name'].lower():
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            metrics = {
                "timestamp": timezone.now().isoformat(),
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "usage_percent": memory_percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "usage_percent": disk_percent
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout
                },
                "processes": processes
            }
            
            # 检查告警
            self._check_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}
    
    def get_trojan_metrics(self) -> Dict:
        """获取Trojan相关指标"""
        try:
            # 获取所有活跃用户配置
            active_configs = TrojanUserConfig.objects.filter(is_active=True)
            
            # 获取最近24小时的使用统计
            since = timezone.now() - timedelta(hours=24)
            recent_logs = TrojanUsageLog.objects.filter(created_at__gte=since)
            
            # 统计指标
            total_users = active_configs.count()
            total_connections = sum(log.connection_count for log in recent_logs)
            total_bytes_sent = sum(log.bytes_sent for log in recent_logs)
            total_bytes_received = sum(log.bytes_received for log in recent_logs)
            total_session_duration = sum(log.session_duration for log in recent_logs)
            
            # 按用户统计
            user_stats = defaultdict(lambda: {
                'connections': 0,
                'bytes_sent': 0,
                'bytes_received': 0,
                'session_duration': 0
            })
            
            for log in recent_logs:
                user_id = log.user.id
                user_stats[user_id]['connections'] += log.connection_count
                user_stats[user_id]['bytes_sent'] += log.bytes_sent
                user_stats[user_id]['bytes_received'] += log.bytes_received
                user_stats[user_id]['session_duration'] += log.session_duration
            
            # 按小时统计
            hourly_stats = defaultdict(lambda: {
                'connections': 0,
                'bytes_sent': 0,
                'bytes_received': 0
            })
            
            for log in recent_logs:
                hour = log.created_at.hour
                hourly_stats[hour]['connections'] += log.connection_count
                hourly_stats[hour]['bytes_sent'] += log.bytes_sent
                hourly_stats[hour]['bytes_received'] += log.bytes_received
            
            metrics = {
                "timestamp": timezone.now().isoformat(),
                "summary": {
                    "total_users": total_users,
                    "total_connections": total_connections,
                    "total_bytes_sent": total_bytes_sent,
                    "total_bytes_received": total_bytes_received,
                    "total_bytes": total_bytes_sent + total_bytes_received,
                    "total_session_duration": total_session_duration,
                    "average_session_duration": total_session_duration / max(total_connections, 1)
                },
                "user_stats": dict(user_stats),
                "hourly_stats": dict(hourly_stats),
                "top_users": self._get_top_users(recent_logs, limit=10)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取Trojan指标失败: {e}")
            return {}
    
    def _get_top_users(self, logs, limit=10) -> List[Dict]:
        """获取使用量最高的用户"""
        try:
            user_stats = defaultdict(lambda: {
                'user_id': None,
                'username': '',
                'total_bytes': 0,
                'connections': 0
            })
            
            for log in logs:
                user_id = log.user.id
                if user_stats[user_id]['user_id'] is None:
                    user_stats[user_id]['user_id'] = user_id
                    user_stats[user_id]['username'] = log.user.username
                
                user_stats[user_id]['total_bytes'] += log.bytes_sent + log.bytes_received
                user_stats[user_id]['connections'] += log.connection_count
            
            # 按总流量排序
            sorted_users = sorted(
                user_stats.values(),
                key=lambda x: x['total_bytes'],
                reverse=True
            )
            
            return sorted_users[:limit]
            
        except Exception as e:
            logger.error(f"获取Top用户失败: {e}")
            return []
    
    def _check_alerts(self, metrics: Dict):
        """检查告警条件"""
        try:
            alerts = []
            
            # CPU使用率告警
            if metrics.get('cpu', {}).get('usage_percent', 0) > self.alert_thresholds['cpu_usage']:
                alerts.append({
                    'type': 'cpu_usage',
                    'level': 'warning',
                    'message': f"CPU使用率过高: {metrics['cpu']['usage_percent']:.1f}%",
                    'timestamp': timezone.now().isoformat()
                })
            
            # 内存使用率告警
            if metrics.get('memory', {}).get('usage_percent', 0) > self.alert_thresholds['memory_usage']:
                alerts.append({
                    'type': 'memory_usage',
                    'level': 'warning',
                    'message': f"内存使用率过高: {metrics['memory']['usage_percent']:.1f}%",
                    'timestamp': timezone.now().isoformat()
                })
            
            # 磁盘使用率告警
            if metrics.get('disk', {}).get('usage_percent', 0) > self.alert_thresholds['disk_usage']:
                alerts.append({
                    'type': 'disk_usage',
                    'level': 'critical',
                    'message': f"磁盘使用率过高: {metrics['disk']['usage_percent']:.1f}%",
                    'timestamp': timezone.now().isoformat()
                })
            
            # 添加告警到队列
            for alert in alerts:
                self.alerts.append(alert)
                logger.warning(f"告警: {alert['message']}")
            
        except Exception as e:
            logger.error(f"检查告警失败: {e}")
    
    def get_alerts(self, limit: int = 20) -> List[Dict]:
        """获取告警列表"""
        return list(self.alerts)[-limit:]
    
    def clear_alerts(self):
        """清除告警"""
        self.alerts.clear()
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        try:
            system_metrics = self.get_system_metrics()
            trojan_metrics = self.get_trojan_metrics()
            alerts = self.get_alerts(10)
            
            return {
                "system": system_metrics,
                "trojan": trojan_metrics,
                "alerts": alerts,
                "timestamp": timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取仪表板数据失败: {e}")
            return {}
    
    def get_user_activity(self, user: User, hours: int = 24) -> Dict:
        """获取用户活动情况"""
        try:
            since = timezone.now() - timedelta(hours=hours)
            logs = TrojanUsageLog.objects.filter(
                user=user,
                created_at__gte=since
            ).order_by('created_at')
            
            # 按小时分组
            hourly_activity = defaultdict(lambda: {
                'connections': 0,
                'bytes_sent': 0,
                'bytes_received': 0,
                'session_duration': 0
            })
            
            for log in logs:
                hour = log.created_at.strftime('%Y-%m-%d %H:00')
                hourly_activity[hour]['connections'] += log.connection_count
                hourly_activity[hour]['bytes_sent'] += log.bytes_sent
                hourly_activity[hour]['bytes_received'] += log.bytes_received
                hourly_activity[hour]['session_duration'] += log.session_duration
            
            # 按IP分组
            ip_activity = defaultdict(lambda: {
                'connections': 0,
                'bytes_sent': 0,
                'bytes_received': 0,
                'last_seen': None
            })
            
            for log in logs:
                ip = log.ip_address
                ip_activity[ip]['connections'] += log.connection_count
                ip_activity[ip]['bytes_sent'] += log.bytes_sent
                ip_activity[ip]['bytes_received'] += log.bytes_received
                if not ip_activity[ip]['last_seen'] or log.created_at > ip_activity[ip]['last_seen']:
                    ip_activity[ip]['last_seen'] = log.created_at
            
            return {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                },
                "period": f"{hours}小时",
                "summary": {
                    "total_logs": logs.count(),
                    "total_connections": sum(log.connection_count for log in logs),
                    "total_bytes_sent": sum(log.bytes_sent for log in logs),
                    "total_bytes_received": sum(log.bytes_received for log in logs),
                    "total_session_duration": sum(log.session_duration for log in logs)
                },
                "hourly_activity": dict(hourly_activity),
                "ip_activity": dict(ip_activity)
            }
            
        except Exception as e:
            logger.error(f"获取用户活动失败: {e}")
            return {}
    
    def get_bandwidth_usage(self, days: int = 7) -> Dict:
        """获取带宽使用情况"""
        try:
            since = timezone.now() - timedelta(days=days)
            logs = TrojanUsageLog.objects.filter(created_at__gte=since)
            
            # 按天分组
            daily_usage = defaultdict(lambda: {
                'bytes_sent': 0,
                'bytes_received': 0,
                'connections': 0,
                'users': set()
            })
            
            for log in logs:
                day = log.created_at.date().isoformat()
                daily_usage[day]['bytes_sent'] += log.bytes_sent
                daily_usage[day]['bytes_received'] += log.bytes_received
                daily_usage[day]['connections'] += log.connection_count
                daily_usage[day]['users'].add(log.user.id)
            
            # 转换set为count
            for day_data in daily_usage.values():
                day_data['unique_users'] = len(day_data['users'])
                del day_data['users']
            
            return {
                "period": f"{days}天",
                "daily_usage": dict(daily_usage),
                "total_bytes_sent": sum(log.bytes_sent for log in logs),
                "total_bytes_received": sum(log.bytes_received for log in logs),
                "total_connections": sum(log.connection_count for log in logs),
                "unique_users": len(set(log.user.id for log in logs))
            }
            
        except Exception as e:
            logger.error(f"获取带宽使用情况失败: {e}")
            return {}
    
    def export_usage_report(self, start_date: datetime, end_date: datetime, 
                           format: str = 'json') -> Tuple[bool, str, Optional[str]]:
        """导出使用报告"""
        try:
            logs = TrojanUsageLog.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).select_related('user')
            
            if format == 'json':
                data = []
                for log in logs:
                    data.append({
                        'user_id': log.user.id,
                        'username': log.user.username,
                        'bytes_sent': log.bytes_sent,
                        'bytes_received': log.bytes_received,
                        'total_bytes': log.bytes_sent + log.bytes_received,
                        'connections': log.connection_count,
                        'session_duration': log.session_duration,
                        'ip_address': log.ip_address,
                        'user_agent': log.user_agent,
                        'created_at': log.created_at.isoformat()
                    })
                
                report = json.dumps(data, indent=2, ensure_ascii=False)
                return True, "报告生成成功", report
                
            elif format == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入标题
                writer.writerow([
                    '用户ID', '用户名', '发送字节', '接收字节', '总字节', 
                    '连接数', '会话时长', 'IP地址', '用户代理', '时间'
                ])
                
                # 写入数据
                for log in logs:
                    writer.writerow([
                        log.user.id,
                        log.user.username,
                        log.bytes_sent,
                        log.bytes_received,
                        log.bytes_sent + log.bytes_received,
                        log.connection_count,
                        log.session_duration,
                        log.ip_address,
                        log.user_agent,
                        log.created_at.isoformat()
                    ])
                
                report = output.getvalue()
                output.close()
                return True, "报告生成成功", report
                
            else:
                return False, "不支持的格式", None
                
        except Exception as e:
            error_msg = f"导出使用报告失败: {e}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """清理旧日志"""
        try:
            cutoff_date = timezone.now() - timedelta(days=days)
            old_logs = TrojanUsageLog.objects.filter(created_at__lt=cutoff_date)
            count = old_logs.count()
            old_logs.delete()
            
            logger.info(f"清理了 {count} 条旧日志")
            return count
            
        except Exception as e:
            logger.error(f"清理旧日志失败: {e}")
            return 0

