"""
AI智能匹配和个性化打招呼语服务
参考get_jobs项目实现
"""
import logging
import os
import json
import random
from typing import Dict, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class AIJobMatchingService:
    """AI智能匹配服务"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY环境变量未设置")
    
    def generate_personalized_greeting(self, job_info: Dict, user_profile: Dict) -> str:
        """生成个性化打招呼语"""
        try:
            if not self.api_key:
                return self._get_default_greeting()
            
            # 构建提示词
            prompt = self._build_greeting_prompt(job_info, user_profile)
            
            # 调用AI API
            greeting = self._call_ai_api(prompt)
            
            if greeting and len(greeting.strip()) > 0:
                return greeting.strip()
            else:
                return self._get_default_greeting()
                
        except Exception as e:
            logger.error(f"生成个性化打招呼语失败: {str(e)}")
            return self._get_default_greeting()
    
    def _build_greeting_prompt(self, job_info: Dict, user_profile: Dict) -> str:
        """构建打招呼语提示词"""
        job_title = job_info.get('title', '')
        company_name = job_info.get('company', '')
        job_requirements = job_info.get('requirements', '')
        job_description = job_info.get('description', '')
        
        user_skills = user_profile.get('skills', [])
        user_experience = user_profile.get('experience', '')
        user_education = user_profile.get('education', '')
        
        prompt = f"""
请为以下职位生成一个专业、个性化的打招呼语：

职位信息：
- 职位：{job_title}
- 公司：{company_name}
- 要求：{job_requirements}
- 描述：{job_description}

求职者信息：
- 技能：{', '.join(user_skills) if user_skills else '未提供'}
- 经验：{user_experience}
- 教育：{user_education}

要求：
1. 长度控制在50-100字
2. 体现对职位的了解和兴趣
3. 突出个人优势
4. 语言专业但不过于正式
5. 避免使用"您好"等常见开头

