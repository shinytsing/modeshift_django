"""
Google Auth 代理服务
用于服务器端代理 Google OAuth 认证，解决国内用户无法直接访问 Google Auth 的问题
"""

import os
import json
import logging
import requests
from urllib.parse import urlencode, parse_qs, urlparse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

User = get_user_model()


class GoogleAuthProxyService:
    """Google Auth 代理服务"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        self.redirect_uri = f"{settings.SITE_URL}/accounts/google/login/callback/"
        # 不使用代理，直接访问Google API
        self.proxy_configs = [None]  # 只使用无代理配置
        self.proxy_config = None
        
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured")
    
    def get_auth_url(self, state: str = None) -> str:
        """
        生成 Google OAuth 授权 URL
        这个 URL 会通过服务器代理访问 Google
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
        }
        
        if state:
            params['state'] = state
            
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        logger.info(f"Generated Google auth URL: {auth_url}")
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        通过授权码换取访问令牌
        使用服务器代理访问 Google Token 端点
        """
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
        }
        
        # 直接访问Google Token端点，不使用代理
        try:
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=token_data,
                proxies=None,  # 明确不使用代理
                timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise requests.RequestException(f"Google token exchange failed: {e}")
        
        # 成功获取响应后处理
        token_info = response.json()
        logger.info("Successfully exchanged code for token")
        return token_info
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        获取用户信息
        使用服务器代理访问 Google UserInfo 端点
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }
        
        # 直接访问Google API，不使用代理
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers,
                proxies=None,  # 明确不使用代理
                timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to get user info from Google API: {e}")
            raise requests.RequestException(f"Google API request failed: {e}")
        
        # 成功获取响应后处理
        user_info = response.json()
        logger.info(f"Successfully retrieved user info for: {user_info.get('email')}")
        return user_info
    
    def create_or_update_user(self, user_info: Dict[str, Any]) -> Tuple[User, bool]:
        """
        创建或更新用户
        返回 (user, created) 元组
        """
        email = user_info.get('email')
        if not email:
            raise ValidationError("Email is required")
        
        # 尝试通过邮箱查找现有用户
        try:
            user = User.objects.get(email=email)
            created = False
            
            # 更新用户信息
            user.first_name = user_info.get('given_name', '')
            user.last_name = user_info.get('family_name', '')
            user.save()
            
            logger.info(f"Updated existing user: {email}")
            
        except User.DoesNotExist:
            # 创建新用户
            username = email.split('@')[0]  # 使用邮箱前缀作为用户名
            
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
                is_active=True
            )
            created = True
            
            logger.info(f"Created new user: {email}")
        
        return user, created
    
    def authenticate_user(self, code: str, state: str = None) -> Tuple[User, bool]:
        """
        完整的用户认证流程
        1. 通过授权码获取访问令牌
        2. 获取用户信息
        3. 创建或更新用户
        返回 (user, created) 元组
        """
        try:
            # 1. 获取访问令牌
            token_info = self.exchange_code_for_token(code)
            access_token = token_info.get('access_token')
            
            if not access_token:
                raise ValidationError("No access token received")
            
            # 2. 获取用户信息
            user_info = self.get_user_info(access_token)
            
            # 3. 创建或更新用户
            user, created = self.create_or_update_user(user_info)
            
            return user, created
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise ValidationError(f"Authentication failed: {str(e)}")
    
    def validate_state(self, received_state: str, expected_state: str) -> bool:
        """验证 state 参数防止 CSRF 攻击"""
        return received_state == expected_state


class GoogleAuthProxyViewMixin:
    """Google Auth 代理视图混入类"""
    
    @property
    def auth_proxy(self):
        """获取认证代理服务实例"""
        if not hasattr(self, '_auth_proxy'):
            self._auth_proxy = GoogleAuthProxyService()
        return self._auth_proxy
    
    def get_auth_url_with_state(self, request) -> str:
        """生成带 state 参数的授权 URL"""
        # 使用 session ID 作为 state 参数
        state = request.session.session_key or str(request.session.create())
        return self.auth_proxy.get_auth_url(state)
    
    def handle_auth_callback(self, request, code: str, state: str = None) -> Tuple[User, bool]:
        """处理认证回调"""
        # 验证 state 参数
        expected_state = request.session.session_key
        if not self.auth_proxy.validate_state(state, expected_state):
            raise ValidationError("Invalid state parameter")
        
        # 执行认证
        return self.auth_proxy.authenticate_user(code, state)
