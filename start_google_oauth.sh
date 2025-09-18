#!/bin/bash
cd /root/modeshift_django
source venv/bin/activate

# 设置环境变量
export GOOGLE_OAUTH_CLIENT_ID="your_google_client_id_here"
export GOOGLE_OAUTH_CLIENT_SECRET="your_google_client_secret_here"

# 启动Django服务
python manage.py runserver 0.0.0.0:8000
