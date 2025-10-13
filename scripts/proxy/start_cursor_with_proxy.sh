#!/bin/bash

# Cursor启动脚本 - 解决Claude模型不可用问题
# 使用代理环境启动Cursor

echo "🚀 启动Cursor with 代理环境..."

# 设置代理环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7891
export ALL_PROXY=socks5://127.0.0.1:7891

# 设置no_proxy
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"

# 设置SSL相关环境变量
export SSL_CERT_FILE=""
export SSL_CERT_DIR=""
export CURL_CA_BUNDLE=""

echo "✅ 代理环境已配置"
echo "🌐 当前IP: $(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip | grep -o '"[0-9.]*"' | tr -d '"')"

# 关闭现有的Cursor进程
echo "🔄 关闭现有Cursor进程..."
pkill -f "Cursor" 2>/dev/null || true
sleep 2

# 启动Cursor
echo "🚀 启动Cursor..."
open -a "Cursor"

echo "✅ Cursor已启动，请检查Claude模型是否可用"

