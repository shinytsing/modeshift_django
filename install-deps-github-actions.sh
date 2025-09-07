#!/bin/bash

# GitHub Actions专用依赖安装脚本
# 跳过在GitHub Actions环境中有问题的依赖

set -e

echo "🔧 GitHub Actions依赖安装开始..."

# 升级pip
python -m pip install --upgrade pip

# 安装基础依赖
echo "📦 安装基础依赖..."
pip install Django==5.0.1
pip install psycopg[binary]>=3.1.0
pip install redis==5.0.1
pip install celery==5.3.4
pip install channels==4.0.0
pip install channels-redis==4.1.0
pip install django-redis==5.4.0
pip install Pillow==10.1.0
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
pip install aiohttp==3.9.1
pip install websockets==12.0

# 安装测试依赖
echo "🧪 安装测试依赖..."
pip install pytest==7.4.3
pip install pytest-django==4.7.0
pip install pytest-cov==4.1.0
pip install pytest-xdist==3.3.1
pip install pytest-html==4.1.1
pip install coverage==7.3.2

# 安装代码质量工具
echo "🔍 安装代码质量工具..."
pip install black==23.11.0
pip install isort==5.12.0
pip install flake8==6.1.0
pip install mypy==1.7.1

# 安装安全扫描工具
echo "🔒 安装安全扫描工具..."
pip install bandit==1.7.5
pip install safety==2.3.5

# 尝试安装PyMuPDF（如果失败则跳过）
echo "📄 尝试安装PyMuPDF..."
pip install PyMuPDF==1.23.8 || echo "⚠️ PyMuPDF安装失败，跳过（不影响核心功能）"

# 验证关键依赖
echo "✅ 验证关键依赖..."
python -c "
import sys
success = True

try:
    import bs4
    print('✅ beautifulsoup4 (bs4) 可用')
except ImportError as e:
    print(f'❌ beautifulsoup4 (bs4) 不可用: {e}')
    success = False

try:
    import aiohttp
    print('✅ aiohttp 可用')
except ImportError as e:
    print(f'❌ aiohttp 不可用: {e}')
    success = False

try:
    import websockets
    print('✅ websockets 可用')
except ImportError as e:
    print(f'❌ websockets 不可用: {e}')
    success = False

try:
    import pytest
    print('✅ pytest 可用')
except ImportError as e:
    print(f'❌ pytest 不可用: {e}')
    success = False

if not success:
    print('❌ 关键依赖验证失败')
    sys.exit(1)
else:
    print('✅ 所有关键依赖验证成功')
"

echo "🎉 GitHub Actions依赖安装完成！"
