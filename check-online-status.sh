#!/bin/bash

# 🔍 检查线上环境状态脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 线上服务器配置
HOST="47.103.143.152"
USERNAME="root"

log_info "检查线上环境状态..."

# 检查服务器连接
log_info "检查服务器连接..."
if ping -c 1 $HOST > /dev/null 2>&1; then
    log_success "服务器连接正常"
else
    log_error "服务器连接失败"
    exit 1
fi

# 检查SSH连接
log_info "检查SSH连接..."
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $USERNAME@$HOST "echo 'SSH连接成功'" > /dev/null 2>&1; then
    log_success "SSH连接正常"
else
    log_error "SSH连接失败"
    exit 1
fi

# 检查线上服务状态
log_info "检查线上服务状态..."
ssh -o StrictHostKeyChecking=no $USERNAME@$HOST << 'EOF'
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 进入项目目录
cd /root/modeshift_django

log_info "项目目录: $(pwd)"

# 检查项目文件
if [ -f "manage.py" ]; then
    log_success "项目文件存在"
else
    log_error "项目文件不存在"
    exit 1
fi

# 检查虚拟环境
if [ -d "venv" ]; then
    log_success "虚拟环境存在"
else
    log_warning "虚拟环境不存在"
fi

# 检查服务进程
log_info "检查服务进程..."
if pgrep -f "python.*manage.py.*runserver" > /dev/null; then
    log_success "Django服务正在运行"
    pgrep -f "python.*manage.py.*runserver" | head -1 | xargs ps -p
else
    log_warning "Django服务未运行"
fi

# 检查端口占用
log_info "检查端口占用..."
if netstat -tlnp | grep :8000 > /dev/null; then
    log_success "端口8000正在使用"
    netstat -tlnp | grep :8000
else
    log_warning "端口8000未被占用"
fi

# 检查数据库
log_info "检查数据库..."
if [ -f "db.sqlite3" ]; then
    log_success "SQLite数据库存在"
    ls -la db.sqlite3
else
    log_warning "SQLite数据库不存在"
fi

# 检查日志文件
log_info "检查日志文件..."
if [ -f "server.log" ]; then
    log_success "服务器日志存在"
    echo "最近10行日志:"
    tail -10 server.log
else
    log_warning "服务器日志不存在"
fi

log_info "线上环境检查完成"

EOF

log_success "线上环境状态检查完成！"
