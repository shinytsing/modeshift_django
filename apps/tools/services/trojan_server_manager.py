"""
Trojan服务器管理模块
负责Trojan服务器的启动、停止、配置管理和监控
"""

import json
import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import ipaddress

import yaml
from django.conf import settings

from .trojan_protocol import TrojanServer, TrojanConfig

logger = logging.getLogger(__name__)


class TrojanServerManager:
    """Trojan服务器管理器"""
    
    def __init__(self):
        self.server_process = None
        self.server_config_path = None
        self.server_log_path = None
        self.is_running = False
        self.start_time = None
        self.clients_count = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        
        # 设置路径
        self.setup_paths()
        
        # 初始化配置
        self.init_config()
    
    def setup_paths(self):
        """设置Trojan相关路径"""
        # 创建Trojan配置目录
        self.trojan_dir = Path(settings.BASE_DIR) / "trojan_server"
        self.trojan_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.server_config_path = self.trojan_dir / "server.json"
        
        # 日志文件路径
        self.server_log_path = self.trojan_dir / "server.log"
        
        # SSL证书路径
        self.ssl_cert_path = self.trojan_dir / "server.crt"
        self.ssl_key_path = self.trojan_dir / "server.key"
        
        # Trojan可执行文件路径
        self.trojan_binary_path = self.find_trojan_binary()
    
    def find_trojan_binary(self) -> Optional[str]:
        """查找Trojan可执行文件"""
        possible_paths = [
            "/usr/local/bin/trojan",
            "/usr/bin/trojan",
            "/opt/homebrew/bin/trojan",
            str(self.trojan_dir / "trojan"),
            str(self.trojan_dir / "trojan.exe"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        return None
    
    def init_config(self):
        """初始化配置"""
        if not self.server_config_path.exists():
            self.create_default_config()
        else:
            logger.info(f"使用现有Trojan服务器配置: {self.server_config_path}")
    
    def create_default_config(self):
        """创建默认服务器配置"""
        # 生成默认密码
        import secrets
        default_password = secrets.token_urlsafe(32)
        
        # 生成SSL证书
        self.generate_ssl_certificate()
        
        # 创建服务器配置
        config = TrojanConfig.generate_server_config(
            host='0.0.0.0',
            port=443,
            ssl_cert=str(self.ssl_cert_path),
            ssl_key=str(self.ssl_key_path),
            password=default_password
        )
        
        # 保存配置
        with open(self.server_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"创建默认Trojan服务器配置: {self.server_config_path}")
        logger.info(f"默认密码: {default_password}")
    
    def generate_ssl_certificate(self):
        """生成SSL证书"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta
            
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # 生成证书
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Trojan Server"),
                x509.NameAttribute(NameOID.COMMON_NAME, "trojan-server"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # 保存证书
            with open(self.ssl_cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # 保存私钥
            with open(self.ssl_key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info(f"SSL证书已生成: {self.ssl_cert_path}")
            
        except Exception as e:
            logger.error(f"生成SSL证书失败: {e}")
            raise
    
    def start_server(self) -> Tuple[bool, str]:
        """启动Trojan服务器"""
        try:
            if self.is_running:
                return True, "服务器已在运行"
            
            # 检查Trojan二进制文件
            if not self.trojan_binary_path:
                return False, "未找到Trojan可执行文件，请先安装Trojan"
            
            # 检查配置文件
            if not self.server_config_path.exists():
                return False, "配置文件不存在"
            
            # 启动服务器进程
            cmd = [
                self.trojan_binary_path,
                "-c", str(self.server_config_path),
                "-l", str(self.server_log_path)
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务器启动
            time.sleep(2)
            
            if self.server_process.poll() is None:
                self.is_running = True
                self.start_time = time.time()
                logger.info("Trojan服务器启动成功")
                return True, "服务器启动成功"
            else:
                stdout, stderr = self.server_process.communicate()
                error_msg = f"服务器启动失败: {stderr}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"启动Trojan服务器时出错: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def stop_server(self) -> Tuple[bool, str]:
        """停止Trojan服务器"""
        try:
            if not self.is_running:
                return True, "服务器未运行"
            
            if self.server_process:
                self.server_process.terminate()
                
                # 等待进程结束
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()
                
                self.server_process = None
            
            self.is_running = False
            self.start_time = None
            logger.info("Trojan服务器已停止")
            return True, "服务器已停止"
            
        except Exception as e:
            error_msg = f"停止Trojan服务器时出错: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def restart_server(self) -> Tuple[bool, str]:
        """重启Trojan服务器"""
        success, msg = self.stop_server()
        if not success:
            return False, f"停止服务器失败: {msg}"
        
        time.sleep(1)
        return self.start_server()
    
    def get_server_status(self) -> Dict:
        """获取服务器状态"""
        status = {
            "is_running": self.is_running,
            "start_time": self.start_time,
            "uptime": time.time() - self.start_time if self.start_time else 0,
            "clients_count": self.clients_count,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "config_path": str(self.server_config_path),
            "log_path": str(self.server_log_path),
            "binary_path": self.trojan_binary_path,
        }
        
        # 如果服务器在运行，检查进程状态
        if self.is_running and self.server_process:
            if self.server_process.poll() is not None:
                # 进程已结束
                self.is_running = False
                status["is_running"] = False
                status["error"] = "服务器进程意外结束"
        
        return status
    
    def get_server_config(self) -> Dict:
        """获取服务器配置"""
        try:
            with open(self.server_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取服务器配置失败: {e}")
            return {}
    
    def update_server_config(self, config: Dict) -> Tuple[bool, str]:
        """更新服务器配置"""
        try:
            # 验证配置
            if not self.validate_config(config):
                return False, "配置验证失败"
            
            # 备份原配置
            backup_path = self.server_config_path.with_suffix('.json.backup')
            if self.server_config_path.exists():
                import shutil
                shutil.copy2(self.server_config_path, backup_path)
            
            # 保存新配置
            with open(self.server_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("服务器配置已更新")
            return True, "配置更新成功"
            
        except Exception as e:
            error_msg = f"更新服务器配置失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def validate_config(self, config: Dict) -> bool:
        """验证配置"""
        required_fields = ["run_type", "local_addr", "local_port", "remote_addr", "remote_port"]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"配置缺少必需字段: {field}")
                return False
        
        if config.get("run_type") != "server":
            logger.error("配置类型必须是server")
            return False
        
        return True
    
    def add_user_password(self, password: str) -> Tuple[bool, str]:
        """添加用户密码"""
        try:
            config = self.get_server_config()
            
            if "password" not in config:
                config["password"] = []
            
            if password not in config["password"]:
                config["password"].append(password)
                
                success, msg = self.update_server_config(config)
                if success:
                    logger.info(f"用户密码已添加: {password}")
                    return True, "密码添加成功"
                else:
                    return False, f"更新配置失败: {msg}"
            else:
                return False, "密码已存在"
                
        except Exception as e:
            error_msg = f"添加用户密码失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def remove_user_password(self, password: str) -> Tuple[bool, str]:
        """移除用户密码"""
        try:
            config = self.get_server_config()
            
            if "password" in config and password in config["password"]:
                config["password"].remove(password)
                
                success, msg = self.update_server_config(config)
                if success:
                    logger.info(f"用户密码已移除: {password}")
                    return True, "密码移除成功"
                else:
                    return False, f"更新配置失败: {msg}"
            else:
                return False, "密码不存在"
                
        except Exception as e:
            error_msg = f"移除用户密码失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_user_passwords(self) -> List[str]:
        """获取所有用户密码"""
        try:
            config = self.get_server_config()
            return config.get("password", [])
        except Exception as e:
            logger.error(f"获取用户密码失败: {e}")
            return []
    
    def get_server_logs(self, lines: int = 100) -> List[str]:
        """获取服务器日志"""
        try:
            if not self.server_log_path.exists():
                return []
            
            with open(self.server_log_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
                
        except Exception as e:
            logger.error(f"读取服务器日志失败: {e}")
            return []
    
    def clear_logs(self) -> Tuple[bool, str]:
        """清除日志"""
        try:
            if self.server_log_path.exists():
                self.server_log_path.unlink()
            return True, "日志已清除"
        except Exception as e:
            error_msg = f"清除日志失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def install_trojan(self) -> Tuple[bool, str]:
        """安装Trojan（如果未安装）"""
        try:
            # 检查是否已安装
            if self.trojan_binary_path:
                return True, "Trojan已安装"
            
            # 尝试下载Trojan二进制文件
            import platform
            import urllib.request
            
            system = platform.system().lower()
            arch = platform.machine().lower()
            
            # 构建下载URL（这里需要根据实际情况调整）
            if system == "linux":
                if arch in ["x86_64", "amd64"]:
                    url = "https://github.com/trojan-gfw/trojan/releases/latest/download/trojan-linux-amd64"
                else:
                    return False, f"不支持的架构: {arch}"
            elif system == "darwin":
                if arch in ["x86_64", "amd64"]:
                    url = "https://github.com/trojan-gfw/trojan/releases/latest/download/trojan-macos-amd64"
                else:
                    return False, f"不支持的架构: {arch}"
            else:
                return False, f"不支持的操作系统: {system}"
            
            # 下载文件
            trojan_binary = self.trojan_dir / "trojan"
            urllib.request.urlretrieve(url, trojan_binary)
            
            # 设置执行权限
            os.chmod(trojan_binary, 0o755)
            
            # 更新二进制路径
            self.trojan_binary_path = str(trojan_binary)
            
            logger.info("Trojan安装成功")
            return True, "Trojan安装成功"
            
        except Exception as e:
            error_msg = f"安装Trojan失败: {e}"
            logger.error(error_msg)
            return False, error_msg

