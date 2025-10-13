#!/bin/bash

# Cursor专用代理环境变量配置
# 用于解决Cursor中Claude模型不可用的问题

echo "🔧 配置Cursor专用代理环境..."

# 设置代理环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 设置SOCKS代理
export all_proxy=socks5://127.0.0.1:7891
export ALL_PROXY=socks5://127.0.0.1:7891

# 设置no_proxy（本地地址不走代理）
export no_proxy="localhost,127.0.0.1,::1"
export NO_PROXY="localhost,127.0.0.1,::1"

echo "✅ 代理环境变量已设置"
echo "HTTP代理: $HTTP_PROXY"
echo "HTTPS代理: $HTTPS_PROXY"
echo "SOCKS代理: $ALL_PROXY"

# 测试连接
echo "🧪 测试Cursor API连接..."
if curl -x http://127.0.0.1:7890 -I https://api.cursor.sh --connect-timeout 10 > /dev/null 2>&1; then
    echo "✅ Cursor API连接成功"
else
    echo "❌ Cursor API连接失败"
fi

if curl -x http://127.0.0.1:7890 -I https://claude.ai --connect-timeout 10 > /dev/null 2>&1; then
    echo "✅ Claude AI连接成功"
else
    echo "❌ Claude AI连接失败"
fi

echo ""
echo "🚀 现在可以启动Cursor了："
echo "   open -a Cursor"
echo ""
echo "或者从终端启动Cursor（继承代理环境）："
echo "   source cursor_proxy_env.sh && open -a Cursor"

