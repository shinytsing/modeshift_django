"""
Playwright服务类 - 参考Java项目get_jobs的PlaywrightUtil实现
提供完整的浏览器自动化、cookie管理和跨标签页同步功能
"""

import json
import os
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright.sync_api import sync_playwright, Browser as SyncBrowser, BrowserContext as SyncBrowserContext, Page as SyncPage
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)


class PlaywrightService:
    """Playwright服务类 - 参考Java项目的PlaywrightUtil"""
    
    def __init__(self, user: User, platform: str = "boss"):
        self.user = user
        self.platform = platform
        self.cookie_dir = os.path.join(settings.BASE_DIR, 'get_jobs_integration', 'cookies')
        self.cookie_file = os.path.join(self.cookie_dir, f'{platform}_cookies_{user.id}.json')
        self.token_file = os.path.join(self.cookie_dir, f'{platform}_token_{user.id}.json')
        
        # 确保目录存在
        os.makedirs(self.cookie_dir, exist_ok=True)
        
        # 浏览器实例
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 设备类型
        self.device_type = "desktop"
        
        # 平台特定配置
        self.platform_configs = {
            "boss": {
                "domain": ".zhipin.com",
                "home_url": "https://www.zhipin.com",
                "login_url": "https://www.zhipin.com/web/user/?ka=header-login",
                "required_cookies": ["__zp_seo_uuid__", "lastCity", "JSESSIONID"]
            },
            "lagou": {
                "domain": ".lagou.com",
                "home_url": "https://www.lagou.com",
                "login_url": "https://passport.lagou.com/login/login.html",
                "required_cookies": ["user_trace_token", "LGUID", "JSESSIONID"]
            },
            "liepin": {
                "domain": ".liepin.com",
                "home_url": "https://www.liepin.com",
                "login_url": "https://passport.liepin.com/c/login.html",
                "required_cookies": ["lpvt", "lpuid", "JSESSIONID"]
            }
        }
    
    def get_platform_config(self) -> Dict[str, str]:
        """获取平台配置"""
        return self.platform_configs.get(self.platform, self.platform_configs["boss"])
    
    def init_browser(self, headless: bool = False, device_type: str = "desktop") -> bool:
        """
        初始化浏览器 - 参考Java项目的init方法
        """
        try:
            logger.info(f"初始化Playwright浏览器 (用户: {self.user.username}, 平台: {self.platform})")
            
            self.playwright = sync_playwright().start()
            
            # 浏览器启动参数 - 参考Java项目的反检测配置
            browser_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--disable-plugins',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-popup-blocking',
                '--disable-translate',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ]
            
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=browser_args
            )
            
            # 创建上下文
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 创建页面
            self.page = self.context.new_page()
            
            # 设置HTTP头 - 参考Java项目的反检测机制
            self.context.set_extra_http_headers({
                'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'accept-language': 'zh-CN,zh;q=0.9',
                'referer': self.get_platform_config()['home_url'],
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin'
            })
            
            # 注入反检测脚本 - 参考Java项目的initStealth方法
            self.init_stealth()
            
            self.device_type = device_type
            
            logger.info(f"浏览器初始化成功 (用户: {self.user.username})")
            return True
            
        except Exception as e:
            logger.error(f"浏览器初始化失败 (用户: {self.user.username}): {e}")
            return False
    
    def init_stealth(self):
        """
        初始化反检测机制 - 参考Java项目的initStealth方法
        """
        try:
            stealth_script = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
            Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});
            """
            
            self.page.add_init_script(stealth_script)
            logger.info("反检测脚本注入成功")
            
        except Exception as e:
            logger.error(f"反检测脚本注入失败: {e}")
    
    def save_cookies(self) -> bool:
        """
        保存cookies - 参考Java项目的saveCookies方法
        """
        try:
            if not self.context:
                logger.error("浏览器上下文未初始化")
                return False
            
            # 获取所有cookies
            cookies = self.context.cookies()
            
            cookie_data = {
                'cookies': cookies,
                'device_type': self.device_type,
                'user_id': self.user.id,
                'username': self.user.username,
                'save_time': time.time(),
                'expires_at': time.time() + (7 * 24 * 60 * 60),  # 7天后过期
                'platform': self.platform
            }
            
            # 保存到文件
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, ensure_ascii=False, indent=2)
            
            # 保存到Redis缓存
            cache_key = f"cookies:{self.platform}:{self.user.id}"
            cache.set(cache_key, cookie_data, 60 * 60 * 24 * 7)  # 7天
            
            logger.info(f"Cookies已保存到文件: {self.cookie_file} (用户: {self.user.username}, 数量: {len(cookies)})")
            return True
            
        except Exception as e:
            logger.error(f"保存Cookies失败 (用户: {self.user.username}): {e}")
            return False
    
    def load_cookies(self) -> bool:
        """
        加载cookies - 参考Java项目的loadCookies方法
        """
        try:
            # 先从Redis缓存尝试
            cache_key = f"cookies:{self.platform}:{self.user.id}"
            cached_data = cache.get(cache_key)
            
            if cached_data and cached_data.get('cookies'):
                cookies = cached_data['cookies']
                logger.info(f"从缓存加载Cookies: {self.platform} (用户: {self.user.username})")
            else:
                # 从文件加载
                if not os.path.exists(self.cookie_file):
                    logger.debug(f"Cookie文件不存在: {self.cookie_file}")
                    return False
                
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    cookie_data = json.load(f)
                
                cookies = cookie_data.get('cookies', [])
                
                # 检查是否过期
                expires_at = cookie_data.get('expires_at', 0)
                if time.time() > expires_at:
                    logger.warning(f"Cookies已过期: {self.platform} (用户: {self.user.username})")
                    return False
                
                # 更新缓存
                cache.set(cache_key, cookie_data, 60 * 60 * 24 * 7)
            
            if not cookies:
                logger.warning(f"没有可用的Cookies: {self.platform} (用户: {self.user.username})")
                return False
            
            # 添加到浏览器上下文
            if self.context:
                self.context.add_cookies(cookies)
                logger.info(f"已从文件加载Cookies: {self.platform} (用户: {self.user.username}, 数量: {len(cookies)})")
                return True
            else:
                logger.error("浏览器上下文未初始化")
                return False
            
        except Exception as e:
            logger.error(f"加载Cookies失败 (用户: {self.user.username}): {e}")
            return False
    
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
            
            # 保存到文件
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, ensure_ascii=False, indent=2)
            
            # 保存到Redis缓存
            cache_key = f"token:{self.platform}:{self.user.id}"
            cache.set(cache_key, token_data, 60 * 60 * 24 * 7)  # 7天
            
            # 保存到跨标签页同步
            self.sync_token_to_cross_tab(token)
            
            logger.info(f"Token已保存: {self.platform} (用户: {self.user.username})")
            return True
            
        except Exception as e:
            logger.error(f"保存Token失败 (用户: {self.user.username}): {e}")
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
            logger.error(f"加载Token失败 (用户: {self.user.username}): {e}")
            return None
    
    def sync_token_to_cross_tab(self, token: str):
        """
        同步token到跨标签页 - 解决跨标签页token同步问题
        """
        try:
            # 保存到localStorage的跨标签页同步
            cross_tab_data = {
                'tokens': {
                    self.platform: {
                        'token': token,
                        'login_time': time.time(),
                        'user_id': self.user.id,
                        'platform': self.platform
                    }
                },
                'last_sync': time.time()
            }
            
            # 保存到Redis用于跨标签页同步
            sync_key = f"cross_tab_tokens:{self.user.id}"
            cache.set(sync_key, cross_tab_data, 60 * 60 * 24 * 7)  # 7天
            
            logger.info(f"Token已同步到跨标签页: {self.platform} (用户: {self.user.username})")
            
        except Exception as e:
            logger.error(f"同步Token到跨标签页失败: {e}")
    
    def is_cookie_valid(self) -> bool:
        """
        检查cookie是否有效 - 参考Java项目的isCookieValid方法
        """
        try:
            if not os.path.exists(self.cookie_file):
                return False
            
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            # 检查是否过期
            expires_at = cookie_data.get('expires_at', 0)
            if time.time() > expires_at:
                return False
            
            # 检查关键cookie是否存在
            cookies = cookie_data.get('cookies', [])
            platform_config = self.get_platform_config()
            required_cookies = platform_config.get('required_cookies', [])
            
            cookie_names = [cookie.get('name', '') for cookie in cookies]
            
            for required_cookie in required_cookies:
                if required_cookie not in cookie_names:
                    return False
            
            return True
            
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
    
    def login_with_token(self, token: str) -> bool:
        """
        使用token登录 - 参考Java项目的登录流程
        """
        try:
            logger.info(f"开始使用Token登录: {self.platform} (用户: {self.user.username})")
            
            # 保存token
            if not self.save_token(token):
                return False
            
            # 初始化浏览器
            if not self.init_browser(headless=False):
                return False
            
            # 加载cookies
            self.load_cookies()
            
            # 访问平台首页
            platform_config = self.get_platform_config()
            self.page.goto(platform_config['home_url'], wait_until='domcontentloaded')
            
            # 等待页面加载
            time.sleep(2)
            
            # 检查登录状态
            if self.check_login_status():
                logger.info(f"Token登录成功: {self.platform} (用户: {self.user.username})")
                return True
            else:
                logger.warning(f"Token登录失败，可能需要重新登录: {self.platform} (用户: {self.user.username})")
                return False
            
        except Exception as e:
            logger.error(f"Token登录失败: {e}")
            return False
    
    def check_login_status(self) -> bool:
        """
        检查登录状态 - 参考Java项目的isLoginRequired方法
        """
        try:
            if not self.page:
                return False
            
            # 检查是否出现登录按钮
            login_selectors = [
                'text="登录"',
                'text="立即登录"',
                '[class*="login"]',
                '[id*="login"]'
            ]
            
            for selector in login_selectors:
                try:
                    element = self.page.locator(selector)
                    if element.count() > 0 and element.is_visible():
                        logger.info(f"检测到登录按钮: {selector}")
                        return False
                except Exception:
                    continue
            
            # 检查是否出现用户相关元素
            user_selectors = [
                '[class*="user"]',
                '[class*="profile"]',
                '[class*="avatar"]',
                'text="我的"'
            ]
            
            for selector in user_selectors:
                try:
                    element = self.page.locator(selector)
                    if element.count() > 0 and element.is_visible():
                        logger.info(f"检测到用户元素: {selector}")
                        return True
                except Exception:
                    continue
            
            logger.info("登录状态检查完成，默认认为已登录")
            return True
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def scan_login(self) -> bool:
        """
        扫码登录 - 参考Java项目的scanLogin方法
        """
        try:
            logger.info(f"开始扫码登录: {self.platform} (用户: {self.user.username})")
            
            platform_config = self.get_platform_config()
            
            # 访问登录页面
            self.page.goto(platform_config['login_url'], wait_until='domcontentloaded')
            time.sleep(2)
            
            # 切换到二维码登录
            try:
                scan_button = self.page.locator('text="扫码登录"')
                if scan_button.count() > 0:
                    scan_button.click()
                    time.sleep(1)
            except Exception:
                pass
            
            logger.info("等待扫码登录...")
            
            # 等待登录完成（最多10分钟）
            start_time = time.time()
            timeout = 10 * 60  # 10分钟
            
            while time.time() - start_time < timeout:
                try:
                    # 检查是否登录成功
                    if self.check_login_status():
                        logger.info("扫码登录成功！")
                        # 保存cookies
                        self.save_cookies()
                        return True
                    
                    time.sleep(2)  # 每2秒检查一次
                    
                except Exception as e:
                    logger.error(f"检查登录状态时异常: {e}")
                    time.sleep(2)
            
            logger.error("扫码登录超时")
            return False
            
        except Exception as e:
            logger.error(f"扫码登录失败: {e}")
            return False
    
    def auto_login(self) -> bool:
        """
        自动登录 - 参考Java项目的login方法
        """
        try:
            logger.info(f"开始自动登录: {self.platform} (用户: {self.user.username})")
            
            # 初始化浏览器
            if not self.init_browser(headless=False):
                return False
            
            # 检查cookie是否有效
            if self.is_cookie_valid():
                logger.info("Cookie有效，尝试加载cookies")
                if self.load_cookies():
                    self.page.goto(self.get_platform_config()['home_url'], wait_until='domcontentloaded')
                    time.sleep(2)
                    
                    if self.check_login_status():
                        logger.info("Cookie登录成功")
                        return True
            
            # 检查token是否有效
            token_data = self.load_token()
            if token_data and token_data.get('is_valid'):
                logger.info("Token有效，尝试token登录")
                if self.login_with_token(token_data['token']):
                    return True
            
            # 需要重新登录
            logger.info("需要重新登录，开始扫码登录")
            return self.scan_login()
            
        except Exception as e:
            logger.error(f"自动登录失败: {e}")
            return False
    
    def close_browser(self):
        """
        关闭浏览器
        """
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            logger.info(f"浏览器已关闭 (用户: {self.user.username})")
            
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
    
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


def get_playwright_service(user: User, platform: str = "boss") -> PlaywrightService:
    """
    获取Playwright服务实例
    """
    return PlaywrightService(user, platform)
