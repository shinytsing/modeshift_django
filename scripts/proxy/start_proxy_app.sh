#!/bin/bash

# 启动代理开关应用

echo "=== 启动代理开关应用 ==="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查tkinter是否可用
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter 未安装，请先安装tkinter"
    echo "macOS用户可以使用: brew install python-tk"
    exit 1
fi

# 启动应用
echo "✅ 启动代理开关应用..."
python3 proxy_gui.py
