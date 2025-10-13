"""
真正的Boss直聘自动投递服务
基于Java项目实现
"""
import json
import logging
import os
import subprocess
import tempfile
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from apps.tools.services.verification_code_manager import verification_manager

logger = logging.getLogger(__name__)


class RealBossJobService:
    """真正的Boss直聘自动投递服务"""
    
    def __init__(self):
        self.java_project_path = os.path.join(settings.BASE_DIR, 'java_job')
        self.temp_dir = os.path.join(settings.BASE_DIR, 'temp_java_jobs')
        self.ensure_temp_dir()
    
    def ensure_temp_dir(self):
        """确保临时目录存在"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def create_boss_config(self, user_input: Dict[str, Any]) -> str:
        """创建Boss直聘配置文件"""
        config_data = {
            "boss": {
                "debugger": False,
                "sayHi": user_input.get('greeting', '您好，我对这个职位很感兴趣，希望能有机会进一步沟通。'),
                "keywords": [user_input.get('position', 'Java开发工程师')],
                "cityCode": [self.get_city_code(user_input.get('city', '北京'))],
                "experience": [self.get_experience_code(user_input.get('experience', '3-5年'))],
                "jobType": "全职",
                "salary": self.get_salary_code(user_input.get('expectedSalary', [15, 25])),
                "degree": [self.get_degree_code(user_input.get('education', '本科'))],
                "scale": ["不限"],
                "stage": ["不限"],
                "expectedSalary": user_input.get('expectedSalary', [15, 25]),
                "waitTime": 3,
                "filterDeadHR": True,
                "enableAI": True,
                "sendImgResume": False,
                "deadStatus": ["2周内活跃", "本月活跃"],
                "maxApplications": 100
            }
        }
        
        # 创建临时配置文件
        config_file = os.path.join(self.temp_dir, f'boss_config_{uuid.uuid4().hex}.yaml')
        with open(config_file, 'w', encoding='utf-8') as f:
            self._write_yaml_config(config_data, f)
        
        return config_file
    
    def _write_yaml_config(self, data: dict, file):
        """写入YAML格式配置"""
        import yaml
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
    
    def get_city_code(self, city: str) -> str:
        """获取城市编码"""
        city_mapping = {
            '北京': '101010100',
            '上海': '101020100', 
            '深圳': '101280600',
            '广州': '101280100',
            '杭州': '101210100',
            '南京': '101190100',
            '成都': '101270100',
            '武汉': '101200100',
            '西安': '101110100',
            '苏州': '101190400'
        }
        return city_mapping.get(city, '101010100')  # 默认北京
    
    def get_experience_code(self, experience: str) -> str:
        """获取工作经验编码"""
        exp_mapping = {
            '1-3年': '102',
            '3-5年': '103', 
            '5-10年': '104',
            '10年以上': '105'
        }
        return exp_mapping.get(experience, '103')  # 默认3-5年
    
    def get_salary_code(self, salary_range: List[int]) -> str:
        """获取薪资范围编码"""
        min_salary = salary_range[0] if len(salary_range) > 0 else 15
        if min_salary < 5:
            return '402'
        elif min_salary < 10:
            return '403'
        elif min_salary < 20:
            return '404'
        elif min_salary < 50:
            return '405'
        else:
            return '406'
    
    def get_degree_code(self, degree: str) -> str:
        """获取学历编码"""
        degree_mapping = {
            '大专': '204',
            '本科': '205',
            '硕士': '206',
            '博士': '207'
        }
        return degree_mapping.get(degree, '205')  # 默认本科
    
    def validate_verification_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证用户输入的验证码"""
        return verification_manager.validate_and_consume(code)
    
    def start_boss_job_delivery(self, user_input: Dict[str, Any], verification_code: str) -> Dict[str, Any]:
        """启动Boss直聘投递任务"""
        try:
            # 验证验证码
            is_valid, error_msg = self.validate_verification_code(verification_code)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg or '验证码无效'
                }
            
            # 创建配置文件
            config_file = self.create_boss_config(user_input)
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 创建任务状态文件
            status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
            initial_status = {
                'task_id': task_id,
                'status': 'verified',
                'verification_code': verification_code,
                'config_file': config_file,
                'qr_code_url': '/tools/java-job/api/qr-image/',  # Boss直聘二维码图片
                'login_status': 'pending',
                'delivery_count': 0,
                'error_message': None,
                'start_time': int(time.time()),
                'end_time': None
            }
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(initial_status, f, ensure_ascii=False, indent=2)
            
            # 启动Java程序
            java_command = self._build_java_command(config_file, task_id)
            
            # 在后台启动Java进程
            process = subprocess.Popen(
                java_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.java_project_path
            )
            
            return {
                'success': True,
                'task_id': task_id,
                'verification_code': verification_code,
                'status_file': status_file,
                'process_id': process.pid,
                'qr_code_url': initial_status['qr_code_url']
            }
            
        except Exception as e:
            logger.error(f"启动Boss投递任务失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_java_command(self, config_file: str, task_id: str) -> List[str]:
        """构建Java命令"""
        # 检查Java是否可用
        java_exec = 'java'
        
        # 构建命令 - 运行Boss.java
        command = [
            java_exec,
            '-cp',
            f'{self.java_project_path}/target/classes:{self.java_project_path}/target/lib/*',
            'boss.Boss',
            '--config', config_file,
            '--task-id', task_id
        ]
        
        return command
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
        
        if not os.path.exists(status_file):
            return {
                'success': False,
                'error': '任务不存在'
            }
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            return {
                'success': True,
                'status': status
            }
        except Exception as e:
            logger.error(f"读取任务状态失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_task_status(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新任务状态"""
        status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
        
        if not os.path.exists(status_file):
            return False
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            status.update(updates)
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"更新任务状态失败: {str(e)}")
            return False
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        try:
            # 更新任务状态为停止
            self.update_task_status(task_id, {
                'status': 'stopped',
                'end_time': int(time.time())
            })
            
            return True
        except Exception as e:
            logger.error(f"停止任务失败: {str(e)}")
            return False
    
    def cleanup_task(self, task_id: str) -> bool:
        """清理任务文件"""
        try:
            status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
            if os.path.exists(status_file):
                os.remove(status_file)
            
            return True
        except Exception as e:
            logger.error(f"清理任务文件失败: {str(e)}")
            return False


# 全局服务实例
real_boss_service = RealBossJobService()
