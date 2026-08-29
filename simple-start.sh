#!/bin/bash

# 🚀 简单的Gunicorn启动脚本
# 避免复杂的逻辑，直接启动

set -e

DEPLOY_PATH="/root/modeshift_django"

echo "🚀 启动Gunicorn服务..."

# 进入项目目录
cd "$DEPLOY_PATH"

# 激活虚拟环境
source venv/bin/activate

# 停止现有进程
pkill -TERM -f gunicorn || true
sleep 2

# 启动Gunicorn
nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application > /dev/null 2>&1 &

# 等待启动
sleep 3

# 检查进程
if ps aux | grep gunicorn | grep -v grep > /dev/null; then
    echo "✅ Gunicorn启动成功"
else
    echo "❌ Gunicorn启动失败"
    exit 1
fi

echo "✅ 启动完成"
