#!/bin/bash
# 服务器端Clash配置脚本 - 让服务器作为中转站访问外网

echo "=== 服务器Clash中转站配置脚本 ==="
echo "目标: 配置服务器作为代理中转站，帮助访问外网"
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请以root用户运行此脚本"
    exit 1
fi

# 更新系统包
echo "1. 更新系统包..."
yum update -y || apt update -y

# 安装必要工具
echo "2. 安装必要工具..."
yum install -y wget curl unzip || apt install -y wget curl unzip

# 下载Clash
echo "3. 下载Clash..."
cd /opt
wget -O clash-linux-amd64.gz https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz
gunzip clash-linux-amd64.gz
mv clash-linux-amd64 clash
chmod +x clash

# 创建配置目录
echo "4. 创建配置目录..."
mkdir -p /etc/clash
mkdir -p /var/log/clash

# 创建Clash配置文件
echo "5. 创建Clash配置文件..."
cat > /etc/clash/config.yaml << 'EOF'
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
    - tls://dns.google:853
    - https://dns.google/dns-query

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
  - name: "Singapore-SG-1"
    type: trojan
    server: sg-1.victoriamitrepeak.com
    port: 443
    password: GUGm7DHtpSx7SuPyUD
    alpn:
      - h2
      - http/1.1
    skip-cert-verify: true
  - name: "Netherlands-NL-1"
    type: trojan
    server: nl-1.concert-geb.com
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
      - Auto
      - HongKong-IPLC-HK-1
      - Japan-TY-1
      - UnitedStates-US-1
      - Singapore-SG-1
      - Netherlands-NL-1
  - name: "Auto"
    type: url-test
    url: 'http://www.gstatic.com/generate_204'
    interval: 300
    proxies:
      - HongKong-IPLC-HK-1
      - Japan-TY-1
      - UnitedStates-US-1
      - Singapore-SG-1
      - Netherlands-NL-1

rules:
  - DOMAIN-SUFFIX,google.com,Proxy
  - DOMAIN-SUFFIX,googleapis.com,Proxy
  - DOMAIN-SUFFIX,gmail.com,Proxy
  - DOMAIN-SUFFIX,youtube.com,Proxy
  - DOMAIN-SUFFIX,facebook.com,Proxy
  - DOMAIN-SUFFIX,twitter.com,Proxy
  - DOMAIN-SUFFIX,instagram.com,Proxy
  - DOMAIN-SUFFIX,github.com,Proxy
  - DOMAIN-SUFFIX,stackoverflow.com,Proxy
  - DOMAIN-SUFFIX,reddit.com,Proxy
  - DOMAIN-KEYWORD,google,Proxy
  - DOMAIN-KEYWORD,youtube,Proxy
  - DOMAIN-KEYWORD,facebook,Proxy
  - DOMAIN-KEYWORD,twitter,Proxy
  - DOMAIN-KEYWORD,instagram,Proxy
  - DOMAIN-KEYWORD,github,Proxy
  - DOMAIN-SUFFIX,cn,DIRECT
  - DOMAIN-SUFFIX,126.com,DIRECT
  - DOMAIN-SUFFIX,163.com,DIRECT
  - DOMAIN-SUFFIX,baidu.com,DIRECT
  - DOMAIN-SUFFIX,qq.com,DIRECT
  - GEOIP,CN,DIRECT
  - MATCH,Proxy
EOF

# 创建systemd服务文件
echo "6. 创建systemd服务..."
cat > /etc/systemd/system/clash.service << 'EOF'
[Unit]
Description=Clash daemon
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/opt/clash -d /etc/clash
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
StandardOutput=journal
StandardError=journal
SyslogIdentifier=clash

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
systemctl daemon-reload

# 启动Clash服务
echo "7. 启动Clash服务..."
systemctl enable clash
systemctl start clash

# 检查服务状态
echo "8. 检查服务状态..."
sleep 3
systemctl status clash --no-pager

# 配置防火墙
echo "9. 配置防火墙..."
# 开放Clash端口
firewall-cmd --permanent --add-port=7890/tcp || ufw allow 7890/tcp
firewall-cmd --permanent --add-port=7891/tcp || ufw allow 7891/tcp
firewall-cmd --permanent --add-port=9090/tcp || ufw allow 9090/tcp
firewall-cmd --reload || ufw reload

# 测试代理连接
echo "10. 测试代理连接..."
sleep 5
curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 || echo "代理测试失败"

echo ""
echo "=== 配置完成 ==="
echo "Clash代理服务已启动，服务器现在可以作为中转站访问外网"
echo "代理地址: http://47.103.143.152:7890"
echo "SOCKS5地址: socks5://47.103.143.152:7891"
echo "管理界面: http://47.103.143.152:9090"
echo ""
echo "使用方法:"
echo "1. 在客户端设置HTTP代理: 47.103.143.152:7890"
echo "2. 在客户端设置SOCKS5代理: 47.103.143.152:7891"
echo "3. 通过管理界面切换节点: http://47.103.143.152:9090"
echo ""
echo "服务管理命令:"
echo "启动: systemctl start clash"
echo "停止: systemctl stop clash"
echo "重启: systemctl restart clash"
echo "状态: systemctl status clash"
echo "日志: journalctl -u clash -f"
