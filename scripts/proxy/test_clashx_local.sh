#!/bin/bash

# ClashX Pro 本地测试脚本
# 用于测试ClashX Pro的代理功能和外网访问情况

echo "=== ClashX Pro 本地测试脚本 ==="
echo "测试时间: $(date)"
echo ""

# 设置代理环境变量
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

echo "已设置代理环境变量:"
echo "  HTTP_PROXY: $HTTP_PROXY"
echo "  HTTPS_PROXY: $HTTPS_PROXY"
echo ""

# 检查ClashX Pro进程
echo "=== 检查ClashX Pro进程 ==="
if pgrep -f "ClashX Pro" > /dev/null; then
    echo "✅ ClashX Pro 正在运行"
    CLASHX_PID=$(pgrep -f "ClashX Pro")
    echo "   进程ID: $CLASHX_PID"
else
    echo "❌ ClashX Pro 未运行"
    echo "请先启动ClashX Pro应用程序"
    exit 1
fi
echo ""

# 检查代理端口
echo "=== 检查代理端口 ==="
if lsof -i :7890 > /dev/null 2>&1; then
    echo "✅ HTTP代理端口 7890 正在监听"
else
    echo "❌ HTTP代理端口 7890 未监听"
fi

if lsof -i :7891 > /dev/null 2>&1; then
    echo "✅ SOCKS代理端口 7891 正在监听"
else
    echo "❌ SOCKS代理端口 7891 未监听"
fi

if lsof -i :9090 > /dev/null 2>&1; then
    echo "✅ 管理界面端口 9090 正在监听"
else
    echo "❌ 管理界面端口 9090 未监听"
fi
echo ""

# 测试代理连接
echo "=== 测试代理连接 ==="

# 测试Google连接
echo "测试Google连接..."
if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo "✅ Google连接成功"
else
    echo "❌ Google连接失败"
fi

# 测试YouTube连接
echo "测试YouTube连接..."
if curl -x http://127.0.0.1:7890 -I https://www.youtube.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo "✅ YouTube连接成功"
else
    echo "❌ YouTube连接失败"
fi

# 测试GitHub连接
echo "测试GitHub连接..."
if curl -x http://127.0.0.1:7890 -I https://www.github.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo "✅ GitHub连接成功"
else
    echo "❌ GitHub连接失败"
fi

# 测试Facebook连接
echo "测试Facebook连接..."
if curl -x http://127.0.0.1:7890 -I https://www.facebook.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo "✅ Facebook连接成功"
else
    echo "❌ Facebook连接失败"
fi

# 测试Twitter连接
echo "测试Twitter连接..."
if curl -x http://127.0.0.1:7890 -I https://www.twitter.com --connect-timeout 10 --max-time 15 > /dev/null 2>&1; then
    echo "✅ Twitter连接成功"
else
    echo "❌ Twitter连接失败"
fi
echo ""

# 测试IP地址检测
echo "=== 测试IP地址检测 ==="
echo "检测当前IP地址..."
CURRENT_IP=$(curl -x http://127.0.0.1:7890 -s --connect-timeout 10 --max-time 15 https://ipinfo.io/ip 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$CURRENT_IP" ]; then
    echo "✅ 当前IP地址: $CURRENT_IP"
    
    # 获取IP详细信息
    echo "获取IP详细信息..."
    IP_INFO=$(curl -x http://127.0.0.1:7890 -s --connect-timeout 10 --max-time 15 https://ipinfo.io/$CURRENT_IP 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$IP_INFO" ]; then
        echo "IP信息: $IP_INFO"
    fi
else
    echo "❌ 无法获取IP地址"
fi
echo ""

# 测试DNS解析
echo "=== 测试DNS解析 ==="
echo "测试Google DNS解析..."
if nslookup google.com 8.8.8.8 > /dev/null 2>&1; then
    echo "✅ Google DNS解析正常"
else
    echo "❌ Google DNS解析失败"
fi

echo "测试Cloudflare DNS解析..."
if nslookup cloudflare.com 1.1.1.1 > /dev/null 2>&1; then
    echo "✅ Cloudflare DNS解析正常"
else
    echo "❌ Cloudflare DNS解析失败"
fi
echo ""

# 测试代理速度
echo "=== 测试代理速度 ==="
echo "测试Google访问速度..."
GOOGLE_TIME=$(curl -x http://127.0.0.1:7890 -w "%{time_total}" -o /dev/null -s https://www.google.com --connect-timeout 10 --max-time 15 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$GOOGLE_TIME" ]; then
    echo "✅ Google访问时间: ${GOOGLE_TIME}秒"
else
    echo "❌ Google访问速度测试失败"
fi

echo "测试YouTube访问速度..."
YOUTUBE_TIME=$(curl -x http://127.0.0.1:7890 -w "%{time_total}" -o /dev/null -s https://www.youtube.com --connect-timeout 10 --max-time 15 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$YOUTUBE_TIME" ]; then
    echo "✅ YouTube访问时间: ${YOUTUBE_TIME}秒"
else
    echo "❌ YouTube访问速度测试失败"
fi
echo ""

# 测试管理界面
echo "=== 测试管理界面 ==="
echo "测试Clash管理界面..."
if curl -s http://127.0.0.1:9090 > /dev/null 2>&1; then
    echo "✅ Clash管理界面可访问: http://127.0.0.1:9090"
else
    echo "❌ Clash管理界面不可访问"
fi
echo ""

# 显示代理配置信息
echo "=== 代理配置信息 ==="
echo "HTTP代理: http://127.0.0.1:7890"
echo "SOCKS代理: socks5://127.0.0.1:7891"
echo "管理界面: http://127.0.0.1:9090"
echo ""

# 显示使用说明
echo "=== 使用说明 ==="
echo "1. 在终端中使用代理:"
echo "   export http_proxy=http://127.0.0.1:7890"
echo "   export https_proxy=http://127.0.0.1:7890"
echo ""
echo "2. 在浏览器中设置代理:"
echo "   HTTP代理: 127.0.0.1:7890"
echo "   SOCKS代理: 127.0.0.1:7891"
echo ""
echo "3. 访问Clash管理界面:"
echo "   http://127.0.0.1:9090"
echo ""

echo "=== 测试完成 ==="
echo "测试时间: $(date)"
