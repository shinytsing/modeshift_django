#!/bin/bash

# QAToolBox 生产环境部署脚本
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin

set -e

echo "🚀 开始部署 QAToolBox 到生产环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务器信息
SERVER="47.103.143.152"
USER="root"
DOMAIN="shenyiqing.xin"

echo -e "${GREEN}📋 部署信息:${NC}"
echo "服务器: $SERVER"
echo "域名: $DOMAIN"
echo "用户: $USER"
echo ""

# 检查本地Git状态
echo -e "${YELLOW}🔍 检查本地Git状态...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ 有未提交的更改，请先提交代码${NC}"
    exit 1
fi

# 推送到GitHub
echo -e "${YELLOW}📤 推送代码到GitHub...${NC}"
git add .
git commit -m "更新Docker部署配置和依赖 - $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo -e "${GREEN}✅ 代码已推送到GitHub${NC}"

# 连接到服务器并部署
echo -e "${YELLOW}🔗 连接到服务器并开始部署...${NC}"

ssh -o StrictHostKeyChecking=no $USER@$SERVER << 'EOF'
set -e

echo "🚀 在服务器上开始部署..."

# 创建项目目录
PROJECT_DIR="/opt/qatoolbox"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 停止现有服务
echo "⏹️ 停止现有服务..."
docker-compose down || true

# 拉取最新代码
echo "📥 拉取最新代码..."
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/your-username/modeshift_django.git .
fi

# 设置环境变量
echo "🔧 设置环境变量..."
if [ ! -f ".env" ]; then
    cp env.production .env
    echo "✅ 已创建 .env 文件"
fi

# 构建和启动服务
echo "🔨 构建Docker镜像..."
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查健康状态
echo "🏥 检查健康状态..."
for i in {1..10}; do
    if curl -f http://localhost/health/ > /dev/null 2>&1; then
        echo "✅ 服务健康检查通过"
        break
    else
        echo "⏳ 等待服务启动... ($i/10)"
        sleep 10
    fi
done

# 显示服务信息
echo "📊 服务信息:"
echo "Web服务: http://47.103.143.152"
echo "域名: https://shenyiqing.xin"
echo ""

# 显示容器状态
echo "🐳 容器状态:"
docker-compose ps

echo "✅ 部署完成！"
EOF

echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}🌐 访问地址: https://shenyiqing.xin${NC}"
echo -e "${GREEN}🔧 管理地址: http://47.103.143.152/admin${NC}"
