"""
BOSS直聘API服务
实现真正的职位搜索和简历投递功能
"""

import requests
import time
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class BossZhipinAPI:
    """BOSS直聘API服务类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.zhipin.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(self.headers)
        self.is_logged_in = False
        self.cookies = {}
    
    def search_jobs(self, keyword: str, city: str, page: int = 1, salary: str = "", experience: str = "", scale: str = "") -> Dict:
        """
        搜索职位
        
        Args:
            keyword: 关键词，如"Python开发"
            city: 城市，如"北京"
            page: 页码
            salary: 薪资范围，如"406" (15-25K)
            experience: 经验要求，如"102" (1-3年)
            scale: 公司规模，如"303" (100-499人)
        
        Returns:
            搜索结果字典
        """
        try:
            # 构建搜索URL
            search_params = {
                'query': keyword,
                'city': self._get_city_code(city),
                'page': page
            }
            
            if salary:
                search_params['salary'] = salary
            if experience:
                search_params['experience'] = experience
            if scale:
                search_params['scale'] = scale
            
            search_url = f"{self.base_url}/web/geek/job?" + urlencode(search_params)
            
            # 发送搜索请求
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # 解析搜索结果
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs = self._parse_job_list(soup)
            
            return {
                'success': True,
                'jobs': jobs,
                'total': len(jobs),
                'page': page,
                'keyword': keyword,
                'city': city
            }
            
        except Exception as e:
            logger.error(f"搜索职位失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'jobs': [],
                'total': 0
            }
    
    def _parse_job_list(self, soup: BeautifulSoup) -> List[Dict]:
        """解析职位列表"""
        jobs = []
        
        # 查找职位列表容器
        job_items = soup.find_all('li', class_='job-card-wrapper')
        
        for item in job_items:
            try:
                job_info = self._extract_job_info(item)
                if job_info:
                    jobs.append(job_info)
            except Exception as e:
                logger.warning(f"解析职位信息失败: {str(e)}")
                continue
        
        return jobs
    
    def _extract_job_info(self, item) -> Optional[Dict]:
        """提取单个职位信息"""
        try:
            # 职位标题和链接
            title_elem = item.find('span', class_='job-name')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # 职位链接
            link_elem = item.find('a')
            job_link = ""
            job_id = ""
            if link_elem:
                job_link = self.base_url + link_elem.get('href', '')
                # 提取job_id
                href = link_elem.get('href', '')
                job_id_match = re.search(r'/job_detail/([^.]+)', href)
                if job_id_match:
                    job_id = job_id_match.group(1)
            
            # 薪资
            salary_elem = item.find('span', class_='salary')
            salary = salary_elem.get_text(strip=True) if salary_elem else ""
            
            # 公司名称
            company_elem = item.find('h3', class_='name')
            company = company_elem.get_text(strip=True) if company_elem else ""
            
            # 公司信息（规模、行业等）
            company_info = item.find('ul', class_='company-tag-list')
            company_tags = []
            if company_info:
                tags = company_info.find_all('li')
                company_tags = [tag.get_text(strip=True) for tag in tags]
            
            # 工作地点
            location_elem = item.find('span', class_='job-area')
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # 工作经验和学历要求
            info_elem = item.find('p', class_='job-limit')
            experience = ""
            education = ""
            if info_elem:
                info_text = info_elem.get_text(strip=True)
                parts = info_text.split('·')
                if len(parts) >= 2:
                    experience = parts[0].strip()
                    education = parts[1].strip()
            
            # HR信息
            hr_elem = item.find('div', class_='info-public')
            hr_name = ""
            hr_title = ""
            if hr_elem:
                hr_name_elem = hr_elem.find('h3')
                hr_title_elem = hr_elem.find('p')
                if hr_name_elem:
                    hr_name = hr_name_elem.get_text(strip=True)
                if hr_title_elem:
                    hr_title = hr_title_elem.get_text(strip=True)
            
            return {
                'id': job_id,
                'title': title,
                'salary': salary,
                'company': company,
                'company_tags': company_tags,
                'location': location,
                'experience': experience,
                'education': education,
                'hr_name': hr_name,
                'hr_title': hr_title,
                'link': job_link,
                'platform': 'boss'
            }
            
        except Exception as e:
            logger.error(f"提取职位信息失败: {str(e)}")
            return None
    
    def send_greeting(self, job_id: str, message: str = "") -> Dict:
        """
        发送招呼/投递简历
        
        Args:
            job_id: 职位ID
            message: 自定义招呼语
        
        Returns:
            投递结果
        """
        try:
            if not self.is_logged_in:
                return {
                    'success': False,
                    'error': '请先登录BOSS直聘'
                }
            
            # 默认招呼语
            if not message:
                message = "您好，我对这个职位很感兴趣，希望能有机会详细了解，期待您的回复。"
            
            # 构建投递请求
            greet_url = f"{self.base_url}/web/geek/chat"
            
            greet_data = {
                'jid': job_id,
                'content': message,
                'type': 1  # 打招呼类型
            }
            
            # 发送投递请求
            response = self.session.post(
                greet_url,
                data=greet_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f"{self.base_url}/web/geek/job"
                },
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                return {
                    'success': True,
                    'message': '投递成功',
                    'job_id': job_id
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', '投递失败'),
                    'job_id': job_id
                }
                
        except Exception as e:
            logger.error(f"发送招呼失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'job_id': job_id
            }
    
    def login_with_phone(self, phone: str, code: str) -> Dict:
        """
        手机验证码登录
        
        Args:
            phone: 手机号
            code: 验证码
        
        Returns:
            登录结果
        """
        try:
            # 发送登录请求
            login_url = f"{self.base_url}/web/user/login"
            
            login_data = {
                'phone': phone,
                'code': code,
                'remember': 1
            }
            
            response = self.session.post(login_url, data=login_data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') == 0:
                self.is_logged_in = True
                self.cookies = dict(response.cookies)
                return {
                    'success': True,
                    'message': '登录成功'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', '登录失败')
                }
                
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_sms_code(self, phone: str) -> Dict:
        """
        发送短信验证码
        使用真实的Boss直聘网站端点
        
        Args:
            phone: 手机号
        
        Returns:
            发送结果
        """
        try:
            # 使用真实的Boss直聘登录页面端点
            sms_url = f"{self.base_url}/web/user/sendSmsCode"
            
            # 构建请求头，模拟真实浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.zhipin.com',
                'Referer': 'https://www.zhipin.com/web/user/login',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
            sms_data = {
                'phone': phone,
                'type': 'login'
            }
            
            response = self.session.post(sms_url, data=sms_data, headers=headers, timeout=10)
            
            # 检查响应状态
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('code') == 0:
                        return {
                            'success': True,
                            'message': '验证码已发送'
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('message', '发送验证码失败')
                        }
                except json.JSONDecodeError:
                    # 如果不是JSON响应，可能是HTML页面
                    if '验证码' in response.text or '短信' in response.text:
                        return {
                            'success': True,
                            'message': '验证码已发送（请检查短信）'
                        }
                    else:
                        return {
                            'success': False,
                            'error': '发送验证码失败，请稍后重试'
                        }
            else:
                return {
                    'success': False,
                    'error': f'请求失败，状态码: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"发送验证码失败: {str(e)}")
            return {
                'success': False,
                'error': f'发送失败: {str(e)}'
            }
    
    def batch_apply_jobs(self, jobs: List[Dict], message: str = "") -> Dict:
        """
        批量投递职位
        
        Args:
            jobs: 职位列表
            message: 统一招呼语
        
        Returns:
            批量投递结果
        """
        results = {
            'success': 0,
            'failed': 0,
            'total': len(jobs),
            'details': []
        }
        
        for job in jobs:
            job_id = job.get('id')
            if not job_id:
                continue
            
            # 投递简历
            result = self.send_greeting(job_id, message)
            
            if result.get('success'):
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'job_id': job_id,
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'result': result
            })
            
            # 避免请求过于频繁
            time.sleep(2)
        
        return results
    
    def _get_city_code(self, city_name: str) -> str:
        """获取城市编码"""
        city_codes = {
            '北京': '101010100',
            '上海': '101020100',
            '广州': '101280100',
            '深圳': '101280600',
            '杭州': '101210100',
            '南京': '101190100',
            '苏州': '101190400',
            '成都': '101270100',
            '武汉': '101200100',
            '西安': '101110100',
            '重庆': '101040100',
            '天津': '101030100'
        }
        return city_codes.get(city_name, '101010100')  # 默认北京
    
    def get_job_detail(self, job_id: str) -> Dict:
        """
        获取职位详情
        
        Args:
            job_id: 职位ID
        
        Returns:
            职位详情
        """
        try:
            detail_url = f"{self.base_url}/job_detail/{job_id}.html"
            
            response = self.session.get(detail_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析职位详情
            detail = self._parse_job_detail(soup)
            
            return {
                'success': True,
                'detail': detail
            }
            
        except Exception as e:
            logger.error(f"获取职位详情失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_job_detail(self, soup: BeautifulSoup) -> Dict:
        """解析职位详情页面"""
        detail = {}
        
        try:
            # 职位描述
            desc_elem = soup.find('div', class_='job-sec-text')
            if desc_elem:
                detail['description'] = desc_elem.get_text(strip=True)
            
            # 职位要求
            req_elem = soup.find('div', class_='job-detail')
            if req_elem:
                detail['requirements'] = req_elem.get_text(strip=True)
            
            # 公司信息
            company_elem = soup.find('div', class_='company-info')
            if company_elem:
                detail['company_info'] = company_elem.get_text(strip=True)
            
        except Exception as e:
            logger.warning(f"解析职位详情部分失败: {str(e)}")
        
        return detail


# 全局实例
boss_api = BossZhipinAPI()