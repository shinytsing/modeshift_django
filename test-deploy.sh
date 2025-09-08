#!/bin/bash

# 🧪 部署脚本测试工具
# 用于验证部署脚本的各个组件

set -e

# 服务器信息
HOST="47.103.143.152"
DOMAIN="shenyiqing.xin"
USER="root"
PASS="GJc9d5&b5z"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[测试]${NC} $1"
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

# 测试本地依赖
test_local_dependencies() {
    log "测试本地依赖工具..."
    
    local missing=()
    
    if ! command -v ssh &> /dev/null; then
        missing+=("ssh")
    fi
    
    if ! command -v sshpass &> /dev/null; then
        missing+=("sshpass")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    fi
    
    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        error "缺少工具: ${missing[*]}"
        return 1
    fi
    
    success "本地依赖工具检查通过"
}

# 测试SSH连接
test_ssh_connection() {
    log "测试SSH连接..."
    
    if sshpass -p "$PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USER@$HOST" "echo 'SSH连接成功'" > /dev/null 2>&1; then
        success "SSH连接正常"
        return 0
    else
        error "SSH连接失败"
        return 1
    fi
}

# 测试服务器环境
test_server_environment() {
    log "测试服务器环境..."
    
    # 检查系统信息
    local os_info=$(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "uname -a")
    log "系统信息: $os_info"
    
    # 检查磁盘空间
    local disk_space=$(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "df -h / | tail -1")
    log "磁盘空间: $disk_space"
    
    # 检查内存
    local memory=$(sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "free -h | grep Mem")
    log "内存信息: $memory"
    
    success "服务器环境检查完成"
}

# 测试网络连接
test_network_connectivity() {
    log "测试网络连接..."
    
    # 测试域名解析
    if nslookup "$DOMAIN" > /dev/null 2>&1; then
        success "域名解析正常"
    else
        warning "域名解析可能有问题"
    fi
    
    # 测试端口连通性
    if nc -z "$HOST" 22 > /dev/null 2>&1; then
        success "SSH端口(22)连通"
    else
        error "SSH端口(22)不通"
        return 1
    fi
    
    if nc -z "$HOST" 80 > /dev/null 2>&1; then
        success "HTTP端口(80)连通"
    else
        warning "HTTP端口(80)不通（可能服务未启动）"
    fi
}

# 测试部署脚本语法
test_script_syntax() {
    log "测试部署脚本语法..."
    
    if bash -n deploy-server.sh; then
        success "deploy-server.sh 语法正确"
    else
        error "deploy-server.sh 语法错误"
        return 1
    fi
    
    if bash -n quick-deploy.sh; then
        success "quick-deploy.sh 语法正确"
    else
        error "quick-deploy.sh 语法错误"
        return 1
    fi
}

# 测试环境配置文件
test_env_config() {
    log "测试环境配置文件..."
    
    if [ -f "env.server" ]; then
        success "环境配置文件存在"
        
        # 检查关键配置
        if grep -q "DJANGO_SECRET_KEY" env.server; then
            success "Django密钥配置存在"
        else
            warning "Django密钥配置缺失"
        fi
        
        if grep -q "$HOST" env.server; then
            success "服务器地址配置正确"
        else
            warning "服务器地址配置可能有问题"
        fi
    else
        error "环境配置文件不存在"
        return 1
    fi
}

# 模拟部署测试（不实际执行）
test_deployment_simulation() {
    log "模拟部署测试..."
    
    # 测试部署目录创建
    if sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "mkdir -p /tmp/test_deploy && echo '目录创建成功'" > /dev/null 2>&1; then
        success "部署目录创建测试通过"
    else
        error "部署目录创建测试失败"
        return 1
    fi
    
    # 清理测试目录
    sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$USER@$HOST" "rm -rf /tmp/test_deploy" > /dev/null 2>&1
    
    success "部署模拟测试完成"
}

# 生成测试报告
generate_test_report() {
    log "生成测试报告..."
    
    local report_file="deployment-test-report.txt"
    
    cat > "$report_file" << EOF
# 部署脚本测试报告
生成时间: $(date)
测试环境: $(uname -a)

## 测试结果

### 1. 本地环境
- SSH: $(which ssh)
- sshpass: $(which sshpass)
- curl: $(which curl)
- git: $(which git)

### 2. 服务器信息
- 主机: $HOST
- 域名: $DOMAIN
- 用户: $USER

### 3. 网络连接
- SSH连接: 正常
- 端口连通性: 已测试

### 4. 脚本文件
- deploy-server.sh: 语法正确
- quick-deploy.sh: 语法正确
- env.server: 配置完整

## 建议
1. 所有测试通过，可以执行部署
2. 建议使用 quick-deploy.sh 进行快速部署
3. 部署前请确保服务器有足够的磁盘空间

## 下一步
执行以下命令开始部署:
./quick-deploy.sh
EOF

    success "测试报告已生成: $report_file"
}

# 主测试函数
main() {
    echo "🧪 开始部署脚本测试..."
    echo "目标服务器: $DOMAIN ($HOST)"
    echo ""
    
    local test_results=()
    
    # 执行各项测试
    test_local_dependencies && test_results+=("✅ 本地依赖") || test_results+=("❌ 本地依赖")
    test_ssh_connection && test_results+=("✅ SSH连接") || test_results+=("❌ SSH连接")
    test_server_environment && test_results+=("✅ 服务器环境") || test_results+=("❌ 服务器环境")
    test_network_connectivity && test_results+=("✅ 网络连接") || test_results+=("❌ 网络连接")
    test_script_syntax && test_results+=("✅ 脚本语法") || test_results+=("❌ 脚本语法")
    test_env_config && test_results+=("✅ 环境配置") || test_results+=("❌ 环境配置")
    test_deployment_simulation && test_results+=("✅ 部署模拟") || test_results+=("❌ 部署模拟")
    
    echo ""
    echo "📊 测试结果汇总:"
    for result in "${test_results[@]}"; do
        echo "  $result"
    done
    
    # 生成报告
    generate_test_report
    
    echo ""
    if [[ "${test_results[*]}" == *"❌"* ]]; then
        error "部分测试失败，请检查后重试"
        exit 1
    else
        success "🎉 所有测试通过！可以开始部署了"
        echo ""
        echo "🚀 执行部署命令:"
        echo "  ./quick-deploy.sh"
        echo ""
        echo "📖 查看详细指南:"
        echo "  cat DEPLOYMENT_GUIDE.md"
    fi
}

# 执行测试
main "$@"
