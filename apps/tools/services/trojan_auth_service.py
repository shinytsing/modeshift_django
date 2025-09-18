"""
Trojan认证服务模块
集成Google OAuth和其他认证方式
"""

import logging
import secrets
from typing import Dict, Optional, Tuple

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils import timezone

from .trojan_user_manager import TrojanUserManager

logger = logging.getLogger(__name__)


class TrojanAuthService:
    """Trojan认证服务"""
    
    def __init__(self):
        self.user_manager = TrojanUserManager()
    
    def authenticate_user(self, request: HttpRequest, username: str = None, 
                         password: str = None, google_token: str = None) -> Tuple[bool, str, Optional[User]]:
        """用户认证"""
        try:
            user = None
            
            if google_token:
                # Google OAuth认证
                success, msg, user = self._authenticate_google_oauth(google_token)
                if not success:
                    return False, msg, None
            elif username and password:
                # 传统用户名密码认证
                user = authenticate(request, username=username, password=password)
                if not user:
                    return False, "用户名或密码错误", None
            else:
                return False, "缺少认证信息", None
            
            # 检查用户状态
            if not user.is_active:
                return False, "用户账户已被禁用", None
            
            # 检查用户是否有Trojan配置权限
            if not self._check_trojan_permission(user):
                return False, "用户没有Trojan代理权限", None
            
            # 记录登录活动
            self._log_auth_activity(user, request, "login_success")
            
            return True, "认证成功", user
            
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return False, f"认证失败: {e}", None
    
    def _authenticate_google_oauth(self, token: str) -> Tuple[bool, str, Optional[User]]:
        """Google OAuth认证"""
        try:
            import requests
            
            # 验证Google token
            google_api_url = f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
            response = requests.get(google_api_url, timeout=10)
            
            if response.status_code != 200:
                return False, "Google token验证失败", None
            
            user_info = response.json()
            
            # 获取或创建用户
            email = user_info.get('email')
            if not email:
                return False, "无法获取Google用户邮箱", None
            
            # 查找现有用户
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # 创建新用户
                username = email.split('@')[0]
                # 确保用户名唯一
                original_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}_{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    password=secrets.token_urlsafe(32)  # 随机密码
                )
                
                logger.info(f"通过Google OAuth创建新用户: {username}")
            
            return True, "Google OAuth认证成功", user
            
        except Exception as e:
            logger.error(f"Google OAuth认证失败: {e}")
            return False, f"Google OAuth认证失败: {e}", None
    
    def _check_trojan_permission(self, user: User) -> bool:
        """检查用户Trojan权限"""
        try:
            # 检查用户角色
            if hasattr(user, 'role') and user.role.is_admin:
                return True
            
            # 检查用户会员状态
            if hasattr(user, 'membership') and user.membership.is_valid:
                return True
            
            # 检查用户状态
            if hasattr(user, 'status') and not user.status.is_active:
                return False
            
            # 默认允许所有活跃用户使用Trojan
            return True
            
        except Exception as e:
            logger.error(f"检查Trojan权限失败: {e}")
            return False
    
    def _log_auth_activity(self, user: User, request: HttpRequest, activity_type: str):
        """记录认证活动"""
        try:
            from apps.users.models import UserActivityLog
            
            # 获取IP地址
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # 记录活动
            UserActivityLog.objects.create(
                user=user,
                activity_type="login",
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    "login_method": "google_oauth" if "google" in activity_type else "password",
                    "success": "success" in activity_type,
                    "trojan_access": True
                }
            )
            
        except Exception as e:
            logger.error(f"记录认证活动失败: {e}")
    
    def create_trojan_config_for_user(self, user: User, expires_days: int = 30) -> Tuple[bool, str, Optional[Dict]]:
        """为用户创建Trojan配置"""
        try:
            # 检查用户是否已有配置
            existing_config = self.user_manager.get_user_config(user)
            if existing_config:
                return False, "用户已有Trojan配置", None
            
            # 创建配置
            success, msg, config = self.user_manager.create_user_config(
                user=user,
                expires_days=expires_days
            )
            
            if not success:
                return False, msg, None
            
            # 生成客户端配置
            success, msg, client_config = self.user_manager.generate_client_config(user)
            if not success:
                return False, msg, None
            
            return True, "Trojan配置创建成功", {
                "config": config,
                "client_config": client_config
            }
            
        except Exception as e:
            logger.error(f"创建Trojan配置失败: {e}")
            return False, f"创建配置失败: {e}", None
    
    def get_user_trojan_info(self, user: User) -> Dict:
        """获取用户Trojan信息"""
        try:
            config = self.user_manager.get_user_config(user)
            if not config:
                return {
                    "has_config": False,
                    "message": "用户没有Trojan配置"
                }
            
            # 获取使用统计
            usage_stats = self.user_manager.get_user_usage_stats(user, days=30)
            
            # 生成各种配置
            success, msg, client_config = self.user_manager.generate_client_config(user)
            clash_config = None
            v2ray_config = None
            
            if success:
                _, _, clash_config = self.user_manager.generate_clash_config(user)
                _, _, v2ray_config = self.user_manager.generate_v2ray_config(user)
            
            return {
                "has_config": True,
                "config": {
                    "server_host": config.server_host,
                    "server_port": config.server_port,
                    "local_port": config.local_port,
                    "is_active": config.is_active,
                    "is_expired": config.is_expired,
                    "days_remaining": config.days_remaining,
                    "created_at": config.created_at.isoformat(),
                    "last_used": config.last_used.isoformat() if config.last_used else None
                },
                "usage_stats": usage_stats,
                "client_config": client_config,
                "clash_config": clash_config,
                "v2ray_config": v2ray_config
            }
            
        except Exception as e:
            logger.error(f"获取用户Trojan信息失败: {e}")
            return {
                "has_config": False,
                "error": str(e)
            }
    
    def refresh_user_config(self, user: User) -> Tuple[bool, str]:
        """刷新用户配置"""
        try:
            config = self.user_manager.get_user_config(user)
            if not config:
                return False, "用户配置不存在"
            
            # 重新生成密码
            success, msg, new_password = self.user_manager.regenerate_password(user)
            if not success:
                return False, msg
            
            # 更新过期时间
            config.expires_at = timezone.now() + timezone.timedelta(days=30)
            config.save()
            
            logger.info(f"用户 {user.username} 的Trojan配置已刷新")
            return True, "配置刷新成功"
            
        except Exception as e:
            logger.error(f"刷新用户配置失败: {e}")
            return False, f"刷新配置失败: {e}"
    
    def revoke_user_access(self, user: User) -> Tuple[bool, str]:
        """撤销用户访问权限"""
        try:
            config = self.user_manager.get_user_config(user)
            if not config:
                return False, "用户配置不存在"
            
            # 停用配置
            config.is_active = False
            config.save()
            
            # 从服务器配置中移除密码
            self.user_manager.server_manager.remove_user_password(config.password)
            
            logger.info(f"用户 {user.username} 的Trojan访问权限已撤销")
            return True, "访问权限已撤销"
            
        except Exception as e:
            logger.error(f"撤销用户访问权限失败: {e}")
            return False, f"撤销权限失败: {e}"
    
    def restore_user_access(self, user: User) -> Tuple[bool, str]:
        """恢复用户访问权限"""
        try:
            config = self.user_manager.get_user_config(user)
            if not config:
                return False, "用户配置不存在"
            
            # 激活配置
            config.is_active = True
            config.save()
            
            # 重新添加密码到服务器配置
            success, msg = self.user_manager.server_manager.add_user_password(config.password)
            if not success:
                config.is_active = False
                config.save()
                return False, f"恢复服务器配置失败: {msg}"
            
            logger.info(f"用户 {user.username} 的Trojan访问权限已恢复")
            return True, "访问权限已恢复"
            
        except Exception as e:
            logger.error(f"恢复用户访问权限失败: {e}")
            return False, f"恢复权限失败: {e}"
    
    def get_google_oauth_url(self, request: HttpRequest) -> str:
        """获取Google OAuth授权URL"""
        try:
            import os
            from urllib.parse import urlencode
            
            client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
            if not client_id:
                raise ValueError("Google OAuth Client ID未配置")
            
            # 构建回调URL
            redirect_uri = f"{request.scheme}://{request.get_host()}/trojan/auth/google/callback/"
            
            # OAuth参数
            params = {
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'scope': 'openid email profile',
                'response_type': 'code',
                'state': secrets.token_urlsafe(32),  # 防止CSRF攻击
                'access_type': 'offline',
                'prompt': 'consent'
            }
            
            # 保存state到session
            request.session['oauth_state'] = params['state']
            
            # 构建授权URL
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
            
            return auth_url
            
        except Exception as e:
            logger.error(f"生成Google OAuth URL失败: {e}")
            raise
    
    def handle_google_oauth_callback(self, request: HttpRequest, code: str, state: str) -> Tuple[bool, str, Optional[User]]:
        """处理Google OAuth回调"""
        try:
            import os
            import requests
            
            # 验证state
            if state != request.session.get('oauth_state'):
                return False, "无效的OAuth state", None
            
            # 清除session中的state
            request.session.pop('oauth_state', None)
            
            client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                return False, "Google OAuth配置不完整", None
            
            # 构建回调URL
            redirect_uri = f"{request.scheme}://{request.get_host()}/trojan/auth/google/callback/"
            
            # 交换access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = requests.post(token_url, data=token_data, timeout=10)
            if response.status_code != 200:
                return False, "获取access token失败", None
            
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                return False, "未获取到access token", None
            
            # 使用access token进行认证
            return self.authenticate_user(request, google_token=access_token)
            
        except Exception as e:
            logger.error(f"处理Google OAuth回调失败: {e}")
            return False, f"OAuth回调处理失败: {e}", None

