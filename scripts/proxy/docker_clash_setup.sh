#!/bin/bash

# Docker Clash代理设置脚本
# 服务器: 47.103.143.152
# 用户: root
# 密码: GJc9d5&b5z

SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"

echo "=== Docker Clash代理设置 ==="
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

echo "=== 连接服务器并设置Docker Clash ==="

# 一键安装脚本
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
set -e

echo "检查Docker状态..."
if ! command -v docker &> /dev/null; then
    echo "安装Docker..."
    apt-get update
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
else
    echo "Docker已安装"
fi

echo "创建Clash配置目录..."
mkdir -p /opt/clash

echo "创建Clash配置文件..."
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

echo "停止现有的Clash容器（如果存在）..."
docker stop clash 2>/dev/null || true
docker rm clash 2>/dev/null || true

echo "启动Clash Docker容器..."
docker run -d \
  --name clash \
  --restart unless-stopped \
  -p 7890:7890 \
  -p 7891:7891 \
  -p 9090:9090 \
  -v /opt/clash/config.yaml:/root/.config/clash/config.yaml \
  dreamacro/clash:latest

echo "等待容器启动..."
sleep 10

echo "检查容器状态..."
docker ps | grep clash

echo "检查Clash服务..."
docker logs clash --tail 20

echo "开放防火墙端口..."
ufw allow 7890/tcp
ufw allow 7891/tcp
ufw allow 9090/tcp

echo "测试代理连接..."
curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 || echo "Google连接测试失败"
curl -x http://127.0.0.1:7890 -I https://www.youtube.com --connect-timeout 10 || echo "YouTube连接测试失败"

echo "=== Docker Clash安装完成 ==="
echo "HTTP代理: http://127.0.0.1:7890"
echo "SOCKS代理: socks5://127.0.0.1:7891"
echo "管理界面: http://0.0.0.0:9090"
echo ""
echo "使用方法："
echo "export http_proxy=http://127.0.0.1:7890"
echo "export https_proxy=http://127.0.0.1:7890"
echo "curl -I https://www.google.com"
echo ""
echo "管理命令："
echo "  docker ps | grep clash     # 查看容器状态"
echo "  docker logs clash -f       # 查看日志"
echo "  docker restart clash       # 重启容器"
echo "  docker stop clash          # 停止容器"
EOF

echo ""
echo "=== 设置完成 ==="
echo "Docker Clash代理已成功安装在服务器 $SERVER_IP 上！"
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
echo "  docker ps | grep clash     # 查看容器状态"
echo "  docker logs clash -f       # 查看日志"
echo "  docker restart clash       # 重启容器"
echo "  docker stop clash          # 停止容器"
