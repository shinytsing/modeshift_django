#!/bin/bash

# ClashX Pro 代理管理器安装脚本

echo "=== ClashX Pro 代理管理器安装脚本 ==="

# 检查是否已安装ClashX Pro
if [ ! -d "/Applications/ClashX Pro.app" ]; then
    echo "❌ 未检测到ClashX Pro，请先安装ClashX Pro"
    echo "下载地址: https://github.com/yichengchen/clashX"
    exit 1
fi

echo "✅ 检测到ClashX Pro已安装"

# 复制应用到Applications目录
APP_NAME="ClashX代理管理器"
if [ -d "${APP_NAME}.app" ]; then
    echo "正在安装到Applications目录..."
    sudo cp -R "${APP_NAME}.app" "/Applications/"
    echo "✅ 安装完成！"
    echo "您可以在Applications文件夹中找到'ClashX代理管理器'应用"
else
    echo "❌ 未找到应用包，请先运行打包脚本"
    exit 1
fi
