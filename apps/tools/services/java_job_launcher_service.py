"""
Java Job Launcher服务
集成Java Boss直聘自动投递项目
"""
import json
import logging
import os
import subprocess
import tempfile
import uuid
import time
import qrcode
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from apps.tools.services.verification_code_manager import verification_manager

logger = logging.getLogger(__name__)


class JavaJobLauncherService:
    """Java Job Launcher服务"""

    def __init__(self):
        self.java_project_path = os.path.join(settings.BASE_DIR, 'java_job')
        self.temp_dir = os.path.join(settings.BASE_DIR, 'temp_java_jobs')
        self.qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        self.ensure_directories()

    def ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.temp_dir, self.qr_codes_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

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
            '苏州': '101190400',
            '天津': '101030100',
            '全国': '101010100',  # 默认使用北京
            '不限': '101010100'   # 默认使用北京
        }
        return city_mapping.get(city, '101010100')  # 默认北京

    def get_experience_code(self, experience: str) -> str:
        """获取工作经验编码"""
        exp_mapping = {
            '在校生': '100',
            '应届毕业生': '101',
            '经验不限': '101',
            '1年以下': '101',
            '1-3年': '102',
            '3-5年': '103',
            '5-10年': '104',
            '10年以上': '105',
            '不限': '101'
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
            '博士': '207',
            '不限': '205'
        }
        return degree_mapping.get(degree, '205')  # 默认本科

    def validate_verification_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证用户输入的验证码"""
        return verification_manager.validate_and_consume(code)

    def generate_qr_code(self, task_id: str) -> str:
        """生成二维码图片（占位符，实际二维码由Java程序生成）"""
        # Java程序会生成实际的二维码，这里返回占位符URL
        return f"/tools/java-job/api/qr-image/?task_id={task_id}"

    def get_java_qr_code(self, task_id: str) -> Optional[str]:
        """获取Java程序生成的二维码"""
        try:
            # 首先检查是否有二维码URL文件
            qr_url_file = os.path.join(self.temp_jobs_dir, f"qr_url_{task_id}.txt")
            if os.path.exists(qr_url_file):
                with open(qr_url_file, 'r', encoding='utf-8') as f:
                    qr_url = f.read().strip()
                if qr_url:
                    # 如果是相对URL，转换为完整URL
                    if qr_url.startswith('/'):
                        qr_url = f"https://login.zhipin.com{qr_url}"
                    return qr_url

            # 备用：检查是否有二维码图片文件
            qr_file_path = os.path.join(self.temp_jobs_dir, f"qr_code_{task_id}.png")

            if os.path.exists(qr_file_path):
                # 将二维码文件复制到media目录
                qr_filename = f"qr_code_{task_id}.png"
                media_qr_path = os.path.join(self.qr_codes_dir, qr_filename)

                # 确保目录存在
                os.makedirs(self.qr_codes_dir, exist_ok=True)

                # 复制文件
                import shutil
                shutil.copy2(qr_file_path, media_qr_path)

                return f"/media/qr_codes/{qr_filename}"

            return None
        except Exception as e:
            logger.error(f"获取Java二维码失败: {str(e)}")
            return None

    def start_java_job_delivery(self, user_input: Dict[str, Any], verification_code: str) -> Dict[str, Any]:
        """启动Java投递任务"""
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

            # 生成二维码
            qr_code_url = self.generate_qr_code(task_id)

            # 创建配置文件
            config_file = self.create_boss_config(user_input)

            # 创建任务状态文件
            status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
            initial_status = {
                'task_id': task_id,
                'status': 'verified',
                'verification_code': verification_code,
                'config_file': config_file,
                'qr_code_url': qr_code_url,
                'login_status': 'pending',
                'delivery_count': 0,
                'error_message': None,
                'start_time': int(time.time()),
                'end_time': None,
                'user_input': user_input
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

            # 更新状态为已启动
            self.update_task_status(task_id, {
                'status': 'java_started',
                'java_process_id': process.pid,
                'qr_code_url': qr_code_url
            })

            return {
                'success': True,
                'task_id': task_id,
                'verification_code': verification_code,
                'status_file': status_file,
                'process_id': process.pid,
                'qr_code_url': qr_code_url
            }

        except Exception as e:
            logger.error(f"启动Java投递任务失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_java_command(self, config_file: str, task_id: str) -> List[str]:
        """构建Java命令"""
        # 检查Java是否可用
        java_exec = 'java'

        # 构建命令 - 运行BossQRCodeExtractorWithFile.java
        command = [
            java_exec,
            '-Dtask.id=' + task_id,
            '-Dclient.ip=127.0.0.1',
            '-cp',
            f'{self.java_project_path}/target/classes:{self.java_project_path}/target/dependency/*',
            'boss.BossQRCodeExtractorWithFile'
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

    def refresh_qr_code(self, task_id: str) -> Dict[str, Any]:
        """刷新二维码"""
        try:
            # 检查Java进程是否还在运行
            status_file = os.path.join(self.temp_dir, f'status_{task_id}.json')
            if not os.path.exists(status_file):
                return {
                    'success': False,
                    'error': '任务不存在'
                }

            # 读取当前状态
            with open(status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)

            java_process_id = status.get('java_process_id')
            if java_process_id:
                # 检查进程是否还在运行
                try:
                    import psutil
                    process = psutil.Process(java_process_id)
                    if not process.is_running():
                        return {
                            'success': False,
                            'error': 'Java进程已停止，请重新启动任务'
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return {
                        'success': False,
                        'error': 'Java进程已停止，请重新启动任务'
                    }

            # 尝试获取Java程序生成的新二维码
            qr_code_url = self.get_java_qr_code(task_id)

            if qr_code_url:
                # 更新任务状态
                self.update_task_status(task_id, {
                    'qr_code_url': qr_code_url,
                    'status': 'qr_generated',
                    'login_status': 'pending'
                })

                return {
                    'success': True,
                    'qr_code_url': qr_code_url
                }
            else:
                return {
                    'success': False,
                    'error': '二维码尚未生成，请稍后再试'
                }

        except Exception as e:
            logger.error(f"刷新二维码失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

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

            # 清理二维码文件
            qr_file = os.path.join(self.qr_codes_dir, f'qr_code_{task_id}.png')
            if os.path.exists(qr_file):
                os.remove(qr_file)

            return True
        except Exception as e:
            logger.error(f"清理任务文件失败: {str(e)}")
            return False


# 全局服务实例
java_job_launcher_service = JavaJobLauncherService()
