#!/bin/bash

# 阿里云服务器部署脚本
# 服务器: 47.103.143.152
# 用户: root
# 域名: shenyinqing.xin

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务器配置
SERVER_HOST="47.103.143.152"
SERVER_USER="root"
SERVER_PORT="22"
DOMAIN="shenyinqing.xin"
DEPLOY_PATH="/root/modeshift_django"

echo -e "${BLUE}🚀 开始部署到阿里云服务器...${NC}"
echo -e "${YELLOW}服务器: ${SERVER_HOST}${NC}"
echo -e "${YELLOW}用户: ${SERVER_USER}${NC}"
echo -e "${YELLOW}域名: ${DOMAIN}${NC}"
echo -e "${YELLOW}部署路径: ${DEPLOY_PATH}${NC}"

# 检查SSH密钥是否存在
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${RED}❌ SSH密钥不存在，请先生成SSH密钥对${NC}"
    echo "运行以下命令生成密钥："
    echo "ssh-keygen -t rsa -b 4096 -C 'your_email@example.com'"
    exit 1
fi

echo -e "${GREEN}✅ SSH密钥检查通过${NC}"

# 添加服务器到known_hosts
echo -e "${BLUE}🔑 添加服务器到known_hosts...${NC}"
ssh-keyscan -H ${SERVER_HOST} >> ~/.ssh/known_hosts

# 测试SSH连接
echo -e "${BLUE}🔗 测试SSH连接...${NC}"
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "echo 'SSH连接成功'"; then
    echo -e "${GREEN}✅ SSH连接成功${NC}"
else
    echo -e "${RED}❌ SSH连接失败${NC}"
    echo "请检查："
    echo "1. 服务器是否运行"
    echo "2. SSH服务是否启动"
    echo "3. 防火墙是否开放22端口"
    echo "4. SSH密钥是否正确"
    exit 1
fi

# 部署到服务器
echo -e "${BLUE}📦 开始部署...${NC}"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "
    echo '📥 拉取最新代码...'
    cd ${DEPLOY_PATH}
    git pull origin main
    
    echo '🐍 激活虚拟环境...'
    source venv/bin/activate
    
    echo '📦 安装依赖...'
    pip install -r requirements.txt
    
    echo '📁 收集静态文件...'
    python manage.py collectstatic --noinput
    
    echo '🗄️ 运行数据库迁移...'
    python manage.py migrate
    
    echo '🔄 重启服务...'
    sudo systemctl restart gunicorn
    sudo systemctl restart nginx
    
    echo '✅ 部署完成'
"

echo -e "${GREEN}🎉 部署成功完成！${NC}"

# 等待服务启动
echo -e "${BLUE}⏳ 等待服务启动...${NC}"
sleep 10

# 测试网站访问
echo -e "${BLUE}🌐 测试网站访问...${NC}"

# 测试首页
if curl -f -s --max-time 10 "https://${DOMAIN}/" > /dev/null; then
    echo -e "${GREEN}✅ 首页访问正常${NC}"
else
    echo -e "${YELLOW}⚠️ 首页访问失败，可能还在启动中${NC}"
fi

# 测试健康检查
if curl -f -s --max-time 10 "https://${DOMAIN}/health/" > /dev/null; then
    echo -e "${GREEN}✅ 健康检查正常${NC}"
else
    echo -e "${YELLOW}⚠️ 健康检查失败${NC}"
fi

# 测试API
if curl -f -s --max-time 10 "https://${DOMAIN}/api/" > /dev/null; then
    echo -e "${GREEN}✅ API访问正常${NC}"
else
    echo -e "${YELLOW}⚠️ API访问失败${NC}"
fi

echo -e "${GREEN}🎉 部署和测试完成！${NC}"
echo -e "${BLUE}网站地址: https://${DOMAIN}${NC}"
echo -e "${BLUE}管理后台: https://${DOMAIN}/admin/${NC}"
echo -e "${BLUE}健康检查: https://${DOMAIN}/health/${NC}"