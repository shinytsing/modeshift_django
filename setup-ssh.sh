#!/bin/bash

# SSH密钥设置脚本
# 用于生成SSH密钥对并配置到阿里云服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务器配置
SERVER_HOST="47.103.143.152"
SERVER_USER="root"

echo -e "${BLUE}🔑 SSH密钥设置脚本${NC}"
echo -e "${YELLOW}服务器: ${SERVER_HOST}${NC}"
echo -e "${YELLOW}用户: ${SERVER_USER}${NC}"

# 检查是否已有SSH密钥
if [ -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}⚠️ SSH密钥已存在${NC}"
    echo "现有公钥内容："
    cat ~/.ssh/id_rsa.pub
    echo ""
    read -p "是否要生成新的密钥对？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ 使用现有密钥${NC}"
        exit 0
    fi
fi

# 生成SSH密钥对
echo -e "${BLUE}🔑 生成SSH密钥对...${NC}"
ssh-keygen -t rsa -b 4096 -C "modeshift_django@${SERVER_HOST}" -f ~/.ssh/id_rsa -N ""

echo -e "${GREEN}✅ SSH密钥生成完成${NC}"

# 显示公钥
echo -e "${BLUE}📋 公钥内容：${NC}"
echo "----------------------------------------"
cat ~/.ssh/id_rsa.pub
echo "----------------------------------------"

echo -e "${YELLOW}📝 请将上面的公钥添加到服务器的 ~/.ssh/authorized_keys 文件中${NC}"
echo ""
echo "你可以通过以下方式添加："
echo "1. 登录服务器：ssh ${SERVER_USER}@${SERVER_HOST}"
echo "2. 创建.ssh目录：mkdir -p ~/.ssh"
echo "3. 添加公钥：echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys"
echo "4. 设置权限：chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
echo ""

# 测试连接
read -p "是否要测试SSH连接？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🔗 测试SSH连接...${NC}"
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST} "echo 'SSH连接成功'"; then
        echo -e "${GREEN}✅ SSH连接成功！${NC}"
    else
        echo -e "${RED}❌ SSH连接失败${NC}"
        echo "请检查："
        echo "1. 公钥是否正确添加到服务器"
        echo "2. 服务器SSH服务是否运行"
        echo "3. 防火墙是否开放22端口"
    fi
fi

echo -e "${GREEN}🎉 SSH设置完成！${NC}"
echo -e "${BLUE}现在可以使用 ./deploy-aliyun.sh 进行部署${NC}"
