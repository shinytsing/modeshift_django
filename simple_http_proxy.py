#!/usr/bin/env python3
import socket
import threading
import select
import time

class SimpleHTTPProxy:
    def __init__(self, host='0.0.0.0', port=7890):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        self.running = True
        
        print(f"简单HTTP代理启动在 {self.host}:{self.port}")
        
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if self.running:
                    print(f"接受连接错误: {e}")
    
    def handle_client(self, client_socket, addr):
        try:
            # 接收客户端请求
            request = client_socket.recv(4096).decode('utf-8')
            if not request:
                return
            
            # 解析请求
            lines = request.split('\n')
            if not lines:
                return
            
            first_line = lines[0]
            parts = first_line.split()
            if len(parts) < 3:
                return
            
            method = parts[0]
            url = parts[1]
            
            # 解析主机和端口
            if '://' in url:
                url = url.split('://', 1)[1]
            
            if '/' in url:
                host_port, path = url.split('/', 1)
                path = '/' + path
            else:
                host_port = url
                path = '/'
            
            if ':' in host_port:
                host, port = host_port.split(':')
                port = int(port)
            else:
                host = host_port
                port = 80 if method == 'GET' else 443
            
            # 创建到目标服务器的连接
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(30)
            target_socket.connect((host, port))
            
            # 转发请求
            target_socket.send(request.encode('utf-8'))
            
            # 转发响应
            while True:
                try:
                    data = target_socket.recv(4096)
                    if not data:
                        break
                    client_socket.send(data)
                except:
                    break
            
            target_socket.close()
            client_socket.close()
            
        except Exception as e:
            print(f"处理客户端错误: {e}")
            try:
                client_socket.close()
            except:
                pass
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()

if __name__ == "__main__":
    proxy = SimpleHTTPProxy()
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
        print("代理服务已停止")
