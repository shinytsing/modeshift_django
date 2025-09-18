#!/bin/bash

# 修复登录重定向问题的脚本
# 解决未登录用户访问首页时自动跳转到登录页面的问题

echo "🔧 开始修复登录重定向问题..."

# 1. 清理静态文件缓存
echo "📁 清理静态文件缓存..."
ssh root@47.103.143.152 "cd /root/modeshift_django && rm -rf staticfiles/* && python manage.py collectstatic --noinput"

# 2. 重启服务以清除内存缓存
echo "🔄 重启服务..."
ssh root@47.103.143.152 "cd /root/modeshift_django && pkill -f gunicorn && sleep 2 && nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --preload --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log config.wsgi:application > /dev/null 2>&1 &"

# 3. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 4. 验证服务状态
echo "✅ 验证服务状态..."
ssh root@47.103.143.152 "cd /root/modeshift_django && curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/"

# 5. 测试外部访问
echo "🌐 测试外部访问..."
curl -s -o /dev/null -w '%{http_code}' https://shenyiqing.xin/

echo "🎉 修复完成！"
echo "💡 建议：清除浏览器缓存后重新访问网站"
