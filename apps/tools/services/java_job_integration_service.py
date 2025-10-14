"""
Java Job项目集成服务
用于调用Java版本的get_jobs项目
"""
import json
import logging
import os
import signal
import subprocess
import tempfile
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from apps.tools.services.verification_code_manager import verification_manager
from apps.tools.services.java_boss_interface_service import java_boss_service
from apps.tools.services.ip_token_binding_service import ip_token_binding_service

logger = logging.getLogger(__name__)


class JavaJobIntegrationService:
    """Java Job项目集成服务"""
    
    def __init__(self):
        self.java_project_path = os.path.join(settings.BASE_DIR, 'java_integration', 'java_job')
        self.temp_dir = os.path.join(settings.BASE_DIR, 'temp_java_jobs')
        self.ensure_temp_dir()
    
    def ensure_temp_dir(self):
        """确保临时目录存在"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def create_job_config(self, user_input: Dict[str, Any]) -> str:
        """创建Java项目的配置文件"""
        config_data = {
            "greeting": user_input.get('greeting', '您好，我对这个职位很感兴趣，希望能有机会进一步沟通。'),
            "city": user_input.get('city', '北京'),
            "position": user_input.get('position', 'Java开发工程师'),
            "experience": user_input.get('experience', '3-5年'),
            "expectedSalary": user_input.get('expectedSalary', [15, 25]),
            "education": user_input.get('education', '本科'),
            "platform": "boss",  # 默认使用Boss直聘
            "sendImgResume": False,  # 默认不发送图片简历
            "blackCompanies": [],
            "blackRecruiters": [],
            "blackJobs": []
        }
        
        # 创建临时配置文件
        config_file = os.path.join(self.temp_dir, f'config_{uuid.uuid4().hex}.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        return config_file
    
    def validate_verification_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证用户输入的验证码"""
        return verification_manager.validate_and_consume(code)
    
    def start_boss_job_delivery(self, user_input: Dict[str, Any], verification_code: str, client_ip: str = None) -> Dict[str, Any]:
        """启动Boss直聘投递任务"""
        # 使用Java Boss接口服务，传递IP地址
        return java_boss_service.start_boss_job_delivery(user_input, verification_code, client_ip)
    
    def _build_java_command(self, config_file: str, task_id: str) -> List[str]:
        """构建Java命令"""
        # 这里需要根据实际的Java项目结构调整
        # 假设Java项目有可执行的jar文件或main类
        java_home = os.environ.get('JAVA_HOME', '/usr/lib/jvm/default-java')
        java_exec = os.path.join(java_home, 'bin', 'java')
        
        # 检查Java是否可用
        if not os.path.exists(java_exec):
            java_exec = 'java'  # 使用系统PATH中的java
        
        # 构建命令
        command = [
            java_exec,
            '-jar',
            os.path.join(self.java_project_path, 'target', 'get_jobs.jar'),
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
        """停止任务并杀死进程"""
        try:
            status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
            
            if not os.path.exists(status_file):
                logger.warning(f"任务状态文件不存在: {status_file}")
                return False
            
            # 读取任务状态
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
            
            # 获取Java进程ID
            java_process_id = status.get('java_process_id')
            
            if java_process_id:
                try:
                    # 尝试终止进程
                    os.kill(java_process_id, signal.SIGTERM)
                    logger.info(f"已发送SIGTERM信号给进程 {java_process_id}")
                    
                    # 等待进程结束
                    time.sleep(2)
                    
                    # 检查进程是否还在运行
                    try:
                        os.kill(java_process_id, 0)  # 检查进程是否存在
                        # 如果进程还存在，强制杀死
                        os.kill(java_process_id, signal.SIGKILL)
                        logger.info(f"强制杀死进程 {java_process_id}")
                    except ProcessLookupError:
                        logger.info(f"进程 {java_process_id} 已正常终止")
                        
                except ProcessLookupError:
                    logger.warning(f"进程 {java_process_id} 不存在或已终止")
                except Exception as e:
                    logger.error(f"杀死进程 {java_process_id} 失败: {str(e)}")
            
            # 更新任务状态为停止
            self.update_task_status(task_id, {
                'status': 'stopped',
                'end_time': int(time.time()),
                'java_process_id': None
            })
            
            logger.info(f"任务 {task_id} 已停止")
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
java_job_service = JavaJobIntegrationService()
