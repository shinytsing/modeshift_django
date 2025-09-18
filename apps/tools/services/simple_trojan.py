import socket
import ssl
import hashlib
import struct
import time

class SimpleTrojan:
    """简化的Trojan实现"""
    
    def __init__(self, server_host, server_port, password):
        self.server_host = server_host
        self.server_port = server_port
        self.password = password
        self.password_hash = hashlib.sha224(password.encode()).hexdigest()
    
    def connect(self, target_host, target_port):
        """连接到目标服务器"""
        try:
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            
            # 连接到Trojan服务器
            sock.connect((self.server_host, self.server_port))
            
            # 创建Trojan请求
            # 格式：密码哈希 + CRLF + 命令 + 地址类型 + 地址 + 端口 + CRLF
            password_hash = self.password_hash.encode()
            command = b'\x01'  # CONNECT
            address_type = b'\x03'  # 域名
            target_host_bytes = target_host.encode()
            address_length = struct.pack('B', len(target_host_bytes))
            address = address_length + target_host_bytes
            port = struct.pack('>H', target_port)
            
            # 组装请求
            request = password_hash + b'\r\n' + command + address_type + address + port + b'\r\n'
            
            # 发送请求
            sock.send(request)
            
            # 等待响应
            time.sleep(1)
            response = sock.recv(1024)
            
            if response:
                print(f'Trojan响应: {response}')
                return sock
            else:
                print('Trojan无响应')
                sock.close()
                return None
                
        except Exception as e:
            print(f'Trojan连接错误: {e}')
            return None
    
    def make_request(self, url):
        """发送HTTP请求"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 443
            path = parsed.path or '/'
            
            # 连接到目标
            sock = self.connect(host, port)
            if not sock:
                return None
            
            # 创建SSL连接
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            # 发送HTTP请求
            request = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'
            ssl_sock.send(request.encode())
            
            # 接收响应
            response_data = b''
            while True:
                try:
                    chunk = ssl_sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                except:
                    break
            
            ssl_sock.close()
            
            # 解析响应
            response_str = response_data.decode('utf-8', errors='ignore')
            lines = response_str.split('\r\n')
            
            # 获取状态码
            status_line = lines[0]
            status_parts = status_line.split(' ', 2)
            status_code = int(status_parts[1]) if len(status_parts) > 1 else 0
            
            return {
                'status_code': status_code,
                'body': response_str,
                'raw_data': response_data
            }
            
        except Exception as e:
            print(f'请求错误: {e}')
            return None

# 测试函数
def test_trojan():
    trojan = SimpleTrojan('ty-1.rise-fuji.com', 443, 'GUGm7DHtpSx7SuPyUD')
    response = trojan.make_request('https://www.google.com')
    return response
