#!/bin/bash

# 🔗 测试服务器连接脚本
# 测试到 47.103.143.152 的连接

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
SERVER="47.103.143.152"
USER="root"
PASSWORD="GJc9d5&b5z"

echo -e "${BLUE}🔗 测试服务器连接...${NC}"
echo "服务器: $SERVER"
echo "用户: $USER"
echo ""

# 检查sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}❌ sshpass未安装${NC}"
    echo "请运行: brew install sshpass"
    exit 1
fi

echo -e "${YELLOW}⏳ 正在连接服务器...${NC}"

# 测试SSH连接
if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $USER@$SERVER "echo 'SSH连接成功'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH连接成功${NC}"
else
    echo -e "${RED}❌ SSH连接失败${NC}"
    echo "请检查："
    echo "1. 服务器IP地址是否正确"
    echo "2. 用户名和密码是否正确"
    echo "3. 服务器是否正在运行"
    echo "4. 网络连接是否正常"
    exit 1
fi

echo ""

# 检查服务器基本信息
echo -e "${BLUE}📊 服务器基本信息:${NC}"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER << 'EOF'
echo "操作系统: $(uname -a)"
echo "Python版本: $(python3 --version)"
echo "磁盘空间:"
df -h /
echo ""
echo "内存使用:"
free -h
echo ""
echo "网络接口:"
ip addr show | grep "inet " | head -3
EOF

echo ""
echo -e "${GREEN}🎉 服务器连接测试完成！${NC}"
echo "现在可以执行部署脚本了："
echo "  ./deploy-now.sh"
