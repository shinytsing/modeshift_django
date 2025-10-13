#!/bin/bash

# 快速关闭代理
echo "🛑 关闭代理..."

# 关闭系统代理
networksetup -setwebproxystate "Wi-Fi" off
networksetup -setsecurewebproxystate "Wi-Fi" off
networksetup -setsocksfirewallproxystate "Wi-Fi" off

# 清除环境变量
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY

echo "✅ 代理已关闭"

# 测试直连
if curl -I https://www.baidu.com --connect-timeout 5 > /dev/null 2>&1; then
    echo "✅ 百度连接成功（直连）"
else
    echo "❌ 连接测试失败"
fi

# 显示当前IP
current_ip=$(curl -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
echo "📍 当前IP: ${current_ip:-未知}"
