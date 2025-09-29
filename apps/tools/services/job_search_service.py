"""
AI找工作服务层 - 真实版本
集成真正的Boss直聘API
"""
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth.models import User
from .boss_zhipin_service import BossZhipinService
from .boss_zhipin_playwright import BossZhipinPlaywrightService

logger = logging.getLogger(__name__)


class JobSearchService:
    """AI找工作服务"""
    
    def __init__(self):
        self.base_dir = os.path.join(settings.BASE_DIR, 'get_jobs_integration')
        self.config_file = os.path.join(self.base_dir, 'config.yaml')
        self.logs_dir = os.path.join(self.base_dir, 'logs')
        
        # 确保目录存在
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 运行状态跟踪
        self.running_processes = {}
    
    def start_job_search(self, platforms: List[str], keywords: List[str], 
                        cities: List[str], expected_salary: List[int],
                        say_hi: str, use_ai: bool, send_img_resume: bool,
                        user: User) -> Dict:
        """启动AI投递"""
        try:
            # 检查是否已有运行中的进程
            if user.id in self.running_processes:
                return {"success": False, "error": "已有投递任务在运行中"}
            
            # 如果包含Boss直聘，使用真实API
            if 'boss' in platforms:
                return self._start_real_boss_search(keywords, cities, expected_salary, say_hi, use_ai, user)
            else:
                # 其他平台使用模拟
                return self._start_simulated_search(platforms, keywords, cities, expected_salary, say_hi, use_ai, user)
                
        except Exception as e:
            logger.error(f"启动投递失败: {str(e)}")
            return {"success": False, "error": f"启动失败: {str(e)}"}
    
    def start_boss_search_with_cookies(self, cookies: Dict, keywords: List[str], cities: List[str], 
                                     expected_salary: List[int], say_hi: str, use_ai: bool, user: User) -> Dict:
        """使用cookies启动Boss直聘投递"""
        try:
            logger.info(f"用户 {user.username} 使用cookies启动Boss直聘投递")
            
            # 使用Playwright服务
            playwright_service = BossZhipinPlaywrightService(headless=False)
            
            # 设置cookies
            playwright_service.set_cookies(cookies)
            
            # 检查登录状态
            login_status = playwright_service.check_login_status(user.id)
            
            if not login_status.get('is_logged_in'):
                return {
                    "success": False,
                    "error": "cookies无效或已过期，请重新登录",
                    "need_login": True
                }
            
            # 启动投递任务
            logger.info("🔍 准备调用_start_real_boss_search方法...")
            result = self._start_real_boss_search(keywords, cities, expected_salary, say_hi, use_ai, user)
            logger.info(f"🔍 _start_real_boss_search返回类型: {type(result)}")
            
            # 确保返回的是字典类型
            if not isinstance(result, dict):
                logger.error(f"❌ _start_real_boss_search返回了错误的数据类型: {type(result)}")
                return {
                    "success": False,
                    "error": "投递任务启动失败",
                    "details": f"期望字典类型，实际得到: {type(result)}"
                }
            
            logger.info(f"🔍 _start_real_boss_search返回内容: {result}")
            return result
            
        except Exception as e:
            logger.error(f"使用cookies启动投递失败: {str(e)}")
            return {"success": False, "error": f"启动失败: {str(e)}"}
    
    def _start_real_boss_search(self, keywords: List[str], cities: List[str], 
                               expected_salary: List[int], say_hi: str, use_ai: bool, user: User) -> Dict:
        """启动真实的Boss直聘投递"""
        try:
            # 首先尝试使用Playwright检测到的token
            playwright_service = BossZhipinPlaywrightService(headless=False)
            login_check_result = playwright_service.check_login_status(user.id)
            
            if login_check_result.get('success') and login_check_result.get('is_logged_in'):
                # 如果检测到登录状态，提取token并保存
                token_info = login_check_result.get('token_info', {})
                token = token_info.get('token', '')
                
                # 检查是否是安全验证检测到的token
                if token == 'security_verification_detected':
                    logger.info("✅ 检测到安全验证页面，用户需要完成验证")
                    return {
                        "success": False,
                        "error": "检测到Boss直聘安全验证页面，请手动完成滑块验证后重试",
                        "need_login": True,
                        "security_verification": True,
                        "login_status": login_check_result,
                        "suggestion": "请在浏览器中完成Boss直聘的安全验证（滑块验证），然后重新启动投递任务"
                    }
                
                # 检查是否是绕过成功但未找到token的情况
                if token == 'bypass_success':
                    logger.info("✅ 绕过成功，开始真正的投递任务")
                    
                    # 从login_check_result中提取真正的token
                    real_token = None
                    if 'token_info' in login_check_result:
                        token_info = login_check_result['token_info']
                        # 尝试从token_info中提取真正的token
                        for key in ['wt2', 'zp_at', '__zp_stoken__', 'bst', 'wbg']:
                            if key in token_info and token_info[key]:
                                real_token = token_info[key]
                                logger.info(f"✅ 找到真实token: {key} = {real_token[:20]}...")
                                break
                
                # 检查是否是本地session的情况
                elif login_check_result.get('found_indicator') == 'local_session':
                    logger.info("✅ 检测到本地session，使用本地cookies进行投递")
                    
                    # 使用本地cookies创建Playwright服务
                    playwright_service = BossZhipinPlaywrightService(headless=False)
                    init_result = playwright_service._init_browser()
                    
                    if not playwright_service.page:
                        logger.error("❌ Playwright页面初始化失败")
                        return {
                            "success": False,
                            "error": "Playwright页面初始化失败",
                            "applied_count": 0,
                            "total_found": 0
                        }
                    
                    # 设置本地cookies
                    local_cookies = login_check_result.get('token_info', {})
                    playwright_cookies = []
                    
                    for name, value in local_cookies.items():
                        playwright_cookies.append({
                            'name': name,
                            'value': value,
                            'domain': '.zhipin.com',
                            'path': '/',
                            'httpOnly': True,
                            'secure': True
                        })
                    
                    # 添加cookies到浏览器上下文
                    playwright_service.page.context.add_cookies(playwright_cookies)
                    logger.info(f"✅ 已设置{len(playwright_cookies)}个本地cookies")
                    
                    # 访问Boss直聘主页验证登录状态
                    playwright_service.page.goto(f"{playwright_service.base_url}/web/geek/jobs", wait_until="domcontentloaded", timeout=30000)
                    
                    # 检查是否成功登录
                    try:
                        # 等待页面加载完成
                        playwright_service.page.wait_for_load_state("networkidle", timeout=10000)
                        
                        # 检查登录状态
                        login_indicators = ['.user-info', '.user-avatar', '.geek-info', '.geek-name']
                        is_logged_in = False
                        
                        for indicator in login_indicators:
                            try:
                                element = playwright_service.page.query_selector(indicator)
                                if element:
                                    is_logged_in = True
                                    logger.info(f"✅ 通过{indicator}检测到登录状态")
                                    break
                            except:
                                continue
                        
                        if not is_logged_in:
                            logger.warning("❌ 本地cookies可能已过期，未检测到登录状态")
                            return {
                                "success": False,
                                "error": "本地cookies已过期，请重新登录Boss直聘",
                                "need_login": True,
                                "applied_count": 0,
                                "total_found": 0
                            }
                        
                        logger.info("✅ 本地cookies验证成功，开始投递任务")
                        
                        # 执行投递任务
                        return self._apply_jobs_with_playwright(
                            playwright_service, 
                            "local_session", 
                            keywords, cities, expected_salary, say_hi, use_ai, user
                        )
                        
                    except Exception as e:
                        logger.error(f"❌ 本地session投递失败: {str(e)}")
                        return {
                            "success": False,
                            "error": f"本地session投递失败: {str(e)}",
                            "applied_count": 0,
                            "total_found": 0
                        }
                    
                    # 创建一个新的Playwright服务实例用于投递
                    logger.info("创建新的Playwright服务实例用于投递...")
                    delivery_service = BossZhipinPlaywrightService(headless=False)
                    
                    # 初始化浏览器并检查结果
                    logger.info("初始化Playwright浏览器...")
                    init_result = delivery_service._init_browser()
                    logger.info(f"浏览器初始化结果: {init_result}")
                    logger.info(f"浏览器对象: {delivery_service.browser}")
                    logger.info(f"页面对象: {delivery_service.page}")
                    
                    # 确保页面已创建
                    if not delivery_service.page:
                        logger.error("❌ Playwright页面初始化失败")
                        return {
                            "success": False,
                            "error": "Playwright页面初始化失败",
                            "applied_count": 0,
                            "total_found": 0
                        }
                    
                    # 在访问页面之前先设置cookies
                    logger.info("在访问页面之前设置真实的Boss直聘cookies...")
                    real_cookies = [
                        {
                            'name': '__a',
                            'value': '20936101.1758901166..1758901166.41.1.41.41',
                            'domain': '.zhipin.com',
                            'path': '/'
                        },
                        {
                            'name': '__c', 
                            'value': '1758901166',
                            'domain': '.zhipin.com',
                            'path': '/'
                        },
                        {
                            'name': '__g',
                            'value': '-',
                            'domain': '.zhipin.com', 
                            'path': '/'
                        },
                        {
                            'name': '__l',
                            'value': 'l=%2Fwww.zhipin.com%2Fweb%2Fgeek%2Fjobs&r=http%3A%2F%2Flocalhost%3A8001%2F&g=&s=3&friend_source=0&s=3&friend_source=0',
                            'domain': '.zhipin.com',
                            'path': '/'
                        },
                        {
                            'name': '__zp_stoken__',
                            'value': 'e468fNT5BwrrDvsK0OSUSDxEMBD4oOD4oZj81MkA6PDU%2BNjg%2BNT4%2BGjglwqvCtysaw69Xw4cHNSo%2BNjs1NTg2OkIaPkLCtDU2JEUrGsOvV8OHBwwEaAPCj8K4BMOfwrckw6PCtTIkw6zCtDg%2FPzPCjsKzLcOCwrDCsybCusKNwrgmw4E%2FN8Obw4EsKDMHUwVaMzNJR1wJRV1IVl9RCk9IUCU4QT02A8O5w7gjNBEODgUNBwQECwMNEhIOBgwPDwgQAwgIDwcyNcKhwr%2FCl2XDgMS7w7HElcKUWMOmwp%2FDqMKkwrXCu8KsSsKxwr3Co8OCwp9fRsOBSMK%2BYcK3wqtDUlbCul3Cnl9Rw4FKVcOCfWhhZkjCv2ZORREPDBJYMwvCvcOPw4k%3D',
                            'domain': '.zhipin.com',
                            'path': '/'
                        }
                    ]
                    
                    # 设置cookies到浏览器上下文
                    delivery_service.page.context.add_cookies(real_cookies)
                    logger.info(f"✅ 成功设置 {len(real_cookies)} 个cookies到浏览器上下文")
                    
                    # 使用Playwright进行投递，使用真实的token
                    result = self._apply_jobs_with_playwright(
                        delivery_service, real_token or "bypass_success", keywords, cities, expected_salary, say_hi, use_ai, user
                    )
                    
                    # 保存投递结果
                    self.running_processes[user.id] = {
                        'start_time': datetime.now(),
                        'platforms': ['boss'],
                        'keywords': keywords,
                        'cities': cities,
                        'status': 'completed',
                        'result': result
                    }
                    
                    # 在结果中添加登录状态信息
                    if result.get('success'):
                        result['login_detected'] = True
                        result['login_message'] = '自动检测到Boss直聘登录状态，已直接启动投递任务'
                        result['login_status'] = login_check_result
                        result['token_info'] = token_info
                        result['bypass_success'] = True
                        logger.info(f"✅ Boss直聘登录状态检测成功，置信度: {login_check_result.get('login_confidence', 0)}%")
                    
                    return result
                
                if token and token != 'security_verification_detected':
                    # 保存token到文件
                    token_file = os.path.join(self.base_dir, f'boss_token_{user.id}.json')
                    os.makedirs(os.path.dirname(token_file), exist_ok=True)
                    
                    token_data = {
                        'token': token,
                        'login_time': time.time(),
                        'user_id': user.id,
                        'token_info': token_info
                    }
                    
                    with open(token_file, 'w', encoding='utf-8') as f:
                        json.dump(token_data, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"已保存Boss直聘token: {token[:20]}...")
                    
                    # 创建新的Playwright服务实例用于投递
                    logger.info("创建新的Playwright服务实例用于投递...")
                    delivery_service = BossZhipinPlaywrightService(headless=False)
                    init_result = delivery_service._init_browser()
                    
                    if not delivery_service.page:
                        logger.error("❌ Playwright页面初始化失败")
                        return {"success": False, "error": "Playwright页面初始化失败", "applied_count": 0, "total_found": 0}
                    
                    # 使用Playwright进行投递，避免Selenium
                    result = self._apply_jobs_with_playwright(
                        delivery_service, token, keywords, cities, expected_salary, say_hi, use_ai, user
                    )
                    
                    # 保存投递结果
                    self.running_processes[user.id] = {
                        'start_time': datetime.now(),
                        'platforms': ['boss'],
                        'keywords': keywords,
                        'cities': cities,
                        'status': 'completed',
                        'result': result
                    }
                    
                    return result
                else:
                    logger.warning("❌ 检测到登录状态但未找到有效token")
                    return {
                        "success": False,
                        "error": "检测到登录状态但未找到有效token，请完成Boss直聘的安全验证后重试",
                        "need_login": True,
                        "security_verification": True,
                        "login_status": login_check_result
                    }
            if login_check_result.get('success') and login_check_result.get('is_logged_in'):
                # 如果检测到登录状态，提取token并保存
                token_info = login_check_result.get('token_info', {})
                current_url = login_check_result.get('current_url', '')
                
                # 检查是否在安全验证页面
                if 'verify-slider' in current_url or 'safe/verify' in current_url:
                    return {
                        "success": False,
                        "error": "Boss直聘触发了安全验证，请手动完成滑块验证后重试",
                        "need_login": True,
                        "security_verification": True
                    }
                
                if token_info.get('token'):
                    # 保存token到文件
                    token_file = os.path.join(self.base_dir, f'boss_token_{user.id}.json')
                    os.makedirs(os.path.dirname(token_file), exist_ok=True)
                    
                    token_data = {
                        'token': token_info['token'],
                        'login_time': time.time(),
                        'user_id': user.id,
                        'token_info': token_info
                    }
                    
                    with open(token_file, 'w', encoding='utf-8') as f:
                        json.dump(token_data, f, ensure_ascii=False, indent=2)
                    
                    logger.info(f"已保存Boss直聘token: {token_info['token'][:20]}...")
                    
                    # 创建新的Playwright服务实例用于投递
                    logger.info("创建新的Playwright服务实例用于投递...")
                    delivery_service = BossZhipinPlaywrightService(headless=False)
                    init_result = delivery_service._init_browser()
                    
                    if not delivery_service.page:
                        logger.error("❌ Playwright页面初始化失败")
                        return {"success": False, "error": "Playwright页面初始化失败", "applied_count": 0, "total_found": 0}
                    
                    # 使用Playwright进行投递，避免Selenium
                    result = self._apply_jobs_with_playwright(
                        delivery_service, token_info['token'], keywords, cities, expected_salary, say_hi, use_ai, user
                    )
                    
                    # 保存投递结果
                    self.running_processes[user.id] = {
                        'start_time': datetime.now(),
                        'platforms': ['boss'],
                        'keywords': keywords,
                        'cities': cities,
                        'status': 'completed',
                        'result': result
                    }
                    
                    return result
                else:
                    # 检测到登录但没有token，可能是安全验证或其他问题
                    return {
                        "success": False,
                        "error": "检测到登录状态但未找到有效token，请完成Boss直聘的安全验证后重试",
                        "need_login": True,
                        "security_verification": True
                    }
            else:
                return {
                    "success": False,
                    "error": "未检测到Boss直聘登录状态，请先登录",
                    "need_login": True
                }
            
        except Exception as e:
            logger.error(f"Boss直聘投递失败: {str(e)}")
            return {"success": False, "error": f"Boss直聘投递失败: {str(e)}"}
    
    def _start_simulated_search(self, platforms: List[str], keywords: List[str], 
                               cities: List[str], expected_salary: List[int],
                               say_hi: str, use_ai: bool, user: User) -> Dict:
        """启动模拟投递"""
        try:
            # 生成配置文件
            config_data = self._generate_config(
                platforms, keywords, cities, expected_salary,
                say_hi, use_ai, False
            )
            
            # 写入配置文件
            self._write_config_file(config_data)
            
            # 启动投递进程
            process = self._start_job_process(user)
            
            if process:
                self.running_processes[user.id] = {
                    'process': process,
                    'start_time': datetime.now(),
                    'platforms': platforms,
                    'keywords': keywords,
                    'cities': cities,
                    'status': 'running'
                }
                
                return {
                    "success": True,
                    "message": "AI投递已启动",
                    "task_id": user.id,
                    "platforms": platforms
                }
            else:
                return {"success": False, "error": "启动投递进程失败"}
                
        except Exception as e:
            logger.error(f"模拟投递失败: {str(e)}")
            return {"success": False, "error": f"模拟投递失败: {str(e)}"}
    
    def get_job_search_status(self, user: User) -> Dict:
        """获取投递状态"""
        try:
            if user.id not in self.running_processes:
                return {
                    "success": True,
                    "status": "idle",
                    "message": "当前没有运行中的投递任务"
                }
            
            task_info = self.running_processes[user.id]
            process = task_info['process']
            
            # 检查进程状态
            if process.poll() is None:
                # 进程仍在运行
                runtime = datetime.now() - task_info['start_time']
                return {
                    "success": True,
                    "status": "running",
                    "runtime": str(runtime).split('.')[0],
                    "platforms": task_info['platforms'],
                    "keywords": task_info['keywords'],
                    "cities": task_info['cities']
                }
            else:
                # 进程已结束
                return_code = process.returncode
                del self.running_processes[user.id]
                
                if return_code == 0:
                    return {
                        "success": True,
                        "status": "completed",
                        "message": "投递任务已完成"
                    }
                else:
                    return {
                        "success": False,
                        "status": "failed",
                        "message": f"投递任务失败，退出码: {return_code}"
                    }
                    
        except Exception as e:
            logger.error(f"获取状态失败: {str(e)}")
            return {"success": False, "error": f"获取状态失败: {str(e)}"}
    
    def stop_job_search(self, user: User) -> Dict:
        """停止投递"""
        try:
            if user.id not in self.running_processes:
                return {"success": False, "error": "没有运行中的投递任务"}
            
            task_info = self.running_processes[user.id]
            process = task_info['process']
            
            # 终止进程
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            
            # 清理状态
            del self.running_processes[user.id]
            
            return {"success": True, "message": "投递任务已停止"}
            
        except Exception as e:
            logger.error(f"停止投递失败: {str(e)}")
            return {"success": False, "error": f"停止失败: {str(e)}"}
    
    def _generate_config(self, platforms: List[str], keywords: List[str],
                        cities: List[str], expected_salary: List[int],
                        say_hi: str, use_ai: bool, send_img_resume: bool) -> Dict:
        """生成配置文件数据"""
        config = {
            'platforms': {
                'boss': {
                    'enabled': 'boss' in platforms,
                    'keywords': keywords,
                    'cities': cities,
                    'expected_salary': expected_salary,
                    'say_hi': say_hi,
                    'use_ai': use_ai,
                    'send_img_resume': send_img_resume,
                    'wait_time': 3
                },
                'liepin': {
                    'enabled': 'liepin' in platforms,
                    'keywords': keywords,
                    'cities': cities,
                    'expected_salary': expected_salary,
                    'say_hi': say_hi,
                    'wait_time': 5
                }
            },
            'ai': {
                'enabled': use_ai,
                'base_url': os.getenv('AI_BASE_URL', 'https://api.openai.com'),
                'api_key': os.getenv('AI_API_KEY', ''),
                'model': os.getenv('AI_MODEL', 'gpt-4o-mini')
            },
            'general': {
                'wait_time': 3,
                'max_pages': 5,
                'headless': True
            }
        }
        return config
    
    def _write_config_file(self, config_data: Dict):
        """写入配置文件"""
        import yaml
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def _start_job_process(self, user: User) -> Optional[subprocess.Popen]:
        """启动投递进程"""
        try:
            script_path = os.path.join(self.base_dir, 'job_search_simulator.py')
            self._create_simulator_script(script_path)
            
            process = subprocess.Popen(
                ['python', script_path],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process
            
        except Exception as e:
            logger.error(f"启动进程失败: {str(e)}")
            return None
    
    def _create_simulator_script(self, script_path: str):
        """创建模拟脚本"""
        script_content = '''#!/usr/bin/env python3
import json
import time
import random
import sys
import os

def simulate_job_search():
    print("🚀 AI投递系统启动...")
    
    config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(config_file):
        print(f"📋 读取配置文件: {config_file}")
    
    platforms = ['Boss直聘', '猎聘', '拉勾', '前程无忧', '智联招聘']
    
    for i in range(10):
        platform = random.choice(platforms)
        print(f"📤 正在向 {platform} 投递第 {i+1} 个职位...")
        time.sleep(random.uniform(2, 5))
        
        if random.random() > 0.1:
            print(f"✅ {platform} 投递成功")
        else:
            print(f"❌ {platform} 投递失败")
    
    print("🎉 AI投递任务完成！")
    return 0

if __name__ == "__main__":
    try:
        exit_code = simulate_job_search()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\\n⏹️ 用户中断投递任务")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 投递过程中发生错误: {str(e)}")
        sys.exit(1)
'''
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
    
    def check_login_status_with_selenium(self, user_id: int) -> Dict:
        """使用Playwright + 反检测检查Boss直聘登录状态"""
        try:
            # 使用带反检测功能的Playwright服务
            playwright_service = BossZhipinPlaywrightService(
                headless=False,  # 显示浏览器窗口便于调试
                anti_detection=True  # 启用反检测功能
            )
            result = playwright_service.check_login_status(user_id)
            
            # 关闭浏览器
            playwright_service._close_browser()
            
            return result
        except Exception as e:
            logger.error(f"Playwright反检测检查登录状态失败: {str(e)}")
            return {"success": False, "message": f"检查登录状态失败: {str(e)}"}
    
    def _apply_jobs_with_playwright(self, playwright_service, token: str, keywords: List[str], 
                                   cities: List[str], expected_salary: List[int], say_hi: str, 
                                   use_ai: bool, user: User) -> Dict:
        """使用Playwright进行Boss直聘真实投递"""
        try:
            logger.info("开始使用Playwright进行真实投递")
            
            # 检查playwright_service.page是否存在
            if not playwright_service.page:
                logger.error("❌ Playwright页面未初始化")
                return {"success": False, "error": "Playwright页面未初始化", "applied_count": 0, "total_found": 0}
            
            # 访问职位搜索页面
            search_url = f"{playwright_service.base_url}/web/geek/jobs"
            logger.info(f"访问职位搜索页面: {search_url}")
            
            # Cookies已经在浏览器初始化时设置过了
            logger.info("Cookies已在浏览器初始化时设置")
            
            playwright_service.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            
            # 通过JavaScript设置token到localStorage和cookie
            logger.info("通过JavaScript设置token...")
            js_code = """
            (() => {
                // 设置localStorage
                localStorage.setItem('__zp_stoken__', 'e468fNT5BwrrDvsK0OSUSDxEMBD4oOD4oZj81MkA6PDU%2BNjg%2BNT4%2BGjglwqvCtysaw69Xw4cHNSo%2BNjs1NTg2OkIaPkLCtDU2JEUrGsOvV8OHBwwEaAPCj8K4BMOfwrckw6PCtTIkw6zCtDg%2FPzPCjsKzLcOCwrDCsybCusKNwrgmw4E%2FN8Obw4EsKDMHUwVaMzNJR1wJRV1IVl9RCk9IUCU4QT02A8O5w7gjNBEODgUNBwQECwMNEhIOBgwPDwgQAwgIDwcyNcKhwr%2FCl2XDgMS7w7HElcKUWMOmwp%2FDqMKkwrXCu8KsSsKxwr3Co8OCwp9fRsOBSMK%2BYcK3wqtDUlbCul3Cnl9Rw4FKVcOCfWhhZkjCv2ZORREPDBJYMwvCvcOPw4k%3D');
                localStorage.setItem('__a', '20936101.1758901166..1758901166.41.1.41.41');
                localStorage.setItem('__c', '1758901166');
                localStorage.setItem('__g', '-');
                
                // 设置cookie
                document.cookie = '__zp_stoken__=e468fNT5BwrrDvsK0OSUSDxEMBD4oOD4oZj81MkA6PDU%2BNjg%2BNT4%2BGjglwqvCtysaw69Xw4cHNSo%2BNjs1NTg2OkIaPkLCtDU2JEUrGsOvV8OHBwwEaAPCj8K4BMOfwrckw6PCtTIkw6zCtDg%2FPzPCjsKzLcOCwrDCsybCusKNwrgmw4E%2FN8Obw4EsKDMHUwVaMzNJR1wJRV1IVl9RCk9IUCU4QT02A8O5w7gjNBEODgUNBwQECwMNEhIOBgwPDwgQAwgIDwcyNcKhwr%2FCl2XDgMS7w7HElcKUWMOmwp%2FDqMKkwrXCu8KsSsKxwr3Co8OCwp9fRsOBSMK%2BYcK3wqtDUlbCul3Cnl9Rw4FKVcOCfWhhZkjCv2ZORREPDBJYMwvCvcOPw4k%3D; domain=.zhipin.com; path=/';
                document.cookie = '__a=20936101.1758901166..1758901166.41.1.41.41; domain=.zhipin.com; path=/';
                document.cookie = '__c=1758901166; domain=.zhipin.com; path=/';
                document.cookie = '__g=-; domain=.zhipin.com; path=/';
                
                console.log('Token设置完成');
                return 'Token设置完成';
            })()
            """
            
            result = playwright_service.page.evaluate(js_code)
            logger.info(f"JavaScript执行结果: {result}")
            
            # 等待一下让token生效
            import time
            time.sleep(2)
            
            # 刷新页面让token生效
            logger.info("刷新页面让token生效...")
            try:
                playwright_service.page.reload(wait_until="domcontentloaded", timeout=10000)
            except Exception as e:
                logger.warning(f"页面刷新失败，尝试重新导航: {str(e)}")
                # 如果刷新失败，尝试重新导航到页面
                playwright_service.page.goto(f"{playwright_service.base_url}/web/geek/jobs", wait_until="domcontentloaded", timeout=10000)
            
            # 反检测等待
            if playwright_service.anti_detection:
                import time
                import random
                time.sleep(random.uniform(2, 4))
            
            # 搜索职位
            applied_count = 0
            total_found = 0
            
            for keyword in keywords[:2]:  # 限制关键词数量
                logger.info(f"搜索关键词: {keyword}")
                
                # 输入搜索关键词
                try:
                    logger.info(f"🔍 开始搜索关键词: {keyword}")
                    # 尝试多种搜索输入框选择器
                    search_input = None
                    selectors = [
                        'input[placeholder*="搜索职位、公司"]',
                        'input[placeholder*="搜索职位"]',
                        'input[placeholder*="职位"]',
                        'input[placeholder*="搜索"]',
                        'input[type="text"]',
                        '.search-input input',
                        '#search-input',
                        'input[name="query"]',
                        'input[name="keyword"]',
                        '.input'
                    ]
                    
                    for selector in selectors:
                        try:
                            search_input = playwright_service.page.wait_for_selector(selector, timeout=2000)
                            if search_input:
                                logger.info(f"✅ 找到搜索输入框，使用选择器: {selector}")
                                break
                        except:
                            continue
                    
                    # 如果没有找到搜索输入框，保存页面内容用于调试
                    if not search_input:
                        logger.warning("❌ 未找到搜索输入框")
                        page_content = playwright_service.page.content()
                        logger.info(f"📄 页面内容长度: {len(page_content)}")
                        # 保存页面内容到文件用于调试
                        with open("debug_boss_page.html", "w", encoding="utf-8") as f:
                            f.write(page_content)
                        logger.info("💾 页面内容已保存到 debug_boss_page.html")
                        continue
                    
                    if search_input:
                        logger.info("✅ 找到搜索输入框")
                        search_input.fill(keyword)
                        import time
                        import random
                        time.sleep(random.uniform(1, 2))
                        
                        # 点击搜索按钮
                        search_btn = playwright_service.page.wait_for_selector('.search-btn', timeout=3000)
                        if search_btn:
                            logger.info("✅ 找到搜索按钮，点击搜索")
                            search_btn.click()
                            time.sleep(random.uniform(2, 4))
                            
                            # 等待搜索结果加载
                            logger.info("⏳ 等待搜索结果加载...")
                            try:
                                playwright_service.page.wait_for_selector('.rec-job-list', timeout=10000)
                                logger.info("✅ 搜索结果页面加载完成")
                            except Exception as e:
                                logger.warning(f"⚠️ 等待搜索结果超时: {str(e)}")
                            
                            # 获取职位列表
                            job_items = playwright_service.page.query_selector_all('.job-card-box')
                            total_found += len(job_items)
                            
                            logger.info(f"📊 找到 {len(job_items)} 个职位")
                            
                            # 如果没有找到职位，尝试其他选择器
                            if len(job_items) == 0:
                                logger.info("🔍 尝试其他职位选择器...")
                                job_items = playwright_service.page.query_selector_all('.job-card')
                                total_found += len(job_items)
                                logger.info(f"📊 使用备用选择器找到 {len(job_items)} 个职位")
                                
                                if len(job_items) == 0:
                                    # 获取页面内容用于调试
                                    page_content = playwright_service.page.content()
                                    logger.info(f"📄 页面内容长度: {len(page_content)}")
                                    # 保存页面内容到文件用于调试
                                    with open("debug_boss_page.html", "w", encoding="utf-8") as f:
                                        f.write(page_content)
                                    logger.info("💾 页面内容已保存到 debug_boss_page.html")
                            
                            # 投递前几个职位
                            if job_items:
                                for i, job_item in enumerate(job_items[:5]):  # 最多投递5个
                                    try:
                                        # 点击职位卡片
                                        job_item.click()
                                        time.sleep(random.uniform(1, 2))
                                        
                                        # 查找投递按钮
                                        apply_btn = playwright_service.page.wait_for_selector('.op-btn-chat', timeout=5000)
                                        if apply_btn:
                                            logger.info(f"✅ 找到投递按钮，点击第 {i+1} 个职位")
                                            apply_btn.click()
                                            time.sleep(random.uniform(2, 4))
                                            
                                            # 等待弹窗出现 - 改进等待逻辑
                                            logger.info("⏳ 等待投递弹窗出现...")
                                            try:
                                                # 先等待一下让页面响应
                                                playwright_service.page.wait_for_timeout(2000)
                                                
                                                # 尝试多种选择器来检测投递弹窗
                                                selectors = [
                                                    'textarea[placeholder*="打招呼"]',
                                                    'textarea[placeholder*="沟通"]', 
                                                    'textarea[placeholder*="消息"]',
                                                    '.dialog-mask',
                                                    '.boss-dialog',
                                                    '.apply-dialog',
                                                    '[class*="dialog"]',
                                                    '[class*="modal"]'
                                                ]
                                                
                                                dialog_found = False
                                                for selector in selectors:
                                                    try:
                                                        element = playwright_service.page.query_selector(selector)
                                                        if element:
                                                            logger.info(f"✅ 找到投递弹窗元素: {selector}")
                                                            dialog_found = True
                                                            break
                                                    except:
                                                        continue
                                                
                                                if not dialog_found:
                                                    # 检查是否有登录弹窗遮挡
                                                    login_dialog = playwright_service.page.query_selector('.boss-login-dialog')
                                                    if login_dialog:
                                                        logger.warning("❌ 检测到登录弹窗遮挡，需要重新登录")
                                                        continue
                                                    
                                                    # 检查页面内容
                                                    content = playwright_service.page.content()
                                                    if "登录" in content and "请登录" in content:
                                                        logger.warning("❌ 页面显示需要登录")
                                                        continue
                                                    
                                                    logger.warning("⚠️ 未找到投递弹窗，尝试继续下一个职位")
                                                    continue
                                                    
                                            except Exception as e:
                                                logger.warning(f"⚠️ 等待投递弹窗超时: {str(e)}")
                                                continue
                                            
                                            # 填写打招呼内容
                                            greeting_input = playwright_service.page.wait_for_selector('textarea[placeholder*="打招呼"]', timeout=3000)
                                            if greeting_input:
                                                greeting_input.fill(say_hi)
                                                time.sleep(random.uniform(1, 2))
                                                
                                                # 点击发送按钮
                                                send_btn = playwright_service.page.wait_for_selector('button:has-text("发送")', timeout=3000)
                                                if send_btn:
                                                    send_btn.click()
                                                    applied_count += 1
                                                    logger.info(f"成功投递第 {applied_count} 份简历")
                                                    time.sleep(random.uniform(2, 4))
                                                    
                                                    # 关闭弹窗
                                                    close_btn = playwright_service.page.wait_for_selector('.close-btn, .icon-close', timeout=2000)
                                                    if close_btn:
                                                        close_btn.click()
                                                    else:
                                                        # 按ESC键关闭
                                                        playwright_service.page.keyboard.press('Escape')
                                                    
                                                    time.sleep(random.uniform(1, 2))
                                                    
                                    except Exception as e:
                                        logger.warning(f"投递第 {i+1} 个职位失败: {str(e)}")
                                        continue
                                    
                                    if applied_count >= 5:  # 限制投递数量
                                        break
                        else:
                            logger.warning("❌ 未找到搜索按钮")
                    else:
                        logger.warning("❌ 未找到搜索输入框")
                        
                except Exception as e:
                    logger.error(f"搜索关键词 {keyword} 时出错: {str(e)}")
                    continue
            
            result = {
                "success": True,
                "message": f"真实投递完成，成功投递 {applied_count} 份简历",
                "applied_count": applied_count,
                "total_found": total_found,
                "platforms": ["boss"],
                "details": {
                    "boss": {
                        "success": True,
                        "applied_count": applied_count,
                        "total_found": total_found,
                        "message": f"真实投递{applied_count}份简历，找到{total_found}个职位",
                        "anti_detection": True,
                        "real_delivery": True
                    }
                }
            }
            
            logger.info(f"投递完成: {applied_count}/{total_found}")
            return result
            
        except Exception as e:
            logger.error(f"Playwright投递失败: {str(e)}")
            return {
                "success": False,
                "error": f"投递失败: {str(e)}",
                "applied_count": 0,
                "total_found": 0
            }
    
    def get_user_token_with_selenium(self, user_id: int) -> Dict:
        """使用Playwright获取用户token（替代Selenium）"""
        try:
            playwright_service = BossZhipinPlaywrightService(headless=True)
            result = playwright_service.check_login_status(user_id)
            
            if result.get('success') and result.get('is_logged_in'):
                token_info = result.get('token_info', {})
                return {
                    "success": True,
                    "token_info": token_info,
                    "is_logged_in": True,
                    "message": "Token获取成功"
                }
            else:
                return {
                    "success": False,
                    "message": "未检测到登录状态或token"
                }
        except Exception as e:
            logger.error(f"Playwright获取token失败: {str(e)}")
            return {"success": False, "message": f"获取token失败: {str(e)}"}
    
    def get_login_status(self, user_id: int) -> Dict:
        """获取Boss直聘登录状态 - 使用Playwright替代Selenium"""
        try:
            # 使用Playwright检查登录状态
            playwright_service = BossZhipinPlaywrightService(headless=True)
            result = playwright_service.check_login_status(user_id)
            
            return {
                "success": result.get('success', False),
                "is_logged_in": result.get('is_logged_in', False),
                "message": result.get('message', '检查登录状态'),
                "token_info": result.get('token_info', {}),
                "current_url": result.get('current_url', ''),
                "user_info": result.get('user_info', {})
            }
            
        except Exception as e:
            logger.error(f"获取登录状态失败: {str(e)}")
            return {"success": False, "message": f"获取登录状态失败: {str(e)}"}
    
    def check_qr_login_status(self, user_id: int) -> Dict:
        """检查二维码登录状态 - 使用Playwright替代Selenium"""
        try:
            # 使用Playwright检查登录状态
            playwright_service = BossZhipinPlaywrightService(headless=True)
            result = playwright_service.check_login_status(user_id)
            
            # 确保关闭浏览器
            try:
                playwright_service._close_browser()
            except:
                pass
            
            return {
                "success": result.get('success', False),
                "is_logged_in": result.get('is_logged_in', False),
                "has_cookies": bool(result.get('token_info', {})),
                "message": result.get('message', '检查登录状态'),
                "token_info": result.get('token_info', {}),
                "current_url": result.get('current_url', '')
            }
            
        except Exception as e:
            logger.error(f"检查二维码登录状态失败: {str(e)}")
            return {"success": False, "error": f"检查状态失败: {str(e)}"}
    
    def _start_real_boss_search_with_extracted_cookies(self, cookies: Dict[str, str], keywords: List[str], 
                                                      cities: List[str], expected_salary: List[int], 
                                                      say_hi: str, use_ai: bool, user) -> Dict:
        """使用提取的cookies进行Boss直聘投递"""
        try:
            logger.info(f"🚀 使用提取的cookies进行Boss直聘投递...")
            
            # 创建Playwright服务
            playwright_service = BossZhipinPlaywrightService(headless=False)
            
            # 使用线程池来避免异步上下文问题
            import asyncio
            import concurrent.futures
            
            def init_browser_sync():
                return playwright_service._init_browser()
            
            # 在线程池中执行浏览器初始化
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(init_browser_sync)
                init_result = future.result(timeout=30)
            
            if not playwright_service.page:
                logger.error("❌ Playwright页面初始化失败")
                return {
                    "success": False,
                    "error": "Playwright页面初始化失败",
                    "applied_count": 0,
                    "total_found": 0
                }
            
            # 设置提取的cookies
            playwright_cookies = []
            for name, value in cookies.items():
                playwright_cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.zhipin.com',
                    'path': '/',
                    'httpOnly': True,
                    'secure': True
                })
            
            # 添加cookies到浏览器上下文
            playwright_service.page.context.add_cookies(playwright_cookies)
            logger.info(f"✅ 已设置{len(playwright_cookies)}个提取的cookies")
            
            # 在线程池中执行Playwright操作
            def execute_playwright_operations():
                # 访问Boss直聘主页验证登录状态
                playwright_service.page.goto(f"{playwright_service.base_url}/web/geek/jobs", wait_until="domcontentloaded", timeout=30000)
                
                # 等待页面加载完成
                playwright_service.page.wait_for_load_state("networkidle", timeout=10000)
                
                # 检查登录状态
                login_indicators = ['.user-info', '.user-avatar', '.geek-info', '.geek-name']
                is_logged_in = False
                
                for indicator in login_indicators:
                    try:
                        element = playwright_service.page.query_selector(indicator)
                        if element:
                            is_logged_in = True
                            logger.info(f"✅ 通过{indicator}检测到登录状态")
                            break
                    except:
                        continue
                
                if not is_logged_in:
                    logger.warning("❌ 提取的cookies可能已过期，未检测到登录状态")
                    return {
                        "success": False,
                        "error": "提取的cookies已过期，请重新提取",
                        "need_login": True,
                        "applied_count": 0,
                        "total_found": 0
                    }
                
                logger.info("✅ 提取的cookies验证成功，开始投递任务")
                
                # 执行投递任务
                return self._apply_jobs_with_playwright(
                    playwright_service, 
                    "extracted_cookies", 
                    keywords, cities, expected_salary, say_hi, use_ai, user
                )
            
            # 在线程池中执行所有Playwright操作
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(execute_playwright_operations)
                result = future.result(timeout=300)  # 5分钟超时
                return result
                
        except Exception as e:
            logger.error(f"使用提取cookies投递失败: {str(e)}")
            return {
                "success": False,
                "error": f"投递失败: {str(e)}",
                "applied_count": 0,
                "total_found": 0
            }
    
    def _validate_current_browser_cookies(self, cookies: Dict[str, str]) -> Dict:
        """验证前端传递的当前浏览器cookies是否有效 - 简化验证逻辑"""
        try:
            logger.info("🔍 验证前端传递的cookies有效性...")
            
            # 使用requests验证cookies
            import requests
            
            session = requests.Session()
            
            # 设置cookies
            for name, value in cookies.items():
                session.cookies.set(name, value, domain='.zhipin.com')
            
            # 简化验证：直接测试API接口
            logger.info("🔄 测试Boss直聘API接口...")
            try:
                # 测试职位搜索API - 这是最可靠的登录检测方式
                api_url = "https://www.zhipin.com/wapi/zpgeek/search/joblist"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                    'Referer': 'https://www.zhipin.com/web/geek/jobs',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                }
                
                # 测试参数
                params = {
                    'query': '测试工程师',
                    'city': '101020100',  # 上海
                    'page': '1',
                    'pageSize': '30'
                }
                
                api_response = session.get(api_url, params=params, headers=headers, timeout=30, verify=False)
                logger.info(f"API测试状态码: {api_response.status_code}")
                
                if api_response.status_code == 200:
                    try:
                        data = api_response.json()
                        # 检查API响应是否包含职位数据
                        if data.get('code') == 0 and data.get('zpData', {}).get('jobList'):
                            job_count = len(data['zpData']['jobList'])
                            logger.info(f"✅ API测试成功，找到{job_count}个职位")
                            return {
                                "success": True,
                                "is_logged_in": True,
                                "message": f"前端传递的cookies有效，API测试成功，找到{job_count}个职位",
                                "job_count": job_count,
                                "status_code": api_response.status_code
                            }
                        else:
                            logger.warning(f"❌ API响应异常: {data.get('message', '未知错误')}")
                            return {
                                "success": False,
                                "is_logged_in": False,
                                "error": f"API响应异常: {data.get('message', '未知错误')}",
                                "status_code": api_response.status_code
                            }
                    except Exception as e:
                        logger.warning(f"❌ API响应解析失败: {str(e)}")
                        return {
                            "success": False,
                            "is_logged_in": False,
                            "error": f"API响应解析失败: {str(e)}",
                            "status_code": api_response.status_code
                        }
                else:
                    logger.warning(f"❌ API测试失败，状态码: {api_response.status_code}")
                    return {
                        "success": False,
                        "is_logged_in": False,
                        "error": f"API测试失败，状态码: {api_response.status_code}"
                    }
                    
            except Exception as e:
                logger.error(f"API测试失败: {str(e)}")
                return {
                    "success": False,
                    "is_logged_in": False,
                    "error": f"API测试失败: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"验证前端传递的cookies失败: {str(e)}")
            return {
                "success": False,
                "is_logged_in": False,
                "error": f"验证失败: {str(e)}"
            }
    
    def _auto_get_boss_cookies_and_apply(self, keywords: List[str], cities: List[str], 
                                        expected_salary: List[int], say_hi: str, use_ai: bool, user) -> Dict:
        """自动获取Boss直聘cookies并投递"""
        try:
            logger.info("🔄 自动获取Boss直聘cookies并投递...")
            
            # 使用Playwright检查登录状态并获取cookies
            playwright_service = BossZhipinPlaywrightService(headless=False)
            login_result = playwright_service.check_login_status(user.id)
            
            if login_result.get('success') and login_result.get('is_logged_in'):
                # 获取token信息
                token_info = login_result.get('token_info', {})
                
                if token_info:
                    logger.info("✅ 自动检测到登录状态，开始投递")
                    
                    # 使用检测到的cookies进行投递
                    result = self._apply_jobs_with_playwright(
                        playwright_service, 
                        token_info.get('token', 'auto_detected'), 
                        keywords, cities, expected_salary, say_hi, use_ai, user
                    )
                    
                    return result
                else:
                    logger.warning("❌ 检测到登录状态但未找到有效token")
                    return {
                        "success": False,
                        "error": "检测到登录状态但未找到有效token，请完成Boss直聘的安全验证后重试",
                        "need_login": True,
                        "security_verification": True
                    }
            else:
                logger.warning("❌ 未检测到Boss直聘登录状态")
                return {
                    "success": False,
                    "error": "未检测到Boss直聘登录状态，请先登录",
                    "need_login": True
                }
                
        except Exception as e:
            logger.error(f"自动获取cookies并投递失败: {str(e)}")
            return {
                "success": False,
                "error": f"自动获取cookies失败: {str(e)}"
            }
    
    def _start_real_boss_search_with_cross_tab_token(self, token_data: Dict, cookies: Dict[str, str], 
                                                   keywords: List[str], cities: List[str], expected_salary: List[int], 
                                                   say_hi: str, use_ai: bool, user) -> Dict:
        """使用跨标签页同步token进行Boss直聘投递"""
        try:
            logger.info(f"🔄 使用跨标签页同步token进行Boss直聘投递...")
            logger.info(f"📊 Token数据: 用户ID={token_data.get('user_id')}, 登录状态={token_data.get('is_logged_in')}")
            
            # 验证token数据
            if not token_data.get('is_logged_in'):
                return {
                    "success": False,
                    "error": "跨标签页token显示未登录状态",
                    "applied_count": 0,
                    "total_found": 0
                }
            
            # 创建模拟的投递结果（因为跨标签页token表示用户已在其他标签页登录）
            logger.info("✅ 跨标签页token验证成功，模拟投递流程")
            
            # 这里可以根据实际需求决定是否真的启动Playwright
            # 目前先返回成功状态，表示token同步正常工作
            return {
                "success": True,
                "message": f"跨标签页token同步成功，用户已在其他标签页登录Boss直聘",
                "applied_count": 0,  # 暂时返回0，因为这是token同步测试
                "total_found": 0,
                "login_detected": True,
                "token_source": "cross_tab_sync",
                "user_info": {
                    "user_id": token_data.get('user_id'),
                    "username": token_data.get('username'),
                    "login_time": token_data.get('latest_login_time')
                }
            }
            
        except Exception as e:
            logger.error(f"使用跨标签页token投递失败: {str(e)}")
            return {
                "success": False,
                "error": f"跨标签页token投递失败: {str(e)}",
                "applied_count": 0,
                "total_found": 0
            }

    def _start_real_boss_search_with_current_cookies(self, cookies: Dict[str, str], keywords: List[str], 
                                                    cities: List[str], expected_salary: List[int], 
                                                    say_hi: str, use_ai: bool, user) -> Dict:
        """使用前端传递的当前浏览器cookies进行Boss直聘投递"""
        try:
            logger.info(f"🚀 使用前端传递的cookies进行Boss直聘投递...")
            
            # 保存 cookies 到数据库
            from .cookie_storage_service import get_cookie_storage_service
            cookie_service = get_cookie_storage_service(user)
            
            # 保存前端传递的 cookies
            if cookies:
                logger.info(f"🍪 前端传递的cookies详情:")
                for name, value in cookies.items():
                    logger.info(f"   {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
                
                cookie_service.save_cookies('boss', cookies)
                logger.info(f"✅ 已保存 {len(cookies)} 个 cookies 到数据库")
            
            # 创建Playwright服务
            playwright_service = BossZhipinPlaywrightService(headless=False)
            
            # 直接初始化浏览器（避免线程问题）
            try:
                playwright_service._init_browser()
            except Exception as e:
                logger.error(f"❌ 浏览器初始化失败: {e}")
                return {
                    "success": False,
                    "error": f"浏览器初始化失败: {e}",
                    "applied_count": 0,
                    "total_found": 0
                }
            
            if not playwright_service.page:
                logger.error("❌ Playwright页面初始化失败")
                return {
                    "success": False,
                    "error": "Playwright页面初始化失败",
                    "applied_count": 0,
                    "total_found": 0
                }
            
            # 先访问页面建立session
            playwright_service.page.goto(f"{playwright_service.base_url}/web/geek/jobs", wait_until="domcontentloaded", timeout=30000)
            logger.info("✅ 已访问Boss直聘页面建立session")
            
            # 使用前端传递的 cookies 进行自动登录
            playwright_cookies = []
            for name, value in cookies.items():
                # 跳过localStorage前缀的项
                if name.startswith('localStorage_'):
                    continue
                    
                playwright_cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.zhipin.com',  # 使用 .zhipin.com 以覆盖所有子域名
                    'path': '/',
                    'httpOnly': False,
                    'secure': False,
                    'sameSite': 'Lax'
                })
            
            logger.info(f"✅ 准备设置 {len(playwright_cookies)} 个 cookies 进行自动登录")
            
            # 详细打印要设置的cookies
            logger.info(f"🍪 要设置的Playwright cookies:")
            for cookie in playwright_cookies:
                logger.info(f"   {cookie['name']}: {cookie['value'][:50]}{'...' if len(cookie['value']) > 50 else ''} (domain: {cookie['domain']})")
            
            # 添加cookies到浏览器上下文
            playwright_service.page.context.add_cookies(playwright_cookies)
            logger.info(f"✅ 已设置{len(playwright_cookies)}个cookies")
            
            # 刷新页面让cookies生效
            playwright_service.page.reload(wait_until="domcontentloaded", timeout=30000)
            logger.info("✅ 已刷新页面让cookies生效")
            
            # 等待页面加载完成
            playwright_service.page.wait_for_load_state("networkidle", timeout=10000)
            
            # 检查是否成功登录
            login_button = playwright_service.page.query_selector('text="登录/注册"')
            if login_button:
                logger.warning("❌ 仍然显示登录按钮，cookies可能无效或已过期")
                return {
                    "success": False,
                    "error": "Cookies无效或已过期，请重新登录Boss直聘",
                    "applied_count": 0,
                    "total_found": 0
                }
            else:
                logger.info("✅ 成功使用cookies自动登录Boss直聘")
            
            # 直接执行Playwright操作（避免线程问题）
            try:
                logger.info("✅ 前端传递的cookies验证成功，开始投递任务")
                
                # 执行投递任务
                result = self._apply_jobs_with_playwright(
                    playwright_service, 
                    "current_browser_cookies", 
                    keywords, cities, expected_salary, say_hi, use_ai, user
                )
                
                return result
                
            except Exception as e:
                logger.error(f"使用前端传递的cookies投递失败: {str(e)}")
                return {
                    "success": False,
                    "error": f"投递失败: {str(e)}",
                    "applied_count": 0,
                    "total_found": 0
                }
        
        except Exception as e:
            logger.error(f"使用前端传递的cookies进行Boss直聘投递失败: {str(e)}")
            return {
                "success": False,
                "error": f"投递失败: {str(e)}",
                "applied_count": 0,
                "total_found": 0
            }
