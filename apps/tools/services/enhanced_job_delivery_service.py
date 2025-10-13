"""
增强版AI找工作服务 - 融合get_jobs项目功能
支持多平台投递：BOSS直聘、猎聘、拉勾、智联招聘
"""
import json
import logging
import os
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth.models import User
from .boss_zhipin_playwright import BossZhipinPlaywrightService
from .anti_detection_service import AntiDetectionService

logger = logging.getLogger(__name__)


@dataclass
class PlatformConfig:
    """平台配置"""
    name: str
    icon: str
    description: str
    login_methods: List[str]
    max_applications: int
    wait_time: int
    enabled: bool = True


@dataclass
class JobSearchConfig:
    """搜索配置"""
    keywords: List[str]
    cities: List[str]
    salary_range: List[int]
    experience: str
    max_applications: int
    interval: int
    blacklist: List[str]
    greeting: str
    use_ai: bool = True


class EnhancedJobDeliveryService:
    """增强版AI找工作服务 - 融合get_jobs项目功能"""
    
    def __init__(self):
        self.base_dir = os.path.join(settings.BASE_DIR, 'get_jobs_integration')
        self.config_file = os.path.join(self.base_dir, 'enhanced_config.yaml')
        self.logs_dir = os.path.join(self.base_dir, 'logs')
        
        # 确保目录存在
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 平台配置
        self.platforms = {
            'boss': PlatformConfig(
                name='BOSS直聘',
                icon='🏢',
                description='推荐使用，投递无上限',
                login_methods=['qr', 'phone', 'iframe'],
                max_applications=200,
                wait_time=3
            ),
            'liepin': PlatformConfig(
                name='猎聘',
                icon='🎯',
                description='默认打招呼无上限',
                login_methods=['qr', 'phone'],
                max_applications=100,
                wait_time=5
            ),
            'lagou': PlatformConfig(
                name='拉勾',
                icon='📱',
                description='投递无上限，限制频率',
                login_methods=['qr', 'phone'],
                max_applications=150,
                wait_time=4
            ),
            'zhilian': PlatformConfig(
                name='智联招聘',
                icon='💼',
                description='投递上限100左右',
                login_methods=['qr', 'phone'],
                max_applications=100,
                wait_time=6
            )
        }
        
        # 运行状态跟踪
        self.running_tasks = {}
        
        # 初始化反检测服务
        self.anti_detection_service = AntiDetectionService()
    
    def start_multi_platform_delivery(self, platforms: List[str], config: JobSearchConfig, user: User) -> Dict:
        """启动多平台投递"""
        try:
            logger.info(f"用户 {user.username} 启动多平台投递: {platforms}")
            
            # 检查是否已有运行中的任务
            if user.id in self.running_tasks:
                return {"success": False, "error": "已有投递任务在运行中"}
            
            # 验证平台
            valid_platforms = []
            for platform in platforms:
                if platform in self.platforms and self.platforms[platform].enabled:
                    valid_platforms.append(platform)
                else:
                    logger.warning(f"平台 {platform} 不可用或已禁用")
            
            if not valid_platforms:
                return {"success": False, "error": "没有可用的投递平台"}
            
            # 创建任务
            task_id = f"delivery_{user.id}_{int(time.time())}"
            task_info = {
                'task_id': task_id,
                'user_id': user.id,
                'platforms': valid_platforms,
                'config': config,
                'start_time': datetime.now(),
                'status': 'running',
                'results': {},
                'total_applied': 0,
                'total_found': 0
            }
            
            self.running_tasks[user.id] = task_info
            
            # 异步执行投递任务
            self._execute_delivery_task(task_info)
            
            return {
                "success": True,
                "message": "多平台投递任务已启动",
                "task_id": task_id,
                "platforms": valid_platforms,
                "config": {
                    "keywords": config.keywords,
                    "cities": config.cities,
                    "max_applications": config.max_applications
                }
            }
            
        except Exception as e:
            logger.error(f"启动多平台投递失败: {str(e)}")
            return {"success": False, "error": f"启动失败: {str(e)}"}
    
    def _execute_delivery_task(self, task_info: Dict):
        """执行投递任务"""
        try:
            user_id = task_info['user_id']
            platforms = task_info['platforms']
            config = task_info['config']
            
            logger.info(f"开始执行投递任务: {task_info['task_id']}")
            
            total_applied = 0
            total_found = 0
            
            for platform in platforms:
                try:
                    logger.info(f"开始投递平台: {platform}")
                    
                    # 检查登录状态
                    login_result = self._check_platform_login(platform, user_id)
                    if not login_result.get('is_logged_in'):
                        logger.warning(f"平台 {platform} 未登录，跳过")
                        task_info['results'][platform] = {
                            'success': False,
                            'error': '未登录',
                            'applied_count': 0,
                            'found_count': 0
                        }
                        continue
                    
                    # 执行平台投递
                    platform_result = self._deliver_to_platform(platform, config, user_id)
                    
                    task_info['results'][platform] = platform_result
                    total_applied += platform_result.get('applied_count', 0)
                    total_found += platform_result.get('found_count', 0)
                    
                    # 平台间等待
                    if platform != platforms[-1]:  # 不是最后一个平台
                        wait_time = self.platforms[platform].wait_time
                        logger.info(f"平台 {platform} 投递完成，等待 {wait_time} 秒后继续下一个平台")
                        time.sleep(wait_time)
                    
                except Exception as e:
                    logger.error(f"平台 {platform} 投递失败: {str(e)}")
                    task_info['results'][platform] = {
                        'success': False,
                        'error': str(e),
                        'applied_count': 0,
                        'found_count': 0
                    }
            
            # 更新任务状态
            task_info['status'] = 'completed'
            task_info['total_applied'] = total_applied
            task_info['total_found'] = total_found
            task_info['end_time'] = datetime.now()
            
            logger.info(f"投递任务完成: 总计投递 {total_applied} 份，找到 {total_found} 个职位")
            
        except Exception as e:
            logger.error(f"执行投递任务失败: {str(e)}")
            task_info['status'] = 'failed'
            task_info['error'] = str(e)
    
    def _check_platform_login(self, platform: str, user_id: int) -> Dict:
        """检查平台登录状态"""
        try:
            if platform == 'boss':
                # 使用现有的Boss直聘服务
                playwright_service = BossZhipinPlaywrightService(headless=True)
                result = playwright_service.check_login_status(user_id)
                return {
                    'is_logged_in': result.get('is_logged_in', False),
                    'token_info': result.get('token_info', {}),
                    'message': result.get('message', '')
                }
            else:
                # 其他平台暂时返回未登录
                return {
                    'is_logged_in': False,
                    'message': f'{platform} 平台登录检查暂未实现'
                }
                
        except Exception as e:
            logger.error(f"检查平台 {platform} 登录状态失败: {str(e)}")
            return {'is_logged_in': False, 'error': str(e)}
    
    def _deliver_to_platform(self, platform: str, config: JobSearchConfig, user_id: int) -> Dict:
        """向指定平台投递"""
        try:
            if platform == 'boss':
                return self._deliver_to_boss(config, user_id)
            elif platform == 'liepin':
                return self._deliver_to_liepin(config, user_id)
            elif platform == 'lagou':
                return self._deliver_to_lagou(config, user_id)
            elif platform == 'zhilian':
                return self._deliver_to_zhilian(config, user_id)
            else:
                return {
                    'success': False,
                    'error': f'不支持的平台: {platform}',
                    'applied_count': 0,
                    'found_count': 0
                }
                
        except Exception as e:
            logger.error(f"平台 {platform} 投递失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'applied_count': 0,
                'found_count': 0
            }
    
    def _deliver_to_boss(self, config: JobSearchConfig, user_id: int) -> Dict:
        """向BOSS直聘投递"""
        try:
            logger.info("开始BOSS直聘投递")
            
            # 使用Playwright服务
            playwright_service = BossZhipinPlaywrightService(headless=True, anti_detection=True)
            
            # 检查登录状态
            login_result = playwright_service.check_login_status(user_id)
            if not login_result.get('is_logged_in'):
                return {
                    'success': False,
                    'error': 'BOSS直聘未登录',
                    'applied_count': 0,
                    'found_count': 0
                }
            
            # 访问职位搜索页面
            search_url = f"{playwright_service.base_url}/web/geek/jobs"
            playwright_service.page.goto(search_url, wait_until="networkidle", timeout=10000)
            
            # 反检测等待
            if playwright_service.anti_detection:
                playwright_service._random_delay(2, 4)
                playwright_service._simulate_human_behavior()
            
            applied_count = 0
            total_found = 0
            
            # 遍历关键词
            for keyword in config.keywords[:3]:  # 限制关键词数量
                logger.info(f"搜索关键词: {keyword}")
                
                try:
                    # 输入搜索关键词
                    search_input = playwright_service.page.wait_for_selector('input[placeholder*="搜索职位"]', timeout=5000)
                    if search_input:
                        search_input.fill(keyword)
                        playwright_service._random_delay(1, 2)
                        
                        # 点击搜索按钮
                        search_btn = playwright_service.page.wait_for_selector('button[type="submit"]', timeout=3000)
                        if search_btn:
                            search_btn.click()
                            playwright_service._random_delay(2, 4)
                            
                            # 等待搜索结果加载
                            playwright_service.page.wait_for_selector('.job-list', timeout=10000)
                            
                            # 获取职位列表
                            job_items = playwright_service.page.query_selector_all('.job-card-wrapper')
                            total_found += len(job_items)
                            
                            logger.info(f"找到 {len(job_items)} 个职位")
                            
                            # 投递职位
                            for i, job_item in enumerate(job_items[:config.max_applications // len(config.keywords)]):
                                try:
                                    # 点击职位卡片
                                    job_item.click()
                                    playwright_service._random_delay(1, 2)
                                    
                                    # 查找投递按钮
                                    apply_btn = playwright_service.page.wait_for_selector('button:has-text("立即沟通")', timeout=3000)
                                    if apply_btn:
                                        apply_btn.click()
                                        playwright_service._random_delay(1, 2)
                                        
                                        # 填写打招呼内容
                                        greeting_input = playwright_service.page.wait_for_selector('textarea[placeholder*="打招呼"]', timeout=3000)
                                        if greeting_input:
                                            greeting_input.fill(config.greeting)
                                            playwright_service._random_delay(1, 2)
                                            
                                            # 点击发送按钮
                                            send_btn = playwright_service.page.wait_for_selector('button:has-text("发送")', timeout=3000)
                                            if send_btn:
                                                send_btn.click()
                                                applied_count += 1
                                                logger.info(f"成功投递第 {applied_count} 份简历")
                                                playwright_service._random_delay(2, 4)
                                                
                                                # 关闭弹窗
                                                close_btn = playwright_service.page.wait_for_selector('.close-btn, .icon-close', timeout=2000)
                                                if close_btn:
                                                    close_btn.click()
                                                else:
                                                    playwright_service.page.keyboard.press('Escape')
                                                
                                                playwright_service._random_delay(1, 2)
                                    
                                    # 投递间隔
                                    time.sleep(config.interval)
                                    
                                except Exception as e:
                                    logger.warning(f"投递第 {i+1} 个职位失败: {str(e)}")
                                    continue
                                
                                if applied_count >= config.max_applications:
                                    break
                        
                except Exception as e:
                    logger.warning(f"搜索关键词 {keyword} 失败: {str(e)}")
                    continue
                
                if applied_count >= config.max_applications:
                    break
            
            # 关闭浏览器
            playwright_service._close_browser()
            
            return {
                'success': True,
                'applied_count': applied_count,
                'found_count': total_found,
                'message': f'BOSS直聘投递完成，成功投递 {applied_count} 份，找到 {total_found} 个职位'
            }
            
        except Exception as e:
            logger.error(f"BOSS直聘投递失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'applied_count': 0,
                'found_count': 0
            }
    
    def _deliver_to_liepin(self, config: JobSearchConfig, user_id: int) -> Dict:
        """向猎聘投递（模拟）"""
        try:
            logger.info("开始猎聘投递（模拟）")
            
            # 模拟投递过程
            applied_count = random.randint(3, 8)
            total_found = random.randint(20, 50)
            
            # 模拟投递延迟
            time.sleep(random.uniform(10, 20))
            
            return {
                'success': True,
                'applied_count': applied_count,
                'found_count': total_found,
                'message': f'猎聘投递完成（模拟），成功投递 {applied_count} 份，找到 {total_found} 个职位'
            }
            
        except Exception as e:
            logger.error(f"猎聘投递失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'applied_count': 0,
                'found_count': 0
            }
    
    def _deliver_to_lagou(self, config: JobSearchConfig, user_id: int) -> Dict:
        """向拉勾投递（模拟）"""
        try:
            logger.info("开始拉勾投递（模拟）")
            
            # 模拟投递过程
            applied_count = random.randint(2, 6)
            total_found = random.randint(15, 40)
            
            # 模拟投递延迟
            time.sleep(random.uniform(8, 15))
            
            return {
                'success': True,
                'applied_count': applied_count,
                'found_count': total_found,
                'message': f'拉勾投递完成（模拟），成功投递 {applied_count} 份，找到 {total_found} 个职位'
            }
            
        except Exception as e:
            logger.error(f"拉勾投递失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'applied_count': 0,
                'found_count': 0
            }
    
    def _deliver_to_zhilian(self, config: JobSearchConfig, user_id: int) -> Dict:
        """向智联招聘投递（模拟）"""
        try:
            logger.info("开始智联招聘投递（模拟）")
            
            # 模拟投递过程
            applied_count = random.randint(1, 5)
            total_found = random.randint(10, 30)
            
            # 模拟投递延迟
            time.sleep(random.uniform(6, 12))
            
            return {
                'success': True,
                'applied_count': applied_count,
                'found_count': total_found,
                'message': f'智联招聘投递完成（模拟），成功投递 {applied_count} 份，找到 {total_found} 个职位'
            }
            
        except Exception as e:
            logger.error(f"智联招聘投递失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'applied_count': 0,
                'found_count': 0
            }
    
    def get_delivery_status(self, user: User) -> Dict:
        """获取投递状态"""
        try:
            if user.id not in self.running_tasks:
                return {
                    "success": True,
                    "status": "idle",
                    "message": "当前没有运行中的投递任务"
                }
            
            task_info = self.running_tasks[user.id]
            
            # 计算运行时间
            runtime = datetime.now() - task_info['start_time']
            
            return {
                "success": True,
                "status": task_info['status'],
                "task_id": task_info['task_id'],
                "platforms": task_info['platforms'],
                "runtime": str(runtime).split('.')[0],
                "total_applied": task_info.get('total_applied', 0),
                "total_found": task_info.get('total_found', 0),
                "results": task_info.get('results', {}),
                "config": {
                    "keywords": task_info['config'].keywords,
                    "cities": task_info['config'].cities,
                    "max_applications": task_info['config'].max_applications
                }
            }
            
        except Exception as e:
            logger.error(f"获取投递状态失败: {str(e)}")
            return {"success": False, "error": f"获取状态失败: {str(e)}"}
    
    def stop_delivery(self, user: User) -> Dict:
        """停止投递"""
        try:
            if user.id not in self.running_tasks:
                return {"success": False, "error": "没有运行中的投递任务"}
            
            task_info = self.running_tasks[user.id]
            task_info['status'] = 'stopped'
            task_info['end_time'] = datetime.now()
            
            # 清理任务
            del self.running_tasks[user.id]
            
            return {"success": True, "message": "投递任务已停止"}
            
        except Exception as e:
            logger.error(f"停止投递失败: {str(e)}")
            return {"success": False, "error": f"停止失败: {str(e)}"}
    
    def get_platform_info(self) -> Dict:
        """获取平台信息"""
        try:
            platform_info = {}
            for platform_id, platform_config in self.platforms.items():
                platform_info[platform_id] = {
                    'name': platform_config.name,
                    'icon': platform_config.icon,
                    'description': platform_config.description,
                    'login_methods': platform_config.login_methods,
                    'max_applications': platform_config.max_applications,
                    'wait_time': platform_config.wait_time,
                    'enabled': platform_config.enabled
                }
            
            return {
                "success": True,
                "platforms": platform_info
            }
            
        except Exception as e:
            logger.error(f"获取平台信息失败: {str(e)}")
            return {"success": False, "error": f"获取平台信息失败: {str(e)}"}
    
    def create_search_config(self, data: Dict) -> JobSearchConfig:
        """创建搜索配置"""
        try:
            # 处理关键词
            keywords = data.get('keywords', ['Python开发'])
            if isinstance(keywords, str):
                keywords = [k.strip() for k in keywords.split(',') if k.strip()]
            
            # 处理城市
            cities = data.get('cities', ['北京'])
            if isinstance(cities, str):
                cities = [cities]
            
            # 处理薪资范围
            salary_range = data.get('expected_salary', [15000, 25000])
            if not isinstance(salary_range, list):
                salary_val = salary_range or 15000
                salary_range = [salary_val, salary_val + 10000]
            
            # 处理黑名单
            blacklist = data.get('blacklist', [])
            if isinstance(blacklist, str):
                blacklist = [item.strip() for item in blacklist.split('\n') if item.strip()]
            
            return JobSearchConfig(
                keywords=keywords,
                cities=cities,
                salary_range=salary_range,
                experience=data.get('experience', ''),
                max_applications=data.get('max_applications', 50),
                interval=data.get('interval', 3),
                blacklist=blacklist,
                greeting=data.get('say_hi', '您好，我对这个职位很感兴趣，希望能有机会进一步沟通。'),
                use_ai=data.get('use_ai', True)
            )
            
        except Exception as e:
            logger.error(f"创建搜索配置失败: {str(e)}")
            # 返回默认配置
            return JobSearchConfig(
                keywords=['Python开发'],
                cities=['北京'],
                salary_range=[15000, 25000],
                experience='',
                max_applications=50,
                interval=3,
                blacklist=[],
                greeting='您好，我对这个职位很感兴趣，希望能有机会进一步沟通。',
                use_ai=True
            )
