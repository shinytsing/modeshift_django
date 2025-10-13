#!/bin/bash

# 一键关闭代理 - 最简版本

echo "🛑 关闭代理..."

# 关闭系统代理
networksetup -setwebproxystate "Wi-Fi" off && \
networksetup -setsecurewebproxystate "Wi-Fi" off && \
networksetup -setsocksfirewallproxystate "Wi-Fi" off

# 清除环境变量
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

echo "✅ 代理已关闭"

# 测试直连
curl -I https://www.baidu.com --connect-timeout 5 > /dev/null 2>&1 && echo "✅ 百度连接成功（直连）" || echo "❌ 连接失败"

# 显示IP
current_ip=$(curl -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
echo "📍 当前IP: ${current_ip:-未知}"