#!/bin/bash

# 🏥 健康检查和监控脚本
# 用于监控ModeShift Django应用的运行状态
# 支持多种检查方式和告警通知

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="modeshift_django"
PROJECT_DIR="/root/modeshift_django"
LOG_FILE="/var/log/health-monitor.log"
ALERT_LOG="/var/log/health-alerts.log"
STATUS_FILE="/tmp/health-status.json"

# 检查配置
CHECK_INTERVAL=30  # 检查间隔（秒）
MAX_RETRIES=3      # 最大重试次数
TIMEOUT=10         # 超时时间（秒）

# 通知配置
NOTIFICATION_EMAIL="1009383129@qq.com"
WEBHOOK_URL=""  # 可选：Slack/Discord webhook

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

log_alert() {
    echo -e "${PURPLE}🚨 $1${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1" >> "$ALERT_LOG"
}

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$ALERT_LOG")"

# 发送通知
send_notification() {
    local message="$1"
    local level="$2"
    
    # 邮件通知
    if [ -n "$NOTIFICATION_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "[$level] ModeShift Django 健康检查" "$NOTIFICATION_EMAIL" 2>/dev/null || true
    fi
    
    # Webhook通知
    if [ -n "$WEBHOOK_URL" ] && command -v curl &> /dev/null; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"[$level] $message\"}" \
            "$WEBHOOK_URL" 2>/dev/null || true
    fi
}

# 检查服务进程
check_processes() {
    log_info "检查服务进程..."
    
    local issues=0
    
    # 检查Gunicorn进程
    if pgrep -f "gunicorn.*wsgi:application" > /dev/null; then
        local gunicorn_pid=$(pgrep -f "gunicorn.*wsgi:application")
        log_success "Gunicorn进程运行正常 (PID: $gunicorn_pid)"
    else
        log_error "Gunicorn进程未运行"
        ((issues++))
    fi
    
    # 检查Nginx进程
    if pgrep nginx > /dev/null; then
        log_success "Nginx进程运行正常"
    else
        log_error "Nginx进程未运行"
        ((issues++))
    fi
    
    # 检查PostgreSQL进程
    if pgrep postgres > /dev/null; then
        log_success "PostgreSQL进程运行正常"
    else
        log_error "PostgreSQL进程未运行"
        ((issues++))
    fi
    
    # 检查Redis进程
    if pgrep redis-server > /dev/null; then
        log_success "Redis进程运行正常"
    else
        log_error "Redis进程未运行"
        ((issues++))
    fi
    
    return $issues
}

# 检查端口监听
check_ports() {
    log_info "检查端口监听..."
    
    local issues=0
    local ports=("80:HTTP" "443:HTTPS" "8000:Django" "5432:PostgreSQL" "6379:Redis")
    
    for port_info in "${ports[@]}"; do
        local port=$(echo "$port_info" | cut -d: -f1)
        local service=$(echo "$port_info" | cut -d: -f2)
        
        if netstat -tlnp | grep ":$port " > /dev/null; then
            log_success "$service 端口 $port 监听正常"
        else
            log_error "$service 端口 $port 未监听"
            ((issues++))
        fi
    done
    
    return $issues
}

# 检查磁盘空间
check_disk_space() {
    log_info "检查磁盘空间..."
    
    local issues=0
    local threshold=85  # 磁盘使用率阈值
    
    # 检查根分区
    local root_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$root_usage" -lt "$threshold" ]; then
        log_success "根分区空间充足 ($root_usage%)"
    else
        log_warning "根分区空间不足 ($root_usage%)"
        ((issues++))
    fi
    
    # 检查项目目录
    if [ -d "$PROJECT_DIR" ]; then
        local project_usage=$(df "$PROJECT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
        if [ "$project_usage" -lt "$threshold" ]; then
            log_success "项目目录空间充足 ($project_usage%)"
        else
            log_warning "项目目录空间不足 ($project_usage%)"
            ((issues++))
        fi
    fi
    
    return $issues
}

# 检查内存使用
check_memory() {
    log_info "检查内存使用..."
    
    local issues=0
    local threshold=90  # 内存使用率阈值
    
    # 获取内存使用率
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$memory_usage" -lt "$threshold" ]; then
        log_success "内存使用正常 ($memory_usage%)"
    else
        log_warning "内存使用过高 ($memory_usage%)"
        ((issues++))
    fi
    
    return $issues
}

# 检查HTTP端点
check_endpoints() {
    log_info "检查HTTP端点..."
    
    local issues=0
    local endpoints=(
        "http://localhost:8000/:首页"
        "http://localhost:8000/health/:健康检查"
        "http://localhost:8000/admin/:管理后台"
        "https://shenyiqing.xin/:域名首页"
        "https://shenyiqing.xin/health/:域名健康检查"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        local url=$(echo "$endpoint_info" | cut -d: -f1-3)
        local name=$(echo "$endpoint_info" | cut -d: -f4)
        
        local retry_count=0
        local success=false
        
        while [ $retry_count -lt $MAX_RETRIES ]; do
            if curl -f -s --connect-timeout $TIMEOUT --max-time $TIMEOUT "$url" > /dev/null 2>&1; then
                log_success "$name 访问正常"
                success=true
                break
            else
                ((retry_count++))
                if [ $retry_count -lt $MAX_RETRIES ]; then
                    log_warning "$name 访问失败，重试 $retry_count/$MAX_RETRIES"
                    sleep 2
                fi
            fi
        done
        
        if [ "$success" = false ]; then
            log_error "$name 访问失败 (URL: $url)"
            ((issues++))
        fi
    done
    
    return $issues
}

# 检查数据库连接
check_database() {
    log_info "检查数据库连接..."
    
    local issues=0
    
    # 检查PostgreSQL连接
    if command -v psql &> /dev/null; then
        if sudo -u postgres psql -c "SELECT 1;" > /dev/null 2>&1; then
            log_success "PostgreSQL连接正常"
        else
            log_error "PostgreSQL连接失败"
            ((issues++))
        fi
    else
        log_warning "psql命令不存在，跳过PostgreSQL检查"
    fi
    
    # 检查Redis连接
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            log_success "Redis连接正常"
        else
            log_error "Redis连接失败"
            ((issues++))
        fi
    else
        log_warning "redis-cli命令不存在，跳过Redis检查"
    fi
    
    return $issues
}

# 检查日志文件
check_logs() {
    log_info "检查日志文件..."
    
    local issues=0
    local log_files=(
        "/var/log/gunicorn_error.log:Gunicorn错误日志"
        "/var/log/gunicorn_access.log:Gunicorn访问日志"
        "/var/log/nginx/error.log:Nginx错误日志"
        "/var/log/postgresql/postgresql.log:PostgreSQL日志"
    )
    
    for log_info in "${log_files[@]}"; do
        local log_file=$(echo "$log_info" | cut -d: -f1)
        local log_name=$(echo "$log_info" | cut -d: -f2)
        
        if [ -f "$log_file" ]; then
            # 检查最近的错误
            local recent_errors=$(tail -n 100 "$log_file" | grep -i "error\|exception\|critical" | wc -l)
            if [ "$recent_errors" -eq 0 ]; then
                log_success "$log_name 无错误"
            else
                log_warning "$log_name 发现 $recent_errors 个错误"
                ((issues++))
            fi
        else
            log_warning "$log_name 文件不存在"
        fi
    done
    
    return $issues
}

# 检查Docker容器（如果使用Docker）
check_docker() {
    log_info "检查Docker容器..."
    
    local issues=0
    
    if command -v docker &> /dev/null; then
        if docker ps --filter "name=$PROJECT_NAME" --format "table {{.Names}}\t{{.Status}}" | grep -q "$PROJECT_NAME"; then
            log_success "Docker容器运行正常"
            
            # 检查容器健康状态
            local unhealthy_containers=$(docker ps --filter "name=$PROJECT_NAME" --filter "health=unhealthy" --format "{{.Names}}" | wc -l)
            if [ "$unhealthy_containers" -gt 0 ]; then
                log_error "发现 $unhealthy_containers 个不健康的容器"
                ((issues++))
            fi
        else
            log_error "Docker容器未运行"
            ((issues++))
        fi
    else
        log_info "Docker未安装，跳过容器检查"
    fi
    
    return $issues
}

# 生成健康状态报告
generate_report() {
    local total_issues=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 创建状态文件
    cat > "$STATUS_FILE" << EOF
{
    "timestamp": "$timestamp",
    "status": "$([ $total_issues -eq 0 ] && echo "healthy" || echo "unhealthy")",
    "issues_count": $total_issues,
    "checks": {
        "processes": $([ $? -eq 0 ] && echo "pass" || echo "fail"),
        "ports": $([ $? -eq 0 ] && echo "pass" || echo "fail"),
        "disk_space": $([ $? -eq 0 ] && echo "pass" || echo "fail"),
        "memory": $([ $? -eq 0 ] && echo "pass" || echo "fail"),
        "endpoints": $([ $? -eq 0 ] && echo "pass" || echo "fail"),
        "database": $([ $? -eq 0 ] && echo "pass" || echo "fail"),
        "logs": $([ $? -eq 0 ] && echo "pass" || echo "fail"),
        "docker": $([ $? -eq 0 ] && echo "pass" || echo "fail")
    }
}
EOF
    
    log_info "健康状态报告已生成: $STATUS_FILE"
}

# 主检查函数
main_check() {
    log_info "🏥 开始健康检查..."
    
    local total_issues=0
    
    # 执行各项检查
    check_processes
    total_issues=$((total_issues + $?))
    
    check_ports
    total_issues=$((total_issues + $?))
    
    check_disk_space
    total_issues=$((total_issues + $?))
    
    check_memory
    total_issues=$((total_issues + $?))
    
    check_endpoints
    total_issues=$((total_issues + $?))
    
    check_database
    total_issues=$((total_issues + $?))
    
    check_logs
    total_issues=$((total_issues + $?))
    
    check_docker
    total_issues=$((total_issues + $?))
    
    # 生成报告
    generate_report $total_issues
    
    # 输出总结
    echo ""
    if [ $total_issues -eq 0 ]; then
        log_success "🎉 所有检查通过，系统运行正常！"
        return 0
    else
        log_error "❌ 发现 $total_issues 个问题，需要关注"
        
        # 发送告警通知
        if [ $total_issues -gt 0 ]; then
            local alert_message="ModeShift Django 健康检查发现 $total_issues 个问题，请及时处理"
            log_alert "$alert_message"
            send_notification "$alert_message" "WARNING"
        fi
        
        return 1
    fi
}

# 持续监控模式
monitor_mode() {
    log_info "🔄 启动持续监控模式 (间隔: ${CHECK_INTERVAL}秒)"
    
    while true; do
        echo "=========================================="
        echo "监控时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "=========================================="
        
        main_check
        
        echo ""
        echo "等待 $CHECK_INTERVAL 秒后进行下次检查..."
        echo "按 Ctrl+C 停止监控"
        echo ""
        
        sleep $CHECK_INTERVAL
    done
}

# 显示帮助信息
show_help() {
    echo "🏥 ModeShift Django 健康检查脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  check         - 执行一次健康检查 (默认)"
    echo "  monitor       - 持续监控模式"
    echo "  report        - 显示最新报告"
    echo "  --help, -h    - 显示帮助信息"
    echo ""
    echo "检查项目:"
    echo "  - 服务进程状态"
    echo "  - 端口监听状态"
    echo "  - 磁盘空间使用"
    echo "  - 内存使用情况"
    echo "  - HTTP端点访问"
    echo "  - 数据库连接"
    echo "  - 日志文件检查"
    echo "  - Docker容器状态"
    echo ""
    echo "示例:"
    echo "  $0 check      # 执行一次检查"
    echo "  $0 monitor     # 持续监控"
    echo "  $0 report     # 查看报告"
}

# 显示报告
show_report() {
    if [ -f "$STATUS_FILE" ]; then
        echo "📊 最新健康检查报告:"
        echo ""
        cat "$STATUS_FILE" | python3 -m json.tool 2>/dev/null || cat "$STATUS_FILE"
    else
        echo "❌ 没有找到健康检查报告"
        echo "请先运行: $0 check"
    fi
}

# 脚本入口
case "${1:-check}" in
    "check")
        main_check
        ;;
    "monitor")
        monitor_mode
        ;;
    "report")
        show_report
        ;;
    "--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ 未知选项: $1"
        show_help
        exit 1
        ;;
esac
