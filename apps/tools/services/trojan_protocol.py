"""
Trojan协议核心实现模块
实现Trojan协议的加密、解密和连接管理
"""

import hashlib
import hmac
import logging
import os
import random
import socket
import ssl
import struct
import time
import ipaddress
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class TrojanCrypto:
    """Trojan加密解密类"""
    
    def __init__(self, password: str):
        self.password = password.encode('utf-8')
        self.key = self._derive_key()
        
    def _derive_key(self) -> bytes:
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'trojan-salt',
            iterations=100000,
        )
        return kdf.derive(self.password)
    
    def encrypt(self, data: bytes) -> bytes:
        """加密数据"""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # PKCS7 padding
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """解密数据"""
        if len(encrypted_data) < 16:
            raise ValueError("加密数据太短")
            
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 移除PKCS7 padding
        padding_length = padded_data[-1]
        if padding_length > 16 or padding_length == 0:
            raise ValueError("无效的填充")
            
        return padded_data[:-padding_length]


class TrojanRequest:
    """Trojan请求解析类"""
    
    def __init__(self, data: bytes):
        self.data = data
        self.command = None
        self.address = None
        self.port = None
        self.payload = None
        self._parse()
    
    def _parse(self):
        """解析Trojan请求"""
        if len(self.data) < 4:
            raise ValueError("请求数据太短")
            
        # Trojan协议格式: [CRLF][CRLF][Command][Address][Port][Payload]
        crlf_pos = self.data.find(b'\r\n\r\n')
        if crlf_pos == -1:
            raise ValueError("无效的Trojan请求格式")
            
        header = self.data[:crlf_pos]
        self.payload = self.data[crlf_pos + 4:]
        
        # 解析命令和地址
        if len(header) < 3:
            raise ValueError("请求头太短")
            
        self.command = header[0]
        
        if self.command == 1:  # CONNECT
            if len(header) < 7:
                raise ValueError("CONNECT请求格式错误")
                
            addr_type = header[1]
            if addr_type == 1:  # IPv4
                self.address = socket.inet_ntoa(header[2:6])
                self.port = struct.unpack('>H', header[6:8])[0]
            elif addr_type == 3:  # Domain
                addr_len = header[2]
                if len(header) < 3 + addr_len + 2:
                    raise ValueError("域名地址格式错误")
                self.address = header[3:3+addr_len].decode('utf-8')
                self.port = struct.unpack('>H', header[3+addr_len:3+addr_len+2])[0]
            else:
                raise ValueError(f"不支持的地址类型: {addr_type}")
        else:
            raise ValueError(f"不支持的命令: {self.command}")


