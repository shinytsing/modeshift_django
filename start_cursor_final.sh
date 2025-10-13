#!/bin/bash

# 最终Cursor启动脚本 - 解决Claude模型问题
# 包含所有必要的配置

echo "🚀 启动Cursor with 完整代理配置..."

# 1. 确保Clash运行
if ! pgrep -f "ClashX Pro" > /dev/null; then
    echo "⚠️  ClashX Pro未运行，正在启动..."
    open -a "ClashX Pro"
    sleep 5
fi

# 2. 设置系统代理
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 7890
networksetup -setsocksfirewallproxy "Wi-Fi" 127.0.0.1 7891

# 3. 设置环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7891
export ALL_PROXY=socks5://127.0.0.1:7891
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"

# 4. SSL相关设置
export SSL_CERT_FILE=""
export SSL_CERT_DIR=""
export CURL_CA_BUNDLE=""
export REQUESTS_CA_BUNDLE=""
export NODE_TLS_REJECT_UNAUTHORIZED=0

# 5. 测试连接
echo "🧪 测试连接..."
current_ip=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip | grep -o '"[0-9.]*"' | tr -d '"')
echo "🌐 当前IP: $current_ip"

# 6. 关闭现有Cursor
echo "🔄 关闭现有Cursor进程..."
pkill -f "Cursor" 2>/dev/null || true
sleep 2

# 7. 启动Cursor
echo "🚀 启动Cursor..."
open -a "Cursor"

echo ""
echo "✅ Cursor已启动！"
echo "📋 请检查以下内容："
echo "   1. Cursor是否正常打开"
echo "   2. 在Cursor中尝试使用Claude模型"
echo "   3. 如果仍有问题，请检查Cursor的设置中的代理配置"
echo ""
echo "🔧 如果问题持续，可以尝试："
echo "   - 在Cursor设置中手动设置代理: http://127.0.0.1:7890"
echo "   - 重启Cursor应用"
echo "   - 检查Cursor的账户设置"
