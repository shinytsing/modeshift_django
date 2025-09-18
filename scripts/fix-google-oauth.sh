#!/bin/bash

# 修复Google OAuth配置问题的脚本
# 解决SocialApp.DoesNotExist错误

echo "🔧 开始修复Google OAuth配置问题..."

# 1. 进入服务器
ssh root@47.103.143.152 << 'EOF'
cd /root/modeshift_django
source venv/bin/activate

echo "📋 检查当前SocialApp配置..."
python manage.py shell << 'PYTHON_EOF'
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# 检查现有的SocialApp
apps = SocialApp.objects.all()
print(f"现有SocialApp数量: {apps.count()}")
for app in apps:
    print(f"- {app.provider}: {app.name}")

# 检查站点配置
sites = Site.objects.all()
print(f"现有站点数量: {sites.count()}")
for site in sites:
    print(f"- {site.id}: {site.domain}")

PYTHON_EOF

echo "🔧 创建Google OAuth SocialApp..."
python manage.py shell << 'PYTHON_EOF'
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os

# 获取或创建站点
site, created = Site.objects.get_or_create(
    id=1,
    defaults={
        'domain': 'shenyiqing.xin',
        'name': 'ModeShift'
    }
)
if created:
    print(f"创建新站点: {site.domain}")
else:
    print(f"使用现有站点: {site.domain}")

# 获取环境变量
client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID', 'your_google_client_id_here')
client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', 'your_google_client_secret_here')

# 检查是否已存在Google SocialApp
google_app = SocialApp.objects.filter(provider='google').first()

if google_app:
    print(f"更新现有Google SocialApp: {google_app.name}")
    google_app.client_id = client_id
    google_app.secret = client_secret
    google_app.save()
else:
    print("创建新的Google SocialApp")
    google_app = SocialApp.objects.create(
        provider='google',
        name='Google',
        client_id=client_id,
        secret=client_secret
    )

# 添加站点到SocialApp
google_app.sites.add(site)
google_app.save()

print(f"Google SocialApp配置完成:")
print(f"- Provider: {google_app.provider}")
print(f"- Name: {google_app.name}")
print(f"- Client ID: {google_app.client_id[:20]}...")
print(f"- Sites: {[s.domain for s in google_app.sites.all()]}")

PYTHON_EOF

echo "✅ Google OAuth配置完成！"
EOF

echo "🎉 修复完成！"
echo "💡 注意：如果仍然出现500错误，请检查环境变量中的Google OAuth配置是否正确"
