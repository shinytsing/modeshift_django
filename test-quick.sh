#!/bin/bash

# 🧪 快速测试脚本
# 测试Git Clone部署的关键功能

set -e

# 服务器信息
HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"
USER="root"
PASS="GJc9d5&b5z"
DEPLOY_PATH="/root/modeshift_django"

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

# 测试SSH连接
test_ssh() {
    log "测试SSH连接..."
    if sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
        success "SSH连接正常"
        return 0
    else
        error "SSH连接失败"
        return 1
    fi
}

# 测试网站访问
test_website() {
    log "测试网站访问..."
    if curl -f -s --max-time 10 "http://$HOST/" > /dev/null 2>&1; then
        success "网站访问正常"
        return 0
    else
        warning "网站访问失败"
        return 1
    fi
}

# 测试域名访问
test_domain() {
    log "测试域名访问..."
    if curl -f -s --max-time 10 "http://$DOMAIN/" > /dev/null 2>&1; then
        success "域名访问正常"
        return 0
    else
        warning "域名访问失败"
        return 1
    fi
}

# 检查服务状态
check_services() {
    log "检查服务状态..."
    
    # 检查Gunicorn
    if sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "ps aux | grep gunicorn | grep -v grep" > /dev/null 2>&1; then
        success "Gunicorn服务运行正常"
    else
        warning "Gunicorn服务未运行"
    fi
    
    # 检查Nginx
    if sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "systemctl is-active nginx" | grep -q "active"; then
        success "Nginx服务运行正常"
    else
        warning "Nginx服务异常"
    fi
}

# 主测试函数
main() {
    echo "🧪 开始快速测试"
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    local results=()
    
    # 执行测试
    test_ssh && results+=("✅ SSH连接") || results+=("❌ SSH连接")
    test_website && results+=("✅ 网站访问") || results+=("❌ 网站访问")
    test_domain && results+=("✅ 域名访问") || results+=("❌ 域名访问")
    check_services && results+=("✅ 服务状态") || results+=("❌ 服务状态")
    
    echo ""
    echo "📊 测试结果汇总:"
    for result in "${results[@]}"; do
        echo "  $result"
    done
    
    echo ""
    if [[ "${results[*]}" == *"❌"* ]]; then
        error "部分测试失败"
        echo ""
        echo "🔧 建议操作:"
        echo "  1. 检查服务器状态"
        echo "  2. 手动重启服务"
        echo "  3. 查看详细日志"
        return 1
    else
        success "🎉 所有测试通过！"
        echo ""
        echo "🌐 访问地址:"
        echo "  • http://$HOST"
        echo "  • http://$DOMAIN"
        echo "👤 管理员账号: admin / admin123"
        return 0
    fi
}

# 显示帮助信息
show_help() {
    echo "🧪 快速测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 执行快速测试"
    echo "  $0 --help       # 显示帮助"
}

# 解析命令行参数
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        log "执行快速测试..."
        ;;
    *)
        error "未知选项: $1"
        show_help
        exit 1
        ;;
esac

# 执行测试
main "$@"
