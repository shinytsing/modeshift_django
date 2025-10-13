"""
Token提取器 - 参考get_jobs项目的实现
支持从localStorage、cookies、页面变量中提取Boss直聘token
"""
import logging
import re
import json
from typing import Dict, Optional, Any, List
from playwright.sync_api import Page
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class TokenExtractor:
    """Token提取器 - 支持多种来源的token提取"""
    
    def __init__(self):
        # Boss直聘相关的token字段名
        self.token_fields = [
            'wt2', 'zp_at', 'zp_token', 'boss_token', 'zhipin_token', 
            'geek_token', '__zp_stoken__', 'access_token', 'auth_token',
            'token', 'jwt', 'session_token', 'user_token'
        ]
        
        # localStorage中的token键名
        self.local_storage_keys = [
            'token', 'access_token', 'auth_token', '__zp_stoken__',
            'wt2', 'zp_at', 'zp_token', 'boss_token', 'zhipin_token',
            'geek_token', 'user_token', 'session_token'
        ]
        
        # sessionStorage中的token键名
        self.session_storage_keys = [
            'token', 'access_token', 'auth_token', '__zp_stoken__',
            'wt2', 'zp_at', 'zp_token', 'boss_token', 'zhipin_token'
        ]
        
        # 页面JavaScript变量中的token字段
        self.js_variable_patterns = [
            r'window\.token\s*=\s*["\']([^"\']+)["\']',
            r'window\.accessToken\s*=\s*["\']([^"\']+)["\']',
            r'window\.authToken\s*=\s*["\']([^"\']+)["\']',
            r'window\.zpToken\s*=\s*["\']([^"\']+)["\']',
            r'window\.bossToken\s*=\s*["\']([^"\']+)["\']',
            r'window\.geekToken\s*=\s*["\']([^"\']+)["\']',
            r'window\.wt2\s*=\s*["\']([^"\']+)["\']',
            r'window\.zp_at\s*=\s*["\']([^"\']+)["\']',
            r'window\.__zp_stoken__\s*=\s*["\']([^"\']+)["\']',
        ]
    
    def extract_from_playwright(self, page: Page) -> Dict[str, Any]:
        """从Playwright页面提取token"""
        token_info = {
            'token': None,
            'source': None,
            'cookies': {},
            'local_storage': {},
            'session_storage': {},
            'js_variables': {},
            'extracted_at': None
        }
        
        try:
            # 1. 从cookies提取token
            logger.info("🔍 从cookies提取token...")
            cookies = page.context.cookies()
            cookie_tokens = self._extract_from_cookies(cookies)
            if cookie_tokens:
                token_info.update(cookie_tokens)
                token_info['cookies'] = {c['name']: c['value'] for c in cookies if '.zhipin.com' in c.get('domain', '')}
            
            # 2. 从localStorage提取token
            logger.info("🔍 从localStorage提取token...")
            local_storage_tokens = self._extract_from_local_storage(page)
            if local_storage_tokens and not token_info.get('token'):
                token_info.update(local_storage_tokens)
            
            # 3. 从sessionStorage提取token
            logger.info("🔍 从sessionStorage提取token...")
            session_storage_tokens = self._extract_from_session_storage(page)
            if session_storage_tokens and not token_info.get('token'):
                token_info.update(session_storage_tokens)
            
            # 4. 从页面JavaScript变量提取token
            logger.info("🔍 从页面JavaScript变量提取token...")
            js_tokens = self._extract_from_js_variables(page)
            if js_tokens and not token_info.get('token'):
                token_info.update(js_tokens)
            
            # 5. 从页面内容中搜索token模式
            logger.info("🔍 从页面内容搜索token模式...")
            content_tokens = self._extract_from_page_content(page)
            if content_tokens and not token_info.get('token'):
                token_info.update(content_tokens)
            
            logger.info(f"✅ Token提取完成: {token_info.get('token', 'None')[:20]}...")
            return token_info
            
        except Exception as e:
            logger.error(f"从Playwright页面提取token失败: {str(e)}")
            return token_info
    
    def extract_from_selenium(self, driver: WebDriver) -> Dict[str, Any]:
        """从Selenium WebDriver提取token"""
        token_info = {
            'token': None,
            'source': None,
            'cookies': {},
            'local_storage': {},
            'session_storage': {},
            'js_variables': {},
            'extracted_at': None
        }
        
        try:
            # 1. 从cookies提取token
            logger.info("🔍 从cookies提取token...")
            cookies = driver.get_cookies()
            cookie_tokens = self._extract_from_selenium_cookies(cookies)
            if cookie_tokens:
                token_info.update(cookie_tokens)
                token_info['cookies'] = {c['name']: c['value'] for c in cookies}
            
            # 2. 从localStorage提取token
            logger.info("🔍 从localStorage提取token...")
            local_storage_tokens = self._extract_from_selenium_local_storage(driver)
            if local_storage_tokens and not token_info.get('token'):
                token_info.update(local_storage_tokens)
            
            # 3. 从sessionStorage提取token
            logger.info("🔍 从sessionStorage提取token...")
            session_storage_tokens = self._extract_from_selenium_session_storage(driver)
            if session_storage_tokens and not token_info.get('token'):
                token_info.update(session_storage_tokens)
            
            # 4. 从页面JavaScript变量提取token
            logger.info("🔍 从页面JavaScript变量提取token...")
            js_tokens = self._extract_from_selenium_js_variables(driver)
            if js_tokens and not token_info.get('token'):
                token_info.update(js_tokens)
            
            logger.info(f"✅ Token提取完成: {token_info.get('token', 'None')[:20]}...")
            return token_info
            
        except Exception as e:
            logger.error(f"从Selenium WebDriver提取token失败: {str(e)}")
            return token_info
    
    def _extract_from_cookies(self, cookies: List[Dict]) -> Dict[str, Any]:
        """从cookies中提取token"""
        for cookie in cookies:
            cookie_name = cookie.get('name', '')
            cookie_value = cookie.get('value', '')
            
            if cookie_name in self.token_fields and len(cookie_value) > 20:
                return {
                    'token': cookie_value,
                    'source': f'cookies.{cookie_name}',
                    'token_length': len(cookie_value)
                }
        
        return {}
    
    def _extract_from_selenium_cookies(self, cookies: List[Dict]) -> Dict[str, Any]:
        """从Selenium cookies中提取token"""
        for cookie in cookies:
            cookie_name = cookie.get('name', '')
            cookie_value = cookie.get('value', '')
            
            if cookie_name in self.token_fields and len(cookie_value) > 20:
                return {
                    'token': cookie_value,
                    'source': f'cookies.{cookie_name}',
                    'token_length': len(cookie_value)
                }
        
        return {}
    
    def _extract_from_local_storage(self, page: Page) -> Dict[str, Any]:
        """从localStorage中提取token"""
        try:
            local_storage = page.evaluate("() => window.localStorage")
            token_info = {}
            
            for key in self.local_storage_keys:
                value = local_storage.get(key)
                if value and len(value) > 20:
                    token_info['token'] = value
                    token_info['source'] = f'localStorage.{key}'
                    token_info['token_length'] = len(value)
                    token_info['local_storage'] = {key: value}
                    break
            
            return token_info
            
        except Exception as e:
            logger.warning(f"从localStorage提取token失败: {str(e)}")
            return {}
    
    def _extract_from_session_storage(self, page: Page) -> Dict[str, Any]:
        """从sessionStorage中提取token"""
        try:
            session_storage = page.evaluate("() => window.sessionStorage")
            token_info = {}
            
            for key in self.session_storage_keys:
                value = session_storage.get(key)
                if value and len(value) > 20:
                    token_info['token'] = value
                    token_info['source'] = f'sessionStorage.{key}'
                    token_info['token_length'] = len(value)
                    token_info['session_storage'] = {key: value}
                    break
            
            return token_info
            
        except Exception as e:
            logger.warning(f"从sessionStorage提取token失败: {str(e)}")
            return {}
    
    def _extract_from_selenium_local_storage(self, driver: WebDriver) -> Dict[str, Any]:
        """从Selenium localStorage中提取token"""
        try:
            local_storage = driver.execute_script("return window.localStorage;")
            token_info = {}
            
            for key in self.local_storage_keys:
                value = local_storage.get(key)
                if value and len(value) > 20:
                    token_info['token'] = value
                    token_info['source'] = f'localStorage.{key}'
                    token_info['token_length'] = len(value)
                    token_info['local_storage'] = {key: value}
                    break
            
            return token_info
            
        except Exception as e:
            logger.warning(f"从Selenium localStorage提取token失败: {str(e)}")
            return {}
    
    def _extract_from_selenium_session_storage(self, driver: WebDriver) -> Dict[str, Any]:
        """从Selenium sessionStorage中提取token"""
        try:
            session_storage = driver.execute_script("return window.sessionStorage;")
            token_info = {}
            
            for key in self.session_storage_keys:
                value = session_storage.get(key)
                if value and len(value) > 20:
                    token_info['token'] = value
                    token_info['source'] = f'sessionStorage.{key}'
                    token_info['token_length'] = len(value)
                    token_info['session_storage'] = {key: value}
                    break
            
            return token_info
            
        except Exception as e:
            logger.warning(f"从Selenium sessionStorage提取token失败: {str(e)}")
            return {}
    
    def _extract_from_js_variables(self, page: Page) -> Dict[str, Any]:
        """从页面JavaScript变量中提取token"""
        try:
            page_content = page.content()
            token_info = {}
            
            for pattern in self.js_variable_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    token = matches[0]
                    if len(token) > 20:
                        token_info['token'] = token
                        token_info['source'] = f'js_variable.{pattern.split("=")[0].strip()}'
                        token_info['token_length'] = len(token)
                        token_info['js_variables'] = {pattern.split("=")[0].strip(): token}
                        break
            
            return token_info
            
        except Exception as e:
            logger.warning(f"从JavaScript变量提取token失败: {str(e)}")
            return {}
    
    def _extract_from_selenium_js_variables(self, driver: WebDriver) -> Dict[str, Any]:
        """从Selenium页面JavaScript变量中提取token"""
        try:
            page_source = driver.page_source
            token_info = {}
            
            for pattern in self.js_variable_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    token = matches[0]
                    if len(token) > 20:
                        token_info['token'] = token
                        token_info['source'] = f'js_variable.{pattern.split("=")[0].strip()}'
                        token_info['token_length'] = len(token)
                        token_info['js_variables'] = {pattern.split("=")[0].strip(): token}
                        break
            
            return token_info
            
        except Exception as e:
            logger.warning(f"从Selenium JavaScript变量提取token失败: {str(e)}")
            return {}
    
    def _extract_from_page_content(self, page: Page) -> Dict[str, Any]:
        """从页面内容中搜索token模式"""
        try:
            page_content = page.content()
            
            # 搜索JSON格式的token
            json_patterns = [
                r'"token"\s*:\s*"([^"]+)"',
                r'"access_token"\s*:\s*"([^"]+)"',
                r'"auth_token"\s*:\s*"([^"]+)"',
                r'"wt2"\s*:\s*"([^"]+)"',
                r'"zp_at"\s*:\s*"([^"]+)"',
                r'"__zp_stoken__"\s*:\s*"([^"]+)"',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    token = matches[0]
                    if len(token) > 20:
                        return {
                            'token': token,
                            'source': f'page_content.{pattern.split(":")[0].strip()}',
                            'token_length': len(token)
                        }
            
            return {}
            
        except Exception as e:
            logger.warning(f"从页面内容提取token失败: {str(e)}")
            return {}
    
    def validate_token(self, token: str) -> bool:
        """验证token有效性"""
        if not token or len(token) < 20:
            return False
        
        # Boss直聘token通常包含特定字符
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_=')
        if not all(c in valid_chars for c in token):
            return False
        
        return True
    
    def get_token_summary(self, token_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取token摘要信息"""
        return {
            'has_token': bool(token_info.get('token')),
            'token_length': token_info.get('token_length', 0),
            'source': token_info.get('source', 'unknown'),
            'is_valid': self.validate_token(token_info.get('token', '')),
            'extraction_methods': [
                'cookies' if token_info.get('cookies') else None,
                'localStorage' if token_info.get('local_storage') else None,
                'sessionStorage' if token_info.get('session_storage') else None,
                'js_variables' if token_info.get('js_variables') else None,
            ],
            'cookie_count': len(token_info.get('cookies', {})),
            'local_storage_count': len(token_info.get('local_storage', {})),
            'session_storage_count': len(token_info.get('session_storage', {}))
        }


# 全局token提取器实例
token_extractor = TokenExtractor()
