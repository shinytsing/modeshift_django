"""
安全验证绕过服务
提供多种方法绕过Boss直聘的安全验证
"""
import logging
import time
import threading
import random
from typing import Dict, List
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

class SecurityBypassService:
    """安全验证绕过服务"""
    
    def __init__(self):
        self.bypass_methods = [
            self._method_slider_bypass,
            self._method_click_bypass,
            self._method_refresh_bypass,
            self._method_ua_bypass,
            self._method_js_bypass,
            self._method_wait_bypass
        ]
    
    def bypass_security_verification(self, page: Page) -> Dict:
        """绕过安全验证页面 - 顺序处理避免线程问题"""
        try:
            logger.info("🔍 开始绕过安全验证页面...")
            
            # 检查是否是安全验证页面
            current_url = page.url
            if not self._is_security_page(current_url):
                return {"bypassed": True, "message": "无需绕过安全验证"}
            
            logger.info("检测到安全验证页面，尝试多种绕过方法...")
            
            # 顺序尝试各种绕过方法，避免多线程问题
            results = []
            
            for i, method in enumerate(self.bypass_methods):
                try:
                    logger.info(f"🔄 尝试绕过方法 {i + 1}: {method.__name__}")
                    result = method(page)
                    results.append(result)
                    
                    if result.get("success"):
                        logger.info(f"✅ 绕过方法 {i + 1} 成功")
                        # 检查是否已经绕过
                        time.sleep(1)
                        current_url = page.url
                        if not self._is_security_page(current_url):
                            logger.info("✅ 成功绕过安全验证")
                            return {"bypassed": True, "message": "成功绕过安全验证", "methods_used": i + 1}
                    else:
                        logger.debug(f"❌ 绕过方法 {i + 1} 失败: {result.get('error', '未知错误')}")
                    
                    # 短暂等待，避免操作过快
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"绕过方法 {i + 1} 异常: {str(e)}")
                    results.append({"success": False, "error": str(e)})
                    continue
            
            # 所有方法都尝试后，检查最终结果
            time.sleep(1)
            current_url = page.url
            
            if not self._is_security_page(current_url):
                logger.info("✅ 成功绕过安全验证")
                return {"bypassed": True, "message": "成功绕过安全验证", "methods_used": len(results)}
            else:
                logger.warning("❌ 未能绕过安全验证")
                return {"bypassed": False, "reason": "security_verification", "message": "需要手动完成安全验证"}
                
        except Exception as e:
            logger.error(f"绕过安全验证失败: {str(e)}")
            return {"bypassed": False, "message": f"绕过安全验证失败: {str(e)}"}
    
    
    def _is_security_page(self, url: str) -> bool:
        """检查是否是安全验证页面"""
        security_indicators = [
            'verify-slider', 'safe/verify', 'security', 'captcha',
            'verification', 'challenge', 'verify'
        ]
        return any(indicator in url.lower() for indicator in security_indicators)
    
    def _method_slider_bypass(self, page: Page) -> Dict:
        """方法1: 滑块验证绕过"""
        try:
            logger.info("🎯 尝试滑块验证绕过...")
            
            # 等待页面加载
            page.wait_for_load_state("networkidle", timeout=5000)
            
            # 查找滑块元素
            slider_selectors = [
                ".slider-move", ".slider-button", "[class*='slider']",
                ".captcha-slider", "#slider", ".verify-slider",
                "[class*='captcha']", "[class*='verify']"
            ]
            
            for selector in slider_selectors:
                try:
                    slider = page.locator(selector)
                    if slider.is_visible():
                        logger.info(f"找到滑块元素: {selector}")
                        
                        # 模拟人类滑动行为
                        box = slider.bounding_box()
                        if box:
                            # 计算滑动距离
                            start_x = box['x'] + box['width'] / 2
                            start_y = box['y'] + box['height'] / 2
                            end_x = start_x + box['width'] - 10
                            
                            # 模拟人类滑动
                            page.mouse.move(start_x, start_y)
                            page.mouse.down()
                            time.sleep(0.1)
                            
                            # 分段滑动，模拟人类行为
                            steps = 20
                            for i in range(steps):
                                progress = (i + 1) / steps
                                current_x = start_x + (end_x - start_x) * progress
                                
                                # 添加随机抖动和速度变化
                                jitter_x = random.uniform(-2, 2)
                                jitter_y = random.uniform(-1, 1)
                                speed_factor = random.uniform(0.8, 1.2)
                                
                                page.mouse.move(
                                    current_x + jitter_x, 
                                    start_y + jitter_y
                                )
                                time.sleep(0.05 * speed_factor)
                            
                            page.mouse.up()
                            logger.info("✅ 完成滑块滑动")
                            time.sleep(2)
                            return {"success": True, "method": "slider"}
                except Exception as e:
                    logger.debug(f"滑块选择器 {selector} 失败: {str(e)}")
                    continue
            
            return {"success": False, "method": "slider", "error": "未找到滑块元素"}
            
        except Exception as e:
            return {"success": False, "method": "slider", "error": str(e)}
    
    def _method_click_bypass(self, page: Page) -> Dict:
        """方法2: 点击验证绕过"""
        try:
            logger.info("🎯 尝试点击验证绕过...")
            
            # 查找点击按钮
            click_selectors = [
                "button:has-text('验证')", "button:has-text('点击验证')",
                ".verify-btn", "#verify-btn", "[class*='verify']",
                "button[class*='btn']", ".btn-verify", "#btn-verify",
                "input[type='button']", "a[class*='verify']"
            ]
            
            for selector in click_selectors:
                try:
                    element = page.locator(selector)
                    if element.is_visible():
                        logger.info(f"找到点击元素: {selector}")
                        element.click()
                        time.sleep(1)
                        return {"success": True, "method": "click"}
                except Exception as e:
                    logger.debug(f"点击选择器 {selector} 失败: {str(e)}")
                    continue
            
            return {"success": False, "method": "click", "error": "未找到点击元素"}
            
        except Exception as e:
            return {"success": False, "method": "click", "error": str(e)}
    
    def _method_refresh_bypass(self, page: Page) -> Dict:
        """方法3: 刷新页面绕过"""
        try:
            logger.info("🎯 尝试刷新页面绕过...")
            
            page.reload()
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            
            return {"success": True, "method": "refresh"}
            
        except Exception as e:
            return {"success": False, "method": "refresh", "error": str(e)}
    
    def _method_ua_bypass(self, page: Page) -> Dict:
        """方法4: User-Agent绕过"""
        try:
            logger.info("🎯 尝试User-Agent绕过...")
            
            # 修改User-Agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            page.reload()
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            
            return {"success": True, "method": "ua"}
            
        except Exception as e:
            return {"success": False, "method": "ua", "error": str(e)}
    
    def _method_js_bypass(self, page: Page) -> Dict:
        """方法5: JavaScript绕过"""
        try:
            logger.info("🎯 尝试JavaScript绕过...")
            
            # 注入反检测脚本
            page.add_init_script("""
                // 隐藏webdriver特征
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // 模拟真实浏览器
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en'],
                });
                
                // 隐藏自动化特征
                window.chrome = {
                    runtime: {},
                };
                
                // 模拟真实用户行为
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' }),
                    }),
                });
            """)
            
            page.reload()
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            
            return {"success": True, "method": "js"}
            
        except Exception as e:
            return {"success": False, "method": "js", "error": str(e)}
    
    def _method_wait_bypass(self, page: Page) -> Dict:
        """方法6: 等待绕过"""
        try:
            logger.info("🎯 尝试等待绕过...")
            
            # 等待页面自动验证
            time.sleep(5)
            
            # 尝试键盘操作
            page.keyboard.press("Tab")
            time.sleep(0.5)
            page.keyboard.press("Enter")
            time.sleep(1)
            
            return {"success": True, "method": "wait"}
            
        except Exception as e:
            return {"success": False, "method": "wait", "error": str(e)}
