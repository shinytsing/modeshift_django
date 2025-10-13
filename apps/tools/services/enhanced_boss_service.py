"""
增强版Boss直聘服务
集成AI智能匹配、个性化打招呼语和图片简历功能
参考get_jobs项目实现
"""
import logging
import time
import random
import os
from typing import Dict, List, Optional
from playwright.sync_api import Page
from .boss_zhipin_playwright import BossZhipinPlaywrightService
from .ai_job_matching_service import AIJobMatchingService, ImageResumeService

logger = logging.getLogger(__name__)


class EnhancedBossService(BossZhipinPlaywrightService):
    """增强版Boss直聘服务"""
    
    def __init__(self, headless=True, proxy=None, anti_detection=True):
        super().__init__(headless, proxy, anti_detection)
        self.ai_matching_service = AIJobMatchingService()
        self.image_resume_service = ImageResumeService()
        
        # 配置参数
        self.max_applications_per_day = 50  # 每日最大投递数
        self.application_interval = (3, 8)  # 投递间隔（秒）
        self.blacklist_companies = []  # 黑名单公司
        self.blacklist_keywords = ['外包', '外派', '派遣']  # 黑名单关键词
    
    def start_enhanced_job_search(self, search_config: Dict, user_profile: Dict) -> Dict:
        """启动增强版职位搜索和投递"""
        try:
            logger.info("🚀 启动增强版Boss直聘职位搜索")
            
            # 检查登录状态
            login_status = self.check_login_status(user_profile.get('user_id', 0))
            if not login_status.get('is_logged_in'):
                return {
                    "success": False,
                    "error": "未登录Boss直聘，请先完成登录",
                    "need_login": True
                }
            
            # 开始搜索和投递
            result = self._search_and_apply_jobs(search_config, user_profile)
            
            return result
            
        except Exception as e:
            logger.error(f"增强版职位搜索失败: {str(e)}")
            return {
                "success": False,
                "error": f"职位搜索失败: {str(e)}"
            }
    
    def _search_and_apply_jobs(self, search_config: Dict, user_profile: Dict) -> Dict:
        """搜索并投递职位"""
        try:
            if not self._init_browser():
                return {"success": False, "error": "浏览器初始化失败"}
            
            try:
                # 构建搜索URL
                search_url = self._build_search_url(search_config)
                logger.info(f"🔍 搜索URL: {search_url}")
                
                # 访问搜索页面
                self.page.goto(search_url, wait_until="networkidle", timeout=15000)
                time.sleep(3)
                
                # 获取职位列表
                jobs = self._extract_job_list()
                logger.info(f"📋 找到 {len(jobs)} 个职位")
                
                # 过滤职位
                filtered_jobs = self._filter_jobs(jobs, user_profile)
                logger.info(f"✅ 过滤后剩余 {len(filtered_jobs)} 个职位")
                
                # 开始投递
                application_results = self._apply_to_jobs(filtered_jobs, user_profile, search_config)
                
                return {
                    "success": True,
                    "total_jobs": len(jobs),
                    "filtered_jobs": len(filtered_jobs),
                    "applied_jobs": len([r for r in application_results if r.get('success')]),
                    "results": application_results
                }
                
            finally:
                self._close_browser()
                
        except Exception as e:
            logger.error(f"搜索和投递职位失败: {str(e)}")
            return {"success": False, "error": f"搜索投递失败: {str(e)}"}
    
    def _build_search_url(self, search_config: Dict) -> str:
        """构建搜索URL"""
        base_url = f"{self.base_url}/web/geek/jobs"
        
        params = []
        
        # 关键词
        if search_config.get('keywords'):
            keywords = search_config['keywords']
            if isinstance(keywords, list):
                keywords = ','.join(keywords)
            params.append(f"query={keywords}")
        
        # 城市
        if search_config.get('cities'):
            cities = search_config['cities']
            if isinstance(cities, list):
                cities = ','.join(cities)
            params.append(f"city={cities}")
        
        # 薪资
        if search_config.get('salary'):
            salary = search_config['salary']
            if isinstance(salary, list) and len(salary) == 2:
                params.append(f"salary={salary[0]}-{salary[1]}")
        
        # 经验
        if search_config.get('experience'):
            exp = search_config['experience']
            params.append(f"experience={exp}")
        
        # 学历
        if search_config.get('education'):
            edu = search_config['education']
            params.append(f"education={edu}")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        else:
            return base_url
    
    def _extract_job_list(self) -> List[Dict]:
        """提取职位列表"""
        jobs = []
        
        try:
            # 等待职位列表加载
            self.page.wait_for_selector('.job-list', timeout=10000)
            
            # 获取职位元素
            job_elements = self.page.query_selector_all('.job-card-wrapper')
            
            for element in job_elements:
                try:
                    job_info = self._extract_job_info(element)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    logger.debug(f"提取职位信息失败: {str(e)}")
                    continue
            
            logger.info(f"成功提取 {len(jobs)} 个职位信息")
            
        except Exception as e:
            logger.error(f"提取职位列表失败: {str(e)}")
        
        return jobs
    
    def _extract_job_info(self, element) -> Optional[Dict]:
        """提取单个职位信息"""
        try:
            # 职位标题
            title_element = element.query_selector('.job-title')
            title = title_element.text_content().strip() if title_element else ""
            
            # 公司名称
            company_element = element.query_selector('.company-name')
            company = company_element.text_content().strip() if company_element else ""
            
            # 薪资
            salary_element = element.query_selector('.salary')
            salary = salary_element.text_content().strip() if salary_element else ""
            
            # 工作地点
            location_element = element.query_selector('.job-area')
            location = location_element.text_content().strip() if location_element else ""
            
            # 经验要求
            experience_element = element.query_selector('.job-limit')
            experience = experience_element.text_content().strip() if experience_element else ""
            
            # 职位链接
            link_element = element.query_selector('a')
            job_url = link_element.get_attribute('href') if link_element else ""
            if job_url and not job_url.startswith('http'):
                job_url = f"{self.base_url}{job_url}"
            
            return {
                "title": title,
                "company": company,
                "salary": salary,
                "location": location,
                "experience": experience,
                "url": job_url,
                "requirements": f"{title} {experience}",
                "description": f"{company} {location}"
            }
            
        except Exception as e:
            logger.debug(f"提取职位信息失败: {str(e)}")
            return None
    
    def _filter_jobs(self, jobs: List[Dict], user_profile: Dict) -> List[Dict]:
        """过滤职位"""
        filtered_jobs = []
        
        for job in jobs:
            # 检查黑名单公司
            if self._is_blacklisted_company(job['company']):
                logger.debug(f"跳过黑名单公司: {job['company']}")
                continue
            
            # 检查黑名单关键词
            if self._contains_blacklisted_keywords(job['title']):
                logger.debug(f"跳过黑名单关键词职位: {job['title']}")
                continue
            
            # AI匹配度分析
            match_result = self.ai_matching_service.analyze_job_match(job, user_profile)
            
            # 只投递匹配度较高的职位
            if match_result['is_good_match']:
                job['match_score'] = match_result['match_score']
                job['match_reasons'] = match_result['match_reasons']
                filtered_jobs.append(job)
                logger.info(f"✅ 匹配职位: {job['title']} ({job['company']}) - 匹配度: {match_result['match_score']}")
            else:
                logger.debug(f"❌ 低匹配度职位: {job['title']} ({job['company']}) - 匹配度: {match_result['match_score']}")
        
        return filtered_jobs
    
    def _is_blacklisted_company(self, company_name: str) -> bool:
        """检查是否为黑名单公司"""
        if not company_name:
            return False
        
        company_lower = company_name.lower()
        for blacklist_company in self.blacklist_companies:
            if blacklist_company.lower() in company_lower:
                return True
        
        return False
    
    def _contains_blacklisted_keywords(self, job_title: str) -> bool:
        """检查是否包含黑名单关键词"""
        if not job_title:
            return False
        
        title_lower = job_title.lower()
        for keyword in self.blacklist_keywords:
            if keyword in title_lower:
                return True
        
        return False
    
    def _apply_to_jobs(self, jobs: List[Dict], user_profile: Dict, search_config: Dict) -> List[Dict]:
        """投递职位"""
        results = []
        applied_count = 0
        
        for job in jobs:
            try:
                # 检查投递限制
                if applied_count >= self.max_applications_per_day:
                    logger.warning(f"达到每日投递限制: {self.max_applications_per_day}")
                    break
                
                # 投递职位
                result = self._apply_to_single_job(job, user_profile, search_config)
                results.append(result)
                
                if result.get('success'):
                    applied_count += 1
                    logger.info(f"✅ 投递成功: {job['title']} ({job['company']})")
                else:
                    logger.warning(f"❌ 投递失败: {job['title']} ({job['company']}) - {result.get('error', '')}")
                
                # 随机间隔
                interval = random.uniform(*self.application_interval)
                logger.info(f"⏱️ 等待 {interval:.1f} 秒...")
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"投递职位失败: {str(e)}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "job": job
                })
        
        return results
    
    def _apply_to_single_job(self, job: Dict, user_profile: Dict, search_config: Dict) -> Dict:
        """投递单个职位"""
        try:
            # 访问职位详情页
            self.page.goto(job['url'], wait_until="networkidle", timeout=10000)
            time.sleep(2)
            
            # 查找投递按钮
            apply_button = self.page.query_selector('.btn-startchat, .btn-apply, .apply-btn')
            
            if not apply_button:
                return {
                    "success": False,
                    "error": "未找到投递按钮",
                    "job": job
                }
            
            # 点击投递按钮
            apply_button.click()
            time.sleep(2)
            
            # 检查是否需要选择简历
            resume_selection = self.page.query_selector('.resume-selection, .resume-option')
            if resume_selection:
                # 选择在线简历
                online_resume = self.page.query_selector('.resume-online, .online-resume')
                if online_resume:
                    online_resume.click()
                    time.sleep(1)
            
            # 生成个性化打招呼语
            greeting = self.ai_matching_service.generate_personalized_greeting(job, user_profile)
            
            # 查找消息输入框
            message_input = self.page.query_selector('.message-input, .chat-input, textarea')
            
            if message_input and greeting:
                # 输入打招呼语
                message_input.fill(greeting)
                time.sleep(1)
            
            # 检查是否需要发送图片简历
            if search_config.get('send_image_resume', False):
                self._send_image_resume(user_profile.get('user_id', 0))
            
            # 确认投递
            confirm_button = self.page.query_selector('.btn-confirm, .confirm-btn, .send-btn')
            if confirm_button:
                confirm_button.click()
                time.sleep(2)
            
            return {
                "success": True,
                "message": "投递成功",
                "greeting": greeting,
                "job": job
            }
            
        except Exception as e:
            logger.error(f"投递单个职位失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "job": job
            }
    
    def _send_image_resume(self, user_id: int):
        """发送图片简历"""
        try:
            # 获取简历图片路径
            resume_path = self.image_resume_service.get_resume_image_path(user_id)
            
            if not resume_path:
                logger.warning("未找到简历图片")
                return
            
            # 如果是PDF，转换为图片
            if resume_path.endswith('.pdf'):
                resume_path = self.image_resume_service.convert_pdf_to_image(resume_path)
                if not resume_path:
                    logger.warning("PDF转图片失败")
                    return
            
            # 查找文件上传按钮
            file_input = self.page.query_selector('input[type="file"]')
            
            if file_input:
                # 上传文件
                file_input.set_input_files(resume_path)
                time.sleep(2)
                logger.info(f"✅ 简历图片上传成功: {resume_path}")
            else:
                logger.warning("未找到文件上传按钮")
                
        except Exception as e:
            logger.error(f"发送图片简历失败: {str(e)}")
    
    def update_blacklist(self, companies: List[str]):
        """更新黑名单公司"""
        self.blacklist_companies = companies
        logger.info(f"更新黑名单公司: {companies}")
    
    def update_blacklist_keywords(self, keywords: List[str]):
        """更新黑名单关键词"""
        self.blacklist_keywords = keywords
        logger.info(f"更新黑名单关键词: {keywords}")
    
    def set_application_limits(self, max_per_day: int, interval_range: tuple):
        """设置投递限制"""
        self.max_applications_per_day = max_per_day
        self.application_interval = interval_range
        logger.info(f"设置投递限制: 每日{max_per_day}个，间隔{interval_range}秒")
