"""
Boss直聘真实集成服务
实现真正的登录、token获取和简历投递
"""
import json
import logging
import os
import time
import requests
from typing import Dict, List, Optional

# 尝试导入selenium，如果失败则使用替代方案
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("Warning: selenium module not found, using alternative implementation")
    SELENIUM_AVAILABLE = False
    # 简单的替代实现
    class MockWebDriver:
        def __init__(self, *args, **kwargs):
            pass
        def get(self, url):
            pass
        def quit(self):
            pass
        def find_element(self, *args, **kwargs):
            return MockElement()
        def find_elements(self, *args, **kwargs):
            return []
        def execute_script(self, *args, **kwargs):
            return None
    
    class MockElement:
        def click(self):
            pass
        def send_keys(self, text):
            pass
        def get_attribute(self, attr):
            return ""
        @property
        def text(self):
            return ""
    
    webdriver = MockWebDriver
    By = type('By', (), {'ID': 'id', 'CLASS_NAME': 'class_name', 'TAG_NAME': 'tag_name'})()
    WebDriverWait = lambda driver, timeout: type('WebDriverWait', (), {'until': lambda condition: None})()
    EC = type('EC', (), {'presence_of_element_located': lambda locator: None})()
    Options = lambda: type('Options', (), {'add_argument': lambda arg: None})()
    TimeoutException = Exception
    NoSuchElementException = Exception

logger = logging.getLogger(__name__)


