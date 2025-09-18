#!/bin/bash

# 🔍 服务器状态检查脚本
# 检查 47.103.143.152 服务器上的服务状态

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
DOMAIN="shenyiqing.xin"

echo -e "${BLUE}🔍 检查服务器状态...${NC}"
echo "服务器: $SERVER"
echo "域名: $DOMAIN"
echo ""

# 检查sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}❌ 需要安装sshpass${NC}"
    echo "请运行: brew install sshpass"
    exit 1
fi

# 连接到服务器检查状态
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER << 'EOF'
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 检查服务器服务状态..."
echo ""

# 检查系统服务
echo -e "${BLUE}📊 系统服务状态:${NC}"
echo "PostgreSQL:"
systemctl is-active postgresql && echo -e "${GREEN}✅ PostgreSQL 运行中${NC}" || echo -e "${RED}❌ PostgreSQL 未运行${NC}"

echo "Redis:"
systemctl is-active redis-server && echo -e "${GREEN}✅ Redis 运行中${NC}" || echo -e "${RED}❌ Redis 未运行${NC}"

echo "Nginx:"
systemctl is-active nginx && echo -e "${GREEN}✅ Nginx 运行中${NC}" || echo -e "${RED}❌ Nginx 未运行${NC}"

echo ""

# 检查端口
echo -e "${BLUE}🔌 端口状态:${NC}"
netstat -tlnp | grep ":8000 " && echo -e "${GREEN}✅ 端口8000 (Django) 监听中${NC}" || echo -e "${RED}❌ 端口8000 未监听${NC}"
netstat -tlnp | grep ":5432 " && echo -e "${GREEN}✅ 端口5432 (PostgreSQL) 监听中${NC}" || echo -e "${RED}❌ 端口5432 未监听${NC}"
netstat -tlnp | grep ":6379 " && echo -e "${GREEN}✅ 端口6379 (Redis) 监听中${NC}" || echo -e "${RED}❌ 端口6379 未监听${NC}"
netstat -tlnp | grep ":80 " && echo -e "${GREEN}✅ 端口80 (Nginx) 监听中${NC}" || echo -e "${RED}❌ 端口80 未监听${NC}"

echo ""

# 检查进程
echo -e "${BLUE}🔄 进程状态:${NC}"
if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
    echo -e "${GREEN}✅ Gunicorn 进程运行中${NC}"
    echo "进程信息:"
    ps aux | grep "gunicorn.*wsgi:application" | grep -v grep
else
    echo -e "${RED}❌ Gunicorn 进程未运行${NC}"
fi

echo ""

# 检查虚拟环境
echo -e "${BLUE}🐍 Python环境:${NC}"
PROJECT_DIR="/root/modeshift_django"
VENV_DIR="$PROJECT_DIR/venv"

if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}✅ 虚拟环境存在${NC}"
    echo "虚拟环境路径: $VENV_DIR"
    
    # 检查虚拟环境中的包
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        echo "Python版本: $(python --version)"
        echo "Django版本: $(python -c 'import django; print(django.get_version())')"
    fi
else
    echo -e "${RED}❌ 虚拟环境不存在${NC}"
fi

echo ""

# 检查项目文件
echo -e "${BLUE}📁 项目文件:${NC}"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${GREEN}✅ 项目目录存在${NC}"
    echo "项目路径: $PROJECT_DIR"
    
    if [ -f "$PROJECT_DIR/.env" ]; then
        echo -e "${GREEN}✅ 环境配置文件存在${NC}"
    else
        echo -e "${RED}❌ 环境配置文件不存在${NC}"
    fi
    
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        echo -e "${GREEN}✅ 依赖文件存在${NC}"
    else
        echo -e "${RED}❌ 依赖文件不存在${NC}"
    fi
else
    echo -e "${RED}❌ 项目目录不存在${NC}"
fi

echo ""

# 健康检查
echo -e "${BLUE}🏥 健康检查:${NC}"
endpoints=(
    "http://localhost:8000/"
    "http://localhost:8000/health/"
    "http://localhost:8000/admin/"
)

for endpoint in "${endpoints[@]}"; do
    if curl -f -s --connect-timeout 5 --max-time 10 "$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $endpoint 正常${NC}"
    else
        echo -e "${RED}❌ $endpoint 异常${NC}"
    fi
done

echo ""

# 检查日志
echo -e "${BLUE}📝 日志文件:${NC}"
if [ -f "/var/log/gunicorn_access.log" ]; then
    echo -e "${GREEN}✅ Gunicorn访问日志存在${NC}"
    echo "最近访问:"
    tail -n 3 /var/log/gunicorn_access.log
else
    echo -e "${RED}❌ Gunicorn访问日志不存在${NC}"
fi

if [ -f "/var/log/gunicorn_error.log" ]; then
    echo -e "${GREEN}✅ Gunicorn错误日志存在${NC}"
    echo "最近错误:"
    tail -n 3 /var/log/gunicorn_error.log
else
    echo -e "${RED}❌ Gunicorn错误日志不存在${NC}"
fi

echo ""

# 磁盘空间
echo -e "${BLUE}💾 磁盘空间:${NC}"
df -h / | tail -n 1

echo ""

# 内存使用
echo -e "${BLUE}🧠 内存使用:${NC}"
free -h

echo ""
echo -e "${GREEN}🎉 状态检查完成！${NC}"
echo ""
echo "🌐 访问地址:"
echo "  - 服务器直连: http://47.103.143.152:8000"
echo "  - 域名访问: https://shenyiqing.xin"
echo "  - 管理后台: https://shenyiqing.xin/admin/"
echo "  - 健康检查: https://shenyiqing.xin/health/"
echo ""
echo "👤 管理员账号: admin/admin123"

EOF

echo ""
echo -e "${GREEN}✅ 状态检查完成！${NC}"
