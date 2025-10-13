"""
Boss直聘登录管理器 - 参考get_jobs项目的实现
支持扫码登录、Cookie验证、登录状态检查等功能
"""
import logging
import time
import os
from typing import Dict, Optional, Any
from pathlib import Path

from playwright.sync_api import Page, Browser, BrowserContext
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .cookie_manager import CookieManager
from .token_extractor import TokenExtractor
from .anti_detection_service import AntiDetectionService

logger = logging.getLogger(__name__)


class BossLoginManager:
    """Boss直聘登录管理器"""
    
    def __init__(self, user_id: Optional[int] = None):
        self.user_id = user_id
        self.cookie_manager = CookieManager(user_id)
        self.token_extractor = TokenExtractor()
        self.anti_detection_service = AntiDetectionService()
        
        # Boss直聘相关URL
        self.base_url = "https://www.zhipin.com"
        self.login_url = f"{self.base_url}/web/user/?ka=header-login"
        self.home_url = f"{self.base_url}/web/geek/jobs"
        
        # 登录相关元素选择器
        self.login_selectors = {
            'login_btn': 'a[ka="header-login"]',
            'scan_switch': '.login-switch-btn',
            'qr_code': '.qr-code img',
            'qr_code_container': '.qr-code',
            'login_success_indicator': '.job-list-container',
            'user_info': '.user-info',
            'user_avatar': '.user-avatar',
            'user_name': '.user-name',
            'error_page_login': '.error-page-login'
        }
        
        # 滑块验证相关选择器
        self.slider_selectors = {
            'slider_container': '.slider-container',
            'slider_track': '.slider-track',
            'slider_button': '.slider-button',
            'slider_text': '.slider-text'
        }
    
    def check_login_status_playwright(self, page: Page) -> Dict[str, Any]:
        """检查Playwright登录状态"""
        try:
            logger.info("🔍 检查Playwright登录状态...")
            
            # 访问主页检查登录状态
            page.goto(self.home_url)
            page.wait_for_load_state('networkidle')
            
            # 检查登录指示器
            login_indicators = [
                self.login_selectors['user_info'],
                self.login_selectors['user_avatar'], 
                self.login_selectors['user_name']
            ]
            
            is_logged_in = False
            for indicator in login_indicators:
                try:
                    element = page.locator(indicator)
                    if element.count() > 0 and element.is_visible():
                        is_logged_in = True
                        logger.info(f"✅ 找到登录指示器: {indicator}")
                        break
                except Exception:
                    continue
            
            # 检查是否需要登录
            if not is_logged_in:
                try:
                    login_btn = page.locator(self.login_selectors['login_btn'])
                    if login_btn.count() > 0 and login_btn.is_visible():
                        logger.info("❌ 用户未登录")
                        return {
                            'success': True,
                            'is_logged_in': False,
                            'message': '用户未登录'
                        }
                except Exception:
                    pass
            
            # 如果已登录，提取token信息
            if is_logged_in:
                token_info = self.token_extractor.extract_from_playwright(page)
                return {
                    'success': True,
                    'is_logged_in': True,
                    'message': '用户已登录',
                    'token_info': token_info
                }
            
            return {
                'success': True,
                'is_logged_in': False,
                'message': '无法确定登录状态'
            }
            
        except Exception as e:
            logger.error(f"检查Playwright登录状态失败: {str(e)}")
            return {
                'success': False,
                'is_logged_in': False,
                'message': f'检查登录状态失败: {str(e)}'
            }
    
    def check_login_status_selenium(self, driver: WebDriver) -> Dict[str, Any]:
        """检查Selenium登录状态"""
        try:
            logger.info("🔍 检查Selenium登录状态...")
            
            # 访问主页检查登录状态
            driver.get(self.home_url)
            time.sleep(3)
            
            # 检查登录指示器
            login_indicators = [
                self.login_selectors['user_info'],
                self.login_selectors['user_avatar'],
                self.login_selectors['user_name']
            ]
            
            is_logged_in = False
            for indicator in login_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and elements[0].is_displayed():
                        is_logged_in = True
                        logger.info(f"✅ 找到登录指示器: {indicator}")
                        break
                except Exception:
                    continue
            
            # 检查是否需要登录
            if not is_logged_in:
                try:
                    login_btn = driver.find_elements(By.CSS_SELECTOR, self.login_selectors['login_btn'])
                    if login_btn and login_btn[0].is_displayed():
                        logger.info("❌ 用户未登录")
                        return {
                            'success': True,
                            'is_logged_in': False,
                            'message': '用户未登录'
                        }
                except Exception:
                    pass
            
            # 如果已登录，提取token信息
            if is_logged_in:
                token_info = self.token_extractor.extract_from_selenium(driver)
                return {
                    'success': True,
                    'is_logged_in': True,
                    'message': '用户已登录',
                    'token_info': token_info
                }
            
            return {
                'success': True,
                'is_logged_in': False,
                'message': '无法确定登录状态'
            }
            
        except Exception as e:
            logger.error(f"检查Selenium登录状态失败: {str(e)}")
            return {
                'success': False,
                'is_logged_in': False,
                'message': f'检查登录状态失败: {str(e)}'
            }
    
    def scan_login_playwright(self, page: Page, timeout: int = 600) -> Dict[str, Any]:
        """Playwright扫码登录流程"""
        try:
            logger.info("🔐 开始Playwright扫码登录流程...")
            
            # 访问登录页面
            page.goto(self.login_url)
            page.wait_for_load_state('networkidle')
            
            # 检查是否已经登录
            login_status = self.check_login_status_playwright(page)
            if login_status.get('is_logged_in'):
                logger.info("✅ 用户已经登录")
                return {
                    'success': True,
                    'message': '用户已经登录',
                    'token_info': login_status.get('token_info', {})
                }
            
            # 切换到二维码登录
            try:
                scan_button = page.locator(self.login_selectors['scan_switch'])
                if scan_button.count() > 0:
                    scan_button.click()
                    logger.info("✅ 已切换到二维码登录")
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"切换二维码登录失败: {str(e)}")
            
            # 等待二维码加载
            try:
                qr_code = page.locator(self.login_selectors['qr_code'])
                qr_code.wait_for(state='visible', timeout=10000)
                logger.info("✅ 二维码已加载")
            except Exception as e:
                logger.error(f"二维码加载失败: {str(e)}")
                return {
                    'success': False,
                    'message': f'二维码加载失败: {str(e)}'
                }
            
            # 等待用户扫码登录
            logger.info("⏳ 等待用户扫码登录...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # 检查是否登录成功
                    success_indicator = page.locator(self.login_selectors['login_success_indicator'])
                    if success_indicator.count() > 0 and success_indicator.is_visible():
                        logger.info("✅ 扫码登录成功！")
                        
                        # 提取token信息
                        token_info = self.token_extractor.extract_from_playwright(page)
                        
                        # 保存cookies
                        cookies = page.context.cookies()
                        cookie_dict = {c['name']: c['value'] for c in cookies if '.zhipin.com' in c.get('domain', '')}
                        self.cookie_manager.save_cookies(cookie_dict, token_info)
                        
                        return {
                            'success': True,
                            'message': '扫码登录成功',
                            'token_info': token_info
                        }
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"检查登录状态时异常: {str(e)}")
                    time.sleep(2)
            
            logger.error("❌ 扫码登录超时")
            return {
                'success': False,
                'message': '扫码登录超时'
            }
            
        except Exception as e:
            logger.error(f"Playwright扫码登录失败: {str(e)}")
            return {
                'success': False,
                'message': f'扫码登录失败: {str(e)}'
            }
    
    def scan_login_selenium(self, driver: WebDriver, timeout: int = 600) -> Dict[str, Any]:
        """Selenium扫码登录流程"""
        try:
            logger.info("🔐 开始Selenium扫码登录流程...")
            
            # 访问登录页面
            driver.get(self.login_url)
            time.sleep(3)
            
            # 检查是否已经登录
            login_status = self.check_login_status_selenium(driver)
            if login_status.get('is_logged_in'):
                logger.info("✅ 用户已经登录")
                return {
                    'success': True,
                    'message': '用户已经登录',
                    'token_info': login_status.get('token_info', {})
                }
            
            # 切换到二维码登录
            try:
                scan_button = driver.find_elements(By.CSS_SELECTOR, self.login_selectors['scan_switch'])
                if scan_button:
                    scan_button[0].click()
                    logger.info("✅ 已切换到二维码登录")
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"切换二维码登录失败: {str(e)}")
            
            # 等待二维码加载
            try:
                wait = WebDriverWait(driver, 10)
                qr_code = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.login_selectors['qr_code'])))
                logger.info("✅ 二维码已加载")
            except Exception as e:
                logger.error(f"二维码加载失败: {str(e)}")
                return {
                    'success': False,
                    'message': f'二维码加载失败: {str(e)}'
                }
            
            # 等待用户扫码登录
            logger.info("⏳ 等待用户扫码登录...")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # 检查是否登录成功
                    success_indicators = driver.find_elements(By.CSS_SELECTOR, self.login_selectors['login_success_indicator'])
                    if success_indicators and success_indicators[0].is_displayed():
                        logger.info("✅ 扫码登录成功！")
                        
                        # 提取token信息
                        token_info = self.token_extractor.extract_from_selenium(driver)
                        
                        # 保存cookies
                        cookies = driver.get_cookies()
                        cookie_dict = {c['name']: c['value'] for c in cookies}
                        self.cookie_manager.save_cookies(cookie_dict, token_info)
                        
                        return {
                            'success': True,
                            'message': '扫码登录成功',
                            'token_info': token_info
                        }
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"检查登录状态时异常: {str(e)}")
                    time.sleep(2)
            
            logger.error("❌ 扫码登录超时")
            return {
                'success': False,
                'message': '扫码登录超时'
            }
            
        except Exception as e:
            logger.error(f"Selenium扫码登录失败: {str(e)}")
            return {
                'success': False,
                'message': f'扫码登录失败: {str(e)}'
            }
    
    def handle_slider_verification_playwright(self, page: Page) -> bool:
        """处理Playwright滑块验证"""
        try:
            logger.info("🔍 检查滑块验证...")
            
            # 检查是否存在滑块验证
            slider_container = page.locator(self.slider_selectors['slider_container'])
            if slider_container.count() == 0:
                logger.info("✅ 无滑块验证")
                return True
            
            logger.info("⚠️ 检测到滑块验证，尝试处理...")
            
            # 获取滑块轨道和按钮
            slider_track = page.locator(self.slider_selectors['slider_track'])
            slider_button = page.locator(self.slider_selectors['slider_button'])
            
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
    
    def handle_slider_verification_selenium(self, driver: WebDriver) -> bool:
        """处理Selenium滑块验证"""
        try:
            logger.info("🔍 检查滑块验证...")
            
            # 检查是否存在滑块验证
            slider_elements = driver.find_elements(By.CSS_SELECTOR, self.slider_selectors['slider_container'])
            if not slider_elements:
                logger.info("✅ 无滑块验证")
                return True
            
            logger.info("⚠️ 检测到滑块验证，尝试处理...")
            
            # 获取滑块轨道和按钮
            slider_track = driver.find_elements(By.CSS_SELECTOR, self.slider_selectors['slider_track'])
            slider_button = driver.find_elements(By.CSS_SELECTOR, self.slider_selectors['slider_button'])
            
            if slider_track and slider_button:
                from selenium.webdriver.common.action_chains import ActionChains
                
                # 获取滑块轨道宽度
                track_width = slider_track[0].size['width']
                button_width = slider_button[0].size['width']
                
                # 计算需要移动的距离
                move_distance = track_width - button_width
                
                # 执行拖拽操作
                action_chains = ActionChains(driver)
                action_chains.click_and_hold(slider_button[0]).move_by_offset(move_distance, 0).release().perform()
                
                logger.info("✅ 滑块验证处理完成")
                
                # 等待验证完成
                time.sleep(2)
                return True
            
            logger.warning("⚠️ 滑块验证处理失败")
            return False
            
        except Exception as e:
            logger.warning(f"处理滑块验证失败: {str(e)}")
            return False
    
    def load_saved_cookies_playwright(self, page: Page) -> bool:
        """加载已保存的Playwright cookies"""
        try:
            cookies = self.cookie_manager.load_cookies()
            if not cookies:
                logger.info("❌ 没有可用的cookies")
                return False
            
            # 转换为Playwright格式
            playwright_cookies = []
            for name, value in cookies.items():
                playwright_cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.zhipin.com',
                    'path': '/',
                    'secure': True,
                    'httpOnly': False
                })
            
            # 添加cookies到页面上下文
            page.context.add_cookies(playwright_cookies)
            logger.info(f"✅ 已加载{len(cookies)}个cookies")
            
            # 刷新页面
            page.reload()
            page.wait_for_load_state('networkidle')
            
            return True
            
        except Exception as e:
            logger.error(f"加载Playwright cookies失败: {str(e)}")
            return False
    
    def load_saved_cookies_selenium(self, driver: WebDriver) -> bool:
        """加载已保存的Selenium cookies"""
        try:
            cookies = self.cookie_manager.load_cookies()
            if not cookies:
                logger.info("❌ 没有可用的cookies")
                return False
            
            # 清除现有cookies
            driver.delete_all_cookies()
            
            # 添加cookies
            for name, value in cookies.items():
                try:
                    driver.add_cookie({
                        'name': name,
                        'value': value,
                        'domain': '.zhipin.com',
                        'path': '/',
                        'secure': True,
                        'httpOnly': False
                    })
                except Exception as e:
                    logger.warning(f"添加cookie失败: {name} - {str(e)}")
            
            logger.info(f"✅ 已加载{len(cookies)}个cookies")
            
            # 刷新页面
            driver.refresh()
            time.sleep(3)
            
            return True
            
        except Exception as e:
            logger.error(f"加载Selenium cookies失败: {str(e)}")
            return False
    
    def get_login_summary(self) -> Dict[str, Any]:
        """获取登录状态摘要"""
        cookie_info = self.cookie_manager.get_cookie_info()
        
        return {
            'user_id': self.user_id,
            'cookie_file_exists': cookie_info.get('file_exists', False),
            'cookie_count': cookie_info.get('cookie_count', 0),
            'has_token': cookie_info.get('has_token', False),
            'token_source': cookie_info.get('token_source'),
            'is_expired': cookie_info.get('is_expired', True),
            'expires_at': cookie_info.get('expires_at'),
            'version': cookie_info.get('version', '1.0')
        }


# 全局登录管理器实例
login_manager = BossLoginManager()