class BossZhipinService:
    """Boss直聘真实服务"""
    
    def __init__(self):
        self.base_url = "https://www.zhipin.com"
        self.login_url = "https://login.zhipin.com/"
        self.api_base = "https://www.zhipin.com/wapi/zpgeek"
        self.session = requests.Session()
        self.driver = None
        self.is_logged_in = False
        self.user_token = None
        self.cookies = {}
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.zhipin.com/',
        })
    
    def login_with_qr_code(self) -> Dict:
        """通过二维码登录"""
        try:
            # 启动浏览器
            self._init_driver()
            
            # 访问登录页面
            self.driver.get(self.login_url)
            time.sleep(3)
            
            # 等待二维码出现
            qr_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "qrcode-img"))
            )
            
            # 获取二维码图片
            qr_img = qr_element.find_element(By.TAG_NAME, "img")
            qr_src = qr_img.get_attribute("src")
            
            logger.info("二维码已生成，请使用Boss直聘APP扫码登录")
            
            # 等待登录成功
            success = self._wait_for_login_success()
            
            if success:
                # 获取登录后的cookies和token
                self._extract_login_info()
                
                return {
                    "success": True,
                    "message": "登录成功",
                    "qr_code_url": qr_src,
                    "token": self.user_token
                }
            else:
                return {
                    "success": False,
                    "error": "登录超时或失败"
                }
                
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return {
                "success": False,
                "error": f"登录失败: {str(e)}"
            }
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    logger.error(f"关闭浏览器失败: {str(e)}")
                finally:
                    self.driver = None
    
    def login_with_token(self, token: str) -> Dict:
        """使用token登录"""
        try:
            # 设置token到请求头
            self.session.headers.update({
                'Authorization': f'Bearer {token}',
                'X-Token': token
            })
            
            # 测试token有效性
            response = self.session.get(f"{self.api_base}/user/info")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    self.is_logged_in = True
                    self.user_token = token
                    
                    return {
                        "success": True,
                        "message": "Token登录成功",
                        "token": token
                    }
            
            return {
                "success": False,
                "error": "Token无效或已过期"
            }
            
        except Exception as e:
            logger.error(f"Token登录失败: {str(e)}")
            return {
                "success": False,
                "error": f"Token登录失败: {str(e)}"
            }
    
    def login_with_cookies(self, cookies: Dict) -> Dict:
        """使用cookies登录"""
        try:
            # 设置cookies
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            # 测试登录状态
            response = self.session.get(f"{self.api_base}/user/info")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    self.is_logged_in = True
                    self.user_token = data.get('data', {}).get('token')
                    
                    return {
                        "success": True,
                        "message": "Cookies登录成功",
                        "token": self.user_token
                    }
            
            return {
                "success": False,
                "error": "Cookies无效或已过期"
            }
            
        except Exception as e:
            logger.error(f"Cookies登录失败: {str(e)}")
            return {
                "success": False,
                "error": f"Cookies登录失败: {str(e)}"
            }
    
    def search_jobs(self, keywords: List[str], cities: List[str], 
                   expected_salary: List[int], page: int = 1) -> Dict:
        """搜索职位"""
        try:
            if not self.is_logged_in:
                return {"success": False, "error": "请先登录"}
            
            # 构建搜索参数
            params = {
                'query': ' '.join(keywords),
                'city': cities[0] if cities else '101010100',  # 默认北京
                'salary': f"{expected_salary[0]}-{expected_salary[1]}" if len(expected_salary) == 2 else str(expected_salary[0]),
                'page': page,
                'ka': f'page-{page}'
            }
            
            # 发送搜索请求
            response = self.session.get(f"{self.api_base}/search/job", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    jobs = data.get('data', {}).get('list', [])
                    
                    return {
                        "success": True,
                        "jobs": jobs,
                        "total": data.get('data', {}).get('total', 0),
                        "page": page
                    }
            
            return {
                "success": False,
                "error": "搜索职位失败"
            }
            
        except Exception as e:
            logger.error(f"搜索职位失败: {str(e)}")
            return {
                "success": False,
                "error": f"搜索职位失败: {str(e)}"
            }
    
    def apply_job(self, job_id: str, say_hi: str = "", use_ai: bool = False) -> Dict:
        """投递简历"""
        try:
            if not self.is_logged_in:
                return {"success": False, "error": "请先登录"}
            
            # 如果启用AI，生成个性化打招呼语
            if use_ai and not say_hi:
                say_hi = self._generate_ai_greeting(job_id)
            
            # 构建投递数据
            data = {
                'jobId': job_id,
                'sayHi': say_hi or "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。",
                'source': 'web'
            }
            
            # 发送投递请求
            response = self.session.post(f"{self.api_base}/job/apply", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return {
                        "success": True,
                        "message": "投递成功",
                        "apply_id": result.get('data', {}).get('applyId')
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get('message', '投递失败')
                    }
            
            return {
                "success": False,
                "error": "投递请求失败"
            }
            
        except Exception as e:
            logger.error(f"投递简历失败: {str(e)}")
            return {
                "success": False,
                "error": f"投递简历失败: {str(e)}"
            }
    
    def batch_apply_jobs(self, keywords: List[str], cities: List[str],
                        expected_salary: List[int], say_hi: str = "",
                        use_ai: bool = False, max_pages: int = 5) -> Dict:
        """批量投递简历"""
        try:
            if not self.is_logged_in:
                return {"success": False, "error": "请先登录"}
            
            total_applied = 0
            total_failed = 0
            applied_jobs = []
            failed_jobs = []
            
            # 遍历多页搜索结果
            for page in range(1, max_pages + 1):
                logger.info(f"正在搜索第 {page} 页职位...")
                
                # 搜索职位
                search_result = self.search_jobs(keywords, cities, expected_salary, page)
                
                if not search_result.get('success'):
                    logger.error(f"第 {page} 页搜索失败: {search_result.get('error')}")
                    continue
                
                jobs = search_result.get('jobs', [])
                if not jobs:
                    logger.info(f"第 {page} 页没有更多职位")
                    break
                
                # 投递每个职位
                for job in jobs:
                    job_id = job.get('jobId')
                    job_title = job.get('jobName', '未知职位')
                    company_name = job.get('companyName', '未知公司')
                    
                    logger.info(f"正在投递: {company_name} - {job_title}")
                    
                    # 投递简历
                    apply_result = self.apply_job(job_id, say_hi, use_ai)
                    
                    if apply_result.get('success'):
                        total_applied += 1
                        applied_jobs.append({
                            'job_id': job_id,
                            'job_title': job_title,
                            'company_name': company_name,
                            'apply_id': apply_result.get('apply_id')
                        })
                        logger.info(f"✅ 投递成功: {company_name} - {job_title}")
                    else:
                        total_failed += 1
                        failed_jobs.append({
                            'job_id': job_id,
                            'job_title': job_title,
                            'company_name': company_name,
                            'error': apply_result.get('error')
                        })
                        logger.error(f"❌ 投递失败: {company_name} - {job_title} - {apply_result.get('error')}")
                    
                    # 避免请求过于频繁
                    time.sleep(2)
            
            return {
                "success": True,
                "message": f"批量投递完成，成功: {total_applied}, 失败: {total_failed}",
                "total_applied": total_applied,
                "total_failed": total_failed,
                "applied_jobs": applied_jobs,
                "failed_jobs": failed_jobs
            }
            
        except Exception as e:
            logger.error(f"批量投递失败: {str(e)}")
            return {
                "success": False,
                "error": f"批量投递失败: {str(e)}"
            }
    
    def _init_driver(self):
        """初始化浏览器驱动"""
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-javascript')
            chrome_options.add_argument('--disable-css')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--silent')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            
            # 指定Chrome浏览器路径（macOS）
            chrome_binary_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_binary_path):
                chrome_options.binary_location = chrome_binary_path
            
            # 使用webdriver-manager自动管理ChromeDriver，指定版本
            try:
                # 尝试使用特定版本的ChromeDriver
                service = Service(ChromeDriverManager(version="119.0.6045.105").install())
            except:
                # 如果特定版本失败，使用最新版本
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Chrome WebDriver初始化成功")
            
        except Exception as e:
            logger.error(f"WebDriver初始化失败: {str(e)}")
            # 尝试备用方案：使用系统PATH中的chromedriver
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("使用系统ChromeDriver初始化成功")
            except Exception as e2:
                logger.error(f"备用WebDriver初始化也失败: {str(e2)}")
                raise Exception(f"无法启动浏览器: {str(e)}")
    
    def _wait_for_login_success(self, timeout: int = 300) -> bool:
        """等待登录成功"""
        try:
            # 等待页面跳转到主页或用户中心
            WebDriverWait(self.driver, timeout).until(
                lambda driver: 'zhipin.com' in driver.current_url and 'login' not in driver.current_url
            )
            return True
        except TimeoutException:
            return False
    
    def _extract_login_info(self):
        """提取登录信息"""
        try:
            # 获取cookies
            for cookie in self.driver.get_cookies():
                self.cookies[cookie['name']] = cookie['value']
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # 获取token
            # 这里需要根据实际的页面结构来获取token
            # 通常token会在localStorage或sessionStorage中
            token = self.driver.execute_script("return localStorage.getItem('token') || sessionStorage.getItem('token')")
            if token:
                self.user_token = token
            
            self.is_logged_in = True
            
        except Exception as e:
            logger.error(f"提取登录信息失败: {str(e)}")
    
    def _generate_ai_greeting(self, job_id: str) -> str:
        """使用AI生成个性化打招呼语"""
        try:
            # 这里可以集成AI服务来生成个性化的打招呼语
            # 暂时返回一个通用的打招呼语
            greetings = [
                "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。",
                "您好，我的技能和经验与这个职位要求很匹配，希望能加入贵公司。",
                "您好，我对这个职位非常感兴趣，希望能有机会与您详细交流。",
                "您好，我仔细阅读了职位描述，认为我的背景很适合这个岗位。"
            ]
            
            import random
            return random.choice(greetings)
            
        except Exception as e:
            logger.error(f"生成AI打招呼语失败: {str(e)}")
            return "您好，我对这个职位很感兴趣，希望能有机会进一步沟通。"
    
    def get_login_status(self) -> Dict:
        """获取登录状态"""
        return {
            "is_logged_in": self.is_logged_in,
            "has_token": bool(self.user_token),
            "cookies_count": len(self.cookies)
        }
    
    def logout(self):
        """退出登录"""
        self.is_logged_in = False
        self.user_token = None
        self.cookies = {}
        self.session.cookies.clear()
        
        if self.driver:
            self.driver.quit()
            self.driver = None
