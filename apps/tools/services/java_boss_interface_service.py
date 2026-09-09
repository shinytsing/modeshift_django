"""
Java Boss直聘接口服务
直接调用Java程序进行Boss直聘自动投递
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
from apps.tools.services.ip_token_binding_service import ip_token_binding_service

logger = logging.getLogger(__name__)


class JavaBossInterfaceService:
    """Java Boss直聘接口服务"""

    def __init__(self):
        self.java_project_path = os.path.join(settings.BASE_DIR, 'java_job', 'java_job')
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
                "debugger": True,
                "sayHi": user_input.get('greeting', '您好，我对这个职位很感兴趣，希望能有机会进一步沟通。'),
                "keywords": [user_input.get('position', 'Java开发工程师')],
                "cityCode": [user_input.get('city', '北京')],  # 直接使用城市名称，让Java程序转换
                "experience": [user_input.get('experience', '3-5年')],  # 直接使用经验描述
                "jobType": "全职",
                "salary": self.get_salary_range(user_input.get('expectedSalary', [15, 25])[0], user_input.get('expectedSalary', [15, 25])[1]),
                "degree": [user_input.get('education', '本科')],  # 直接使用学历描述
                "scale": ["不限"],
                "stage": ["不限"],
                "industry": ["不限"],
                "expectedSalary": user_input.get('expectedSalary', [15, 25]),
                "waitTime": 3,
                "filterDeadHR": True,
                "enableAI": True,
                "sendImgResume": False,
                "deadStatus": ["2周内活跃", "本月活跃"],
                "maxApplications": 100
            }
        }

        # 写入Java项目的config.yaml文件到两个位置：
        # 1. src/main/resources/config.yaml (源码位置)
        # 2. target/classes/config.yaml (运行时classpath位置)
        src_config_file = os.path.join(self.java_project_path, 'src', 'main', 'resources', 'config.yaml')
        target_config_file = os.path.join(self.java_project_path, 'target', 'classes', 'config.yaml')

        # 确保target/classes目录存在
        os.makedirs(os.path.dirname(target_config_file), exist_ok=True)

        # 写入两个位置的配置文件
        with open(src_config_file, 'w', encoding='utf-8') as f:
            self._write_yaml_config(config_data, f)

        with open(target_config_file, 'w', encoding='utf-8') as f:
            self._write_yaml_config(config_data, f)

        return target_config_file

    def _write_yaml_config(self, data: dict, file):
        """写入YAML格式配置"""
        import yaml
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

    def get_salary_range(self, min_salary: int, max_salary: int) -> str:
        """获取薪资范围描述"""
        if min_salary < 5:
            return "5K以下"
        elif min_salary < 10:
            return "5-10K"
        elif min_salary < 20:
            return "10-20K"
        elif min_salary < 50:
            return "20-50K"
        else:
            return "50K以上"

    def validate_verification_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证用户输入的验证码"""
        return verification_manager.validate_and_consume(code)

    def start_boss_job_delivery(self, user_input: Dict[str, Any], verification_code: str, client_ip: str = None) -> Dict[str, Any]:
        """启动Boss直聘投递任务"""
        try:
            # 验证验证码
            is_valid, error_msg = self.validate_verification_code(verification_code)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg or '验证码无效'
                }

            # 生成任务ID
            task_id = str(uuid.uuid4())

            # 如果提供了IP地址，进行IP-Token绑定验证
            if client_ip:
                # 检查是否已存在绑定
                existing_binding = ip_token_binding_service.get_binding_info(task_id)
                if existing_binding:
                    # 验证IP是否匹配
                    if not ip_token_binding_service.validate_binding(task_id, client_ip):
                        logger.warning(f"IP地址不匹配，清理旧token并创建新绑定: 任务 {task_id}, 旧IP {existing_binding.get('ip_address')}, 新IP {client_ip}")
                        # 强制清理旧任务的所有相关文件
                        ip_token_binding_service.force_cleanup_task(task_id)
                        # 创建新绑定
                        if not ip_token_binding_service.create_binding(task_id, client_ip):
                            return {
                                'success': False,
                                'error': '创建新IP-Token绑定失败'
                            }
                else:
                    # 创建新的IP-Token绑定
                    if not ip_token_binding_service.create_binding(task_id, client_ip):
                        return {
                            'success': False,
                            'error': '创建IP-Token绑定失败'
                        }

            # 创建配置文件
            config_file = self.create_boss_config(user_input)

            # 创建任务状态文件
            status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
            initial_status = {
                'task_id': task_id,
                'status': 'verified',
                'verification_code': verification_code,
                'config_file': config_file,
                'client_ip': client_ip,
                'qr_code_url': '/tools/java-job/api/qr-image/',  # Boss直聘二维码图片
                'login_status': 'pending',
                'delivery_count': 0,
                'error_message': None,
                'start_time': int(time.time()),
                'end_time': None,
                'java_process_id': None
            }

            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(initial_status, f, ensure_ascii=False, indent=2)

            # 启动Java程序
            java_command = self._build_java_command(config_file, task_id, client_ip)

            # 在后台启动Java进程
            process = subprocess.Popen(
                java_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.java_project_path,
                env={**os.environ}  # 使用系统默认的Java环境
            )

            # 更新状态文件中的进程ID
            initial_status['java_process_id'] = process.pid
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(initial_status, f, ensure_ascii=False, indent=2)

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

    def _build_java_command(self, config_file: str, task_id: str, client_ip: str = None) -> List[str]:
        """构建Java命令"""
        # 构建命令 - 运行BossQRCodeExtractorWithFile.java
        # 添加系统属性来指定二维码保存路径
        qr_image_path = os.path.join(self.temp_dir, f'qr_code_{task_id}.png')

        command = [
            'java',  # 使用系统PATH中的java
            '-cp',
            f'{self.java_project_path}/target/classes:{self.java_project_path}/target/dependency/*',
            f'-Dqr.image.path={qr_image_path}',
            f'-Dtask.id={task_id}',
        ]

        # 如果提供了客户端IP，添加到系统属性中
        if client_ip:
            command.append(f'-Dclient.ip={client_ip}')

        command.append('boss.BossQRCodeExtractorWithFile')

        return command

    def _build_boss_delivery_command(self, config_file: str, task_id: str, client_ip: str = None) -> List[str]:
        """构建Boss投递命令"""
        command = [
            'java',  # 使用系统PATH中的java
            '-cp',
            f'{self.java_project_path}/target/classes:{self.java_project_path}/target/dependency/*',
            f'-Dtask.id={task_id}',
        ]

        # 如果提供了客户端IP，添加到系统属性中
        if client_ip:
            command.append(f'-Dclient.ip={client_ip}')

        command.append('boss.Boss')

        return command

    def start_delivery_task(self, task_id: str, client_ip: str = None) -> Dict[str, Any]:
        """启动投递任务（在登录成功后）"""
        try:
            # 检查登录状态
            login_status_file = os.path.join(self.temp_dir, f'login_status_{task_id}.json')
            if not os.path.exists(login_status_file):
                return {
                    'success': False,
                    'error': '用户尚未登录'
                }

            # 读取登录状态
            with open(login_status_file, 'r', encoding='utf-8') as f:
                login_status = json.load(f)

            if login_status.get('status') != 'success':
                return {
                    'success': False,
                    'error': '登录状态异常'
                }

            # 构建投递命令
            config_file = os.path.join(self.temp_dir, f'config_{task_id}.json')
            command = self._build_boss_delivery_command(config_file, task_id, client_ip)

            # 启动投递进程
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.java_project_path
            )

            # 更新任务状态
            status_data = {
                'status': 'delivery_started',
                'message': '投递任务已启动',
                'delivery_start_time': time.time(),
                'process_id': process.pid
            }

            status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)

            return {
                'success': True,
                'message': '投递任务已启动',
                'process_id': process.pid
            }

        except Exception as e:
            logger.error(f"启动投递任务失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

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
java_boss_service = JavaBossInterfaceService()