请直接输出打招呼语，不要包含其他内容：
"""
        return prompt
    
    def _call_ai_api(self, prompt: str) -> str:
        """调用AI API"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"AI API调用失败: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"调用AI API失败: {str(e)}")
            return ""
    
    def _get_default_greeting(self) -> str:
        """获取默认打招呼语"""
        greetings = [
            "您好，我对这个职位很感兴趣，希望能有机会与您进一步沟通。",
            "您好，我的技能和经验与这个职位要求很匹配，期待您的回复。",
            "您好，我对贵公司的发展前景很看好，希望能加入团队。",
            "您好，我有相关工作经验，相信能为团队带来价值。",
            "您好，我对这个职位非常感兴趣，希望能有机会面试。"
        ]
        return random.choice(greetings)
    
    def analyze_job_match(self, job_info: Dict, user_profile: Dict) -> Dict:
        """分析职位匹配度"""
        try:
            match_score = 0
            match_reasons = []
            
            # 技能匹配
            job_skills = self._extract_skills_from_job(job_info)
            user_skills = user_profile.get('skills', [])
            
            skill_matches = set(job_skills) & set(user_skills)
            if skill_matches:
                skill_score = len(skill_matches) / len(job_skills) * 40
                match_score += skill_score
                match_reasons.append(f"技能匹配：{', '.join(skill_matches)}")
            
            # 经验匹配
            job_experience = self._extract_experience_from_job(job_info)
            user_experience = user_profile.get('experience_years', 0)
            
            if user_experience >= job_experience:
                exp_score = min(30, (user_experience - job_experience + 1) * 10)
                match_score += exp_score
                match_reasons.append(f"经验充足：{user_experience}年")
            
            # 教育背景匹配
            job_education = job_info.get('education', '')
            user_education = user_profile.get('education', '')
            
            if job_education.lower() in user_education.lower():
                match_score += 20
                match_reasons.append("教育背景匹配")
            
            # 薪资匹配
            job_salary = self._extract_salary_from_job(job_info)
            user_expected_salary = user_profile.get('expected_salary', 0)
            
            if user_expected_salary <= job_salary:
                match_score += 10
                match_reasons.append("薪资期望合理")
            
            return {
                "match_score": min(100, match_score),
                "match_reasons": match_reasons,
                "is_good_match": match_score >= 60
            }
            
        except Exception as e:
            logger.error(f"分析职位匹配度失败: {str(e)}")
            return {
                "match_score": 50,
                "match_reasons": ["分析失败"],
                "is_good_match": False
            }
    
    def _extract_skills_from_job(self, job_info: Dict) -> List[str]:
        """从职位信息中提取技能要求"""
        skills = []
        
        # 从职位描述和要求中提取技能关键词
        text = f"{job_info.get('title', '')} {job_info.get('requirements', '')} {job_info.get('description', '')}"
        
        # 常见技能关键词
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Angular',
            'Spring', 'Django', 'Flask', 'MySQL', 'PostgreSQL', 'Redis',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'Linux', 'Git',
            '机器学习', '深度学习', '数据分析', '算法', '数据结构',
            '前端', '后端', '全栈', '移动端', 'iOS', 'Android'
        ]
        
        for keyword in skill_keywords:
            if keyword.lower() in text.lower():
                skills.append(keyword)
        
        return skills
    
    def _extract_experience_from_job(self, job_info: Dict) -> int:
        """从职位信息中提取经验要求"""
        text = f"{job_info.get('requirements', '')} {job_info.get('description', '')}"
        
        # 提取经验年数
        import re
        patterns = [
            r'(\d+)[-~](\d+)年',
            r'(\d+)年以上',
            r'(\d+)年以下',
            r'(\d+)年'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if '-' in pattern or '~' in pattern:
                    return int(match.group(1))
                else:
                    return int(match.group(1))
        
        return 0
    
    def _extract_salary_from_job(self, job_info: Dict) -> int:
        """从职位信息中提取薪资"""
        salary_text = job_info.get('salary', '')
        
        if not salary_text:
            return 0
        
        # 提取薪资数字
        import re
        numbers = re.findall(r'\d+', salary_text)
        
        if numbers:
            # 取最高薪资
            return max([int(num) for num in numbers])
        
        return 0


class ImageResumeService:
    """图片简历服务"""
    
    def __init__(self):
        self.resume_images_dir = os.path.join(settings.MEDIA_ROOT, 'resume_images')
        os.makedirs(self.resume_images_dir, exist_ok=True)
    
    def get_resume_image_path(self, user_id: int) -> Optional[str]:
        """获取用户简历图片路径"""
        try:
            # 查找用户的简历图片
            possible_names = [
                f'resume_{user_id}.jpg',
                f'resume_{user_id}.png',
                f'resume_{user_id}.pdf',
                f'user_{user_id}_resume.jpg',
                f'user_{user_id}_resume.png',
                f'user_{user_id}_resume.pdf'
            ]
            
            for filename in possible_names:
                file_path = os.path.join(self.resume_images_dir, filename)
                if os.path.exists(file_path):
                    return file_path
            
            return None
            
        except Exception as e:
            logger.error(f"获取简历图片路径失败: {str(e)}")
            return None
    
    def upload_resume_image(self, user_id: int, file) -> bool:
        """上传简历图片"""
        try:
            # 生成文件名
            file_extension = os.path.splitext(file.name)[1]
            filename = f'resume_{user_id}{file_extension}'
            file_path = os.path.join(self.resume_images_dir, filename)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            
            logger.info(f"简历图片上传成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"上传简历图片失败: {str(e)}")
            return False
    
    def convert_pdf_to_image(self, pdf_path: str) -> Optional[str]:
        """将PDF简历转换为图片"""
        try:
            from pdf2image import convert_from_path
            
            # 转换PDF为图片
            images = convert_from_path(pdf_path, first_page=1, last_page=1)
            
            if images:
                # 保存第一页为图片
                image_path = pdf_path.replace('.pdf', '.jpg')
                images[0].save(image_path, 'JPEG')
                return image_path
            
            return None
            
        except Exception as e:
            logger.error(f"PDF转图片失败: {str(e)}")
            return None
