#!/bin/bash

# 检查代理状态

echo "=== 代理状态检查 ==="

# 检查ClashX Pro进程
if pgrep -f "ClashX Pro" > /dev/null; then
    echo "✅ ClashX Pro 正在运行"
    clashx_pid=$(pgrep -f "ClashX Pro")
    echo "   进程ID: $clashx_pid"
else
    echo "❌ ClashX Pro 未运行"
fi

# 检查代理端口
echo ""
echo "端口状态:"
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

# 检查系统代理设置
echo ""
echo "系统代理设置:"
web_proxy=$(networksetup -getwebproxy "Wi-Fi")
if [[ $web_proxy == *"Enabled: Yes"* ]]; then
    echo "✅ HTTP代理已启用"
    echo "   $web_proxy"
else
    echo "❌ HTTP代理未启用"
fi

secure_proxy=$(networksetup -getsecurewebproxy "Wi-Fi")
if [[ $secure_proxy == *"Enabled: Yes"* ]]; then
    echo "✅ HTTPS代理已启用"
    echo "   $secure_proxy"
else
    echo "❌ HTTPS代理未启用"
fi

socks_proxy=$(networksetup -getsocksfirewallproxy "Wi-Fi")
if [[ $socks_proxy == *"Enabled: Yes"* ]]; then
    echo "✅ SOCKS代理已启用"
    echo "   $socks_proxy"
else
    echo "❌ SOCKS代理未启用"
fi

# 测试连接
echo ""
echo "连接测试:"
if curl -x http://127.0.0.1:7890 -I https://www.google.com --connect-timeout 5 > /dev/null 2>&1; then
    echo "✅ Google连接成功（通过代理）"
else
    echo "❌ Google连接失败"
fi

if curl -I https://www.baidu.com --connect-timeout 5 > /dev/null 2>&1; then
    echo "✅ 百度连接成功（直连）"
else
    echo "❌ 百度连接失败"
fi

# 获取当前IP
echo ""
echo "IP地址检测:"
current_ip=$(curl -s https://httpbin.org/ip 2>/dev/null | grep -o '"[0-9.]*"' | tr -d '"')
if [ -n "$current_ip" ]; then
    echo "当前IP: $current_ip"
else
    echo "无法获取IP地址"
fi
