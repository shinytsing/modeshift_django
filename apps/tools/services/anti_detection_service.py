"""
反检测服务类
专门处理Boss直聘等网站的反爬虫检测
"""
import random
import time
import logging
from typing import Dict, List, Optional, Any
from playwright.sync_api import Page, BrowserContext

logger = logging.getLogger(__name__)


class AntiDetectionService:
    """反检测服务类"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        self.screen_resolutions = [
            '1920x1080', '1366x768', '1440x900', '1536x864', '1280x720',
            '1600x900', '1024x768', '1280x1024', '1680x1050', '1920x1200',
            '2560x1440', '3840x2160', '1440x2560', '2160x1440'
        ]
        
        self.timezones = [
            'Asia/Shanghai', 'Asia/Beijing', 'Asia/Chongqing', 'Asia/Harbin',
            'Asia/Urumqi', 'Asia/Kashgar', 'Asia/Taipei', 'Asia/Hong_Kong',
            'Asia/Tokyo', 'Asia/Seoul', 'America/New_York', 'America/Los_Angeles',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin'
        ]
        
        self.languages = [
            'zh-CN,zh;q=0.9,en;q=0.8',
            'zh-CN,zh;q=0.8,en;q=0.6',
            'en-US,en;q=0.9,zh-CN;q=0.8',
            'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
            'en-GB,en;q=0.9,en-US;q=0.8',
        ]
    
    def setup_browser_anti_detection(self, page: Page) -> None:
        """设置浏览器反检测 - 参考get_jobs项目的实现"""
        try:
            logger.info("🔧 设置浏览器反检测...")
            
            # 隐藏webdriver特征 - 增强版
            page.add_init_script("""
                // 隐藏webdriver特征
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // 隐藏自动化特征
                window.chrome = {
                    runtime: {},
                };
                
                // 删除自动化相关属性
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Reflect;
                
                // 模拟真实的navigator属性
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'MacIntel',
                });
                
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
                
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
                
                // 随机化屏幕分辨率
                Object.defineProperty(screen, 'width', {
                    get: () => 1920,
                });
                
                Object.defineProperty(screen, 'height', {
                    get: () => 1080,
                });
                
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1920,
                });
                
                Object.defineProperty(screen, 'availHeight', {
                    get: () => 1040,
                });
                
                // 模拟真实的WebGL
                const getParameter = WebGLRenderingContext.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter(parameter);
                };
                
                // 隐藏自动化检测相关的方法
                const originalQuery = window.document.querySelector;
                window.document.querySelector = function(selector) {
                    if (selector.includes('webdriver') || selector.includes('automation')) {
                        return null;
                    }
                    return originalQuery.call(this, selector);
                };
                
                // 模拟真实的鼠标事件
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {
                    if (type === 'mousedown' || type === 'mouseup' || type === 'click') {
                        // 添加随机延迟
                        const wrappedListener = function(event) {
                            setTimeout(() => listener.call(this, event), Math.random() * 10);
                        };
                        return originalAddEventListener.call(this, type, wrappedListener, options);
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
                
                // 隐藏自动化相关的错误
                const originalConsoleError = console.error;
                console.error = function(...args) {
                    const message = args.join(' ');
                    if (message.includes('webdriver') || message.includes('automation') || message.includes('selenium')) {
                        return;
                    }
                    return originalConsoleError.apply(this, args);
                };
            """)
            
            # 设置随机User-Agent
            user_agent = random.choice(self.user_agents)
            page.set_extra_http_headers({
                'User-Agent': user_agent
            })
            logger.info(f"✅ 设置User-Agent: {user_agent[:50]}...")
            
            # 设置随机请求头
            headers = self._get_random_headers()
            page.set_extra_http_headers(headers)
            logger.info("✅ 设置随机请求头")
            
            logger.info("✅ 浏览器反检测设置完成")
            
        except Exception as e:
            logger.error(f"❌ 设置浏览器反检测失败: {str(e)}")
    
    def _get_random_headers(self) -> Dict[str, str]:
        """获取随机请求头"""
        language = random.choice(self.languages)
        
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': language,
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'X-Forwarded-For': self._generate_random_ip(),
            'X-Real-IP': self._generate_random_ip(),
            'X-Client-IP': self._generate_random_ip(),
        }
    
    def _generate_random_ip(self) -> str:
        """生成随机IP地址"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> None:
        """随机延迟"""
        delay = random.uniform(min_delay, max_delay)
        logger.info(f"⏱️  随机延迟: {delay:.2f}秒")
        time.sleep(delay)
    
    def simulate_human_behavior(self, page: Page) -> None:
        """模拟人类行为"""
        try:
            logger.info("🖱️  模拟人类行为...")
            
            # 随机鼠标移动
            move_count = random.randint(3, 8)
            for _ in range(move_count):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.3))
            
            # 随机滚动
            scroll_count = random.randint(2, 5)
            for _ in range(scroll_count):
                scroll_delta = random.randint(-300, 300)
                page.mouse.wheel(0, scroll_delta)
                time.sleep(random.uniform(0.5, 1.0))
            
            # 随机点击空白区域
            if random.random() > 0.5:
                x = random.randint(50, 200)
                y = random.randint(50, 200)
                page.mouse.click(x, y)
                time.sleep(random.uniform(0.2, 0.5))
            
            logger.info("✅ 人类行为模拟完成")
            
        except Exception as e:
            logger.error(f"❌ 人类行为模拟失败: {str(e)}")
    
    def simulate_typing(self, page: Page, selector: str, text: str) -> bool:
        """模拟人类打字"""
        try:
            element = page.wait_for_selector(selector, timeout=5000)
            if not element:
                return False
            
            # 点击元素
            element.click()
            time.sleep(random.uniform(0.2, 0.5))
            
            # 清空内容
            element.fill("")
            time.sleep(random.uniform(0.3, 0.7))
            
            # 逐字符输入
            for char in text:
                element.type(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            logger.info(f"✅ 模拟打字完成: {text[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ 模拟打字失败: {str(e)}")
            return False
    
    def simulate_click(self, page: Page, selector: str) -> bool:
        """模拟人类点击"""
        try:
            element = page.wait_for_selector(selector, timeout=5000)
            if not element:
                return False
            
            # 先移动到元素上
            element.hover()
            time.sleep(random.uniform(0.2, 0.5))
            
            # 点击
            element.click()
            time.sleep(random.uniform(0.3, 0.8))
            
            logger.info(f"✅ 模拟点击完成: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 模拟点击失败: {str(e)}")
            return False
    
    def bypass_security_check(self, page: Page) -> Dict[str, Any]:
        """尝试绕过安全检查"""
        try:
            logger.info("🛡️  尝试绕过安全检查...")
            
            # 等待页面加载
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            self.random_delay(2, 4)
            
            # 模拟人类行为
            self.simulate_human_behavior(page)
            
            # 检查是否遇到安全验证
            current_url = page.url
            if "verify-slider" in current_url or "safe/verify" in current_url:
                logger.warning("⚠️  检测到安全验证页面")
                return {
                    "bypassed": False,
                    "reason": "security_verification",
                    "url": current_url,
                    "message": "需要手动完成安全验证"
                }
            
            # 检查页面标题
            title = page.title()
            if "验证" in title or "安全" in title:
                logger.warning("⚠️  页面标题包含验证信息")
                return {
                    "bypassed": False,
                    "reason": "title_verification",
                    "title": title,
                    "message": "页面可能包含验证信息"
                }
            
            logger.info("✅ 成功绕过安全检查")
            return {
                "bypassed": True,
                "url": current_url,
                "title": title,
                "message": "安全检查绕过成功"
            }
            
        except Exception as e:
            logger.error(f"❌ 绕过安全检查失败: {str(e)}")
            return {
                "bypassed": False,
                "reason": "error",
                "error": str(e),
                "message": f"绕过安全检查失败: {str(e)}"
            }
    
    def extract_tokens_from_page(self, page: Page) -> Dict[str, str]:
        """从页面中提取token"""
        try:
            logger.info("🔑 提取页面token...")
            tokens = {}
            
            # 从cookies中提取
            cookies = page.context.cookies()
            for cookie in cookies:
                if cookie['name'] in ['wt2', 'zp_at', '__a', '__c', '__g']:
                    tokens[cookie['name']] = cookie['value']
                    logger.info(f"✅ 找到cookie token: {cookie['name']}")
            
            # 从localStorage中提取
            try:
                local_storage = page.evaluate("() => { return Object.keys(localStorage).reduce((acc, key) => { acc[key] = localStorage.getItem(key); return acc; }, {}); }")
                for key, value in local_storage.items():
                    if any(token_name in key.lower() for token_name in ['wt2', 'zp_at', 'token', 'auth']):
                        tokens[f"localStorage_{key}"] = value
                        logger.info(f"✅ 找到localStorage token: {key}")
            except Exception as e:
                logger.warning(f"⚠️  提取localStorage失败: {str(e)}")
            
            # 从sessionStorage中提取
            try:
                session_storage = page.evaluate("() => { return Object.keys(sessionStorage).reduce((acc, key) => { acc[key] = sessionStorage.getItem(key); return acc; }, {}); }")
                for key, value in session_storage.items():
                    if any(token_name in key.lower() for token_name in ['wt2', 'zp_at', 'token', 'auth']):
                        tokens[f"sessionStorage_{key}"] = value
                        logger.info(f"✅ 找到sessionStorage token: {key}")
            except Exception as e:
                logger.warning(f"⚠️  提取sessionStorage失败: {str(e)}")
            
            logger.info(f"✅ 总共提取到 {len(tokens)} 个token")
            return tokens
            
        except Exception as e:
            logger.error(f"❌ 提取token失败: {str(e)}")
            return {}
    
    def wait_for_element_with_retry(self, page: Page, selector: str, max_retries: int = 3) -> Optional[Any]:
        """带重试的元素等待"""
        for attempt in range(max_retries):
            try:
                element = page.wait_for_selector(selector, timeout=5000)
                if element:
                    return element
            except Exception as e:
                logger.warning(f"⚠️  第 {attempt + 1} 次尝试等待元素失败: {str(e)}")
                if attempt < max_retries - 1:
                    self.random_delay(1, 2)
        
        logger.error(f"❌ 等待元素失败，已重试 {max_retries} 次: {selector}")
        return None
    
    def safe_navigation(self, page: Page, url: str, max_retries: int = 3) -> bool:
        """安全的页面导航"""
        for attempt in range(max_retries):
            try:
                logger.info(f"🌐 第 {attempt + 1} 次尝试访问: {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # 等待页面稳定
                self.random_delay(2, 4)
                
                # 检查是否成功加载
                if page.url == url or url in page.url:
                    logger.info("✅ 页面导航成功")
                    return True
                
            except Exception as e:
                logger.warning(f"⚠️  第 {attempt + 1} 次导航失败: {str(e)}")
                if attempt < max_retries - 1:
                    self.random_delay(3, 5)
        
        logger.error(f"❌ 页面导航失败，已重试 {max_retries} 次: {url}")
        return False
    
    def setup_stealth_mode(self, page: Page) -> None:
        """设置隐身模式 - 参考get_jobs项目的实现"""
        try:
            logger.info("🥷 设置隐身模式...")
            
            # 设置HTTP头
            headers = {
                'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'accept-language': 'zh-CN,zh;q=0.9',
                'referer': 'https://www.zhipin.com/',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin'
            }
            
            page.set_extra_http_headers(headers)
            
            # 注入反检测脚本
            stealth_script = """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Reflect;
                
                // 模拟真实的浏览器环境
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'MacIntel',
                });
                
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
                
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
                
                // 隐藏自动化特征
                window.chrome = {
                    runtime: {},
                };
                
                // 模拟真实的屏幕信息
                Object.defineProperty(screen, 'width', {
                    get: () => 1920,
                });
                
                Object.defineProperty(screen, 'height', {
                    get: () => 1080,
                });
                
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1920,
                });
                
                Object.defineProperty(screen, 'availHeight', {
                    get: () => 1040,
                });
                
                // 模拟真实的WebGL
                const getParameter = WebGLRenderingContext.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter(parameter);
                };
                
                // 隐藏自动化检测相关的方法
                const originalQuery = window.document.querySelector;
                window.document.querySelector = function(selector) {
                    if (selector.includes('webdriver') || selector.includes('automation')) {
                        return null;
                    }
                    return originalQuery.call(this, selector);
                };
                
                // 模拟真实的鼠标事件
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {
                    if (type === 'mousedown' || type === 'mouseup' || type === 'click') {
                        const wrappedListener = function(event) {
                            setTimeout(() => listener.call(this, event), Math.random() * 10);
                        };
                        return originalAddEventListener.call(this, type, wrappedListener, options);
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
                
                // 隐藏自动化相关的错误
                const originalConsoleError = console.error;
                console.error = function(...args) {
                    const message = args.join(' ');
                    if (message.includes('webdriver') || message.includes('automation') || message.includes('selenium')) {
                        return;
                    }
                    return originalConsoleError.apply(this, args);
                };
            """
            
            page.add_init_script(stealth_script)
            logger.info("✅ 隐身模式设置完成")
            
        except Exception as e:
            logger.error(f"❌ 设置隐身模式失败: {str(e)}")
    
    def handle_slider_verification(self, page: Page) -> bool:
        """处理滑块验证 - 参考get_jobs项目的实现"""
        try:
            logger.info("🔍 检查滑块验证...")
            
            # 检查是否存在滑块验证
            slider_container = page.locator('.slider-container')
            if slider_container.count() == 0:
                logger.info("✅ 无滑块验证")
                return True
            
            logger.info("⚠️ 检测到滑块验证，尝试处理...")
            
            # 获取滑块轨道和按钮
            slider_track = page.locator('.slider-track')
            slider_button = page.locator('.slider-button')
            
            if slider_track.count() > 0 and slider_button.count() > 0:
                # 获取滑块轨道宽度
                track_box = slider_track.bounding_box()
                button_box = slider_button.bounding_box()
                
                if track_box and button_box:
                    # 计算需要移动的距离
                    move_distance = track_box['width'] - button_box['width']
                    
                    # 执行拖拽操作
                    slider_button.drag_to(slider_track, target_position={'x': move_distance, 'y': 0})
                    logger.info("✅ 滑块验证处理完成")
                    
                    # 等待验证完成
                    time.sleep(2)
                    return True
            
            logger.warning("⚠️ 滑块验证处理失败")
            return False
            
        except Exception as e:
            logger.warning(f"处理滑块验证失败: {str(e)}")
            return False
    
    def wait_for_slider_verification(self, page: Page) -> bool:
        """等待滑块验证 - 参考get_jobs项目的实现"""
        try:
            logger.info("⏳ 等待滑块验证...")
            
            # 等待滑块验证出现
            slider_container = page.locator('.slider-container')
            slider_container.wait_for(state='visible', timeout=10000)
            
            # 处理滑块验证
            return self.handle_slider_verification(page)
            
        except Exception as e:
            logger.info(f"无滑块验证: {str(e)}")
            return True