class TrojanServer:
    """Trojan服务器实现"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 443, 
                 ssl_cert: str = None, ssl_key: str = None,
                 password: str = None):
        self.host = host
        self.port = port
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.password = password
        self.crypto = TrojanCrypto(password) if password else None
        self.clients = {}
        self.is_running = False
        
    def start(self):
        """启动Trojan服务器"""
        try:
            # 创建SSL上下文
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            if self.ssl_cert and self.ssl_key:
                context.load_cert_chain(self.ssl_cert, self.ssl_key)
            else:
                # 生成自签名证书
                context = self._generate_self_signed_cert(context)
            
            # 创建服务器socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(100)
            
            logger.info(f"Trojan服务器启动在 {self.host}:{self.port}")
            self.is_running = True
            
            while self.is_running:
                try:
                    client_socket, addr = server_socket.accept()
                    logger.info(f"新连接来自 {addr}")
                    
                    # 为每个客户端创建处理线程
                    import threading
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except Exception as e:
                    if self.is_running:
                        logger.error(f"接受连接时出错: {e}")
                        
        except Exception as e:
            logger.error(f"启动Trojan服务器失败: {e}")
            raise
    
    def _generate_self_signed_cert(self, context):
        """生成自签名SSL证书"""
        try:
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # 生成证书
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from datetime import datetime, timedelta
            
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Trojan Server"),
                x509.NameAttribute(NameOID.COMMON_NAME, self.host),
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
                    x509.DNSName(self.host),
                    x509.IPAddress(ipaddress.IPv4Address(self.host)),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # 保存证书和私钥到临时文件
            import tempfile
            cert_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.crt')
            key_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.key')
            
            cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
            key_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
            cert_file.close()
            key_file.close()
            
            # 加载证书
            context.load_cert_chain(cert_file.name, key_file.name)
            
            return context
            
        except Exception as e:
            logger.error(f"生成自签名证书失败: {e}")
            return context
    
    def _handle_client(self, client_socket, addr):
        """处理客户端连接"""
        try:
            # 创建SSL连接
            ssl_socket = ssl.wrap_socket(
                client_socket,
                server_side=True,
                certfile=self.ssl_cert,
                keyfile=self.ssl_key
            )
            
            # 读取Trojan请求
            request_data = ssl_socket.recv(4096)
            if not request_data:
                return
                
            # 解密请求
            if self.crypto:
                try:
                    decrypted_data = self.crypto.decrypt(request_data)
                except Exception as e:
                    logger.error(f"解密请求失败: {e}")
                    return
            else:
                decrypted_data = request_data
            
            # 解析请求
            try:
                request = TrojanRequest(decrypted_data)
            except Exception as e:
                logger.error(f"解析请求失败: {e}")
                return
            
            # 处理CONNECT命令
            if request.command == 1:  # CONNECT
                self._handle_connect(ssl_socket, request)
            else:
                logger.warning(f"不支持的命令: {request.command}")
                
        except Exception as e:
            logger.error(f"处理客户端连接失败: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _handle_connect(self, ssl_socket, request):
        """处理CONNECT请求"""
        try:
            # 连接到目标服务器
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((request.address, request.port))
            
            # 发送连接成功响应
            response = b'\x00\x00\x00\x00'  # Trojan成功响应
            if self.crypto:
                encrypted_response = self.crypto.encrypt(response)
            else:
                encrypted_response = response
            ssl_socket.send(encrypted_response)
            
            # 开始数据转发
            self._relay_data(ssl_socket, target_socket)
            
        except Exception as e:
            logger.error(f"处理CONNECT请求失败: {e}")
            # 发送错误响应
            error_response = b'\x01\x00\x00\x00'  # Trojan错误响应
            if self.crypto:
                encrypted_error = self.crypto.encrypt(error_response)
            else:
                encrypted_error = error_response
            try:
                ssl_socket.send(encrypted_error)
            except:
                pass
    
    def _relay_data(self, client_socket, target_socket):
        """数据转发"""
        import select
        import threading
        
        def forward_data(source, destination, crypto=None):
            try:
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    
                    if crypto:
                        try:
                            decrypted = crypto.decrypt(data)
                            destination.send(decrypted)
                        except:
                            # 如果解密失败，直接转发（可能是非加密数据）
                            destination.send(data)
                    else:
                        destination.send(data)
            except:
                pass
        
        # 创建两个转发线程
        client_to_target = threading.Thread(
            target=forward_data,
            args=(client_socket, target_socket, self.crypto)
        )
        target_to_client = threading.Thread(
            target=forward_data,
            args=(target_socket, client_socket, None)
        )
        
        client_to_target.daemon = True
        target_to_client.daemon = True
        
        client_to_target.start()
        target_to_client.start()
        
        # 等待任一线程结束
        client_to_target.join()
        target_to_client.join()
        
        # 关闭连接
        try:
            client_socket.close()
            target_socket.close()
        except:
            pass
    
    def stop(self):
        """停止服务器"""
        self.is_running = False
        logger.info("Trojan服务器已停止")


class TrojanClient:
    """Trojan客户端实现"""
    
    def __init__(self, server_host: str, server_port: int, 
                 password: str, ssl_verify: bool = False):
        self.server_host = server_host
        self.server_port = server_port
        self.password = password
        self.ssl_verify = ssl_verify
        self.crypto = TrojanCrypto(password)
        
    def connect_to_target(self, target_host: str, target_port: int) -> socket.socket:
        """通过Trojan服务器连接到目标"""
        try:
            # 连接到Trojan服务器
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((self.server_host, self.server_port))
            
            # 创建SSL连接
            context = ssl.create_default_context()
            if not self.ssl_verify:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            ssl_socket = context.wrap_socket(server_socket, server_hostname=self.server_host)
            
            # 构造Trojan请求
            request = self._build_connect_request(target_host, target_port)
            encrypted_request = self.crypto.encrypt(request)
            
            # 发送请求
            ssl_socket.send(encrypted_request)
            
            # 接收响应
            response = ssl_socket.recv(1024)
            decrypted_response = self.crypto.decrypt(response)
            
            if decrypted_response[0] != 0:
                raise Exception("Trojan服务器拒绝连接")
            
            return ssl_socket
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            raise
    
    def _build_connect_request(self, target_host: str, target_port: int) -> bytes:
        """构造CONNECT请求"""
        # Trojan协议格式: [CRLF][CRLF][Command][Address][Port][Payload]
        request = b'\r\n\r\n'  # Trojan标识
        
        # CONNECT命令
        request += b'\x01'
        
        # 地址类型和地址
        try:
            # 尝试解析为IP地址
            socket.inet_aton(target_host)
            request += b'\x01'  # IPv4
            request += socket.inet_aton(target_host)
        except:
            # 域名
            request += b'\x03'  # Domain
            request += bytes([len(target_host)])
            request += target_host.encode('utf-8')
        
        # 端口
        request += struct.pack('>H', target_port)
        
        return request


class TrojanConfig:
    """Trojan配置管理类"""
    
    @staticmethod
    def generate_client_config(server_host: str, server_port: int, 
                              password: str, ssl_verify: bool = False) -> Dict:
        """生成客户端配置"""
        return {
            "run_type": "client",
            "local_addr": "127.0.0.1",
            "local_port": 1080,
            "remote_addr": server_host,
            "remote_port": server_port,
            "password": [password],
            "ssl": {
                "verify": ssl_verify,
                "verify_hostname": ssl_verify,
                "cert": "",
                "cipher": "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384",
                "cipher_tls13": "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384",
                "sni": server_host,
                "alpn": ["h2", "http/1.1"],
                "reuse_session": True,
                "session_ticket": False,
                "curves": "",
                "dhparam": ""
            },
            "tcp": {
                "no_delay": True,
                "keep_alive": True,
                "reuse_port": False,
                "fast_open": False,
                "fast_open_qlen": 20
            }
        }
    
    @staticmethod
    def generate_server_config(host: str = '0.0.0.0', port: int = 443,
                              ssl_cert: str = None, ssl_key: str = None,
                              password: str = None) -> Dict:
        """生成服务器配置"""
        return {
            "run_type": "server",
            "local_addr": host,
            "local_port": port,
            "remote_addr": "127.0.0.1",
            "remote_port": 80,
            "password": [password] if password else [],
            "ssl": {
                "cert": ssl_cert,
                "key": ssl_key,
                "cipher": "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384",
                "cipher_tls13": "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384",
                "alpn": ["h2", "http/1.1"],
                "reuse_session": True,
                "session_ticket": False,
                "curves": "",
                "dhparam": ""
            },
            "tcp": {
                "no_delay": True,
                "keep_alive": True,
                "reuse_port": False,
                "fast_open": False,
                "fast_open_qlen": 20
            },
            "router": {
                "enabled": True,
                "rules": [
                    {
                        "domain": ["geosite:cn"],
                        "geoip": ["cn"],
                        "outbound": "direct"
                    }
                ]
            }
        }

