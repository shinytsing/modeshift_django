#!/bin/bash

echo "=== 停止Django服务 ==="
pkill -f 'python.*manage.py'
pkill -f gunicorn
sleep 3

echo "=== 启动Django服务 ==="
cd /root/modeshift_django
source venv/bin/activate

# 启动开发服务器
nohup python manage.py runserver 0.0.0.0:8001 --settings=config.settings.production > django.log 2>&1 &

# 启动Gunicorn
nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --max-requests 1000 --max-requests-jitter 100 --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log wsgi:application > gunicorn.log 2>&1 &

sleep 5

echo "=== 检查服务状态 ==="
ps aux | grep -E '(gunicorn|python.*manage.py)' | grep -v grep
netstat -tlnp | grep :8000

echo "=== 服务重启完成 ==="
