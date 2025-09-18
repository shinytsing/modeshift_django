#!/bin/bash

# OAuth调试测试脚本

echo "🔍 开始OAuth调试测试..."

# 1. 检查网络连接
echo "📡 测试网络连接..."
ssh root@47.103.143.152 "curl -s -o /dev/null -w '%{http_code}' https://accounts.google.com/"

# 2. 检查OAuth配置
echo "⚙️ 检查OAuth配置..."
ssh root@47.103.143.152 "cd /root/modeshift_django && source venv/bin/activate && python manage.py shell << 'PYTHON_EOF'
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os

print('=== OAuth配置检查 ===')
google_app = SocialApp.objects.filter(provider='google').first()
if google_app:
    print(f'Client ID: {google_app.client_id}')
    print(f'Secret: {google_app.secret[:20]}...')
    print(f'Sites: {[s.domain for s in google_app.sites.all()]}')
else:
    print('未找到Google SocialApp')

print(f'环境变量 CLIENT_ID: {os.getenv(\"GOOGLE_OAUTH_CLIENT_ID\", \"未设置\")}')
print(f'环境变量 SECRET: {os.getenv(\"GOOGLE_OAUTH_CLIENT_SECRET\", \"未设置\")}')
PYTHON_EOF"

# 3. 测试OAuth启动
echo "🚀 测试OAuth启动..."
curl -I https://shenyiqing.xin/accounts/google/login/ | head -1

# 4. 检查服务状态
echo "📊 检查服务状态..."
ssh root@47.103.143.152 "ps aux | grep gunicorn | grep -v grep"

echo "✅ OAuth调试测试完成"
