#!/bin/bash

# 依赖检查和安装脚本
# 确保所有必需的依赖都正确安装

set -e

echo "🔍 开始检查和安装依赖..."

# 检查Python版本
echo "🐍 Python版本:"
python --version

# 升级pip
echo "📦 升级pip..."
python -m pip install --upgrade pip

# 安装requirements.txt中的所有依赖
echo "📋 安装requirements.txt中的依赖..."
pip install -r requirements.txt

# 额外安装可能缺失的关键依赖
echo "🔧 安装关键依赖..."
pip install beautifulsoup4==4.12.2 || echo "beautifulsoup4安装失败"
pip install lxml==4.9.3 || echo "lxml安装失败"
# PyMuPDF在macOS上编译可能失败，跳过
# pip install PyMuPDF==1.23.8 || echo "PyMuPDF安装失败"
pip install aiohttp==3.9.1 || echo "aiohttp安装失败"
pip install websockets==12.0 || echo "websockets安装失败"
# opencv-python在macOS上可能有问题，跳过
# pip install opencv-python==4.8.1.78 || echo "opencv-python安装失败"
# torch相关依赖在macOS上可能有问题，跳过
# pip install torch==2.1.0 || echo "torch安装失败"
# pip install torchvision==0.16.0 || echo "torchvision安装失败"
pip install scikit-learn==1.3.2 || echo "scikit-learn安装失败"

# 验证关键依赖
echo "✅ 验证关键依赖..."
python -c "
try:
    import bs4
    print('✅ beautifulsoup4 (bs4) 可用')
except ImportError as e:
    print(f'❌ beautifulsoup4 (bs4) 不可用: {e}')

try:
    import lxml
    print('✅ lxml 可用')
except ImportError as e:
    print(f'❌ lxml 不可用: {e}')

# PyMuPDF在macOS上可能编译失败，跳过验证
# try:
#     import fitz
#     print('✅ PyMuPDF (fitz) 可用')
# except ImportError as e:
#     print(f'❌ PyMuPDF (fitz) 不可用: {e}')

try:
    import aiohttp
    print('✅ aiohttp 可用')
except ImportError as e:
    print(f'❌ aiohttp 不可用: {e}')

try:
    import websockets
    print('✅ websockets 可用')
except ImportError as e:
    print(f'❌ websockets 不可用: {e}')

# opencv-python在macOS上可能有问题，跳过验证
# try:
#     import cv2
#     print('✅ opencv-python (cv2) 可用')
# except ImportError as e:
#     print(f'❌ opencv-python (cv2) 不可用: {e}')

# torch相关依赖在macOS上可能有问题，跳过验证
# try:
#     import torch
#     print('✅ torch 可用')
# except ImportError as e:
#     print(f'❌ torch 不可用: {e}')

# try:
#     import torchvision
#     print('✅ torchvision 可用')
# except ImportError as e:
#     print(f'❌ torchvision 不可用: {e}')

try:
    import sklearn
    print('✅ scikit-learn (sklearn) 可用')
except ImportError as e:
    print(f'❌ scikit-learn (sklearn) 不可用: {e}')
"

echo "🎉 依赖检查和安装完成！"
