"""
Cookie管理服务 - 参考Java项目get_jobs的实现
提供类似Java项目的cookie持久化和管理功能
"""

import json
import os
import time
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)


class CookieManagerService:
    """Cookie管理服务类 - 参考Java项目的PlaywrightUtil和SeleniumUtil"""
    
    def __init__(self, user: User, platform: str = "boss"):
        self.user = user
        self.platform = platform
        self.cookie_dir = os.path.join(settings.BASE_DIR, 'get_jobs_integration', 'cookies')
        self.cookie_file = os.path.join(self.cookie_dir, f'{platform}_cookies_{user.id}.json')
        self.token_file = os.path.join(self.cookie_dir, f'{platform}_token_{user.id}.json')
        
        # 确保目录存在
        os.makedirs(self.cookie_dir, exist_ok=True)
    
    def save_cookies(self, cookies: List[Dict[str, Any]], device_type: str = "desktop") -> bool:
        """
        保存cookies到文件 - 参考Java项目的saveCookies方法
        """
        try:
            cookie_data = {
                'cookies': cookies,
                'device_type': device_type,
                'user_id': self.user.id,
                'username': self.user.username,
                'save_time': time.time(),
                'expires_at': time.time() + (7 * 24 * 60 * 60),  # 7天后过期
                'platform': self.platform
            }
            
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, ensure_ascii=False, indent=2)
            
            # 同时保存到Redis缓存
            cache_key = f"cookies:{self.platform}:{self.user.id}"
            cache.set(cache_key, cookie_data, 60 * 60 * 24 * 7)  # 7天
            
            logger.info(f"Cookies已保存到文件: {self.cookie_file} (用户: {self.user.username}, 平台: {self.platform})")
            return True
            
        except Exception as e:
            logger.error(f"保存Cookies失败 (用户: {self.user.username}, 平台: {self.platform}): {e}")
            return False
    
    def load_cookies(self, device_type: str = "desktop") -> List[Dict[str, Any]]:
        """
        从文件加载cookies - 参考Java项目的loadCookies方法
        """
        try:
            # 先从Redis缓存尝试
            cache_key = f"cookies:{self.platform}:{self.user.id}"
            cached_data = cache.get(cache_key)
            
            if cached_data and cached_data.get('cookies'):
                logger.info(f"从缓存加载Cookies: {self.platform} (用户: {self.user.username})")
                return cached_data['cookies']
            
            # 从文件加载
            if not os.path.exists(self.cookie_file):
                # 只在调试模式下记录警告，避免日志污染
                if settings.DEBUG:
                    logger.debug(f"Cookie文件不存在: {self.cookie_file}")
                return []
            
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            cookies = cookie_data.get('cookies', [])
            
            # 检查是否过期
            expires_at = cookie_data.get('expires_at', 0)
            if time.time() > expires_at:
                logger.warning(f"Cookies已过期: {self.platform} (用户: {self.user.username})")
                return []
            
            # 更新缓存
            cache.set(cache_key, cookie_data, 60 * 60 * 24 * 7)
            
            logger.info(f"已从文件加载Cookies: {self.platform} (用户: {self.user.username}, 数量: {len(cookies)})")
            return cookies
            
        except Exception as e:
            logger.error(f"加载Cookies失败 (用户: {self.user.username}, 平台: {self.platform}): {e}")
            return []
    
    def save_token(self, token: str, login_method: str = "token") -> bool:
        """
        保存登录token - 参考Java项目的token管理
        """
        try:
            token_data = {
                'token': token,
                'login_time': time.time(),
                'user_id': self.user.id,
                'username': self.user.username,
                'login_method': login_method,
                'platform': self.platform,
                'expires_at': time.time() + (7 * 24 * 60 * 60),  # 7天后过期
                'is_valid': True
            }
            
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            
            # 同时保存到Redis缓存
            cache_key = f"token:{self.platform}:{self.user.id}"
            cache.set(cache_key, token_data, 60 * 60 * 24 * 7)  # 7天
            
            logger.info(f"Token已保存: {self.platform} (用户: {self.user.username})")
            return True
            
        except Exception as e:
            logger.error(f"保存Token失败 (用户: {self.user.username}, 平台: {self.platform}): {e}")
            return False
    
    def load_token(self) -> Optional[Dict[str, Any]]:
        """
        加载登录token
        """
        try:
            # 先从Redis缓存尝试
            cache_key = f"token:{self.platform}:{self.user.id}"
            cached_data = cache.get(cache_key)
            
            if cached_data and cached_data.get('is_valid'):
                logger.info(f"从缓存加载Token: {self.platform} (用户: {self.user.username})")
                return cached_data
            
            # 从文件加载
            if not os.path.exists(self.token_file):
                # 只在调试模式下记录警告，避免日志污染
                if settings.DEBUG:
                    logger.debug(f"Token文件不存在: {self.token_file}")
                return None
            
            with open(self.token_file, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            # 检查是否过期
            expires_at = token_data.get('expires_at', 0)
            if time.time() > expires_at:
                logger.warning(f"Token已过期: {self.platform} (用户: {self.user.username})")
                token_data['is_valid'] = False
                return None
            
            # 更新缓存
            cache.set(cache_key, token_data, 60 * 60 * 24 * 7)
            
            logger.info(f"已从文件加载Token: {self.platform} (用户: {self.user.username})")
            return token_data
            
        except Exception as e:
            logger.error(f"加载Token失败 (用户: {self.user.username}, 平台: {self.platform}): {e}")
            return None
    
    def is_cookie_valid(self) -> bool:
        """
        检查cookie是否有效 - 参考Java项目的isCookieValid方法
        """
        try:
            cookies = self.load_cookies()
            return len(cookies) > 0
        except Exception:
            return False
    
    def is_token_valid(self) -> bool:
        """
        检查token是否有效
        """
        try:
            token_data = self.load_token()
            return token_data is not None and token_data.get('is_valid', False)
        except Exception:
            return False
    
    def clear_cookies(self) -> bool:
        """
        清除cookies
        """
        try:
            # 删除文件
            if os.path.exists(self.cookie_file):
                os.remove(self.cookie_file)
            
            # 清除缓存
            cache_key = f"cookies:{self.platform}:{self.user.id}"
            cache.delete(cache_key)
            
            logger.info(f"Cookies已清除: {self.platform} (用户: {self.user.username})")
            return True
            
        except Exception as e:
            logger.error(f"清除Cookies失败 (用户: {self.user.username}, 平台: {self.platform}): {e}")
            return False
    
    def clear_token(self) -> bool:
        """
        清除token
        """
        try:
            # 删除文件
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            
            # 清除缓存
            cache_key = f"token:{self.platform}:{self.user.id}"
            cache.delete(cache_key)
            
            logger.info(f"Token已清除: {self.platform} (用户: {self.user.username})")
            return True
            
        except Exception as e:
            logger.error(f"清除Token失败 (用户: {self.user.username}, 平台: {self.platform}): {e}")
            return False
    
    def get_login_status(self) -> Dict[str, Any]:
        """
        获取登录状态信息
        """
        return {
            'platform': self.platform,
            'user_id': self.user.id,
            'username': self.user.username,
            'has_cookies': self.is_cookie_valid(),
            'has_token': self.is_token_valid(),
            'cookie_file_exists': os.path.exists(self.cookie_file),
            'token_file_exists': os.path.exists(self.token_file),
            'last_check': timezone.now().isoformat()
        }


class BossZhipinCookieManager(CookieManagerService):
    """Boss直聘专用Cookie管理器"""
    
    def __init__(self, user: User):
        super().__init__(user, "boss")
    
    def validate_boss_login(self, cookies: List[Dict[str, Any]]) -> bool:
        """
        验证Boss直聘登录状态 - 参考Java项目的登录检查机制
        """
        try:
            # 检查关键cookie是否存在
            required_cookies = ['__zp_seo_uuid__', 'lastCity', 'JSESSIONID']
            
            cookie_names = [cookie.get('name', '') for cookie in cookies]
            
            for required_cookie in required_cookies:
                if required_cookie not in cookie_names:
                    logger.warning(f"缺少关键Cookie: {required_cookie}")
                    return False
            
            logger.info(f"Boss直聘登录状态验证通过 (用户: {self.user.username})")
            return True
            
        except Exception as e:
            logger.error(f"Boss直聘登录状态验证失败: {e}")
            return False
    
    def save_boss_cookies(self, cookies: List[Dict[str, Any]]) -> bool:
        """
        保存Boss直聘cookies并验证
        """
        if self.validate_boss_login(cookies):
            return self.save_cookies(cookies)
        else:
            logger.warning(f"Boss直聘cookies验证失败，未保存 (用户: {self.user.username})")
            return False


def get_cookie_manager(user: User, platform: str = "boss") -> CookieManagerService:
    """
    获取Cookie管理器实例
    """
    if platform == "boss":
        return BossZhipinCookieManager(user)
    else:
        return CookieManagerService(user, platform)
