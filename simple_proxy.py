#!/usr/bin/env python3
import socket
import threading
import select

class SimpleProxy:
    def __init__(self, host='0.0.0.0', port=7890):
        self.host = host
        self.port = port
        self.server_socket = None
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        print(f"简单代理服务启动在 {self.host}:{self.port}")
        
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"新连接: {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except:
                break
    
    def handle_client(self, client_socket):
        try:
            # 读取请求
            data = client_socket.recv(4096)
            if not data:
                return
            
            request = data.decode('utf-8', errors='ignore')
            print(f"收到请求: {request[:100]}...")
            
            # 解析请求
            lines = request.split('\n')
            if not lines:
                return
            
            first_line = lines[0]
            if 'CONNECT' in first_line:
                # HTTPS代理
                self.handle_https(client_socket, first_line)
            else:
                # HTTP代理
                self.handle_http(client_socket, request)
                
        except Exception as e:
            print(f"处理客户端错误: {e}")
        finally:
            client_socket.close()
    
    def handle_https(self, client_socket, first_line):
        try:
            # 解析CONNECT请求
            parts = first_line.split()
            if len(parts) < 2:
                return
            
            target = parts[1]
            if ':' in target:
                host, port = target.split(':')
                port = int(port)
            else:
                host = target
                port = 443
            
            # 连接到目标服务器
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(30)
            target_socket.connect((host, port))
            
            # 发送200响应
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            
            # 开始数据转发
            self.forward_data(client_socket, target_socket)
            
        except Exception as e:
            print(f"HTTPS代理错误: {e}")
            client_socket.send(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
    
    def handle_http(self, client_socket, request):
        try:
            # 简单的HTTP代理
            lines = request.split('\n')
            first_line = lines[0]
            parts = first_line.split()
            
            if len(parts) < 2:
                return
            
            url = parts[1]
            if url.startswith('/'):
                # 相对URL，需要添加host
                host = None
                for line in lines:
                    if line.lower().startswith('host:'):
                        host = line.split(':', 1)[1].strip()
                        break
                
                if host:
                    url = f"http://{host}{url}"
                else:
                    url = f"http://{url}"
            
            print(f"代理HTTP请求: {url}")
            
            # 直接转发请求
            import urllib.request
            import urllib.parse
            
            req = urllib.request.Request(url)
            for line in lines[1:]:
                if ':' in line:
                    header, value = line.split(':', 1)
                    if header.lower() not in ['host', 'connection']:
                        req.add_header(header.strip(), value.strip())
            
            with urllib.request.urlopen(req, timeout=30) as response:
                # 发送响应头
                client_socket.send(f'HTTP/1.1 {response.status} {response.reason}\r\n'.encode())
                for header, value in response.headers.items():
                    client_socket.send(f'{header}: {value}\r\n'.encode())
                client_socket.send(b'\r\n')
                
                # 发送响应体
                while True:
                    data = response.read(4096)
                    if not data:
                        break
                    client_socket.send(data)
                    
        except Exception as e:
            print(f"HTTP代理错误: {e}")
            client_socket.send(b'HTTP/1.1 500 Internal Server Error\r\n\r\n')
    
    def forward_data(self, client_socket, target_socket):
        try:
            while True:
                ready_sockets, _, _ = select.select([client_socket, target_socket], [], [], 30)
                if not ready_sockets:
                    break
                
                for sock in ready_sockets:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return
                        
                        if sock is client_socket:
                            target_socket.send(data)
                        else:
                            client_socket.send(data)
                    except:
                        return
        except:
            pass
        finally:
            target_socket.close()

if __name__ == '__main__':
    proxy = SimpleProxy('0.0.0.0', 7890)
    proxy.start()
