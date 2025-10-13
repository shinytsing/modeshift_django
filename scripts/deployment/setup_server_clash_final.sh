#!/bin/bash
# 最终配置服务器Clash代理

echo "=== 最终配置服务器Clash代理 ==="

ssh root@47.103.143.152 << 'EOF'
echo "1. 停止现有代理服务..."
systemctl stop simple-proxy 2>/dev/null || true

echo "2. 安装Clash..."
cd /tmp
# 尝试多个下载源
wget -O clash.gz "https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz" || \
curl -L -o clash.gz "https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz" || \
wget -O clash.gz "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz"

if [ -f "clash.gz" ]; then
    gunzip clash.gz
    chmod +x clash-linux-amd64-v1.18.0
    mv clash-linux-amd64-v1.18.0 /opt/clash
    echo "Clash安装成功"
else
    echo "Clash下载失败，使用备用方案..."
    # 创建简单的SOCKS5代理
    cat > /opt/socks5_proxy.py << 'PYEOF'
#!/usr/bin/env python3
import socket
import threading
import select
import struct

class SOCKS5Proxy:
    def __init__(self, host='0.0.0.0', port=1080):
        self.host = host
        self.port = port
        self.server_socket = None
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        print(f"SOCKS5代理服务启动在 {self.host}:{self.port}")
        
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"新连接: {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
    
    def handle_client(self, client_socket):
        try:
            # SOCKS5握手
            data = client_socket.recv(1024)
            if not data or data[0] != 0x05:
                client_socket.close()
                return
            
            # 发送认证方法
            client_socket.send(b'\x05\x00')
            
            # 接收连接请求
            data = client_socket.recv(1024)
            if not data or data[0] != 0x05 or data[1] != 0x01:
                client_socket.close()
                return
            
            # 解析目标地址
            addr_type = data[3]
            if addr_type == 0x01:  # IPv4
                target_host = socket.inet_ntoa(data[4:8])
                target_port = struct.unpack('>H', data[8:10])[0]
            elif addr_type == 0x03:  # 域名
                domain_length = data[4]
                target_host = data[5:5+domain_length].decode()
                target_port = struct.unpack('>H', data[5+domain_length:7+domain_length])[0]
            else:
                client_socket.close()
                return
            
            print(f"连接目标: {target_host}:{target_port}")
            
            # 连接到目标服务器
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(30)
            target_socket.connect((target_host, target_port))
            
            # 发送连接成功响应
            client_socket.send(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
            
            # 开始数据转发
            self.forward_data(client_socket, target_socket)
            
        except Exception as e:
            print(f"处理客户端连接错误: {e}")
        finally:
            client_socket.close()
    
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
    proxy = SOCKS5Proxy('0.0.0.0', 1080)
    proxy.start()
PYEOF
    chmod +x /opt/socks5_proxy.py
    echo "创建了SOCKS5代理服务"
fi

echo "3. 创建Clash配置文件..."
mkdir -p /etc/clash
cat > /etc/clash/config.yaml << 'CONFIGEOF'
port: 7890
socks-port: 7891
allow-lan: true
bind-address: '*'
mode: rule
log-level: info
external-controller: '0.0.0.0:9090'

dns:
  enable: true
  ipv6: false
  nameserver:
    - 223.5.5.5
    - 8.8.8.8
    - 1.1.1.1
  fallback:
    - 8.8.8.8
    - 1.1.1.1

proxies:
  - name: "HongKong-IPLC-HK-1"
    type: trojan
    server: iplc-hk-1.trojanwheel.com
    port: 465
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
  - name: "Japan-TY-1"
    type: trojan
    server: ty-1.rise-fuji.com
    port: 443
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
  - name: "UnitedStates-US-1"
    type: trojan
    server: us-1.regentgrandvalley.com
    port: 443
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true

proxy-groups:
  - name: "Proxy"
    type: select
    proxies:
      - HongKong-IPLC-HK-1
      - Japan-TY-1
      - UnitedStates-US-1
  - name: "Auto"
    type: url-test
    url: 'http://www.gstatic.com/generate_204'
    interval: 300
    proxies:
      - HongKong-IPLC-HK-1
      - Japan-TY-1
      - UnitedStates-US-1

rules:
  - DOMAIN-SUFFIX,google.com,Proxy
  - DOMAIN-SUFFIX,googleapis.com,Proxy
  - DOMAIN-SUFFIX,gmail.com,Proxy
  - DOMAIN-SUFFIX,youtube.com,Proxy
  - DOMAIN-SUFFIX,facebook.com,Proxy
  - DOMAIN-SUFFIX,twitter.com,Proxy
  - DOMAIN-SUFFIX,instagram.com,Proxy
  - DOMAIN-SUFFIX,github.com,Proxy
  - DOMAIN-KEYWORD,google,Proxy
  - DOMAIN-KEYWORD,youtube,Proxy
  - DOMAIN-KEYWORD,facebook,Proxy
  - DOMAIN-KEYWORD,twitter,Proxy
  - DOMAIN-KEYWORD,instagram,Proxy
  - DOMAIN-KEYWORD,github,Proxy
  - DOMAIN-SUFFIX,cn,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
CONFIGEOF

echo "4. 创建systemd服务..."
if [ -f "/opt/clash" ]; then
    cat > /etc/systemd/system/clash.service << 'SERVICEEOF'
[Unit]
Description=Clash daemon
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/opt/clash -d /etc/clash
User=root

[Install]
WantedBy=multi-user.target
SERVICEEOF
else
    cat > /etc/systemd/system/clash.service << 'SERVICEEOF'
[Unit]
Description=SOCKS5 Proxy daemon
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /opt/socks5_proxy.py
User=root

[Install]
WantedBy=multi-user.target
SERVICEEOF
fi

echo "5. 启动服务..."
systemctl daemon-reload
systemctl enable clash
systemctl start clash

echo "6. 配置防火墙..."
ufw allow 7890/tcp
ufw allow 7891/tcp
ufw allow 1080/tcp
ufw reload

echo "7. 检查服务状态..."
sleep 5
systemctl status clash --no-pager

echo "8. 测试代理..."
sleep 3
if [ -f "/opt/clash" ]; then
    echo "测试Clash代理..."
    curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 || echo "Clash代理测试失败"
else
    echo "测试SOCKS5代理..."
    curl --socks5 127.0.0.1:1080 -I https://www.google.com --connect-timeout 10 || echo "SOCKS5代理测试失败"
fi

echo "=== 代理服务配置完成 ==="
if [ -f "/opt/clash" ]; then
    echo "Clash代理地址:"
    echo "HTTP: http://47.103.143.152:7890"
    echo "SOCKS5: socks5://47.103.143.152:7891"
    echo "管理界面: http://47.103.143.152:9090"
else
    echo "SOCKS5代理地址:"
    echo "SOCKS5: socks5://47.103.143.152:1080"
fi
EOF

echo "代理服务配置完成"


