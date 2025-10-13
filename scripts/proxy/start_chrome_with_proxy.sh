#!/bin/bash

# Chrome浏览器代理启动脚本
# 使用ClashX Pro代理启动Chrome

echo "🚀 启动Chrome浏览器（使用ClashX Pro代理）..."

# 检查ClashX Pro是否运行
if ! lsof -i :7890 > /dev/null 2>&1; then
    echo "❌ ClashX Pro未运行，请先启动ClashX Pro"
    exit 1
fi

echo "✅ ClashX Pro代理已就绪"

# 启动Chrome并配置代理
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --proxy-server="http://127.0.0.1:7890" \
    --disable-web-security \
    --disable-features=VizDisplayCompositor \
    --user-data-dir="/tmp/chrome_proxy_session" \
    --no-first-run \
    --no-default-browser-check \
    "https://www.google.com/search?q=卓越工程师计划"

echo "🌐 Chrome已启动，代理配置完成"
