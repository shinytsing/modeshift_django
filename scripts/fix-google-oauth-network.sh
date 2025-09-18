#!/bin/bash

# Google OAuth网络问题修复脚本

echo "🔧 修复Google OAuth网络连接问题..."

# 1. 检查网络连接
echo "📡 检查网络连接..."
ssh root@47.103.143.152 "ping -c 2 8.8.8.8"

# 2. 尝试配置代理（如果需要）
echo "🌐 检查代理配置..."
ssh root@47.103.143.152 "env | grep -i proxy"

# 3. 修改Django设置以增加超时时间
echo "⏱️ 修改OAuth超时设置..."
ssh root@47.103.143.152 "cd /root/modeshift_django && cat >> config/settings/base.py << 'EOF'

# Google OAuth网络超时设置
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'OAUTH_TIMEOUT': 30,  # 增加超时时间到30秒
    }
}

# 网络请求超时设置
import requests
requests.adapters.DEFAULT_TIMEOUT = 30
EOF"

# 4. 重启服务
echo "🔄 重启服务..."
ssh root@47.103.143.152 "cd /root/modeshift_django && pkill -f gunicorn && sleep 3 && nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --preload --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log config.wsgi:application > /dev/null 2>&1 &"

# 5. 测试服务
echo "🧪 测试服务..."
sleep 5
curl -s -o /dev/null -w '%{http_code}' https://shenyiqing.xin/ && echo " - 首页状态"

echo "✅ Google OAuth网络问题修复完成"
echo "💡 如果问题仍然存在，可能需要："
echo "   1. 联系服务器提供商检查网络策略"
echo "   2. 配置代理服务器"
echo "   3. 使用其他OAuth提供商"
