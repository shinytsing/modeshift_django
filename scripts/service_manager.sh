#!/bin/bash

# 服务管理脚本
# 支持零停机时间部署和服务管理

set -e

# 配置变量
PROJECT_DIR="/root/modeshift_django"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
PID_DIR="$PROJECT_DIR"
CONFIG_FILE="$PROJECT_DIR/gunicorn.conf.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# 检查服务状态
check_service_status() {
    local port=$1
    local service_name=$2
    
    if curl -s -f "http://127.0.0.1:$port/health/" > /dev/null 2>&1; then
        log "$service_name 服务运行正常 (端口: $port)"
        return 0
    else
        warn "$service_name 服务无响应 (端口: $port)"
        return 1
    fi
}

# 获取服务PID
get_service_pid() {
    local port=$1
    ps aux | grep "gunicorn.*$port" | grep -v grep | awk '{print $2}' | head -1
}

# 启动服务
start_service() {
    local port=$1
    local service_name=$2
    local config_file=${3:-$CONFIG_FILE}
    
    log "启动 $service_name 服务 (端口: $port)"
    
    # 检查端口是否已被占用
    if netstat -tlnp | grep ":$port " > /dev/null; then
        warn "端口 $port 已被占用"
        return 1
    fi
    
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    # 启动服务
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 使用配置文件启动Gunicorn
    nohup gunicorn \
        --config "$config_file" \
        --bind "0.0.0.0:$port" \
        --pid "$PID_DIR/gunicorn_$service_name.pid" \
        --access-logfile "$LOG_DIR/gunicorn_access_$service_name.log" \
        --error-logfile "$LOG_DIR/gunicorn_error_$service_name.log" \
        wsgi:application > "$LOG_DIR/$service_name.log" 2>&1 &
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if check_service_status $port $service_name; then
        log "$service_name 服务启动成功"
        return 0
    else
        error "$service_name 服务启动失败"
        return 1
    fi
}

# 停止服务
stop_service() {
    local port=$1
    local service_name=$2
    local graceful=${3:-true}
    
    log "停止 $service_name 服务 (端口: $port)"
    
    local pid=$(get_service_pid $port)
    
    if [ -n "$pid" ]; then
        if [ "$graceful" = true ]; then
            # 优雅关闭
            log "发送SIGTERM信号到进程 $pid"
            kill -TERM $pid
            
            # 等待进程优雅关闭
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 30 ]; do
                sleep 1
                ((count++))
            done
            
            # 如果进程仍在运行，强制关闭
            if kill -0 $pid 2>/dev/null; then
                warn "强制关闭进程 $pid"
                kill -KILL $pid
            fi
        else
            # 强制关闭
            kill -KILL $pid
        fi
        
        log "$service_name 服务已停止"
    else
        warn "未找到端口 $port 上的服务进程"
    fi
}

# 重启服务
restart_service() {
    local port=$1
    local service_name=$2
    local config_file=${3:-$CONFIG_FILE}
    
    log "重启 $service_name 服务 (端口: $port)"
    
    # 停止服务
    stop_service $port $service_name
    
    # 等待一段时间
    sleep 3
    
    # 启动服务
    start_service $port $service_name $config_file
}

# 重新加载服务配置
reload_service() {
    local port=$1
    local service_name=$2
    
    log "重新加载 $service_name 服务配置 (端口: $port)"
    
    local pid=$(get_service_pid $port)
    
    if [ -n "$pid" ]; then
        # 发送HUP信号重新加载配置
        kill -HUP $pid
        log "$service_name 服务配置已重新加载"
    else
        error "未找到端口 $port 上的服务进程"
    fi
}

# 滚动更新
rolling_update() {
    local main_port=8000
    local backup_port=8001
    local main_service="main"
    local backup_service="backup"
    
    log "开始滚动更新..."
    
    # 1. 启动备用服务
    if ! start_service $backup_port $backup_service; then
        error "备用服务启动失败"
    fi
    
    # 2. 等待备用服务完全就绪
    sleep 10
    
    # 3. 更新Nginx配置，将流量切换到备用服务
    log "切换流量到备用服务..."
    update_nginx_config $main_port $backup_port "switch_to_backup"
    
    # 4. 停止主服务
    stop_service $main_port $main_service
    
    # 5. 更新代码（这里可以添加代码更新逻辑）
    log "更新应用代码..."
    update_application_code
    
    # 6. 启动新的主服务
    if ! start_service $main_port $main_service; then
        error "新主服务启动失败"
    fi
    
    # 7. 恢复Nginx配置
    log "恢复流量到主服务..."
    update_nginx_config $main_port $backup_port "switch_to_main"
    
    # 8. 等待新主服务稳定
    sleep 10
    
    # 9. 停止备用服务
    stop_service $backup_port $backup_service
    
    log "滚动更新完成！"
}

