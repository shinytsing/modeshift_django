#!/bin/bash

# 检查服务器代理设置脚本
# 服务器: 47.103.143.152
# 用户: root
# 密码: GJc9d5&b5z

SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"

echo "=== 检查服务器代理设置 ==="
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

echo "=== 连接服务器并检查代理工具 ==="

# 检查服务器上的代理工具
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
set -e

echo "=== 检查服务器环境 ==="
echo "系统信息:"
uname -a
echo ""

echo "检查已安装的代理工具:"
which clash 2>/dev/null && echo "Clash已安装" || echo "Clash未安装"
which v2ray 2>/dev/null && echo "V2Ray已安装" || echo "V2Ray未安装"
which shadowsocks 2>/dev/null && echo "Shadowsocks已安装" || echo "Shadowsocks未安装"
which proxychains 2>/dev/null && echo "Proxychains已安装" || echo "Proxychains未安装"
echo ""

echo "检查网络连接:"
echo "测试Google连接:"
curl -I https://www.google.com --connect-timeout 10 || echo "Google连接失败"
echo ""

echo "测试YouTube连接:"
curl -I https://www.youtube.com --connect-timeout 10 || echo "YouTube连接失败"
echo ""

echo "测试GitHub连接:"
curl -I https://www.github.com --connect-timeout 10 || echo "GitHub连接失败"
echo ""

echo "检查防火墙状态:"
ufw status 2>/dev/null || iptables -L 2>/dev/null || echo "无法检查防火墙状态"
echo ""

echo "检查端口占用:"
netstat -tlnp | grep -E ":(7890|7891|9090|1080|8080)" || echo "相关端口未被占用"
echo ""

echo "检查系统服务:"
systemctl list-units --type=service | grep -E "(clash|proxy|v2ray|ss)" || echo "未找到相关代理服务"
echo ""

echo "=== 建议的解决方案 ==="
echo "1. 如果Google/YouTube连接失败，说明需要代理"
echo "2. 可以尝试安装以下工具之一："
echo "   - Clash (推荐)"
echo "   - V2Ray"
echo "   - Shadowsocks"
echo "   - Proxychains"
echo "3. 或者使用Docker运行代理容器"
echo "4. 检查防火墙设置，确保代理端口开放"
EOF

echo ""
echo "=== 检查完成 ==="
echo "请根据服务器检查结果选择合适的代理方案"
