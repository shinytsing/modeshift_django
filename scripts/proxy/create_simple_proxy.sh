#!/bin/bash
# 创建简单的HTTP代理服务

echo "=== 创建简单HTTP代理服务 ==="

ssh root@47.103.143.152 << 'EOF'
echo "1. 安装Python和必要工具..."
apt update
apt install -y python3 python3-pip curl wget

echo "2. 创建简单代理服务..."
cat > /opt/simple_proxy.py << 'PYEOF'
#!/usr/bin/env python3
import http.server
import urllib.request
import urllib.parse
import urllib.error
import socket
import threading
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            # 解析目标URL
            url = self.path
            if not url.startswith('http'):
                # 如果不是完整URL，尝试构造
                if url.startswith('/'):
                    url = url[1:]
                url = 'https://' + url
            
            print(f"代理请求: {url}")
            
            # 设置请求头
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    headers[header] = value
            
            # 创建请求
            req = urllib.request.Request(url, headers=headers)
            
            if self.command == 'POST':
                # 读取POST数据
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                req.data = post_data
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                # 发送响应头
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # 发送响应体
                self.wfile.write(response.read())
                
        except Exception as e:
            print(f"代理错误: {e}")
            self.send_error(500, f"代理错误: {str(e)}")
    
    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8080), ProxyHandler)
    print("简单HTTP代理服务启动在端口8080")
    server.serve_forever()
PYEOF

chmod +x /opt/simple_proxy.py

echo "3. 创建systemd服务..."
cat > /etc/systemd/system/simple-proxy.service << 'SERVICEEOF'
[Unit]
Description=Simple HTTP Proxy
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /opt/simple_proxy.py
User=root

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo "4. 启动代理服务..."
systemctl daemon-reload
systemctl enable simple-proxy
systemctl start simple-proxy

echo "5. 配置防火墙..."
ufw allow 8080/tcp

echo "6. 检查服务状态..."
sleep 3
systemctl status simple-proxy --no-pager

echo "7. 测试代理..."
sleep 2
curl -x http://127.0.0.1:8080 -I https://www.google.com --connect-timeout 10 || echo "代理测试失败"

echo "=== 简单代理服务配置完成 ==="
echo "HTTP代理地址: http://47.103.143.152:8080"
echo "使用方法: curl -x http://47.103.143.152:8080 https://www.google.com"
EOF

echo "简单代理服务配置完成"
