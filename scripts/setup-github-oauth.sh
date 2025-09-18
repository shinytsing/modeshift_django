#!/bin/bash

# 设置GitHub OAuth作为Google OAuth的替代方案

echo "🐙 设置GitHub OAuth替代方案..."

# 1. 在服务器上配置GitHub SocialApp
ssh root@47.103.143.152 "cd /root/modeshift_django && source venv/bin/activate && python manage.py shell << 'PYTHON_EOF'
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

print('=== 配置GitHub OAuth ===')

# 获取站点
site = Site.objects.get(id=1)

# 创建GitHub SocialApp
github_app, created = SocialApp.objects.get_or_create(
    provider='github',
    defaults={
        'name': 'GitHub',
        'client_id': 'your-github-client-id',
        'secret': 'your-github-client-secret'
    }
)

if created:
    print('创建新的GitHub SocialApp')
else:
    print('更新现有GitHub SocialApp')

# 添加站点
github_app.sites.add(site)
github_app.save()

print(f'GitHub SocialApp配置完成:')
print(f'- Provider: {github_app.provider}')
print(f'- Name: {github_app.name}')
print(f'- Sites: {[s.domain for s in github_app.sites.all()]}')

PYTHON_EOF"

echo "✅ GitHub OAuth配置完成"
echo "💡 需要在GitHub上创建OAuth应用："
echo "   1. 访问 https://github.com/settings/applications/new"
echo "   2. 设置回调URL: https://shenyiqing.xin/accounts/github/login/callback/"
echo "   3. 获取Client ID和Secret"
echo "   4. 更新服务器上的配置"
