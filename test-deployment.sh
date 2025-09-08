#!/bin/bash

# 🧪 部署测试脚本
# 用于验证部署是否成功

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
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

# 默认URL
WEB_URL=${WEB_URL:-"https://shenyinqing.xin"}
API_URL=${API_URL:-"https://shenyinqing.xin"}

# 测试函数
test_endpoint() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    log_info "测试 $name: $url"
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        log_success "$name 正常"
        return 0
    else
        log_error "$name 失败"
        return 1
    fi
}

# 性能测试
test_performance() {
    local url=$1
    local name=$2
    
    log_info "性能测试 $name"
    
    response_time=$(curl -o /dev/null -s -w '%{time_total}' --max-time 10 "$url")
    status_code=$(curl -o /dev/null -s -w '%{http_code}' --max-time 10 "$url")
    
    log_info "响应时间: ${response_time}秒"
    log_info "状态码: $status_code"
    
    if [ "$status_code" = "200" ]; then
        log_success "状态码正常"
    else
        log_warning "状态码异常: $status_code"
    fi
    
    if (( $(echo "$response_time < 2.0" | bc -l 2>/dev/null || echo "0") )); then
        log_success "性能优秀"
    elif (( $(echo "$response_time < 5.0" | bc -l 2>/dev/null || echo "0") )); then
        log_warning "性能一般"
    else
        log_error "性能较差"
    fi
}

# SSL测试
test_ssl() {
    local domain=$1
    
    if [[ "$domain" == https://* ]]; then
        log_info "SSL证书测试"
        
        domain_name=$(echo $domain | sed 's|https://||' | cut -d'/' -f1)
        
        if echo | openssl s_client -servername $domain_name -connect $domain_name:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
            log_success "SSL证书正常"
        else
            log_warning "SSL证书检测失败"
        fi
    fi
}

# 主测试函数
main() {
    log_info "🧪 开始部署测试"
    log_info "测试目标: $WEB_URL"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 5
    
    # 基础功能测试
    log_info "📊 基础功能测试"
    test_endpoint "$WEB_URL/" "首页"
    test_endpoint "$WEB_URL/admin/" "管理后台"
    test_endpoint "$WEB_URL/static/" "静态文件"
    
    # API测试
    log_info "🔌 API功能测试"
    test_endpoint "$API_URL/api/" "API根路径"
    test_endpoint "$API_URL/health/" "健康检查"
    test_endpoint "$API_URL/api/users/" "用户API"
    test_endpoint "$API_URL/api/tools/" "工具API"
    
    # 性能测试
    log_info "⚡ 性能测试"
    test_performance "$WEB_URL/" "首页"
    
    # SSL测试
    test_ssl "$WEB_URL"
    
    log_success "🎉 部署测试完成！"
    log_info "网站地址: $WEB_URL"
    log_info "API地址: $API_URL"
}

# 显示帮助
show_help() {
    echo "🧪 部署测试脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h    显示帮助信息"
    echo "  --url URL     指定测试URL"
    echo ""
    echo "环境变量:"
    echo "  WEB_URL       网站URL (默认: https://shenyinqing.xin)"
    echo "  API_URL       API URL (默认: https://shenyinqing.xin)"
    echo ""
    echo "示例:"
    echo "  $0"
    echo "  $0 --url https://example.com"
    echo "  WEB_URL=https://example.com $0"
}

# 处理参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --url)
            WEB_URL="$2"
            API_URL="$2"
            shift 2
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 执行测试
main
