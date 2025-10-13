#!/bin/bash

# Cursor区域限制绕过脚本
# 解决"This model provider doesn't serve your region"问题

echo "🌍 解决Cursor区域限制问题..."

# 1. 确保使用美国节点
echo "🇺🇸 切换到美国节点..."
curl -X PUT "http://127.0.0.1:9090/proxies/Proxy" \
  -H "Content-Type: application/json" \
  -d '{"name": "UnitedStates-US-1"}' 2>/dev/null || echo "无法切换节点"

# 2. 设置全局代理模式
echo "🌐 设置全局代理模式..."
curl -X PATCH "http://127.0.0.1:9090/configs" \
  -H "Content-Type: application/json" \
  -d '{"mode": "global"}' 2>/dev/null || echo "无法设置全局模式"

# 3. 测试连接
echo "🧪 测试连接..."
current_ip=$(curl -x http://127.0.0.1:7890 -s https://httpbin.org/ip | grep -o '"[0-9.]*"' | tr -d '"')
echo "当前IP: $current_ip"

# 4. 检查地理位置
echo "📍 检查地理位置..."
location=$(curl -x http://127.0.0.1:7890 -s "https://ipapi.co/$current_ip/json/" | grep -o '"country_name":"[^"]*"' | cut -d'"' -f4)
echo "检测到位置: $location"

# 5. 重启Cursor
echo "🔄 重启Cursor..."
pkill -f "Cursor" 2>/dev/null || true
sleep 3

# 6. 设置环境变量启动Cursor
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

echo "🚀 启动Cursor..."
open -a "Cursor"

echo ""
echo "✅ 配置完成！"
echo "📋 请检查："
echo "   1. Cursor是否正常打开"
echo "   2. 尝试使用Claude模型"
echo "   3. 如果仍有问题，请尝试重新登录Cursor账户"