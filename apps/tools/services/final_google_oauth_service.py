import os
import requests
from django.conf import settings
from apps.tools.services.simple_google_access import simple_google_access

class FinalGoogleOAuthService:
    """最终的Google OAuth服务"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        self.redirect_uri = 'https://shenyiqing.xin/tools/auth/google/callback/'
        self.scope = 'openid email profile'
        self.auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        self.token_url = 'https://oauth2.googleapis.com/token'
        self.user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    
    def get_auth_url(self, state=None):
        """获取Google OAuth授权URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{self.auth_url}?{query_string}'
    
    def exchange_code_for_token(self, code):
        """用授权码换取访问令牌"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = simple_google_access.make_request(
                self.token_url, 
                method='POST', 
                data=data
            )
            if response:
                return response.json()
            return None
        except Exception as e:
            print(f"获取令牌失败: {e}")
            return None
    
    def get_user_info(self, access_token):
        """获取用户信息"""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = simple_google_access.make_request(
                self.user_info_url,
                headers=headers
            )
            if response:
                return response.json()
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def test_connection(self):
        """测试Google连接"""
        try:
            return simple_google_access.test_google_access()
        except Exception as e:
            print(f"Google连接测试错误: {e}")
            return False

# 创建全局实例
final_google_oauth_service = FinalGoogleOAuthService()
