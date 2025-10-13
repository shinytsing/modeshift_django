"""
IP-Token绑定管理服务
确保一个token只绑定一个IP地址，防止跨IP使用
"""
import json
import logging
import os
import time
from typing import Dict, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class IPTokenBindingService:
    """IP-Token绑定管理服务"""
    
    def __init__(self):
        self.binding_file = os.path.join(settings.BASE_DIR, 'temp_java_jobs', 'ip_token_bindings.json')
        self.ensure_binding_file()
    
    def ensure_binding_file(self):
        """确保绑定文件存在"""
        binding_dir = os.path.dirname(self.binding_file)
        if not os.path.exists(binding_dir):
            os.makedirs(binding_dir)
        
        if not os.path.exists(self.binding_file):
            with open(self.binding_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _load_bindings(self) -> Dict[str, Any]:
        """加载IP-Token绑定数据"""
        try:
            with open(self.binding_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载IP-Token绑定失败: {str(e)}")
            return {}
    
    def _save_bindings(self, bindings: Dict[str, Any]):
        """保存IP-Token绑定数据"""
        try:
            with open(self.binding_file, 'w', encoding='utf-8') as f:
                json.dump(bindings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存IP-Token绑定失败: {str(e)}")
    
    def _cleanup_old_token(self, task_id: str, old_ip: str):
        """清理旧的token相关文件"""
        try:
            # 清理任务状态文件
            status_file = os.path.join(os.path.dirname(self.binding_file), f'status_{task_id}.json')
            if os.path.exists(status_file):
                os.remove(status_file)
                logger.info(f"已清理任务状态文件: {status_file}")
            
            # 清理二维码图片文件
            qr_image_file = os.path.join(os.path.dirname(self.binding_file), f'qr_code_{task_id}.png')
            if os.path.exists(qr_image_file):
                os.remove(qr_image_file)
                logger.info(f"已清理二维码图片文件: {qr_image_file}")
            
            # 清理登录状态文件
            login_status_file = os.path.join(os.path.dirname(self.binding_file), f'qr_code_{task_id}_login_status.json')
            if os.path.exists(login_status_file):
                os.remove(login_status_file)
                logger.info(f"已清理登录状态文件: {login_status_file}")
            
            # 停止相关的Java进程（如果还在运行）
            self._stop_java_process(task_id)
            
            logger.info(f"已清理任务 {task_id} 的所有相关文件和进程")
            
        except Exception as e:
            logger.error(f"清理旧token失败: {str(e)}")
    
    def _stop_java_process(self, task_id: str):
        """停止相关的Java进程"""
        try:
            import psutil
            
            # 查找包含task_id的Java进程
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'java' and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline'])
                        if task_id in cmdline:
                            proc.terminate()
                            logger.info(f"已停止Java进程 PID {proc.info['pid']} (任务 {task_id})")
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except ImportError:
            logger.warning("psutil未安装，无法自动停止Java进程")
        except Exception as e:
            logger.error(f"停止Java进程失败: {str(e)}")
    
    def create_binding(self, task_id: str, ip_address: str) -> bool:
        """创建IP-Token绑定"""
        try:
            bindings = self._load_bindings()
            
            # 检查是否已存在绑定
            if task_id in bindings:
                existing_ip = bindings[task_id].get('ip_address')
                if existing_ip != ip_address:
                    logger.warning(f"任务 {task_id} 已绑定到IP {existing_ip}，当前IP {ip_address} 不匹配，清理旧token")
                    # 清理旧的token绑定
                    self._cleanup_old_token(task_id, existing_ip)
            
            # 创建新绑定
            bindings[task_id] = {
                'ip_address': ip_address,
                'created_at': time.time(),
                'last_accessed': time.time(),
                'status': 'active'
            }
            
            self._save_bindings(bindings)
            logger.info(f"成功创建IP-Token绑定: 任务 {task_id} -> IP {ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"创建IP-Token绑定失败: {str(e)}")
            return False
    
    def validate_binding(self, task_id: str, ip_address: str) -> bool:
        """验证IP-Token绑定"""
        try:
            bindings = self._load_bindings()
            
            if task_id not in bindings:
                logger.warning(f"任务 {task_id} 未找到绑定记录")
                return False
            
            binding = bindings[task_id]
            stored_ip = binding.get('ip_address')
            
            if stored_ip != ip_address:
                logger.warning(f"IP地址不匹配: 存储IP {stored_ip} != 当前IP {ip_address}")
                return False
            
            # 更新最后访问时间
            binding['last_accessed'] = time.time()
            self._save_bindings(bindings)
            
            logger.info(f"IP-Token绑定验证成功: 任务 {task_id} -> IP {ip_address}")
            return True
            
        except Exception as e:
            logger.error(f"验证IP-Token绑定失败: {str(e)}")
            return False
    
    def remove_binding(self, task_id: str):
        """移除IP-Token绑定"""
        try:
            bindings = self._load_bindings()
            
            if task_id in bindings:
                del bindings[task_id]
                self._save_bindings(bindings)
                logger.info(f"成功移除IP-Token绑定: 任务 {task_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"移除IP-Token绑定失败: {str(e)}")
            return False
    
    def get_binding_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取绑定信息"""
        try:
            bindings = self._load_bindings()
            return bindings.get(task_id)
        except Exception as e:
            logger.error(f"获取绑定信息失败: {str(e)}")
            return None
    
    def cleanup_expired_bindings(self, max_age_hours: int = 24):
        """清理过期的绑定"""
        try:
            bindings = self._load_bindings()
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            expired_tasks = []
            for task_id, binding in bindings.items():
                created_at = binding.get('created_at', 0)
                if current_time - created_at > max_age_seconds:
                    expired_tasks.append(task_id)
            
            for task_id in expired_tasks:
                del bindings[task_id]
                logger.info(f"清理过期绑定: 任务 {task_id}")
            
            if expired_tasks:
                self._save_bindings(bindings)
            
            return len(expired_tasks)
            
        except Exception as e:
            logger.error(f"清理过期绑定失败: {str(e)}")
            return 0
    
    def force_cleanup_task(self, task_id: str):
        """强制清理任务的所有相关文件"""
        try:
            # 清理任务状态文件
            status_file = os.path.join(os.path.dirname(self.binding_file), f'status_{task_id}.json')
            if os.path.exists(status_file):
                os.remove(status_file)
                logger.info(f"已清理任务状态文件: {status_file}")
            
            # 清理二维码图片文件
            qr_image_file = os.path.join(os.path.dirname(self.binding_file), f'qr_code_{task_id}.png')
            if os.path.exists(qr_image_file):
                os.remove(qr_image_file)
                logger.info(f"已清理二维码图片文件: {qr_image_file}")
            
            # 清理登录状态文件
            login_status_file = os.path.join(os.path.dirname(self.binding_file), f'qr_code_{task_id}_login_status.json')
            if os.path.exists(login_status_file):
                os.remove(login_status_file)
                logger.info(f"已清理登录状态文件: {login_status_file}")
            
            # 停止相关的Java进程
            self._stop_java_process(task_id)
            
            # 移除绑定记录
            self.remove_binding(task_id)
            
            logger.info(f"已强制清理任务 {task_id} 的所有相关文件、进程和绑定记录")
            return True
            
        except Exception as e:
            logger.error(f"强制清理任务失败: {str(e)}")
            return False
    
    def get_all_bindings(self) -> Dict[str, Any]:
        """获取所有绑定信息"""
        return self._load_bindings()


# 创建全局实例
ip_token_binding_service = IPTokenBindingService()
