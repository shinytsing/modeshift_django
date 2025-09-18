#!/bin/bash

# 简单代理设置脚本
# 服务器: 47.103.143.152
# 用户: root
# 密码: GJc9d5&b5z

SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"

echo "=== 简单代理设置 ==="
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

echo "=== 连接服务器并设置简单代理 ==="

# 一键安装脚本
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
set -e

echo "安装Tinyproxy..."
apt-get update
apt-get install -y tinyproxy

echo "配置Tinyproxy..."
cat > /etc/tinyproxy/tinyproxy.conf << 'TINYPROXY_EOF'
User tinyproxy
Group tinyproxy
Port 8888
Timeout 600
DefaultErrorFile "/usr/share/tinyproxy/default.html"
StatFile "/usr/share/tinyproxy/stats.html"
Logfile "/var/log/tinyproxy/tinyproxy.log"
LogLevel Info
PidFile "/run/tinyproxy/tinyproxy.pid"
MaxClients 100
MinSpareServers 5
MaxSpareServers 20
StartServers 10
MaxRequestsPerChild 0
ViaProxyName "tinyproxy"
DisableViaHeader Yes
TINYPROXY_EOF

echo "启动Tinyproxy服务..."
systemctl enable tinyproxy
systemctl start tinyproxy

echo "开放防火墙端口..."
ufw allow 8888/tcp

echo "检查服务状态..."
systemctl status tinyproxy --no-pager

echo "测试代理连接..."
curl -x http://127.0.0.1:8888 -I https://www.google.com --connect-timeout 10 || echo "Google连接测试失败"

echo "=== Tinyproxy安装完成 ==="
echo "HTTP代理: http://127.0.0.1:8888"
echo ""
echo "使用方法："
echo "export http_proxy=http://127.0.0.1:8888"
echo "export https_proxy=http://127.0.0.1:8888"
echo "curl -I https://www.google.com"
EOF

echo ""
echo "=== 设置完成 ==="
echo "简单代理已成功安装在服务器 $SERVER_IP 上！"
echo ""
echo "现在你可以："
echo "1. SSH连接到服务器: ssh root@$SERVER_IP"
echo "2. 设置代理环境变量:"
echo "   export http_proxy=http://127.0.0.1:8888"
echo "   export https_proxy=http://127.0.0.1:8888"
echo "3. 测试访问Google: curl -I https://www.google.com"
echo ""
echo "管理命令："
echo "  systemctl status tinyproxy    # 查看状态"
echo "  systemctl restart tinyproxy   # 重启服务"
echo "  systemctl stop tinyproxy      # 停止服务"
echo "  journalctl -u tinyproxy -f    # 查看日志"
