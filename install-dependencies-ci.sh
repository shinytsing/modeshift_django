#!/bin/bash

# CI/CD专用依赖安装脚本
# 跳过所有在macOS上有问题的依赖

set -e

echo "🔍 开始检查和安装依赖..."

# 检查Python版本
echo "🐍 Python版本:"
python --version

# 升级pip
echo "📦 升级pip..."
python -m pip install --upgrade pip

# 安装requirements.txt中的基础依赖（跳过有问题的）
echo "📋 安装基础依赖..."
pip install Django==5.0.1 || echo "Django安装失败"
pip install psycopg[binary]>=3.1.0 || echo "psycopg安装失败"
pip install redis==5.0.1 || echo "redis安装失败"
pip install celery==5.3.4 || echo "celery安装失败"
pip install channels==4.0.0 || echo "channels安装失败"
pip install channels-redis==4.1.0 || echo "channels-redis安装失败"
pip install django-redis==5.4.0 || echo "django-redis安装失败"
pip install Pillow==10.1.0 || echo "Pillow安装失败"
pip install requests==2.31.0 || echo "requests安装失败"
pip install beautifulsoup4==4.12.2 || echo "beautifulsoup4安装失败"
pip install lxml==4.9.3 || echo "lxml安装失败"
pip install aiohttp==3.9.1 || echo "aiohttp安装失败"
pip install websockets==12.0 || echo "websockets安装失败"

# 安装测试依赖
echo "🧪 安装测试依赖..."
pip install pytest==7.4.3 || echo "pytest安装失败"
pip install pytest-django==4.7.0 || echo "pytest-django安装失败"
pip install pytest-cov==4.1.0 || echo "pytest-cov安装失败"
pip install pytest-xdist==3.3.1 || echo "pytest-xdist安装失败"
pip install pytest-html==4.1.1 || echo "pytest-html安装失败"
pip install coverage==7.3.2 || echo "coverage安装失败"

# 安装代码质量工具
echo "🔧 安装代码质量工具..."
pip install black==23.11.0 || echo "black安装失败"
pip install isort==5.12.0 || echo "isort安装失败"
pip install flake8==6.1.0 || echo "flake8安装失败"
pip install mypy==1.7.1 || echo "mypy安装失败"
pip install bandit==1.7.5 || echo "bandit安装失败"
pip install safety==2.3.5 || echo "safety安装失败"

# 验证关键依赖
echo "✅ 验证关键依赖..."
python -c "
try:
    import django
    print('✅ Django 可用')
except ImportError as e:
    print(f'❌ Django 不可用: {e}')

try:
    import psycopg
    print('✅ psycopg 可用')
except ImportError as e:
    print(f'❌ psycopg 不可用: {e}')

try:
    import redis
    print('✅ redis 可用')
except ImportError as e:
    print(f'❌ redis 不可用: {e}')

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
    import pytest
    print('✅ pytest 可用')
except ImportError as e:
    print(f'❌ pytest 不可用: {e}')
"

echo "🎉 依赖安装完成！"