# 更新Nginx配置
update_nginx_config() {
    local main_port=$1
    local backup_port=$2
    local action=$3
    
    local nginx_config="/etc/nginx/sites-available/default"
    
    case $action in
        "switch_to_backup")
            # 将主服务标记为down
            sed -i "s/server 127.0.0.1:$main_port max_fails=3 fail_timeout=30s;/server 127.0.0.1:$main_port down;/" "$nginx_config"
            ;;
        "switch_to_main")
            # 恢复主服务
            sed -i "s/server 127.0.0.1:$main_port down;/server 127.0.0.1:$main_port max_fails=3 fail_timeout=30s;/" "$nginx_config"
            ;;
    esac
    
    # 重新加载Nginx配置
    nginx -s reload
    log "Nginx配置已更新"
}

# 更新应用代码
update_application_code() {
    log "更新应用代码..."
    
    # 这里可以添加代码更新逻辑，比如：
    # git pull
    # pip install -r requirements.txt
    # python manage.py migrate
    # python manage.py collectstatic --noinput
    
    # 示例：检查代码更新
    cd "$PROJECT_DIR"
    if [ -d ".git" ]; then
        git fetch origin
        local local_commit=$(git rev-parse HEAD)
        local remote_commit=$(git rev-parse origin/main)
        
        if [ "$local_commit" != "$remote_commit" ]; then
            log "发现新代码，正在更新..."
            git pull origin main
            pip install -r requirements.txt
            python manage.py migrate
            python manage.py collectstatic --noinput
        else
            log "代码已是最新版本"
        fi
    else
        log "非Git仓库，跳过代码更新"
    fi
}

# 监控服务
monitor_services() {
    local main_port=8000
    local backup_port=8001
    
    log "开始监控服务状态..."
    
    while true; do
        # 检查主服务
        if ! check_service_status $main_port "主服务"; then
            warn "主服务异常，尝试重启..."
            restart_service $main_port "main"
        fi
        
        # 检查备用服务（如果存在）
        if netstat -tlnp | grep ":$backup_port " > /dev/null; then
            if ! check_service_status $backup_port "备用服务"; then
                warn "备用服务异常"
            fi
        fi
        
        sleep 30
    done
}

# 显示服务状态
show_status() {
    local main_port=8000
    local backup_port=8001
    
    echo "=== 服务状态 ==="
    
    # 主服务状态
    echo -n "主服务 (端口 $main_port): "
    if check_service_status $main_port "主服务" > /dev/null 2>&1; then
        echo -e "${GREEN}运行中${NC}"
    else
        echo -e "${RED}停止${NC}"
    fi
    
    # 备用服务状态
    echo -n "备用服务 (端口 $backup_port): "
    if check_service_status $backup_port "备用服务" > /dev/null 2>&1; then
        echo -e "${GREEN}运行中${NC}"
    else
        echo -e "${YELLOW}未启动${NC}"
    fi
    
    # 进程信息
    echo ""
    echo "=== 进程信息 ==="
    ps aux | grep gunicorn | grep -v grep || echo "未找到Gunicorn进程"
    
    # 端口信息
    echo ""
    echo "=== 端口信息 ==="
    netstat -tlnp | grep -E ":(8000|8001) " || echo "未找到相关端口"
}

# 清理日志
cleanup_logs() {
    local days=${1:-7}
    
    log "清理 $days 天前的日志文件..."
    
    find "$LOG_DIR" -name "*.log" -type f -mtime +$days -delete
    find "$LOG_DIR" -name "*.log.*" -type f -mtime +$days -delete
    
    log "日志清理完成"
}

# 主函数
main() {
    case "${1:-status}" in
        "start")
            local port=${2:-8000}
            local service_name=${3:-"main"}
            start_service $port $service_name
            ;;
        "stop")
            local port=${2:-8000}
            local service_name=${3:-"main"}
            local graceful=${4:-true}
            stop_service $port $service_name $graceful
            ;;
        "restart")
            local port=${2:-8000}
            local service_name=${3:-"main"}
            restart_service $port $service_name
            ;;
        "reload")
            local port=${2:-8000}
            local service_name=${3:-"main"}
            reload_service $port $service_name
            ;;
        "rolling_update")
            rolling_update
            ;;
        "monitor")
            monitor_services
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            local days=${2:-7}
            cleanup_logs $days
            ;;
        *)
            echo "用法: $0 {start|stop|restart|reload|rolling_update|monitor|status|cleanup}"
            echo ""
            echo "命令说明:"
            echo "  start [port] [service_name]     - 启动服务"
            echo "  stop [port] [service_name] [graceful] - 停止服务"
            echo "  restart [port] [service_name]   - 重启服务"
            echo "  reload [port] [service_name]   - 重新加载服务配置"
            echo "  rolling_update                  - 滚动更新部署"
            echo "  monitor                        - 监控服务状态"
            echo "  status                         - 显示服务状态"
            echo "  cleanup [days]                 - 清理日志文件"
            echo ""
            echo "示例:"
            echo "  $0 start 8000 main            # 在端口8000启动主服务"
            echo "  $0 stop 8000 main true        # 优雅停止主服务"
            echo "  $0 rolling_update             # 执行滚动更新"
            echo "  $0 status                     # 显示服务状态"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
