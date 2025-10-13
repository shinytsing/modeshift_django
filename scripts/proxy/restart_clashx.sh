#!/bin/bash

# ClashX Pro 重启脚本

echo "=== ClashX Pro 重启脚本 ==="

# 检查ClashX Pro是否在运行
if pgrep -f "ClashX Pro" > /dev/null; then
    echo "正在停止ClashX Pro..."
    pkill -f "ClashX Pro"
    sleep 3
fi

# 检查是否完全停止
if pgrep -f "ClashX Pro" > /dev/null; then
    echo "强制停止ClashX Pro..."
    pkill -9 -f "ClashX Pro"
    sleep 2
fi

echo "启动ClashX Pro..."
open -a "ClashX Pro"

echo "等待ClashX Pro启动..."
sleep 5

# 检查是否启动成功
if pgrep -f "ClashX Pro" > /dev/null; then
    echo "✅ ClashX Pro 启动成功"
    
    # 等待服务完全启动
    echo "等待服务完全启动..."
    sleep 10
    
    # 检查端口
    if lsof -i :7890 > /dev/null 2>&1; then
        echo "✅ 代理端口 7890 已启动"
    else
        echo "❌ 代理端口 7890 未启动"
    fi
    
    if lsof -i :9090 > /dev/null 2>&1; then
        echo "✅ 管理端口 9090 已启动"
    else
        echo "❌ 管理端口 9090 未启动"
    fi
    
else
    echo "❌ ClashX Pro 启动失败"
    exit 1
fi

echo "=== 重启完成 ==="
