"""
简单安全验证绕过服务
基于项目现有代码的简化版本，使用requests而不是playwright
"""
import logging
import time
import random
import requests
from typing import Dict, Optional
from fake_useragent import UserAgent
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .cookie_manager import cookie_manager

logger = logging.getLogger(__name__)

class SimpleSecurityBypassService:
    """简单安全验证绕过服务 - 基于项目现有代码"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """设置session配置"""
        # 禁用SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self._update_headers()
    
    def _update_headers(self):
        """更新请求头"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def bypass_security_verification(self, url: str) -> Dict:
        """绕过安全验证 - 参考get_jobs项目实现"""
        try:
            logger.info("🔍 开始绕过安全验证...")
            
            # 首先尝试访问登录页面获取真实的session
            logger.info("🔄 尝试访问登录页面建立session...")
            login_result = self._establish_session()
            if login_result:
                logger.info("✅ 成功建立session")
            
            # 参考get_jobs项目的绕过策略：先访问主页建立session
            logger.info("🔄 参考get_jobs项目：先访问主页建立session...")
            try:
                # 访问Boss直聘主页
                main_response = self.session.get("https://www.zhipin.com/", timeout=30, verify=False)
                self._random_delay(1, 2)
                
                # 访问登录页面
                login_response = self.session.get("https://login.zhipin.com/", timeout=30, verify=False)
                self._random_delay(1, 2)
                
                # 访问用户中心
                user_response = self.session.get("https://www.zhipin.com/web/geek/", timeout=30, verify=False)
                self._random_delay(1, 2)
                
                logger.info("✅ 成功建立Boss直聘session")
            except Exception as e:
                logger.warning(f"建立session失败: {str(e)}")
            
            # 方法1: 改变Referer
            logger.info("🔄 尝试方法1: 改变Referer")
            result = self._method_1_change_referer(url)
            if result and self._is_bypassed(result):
                logger.info("✅ 方法1成功绕过安全验证")
                return {"bypassed": True, "method": "referer", "response": result}
            
            # 方法2: 随机化请求头
            logger.info("🔄 尝试方法2: 随机化请求头")
            result = self._method_2_random_headers(url)
            if result and self._is_bypassed(result):
                logger.info("✅ 方法2成功绕过安全验证")
                return {"bypassed": True, "method": "headers", "response": result}
            
            # 方法3: 会话预热
            logger.info("🔄 尝试方法3: 会话预热")
            result = self._method_3_session_warming(url)
            if result and self._is_bypassed(result):
                logger.info("✅ 方法3成功绕过安全验证")
                return {"bypassed": True, "method": "warming", "response": result}
            
            # 方法4: Cookie操作
            logger.info("🔄 尝试方法4: Cookie操作")
            result = self._method_4_cookie_manipulation(url)
            if result and self._is_bypassed(result):
                logger.info("✅ 方法4成功绕过安全验证")
                return {"bypassed": True, "method": "cookies", "response": result}
            
            # 方法5: 多次重试
            logger.info("🔄 尝试方法5: 多次重试")
            result = self._method_5_multiple_retries(url)
            if result and self._is_bypassed(result):
                logger.info("✅ 方法5成功绕过安全验证")
                return {"bypassed": True, "method": "retries", "response": result}
            
            # 方法6: 高级绕过策略 - 参考get_jobs项目
            logger.info("🔄 尝试方法6: 高级绕过策略")
            result = self._method_6_advanced_bypass(url)
            if result and self._is_bypassed(result):
                logger.info("✅ 方法6成功绕过安全验证")
                return {"bypassed": True, "method": "advanced", "response": result}
            
            logger.warning("❌ 所有绕过方法都失败了")
            return {"bypassed": False, "message": "需要手动完成安全验证"}
            
        except Exception as e:
            logger.error(f"绕过安全验证失败: {str(e)}")
            return {"bypassed": False, "message": f"绕过失败: {str(e)}"}
    
    def _is_bypassed(self, response) -> bool:
        """检查是否成功绕过安全验证（但不等于已登录）"""
        if not response:
            return False
        
        # 检查URL是否包含验证页面标识
        if 'verify-slider' in response.url or 'safe/verify' in response.url:
            return False
        
        # 检查响应内容长度（验证页面通常较短）
        if len(response.text) < 5000:
            return False
        
        # 检查页面标题
        if '验证' in response.text or '安全' in response.text:
            return False
        
        # 注意：绕过安全验证不等于已登录！
        # 这里只检查是否绕过了安全验证，不检查登录状态
        return True
    
    def _method_1_change_referer(self, url: str):
        """方法1: 改变Referer - 参考get_jobs项目"""
        try:
            # 先访问主页建立session
            try:
                self.session.get("https://www.zhipin.com/", timeout=15, verify=False)
                self._random_delay(1, 2)
            except:
                pass
            
            # 设置更真实的请求头
            self.session.headers.update({
                'Referer': 'https://www.zhipin.com/web/geek/jobs',
                'Origin': 'https://www.zhipin.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            self._random_delay(1, 3)
            return self.session.get(url, timeout=30, verify=False)
        except Exception as e:
            logger.debug(f"方法1失败: {str(e)}")
            return None
    
    def _method_2_random_headers(self, url: str):
        """方法2: 随机化请求头"""
        try:
            self._update_headers()
            self.session.headers.update({
                'Accept': random.choice([
                    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                ]),
                'Accept-Language': random.choice([
                    'zh-CN,zh;q=0.9,en;q=0.8',
                    'zh-CN,zh;q=0.8,en;q=0.6',
                    'en-US,en;q=0.9,zh-CN;q=0.8',
                ]),
            })
            self._random_delay(1, 3)
            return self.session.get(url, timeout=30, verify=False)
        except Exception as e:
            logger.debug(f"方法2失败: {str(e)}")
            return None
    
    def _method_3_session_warming(self, url: str):
        """方法3: 会话预热"""
        try:
            # 访问一些相关页面来建立正常的会话历史
            warm_urls = [
                'https://www.zhipin.com/',
                'https://www.zhipin.com/web/geek/',
                'https://www.zhipin.com/web/geek/jobs',
            ]
            
            for warm_url in warm_urls:
                try:
                    self.session.get(warm_url, timeout=15, verify=False)
                    self._random_delay(0.5, 1.5)
                except:
                    pass
            
            self._random_delay(2, 4)
            return self.session.get(url, timeout=30, verify=False)
        except Exception as e:
            logger.debug(f"方法3失败: {str(e)}")
            return None
    
    def _method_4_cookie_manipulation(self, url: str):
        """方法4: Cookie操作"""
        try:
            # 添加一些常见的Cookie
            self.session.cookies.update({
                'Hm_lvt_194df3105fd7148422f53a601620a2d0': str(int(time.time())),
                'Hm_lpvt_194df3105fd7148422f53a601620a2d0': str(int(time.time())),
                'lastCity': '101010100',
                'JSESSIONID': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=32)),
            })
            self._random_delay(1, 3)
            return self.session.get(url, timeout=30, verify=False)
        except Exception as e:
            logger.debug(f"方法4失败: {str(e)}")
            return None
    
    def _method_5_multiple_retries(self, url: str):
        """方法5: 多次重试"""
        try:
            for attempt in range(3):
                logger.info(f"重试第 {attempt + 1} 次...")
                
                # 每次重试都更新User-Agent
                self._update_headers()
                
                # 添加随机延迟
                self._random_delay(2, 5)
                
                response = self.session.get(url, timeout=30, verify=False)
                
                if self._is_bypassed(response):
                    return response
                
                # 如果不是最后一次尝试，等待更长时间
                if attempt < 2:
                    self._random_delay(5, 10)
            
            return None
        except Exception as e:
            logger.debug(f"方法5失败: {str(e)}")
            return None
    
    def _random_delay(self, min_seconds: float, max_seconds: float):
        """随机延迟"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _establish_session(self):
        """建立真实的session - 使用用户提供的真实cookies"""
        try:
            # 使用用户提供的真实cookies
            real_cookies = {
                '__a': '20936101.1758901166..1758901166.40.1.40.40',
                '__c': '1758901166',
                '__g': '-',
                '__l': 'l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs&r=http%3A%2F%2Flocalhost%3A8001%2F&g=&s=3&friend_source=0&s=3&friend_source=0',
                '__zp_stoken__': 'e468fNT5BwrrDvsK0OSUSDxEMBD4oOD4oZj81MkA6PDU%2BNjg%2BNT4%2BGjglwqvCtysaw69Xw4cHNSo%2BNjs1NTg2OkIaPkLCtDU2JEUrGsOvV8OHBwwEaAPCj8K4BMOfwrckw6PCtTIkw6zCtDg%2FPzPCjsKzLcOCwrDCsybCusKNwrgmw4E%2FN8Obw4EsKDMHUwVaMzNJR1wJRV1IVl9RCk9IUCU4QT02A8O5w7gjNBEODgUNBwQECwMNEhIOBgwPDwgQAwgIDwcyNcKhwr%2FCl2XDgMS7w7HElcKUWMOmwp%2FDqMKkwrXCu8KsSsKxwr3Co8OCwp9fRsOBSMK%2BYcK3wqtDUlbCul3Cnl9Rw4FKVcOCfWhhZkjCv2ZORREPDBJYMwvCvcOPw4k%3D',
                'ab_guid': '9f930709-775a-4224-b643-1494f7281c7c'
            }
            
            # 设置cookies到session
            for name, value in real_cookies.items():
                self.session.cookies.set(name, value, domain='.zhipin.com')
                logger.info(f"✅ 设置cookie: {name} = {value[:20]}...")
            
            logger.info(f"✅ 成功设置 {len(real_cookies)} 个真实cookies")
            
            # 访问主页建立session
            logger.info("访问Boss直聘主页建立session...")
            response = self.session.get("https://www.zhipin.com/", timeout=30, verify=False)
            self._random_delay(1, 2)
            
            logger.info(f"Session建立完成，cookies数量: {len(self.session.cookies)}")
            return True
            
        except Exception as e:
            logger.warning(f"建立session失败: {str(e)}")
            return False
    
    def _get_chrome_cookies(self):
        """从Chrome浏览器获取cookies - 参考get_jobs项目实现"""
        try:
            import sqlite3
            import os
            import tempfile
            import shutil
            import subprocess
            
            # Chrome cookie文件路径
            cookie_paths = [
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Profile 1/Cookies"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Network/Cookies"),
            ]
            
            for cookie_path in cookie_paths:
                if not os.path.exists(cookie_path):
                    continue
                
                logger.info(f"检查cookie文件: {cookie_path}")
                
                # 复制cookie文件到临时目录
                temp_cookie = tempfile.mktemp()
                shutil.copy2(cookie_path, temp_cookie)
                
                try:
                    # 连接SQLite数据库
                    conn = sqlite3.connect(temp_cookie)
                    cursor = conn.cursor()
                    
                    # 查询Boss直聘相关的cookies - 参考get_jobs项目的查询方式
                    cursor.execute("""
                        SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, creation_utc
                        FROM cookies 
                        WHERE (host_key LIKE '%zhipin.com%' OR host_key LIKE '%boss.com%' OR host_key LIKE '%.zhipin.com%')
                        AND name IN ('wt2', 'zp_at', '__zp_stoken__', 'bst', 'wbg', '__a', '__c', '__g', 'acw_tc', 'lastCity', 'uid')
                        ORDER BY creation_utc DESC
                        LIMIT 20
                    """)
                    
                    cookies = cursor.fetchall()
                    conn.close()
                    
                    if cookies:
                        logger.info(f"找到 {len(cookies)} 个Boss直聘cookies")
                        cookie_list = []
                        for cookie in cookies:
                            name, value, domain, path, expires, secure, httponly, created = cookie
                            
                            # 检查cookie值是否有效（不是空字符串）
                            if value and len(value) > 0:
                                cookie_list.append({
                                    'name': name,
                                    'value': value,
                                    'domain': domain,
                                    'path': path,
                                    'expires': expires,
                                    'secure': bool(secure),
                                    'httponly': bool(httponly)
                                })
                                logger.info(f"✅ 有效cookie: {name} = {value[:20]}...")
                            else:
                                logger.debug(f"❌ 空值cookie: {name}")
                        
                        if cookie_list:
                            return cookie_list
                    
                except Exception as e:
                    logger.debug(f"处理cookie文件失败: {str(e)}")
                    continue
                finally:
                    # 清理临时文件
                    try:
                        os.unlink(temp_cookie)
                    except:
                        pass
            
            # 如果无法从Chrome获取cookies，尝试使用系统命令
            logger.info("尝试使用系统命令获取cookies...")
            return self._get_cookies_via_system_command()
            
        except Exception as e:
            logger.warning(f"获取Chrome cookies失败: {str(e)}")
            return None
    
    def _get_cookies_via_system_command(self):
        """使用系统命令获取cookies - 参考get_jobs项目"""
        try:
            import subprocess
            import json
            
            # 尝试使用Chrome的调试端口获取cookies
            try:
                # 检查Chrome是否在运行
                result = subprocess.run(['pgrep', '-f', 'Google Chrome'], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("检测到Chrome正在运行，尝试通过调试端口获取cookies")
                    
                    # 尝试连接到Chrome的调试端口
                    import requests
                    try:
                        response = requests.get('http://localhost:9222/json', timeout=5)
                        if response.status_code == 200:
                            tabs = response.json()
                            logger.info(f"找到 {len(tabs)} 个Chrome标签页")
                            
                            # 查找Boss直聘相关的标签页
                            for tab in tabs:
                                if 'zhipin.com' in tab.get('url', ''):
                                    logger.info(f"找到Boss直聘标签页: {tab.get('url')}")
                                    # 这里可以进一步获取该标签页的cookies
                                    return self._extract_cookies_from_tab(tab)
                    except Exception as e:
                        logger.debug(f"通过调试端口获取cookies失败: {str(e)}")
            except Exception as e:
                logger.debug(f"系统命令获取cookies失败: {str(e)}")
            
            return None
            
        except Exception as e:
            logger.warning(f"系统命令获取cookies失败: {str(e)}")
            return None
    
    def _extract_cookies_from_tab(self, tab):
        """从Chrome标签页提取cookies"""
        try:
            import requests
            
            tab_id = tab.get('id')
            if not tab_id:
                return None
            
            # 获取该标签页的cookies
            cookies_url = f'http://localhost:9222/json/runtime/evaluate'
            payload = {
                'expression': 'document.cookie'
            }
            
            response = requests.post(cookies_url, json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                cookie_string = result.get('result', {}).get('value', '')
                
                if cookie_string:
                    logger.info(f"从标签页获取到cookies: {cookie_string[:100]}...")
                    # 解析cookie字符串
                    cookies = {}
                    for cookie in cookie_string.split(';'):
                        if '=' in cookie:
                            name, value = cookie.strip().split('=', 1)
                            if name in ['wt2', 'zp_at', '__zp_stoken__', 'bst', 'wbg']:
                                cookies[name] = value
                    
                    if cookies:
                        cookie_list = []
                        for name, value in cookies.items():
                            cookie_list.append({
                                'name': name,
                                'value': value,
                                'domain': '.zhipin.com',
                                'path': '/',
                                'expires': 0,
                                'secure': False,
                                'httponly': False
                            })
                        return cookie_list
            
            return None
            
        except Exception as e:
            logger.debug(f"从标签页提取cookies失败: {str(e)}")
            return None
    
    def extract_tokens_from_response(self, response) -> Dict[str, str]:
        """从响应中提取token - 增强版"""
        try:
            if not response:
                return {}
            
            token_info = {}
            
            # 从cookies中提取token
            for cookie in self.session.cookies:
                if cookie.name in ['wt2', 'zp_at', '__a', '__c', '__g', '__zp_stoken__', 'bst', 'wbg']:
                    token_info[cookie.name] = cookie.value
                    logger.info(f"✅ 找到cookie token: {cookie.name} = {cookie.value[:20]}...")
            
            # 检查页面内容是否真的登录了
            content = response.text
            if "登录/注册" in content or ("登录" in content and "注册" in content):
                logger.warning("❌ 页面包含'登录/注册'按钮，说明未登录")
                # 即使有cookies，如果页面显示登录按钮，说明未登录
                return {}
            
            # 如果提取到有效的tokens，自动保存到cookie管理器
            if token_info:
                logger.info(f"🍪 自动保存{len(token_info)}个tokens到cookie管理器")
                cookie_manager.save_cookies(token_info)
            
            # 从页面内容中提取token
            content = response.text
            
            # 使用正则表达式提取token
            import re
            
            # 提取wt2 token - 多种模式
            wt2_patterns = [
                r'wt2["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'"wt2"\s*:\s*"([^"]+)"',
                r'wt2\s*=\s*["\']([^"\']+)["\']',
                r'window\.wt2\s*=\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in wt2_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    token_info['wt2_content'] = matches[0]
                    logger.info(f"✅ 在页面内容中找到wt2 token: {matches[0][:20]}...")
                    break
            
            # 提取zp_at token - 多种模式
            zp_at_patterns = [
                r'zp_at["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'"zp_at"\s*:\s*"([^"]+)"',
                r'zp_at\s*=\s*["\']([^"\']+)["\']',
                r'window\.zp_at\s*=\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in zp_at_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    token_info['zp_at_content'] = matches[0]
                    logger.info(f"✅ 在页面内容中找到zp_at token: {matches[0][:20]}...")
                    break
            
            # 提取其他可能的token
            other_patterns = [
                (r'"token"\s*:\s*"([^"]+)"', 'token'),
                (r'"accessToken"\s*:\s*"([^"]+)"', 'accessToken'),
                (r'"authToken"\s*:\s*"([^"]+)"', 'authToken'),
                (r'"sessionId"\s*:\s*"([^"]+)"', 'sessionId'),
                (r'"userId"\s*:\s*"([^"]+)"', 'userId')
            ]
            
            for pattern, token_name in other_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    token_info[f'{token_name}_content'] = matches[0]
                    logger.info(f"✅ 在页面内容中找到{token_name} token: {matches[0][:20]}...")
            
            # 如果找到了任何token，设置主要的token字段
            if token_info:
                # 优先使用__zp_stoken__ token
                if '__zp_stoken__' in token_info:
                    token_info['token'] = token_info['__zp_stoken__']
                    logger.info(f"✅ 使用__zp_stoken__作为主要token: {token_info['__zp_stoken__'][:20]}...")
                elif 'wt2_content' in token_info:
                    token_info['token'] = token_info['wt2_content']
                elif 'wt2' in token_info:
                    token_info['token'] = token_info['wt2']
                elif 'zp_at_content' in token_info:
                    token_info['token'] = token_info['zp_at_content']
                elif 'zp_at' in token_info:
                    token_info['token'] = token_info['zp_at']
                
                logger.info(f"✅ 总共找到 {len(token_info)} 个token")
            else:
                logger.warning("❌ 未找到任何token")
            
            return token_info
            
        except Exception as e:
            logger.error(f"提取token失败: {str(e)}")
            return {}
    
    def _method_6_advanced_bypass(self, url: str):
        """方法6: 高级绕过策略 - 参考get_jobs项目"""
        try:
            # 策略1: 模拟真实用户行为
            logger.info("🔄 策略1: 模拟真实用户行为")
            
            # 先访问多个页面建立真实的浏览历史
            warm_urls = [
                "https://www.zhipin.com/",
                "https://www.zhipin.com/web/geek/",
                "https://www.zhipin.com/web/geek/jobs",
                "https://www.zhipin.com/web/geek/jobs?city=101010100",
            ]
            
            for warm_url in warm_urls:
                try:
                    self.session.get(warm_url, timeout=15, verify=False)
                    self._random_delay(0.5, 1.5)
                except:
                    continue
            
            # 策略2: 使用更真实的请求头
            self.session.headers.update({
                'Referer': 'https://www.zhipin.com/web/geek/jobs?city=101010100',
                'Origin': 'https://www.zhipin.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # 策略3: 添加真实的cookies
            self.session.cookies.update({
                'lastCity': '101010100',
                'Hm_lvt_194df3105fd7148422f53a601620a2d0': str(int(time.time())),
                'Hm_lpvt_194df3105fd7148422f53a601620a2d0': str(int(time.time())),
            })
            
            self._random_delay(2, 4)
            response = self.session.get(url, timeout=30, verify=False)
            
            # 策略4: 如果还是验证页面，尝试POST请求
            if not self._is_bypassed(response):
                logger.info("🔄 策略4: 尝试POST请求")
                try:
                    post_data = {
                        'city': '101010100',
                        'query': '',
                        'page': '1',
                        'ka': 'sel-city-101010100'
                    }
                    response = self.session.post(url, data=post_data, timeout=30, verify=False)
                except:
                    pass
            
            return response
            
        except Exception as e:
            logger.debug(f"方法6失败: {str(e)}")
            return None
