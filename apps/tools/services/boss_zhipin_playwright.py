"""
Boss直聘Playwright服务 - 替代Selenium
基于Playwright实现更稳定的Boss直聘登录状态检测
集成反检测技术绕过安全验证
"""
import logging
import time
import random
from typing import Dict, Optional, Any, List

from django.core.cache import cache
from playwright.sync_api import sync_playwright, Browser, Page
from .anti_detection_service import AntiDetectionService
from .security_bypass_service import SecurityBypassService
from .simple_security_bypass import SimpleSecurityBypassService
from .cookie_manager import cookie_manager
from .proxy_pool_service import proxy_pool

logger = logging.getLogger(__name__)


class BossZhipinPlaywrightService:
    """Boss直聘Playwright服务 - 替代Selenium"""

    def __init__(self, headless=True, proxy=None, anti_detection=True):
        self.headless = headless
        self.proxy = proxy
        self.anti_detection = anti_detection
        self.base_url = "https://www.zhipin.com"
        self.browser = None
        self.page = None
        self.playwright = None
        
        # 初始化反检测服务
        self.anti_detection_service = AntiDetectionService() if anti_detection else None
        # 初始化安全验证绕过服务
        self.security_bypass_service = SecurityBypassService()
        # 初始化简单安全验证绕过服务
        self.simple_bypass_service = SimpleSecurityBypassService()

    def _connect_to_existing_browser(self) -> bool:
        """尝试连接到现有的Chrome浏览器实例"""
        try:
            import subprocess
            import json
            
            logger.info("🔍 尝试连接到现有的Chrome浏览器实例...")
            
            # 查找Chrome进程
            try:
                # macOS/Linux
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                chrome_processes = [line for line in result.stdout.split('\n') if 'chrome' in line.lower() and '--remote-debugging-port' in line]
                
                if chrome_processes:
                    logger.info(f"✅ 找到Chrome进程: {len(chrome_processes)}个")
                    
                    # 尝试连接到调试端口
                    for port in [9222, 9223, 9224, 9225]:
                        try:
                            logger.info(f"🔌 尝试连接到端口 {port}...")
                            
                            # 启动Playwright
                            self.playwright = sync_playwright().start()
                            
                            # 连接到现有浏览器
                            self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
                            
                            # 获取现有页面
                            contexts = self.browser.contexts
                            if contexts:
                                context = contexts[0]
                                pages = context.pages
                                if pages:
                                    self.page = pages[0]
                                    logger.info("✅ 成功连接到现有Chrome浏览器实例")
                                    return True
                                    
                        except Exception as e:
                            logger.debug(f"⚠️ 端口 {port} 连接失败: {str(e)}")
                            continue
                            
            except Exception as e:
                logger.debug(f"⚠️ 查找Chrome进程失败: {str(e)}")
            
            logger.info("❌ 无法连接到现有浏览器实例")
            return False
            
        except Exception as e:
            logger.error(f"❌ 连接现有浏览器失败: {str(e)}")
            return False

    def _init_browser(self) -> bool:
        """初始化Playwright浏览器 - 使用代理池绕过IP封禁"""
        try:
            import random
            import asyncio
            
            # 检查是否在asyncio循环中
            try:
                loop = asyncio.get_running_loop()
                logger.warning("⚠️ 检测到asyncio循环，使用线程隔离方式启动Playwright")
                # 使用线程隔离的方式启动Playwright，避免asyncio冲突
                import threading
                import queue
                
                result_queue = queue.Queue()
                
                def run_playwright_in_thread():
                    try:
                        playwright = sync_playwright().start()
                        result_queue.put(('success', playwright))
                    except Exception as e:
                        result_queue.put(('error', str(e)))
                
                # 在新线程中启动Playwright
                thread = threading.Thread(target=run_playwright_in_thread)
                thread.start()
                thread.join(timeout=30)  # 30秒超时
                
                if thread.is_alive():
                    logger.error("❌ Playwright启动超时")
                    return False
                
                result_type, result_value = result_queue.get_nowait()
                if result_type == 'success':
                    self.playwright = result_value
                    logger.info("✅ 在线程中成功启动Playwright")
                else:
                    logger.error(f"❌ 在线程中启动Playwright失败: {result_value}")
                    return False
                    
            except RuntimeError:
                # 没有运行中的循环，可以安全使用sync API
                logger.info("✅ 没有asyncio循环，可以安全使用sync API")
                self.playwright = sync_playwright().start()
            except Exception as e:
                logger.error(f"❌ Playwright启动异常: {str(e)}")
                return False
            
            # 使用代理池获取代理，添加连接测试
            selected_proxy = proxy_pool.get_random_proxy()
            proxy_config = None
            
            if selected_proxy and selected_proxy['server']:
                # 测试代理连接
                try:
                    import requests
                    test_response = requests.get('http://httpbin.org/ip', 
                                               proxies={'http': selected_proxy['server'], 'https': selected_proxy['server']}, 
                                               timeout=5)
                    if test_response.status_code == 200:
                        logger.info(f"🌐 代理连接测试成功，使用代理: {selected_proxy['server']}")
                        proxy_config = {'server': selected_proxy['server']}
                    else:
                        logger.warning(f"⚠️ 代理连接测试失败，状态码: {test_response.status_code}")
                        proxy_config = None
                except Exception as e:
                    logger.warning(f"⚠️ 代理连接测试失败: {str(e)}，使用直连")
                    proxy_config = None
            
            if proxy_config is None:
                logger.info("🌐 使用直连")
            
            # 反检测浏览器参数 - 增强版
            browser_args = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-javascript',
                '--no-first-run',
                '--no-default-browser-check',
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
                # 添加更多反检测参数
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-domain-reliability',
                '--disable-component-extensions-with-background-pages',
                '--disable-background-networking',
                '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                '--disable-features=VizDisplayCompositor',
                '--run-all-compositor-stages-before-draw',
                '--disable-threaded-animation',
                '--disable-threaded-scrolling',
                '--disable-checker-imaging',
                '--disable-new-content-rendering-timeout',
                '--disable-image-animation-resync',
                '--disable-partial-raster',
                '--disable-skia-runtime-opts',
                '--disable-system-font-check',
                '--disable-font-subpixel-positioning',
                '--disable-lcd-text',
                '--disable-gpu-rasterization',
                '--disable-gpu-compositing',
                '--disable-gpu-sandbox',
                '--disable-software-rasterizer',
                '--disable-gpu-memory-buffer-video-frames',
                '--disable-gpu-memory-buffer-compositor-resources',
                '--disable-gpu-memory-buffer-video-frames',
                '--disable-gpu-process-crash-limit',
                '--disable-gpu-watchdog',
                '--disable-gpu-driver-bug-workarounds',
                '--disable-gpu-rasterization',
                '--disable-gpu-sandbox',
                '--disable-gpu-compositing',
                '--disable-gpu-memory-buffer-video-frames',
                '--disable-gpu-memory-buffer-compositor-resources',
                '--disable-gpu-memory-buffer-video-frames',
                '--disable-gpu-process-crash-limit',
                '--disable-gpu-watchdog',
                '--disable-gpu-driver-bug-workarounds',
                # 随机化User-Agent
                f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 120)}.0.0.0 Safari/537.36'
            ]
            
            # 启动浏览器
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=browser_args,
                proxy=proxy_config
            )
            
            # 创建页面
            self.page = self.browser.new_page()
            
            # 反检测设置
            if self.anti_detection_service:
                self.anti_detection_service.setup_browser_anti_detection(self.page)
            
            # 设置视口大小
            self.page.set_viewport_size({"width": 1200, "height": 800})
            
            logger.info("Playwright浏览器初始化成功")
            return True

        except Exception as e:
            logger.error(f"Playwright浏览器初始化失败: {str(e)}")
            return False

    def _close_browser(self):
        """关闭Playwright浏览器"""
        try:
            if self.page:
                try:
                    self.page.close()
                except Exception as e:
                    logger.warning(f"关闭页面失败: {e}")
                self.page = None
                
            if self.browser:
                try:
                    self.browser.close()
                except Exception as e:
                    logger.warning(f"关闭浏览器失败: {e}")
                self.browser = None
                
            if self.playwright:
                try:
                    self.playwright.stop()
                except Exception as e:
                    logger.warning(f"停止Playwright失败: {e}")
                self.playwright = None
                
            logger.info("Playwright浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭Playwright浏览器失败: {str(e)}")
    
    def _check_existing_browser_session(self) -> Dict:
        """检测现有浏览器session中的登录状态"""
        try:
            # 方法1: 尝试连接到现有的Chrome浏览器实例
            playwright = sync_playwright().start()
            
            # 连接到现有的Chrome浏览器（如果存在）
            try:
                # 尝试连接到默认的Chrome用户数据目录
                browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
                context = browser.contexts[0] if browser.contexts else None
                
                if not context:
                    logger.info("未找到现有的浏览器上下文")
                    return {"success": False, "is_logged_in": False, "message": "未找到现有浏览器session"}
                
                # 获取所有页面
                pages = context.pages
                if not pages:
                    logger.info("未找到现有的浏览器页面")
                    return {"success": False, "is_logged_in": False, "message": "未找到现有浏览器页面"}
                
                # 检查每个页面是否包含Boss直聘相关内容
                for page in pages:
                    try:
                        current_url = page.url
                        logger.info(f"检查页面: {current_url}")
                        
                        # 检查是否是Boss直聘相关页面
                        if any(domain in current_url for domain in ['zhipin.com', 'boss.com']):
                            logger.info(f"找到Boss直聘相关页面: {current_url}")
                            
                            # 尝试提取token
                            token_info = self._extract_token_from_page(page)
                            
                            # 检查登录状态
                            is_logged_in = self._check_page_login_status(page)
                            
                            if is_logged_in and token_info.get('token'):
                                logger.info("✅ 在现有浏览器session中检测到登录状态和token")
                                
                                # 使用检测到的token进行验证
                                token_validation = self._validate_token_with_playwright(token_info['token'])
                                
                                if token_validation.get('success'):
                                    logger.info("✅ Token验证成功，可以开始投递任务")
                                    return {
                                        "success": True,
                                        "is_logged_in": True,
                                        "found_indicator": "existing_session",
                                        "login_confidence": 95,
                                        "current_url": current_url,
                                        "message": "在现有浏览器session中检测到有效登录状态",
                                        "token_info": token_info,
                                        "token_validation": token_validation
                                    }
                                else:
                                    logger.warning("Token验证失败，继续检查其他页面")
                                    continue
                    except Exception as e:
                        logger.warning(f"检查页面时出错: {str(e)}")
                        continue
                
                browser.close()
                playwright.stop()
                
                return {"success": False, "is_logged_in": False, "message": "现有浏览器session中未检测到Boss直聘登录状态"}
                
            except Exception as e:
                logger.info(f"无法连接到现有浏览器: {str(e)}")
                playwright.stop()
                
                # 方法2: 检查浏览器进程和cookie文件
                return self._check_browser_process_and_cookies()
                
        except Exception as e:
            logger.error(f"检测现有浏览器session失败: {str(e)}")
            return {"success": False, "is_logged_in": False, "message": f"检测现有session失败: {str(e)}"}
    
    def _check_browser_tabs_via_cookies(self) -> Dict:
        """通过检查浏览器cookie文件来检测其他标签页的登录状态 - 参考get_jobs项目实现"""
        try:
            import os
            import sqlite3
            import tempfile
            import shutil
            import json
            import time
            from datetime import datetime
            
            logger.info("🔍 通过cookie文件检测其他标签页的登录状态...")
            
            # Chrome cookie文件路径 - 支持更多路径
            cookie_paths = [
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 1/Cookies"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 2/Cookies"),
                os.path.expanduser("~/.config/google-chrome/Default/Cookies"),
                os.path.expanduser("~/.config/google-chrome/Profile 1/Cookies"),
                os.path.expanduser("~/.config/google-chrome/Profile 2/Cookies"),
                # Windows路径
                os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default/Cookies"),
                os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Profile 1/Cookies"),
            ]
            
            for cookie_path in cookie_paths:
                if not os.path.exists(cookie_path):
                    continue
                    
                logger.info(f"检查cookie文件: {cookie_path}")
                
                try:
                    # 复制cookie文件到临时位置
                    temp_cookie_path = tempfile.mktemp()
                    shutil.copy2(cookie_path, temp_cookie_path)
                    
                    # 连接SQLite数据库
                    conn = sqlite3.connect(temp_cookie_path)
                    cursor = conn.cursor()
                    
                    # 查询Boss直聘相关的cookies - 修复查询条件
                    cursor.execute("""
                        SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, creation_utc
                        FROM cookies 
                        WHERE (host_key LIKE '%zhipin.com%' OR host_key LIKE '%boss.com%' OR host_key LIKE '%.zhipin.com%')
                        AND name IN ('wt2', 'zp_at', '__zp_stoken__', 'bst', 'wbg')
                        ORDER BY creation_utc DESC
                    """)
                    
                    cookies = cursor.fetchall()
                    conn.close()
                    
                    # 清理临时文件
                    os.unlink(temp_cookie_path)
                    
                    if not cookies:
                        continue
                    
                    logger.info(f"找到 {len(cookies)} 个Boss直聘相关cookies")
                    
                    # 查找token相关的cookies
                    token_cookies = {}
                    for cookie in cookies:
                        name, value, domain, path, expires_utc, is_secure, is_httponly, creation_utc = cookie
                        
                        # 检查cookie是否过期
                        if expires_utc > 0:
                            current_time = datetime.now().timestamp() * 1000000  # 转换为微秒
                            if current_time > expires_utc:
                                logger.debug(f"Cookie {name} 已过期")
                                continue
                        
                        # 专门匹配Boss直聘的token cookies
                        if name in ['wt2', 'zp_at', '__zp_stoken__', 'bst', 'wbg']:
                            token_cookies[name] = {
                                'value': value,
                                'domain': domain,
                                'path': path,
                                'expires': expires_utc,
                                'is_secure': bool(is_secure),
                                'is_httponly': bool(is_httponly),
                                'creation_time': creation_utc
                            }
                            logger.info(f"找到token cookie: {name} = {value[:30]}...")
                    
                    if token_cookies:
                        # 使用找到的token进行验证
                        for token_name, token_data in token_cookies.items():
                            token_value = token_data['value']
                            if len(token_value) > 10:  # 降低长度要求
                                logger.info(f"尝试使用 {token_name} token进行验证...")
                                
                                # 使用token直接访问Boss直聘页面验证
                                validation_result = self._validate_token_direct_access(token_value)
                                if validation_result.get('success'):
                                    logger.info(f"✅ 使用 {token_name} token验证成功")
                                    return {
                                        "success": True,
                                        "is_logged_in": True,
                                        "found_indicator": "cookie_file",
                                        "login_confidence": 90,
                                        "current_url": "cookie_extracted",
                                        "message": f"从cookie文件中检测到有效登录状态 ({token_name})",
                                        "token_info": {
                                            "token": token_value,
                                            "source": "cookie_file",
                                            "cookie_name": token_name,
                                            "all_cookies": token_cookies
                                        },
                                        "token_validation": validation_result
                                    }
                    
                except Exception as e:
                    logger.warning(f"处理cookie文件 {cookie_path} 失败: {str(e)}")
                    continue
            
            return {"success": False, "is_logged_in": False, "message": "未在cookie文件中找到有效的Boss直聘token"}
            
        except Exception as e:
            logger.error(f"检查cookie文件失败: {str(e)}")
            return {"success": False, "is_logged_in": False, "message": f"检查cookie文件失败: {str(e)}"}
    
    def _validate_token_direct_access(self, token: str) -> Dict:
        """直接使用token访问Boss直聘页面验证 - 参考get_jobs项目实现"""
        try:
            import requests
            
            logger.info(f"🔍 使用token直接访问Boss直聘页面验证: {token[:20]}...")
            
            # 设置请求头 - 使用完整的cookie字符串
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie': f'wt2={token}; zp_at={token}; __zp_stoken__={token}'  # 设置多个token cookies
            }
            
            # 访问Boss直聘页面
            test_urls = [
                "https://www.zhipin.com/web/geek/jobs",
                "https://www.zhipin.com/web/geek/chat",
                "https://www.zhipin.com/web/geek/profile"
            ]
            
            for url in test_urls:
                try:
                    response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        
                        # 检查是否包含登录后的特征
                        login_indicators = [
                            '立即沟通', '投递简历', '我的简历', '我的投递',
                            '个人中心', '退出', 'logout', 'user-info',
                            'geek-info', 'profile', '简历管理', '我的投递记录',
                            '沟通记录', '面试邀请', '职位推荐', '求职者',
                            '工作台', '消息中心', '设置', '我的'
                        ]
                        
                        found_indicators = [indicator for indicator in login_indicators if indicator in content]
                        
                        if found_indicators:
                            logger.info(f"✅ Token验证成功，找到登录指标: {found_indicators}")
                            return {
                                "success": True,
                                "is_logged_in": True,
                                "found_indicators": found_indicators,
                                "test_url": url,
                                "message": "Token验证成功，用户已登录"
                            }
                        
                        # 检查是否被重定向到登录页面
                        if 'login' in response.url.lower() or 'signin' in response.url.lower():
                            logger.info(f"Token无效，被重定向到登录页面: {response.url}")
                            continue
                        
                        # 如果页面正常加载且不包含登录表单，可能已登录
                        if 'zhipin.com' in response.url and len(response.text) > 10000:
                            logger.info("Token可能有效，页面正常加载")
                            return {
                                "success": True,
                                "is_logged_in": True,
                                "test_url": url,
                                "message": "Token可能有效，页面正常加载"
                            }
                            
                except Exception as e:
                    logger.warning(f"访问 {url} 失败: {str(e)}")
                    continue
            
            return {"success": False, "is_logged_in": False, "message": "Token验证失败"}
            
        except Exception as e:
            logger.error(f"Token验证失败: {str(e)}")
            return {"success": False, "is_logged_in": False, "message": f"Token验证失败: {str(e)}"}
    
    def _check_browser_cookies_directly(self) -> Dict:
        """直接检查浏览器cookie文件中的Boss直聘token"""
        try:
            import os
            import sqlite3
            import json
            import base64
            from datetime import datetime
            
            # Chrome cookie文件路径
            cookie_paths = [
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 1/Cookies"),
                os.path.expanduser("~/.config/google-chrome/Default/Cookies"),
                os.path.expanduser("~/.config/google-chrome/Profile 1/Cookies")
            ]
            
            for cookie_path in cookie_paths:
                if not os.path.exists(cookie_path):
                    continue
                    
                logger.info(f"检查cookie文件: {cookie_path}")
                
                try:
                    # 复制cookie文件到临时位置（因为Chrome可能正在使用）
                    import tempfile
                    import shutil
                    
                    temp_cookie_path = tempfile.mktemp()
                    shutil.copy2(cookie_path, temp_cookie_path)
                    
                    # 连接SQLite数据库
                    conn = sqlite3.connect(temp_cookie_path)
                    cursor = conn.cursor()
                    
                    # 首先检查表结构
                    cursor.execute("PRAGMA table_info(cookies)")
                    columns = [column[1] for column in cursor.fetchall()]
                    logger.info(f"Cookie表结构: {columns}")
                    
                    # 查询Boss直聘相关的cookies
                    cursor.execute("""
                        SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly
                        FROM cookies 
                        WHERE host_key LIKE '%zhipin.com%' OR host_key LIKE '%boss.com%'
                        ORDER BY creation_utc DESC
                    """)
                    
                    cookies = cursor.fetchall()
                    conn.close()
                    
                    # 清理临时文件
                    os.unlink(temp_cookie_path)
                    
                    if not cookies:
                        continue
                    
                    logger.info(f"找到 {len(cookies)} 个Boss直聘相关cookies")
                    
                    # 查找token相关的cookies
                    token_cookies = {}
                    for cookie in cookies:
                        name, value, domain, path, expires_utc, is_secure, is_httponly = cookie
                        
                        if name in ['wt2', 'zp_at', 'zp_token', 'boss_token', 'token']:
                            token_cookies[name] = {
                                'value': value,
                                'domain': domain,
                                'path': path,
                                'expires': expires_utc,
                                'is_secure': bool(is_secure),
                                'is_httponly': bool(is_httponly)
                            }
                            logger.info(f"找到token cookie: {name} = {value[:20]}...")
                    
                    if token_cookies:
                        # 使用找到的token进行验证
                        for token_name, token_data in token_cookies.items():
                            token_value = token_data['value']
                            if len(token_value) > 10:  # 确保是有效的token
                                logger.info(f"尝试使用 {token_name} token进行验证...")
                                
                                validation_result = self._validate_token_with_playwright(token_value)
                                if validation_result.get('success'):
                                    logger.info(f"✅ 使用 {token_name} token验证成功")
                                    return {
                                        "success": True,
                                        "is_logged_in": True,
                                        "found_indicator": "cookie_file",
                                        "login_confidence": 90,
                                        "current_url": "cookie_extracted",
                                        "message": f"从cookie文件中检测到有效登录状态 ({token_name})",
                                        "token_info": {
                                            "token": token_value,
                                            "source": "cookie_file",
                                            "cookie_name": token_name,
                                            "all_cookies": token_cookies
                                        },
                                        "token_validation": validation_result
                                    }
                    
                except Exception as e:
                    logger.warning(f"处理cookie文件 {cookie_path} 失败: {str(e)}")
                    continue
            
            return {"success": False, "is_logged_in": False, "message": "未在cookie文件中找到有效的Boss直聘token"}
            
        except Exception as e:
            logger.error(f"检查cookie文件失败: {str(e)}")
            return {"success": False, "is_logged_in": False, "message": f"检查cookie文件失败: {str(e)}"}
    
    def _check_browser_process_and_cookies(self) -> Dict:
        """通过检查浏览器进程和cookie文件来检测登录状态"""
        try:
            import subprocess
            import os
            import json
            
            # 检查Chrome进程是否在运行
            try:
                result = subprocess.run(['pgrep', '-f', 'chrome'], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.info("未检测到Chrome浏览器进程")
                    return {"success": False, "is_logged_in": False, "message": "未检测到Chrome浏览器进程"}
                
                logger.info("检测到Chrome浏览器进程正在运行")
            except Exception as e:
                logger.warning(f"检查Chrome进程失败: {str(e)}")
            
            # 方法3: 通过HTTP请求检测登录状态
            return self._check_login_via_http_request()
            
        except Exception as e:
            logger.error(f"检查浏览器进程和cookie失败: {str(e)}")
            return {"success": False, "is_logged_in": False, "message": f"检查浏览器进程失败: {str(e)}"}
    
    def _check_login_via_http_request(self) -> Dict:
        """通过HTTP请求检测Boss直聘登录状态"""
        try:
            import requests
            import time
            
            # 尝试访问Boss直聘的API端点来检测登录状态
            api_urls = [
                "https://www.zhipin.com/web/geek/jobs",
                "https://www.zhipin.com/web/geek/user",
                "https://www.zhipin.com/web/geek/profile"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            for url in api_urls:
                try:
                    logger.info(f"尝试访问: {url}")
                    response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                    
                    logger.info(f"响应状态码: {response.status_code}")
                    logger.info(f"最终URL: {response.url}")
                    logger.info(f"响应内容长度: {len(response.text)}")
                    
                    # 检查是否被重定向到登录页面
                    if 'login' in response.url.lower() or 'signin' in response.url.lower():
                        logger.info("被重定向到登录页面，未登录")
                        continue
                    
                    # 检查响应内容是否包含登录后的特征
                    content = response.text.lower()
                    login_indicators = [
                        '立即沟通', '投递简历', '我的简历', '我的投递',
                        '个人中心', '退出', 'logout', 'user-info',
                        'geek-info', 'profile', '简历管理', '我的投递记录',
                        '沟通记录', '面试邀请', '职位推荐', '求职者',
                        '工作台', '消息中心', '设置', '我的',
                        '简历', '投递', '沟通', '邀请'
                    ]
                    
                    found_indicators = [indicator for indicator in login_indicators if indicator in content]
                    indicator_count = len(found_indicators)
                    
                    logger.info(f"找到的登录指标: {found_indicators}")
                    logger.info(f"匹配的指标数量: {indicator_count}")
                    
                    if indicator_count >= 1:  # 降低阈值，只要有1个指标就认为已登录
                        logger.info(f"✅ 通过HTTP请求检测到登录状态 (匹配{indicator_count}个指标)")
                        
                        # 尝试从HTTP响应中提取token
                        token_info = self._extract_token_from_http_response(response)
                        
                        return {
                            "success": True,
                            "is_logged_in": True,
                            "found_indicator": "http_request",
                            "login_confidence": min(80, 60 + indicator_count * 10),
                            "current_url": response.url,
                            "message": f"通过HTTP请求检测到登录状态 (匹配{indicator_count}个指标)",
                            "token_info": token_info,
                            "found_indicators": found_indicators
                        }
                    
                    # 检查是否包含登录表单
                    login_form_indicators = ['登录', 'login', 'signin', '手机号', '验证码', '密码']
                    form_indicators = [indicator for indicator in login_form_indicators if indicator in content]
                    
                    if form_indicators:
                        logger.info(f"页面包含登录表单指标: {form_indicators}")
                        continue
                    
                    # 如果页面正常加载且不包含登录表单，可能已登录
                    if response.status_code == 200 and 'zhipin.com' in response.url:
                        # 检查页面内容长度，如果太短可能是登录页面
                        if len(response.text) < 10000:  # 登录后的页面通常内容较多
                            logger.info(f"页面内容较短 ({len(response.text)} 字符)，可能是登录页面")
                            continue
                        
                        logger.info("页面正常加载且无登录表单，假设已登录")
                        
                        # 尝试从HTTP响应中提取token
                        token_info = self._extract_token_from_http_response(response)
                        
                        return {
                            "success": True,
                            "is_logged_in": True,
                            "found_indicator": "http_request_success",
                            "login_confidence": 50,
                            "current_url": response.url,
                            "message": "页面正常加载且无登录表单，假设已登录",
                            "token_info": token_info
                        }
                        
                except Exception as e:
                    logger.warning(f"访问 {url} 失败: {str(e)}")
                    continue
            
            return {"success": False, "is_logged_in": False, "message": "通过HTTP请求未检测到登录状态"}
            
        except Exception as e:
            logger.error(f"HTTP请求检测失败: {str(e)}")
            return {"success": False, "is_logged_in": False, "message": f"HTTP请求检测失败: {str(e)}"}
    
    def _extract_token_from_http_response(self, response) -> Dict:
        """从HTTP响应中提取token信息"""
        try:
            token_info = {}
            content = response.text
            
            logger.info("🔍 从HTTP响应中提取token...")
            
            # 从响应头中提取token
            for header_name, header_value in response.headers.items():
                if any(token_key in header_name.lower() for token_key in ['token', 'auth', 'wt2', 'zp_at']):
                    token_info['response_headers'] = {header_name: header_value}
                    if not token_info.get('token') and len(header_value) > 10:
                        token_info['token'] = header_value
                        token_info['source'] = 'response_headers'
                    logger.info(f"✅ 从响应头找到token: {header_name}")
            
            # 从响应内容中提取token
            import re
            token_patterns = [
                r'"wt2":"([^"]+)"',
                r'"zp_at":"([^"]+)"',
                r'"token":"([^"]+)"',
                r'"authToken":"([^"]+)"',
                r'"accessToken":"([^"]+)"',
                r'wt2=([^&\s]+)',
                r'zp_at=([^&\s]+)',
                r'token=([^&\s]+)',
                r'window\.wt2\s*=\s*["\']([^"\']+)["\']',
                r'window\.token\s*=\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in token_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) > 10:
                        token_info['response_content'] = {'pattern': pattern, 'value': match}
                        if not token_info.get('token'):
                            token_info['token'] = match
                            token_info['source'] = 'response_content'
                        logger.info(f"✅ 从响应内容找到token: {pattern}")
                        break
                if token_info.get('token'):
                    break
            
            # 设置基本信息
            if not token_info.get('source'):
                token_info['source'] = 'http_response'
            if not token_info.get('expires_at'):
                token_info['expires_at'] = '未知'
            if not token_info.get('cookie_count'):
                token_info['cookie_count'] = 0
            
            if token_info.get('token'):
                logger.info(f"🎉 从HTTP响应成功提取到token: {token_info['token'][:20]}... (来源: {token_info.get('source', '未知')})")
            else:
                logger.warning("❌ 从HTTP响应未能提取到有效token")
                logger.info(f"HTTP响应token_info: {token_info}")
            
            return token_info
            
        except Exception as e:
            logger.warning(f"从HTTP响应提取token失败: {str(e)}")
            return {}
    
    def _validate_boss_token(self, token_info: Dict) -> Dict:
        """验证Boss直聘token的有效性"""
        try:
            if not token_info or not token_info.get('token'):
                return {"valid": False, "reason": "no_token"}
            
            token = token_info['token']
            source = token_info.get('source', 'unknown')
            
            # 检查token长度
            if len(token) < 10:
                return {"valid": False, "reason": "token_too_short"}
            
            # 检查token格式
            boss_token_patterns = [
                r'^[A-Za-z0-9+/=]+$',  # Base64格式
                r'^[A-Za-z0-9_-]+$',   # 字母数字下划线
                r'^[A-Fa-f0-9]+$',     # 十六进制
            ]
            
            import re
            for pattern in boss_token_patterns:
                if re.match(pattern, token):
                    logger.info(f"✅ Token格式验证通过: {source}")
                    return {"valid": True, "reason": "format_valid"}
            
            # 如果格式不匹配，但长度足够，也认为可能有效
            if len(token) > 20:
                logger.info(f"⚠️ Token格式不匹配但长度足够: {source}")
                return {"valid": True, "reason": "length_sufficient"}
            
            return {"valid": False, "reason": "format_invalid"}
            
        except Exception as e:
            logger.error(f"Token验证失败: {str(e)}")
            return {"valid": False, "reason": "validation_error"}
    
    def _extract_token_from_page(self, page) -> Dict:
        """从指定页面提取token信息 - 增强版"""
        try:
            token_info = {}
            logger.info("🔍 开始从页面提取token...")
            
            # 1. 尝试从localStorage获取token
            try:
                logger.info("🔍 检查localStorage...")
                local_storage = page.evaluate("() => window.localStorage")
                logger.info(f"localStorage内容: {list(local_storage.keys())}")
                
                for key, value in local_storage.items():
                    # 专门查找Boss直聘相关的token - 增强版
                    boss_local_storage_keys = [
                        'wt2', 'zp_at', 'zp_token', 'boss_token', 'zhipin_token', 'geek_token',
                        '__zp_stoken__', '__zp_seo__', '__zp_seo_uuid__', '__zp_stoken__',
                        'zp_seo_uuid', 'zp_seo', 'zp_token', 'zp_at', 'wt2',
                        'bst', 'wbg', 'zp_seo_uuid', 'zp_seo', 'zp_token', 'zp_at', 'wt2',
                        'sessionid', 'session_id', 'auth_token', 'access_token',
                        'user_token', 'login_token', 'auth_cookie', 'user_cookie',
                        '__a', '__c', '__g', '__l', '__zp_stoken__', '__zp_seo__',
                        'userInfo', 'user_info', 'loginInfo', 'login_info',
                        'token', 'auth', 'access', 'jwt', 'session', 'user'
                    ]
                    
                    if any(token_key in key.lower() for token_key in boss_local_storage_keys):
                        token_info['localStorage'] = {key: value}
                        if not token_info.get('token') and len(str(value)) > 5:  # 降低长度要求
                            token_info['token'] = str(value)
                            token_info['source'] = 'localStorage'
                            token_info['localStorage_key'] = key
                        logger.info(f"✅ 从localStorage找到Boss直聘token: {key} = {str(value)[:30]}...")
                    elif any(token_key in key.lower() for token_key in ['token', 'auth', 'access', 'jwt', 'session', 'user']) and 'wljssdk' not in key.lower():
                        # 排除通用SDK token，查找其他可能的token
                        if len(str(value)) > 20 and not str(value).startswith('{"value"'):
                            token_info['localStorage'] = {key: value}
                            if not token_info.get('token'):
                                token_info['token'] = str(value)
                                token_info['source'] = 'localStorage'
                            logger.info(f"✅ 从localStorage找到可能的token: {key} = {str(value)[:30]}...")
            except Exception as e:
                logger.warning(f"获取localStorage失败: {str(e)}")
            
            # 2. 尝试从cookies获取token
            try:
                logger.info("🔍 检查cookies...")
                cookies = page.context.cookies()
                logger.info(f"找到 {len(cookies)} 个cookies")
                
                cookie_count = 0
                boss_cookies = {}
                
                for cookie in cookies:
                    cookie_name = cookie['name']
                    cookie_value = cookie['value']
                    logger.info(f"Cookie: {cookie_name} = {cookie_value[:20]}...")
                    
                    # 专门查找Boss直聘相关的cookies - 增强版
                    boss_token_keys = [
                        'wt2', 'zp_at', 'zp_token', 'boss_token', 'zhipin_token', 'geek_token',
                        '__zp_stoken__', '__zp_seo__', '__zp_seo_uuid__', '__zp_stoken__',
                        'zp_seo_uuid', 'zp_seo', 'zp_token', 'zp_at', 'wt2',
                        'bst', 'wbg', 'zp_seo_uuid', 'zp_seo', 'zp_token', 'zp_at', 'wt2',
                        'sessionid', 'session_id', 'auth_token', 'access_token',
                        'user_token', 'login_token', 'auth_cookie', 'user_cookie',
                        '__a', '__c', '__g', '__l', '__zp_stoken__', '__zp_seo__'
                    ]
                    
                    if any(token_key in cookie_name.lower() for token_key in boss_token_keys):
                        boss_cookies[cookie_name] = cookie_value
                        cookie_count += 1
                        if not token_info.get('token') and len(cookie_value) > 5:  # 降低长度要求
                            token_info['token'] = cookie_value
                            token_info['source'] = 'cookies'
                            token_info['cookie_name'] = cookie_name
                        logger.info(f"✅ 从cookies找到Boss直聘token: {cookie_name} = {cookie_value[:30]}...")
                    elif any(token_key in cookie_name.lower() for token_key in ['token', 'auth', 'session']) and len(cookie_value) > 10:
                        # 查找其他可能的token cookies
                        token_info['cookies'] = {cookie_name: cookie_value}
                        if not token_info.get('token'):
                            token_info['token'] = cookie_value
                            token_info['source'] = 'cookies'
                        logger.info(f"✅ 从cookies找到可能的token: {cookie_name}")
            except Exception as e:
                logger.warning(f"获取cookies失败: {str(e)}")
            
            # 3. 尝试从页面JavaScript变量中获取token
            try:
                logger.info("🔍 检查JavaScript变量...")
                # 扩展token变量列表
                token_vars = [
                    'window.__INITIAL_STATE__',
                    'window.__NUXT__',
                    'window.userInfo',
                    'window.token',
                    'window.authToken',
                    'window.wt2',
                    'window.__APP_INITIAL_STATE__',
                    'window.__INITIAL_DATA__',
                    'window.user',
                    'window.auth',
                    'window.session',
                    'window.__DATA__'
                ]
                
                for var_name in token_vars:
                    try:
                        var_value = page.evaluate(f"() => {var_name}")
                        if var_value:
                            logger.info(f"找到变量 {var_name}: {type(var_value)}")
                            
                            if isinstance(var_value, dict):
                                # 在对象中查找token
                                for key, value in var_value.items():
                                    if any(token_key in key.lower() for token_key in ['token', 'auth', 'wt2', 'zp_at', 'access', 'session', 'user_id', 'uid']):
                                        if isinstance(value, str) and len(value) > 10:
                                            token_info['js_variables'] = {var_name: {key: value}}
                                            if not token_info.get('token'):
                                                token_info['token'] = value
                                                token_info['source'] = f'js_variable_{var_name}'
                                            logger.info(f"✅ 从JavaScript变量找到token: {var_name}.{key}")
                                            break
                            elif isinstance(var_value, str) and len(var_value) > 10:
                                # 直接是字符串token
                                token_info['js_variables'] = {var_name: var_value}
                                if not token_info.get('token'):
                                    token_info['token'] = var_value
                                    token_info['source'] = f'js_variable_{var_name}'
                                logger.info(f"✅ 从JavaScript变量找到token: {var_name}")
                    except Exception as e:
                        logger.debug(f"检查变量 {var_name} 失败: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.warning(f"获取JavaScript变量失败: {str(e)}")
            
            # 4. 尝试从页面HTML中提取token
            try:
                logger.info("🔍 从HTML内容中提取token...")
                page_content = page.content()
                import re
                
                # 扩展token模式列表
                token_patterns = [
                    r'"wt2":"([^"]+)"',
                    r'"zp_at":"([^"]+)"',
                    r'"token":"([^"]+)"',
                    r'"authToken":"([^"]+)"',
                    r'"accessToken":"([^"]+)"',
                    r'"sessionToken":"([^"]+)"',
                    r'"userToken":"([^"]+)"',
                    r'wt2=([^&\s]+)',
                    r'zp_at=([^&\s]+)',
                    r'token=([^&\s]+)',
                    r'authToken=([^&\s]+)',
                    r'window\.wt2\s*=\s*["\']([^"\']+)["\']',
                    r'window\.token\s*=\s*["\']([^"\']+)["\']',
                    r'window\.authToken\s*=\s*["\']([^"\']+)["\']',
                    r'__INITIAL_STATE__.*?["\']token["\']:\s*["\']([^"\']+)["\']',
                    r'__NUXT__.*?["\']token["\']:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in token_patterns:
                    matches = re.findall(pattern, page_content, re.IGNORECASE)
                    for match in matches:
                        if len(match) > 10:  # 确保是有效的token
                            token_info['html_extraction'] = {'pattern': pattern, 'value': match}
                            if not token_info.get('token'):
                                token_info['token'] = match
                                token_info['source'] = 'html_extraction'
                            logger.info(f"✅ 从HTML中提取到token: {pattern}")
                            break
                    if token_info.get('token'):
                        break
                        
            except Exception as e:
                logger.warning(f"从HTML提取token失败: {str(e)}")
            
            # 5. 尝试从页面URL参数中提取token
            try:
                logger.info("🔍 检查URL参数中的token...")
                current_url = page.url
                import urllib.parse
                
                parsed_url = urllib.parse.urlparse(current_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                for param_name, param_values in query_params.items():
                    if any(token_key in param_name.lower() for token_key in ['token', 'auth', 'wt2', 'zp_at']):
                        for value in param_values:
                            if len(value) > 10:
                                token_info['url_params'] = {param_name: value}
                                if not token_info.get('token'):
                                    token_info['token'] = value
                                    token_info['source'] = 'url_params'
                                logger.info(f"✅ 从URL参数找到token: {param_name}")
                                break
            except Exception as e:
                logger.warning(f"从URL参数提取token失败: {str(e)}")
            
            # 6. 尝试从页面标题和meta标签中提取token
            try:
                logger.info("🔍 检查页面标题和meta标签...")
                title = page.title()
                logger.info(f"页面标题: {title}")
                
                # 检查meta标签
                meta_tags = page.evaluate("""
                    () => {
                        const metas = document.querySelectorAll('meta');
                        const result = {};
                        metas.forEach(meta => {
                            const name = meta.getAttribute('name') || meta.getAttribute('property');
                            const content = meta.getAttribute('content');
                            if (name && content) {
                                result[name] = content;
                            }
                        });
                        return result;
                    }
                """)
                
                for name, content in meta_tags.items():
                    if any(token_key in name.lower() for token_key in ['token', 'auth', 'wt2', 'zp_at']):
                        if len(content) > 10:
                            token_info['meta_tags'] = {name: content}
                            if not token_info.get('token'):
                                token_info['token'] = content
                                token_info['source'] = 'meta_tags'
                            logger.info(f"✅ 从meta标签找到token: {name}")
            except Exception as e:
                logger.warning(f"从meta标签提取token失败: {str(e)}")
            
            # 设置cookie信息
            if boss_cookies:
                token_info['cookies'] = boss_cookies
                token_info['cookie_count'] = cookie_count
                logger.info(f"✅ 找到 {cookie_count} 个Boss直聘相关cookies")
            
            # 设置过期时间（如果有的话）
            if not token_info.get('expires_at'):
                token_info['expires_at'] = '未知'
            
            # 验证提取到的token
            if token_info.get('token'):
                validation_result = self._validate_boss_token(token_info)
                token_info['validation'] = validation_result
                
                if validation_result['valid']:
                    logger.info(f"🎉 成功提取到有效token: {token_info['token'][:20]}... (来源: {token_info.get('source', '未知')})")
                else:
                    logger.warning(f"⚠️ 提取到token但验证失败: {validation_result['reason']}")
            else:
                logger.warning("❌ 未能提取到有效token")
                logger.info(f"提取到的信息: {token_info}")
            
            return token_info
            
        except Exception as e:
            logger.error(f"提取token失败: {str(e)}")
            return {}
    
    def _navigate_with_retry(self, url: str, max_retries: int = 3, timeout: int = 30000) -> bool:
        """带重试机制的页面导航方法"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 尝试访问页面 (第{attempt + 1}次): {url}")
                self.page.goto(url, timeout=timeout)
                self.page.wait_for_load_state('load', timeout=15000)
                logger.info(f"✅ 页面访问成功: {url}")
                return True
            except Exception as e:
                logger.warning(f"⚠️ 第{attempt + 1}次访问失败: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待时间
                    logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ 页面访问最终失败: {str(e)}")
                    return False
        return False
    
    def _check_page_login_status(self, page) -> bool:
        """检查指定页面的登录状态 - 基于深度调试的优化检测方法"""
        try:
            logger.info("🔍 开始检查页面登录状态...")
            
            # 等待页面加载完成
            try:
                page.wait_for_load_state('networkidle', timeout=5000)
            except Exception:
                pass
            
            current_url = page.url
            logger.info(f"🔍 当前页面URL: {current_url}")
            
            # 0. 检查是否遇到安全验证页面
            if 'security-check.html' in current_url:
                logger.warning("⚠️ 遇到安全验证页面，需要等待验证完成")
                # 等待安全验证完成
                import time
                time.sleep(5)  # 等待5秒
                
                # 检查是否自动跳转
                try:
                    page.wait_for_load_state('networkidle', timeout=10000)
                    current_url = page.url
                    logger.info(f"🔍 安全验证后URL: {current_url}")
                except Exception:
                    pass
            
            # 1. 优先检查关键登录成功指标 - 基于Java项目的发现
            # Java项目使用 div.job-list-container 作为登录成功的标志
            critical_login_indicators = [
                'div.job-list-container',  # 职位列表容器（Java项目的关键指标）
                'div[class*="job-list-container"]',  # 更宽泛的匹配
                'ul.rec-job-list',  # 职位列表
                'li.job-card-box',  # 职位卡片
            ]
            
            for indicator in critical_login_indicators:
                try:
                    element = page.query_selector(indicator)
                    if element and element.is_visible():
                        logger.info(f"✅ 找到关键登录指标: {indicator}，确认已登录")
                        return True
                except Exception:
                    continue
            
            # 2. 检查URL是否包含登录后的特征（优先级提高）
            if any(path in current_url for path in ['/web/geek/jobs', '/web/geek/chat', '/web/geek/profile', '/web/geek/job']):
                logger.info(f"✅ 通过URL检测到登录状态: {current_url}")
                return True
            
            # 3. 检查是否有登录/注册按钮（如果有说明未登录）
            login_indicators = [
                'text="登录/注册"',
                'text="立即登录"',
                'text="扫码登录"',
                '.login-btn',
                'button:has-text("登录")',
                'a:has-text("登录")',
                '//li[@class="nav-figure"]',  # Java项目的登录按钮定位器
                '//div[@class="btns"]'  # Java项目的登录按钮容器
            ]
            
            for indicator in login_indicators:
                try:
                    element = page.query_selector(indicator)
                    if element and element.is_visible():
                        logger.info(f"❌ 发现登录按钮: {indicator}，说明未登录")
                        return False
                except Exception:
                    continue
            
            # 4. 检查页面是否包含登录后的特征元素
            logged_in_selectors = [
                # 用户信息相关
                '.user-name', '.geek-name', '.profile-name',
                '.user-avatar', '.geek-avatar', '.profile-avatar',
                '.nav-user', '.user-menu', '.profile-menu',
                
                # 功能按钮相关
                'button:has-text("立即沟通")', 'button:has-text("投递简历")',
                'button:has-text("收藏")', 'button:has-text("举报")',
                'a.btn-startchat', 'a.op-btn-chat',  # Java项目的聊天按钮
                
                # 页面结构相关
                'div.job-list-container',  # 职位列表容器（关键指标）
                '.job-list', '.job-item',
                '.search-result', '.job-search-result',
                
                # 用户中心相关
                '.user-center', '.my-resume', '.my-delivery',
                'a:has-text("我的简历")', 'a:has-text("我的投递")',
                'a:has-text("个人中心")'
            ]
            
            found_indicators = []
            for selector in logged_in_selectors:
                try:
                    element = page.query_selector(selector)
                    if element and element.is_visible():
                        found_indicators.append(selector)
                        logger.info(f"✅ 找到登录后元素: {selector}")
                except Exception:
                    continue
            
            # 如果找到登录后元素，确认已登录
            if found_indicators:
                logger.info(f"✅ 找到 {len(found_indicators)} 个登录后元素，确认已登录")
                return True
            
            # 5. 检查页面内容是否包含登录后的关键词
            try:
                page_content = page.content().lower()
                login_keywords = [
                    '立即沟通', '投递简历', '我的简历', '我的投递',
                    '个人中心', '退出', 'logout', '用户中心',
                    '简历管理', '投递管理', '消息中心'
                ]
                
                keyword_count = sum(1 for keyword in login_keywords if keyword in page_content)
                if keyword_count >= 2:
                    logger.info(f"✅ 通过页面内容检测到登录状态 (匹配{keyword_count}个关键词)")
                    return True
            except Exception as e:
                logger.warning(f"检查页面内容失败: {str(e)}")
            
            # 6. 检查页面标题
            try:
                page_title = page.title()
                if any(keyword in page_title for keyword in ['职位', '招聘', 'Boss直聘']):
                    logger.info(f"✅ 通过页面标题检测到登录状态: {page_title}")
                    return True
            except Exception:
                pass
            
            logger.warning("⚠️ 未找到明确的登录状态指示器，认为未登录")
            return False
            
        except Exception as e:
            logger.warning(f"检查页面登录状态失败: {str(e)}")
            return False
    
    def _validate_token_with_playwright(self, token: str) -> Dict:
        """使用Playwright验证token的有效性"""
        try:
            # 初始化新的Playwright实例进行token验证
            playwright = sync_playwright().start()
            
            try:
                # 启动新的浏览器实例
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # 设置token到cookies
                context.add_cookies([
                    {
                        'name': 'wt2',
                        'value': token,
                        'domain': '.zhipin.com',
                        'path': '/',
                        'httpOnly': True,
                        'secure': True
                    }
                ])
                
                # 访问Boss直聘页面验证token
                page.goto("https://www.zhipin.com/web/geek/jobs", wait_until="networkidle", timeout=10000)
                
                # 检查是否成功登录
                is_logged_in = self._check_page_login_status(page)
                
                if is_logged_in:
                    logger.info("✅ Token验证成功，用户已登录")
                    return {
                        "success": True,
                        "is_logged_in": True,
                        "message": "Token验证成功",
                        "current_url": page.url
                    }
                else:
                    logger.warning("❌ Token验证失败，用户未登录")
                    return {
                        "success": False,
                        "is_logged_in": False,
                        "message": "Token验证失败，用户未登录"
                    }
                    
            finally:
                browser.close()
                playwright.stop()
                
        except Exception as e:
            logger.error(f"Token验证过程中出错: {str(e)}")
            return {
                "success": False,
                "is_logged_in": False,
                "message": f"Token验证失败: {str(e)}"
            }
    
    def _check_login_via_simple_bypass(self) -> Dict:
        """使用简单绕过服务检查登录状态"""
        try:
            logger.info("🔍 使用简单绕过服务检查登录状态...")
            
            # 尝试访问Boss直聘主页
            main_url = f"{self.base_url}/web/geek/jobs"
            
            # 使用简单绕过服务
            bypass_result = self.simple_bypass_service.bypass_security_verification(main_url)
            
            if bypass_result.get('bypassed'):
                logger.info("✅ 简单绕过服务成功绕过安全验证")
                
                # 提取token
                response = bypass_result.get('response')
                if response:
                    token_info = self.simple_bypass_service.extract_tokens_from_response(response)
                    
                    # 检查页面内容是否真的登录了（更严格的检查）
                    content = response.text
                    if len(content) < 10000:  # 页面内容太短，可能是静态页面
                        logger.warning("❌ 页面内容太短，可能是静态页面，说明未登录")
                        return {
                            "success": True,
                            "is_logged_in": False,
                            "found_indicator": "static_page",
                            "login_confidence": 0,
                            "current_url": response.url,
                            "message": "页面内容太短，可能是静态页面，需要先登录",
                            "security_verification": False,
                            "token_info": None,
                            "method_used": bypass_result.get('method', 'unknown')
                        }
                    
                    # 检查是否找到了有效token
                    if token_info and token_info.get('token'):
                        return {
                            "success": True,
                            "is_logged_in": True,
                            "found_indicator": "simple_bypass",
                            "login_confidence": 90,
                            "current_url": response.url,
                            "message": "通过简单绕过服务检测到登录状态",
                            "token_info": token_info,
                            "method_used": bypass_result.get('method', 'unknown')
                        }
                    else:
                        # 没有找到token，说明未登录
                        logger.warning("❌ 绕过成功但未找到token，说明未登录")
                        return {
                            "success": True,
                            "is_logged_in": False,
                            "found_indicator": "simple_bypass_no_token",
                            "login_confidence": 0,
                            "current_url": response.url,
                            "message": "绕过成功但未找到登录token，需要先登录",
                            "security_verification": False,
                            "token_info": None,
                            "method_used": bypass_result.get('method', 'unknown')
                        }
            
            # 即使未能绕过，也检查是否是安全验证页面
            if 'security_verification' in str(bypass_result):
                logger.warning("❌ 检测到安全验证页面，说明未登录")
                return {
                    "success": True,
                    "is_logged_in": False,
                    "found_indicator": "security_verification",
                    "login_confidence": 0,
                    "message": "检测到安全验证页面，需要先登录",
                    "security_verification": True,
                    "token_info": None,
                    "current_url": bypass_result.get('response', {}).get('url', ''),
                    "method_used": "security_verification_detection"
                }
            
            # 如果绕过成功但未找到token，说明未登录
            if bypass_result.get('bypassed') and not token_info:
                logger.warning("❌ 绕过成功但未找到token，说明未登录")
                return {
                    "success": True,
                    "is_logged_in": False,
                    "found_indicator": "bypass_success_no_token",
                    "login_confidence": 0,
                    "message": "绕过成功但未找到token，需要先登录",
                    "security_verification": False,
                    "token_info": None,
                    "current_url": bypass_result.get('response', {}).get('url', ''),
                    "method_used": bypass_result.get('method', 'unknown')
                }
            
            # 如果found_indicator是simple_bypass但token_info为空，说明未登录
            if result.get('found_indicator') == 'simple_bypass' and not token_info:
                logger.warning("❌ simple_bypass检测成功但未找到token，说明未登录")
                return {
                    "success": True,
                    "is_logged_in": False,
                    "found_indicator": "simple_bypass_no_token",
                    "login_confidence": 0,
                    "message": "simple_bypass检测成功但未找到token，需要先登录",
                    "security_verification": False,
                    "token_info": None,
                    "current_url": result.get('current_url', ''),
                    "method_used": result.get('method_used', 'unknown')
                }
            
            return {
                "success": False,
                "is_logged_in": False,
                "message": "简单绕过服务未能检测到登录状态"
            }
            
        except Exception as e:
            logger.error(f"简单绕过服务检查失败: {str(e)}")
            return {
                "success": False,
                "is_logged_in": False,
                "message": f"简单绕过服务检查失败: {str(e)}"
            }
    
    def _check_login_via_local_session(self) -> Dict:
        """通过本地浏览器session检查登录状态"""
        try:
            from .local_session_extractor import LocalSessionExtractor
            
            logger.info("🔍 从本地浏览器提取Boss直聘session...")
            extractor = LocalSessionExtractor()
            session_result = extractor.get_all_boss_sessions()
            
            if not session_result.get('success'):
                logger.warning(f"❌ 本地session提取失败: {session_result.get('error')}")
                return {
                    "success": False,
                    "is_logged_in": False,
                    "message": f"本地session提取失败: {session_result.get('error')}"
                }
            
            best_result = session_result['best_result']
            cookies = best_result['cookies']
            
            if not cookies:
                logger.warning("❌ 未找到有效的Boss直聘cookies")
                return {
                    "success": False,
                    "is_logged_in": False,
                    "message": "未找到有效的Boss直聘cookies"
                }
            
            logger.info(f"✅ 从{best_result['browser']}浏览器提取到{len(cookies)}个cookies")
            
            # 验证cookies是否有效
            validation_result = self._validate_local_cookies(cookies)
            
            if validation_result.get('valid'):
                return {
                    "success": True,
                    "is_logged_in": True,
                    "found_indicator": "local_session",
                    "login_confidence": 95,
                    "message": f"通过本地{best_result['browser']}浏览器检测到登录状态",
                    "token_info": cookies,
                    "browser": best_result['browser'],
                    "cookie_count": len(cookies),
                    "validation": validation_result
                }
            else:
                logger.warning(f"❌ 本地cookies验证失败: {validation_result.get('error')}")
                return {
                    "success": False,
                    "is_logged_in": False,
                    "message": f"本地cookies验证失败: {validation_result.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"本地session检查失败: {str(e)}")
            return {
                "success": False,
                "is_logged_in": False,
                "message": f"本地session检查失败: {str(e)}"
            }
    
    def _validate_local_cookies(self, cookies: Dict[str, str]) -> Dict[str, Any]:
        """验证本地cookies是否有效"""
        try:
            import requests
            
            # 使用提取的cookies访问Boss直聘API
            session = requests.Session()
            
            # 设置cookies
            for name, value in cookies.items():
                session.cookies.set(name, value, domain='.zhipin.com')
            
            # 测试访问用户信息API
            test_url = f"{self.base_url}/api/user/info"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': f"{self.base_url}/web/geek/jobs",
                'Accept': 'application/json, text/plain, */*',
            }
            
            response = session.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('code') == 0 and data.get('data'):
                        logger.info("✅ 本地cookies验证成功，用户已登录")
                        return {
                            "valid": True,
                            "user_info": data.get('data', {}),
                            "message": "cookies有效，用户已登录"
                        }
                except:
                    pass
            
            # 如果API验证失败，尝试访问主页
            main_url = f"{self.base_url}/web/geek/jobs"
            response = session.get(main_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 检查页面内容是否包含登录用户信息
                content = response.text
                if any(indicator in content for indicator in ['user-info', 'user-avatar', 'geek-info']):
                    logger.info("✅ 本地cookies验证成功，通过页面内容检测到登录状态")
                    return {
                        "valid": True,
                        "message": "cookies有效，通过页面内容检测到登录状态"
                    }
            
            logger.warning("❌ 本地cookies验证失败，用户可能未登录或cookies已过期")
            return {
                "valid": False,
                "error": "cookies无效或已过期",
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"cookies验证失败: {str(e)}")
            return {
                "valid": False,
                "error": f"验证失败: {str(e)}"
            }
    
    def _validate_saved_cookies(self, cookies: Dict[str, str]) -> Dict:
        """验证保存的cookies是否有效"""
        try:
            logger.info("🔍 验证保存的cookies有效性...")
            
            # 使用requests验证cookies
            import requests
            
            session = requests.Session()
            
            # 设置cookies
            for name, value in cookies.items():
                session.cookies.set(name, value, domain='.zhipin.com')
            
            # 测试访问Boss直聘主页
            test_url = "https://www.zhipin.com/web/geek/jobs"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = session.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # 检查是否包含登录用户信息
                login_indicators = [
                    'user-info', 'user-avatar', 'geek-info', 'geek-name',
                    'user-name', 'user-profile', 'login-success'
                ]
                
                is_logged_in = any(indicator in content for indicator in login_indicators)
                
                if is_logged_in:
                    logger.info("✅ 保存的cookies验证成功，用户已登录")
                    return {
                        "success": True,
                        "is_logged_in": True,
                        "found_indicator": "saved_cookies",
                        "login_confidence": 95,
                        "message": "使用保存的cookies检测到登录状态",
                        "token_info": cookies,
                        "browser": "saved",
                        "cookie_count": len(cookies)
                    }
                else:
                    logger.warning("❌ 保存的cookies可能已过期，未检测到登录状态")
                    # 清除过期的cookies
                    cookie_manager.clear_cookies()
                    return {
                        "success": False,
                        "is_logged_in": False,
                        "error": "保存的cookies已过期",
                        "need_login": True
                    }
            else:
                logger.warning(f"❌ cookies验证请求失败，状态码: {response.status_code}")
                return {
                    "success": False,
                    "is_logged_in": False,
                    "error": f"验证请求失败，状态码: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"验证保存的cookies失败: {str(e)}")
            return {
                "success": False,
                "is_logged_in": False,
                "error": f"验证失败: {str(e)}"
            }

    def set_cookies(self, cookies: Dict) -> bool:
        """设置cookies到浏览器上下文 - 修复asyncio问题"""
        try:
            if not self.page:
                if not self._init_browser():
                    return False
            
            # 导航到Boss直聘首页
            self.page.goto(self.base_url, timeout=10000)
            
            # 转换cookies格式并直接设置
            playwright_cookies = []
            for name, value in cookies.items():
                if isinstance(value, str) and len(value) > 0:
                    playwright_cookies.append({
                        "name": name,
                        "value": value,
                        "domain": ".zhipin.com",
                        "path": "/",
                        "secure": True,
                        "httpOnly": True
                    })
            
            # 直接添加cookies到上下文，不使用asyncio检查
            self.page.context.add_cookies(playwright_cookies)
            logger.info(f"✅ 已设置 {len(playwright_cookies)} 个cookies")
            
            # 保存cookies到文件（持久化存储）
            self.save_cookies_to_file(playwright_cookies)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 设置cookies失败: {str(e)}")
            return False
    
    def save_cookies_to_file(self, cookies: List[Dict]) -> bool:
        """保存cookies到文件"""
        try:
            # 使用Cookie管理器保存
            success = cookie_manager.save_cookies(cookies, "boss")
            if success:
                logger.info("✅ Cookies已保存到文件")
            else:
                logger.warning("⚠️ Cookies保存到文件失败")
            return success
        except Exception as e:
            logger.error(f"❌ 保存cookies到文件失败: {str(e)}")
            return False
    
    def load_cookies_from_file(self) -> bool:
        """从文件加载cookies"""
        try:
            # 检查Cookie文件是否存在且有效
            if not cookie_manager.is_cookie_valid("boss"):
                logger.info("📁 Cookie文件不存在或已过期")
                return False
            
            # 加载cookies
            cookies = cookie_manager.load_cookies("boss")
            if not cookies:
                logger.warning("⚠️ 从文件加载cookies失败")
                return False
            
            # 转换为Playwright格式
            playwright_cookies = cookie_manager.convert_to_playwright_cookies(cookies)
            
            # 设置到浏览器上下文
            if self.page and self.page.context:
                self.page.context.add_cookies(playwright_cookies)
                logger.info(f"✅ 已从文件加载 {len(playwright_cookies)} 个cookies")
                return True
            else:
                logger.error("❌ 浏览器上下文未初始化")
                return False
                
        except Exception as e:
            logger.error(f"❌ 从文件加载cookies失败: {str(e)}")
            return False

    def check_login_status(self, user_id: int) -> Dict:
        """检查登录状态 - 多种方式检测"""
        try:
            import asyncio
            
            # 检查是否在asyncio循环中
            try:
                loop = asyncio.get_running_loop()
                logger.warning("⚠️ 检测到asyncio循环，使用线程隔离方式检查登录状态")
                # 使用线程隔离的方式检查登录状态，避免asyncio冲突
                import threading
                import queue
                
                result_queue = queue.Queue()
                
                def check_login_in_thread():
                    try:
                        # 在新线程中执行登录状态检查
                        result = self._check_playwright_browser_instance()
                        result_queue.put(('success', result))
                    except Exception as e:
                        result_queue.put(('error', str(e)))
                
                # 在新线程中检查登录状态
                thread = threading.Thread(target=check_login_in_thread)
                thread.start()
                thread.join(timeout=15)  # 15秒超时
                
                if thread.is_alive():
                    logger.warning("⚠️ 登录状态检查超时，返回默认状态")
                    return {
                        "success": True,
                        "is_logged_in": False,
                        "message": "检查超时，请手动确认登录状态",
                        "token_info": {},
                        "current_url": "",
                        "found_indicator": "",
                        "login_confidence": 0,
                        "token_validation": {},
                        "timeout": True
                    }
                
                result_type, result_value = result_queue.get_nowait()
                if result_type == 'success':
                    logger.info("✅ 在线程中成功检查登录状态")
                    return result_value
                else:
                    logger.error(f"❌ 在线程中检查登录状态失败: {result_value}")
                    return {
                        "success": False,
                        "is_logged_in": False,
                        "message": f"检查失败: {result_value}",
                        "token_info": {},
                        "current_url": "",
                        "found_indicator": "",
                        "login_confidence": 0,
                        "token_validation": {},
                        "error": result_value
                    }
                    
            except RuntimeError:
                # 没有运行中的循环，可以安全使用sync API
                logger.info("✅ 没有asyncio循环，可以安全使用sync API")
                pass
            
            logger.info("🔍 开始多种方式检测Boss直聘登录状态...")
            
            # 首先尝试检测Playwright浏览器实例
            logger.info("🔍 尝试检测Playwright浏览器实例...")
            playwright_result = self._check_playwright_browser_instance()
            if playwright_result.get('success') and playwright_result.get('is_logged_in'):
                logger.info("✅ 通过Playwright浏览器实例检测到登录状态")
                return playwright_result
            
            # 然后尝试从本地浏览器提取session
            logger.info("🔍 尝试从本地浏览器提取Boss直聘session...")
            local_session_result = self._check_login_via_local_session()
            if local_session_result.get('success') and local_session_result.get('is_logged_in'):
                logger.info("✅ 通过本地session检测到登录状态")
                return local_session_result
            
            # 然后尝试通过cookie文件检测其他标签页的登录状态
            logger.info("🔍 尝试通过cookie文件检测其他标签页的登录状态...")
            cookie_result = self._check_browser_tabs_via_cookies()
            if cookie_result.get('success') and cookie_result.get('is_logged_in'):
                logger.info("✅ 从其他标签页的cookie中检测到有效token")
                return cookie_result
            
            # 然后尝试检测现有浏览器session
            logger.info("🔍 尝试检测现有浏览器session...")
            existing_session_result = self._check_existing_browser_session()
            if existing_session_result.get('success') and existing_session_result.get('is_logged_in'):
                logger.info("✅ 检测到现有浏览器session中的登录状态")
                return existing_session_result
            
            # 然后尝试通过HTTP请求检测登录状态
            logger.info("🔍 尝试通过HTTP请求检测登录状态...")
            http_result = self._check_login_via_http_request()
            if http_result.get('success') and http_result.get('is_logged_in'):
                logger.info("✅ 通过HTTP请求检测到登录状态")
                logger.info(f"HTTP请求返回的token_info: {http_result.get('token_info', {})}")
                return http_result
            
            # 如果所有方法都失败，返回未登录状态
            logger.info("❌ 所有检测方法都未发现登录状态")
            return {
                "success": True,
                "is_logged_in": False,
                "message": "需要登录",
                "token_info": {},
                "current_url": "",
                "found_indicator": "",
                "login_confidence": 0,
                "token_validation": {},
                "detection_methods": "all_failed"
            }
            
        except Exception as e:
            logger.error(f"❌ 登录状态检查失败: {str(e)}")
            return {
                "success": False,
                "is_logged_in": False,
                "message": f"检查失败: {str(e)}",
                "token_info": {},
                "current_url": "",
                "found_indicator": "",
                "login_confidence": 0,
                "token_validation": {}
            }
    
    def _check_playwright_browser_instance(self) -> Dict:
        """检测Playwright浏览器实例中的登录状态"""
        try:
            logger.info("🔍 检测Playwright浏览器实例...")
            
            # 初始化浏览器
            if not self._init_browser():
                logger.warning("❌ Playwright浏览器初始化失败")
                return {
                    "success": False,
                    "is_logged_in": False,
                    "message": "浏览器初始化失败"
                }
            
            try:
                # 访问Boss直聘主页
                main_url = f"{self.base_url}/web/geek/jobs"
                logger.info(f"正在访问Boss直聘主页: {main_url}")
                
                self.page.goto(main_url, timeout=10000)
                self.page.wait_for_load_state('networkidle', timeout=5000)
                
                # 检查登录状态
                login_status = self._check_page_login_status(self.page)
                
                if login_status:
                    logger.info("✅ 在Playwright浏览器中检测到登录状态")
                    
                    # 提取cookies
                    cookies = self.page.context.cookies()
                    cookie_dict = {}
                    for cookie in cookies:
                        if 'zhipin.com' in cookie.get('domain', ''):
                            cookie_dict[cookie['name']] = cookie['value']
                    
                    return {
                        "success": True,
                        "is_logged_in": True,
                        "message": "在Playwright浏览器中检测到登录状态",
                        "token_info": cookie_dict,
                        "found_indicator": "playwright_browser",
                        "login_confidence": 90,
                        "current_url": self.page.url,
                        "cookie_count": len(cookie_dict)
                    }
                else:
                    logger.info("❌ 在Playwright浏览器中未检测到登录状态")
                    return {
                        "success": True,
                        "is_logged_in": False,
                        "message": "在Playwright浏览器中未检测到登录状态"
                    }
                    
            except Exception as e:
                logger.error(f"❌ Playwright浏览器检测失败: {str(e)}")
                return {
                    "success": False,
                    "is_logged_in": False,
                    "message": f"浏览器检测失败: {str(e)}"
                }
            finally:
                # 关闭浏览器
                try:
                    self._close_browser()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"❌ Playwright浏览器实例检测失败: {str(e)}")
            return {
                "success": False,
                "is_logged_in": False,
                "message": f"检测失败: {str(e)}"
            }
            
            # 最后尝试从本地浏览器提取session
            logger.info("🔍 尝试从本地浏览器提取Boss直聘session...")
            local_session_result = self._check_login_via_local_session()
            if local_session_result.get('success') and local_session_result.get('is_logged_in'):
                logger.info("✅ 通过本地session检测到登录状态")
                return local_session_result
            
            # 然后尝试通过cookie文件检测其他标签页的登录状态
            logger.info("🔍 尝试通过cookie文件检测其他标签页的登录状态...")
            cookie_result = self._check_browser_tabs_via_cookies()
            if cookie_result.get('success') and cookie_result.get('is_logged_in'):
                logger.info("✅ 从其他标签页的cookie中检测到有效token")
                return cookie_result
            
            # 然后尝试检测现有浏览器session
            logger.info("🔍 尝试检测现有浏览器session...")
            existing_session_result = self._check_existing_browser_session()
            if existing_session_result.get('success') and existing_session_result.get('is_logged_in'):
                logger.info("✅ 检测到现有浏览器session中的登录状态")
                return existing_session_result
            
            # 然后尝试通过HTTP请求检测登录状态
            logger.info("🔍 尝试通过HTTP请求检测登录状态...")
            http_result = self._check_login_via_http_request()
            if http_result.get('success') and http_result.get('is_logged_in'):
                logger.info("✅ 通过HTTP请求检测到登录状态")
                logger.info(f"HTTP请求返回的token_info: {http_result.get('token_info', {})}")
                return http_result
            
            # 如果没有检测到现有session，则启动新的浏览器实例
            logger.info("🔄 未检测到现有session，启动新的浏览器实例进行检测...")
            
            # 初始化浏览器
            if not self._init_browser():
                return {"success": False, "message": "Playwright浏览器初始化失败"}

            try:
                # 访问Boss直聘主页
                main_url = f"{self.base_url}/web/geek/jobs"
                logger.info(f"正在访问Boss直聘主页: {main_url}")

                # 使用反检测服务进行安全导航
                if self.anti_detection_service:
                    success = self.anti_detection_service.safe_navigation(self.page, main_url)
                    if not success:
                        return {"success": False, "message": "页面导航失败"}
                    
                    # 尝试绕过安全检查
                    security_result = self.anti_detection_service.bypass_security_check(self.page)
                    if not security_result.get("bypassed"):
                        # 检查是否是安全验证页面，如果是，则尝试绕过
                        if security_result.get("reason") == "security_verification":
                            logger.info("✅ 检测到安全验证页面，尝试绕过...")
                            
                            # 使用新的安全验证绕过服务
                            bypass_result = self.security_bypass_service.bypass_security_verification(self.page)
                            
                            if bypass_result.get("bypassed"):
                                logger.info("✅ 成功绕过安全验证")
                                # 尝试从页面提取token
                                token_info = self._extract_token_from_page(self.page)
                                
                                return {
                                    "success": True,
                                    "is_logged_in": True,
                                    "found_indicator": "security_verification_bypassed",
                                    "login_confidence": 90,
                                    "current_url": self.page.url,
                                    "message": "成功绕过安全验证并检测到登录状态",
                                    "security_verification": False,
                                    "token_info": token_info
                                }
                            else:
                                logger.info("❌ 未能绕过安全验证，但认为已登录")
                                # 即使未能绕过，也认为已登录（因为检测到了安全验证页面）
                                token_info = self._extract_token_from_page(self.page)
                                
                                return {
                                    "success": True,
                                    "is_logged_in": False,
                                    "found_indicator": "security_verification",
                                    "login_confidence": 0,
                                    "current_url": self.page.url,
                                    "message": "检测到安全验证页面，需要先登录",
                                    "security_verification": True,
                                    "token_info": None
                                }
                        else:
                            return {
                                "success": False,
                                "message": security_result.get("message", "安全检查失败"),
                                "is_logged_in": False,
                                "security_check": True
                            }
                else:
                    self.page.goto(main_url, wait_until="networkidle", timeout=10000)
                    time.sleep(2)

                # 首先尝试提取token
                token_info = self._extract_token_from_browser()
                
                # 检查登录状态 - 使用多种检测方式
                is_logged_in = False
                found_indicator = None
                login_confidence = 0
                
                # 获取页面内容
                page_content = self.page.content()
                current_url = self.page.url
                
                logger.info(f"当前页面URL: {current_url}")
                logger.info(f"页面标题: {self.page.title()}")
                
                # 1. 检查是否有有效的token（最高优先级）
                if token_info.get('token') and len(token_info.get('token', '')) > 10:
                    is_logged_in = True
                    found_indicator = "token_found"
                    login_confidence = 100
                    logger.info(f"✅ 通过token检测到登录状态: {token_info['token'][:20]}...")
                else:
                    # 2. 检查URL是否包含用户相关路径
                    user_paths = ['/user/', '/profile/', '/geek/', '/my/', '/account/', '/dashboard/']
                    if any(path in current_url for path in user_paths):
                        is_logged_in = True
                        found_indicator = "user_url"
                        login_confidence = 90
                        logger.info("✅ 通过用户URL检测到登录状态")
                    
                    # 3. 检查是否在安全验证页面
                    elif 'verify-slider' in current_url or 'safe/verify' in current_url or 'security' in current_url:
                        is_logged_in = False
                        found_indicator = "security_verification"
                        login_confidence = 0
                        logger.warning("❌ 检测到安全验证页面，说明未登录")
                        
                        # 安全验证页面说明未登录，不需要提取token
                        token_info = None
                    
                    # 4. 检查页面是否包含登录后的特征元素
                    elif self._check_logged_in_elements():
                        is_logged_in = True
                        found_indicator = "logged_in_elements"
                        login_confidence = 80
                        logger.info("✅ 通过登录后元素检测到登录状态")
                        
                        # 重新尝试提取token信息
                        if not token_info or not token_info.get('token'):
                            logger.info("🔍 重新尝试从页面提取token信息...")
                            token_info = self._extract_token_from_page(self.page)
                    
                    # 5. 检查页面是否包含退出相关关键词
                    elif any(keyword in page_content.lower() for keyword in ['退出', 'logout', '登出', 'sign out']):
                        is_logged_in = True
                        found_indicator = "logout_keywords"
                        login_confidence = 75
                        logger.info("✅ 通过退出关键词检测到登录状态")
                        
                        # 重新尝试提取token信息
                        if not token_info or not token_info.get('token'):
                            logger.info("🔍 重新尝试从页面提取token信息...")
                            token_info = self._extract_token_from_page(self.page)
                    
                    # 6. 检查是否有职位搜索功能（登录后才有）
                    elif any(keyword in page_content.lower() for keyword in ['搜索职位', 'job search', '职位搜索', '立即沟通', '投递简历']):
                        is_logged_in = True
                        found_indicator = "job_search_available"
                        login_confidence = 70
                        logger.info("✅ 通过职位搜索功能检测到登录状态")
                        
                        # 重新尝试提取token信息
                        if not token_info or not token_info.get('token'):
                            logger.info("🔍 重新尝试从页面提取token信息...")
                            token_info = self._extract_token_from_page(self.page)
                    
                    # 7. 检查是否包含Boss直聘特有的登录后元素
                    elif self._check_boss_specific_elements():
                        is_logged_in = True
                        found_indicator = "boss_specific_elements"
                        login_confidence = 65
                        logger.info("✅ 通过Boss直聘特有元素检测到登录状态")
                    
                    # 8. 检查是否不包含登录相关关键词（低优先级）
                    elif not any(keyword in page_content.lower() for keyword in ['登录', 'login', '注册', 'register', '手机号', '验证码', '密码']):
                        is_logged_in = True
                        found_indicator = "no_login_keywords"
                        login_confidence = 60
                        logger.info("✅ 页面不包含登录关键词，认为已登录")
                    
                    # 9. 检查是否被重定向到登录页面
                    elif any(keyword in current_url.lower() for keyword in ['login', 'signin', 'auth', '登录']):
                        is_logged_in = False
                        found_indicator = "redirected_to_login"
                        login_confidence = 0
                        logger.warning("❌ 被重定向到登录页面，未登录")
                    
                    # 10. 检查页面是否包含登录表单
                    elif any(keyword in page_content.lower() for keyword in ['登录表单', 'login form', '用户名', '密码输入', '验证码输入']):
                        is_logged_in = False
                        found_indicator = "login_form_present"
                        login_confidence = 0
                        logger.warning("❌ 页面包含登录表单，未登录")
                    
                    else:
                        # 默认情况，尝试通过其他方式判断
                        is_logged_in = self._fallback_login_check()
                        if is_logged_in:
                            found_indicator = "fallback_check"
                            login_confidence = 50
                            logger.info("✅ 通过备用检查方式检测到登录状态")
                        else:
                            found_indicator = "no_login_detected"
                            login_confidence = 0
                            logger.warning("❌ 未检测到登录状态")

                # 获取页面信息
                page_title = self.page.title()
                current_url = self.page.url

                # 尝试获取用户信息
                user_info = {}
                if is_logged_in:
                    try:
                        # 尝试获取用户名
                        username_selectors = [".user-name", ".geek-name", ".profile-name"]
                        for selector in username_selectors:
                            try:
                                element = self.page.query_selector(selector)
                                if element and element.text_content().strip():
                                    user_info["username"] = element.text_content().strip()
                                    break
                            except Exception:
                                continue

                        # 尝试获取头像
                        avatar_selectors = [".user-avatar img", ".geek-avatar img", ".profile-avatar img"]
                        for selector in avatar_selectors:
                            try:
                                element = self.page.query_selector(selector)
                                if element:
                                    avatar_src = element.get_attribute("src")
                                    if avatar_src and "default" not in avatar_src.lower():
                                        user_info["avatar"] = avatar_src
                                        break
                            except Exception:
                                continue

                    except Exception as e:
                        logger.warning(f"获取用户信息失败: {str(e)}")

                result = {
                    "success": True,
                    "status": "SUCCESS" if is_logged_in else "NOT_LOGGED_IN",
                    "is_logged_in": is_logged_in,
                    "page_title": page_title,
                    "current_url": current_url,
                    "user_info": user_info,
                    "found_indicator": found_indicator,
                    "login_confidence": login_confidence,
                    "token_info": token_info,
                    "message": f"已登录 (置信度: {login_confidence}%)" if is_logged_in else f"未登录 (置信度: {login_confidence}%)",
                }

                logger.info(f"登录状态检查完成: {result}")
                return result

            finally:
                # 关闭浏览器
                self._close_browser()

        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return {"success": False, "message": f"检查登录状态失败: {str(e)}"}
    
    def _extract_token_from_browser(self) -> Dict:
        """从浏览器中提取token信息"""
        try:
            token_info = {}
            
            # 尝试从localStorage获取token
            try:
                local_storage = self.page.evaluate("() => window.localStorage")
                for key, value in local_storage.items():
                    if any(token_key in key.lower() for token_key in ['token', 'auth', 'access', 'jwt']):
                        token_info['localStorage'] = {key: value}
                        if not token_info.get('token'):
                            token_info['token'] = value
                        logger.info(f"从localStorage找到token: {key}")
            except Exception as e:
                logger.warning(f"获取localStorage失败: {str(e)}")
            
            # 尝试从sessionStorage获取token
            try:
                session_storage = self.page.evaluate("() => window.sessionStorage")
                for key, value in session_storage.items():
                    if any(token_key in key.lower() for token_key in ['token', 'auth', 'access', 'jwt']):
                        token_info['sessionStorage'] = {key: value}
                        if not token_info.get('token'):
                            token_info['token'] = value
                        logger.info(f"从sessionStorage找到token: {key}")
            except Exception as e:
                logger.warning(f"获取sessionStorage失败: {str(e)}")
            
            # 尝试从cookies获取token
            try:
                cookies = self.page.context.cookies()
                for cookie in cookies:
                    # 特别检查Boss直聘的token cookie
                    if cookie['name'] in ['wt2', 'zp_at']:
                        token_info['cookies'] = {cookie['name']: cookie['value']}
                        if not token_info.get('token'):
                            token_info['token'] = cookie['value']
                        logger.info(f"从cookies找到Boss直聘token: {cookie['name']}")
                    elif any(token_key in cookie['name'].lower() for token_key in ['token', 'auth', 'access', 'jwt', 'stoken']):
                        token_info['cookies'] = {cookie['name']: cookie['value']}
                        if not token_info.get('token'):
                            token_info['token'] = cookie['value']
                        logger.info(f"从cookies找到token: {cookie['name']}")
            except Exception as e:
                logger.warning(f"获取cookies失败: {str(e)}")
            
            # 尝试从页面中查找token（通过JavaScript变量）
            try:
                js_tokens = self.page.evaluate("""
                    () => {
                        var tokens = {};
                        // 检查常见的token变量名
                        var tokenVars = ['token', 'accessToken', 'authToken', 'jwt', 'userToken', 'auth_token'];
                        for (var i = 0; i < tokenVars.length; i++) {
                            var varName = tokenVars[i];
                            if (window[varName]) {
                                tokens[varName] = window[varName];
                            }
                        }
                        return tokens;
                    }
                """)
                if js_tokens:
                    token_info['js_variables'] = js_tokens
                    if not token_info.get('token'):
                        # 取第一个找到的token
                        token_info['token'] = list(js_tokens.values())[0]
                    logger.info(f"从JavaScript变量找到token: {list(js_tokens.keys())}")
            except Exception as e:
                logger.warning(f"获取JavaScript变量失败: {str(e)}")
            
            return token_info
            
        except Exception as e:
            logger.error(f"提取token失败: {str(e)}")
            return {}

    def get_login_page_url(self, user_id: int) -> Dict:
        """获取Boss直聘登录页面URL"""
        try:
            # 检查缓存
            cache_key = f"boss_login_url_{user_id}"
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info("使用缓存的登录页面URL")
                return cached_result

            login_url = f"{self.base_url}/web/user/?ka=header-login"

            result = {"success": True, "login_url": login_url, "message": "登录页面URL获取成功"}

            # 缓存结果（10分钟）
            cache.set(cache_key, result, 600)

            return result

        except Exception as e:
            logger.error(f"获取登录页面URL失败: {str(e)}")
            return {"success": False, "message": f"获取登录页面URL失败: {str(e)}"}
    
    def _check_logged_in_elements(self) -> bool:
        """检查页面是否包含登录后的特征元素"""
        try:
            # 检查常见的登录后元素
            logged_in_selectors = [
                # 用户相关元素
                '.user-name', '.geek-name', '.profile-name',
                '.user-avatar', '.geek-avatar', '.profile-avatar',
                
                # 功能按钮
                'button:has-text("立即沟通")', 'button:has-text("投递简历")',
                'button:has-text("收藏")', 'button:has-text("分享")',
                
                # 导航菜单
                '.nav-user', '.user-menu', '.profile-menu',
                
                # 职位相关功能
                '.job-card-wrapper', '.job-list', '.search-form',
                
                # 消息和通知
                '.message-icon', '.notification-icon', '.bell-icon'
            ]
            
            for selector in logged_in_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        logger.info(f"找到登录后元素: {selector}")
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"检查登录后元素失败: {str(e)}")
            return False
    
    def _check_boss_specific_elements(self) -> bool:
        """检查Boss直聘特有的登录后元素"""
        try:
            # Boss直聘特有的登录后元素选择器
            boss_specific_selectors = [
                # Boss直聘特有的用户信息元素
                '.geek-info', '.geek-name', '.geek-avatar',
                '.user-info', '.user-name', '.user-avatar',
                
                # Boss直聘特有的功能按钮
                'button:has-text("立即沟通")', 'button:has-text("投递简历")',
                'button:has-text("收藏职位")', 'button:has-text("分享职位")',
                'button:has-text("筛选")', 'button:has-text("排序")',
                
                # Boss直聘特有的导航元素
                '.nav-geek', '.geek-menu', '.user-menu',
                '.header-user', '.header-geek',
                
                # Boss直聘特有的职位列表元素
                '.job-card', '.job-list-item', '.job-item',
                '.company-info', '.job-title', '.job-salary',
                
                # Boss直聘特有的搜索元素
                '.search-form', '.search-input', '.search-btn',
                '.filter-panel', '.filter-item',
                
                # Boss直聘特有的消息元素
                '.message-count', '.notification-count', '.bell-icon',
                '.chat-icon', '.message-icon',
                
                # Boss直聘特有的个人中心元素
                '.my-resume', '.my-application', '.my-collection',
                '.my-message', '.my-profile', '.my-settings'
            ]
            
            found_elements = 0
            for selector in boss_specific_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        found_elements += 1
                        logger.info(f"找到Boss直聘特有元素: {selector}")
                        # 如果找到多个元素，认为已登录
                        if found_elements >= 2:
                            return True
                except Exception:
                    continue
            
            # 如果找到至少一个Boss直聘特有元素，也认为可能已登录
            if found_elements >= 1:
                logger.info(f"找到 {found_elements} 个Boss直聘特有元素")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"检查Boss直聘特有元素失败: {str(e)}")
            return False
    
    def _fallback_login_check(self) -> bool:
        """备用登录检查方法"""
        try:
            # 检查页面是否包含特定的登录后内容
            page_content = self.page.content().lower()
            
            # 检查是否包含职位列表相关的内容
            job_indicators = [
                '职位列表', 'job list', '招聘信息', '职位详情',
                '公司信息', '工作地点', '薪资范围', '工作经验'
            ]
            
            job_count = sum(1 for indicator in job_indicators if indicator in page_content)
            if job_count >= 3:
                logger.info(f"通过职位相关内容检测到登录状态 (匹配{job_count}个指标)")
                return True
            
            # 检查是否包含用户操作相关的内容
            user_action_indicators = [
                '我的简历', '我的投递', '我的收藏', '我的消息',
                '个人中心', '账户设置', '退出登录'
            ]
            
            action_count = sum(1 for indicator in user_action_indicators if indicator in page_content)
            if action_count >= 2:
                logger.info(f"通过用户操作内容检测到登录状态 (匹配{action_count}个指标)")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"备用登录检查失败: {str(e)}")
            return False
