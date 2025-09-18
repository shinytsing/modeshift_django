"""
Trojan用户管理模块
负责用户代理配置的生成、分发和管理
"""

import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .trojan_protocol import TrojanConfig
from .trojan_server_manager import TrojanServerManager

logger = logging.getLogger(__name__)


class TrojanUserConfig(models.Model):
    """Trojan用户配置模型"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trojan_config")
    password = models.CharField(max_length=255, verbose_name="Trojan密码")
    server_host = models.CharField(max_length=255, default="shenyiqing.xin", verbose_name="服务器地址")
    server_port = models.IntegerField(default=443, verbose_name="服务器端口")
    local_port = models.IntegerField(default=1080, verbose_name="本地端口")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间")
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="最后使用时间")
    
    class Meta:
        db_table = "trojan_user_config"
        verbose_name = "Trojan用户配置"
        verbose_name_plural = "Trojan用户配置"
    
    def __str__(self):
        return f"{self.user.username} - Trojan配置"
    
    @property
    def is_expired(self):
        """检查是否过期"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def days_remaining(self):
        """剩余天数"""
        if not self.expires_at:
            return None
        delta = self.expires_at - timezone.now()
        return delta.days if delta.days > 0 else 0


class TrojanUsageLog(models.Model):
    """Trojan使用日志模型"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trojan_usage_logs")
    bytes_sent = models.BigIntegerField(default=0, verbose_name="发送字节数")
    bytes_received = models.BigIntegerField(default=0, verbose_name="接收字节数")
    connection_count = models.IntegerField(default=0, verbose_name="连接次数")
    session_duration = models.IntegerField(default=0, verbose_name="会话时长(秒)")
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    user_agent = models.TextField(verbose_name="用户代理", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="记录时间")
    
    class Meta:
        db_table = "trojan_usage_log"
        verbose_name = "Trojan使用日志"
        verbose_name_plural = "Trojan使用日志"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["ip_address", "created_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class TrojanUserManager:
    """Trojan用户管理器"""
    
    def __init__(self):
        self.server_manager = TrojanServerManager()
    
    def create_user_config(self, user: User, server_host: str = "shenyiqing.xin", 
                          server_port: int = 443, expires_days: int = 30) -> Tuple[bool, str, Optional[TrojanUserConfig]]:
        """为用户创建Trojan配置"""
        try:
            # 检查用户是否已有配置
            existing_config = self.get_user_config(user)
            if existing_config:
                return False, "用户已有Trojan配置", existing_config
            
            # 生成唯一密码
            password = self.generate_password()
            
            # 创建配置记录
            config = TrojanUserConfig.objects.create(
                user=user,
                password=password,
                server_host=server_host,
                server_port=server_port,
                expires_at=timezone.now() + timedelta(days=expires_days) if expires_days > 0 else None
            )
            
            # 在服务器配置中添加密码
            success, msg = self.server_manager.add_user_password(password)
            if not success:
                config.delete()
                return False, f"添加服务器密码失败: {msg}", None
            
            logger.info(f"为用户 {user.username} 创建Trojan配置成功")
            return True, "配置创建成功", config
            
        except Exception as e:
            error_msg = f"创建用户配置失败: {e}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def get_user_config(self, user: User) -> Optional[TrojanUserConfig]:
        """获取用户配置"""
        try:
            return TrojanUserConfig.objects.get(user=user)
        except TrojanUserConfig.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"获取用户配置失败: {e}")
            return None
    
    def update_user_config(self, user: User, **kwargs) -> Tuple[bool, str]:
        """更新用户配置"""
        try:
            config = self.get_user_config(user)
            if not config:
                return False, "用户配置不存在"
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.save()
            
            logger.info(f"用户 {user.username} 的Trojan配置已更新")
            return True, "配置更新成功"
            
        except Exception as e:
            error_msg = f"更新用户配置失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_user_config(self, user: User) -> Tuple[bool, str]:
        """删除用户配置"""
        try:
            config = self.get_user_config(user)
            if not config:
                return False, "用户配置不存在"
            
            # 从服务器配置中移除密码
            success, msg = self.server_manager.remove_user_password(config.password)
            if not success:
                logger.warning(f"移除服务器密码失败: {msg}")
            
            # 删除配置记录
            config.delete()
            
            logger.info(f"用户 {user.username} 的Trojan配置已删除")
            return True, "配置删除成功"
            
        except Exception as e:
            error_msg = f"删除用户配置失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def regenerate_password(self, user: User) -> Tuple[bool, str, Optional[str]]:
        """重新生成用户密码"""
        try:
            config = self.get_user_config(user)
            if not config:
                return False, "用户配置不存在", None
            
            old_password = config.password
            new_password = self.generate_password()
            
            # 更新配置
            config.password = new_password
            config.save()
            
            # 更新服务器配置
            self.server_manager.remove_user_password(old_password)
            success, msg = self.server_manager.add_user_password(new_password)
            if not success:
                # 回滚
                config.password = old_password
                config.save()
                self.server_manager.add_user_password(old_password)
                return False, f"更新服务器密码失败: {msg}", None
            
            logger.info(f"用户 {user.username} 的Trojan密码已重新生成")
            return True, "密码重新生成成功", new_password
            
        except Exception as e:
            error_msg = f"重新生成密码失败: {e}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def generate_password(self) -> str:
        """生成Trojan密码"""
        return secrets.token_urlsafe(32)
    
    def generate_client_config(self, user: User) -> Tuple[bool, str, Optional[Dict]]:
        """生成客户端配置"""
        try:
            config = self.get_user_config(user)
            if not config:
                return False, "用户配置不存在", None
            
            if not config.is_active:
                return False, "用户配置未激活", None
            
            if config.is_expired:
                return False, "用户配置已过期", None
            
            # 生成Trojan客户端配置
            client_config = TrojanConfig.generate_client_config(
                server_host=config.server_host,
                server_port=config.server_port,
                password=config.password,
                ssl_verify=False  # 使用自签名证书时设为False
            )
            
            # 更新最后使用时间
            config.last_used = timezone.now()
            config.save()
            
            logger.info(f"为用户 {user.username} 生成客户端配置")
            return True, "配置生成成功", client_config
            
        except Exception as e:
            error_msg = f"生成客户端配置失败: {e}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def generate_clash_config(self, user: User) -> Tuple[bool, str, Optional[Dict]]:
        """生成Clash配置"""
        try:
            config = self.get_user_config(user)
            if not config:
                return False, "用户配置不存在", None
            
            if not config.is_active:
                return False, "用户配置未激活", None
            
            if config.is_expired:
                return False, "用户配置已过期", None
            
            # 生成Clash配置
            clash_config = {
                "port": 7890,
                "socks-port": 7891,
                "allow-lan": True,
                "mode": "rule",
                "log-level": "info",
                "external-controller": "127.0.0.1:9090",
                "proxies": [
                    {
                        "name": f"Trojan-{user.username}",
                        "type": "trojan",
                        "server": config.server_host,
                        "port": config.server_port,
                        "password": config.password,
                        "sni": config.server_host,
                        "skip-cert-verify": True,
                        "udp": True,
                    }
                ],
                "proxy-groups": [
                    {
                        "name": "PROXY",
                        "type": "select",
                        "proxies": [f"Trojan-{user.username}", "DIRECT"]
                    },
                    {
                        "name": "Auto",
                        "type": "url-test",
                        "url": "http://www.gstatic.com/generate_204",
                        "interval": 300,
                        "proxies": [f"Trojan-{user.username}"]
                    }
                ],
                "rules": [
                    "DOMAIN-KEYWORD,google,PROXY",
                    "DOMAIN-KEYWORD,youtube,PROXY",
                    "DOMAIN-KEYWORD,facebook,PROXY",
                    "DOMAIN-KEYWORD,twitter,PROXY",
                    "DOMAIN-KEYWORD,instagram,PROXY",
                    "DOMAIN-KEYWORD,github,PROXY",
                    "DOMAIN-SUFFIX,googleapis.com,PROXY",
                    "DOMAIN-SUFFIX,gstatic.com,PROXY",
                    "DOMAIN-SUFFIX,ytimg.com,PROXY",
                    "DOMAIN-SUFFIX,googlevideo.com,PROXY",
                    "GEOIP,CN,DIRECT",
                    "MATCH,PROXY"
                ]
            }
            
            # 更新最后使用时间
            config.last_used = timezone.now()
            config.save()
            
            logger.info(f"为用户 {user.username} 生成Clash配置")
            return True, "Clash配置生成成功", clash_config
            
        except Exception as e:
            error_msg = f"生成Clash配置失败: {e}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def generate_v2ray_config(self, user: User) -> Tuple[bool, str, Optional[Dict]]:
        """生成V2Ray配置"""
        try:
            config = self.get_user_config(user)
            if not config:
                return False, "用户配置不存在", None
            
            if not config.is_active:
                return False, "用户配置未激活", None
            
            if config.is_expired:
                return False, "用户配置已过期", None
            
            # 生成V2Ray配置
            v2ray_config = {
                "log": {
                    "loglevel": "warning"
                },
                "inbounds": [
                    {
                        "port": config.local_port,
                        "protocol": "socks",
                        "settings": {
                            "auth": "noauth",
                            "udp": True
                        }
                    }
                ],
                "outbounds": [
                    {
                        "protocol": "trojan",
                        "settings": {
                            "servers": [
                                {
                                    "address": config.server_host,
                                    "port": config.server_port,
                                    "password": config.password
                                }
                            ]
                        },
                        "streamSettings": {
                            "network": "tcp",
                            "security": "tls",
                            "tlsSettings": {
                                "serverName": config.server_host,
                                "allowInsecure": True
                            }
                        }
                    }
                ]
            }
            
            # 更新最后使用时间
            config.last_used = timezone.now()
            config.save()
            
            logger.info(f"为用户 {user.username} 生成V2Ray配置")
            return True, "V2Ray配置生成成功", v2ray_config
            
        except Exception as e:
            error_msg = f"生成V2Ray配置失败: {e}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def log_usage(self, user: User, bytes_sent: int = 0, bytes_received: int = 0,
                  connection_count: int = 1, session_duration: int = 0,
                  ip_address: str = None, user_agent: str = "") -> bool:
        """记录使用情况"""
        try:
            TrojanUsageLog.objects.create(
                user=user,
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                connection_count=connection_count,
                session_duration=session_duration,
                ip_address=ip_address or "127.0.0.1",
                user_agent=user_agent
            )
            return True
        except Exception as e:
            logger.error(f"记录使用情况失败: {e}")
            return False
    
    def get_user_usage_stats(self, user: User, days: int = 30) -> Dict:
        """获取用户使用统计"""
        try:
            since = timezone.now() - timedelta(days=days)
            logs = TrojanUsageLog.objects.filter(user=user, created_at__gte=since)
            
            total_bytes_sent = sum(log.bytes_sent for log in logs)
            total_bytes_received = sum(log.bytes_received for log in logs)
            total_connections = sum(log.connection_count for log in logs)
            total_duration = sum(log.session_duration for log in logs)
            
            return {
                "total_bytes_sent": total_bytes_sent,
                "total_bytes_received": total_bytes_received,
                "total_bytes": total_bytes_sent + total_bytes_received,
                "total_connections": total_connections,
                "total_duration": total_duration,
                "average_session_duration": total_duration / max(total_connections, 1),
                "days": days,
                "log_count": logs.count()
            }
        except Exception as e:
            logger.error(f"获取用户使用统计失败: {e}")
            return {}
    
    def get_all_users_with_config(self) -> List[TrojanUserConfig]:
        """获取所有有配置的用户"""
        try:
            return TrojanUserConfig.objects.filter(is_active=True).select_related('user')
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    def cleanup_expired_configs(self) -> int:
        """清理过期配置"""
        try:
            expired_configs = TrojanUserConfig.objects.filter(
                expires_at__lt=timezone.now(),
                is_active=True
            )
            
            count = 0
            for config in expired_configs:
                # 从服务器配置中移除密码
                self.server_manager.remove_user_password(config.password)
                
                # 停用配置
                config.is_active = False
                config.save()
                
                count += 1
            
            logger.info(f"清理了 {count} 个过期配置")
            return count
            
        except Exception as e:
            logger.error(f"清理过期配置失败: {e}")
            return 0
    
    def get_server_status(self) -> Dict:
        """获取服务器状态"""
        return self.server_manager.get_server_status()
    
    def start_server(self) -> Tuple[bool, str]:
        """启动服务器"""
        return self.server_manager.start_server()
    
    def stop_server(self) -> Tuple[bool, str]:
        """停止服务器"""
        return self.server_manager.stop_server()
    
    def restart_server(self) -> Tuple[bool, str]:
        """重启服务器"""
        return self.server_manager.restart_server()

