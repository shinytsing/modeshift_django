#!/bin/bash

# 设置代理环境变量
export USE_PROXY=true
export PROXY_URL=socks5://127.0.0.1:1080

# 启动Django服务
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
