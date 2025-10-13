#!/bin/bash

# 一键开启代理 - 最简版本
# 服务器: 47.103.143.152, 域名: shenyiqing.xin

echo "🚀 启动代理..."

# 启动ClashX Pro
open -a "ClashX Pro" 2>/dev/null && sleep 3

# 设置系统代理
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890 && \
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890 && \
networksetup -setsocksfirewallproxy "Wi-Fi" 127.0.0.1 7891

# 设置环境变量
export http_proxy=http://127.0.0.1:7890 https_proxy=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890

echo "✅ 代理已开启"
echo "🌐 管理界面: http://127.0.0.1:9090"

# 快速测试
curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5 > /dev/null 2>&1 && echo "✅ Google连接成功" || echo "❌ 连接失败"

# 显示IP
current_ip=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
echo "📍 当前IP: ${current_ip:-未知}"