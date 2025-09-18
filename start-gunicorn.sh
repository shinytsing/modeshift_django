#!/bin/bash

# 🚀 稳定的Gunicorn启动脚本
# 解决启动失败问题

set -e

DEPLOY_PATH="/root/modeshift_django"
PID_FILE="/tmp/gunicorn.pid"
LOG_FILE="/tmp/gunicorn.log"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if netstat -tlnp | grep ":$port " > /dev/null; then
        warning "端口 $port 已被占用"
        return 1
    else
        log "端口 $port 可用"
        return 0
    fi
}

# 停止现有Gunicorn进程
stop_gunicorn() {
    log "停止现有Gunicorn进程..."
    
    # 停止systemd服务
    if systemctl is-active --quiet gunicorn-modeshift 2>/dev/null; then
        log "停止systemd服务..."
        systemctl stop gunicorn-modeshift || true
        sleep 2
    fi
    
    # 尝试优雅停止
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "停止进程 $pid"
            kill -TERM "$pid" || true
            sleep 3
        fi
    fi
    
    # 强制停止所有gunicorn进程
    pkill -TERM -f gunicorn || true
    sleep 2
    
    # 如果还有进程，强制杀死
    if pgrep -f gunicorn > /dev/null; then
        warning "强制停止Gunicorn进程"
        pkill -9 -f gunicorn || true
        sleep 1
    fi
    
    # 清理PID文件
    rm -f "$PID_FILE"
    
    success "Gunicorn进程已停止"
}

# 启动Gunicorn
start_gunicorn() {
    log "启动Gunicorn服务..."
    
    # 检查端口
    if ! check_port 8000; then
        error "端口8000被占用，无法启动"
        return 1
    fi
    
    # 进入项目目录
    cd "$DEPLOY_PATH" || {
        error "无法进入项目目录: $DEPLOY_PATH"
        return 1
    }
    
    # 激活虚拟环境
    if [ ! -f "venv/bin/activate" ]; then
        error "虚拟环境不存在: venv/bin/activate"
        return 1
    fi
    
    source venv/bin/activate || {
        error "无法激活虚拟环境"
        return 1
    }
    
    # 加载环境变量
    if [ -f ".env" ]; then
        log "加载环境变量..."
        export $(grep -v '^#' .env | xargs)
        success "环境变量加载完成"
    else
        warning "未找到.env文件"
    fi
    
    # 检查WSGI模块
    python -c "import wsgi" || {
        error "WSGI模块加载失败"
        return 1
    }
    
    # 启动Gunicorn
    log "启动Gunicorn进程..."
    
    # 使用systemd服务方式启动
    if command -v systemctl > /dev/null 2>&1; then
        # 创建systemd服务文件
        cat > /etc/systemd/system/gunicorn-modeshift.service << EOF
[Unit]
Description=Gunicorn instance to serve modeshift_django
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=$DEPLOY_PATH
Environment="PATH=$DEPLOY_PATH/venv/bin"
ExecStart=$DEPLOY_PATH/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
        
        # 重新加载systemd配置
        systemctl daemon-reload
        
        # 启动服务
        systemctl start gunicorn-modeshift
        systemctl enable gunicorn-modeshift
        
        # 等待启动
        sleep 3
        
        # 检查服务状态
        if systemctl is-active --quiet gunicorn-modeshift; then
            success "Gunicorn systemd服务启动成功"
            return 0
        else
            error "Gunicorn systemd服务启动失败"
            systemctl status gunicorn-modeshift
            return 1
        fi
    else
        # 回退到nohup方式
        nohup gunicorn \
            --bind 0.0.0.0:8000 \
            --workers 3 \
            --timeout 120 \
            --pid "$PID_FILE" \
            --access-logfile "$LOG_FILE" \
            --error-logfile "$LOG_FILE" \
            --log-level info \
            wsgi:application > /dev/null 2>&1 &
    fi
    
    # 等待启动
    sleep 5
    
    # 检查是否启动成功
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            success "Gunicorn启动成功 (PID: $pid)"
            return 0
        else
            error "Gunicorn启动失败"
            return 1
        fi
    else
        error "PID文件未创建，启动失败"
        return 1
    fi
}

# 检查服务状态
check_status() {
    log "检查服务状态..."
    
    # 检查systemd服务状态
    if systemctl is-active --quiet gunicorn-modeshift 2>/dev/null; then
        success "Gunicorn systemd服务正在运行"
        
        # 检查端口监听
        if netstat -tlnp | grep ":8000 " > /dev/null; then
            success "端口8000监听正常"
        else
            warning "端口8000监听异常"
        fi
        
        return 0
    fi
    
    # 回退到PID文件检查
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            success "Gunicorn正在运行 (PID: $pid)"
            
            # 检查端口监听
            if netstat -tlnp | grep ":$pid " | grep 8000 > /dev/null; then
                success "端口8000监听正常"
            else
                warning "端口8000监听异常"
            fi
            
            return 0
        else
            error "Gunicorn进程不存在"
            return 1
        fi
    else
        error "PID文件不存在"
        return 1
    fi
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            log "启动Gunicorn服务..."
            stop_gunicorn
            start_gunicorn
            check_status
            ;;
        stop)
            log "停止Gunicorn服务..."
            stop_gunicorn
            ;;
        restart)
            log "重启Gunicorn服务..."
            stop_gunicorn
            start_gunicorn
            check_status
            ;;
        status)
            check_status
            ;;
        *)
            echo "用法: $0 {start|stop|restart|status}"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
