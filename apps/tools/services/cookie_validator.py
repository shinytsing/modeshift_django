"""
Cookie验证器 - 参考get_jobs项目的实现
支持Cookie有效性验证和自动延长过期时间
"""
import logging
import time
import requests
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta

from playwright.sync_api import Page
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class CookieValidator:
    """Cookie验证器 - 支持多种验证方式"""
    
    def __init__(self):
        self.base_url = "https://www.zhipin.com"
        self.test_urls = [
            f"{self.base_url}/web/geek/jobs",
            f"{self.base_url}/web/user/",
            f"{self.base_url}/web/geek/chat"
        ]
        
        # 登录状态指示器
        self.login_indicators = [
            '.user-info',
            '.user-avatar', 
            '.user-name',
            '.job-list-container',
            '.chat-list-container'
        ]
        
        # 未登录指示器
        self.logout_indicators = [
            'a[ka="header-login"]',
            '.login-btn',
            '.login-button',
            '.error-page-login'
        ]
    
    def validate_cookies_playwright(self, page: Page, cookies: Dict[str, str]) -> Dict[str, Any]:
        """使用Playwright验证Cookie有效性"""
        try:
            logger.info("🔍 使用Playwright验证Cookie有效性...")
            
            # 添加cookies到页面上下文
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
            
            page.context.add_cookies(playwright_cookies)
            
            # 测试多个URL
            validation_results = []
            for url in self.test_urls:
                try:
                    logger.info(f"🌐 测试URL: {url}")
                    page.goto(url)
                    page.wait_for_load_state('networkidle', timeout=10000)
                    
                    # 检查登录状态
                    is_logged_in = self._check_login_status_playwright(page)
                    
                    validation_results.append({
                        'url': url,
                        'is_logged_in': is_logged_in,
                        'status': 'success' if is_logged_in else 'failed'
                    })
                    
                    logger.info(f"✅ URL {url} 验证结果: {'已登录' if is_logged_in else '未登录'}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ URL {url} 验证失败: {str(e)}")
                    validation_results.append({
                        'url': url,
                        'is_logged_in': False,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # 计算总体有效性
            success_count = sum(1 for result in validation_results if result['is_logged_in'])
            total_count = len(validation_results)
            is_valid = success_count >= total_count * 0.6  # 60%以上成功认为有效
            
            return {
                'is_valid': is_valid,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'success_count': success_count,
                'total_count': total_count,
                'validation_results': validation_results,
                'method': 'playwright'
            }
            
        except Exception as e:
            logger.error(f"❌ Playwright Cookie验证失败: {str(e)}")
            return {
                'is_valid': False,
                'error': str(e),
                'method': 'playwright'
            }
    
    def validate_cookies_selenium(self, driver: WebDriver, cookies: Dict[str, str]) -> Dict[str, Any]:
        """使用Selenium验证Cookie有效性"""
        try:
            logger.info("🔍 使用Selenium验证Cookie有效性...")
            
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
                    logger.warning(f"⚠️ 添加cookie失败: {name} - {str(e)}")
            
            # 测试多个URL
            validation_results = []
            for url in self.test_urls:
                try:
                    logger.info(f"🌐 测试URL: {url}")
                    driver.get(url)
                    time.sleep(3)
                    
                    # 检查登录状态
                    is_logged_in = self._check_login_status_selenium(driver)
                    
                    validation_results.append({
                        'url': url,
                        'is_logged_in': is_logged_in,
                        'status': 'success' if is_logged_in else 'failed'
                    })
                    
                    logger.info(f"✅ URL {url} 验证结果: {'已登录' if is_logged_in else '未登录'}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ URL {url} 验证失败: {str(e)}")
                    validation_results.append({
                        'url': url,
                        'is_logged_in': False,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # 计算总体有效性
            success_count = sum(1 for result in validation_results if result['is_logged_in'])
            total_count = len(validation_results)
            is_valid = success_count >= total_count * 0.6  # 60%以上成功认为有效
            
            return {
                'is_valid': is_valid,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'success_count': success_count,
                'total_count': total_count,
                'validation_results': validation_results,
                'method': 'selenium'
            }
            
        except Exception as e:
            logger.error(f"❌ Selenium Cookie验证失败: {str(e)}")
            return {
                'is_valid': False,
                'error': str(e),
                'method': 'selenium'
            }
    
    def validate_cookies_http(self, cookies: Dict[str, str]) -> Dict[str, Any]:
        """使用HTTP请求验证Cookie有效性"""
        try:
            logger.info("🔍 使用HTTP请求验证Cookie有效性...")
            
            # 构建cookie字符串
            cookie_string = "; ".join([f"{name}={value}" for name, value in cookies.items()])
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie': cookie_string
            }
            
            # 测试多个URL
            validation_results = []
            for url in self.test_urls:
                try:
                    logger.info(f"🌐 测试URL: {url}")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    # 检查响应状态
                    if response.status_code == 200:
                        # 检查响应内容中的登录指示器
                        content = response.text
                        is_logged_in = self._check_login_status_http(content)
                        
                        validation_results.append({
                            'url': url,
                            'is_logged_in': is_logged_in,
                            'status_code': response.status_code,
                            'status': 'success' if is_logged_in else 'failed'
                        })
                        
                        logger.info(f"✅ URL {url} 验证结果: {'已登录' if is_logged_in else '未登录'}")
                    else:
                        logger.warning(f"⚠️ URL {url} 返回状态码: {response.status_code}")
                        validation_results.append({
                            'url': url,
                            'is_logged_in': False,
                            'status_code': response.status_code,
                            'status': 'error'
                        })
                    
                except Exception as e:
                    logger.warning(f"⚠️ URL {url} 验证失败: {str(e)}")
                    validation_results.append({
                        'url': url,
                        'is_logged_in': False,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # 计算总体有效性
            success_count = sum(1 for result in validation_results if result['is_logged_in'])
            total_count = len(validation_results)
            is_valid = success_count >= total_count * 0.6  # 60%以上成功认为有效
            
            return {
                'is_valid': is_valid,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'success_count': success_count,
                'total_count': total_count,
                'validation_results': validation_results,
                'method': 'http'
            }
            
        except Exception as e:
            logger.error(f"❌ HTTP Cookie验证失败: {str(e)}")
            return {
                'is_valid': False,
                'error': str(e),
                'method': 'http'
            }
    
    def _check_login_status_playwright(self, page: Page) -> bool:
        """检查Playwright页面登录状态"""
        try:
            # 检查登录指示器
            for indicator in self.login_indicators:
                try:
                    element = page.locator(indicator)
                    if element.count() > 0 and element.is_visible():
                        return True
                except Exception:
                    continue
            
            # 检查未登录指示器
            for indicator in self.logout_indicators:
                try:
                    element = page.locator(indicator)
                    if element.count() > 0 and element.is_visible():
                        return False
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"检查Playwright登录状态失败: {str(e)}")
            return False
    
    def _check_login_status_selenium(self, driver: WebDriver) -> bool:
        """检查Selenium页面登录状态"""
        try:
            from selenium.webdriver.common.by import By
            
            # 检查登录指示器
            for indicator in self.login_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and elements[0].is_displayed():
                        return True
                except Exception:
                    continue
            
            # 检查未登录指示器
            for indicator in self.logout_indicators:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements and elements[0].is_displayed():
                        return False
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"检查Selenium登录状态失败: {str(e)}")
            return False
    
    def _check_login_status_http(self, content: str) -> bool:
        """检查HTTP响应内容中的登录状态"""
        try:
            # 检查登录指示器
            login_keywords = [
                'user-info',
                'user-avatar',
                'user-name',
                'job-list-container',
                'chat-list-container'
            ]
            
            for keyword in login_keywords:
                if keyword in content:
                    return True
            
            # 检查未登录指示器
            logout_keywords = [
                'header-login',
                'login-btn',
                'login-button',
                'error-page-login'
            ]
            
            for keyword in logout_keywords:
                if keyword in content:
                    return False
            
            return False
            
        except Exception as e:
            logger.warning(f"检查HTTP登录状态失败: {str(e)}")
            return False
    
    def auto_extend_cookie_expiry(self, cookie_file_path: str, days: int = 7) -> bool:
        """自动延长Cookie过期时间 - 参考get_jobs项目的实现"""
        try:
            logger.info(f"🔄 自动延长Cookie过期时间{days}天...")
            
            import json
            from pathlib import Path
            
            cookie_file = Path(cookie_file_path)
            if not cookie_file.exists():
                logger.warning("❌ Cookie文件不存在")
                return False
            
            # 读取cookie文件
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            # 延长过期时间
            current_time = int(time.time())
            new_expires_at = current_time + (days * 24 * 3600)
            
            cookie_data['expires_at'] = new_expires_at
            cookie_data['extended_at'] = current_time
            cookie_data['extended_count'] = cookie_data.get('extended_count', 0) + 1
            
            # 保存更新后的cookie文件
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookie_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 已延长Cookie过期时间{days}天")
            return True
            
        except Exception as e:
            logger.error(f"❌ 延长Cookie过期时间失败: {str(e)}")
            return False
    
    def get_cookie_health_status(self, cookie_file_path: str) -> Dict[str, Any]:
        """获取Cookie健康状态"""
        try:
            import json
            from pathlib import Path
            
            cookie_file = Path(cookie_file_path)
            if not cookie_file.exists():
                return {
                    'file_exists': False,
                    'status': 'not_found',
                    'message': 'Cookie文件不存在'
                }
            
            # 读取cookie文件
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            current_time = int(time.time())
            expires_at = cookie_data.get('expires_at', 0)
            timestamp = cookie_data.get('timestamp', 0)
            
            # 计算剩余时间
            remaining_seconds = expires_at - current_time
            remaining_days = remaining_seconds / (24 * 3600)
            
            # 判断健康状态
            if remaining_seconds <= 0:
                status = 'expired'
                message = 'Cookie已过期'
            elif remaining_days <= 1:
                status = 'critical'
                message = f'Cookie将在{remaining_days:.1f}天内过期'
            elif remaining_days <= 3:
                status = 'warning'
                message = f'Cookie将在{remaining_days:.1f}天内过期'
            else:
                status = 'healthy'
                message = f'Cookie健康，剩余{remaining_days:.1f}天'
            
            return {
                'file_exists': True,
                'status': status,
                'message': message,
                'remaining_days': remaining_days,
                'expires_at': expires_at,
                'timestamp': timestamp,
                'cookie_count': len(cookie_data.get('cookies', {})),
                'extended_count': cookie_data.get('extended_count', 0),
                'version': cookie_data.get('version', '1.0')
            }
            
        except Exception as e:
            logger.error(f"❌ 获取Cookie健康状态失败: {str(e)}")
            return {
                'file_exists': False,
                'status': 'error',
                'message': f'获取健康状态失败: {str(e)}'
            }
    
    def validate_and_extend_cookies(self, cookie_file_path: str, validation_method: str = 'http') -> Dict[str, Any]:
        """验证并自动延长Cookie - 参考get_jobs项目的实现"""
        try:
            logger.info("🔍 验证并自动延长Cookie...")
            
            # 获取Cookie健康状态
            health_status = self.get_cookie_health_status(cookie_file_path)
            
            if not health_status['file_exists']:
                return {
                    'success': False,
                    'message': 'Cookie文件不存在',
                    'action': 'create_new'
                }
            
            # 如果Cookie已过期，需要重新登录
            if health_status['status'] == 'expired':
                return {
                    'success': False,
                    'message': 'Cookie已过期，需要重新登录',
                    'action': 're_login',
                    'health_status': health_status
                }
            
            # 读取Cookie进行验证
            import json
            with open(cookie_file_path, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            cookies = cookie_data.get('cookies', {})
            if not cookies:
                return {
                    'success': False,
                    'message': 'Cookie文件中没有有效的cookies',
                    'action': 're_login'
                }
            
            # 验证Cookie有效性
            if validation_method == 'http':
                validation_result = self.validate_cookies_http(cookies)
            else:
                # 默认使用HTTP验证
                validation_result = self.validate_cookies_http(cookies)
            
            if validation_result['is_valid']:
                # Cookie有效，检查是否需要延长
                if health_status['remaining_days'] <= 3:
                    # 自动延长过期时间
                    extend_success = self.auto_extend_cookie_expiry(cookie_file_path, 7)
                    if extend_success:
                        return {
                            'success': True,
                            'message': 'Cookie有效且已自动延长过期时间',
                            'action': 'extended',
                            'validation_result': validation_result,
                            'health_status': health_status
                        }
                    else:
                        return {
                            'success': True,
                            'message': 'Cookie有效但延长过期时间失败',
                            'action': 'valid',
                            'validation_result': validation_result,
                            'health_status': health_status
                        }
                else:
                    return {
                        'success': True,
                        'message': 'Cookie有效且无需延长',
                        'action': 'valid',
                        'validation_result': validation_result,
                        'health_status': health_status
                    }
            else:
                # Cookie无效，需要重新登录
                return {
                    'success': False,
                    'message': 'Cookie验证失败，需要重新登录',
                    'action': 're_login',
                    'validation_result': validation_result,
                    'health_status': health_status
                }
            
        except Exception as e:
            logger.error(f"❌ 验证并延长Cookie失败: {str(e)}")
            return {
                'success': False,
                'message': f'验证并延长Cookie失败: {str(e)}',
                'action': 'error'
            }


# 全局Cookie验证器实例
cookie_validator = CookieValidator()
