#!/bin/bash

# 最简化的依赖安装脚本
# 跳过所有在macOS上有问题的依赖

set -e

echo "🔍 开始检查和安装依赖..."

# 检查Python版本
echo "🐍 Python版本:"
python --version

# 升级pip
echo "📦 升级pip..."
python -m pip install --upgrade pip

# 安装requirements.txt中的所有依赖，但跳过有问题的
echo "📋 安装requirements.txt中的依赖..."
pip install -r requirements.txt --no-deps || echo "requirements.txt安装失败，继续..."

# 手动安装关键依赖（跳过有问题的）
echo "🔧 安装关键依赖..."
pip install beautifulsoup4==4.12.2 || echo "beautifulsoup4安装失败"
pip install lxml==4.9.3 || echo "lxml安装失败"
pip install aiohttp==3.9.1 || echo "aiohttp安装失败"
pip install websockets==12.0 || echo "websockets安装失败"
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

try:
    import sklearn
    print('✅ scikit-learn 可用')
except ImportError as e:
    print(f'❌ scikit-learn 不可用: {e}')
"

echo "🎉 依赖安装完成！"
