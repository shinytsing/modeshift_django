#!/bin/bash

# 代理开关GUI启动脚本
# 双击此文件即可启动代理开关GUI应用

echo "=== 启动代理开关GUI ==="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUI_FILE="$SCRIPT_DIR/代理开关GUI.py"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    osascript -e 'display dialog "Python3 未安装，请先安装Python3" with title "错误" buttons {"确定"} default button "确定"'
    exit 1
fi

# 检查tkinter是否可用
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter 未安装，请先安装tkinter"
    osascript -e 'display dialog "tkinter 未安装，请先安装tkinter" with title "错误" buttons {"确定"} default button "确定"'
    exit 1
fi

# 检查GUI文件是否存在
if [ ! -f "$GUI_FILE" ]; then
    echo "❌ GUI文件不存在: $GUI_FILE"
    osascript -e 'display dialog "GUI文件不存在" with title "错误" buttons {"确定"} default button "确定"'
    exit 1
fi

echo "✅ 启动代理开关GUI..."
python3 "$GUI_FILE"
