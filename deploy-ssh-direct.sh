#!/bin/bash

# SSH直接连接部署方法
# 使用方法: ./deploy-ssh-direct.sh

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

# 服务器配置
HOST="47.103.143.152"
USERNAME="root"
DEPLOY_PATH="/root/modeshift_django"

echo "🚀 SSH直接连接部署方法"
echo "======================"
echo ""

# 方法1: 使用SSH密钥连接
deploy_with_ssh_key() {
    log_info "方法1: 使用SSH密钥连接"
    
    # 检查SSH密钥
    if [ ! -f ~/.ssh/id_rsa ]; then
        log_error "SSH密钥不存在，请先生成SSH密钥"
        echo "生成命令: ssh-keygen -t rsa -b 4096 -C 'your_email@example.com'"
        return 1
    fi
    
    # 测试SSH连接
    log_info "测试SSH连接..."
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $USERNAME@$HOST "echo 'SSH连接成功'"; then
        log_success "SSH连接正常"
    else
        log_error "SSH连接失败"
        return 1
    fi
    
    # 执行部署
    log_info "开始部署..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        cd $DEPLOY_PATH &&
        echo '📥 拉取最新代码...' &&
        git pull origin main &&
        echo '🐍 更新虚拟环境...' &&
        venv/bin/python -m pip install -r requirements.txt --quiet &&
        echo '📁 Django操作...' &&
        venv/bin/python manage.py collectstatic --noinput &&
        venv/bin/python manage.py migrate --noinput &&
        echo '🔄 重启服务...' &&
        pkill -TERM -f gunicorn || true &&
        sleep 3 &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
        sudo nginx -s reload &&
        echo '✅ 部署完成'
    "
    
    log_success "SSH密钥部署完成"
}

# 方法2: 使用密码连接
deploy_with_password() {
    log_info "方法2: 使用密码连接"
    
    echo "请输入服务器密码:"
    read -s PASSWORD
    
    # 使用sshpass进行密码连接
    if command -v sshpass > /dev/null; then
        log_info "使用sshpass进行密码连接..."
        sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
            cd $DEPLOY_PATH &&
            echo '📥 拉取最新代码...' &&
            git pull origin main &&
            echo '🔄 重启服务...' &&
            pkill -TERM -f gunicorn || true &&
            sleep 3 &&
            nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
            sudo nginx -s reload &&
            echo '✅ 部署完成'
        "
        log_success "密码连接部署完成"
    else
        log_error "sshpass未安装，请安装: sudo apt-get install sshpass"
        return 1
    fi
}

# 方法3: 使用expect自动输入密码
deploy_with_expect() {
    log_info "方法3: 使用expect自动输入密码"
    
    if ! command -v expect > /dev/null; then
        log_error "expect未安装，请安装: sudo apt-get install expect"
        return 1
    fi
    
    echo "请输入服务器密码:"
    read -s PASSWORD
    
    expect << EOF
spawn ssh -o StrictHostKeyChecking=no $USERNAME@$HOST
expect "password:"
send "$PASSWORD\r"
expect "#"
send "cd $DEPLOY_PATH\r"
expect "#"
send "git pull origin main\r"
expect "#"
send "pkill -TERM -f gunicorn || true\r"
expect "#"
send "sleep 3\r"
expect "#"
send "nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon\r"
expect "#"
send "sudo nginx -s reload\r"
expect "#"
send "exit\r"
expect eof
EOF
    
    log_success "expect自动部署完成"
}

# 主菜单
show_menu() {
    echo "请选择部署方法:"
    echo "1. SSH密钥连接 (推荐)"
    echo "2. 密码连接"
    echo "3. expect自动输入密码"
    echo "4. 退出"
    echo ""
    read -p "请输入选择 (1-4): " choice
    
    case $choice in
        1)
            deploy_with_ssh_key
            ;;
        2)
            deploy_with_password
            ;;
        3)
            deploy_with_expect
            ;;
        4)
            echo "退出"
            exit 0
            ;;
        *)
            log_error "无效选择"
            show_menu
            ;;
    esac
}

# 执行主菜单
show_menu
