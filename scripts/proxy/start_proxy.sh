#!/bin/bash

# 快速启动代理 - 简化版
# 服务器: 47.103.143.152, 域名: shenyiqing.xin

echo "🚀 启动ClashX Pro代理..."

# 启动ClashX Pro
open -a "ClashX Pro" 2>/dev/null

# 等待启动
sleep 5

# 设置系统代理
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsocksfirewallproxy "Wi-Fi" 127.0.0.1 7891

# 设置环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

echo "✅ 代理已启动"
echo "🌐 管理界面: http://127.0.0.1:9090"

# 快速测试
if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5 > /dev/null 2>&1; then
    echo "✅ Google连接成功"
else
    echo "❌ 连接测试失败"
fi

# 显示当前IP
current_ip=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
echo "📍 当前IP: ${current_ip:-未知}"
