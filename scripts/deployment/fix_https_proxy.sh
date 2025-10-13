#!/bin/bash
# 修复HTTPS代理支持

echo "=== 修复HTTPS代理支持 ==="

ssh root@47.103.143.152 << 'EOF'
echo "1. 停止现有代理服务..."
systemctl stop simple-proxy

echo "2. 创建支持HTTPS的代理服务..."
cat > /opt/https_proxy.py << 'PYEOF'
#!/usr/bin/env python3
import http.server
import socketserver
import socket
import threading
import ssl
import urllib.request
import urllib.parse
import urllib.error
import select

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        """处理HTTPS CONNECT请求"""
        try:
            # 解析目标地址
            host, port = self.path.split(':')
            port = int(port)
            
            print(f"CONNECT请求: {host}:{port}")
            
            # 创建到目标服务器的连接
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(30)
            target_socket.connect((host, port))
            
            # 发送200 Connection Established响应
            self.send_response(200, 'Connection Established')
            self.send_header('Connection', 'close')
            self.end_headers()
            
            # 开始隧道传输
            self.tunnel_data(self.connection, target_socket)
            
        except Exception as e:
            print(f"CONNECT错误: {e}")
            self.send_error(502, f"CONNECT错误: {str(e)}")
    
    def tunnel_data(self, client_socket, target_socket):
        """在客户端和目标服务器之间传输数据"""
        try:
            while True:
                # 使用select检查socket是否可读
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
    
    def do_GET(self):
        """处理HTTP GET请求"""
        self.handle_http_request()
    
    def do_POST(self):
        """处理HTTP POST请求"""
        self.handle_http_request()
    
    def handle_http_request(self):
        """处理HTTP请求"""
        try:
            url = self.path
            if not url.startswith('http'):
                if url.startswith('/'):
                    url = url[1:]
                url = 'http://' + url
            
            print(f"HTTP请求: {url}")
            
            # 设置请求头
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    headers[header] = value
            
            # 创建请求
            req = urllib.request.Request(url, headers=headers)
            
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req.data = post_data
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.read())
                
        except Exception as e:
            print(f"HTTP请求错误: {e}")
            self.send_error(500, f"HTTP请求错误: {str(e)}")
    
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8080), ProxyHandler)
    print("HTTPS代理服务启动在端口8080")
    server.serve_forever()
PYEOF

chmod +x /opt/https_proxy.py

echo "3. 重启代理服务..."
systemctl start simple-proxy

echo "4. 检查服务状态..."
sleep 3
systemctl status simple-proxy --no-pager

echo "5. 测试HTTPS代理..."
sleep 2
curl -x http://127.0.0.1:8080 -I https://www.google.com --connect-timeout 10 || echo "HTTPS代理测试失败"

echo "6. 测试HTTP代理..."
curl -x http://127.0.0.1:8080 -I http://httpbin.org/ip --connect-timeout 10 || echo "HTTP代理测试失败"

echo "=== HTTPS代理修复完成 ==="
EOF

echo "HTTPS代理修复完成"
