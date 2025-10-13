#!/bin/bash

# 简化版Clash代理设置脚本
# 服务器: 47.103.143.152
# 用户: root
# 密码: GJc9d5&b5z

SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"

echo "=== 简化版Clash代理设置 ==="
echo "服务器: $SERVER_IP"

# 检查sshpass
if ! command -v sshpass &> /dev/null; then
    echo "安装sshpass..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install sshpass
    else
        sudo apt-get install -y sshpass
    fi
fi

echo "=== 连接服务器并安装Clash ==="

# 一键安装脚本
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
set -e

echo "更新系统包..."
apt-get update

echo "安装依赖..."
apt-get install -y wget curl unzip

echo "创建Clash目录..."
mkdir -p /opt/clash
cd /opt/clash

echo "下载Clash (使用稳定版本)..."
# 使用已知可用的版本
wget -O clash.gz "https://github.com/Dreamacro/clash/releases/download/v1.17.0/clash-linux-amd64-v1.17.0.gz"
gunzip clash.gz
chmod +x clash

echo "创建配置文件..."
cat > /opt/clash/config.yaml << 'CONFIG_EOF'
port: 7890
socks-port: 7891
allow-lan: true
mode: rule
log-level: silent
external-controller: 0.0.0.0:9090
secret: ""
dns:
  enable: true
  ipv6: false
  nameserver:
    - 223.5.5.5
    - 180.76.76.76
    - 119.29.29.29
    - 8.8.8.8
    - 1.1.1.1
  fallback:
    - 8.8.8.8
    - tls://dns.rubyfish.cn:853
    - tls://1.0.0.1:853
    - tls://dns.google:853
    - https://dns.rubyfish.cn/dns-query
    - https://cloudflare-dns.com/dns-query
    - https://dns.google/dns-query
  fallback-filter:
    geoip: true
    ipcidr:
      - 240.0.0.0/4
      - 0.0.0.0/32
      - 127.0.0.1/32
    domain:
      - +.google.com
      - +.facebook.com
      - +.youtube.com
      - +.xn--ngstr-lra8j.com
      - +.google.cn
      - +.googleapis.cn
      - +.gvt1.com
proxies:
  - name: HongKong-IPLC-HK-1
    type: trojan
    server: iplc-hk-1.trojanwheel.com
    port: 465
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
  - name: Japan-TY-1
    type: trojan
    server: ty-1.rise-fuji.com
    port: 443
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
  - name: UnitedStates-US-1
    type: trojan
    server: us-1.regentgrandvalley.com
    port: 443
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
  - name: Singapore-SG-1
    type: trojan
    server: sg-1.victoriamitrepeak.com
    port: 443
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
  - name: Netherlands-NL-1
    type: trojan
    server: nl-1.concert-geb.com
    port: 443
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
proxy-groups:
  - name: Proxy
    type: select
    proxies:
      - Auto
      - HongKong-IPLC-HK-1
      - Japan-TY-1
      - UnitedStates-US-1
      - Singapore-SG-1
      - Netherlands-NL-1
  - name: Auto
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    proxies:
      - HongKong-IPLC-HK-1
      - Japan-TY-1
      - UnitedStates-US-1
      - Singapore-SG-1
      - Netherlands-NL-1
rules:
  - DOMAIN-SUFFIX,chatgpt.com,Proxy
  - DOMAIN-SUFFIX,ghcr.io,Proxy
  - DOMAIN-SUFFIX,googleapis.cn,Proxy
  - DOMAIN-KEYWORD,googleapis.cn,Proxy
  - DOMAIN-SUFFIX,cn,DIRECT
  - DOMAIN-SUFFIX,126.com,DIRECT
  - DOMAIN-SUFFIX,163.com,DIRECT
  - DOMAIN-SUFFIX,baidu.com,DIRECT
  - DOMAIN-SUFFIX,bilibili.com,DIRECT
  - DOMAIN-SUFFIX,qq.com,DIRECT
  - DOMAIN-SUFFIX,weibo.com,DIRECT
  - DOMAIN-SUFFIX,zhihu.com,DIRECT
  - DOMAIN-KEYWORD,google,Proxy
  - DOMAIN-KEYWORD,gmail,Proxy
  - DOMAIN-KEYWORD,youtube,Proxy
  - DOMAIN-KEYWORD,facebook,Proxy
  - DOMAIN-KEYWORD,twitter,Proxy
  - DOMAIN-KEYWORD,instagram,Proxy
  - DOMAIN-KEYWORD,github,Proxy
  - DOMAIN-SUFFIX,google.com,Proxy
  - DOMAIN-SUFFIX,youtube.com,Proxy
  - DOMAIN-SUFFIX,facebook.com,Proxy
  - DOMAIN-SUFFIX,twitter.com,Proxy
  - DOMAIN-SUFFIX,instagram.com,Proxy
  - DOMAIN-SUFFIX,github.com,Proxy
  - DOMAIN-SUFFIX,stackoverflow.com,Proxy
  - DOMAIN-SUFFIX,medium.com,Proxy
  - DOMAIN-SUFFIX,reddit.com,Proxy
  - DOMAIN-SUFFIX,telegram.org,Proxy
  - DOMAIN-SUFFIX,local,DIRECT
  - IP-CIDR,127.0.0.0/8,DIRECT
  - IP-CIDR,172.16.0.0/12,DIRECT
  - IP-CIDR,192.168.0.0/16,DIRECT
  - IP-CIDR,10.0.0.0/8,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
CONFIG_EOF

echo "创建systemd服务..."
cat > /etc/systemd/system/clash.service << 'SERVICE_EOF'
[Unit]
Description=Clash daemon
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/opt/clash/clash -f /opt/clash/config.yaml
WorkingDirectory=/opt/clash
User=root
Group=root

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "启动Clash服务..."
systemctl daemon-reload
systemctl enable clash
systemctl start clash

echo "等待服务启动..."
sleep 5

echo "检查服务状态..."
systemctl status clash --no-pager

echo "测试代理连接..."
curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 || echo "Google连接测试失败"
curl -x http://127.0.0.1:7890 -I https://www.youtube.com --connect-timeout 10 || echo "YouTube连接测试失败"

echo "=== Clash安装完成 ==="
echo "HTTP代理: http://127.0.0.1:7890"
echo "SOCKS代理: socks5://127.0.0.1:7891"
echo "管理界面: http://0.0.0.0:9090"
echo ""
echo "使用方法："
echo "export http_proxy=http://127.0.0.1:7890"
echo "export https_proxy=http://127.0.0.1:7890"
echo "curl -I https://www.google.com"
EOF

echo ""
echo "=== 设置完成 ==="
echo "Clash代理已成功安装在服务器 $SERVER_IP 上！"
echo ""
echo "现在你可以："
echo "1. SSH连接到服务器: ssh root@$SERVER_IP"
echo "2. 设置代理环境变量:"
echo "   export http_proxy=http://127.0.0.1:7890"
echo "   export https_proxy=http://127.0.0.1:7890"
echo "3. 测试访问Google: curl -I https://www.google.com"
echo "4. 访问管理界面: http://$SERVER_IP:9090"
echo ""
echo "管理命令："
echo "  systemctl status clash    # 查看状态"
echo "  systemctl restart clash   # 重启服务"
echo "  systemctl stop clash      # 停止服务"
echo "  journalctl -u clash -f    # 查看日志"
