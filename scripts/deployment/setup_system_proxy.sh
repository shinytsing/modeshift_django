#!/bin/bash

# 系统级代理配置脚本 - 解决Cursor Claude模型问题

echo "🔧 配置系统级代理..."

# 1. 设置系统代理
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsocksfirewallproxy "Wi-Fi" 127.0.0.1 7891

# 2. 设置代理绕过列表
networksetup -setproxybypassdomains "Wi-Fi" "localhost" "127.0.0.1" "::1" "*.local"

# 3. 设置环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7891
export ALL_PROXY=socks5://127.0.0.1:7891

# 4. 设置SSL相关环境变量
export SSL_CERT_FILE=""
export SSL_CERT_DIR=""
export CURL_CA_BUNDLE=""
export REQUESTS_CA_BUNDLE=""

# 5. 设置Node.js代理（如果Cursor使用Node.js）
export NODE_TLS_REJECT_UNAUTHORIZED=0

echo "✅ 系统代理已配置"
echo "🌐 当前IP: $(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip | grep -o '"[0-9.]*"' | tr -d '"')"

# 6. 测试关键连接
echo "🧪 测试关键连接..."
echo -n "Google: "
curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5 > /dev/null 2>&1 && echo "✅" || echo "❌"

echo -n "GitHub: "
curl -x http://127.0.0.1:7890 -I https://www.github.com --connect-timeout 5 > /dev/null 2>&1 && echo "✅" || echo "❌"

echo -n "Claude: "
curl -x http://127.0.0.1:7890 -I https://claude.ai --connect-timeout 5 > /dev/null 2>&1 && echo "✅" || echo "❌"

echo ""
echo "🚀 现在可以启动Cursor了"
echo "   完全退出Cursor，然后重新打开"