"""
Cookie 存储服务
参考 get_jobs 项目的实现方式，提供完整的 cookie 管理功能
"""
import json
import logging
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from playwright.sync_api import sync_playwright
from ..models.user_cookie import UserCookie, CookieSession

logger = logging.getLogger(__name__)


class CookieStorageService:
    """Cookie 存储服务"""
    
    def __init__(self, user: User):
        self.user = user
    
    def save_cookies(self, platform: str, cookies_dict: dict) -> bool:
        """保存用户 cookies 到数据库"""
        try:
            # 获取或创建 UserCookie 对象
            user_cookie, created = UserCookie.objects.get_or_create(
                user=self.user,
                platform=platform,
                defaults={
                    'cookies': cookies_dict,
                    'is_active': True,
                    'expires_at': timezone.now() + timedelta(days=7)  # 默认7天过期
                }
            )
            
            if not created:
                # 更新现有记录
                user_cookie.cookies = cookies_dict
                user_cookie.is_active = True
                user_cookie.expires_at = timezone.now() + timedelta(days=7)
                user_cookie.save()
            
            logger.info(f"✅ 成功保存用户 {self.user.username} 的 {platform} cookies")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存 cookies 失败: {str(e)}")
            return False
    
    def get_cookies(self, platform: str) -> dict:
        """获取用户 cookies"""
        try:
            user_cookie = UserCookie.objects.filter(
                user=self.user,
                platform=platform,
                is_active=True
            ).first()
            
            if user_cookie and not user_cookie.is_expired():
                return user_cookie.get_cookies_dict()
            else:
                logger.warning(f"用户 {self.user.username} 的 {platform} cookies 不存在或已过期")
                return {}
                
        except Exception as e:
            logger.error(f"获取 cookies 失败: {str(e)}")
            return {}
    
    def get_playwright_cookies(self, platform: str) -> list:
        """获取 Playwright 格式的 cookies"""
        try:
            user_cookie = UserCookie.objects.filter(
                user=self.user,
                platform=platform,
                is_active=True
            ).first()
            
            if user_cookie and not user_cookie.is_expired():
                return user_cookie.get_playwright_cookies()
            else:
                logger.warning(f"用户 {self.user.username} 的 {platform} cookies 不存在或已过期")
                return []
                
        except Exception as e:
            logger.error(f"获取 Playwright cookies 失败: {str(e)}")
            return []
    
    def save_storage_state(self, platform: str, storage_state: dict) -> bool:
        """保存 Playwright storage state"""
        try:
            session_id = f"{self.user.id}_{platform}_{int(timezone.now().timestamp())}"
            
            cookie_session, created = CookieSession.objects.get_or_create(
                user=self.user,
                platform=platform,
                session_id=session_id,
                defaults={
                    'storage_state': storage_state,
                    'is_active': True
                }
            )
            
            if not created:
                cookie_session.storage_state = storage_state
                cookie_session.save()
            
            logger.info(f"✅ 成功保存用户 {self.user.username} 的 {platform} storage state")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存 storage state 失败: {str(e)}")
            return False
    
    def get_storage_state(self, platform: str) -> dict:
        """获取 Playwright storage state"""
        try:
            cookie_session = CookieSession.objects.filter(
                user=self.user,
                platform=platform,
                is_active=True
            ).order_by('-last_used').first()
            
            if cookie_session:
                return cookie_session.get_storage_state()
            else:
                logger.warning(f"用户 {self.user.username} 的 {platform} storage state 不存在")
                return {}
                
        except Exception as e:
            logger.error(f"获取 storage state 失败: {str(e)}")
            return {}
    
    def validate_cookies(self, platform: str) -> dict:
        """验证 cookies 有效性"""
        try:
            cookies = self.get_cookies(platform)
            if not cookies:
                return {
                    'success': False,
                    'is_logged_in': False,
                    'error': '没有找到有效的 cookies'
                }
            
            # 使用 Playwright 验证 cookies
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # 设置 cookies
                playwright_cookies = self.get_playwright_cookies(platform)
                if playwright_cookies:
                    context.add_cookies(playwright_cookies)
                
                # 访问平台页面验证
                if platform == 'boss':
                    page.goto("https://www.zhipin.com/web/geek/jobs", wait_until="domcontentloaded", timeout=10000)
                    
                    # 检查登录状态
                    login_indicators = ['.user-info', '.user-avatar', '.geek-info', '.geek-name']
                    is_logged_in = False
                    
                    for indicator in login_indicators:
                        try:
                            element = page.query_selector(indicator)
                            if element:
                                is_logged_in = True
                                break
                        except:
                            continue
                    
                    browser.close()
                    
                    return {
                        'success': True,
                        'is_logged_in': is_logged_in,
                        'message': '登录状态验证完成',
                        'cookie_count': len(cookies)
                    }
                else:
                    browser.close()
                    return {
                        'success': False,
                        'is_logged_in': False,
                        'error': f'不支持的平台: {platform}'
                    }
                    
        except Exception as e:
            logger.error(f"验证 cookies 失败: {str(e)}")
            return {
                'success': False,
                'is_logged_in': False,
                'error': f'验证失败: {str(e)}'
            }
    
    def clear_cookies(self, platform: str = None) -> bool:
        """清除 cookies"""
        try:
            if platform:
                # 清除特定平台的 cookies
                UserCookie.objects.filter(user=self.user, platform=platform).update(is_active=False)
                CookieSession.objects.filter(user=self.user, platform=platform).update(is_active=False)
                logger.info(f"✅ 清除用户 {self.user.username} 的 {platform} cookies")
            else:
                # 清除所有平台的 cookies
                UserCookie.objects.filter(user=self.user).update(is_active=False)
                CookieSession.objects.filter(user=self.user).update(is_active=False)
                logger.info(f"✅ 清除用户 {self.user.username} 的所有 cookies")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 清除 cookies 失败: {str(e)}")
            return False
    
    def get_user_cookies_info(self) -> dict:
        """获取用户所有 cookies 信息"""
        try:
            cookies_info = {}
            
            user_cookies = UserCookie.objects.filter(user=self.user, is_active=True)
            for cookie in user_cookies:
                cookies_info[cookie.platform] = {
                    'cookie_count': len(cookie.get_cookies_dict()),
                    'created_at': cookie.created_at,
                    'updated_at': cookie.updated_at,
                    'expires_at': cookie.expires_at,
                    'is_expired': cookie.is_expired()
                }
            
            return cookies_info
            
        except Exception as e:
            logger.error(f"获取用户 cookies 信息失败: {str(e)}")
            return {}


# 全局 cookie 存储服务实例
def get_cookie_storage_service(user: User) -> CookieStorageService:
    """获取用户 cookie 存储服务实例"""
    return CookieStorageService(user)
