import socket
import ssl
import hashlib
import struct
import base64
import threading
import time
from urllib.parse import urlparse

class TrojanProtocolV2:
    """Trojan协议实现 V2 - 修复版本"""
    
    def __init__(self, server_host, server_port, password):
        self.server_host = server_host
        self.server_port = server_port
        self.password = password
        # Trojan使用SHA224哈希
        self.password_hash = hashlib.sha224(password.encode()).hexdigest()
    
    def create_handshake(self, target_host, target_port):
        """创建Trojan握手数据 - 修复版本"""
        # Trojan协议格式：
        # 密码哈希(56字节) + CRLF + 命令(1字节) + 地址类型(1字节) + 地址 + 端口(2字节) + CRLF
        
        # 密码哈希
        password_hash = self.password_hash.encode()
        
        # 命令：1 = CONNECT
        command = b'\x01'
        
        # 地址类型：3 = 域名
        address_type = b'\x03'
        
        # 地址长度 + 地址
        target_host_bytes = target_host.encode()
        address_length = struct.pack('B', len(target_host_bytes))
        address = address_length + target_host_bytes
        
        # 端口
        port = struct.pack('>H', target_port)
        
        # 组装Trojan请求头
        trojan_header = password_hash + b'\r\n' + command + address_type + address + port + b'\r\n'
        
        return trojan_header
    
    def connect_to_target(self, target_host, target_port):
        """通过Trojan代理连接到目标服务器 - 修复版本"""
        try:
            # 创建到Trojan服务器的连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            
            # 连接到Trojan服务器
            print(f"连接到Trojan服务器: {self.server_host}:{self.server_port}")
            sock.connect((self.server_host, self.server_port))
            
            # 创建Trojan握手数据
            handshake = self.create_handshake(target_host, target_port)
            print(f"发送Trojan握手数据: {len(handshake)} 字节")
            
            # 发送握手数据
            sock.send(handshake)
            
            # 等待响应（Trojan服务器应该返回200 OK或直接开始数据传输）
            response = sock.recv(1024)
            print(f"收到Trojan响应: {response}")
            
            if b'200' in response or len(response) > 0:
                print(f"Trojan握手成功: {target_host}:{target_port}")
                return sock
            else:
                print(f"Trojan握手失败: {response}")
                sock.close()
                return None
                
        except Exception as e:
            print(f"Trojan连接错误: {e}")
            return None
    
    def make_https_request(self, url, method='GET', headers=None, data=None):
        """通过Trojan代理发送HTTPS请求 - 修复版本"""
        try:
            # 解析URL
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 443
            path = parsed.path or '/'
            if parsed.query:
                path += '?' + parsed.query
            
            print(f"通过Trojan访问: {host}:{port}{path}")
            
            # 通过Trojan连接到目标服务器
            sock = self.connect_to_target(host, port)
            if not sock:
                return None
            
            # 创建SSL上下文
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # 包装socket为SSL
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            # 构建HTTP请求
            if headers is None:
                headers = {}
            
            # 默认请求头
            default_headers = {
                'Host': host,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Connection': 'close'
            }
            default_headers.update(headers)
            
            # 构建请求行
            request_line = f'{method} {path} HTTP/1.1\r\n'
            
            # 构建请求头
            header_lines = [f'{k}: {v}' for k, v in default_headers.items()]
            headers_str = '\r\n'.join(header_lines) + '\r\n\r\n'
            
            # 构建完整请求
            request = request_line + headers_str
            if data:
                request += data
            
            print(f"发送HTTP请求: {len(request)} 字节")
            
            # 发送请求
            ssl_sock.send(request.encode())
            
            # 接收响应
            response_data = b''
            while True:
                try:
                    chunk = ssl_sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    print(f"收到响应数据: {len(chunk)} 字节")
                except:
                    break
            
            # 关闭连接
            ssl_sock.close()
            
            # 解析响应
            response_str = response_data.decode('utf-8', errors='ignore')
            lines = response_str.split('\r\n')
            
            # 解析状态行
            status_line = lines[0]
            status_parts = status_line.split(' ', 2)
            status_code = int(status_parts[1]) if len(status_parts) > 1 else 0
            
            # 解析响应头
            headers = {}
            body_start = 0
            for i, line in enumerate(lines[1:], 1):
                if line == '':
                    body_start = i + 1
                    break
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
            
            # 获取响应体
            body = '\r\n'.join(lines[body_start:])
            
            return {
                'status_code': status_code,
                'headers': headers,
                'body': body,
                'raw_data': response_data
            }
            
        except Exception as e:
            print(f"HTTPS请求错误: {e}")
            return None

# 创建Trojan客户端实例
def create_trojan_client_v2(server_host, server_port, password):
    return TrojanProtocolV2(server_host, server_port, password)
