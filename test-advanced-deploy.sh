#!/bin/bash

# Advanced Deployment Test Script
# 现代化部署测试脚本

set -euo pipefail

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} ${YELLOW}$1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
    exit 1
}

info() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] ℹ️  $1${NC}"
}

warning() {
    echo -e "${PURPLE}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

# 配置
readonly SERVER_HOST="47.103.143.152"
readonly SERVER_USER="root"
readonly SERVER_PASSWORD="GJc9d5&b5z"
readonly DEPLOY_PATH="/root/modeshift_django"
readonly PYTHON_VERSION="3.12"

# 测试计数器
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log "Running test: $test_name"
    
    if eval "$test_command"; then
        success "$test_name passed"
        ((TESTS_PASSED++))
        return 0
    else
        error "$test_name failed"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 检查依赖
check_dependencies() {
    log "Checking dependencies..."
    
    local deps=("sshpass" "ssh" "curl" "tar" "rsync")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing_deps[*]}"
    fi
    
    success "All dependencies available"
}

# 测试SSH连接
test_ssh_connection() {
    sshpass -p "$SERVER_PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
        "$SERVER_USER@$SERVER_HOST" "echo 'SSH connection successful'"
}

# 测试服务器环境
test_server_environment() {
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        echo "=== Server Environment Check ==="
        echo "OS: $(lsb_release -d | cut -f2)"
        echo "Kernel: $(uname -r)"
        echo "Python: $(python3 --version)"
        echo "Pip: $(pip3 --version)"
        echo "Disk space: $(df -h / | tail -1 | awk '{print $4}')"
        echo "Memory: $(free -h | grep Mem | awk '{print $7}')"
        echo "Uptime: $(uptime -p)"
        
        # Check required services
        echo "=== Service Status ==="
        systemctl is-active nginx || echo "Nginx not active"
        systemctl is-active postgresql || echo "PostgreSQL not active"
        systemctl is-active redis-server || echo "Redis not active"
        
        echo "=== Port Status ==="
        netstat -tlnp | grep -E ':(80|443|5432|6379|8000)' || echo "No services listening on expected ports"
EOF
}

# 测试代码打包
test_code_packaging() {
    log "Testing code packaging..."
    
    # Create test deployment directory
    local test_dir="test-deployment-$(date +%s)"
    mkdir -p "$test_dir"
    
    # Copy source code (excluding unnecessary files)
    rsync -av --exclude='.git' \
              --exclude='venv' \
              --exclude='__pycache__' \
              --exclude='*.pyc' \
              --exclude='.pytest_cache' \
              --exclude='coverage-reports' \
              --exclude='htmlcov' \
              --exclude='*.log' \
              --exclude='test-*' \
              --exclude='.github' \
              --exclude='node_modules' \
              --exclude='.env*' \
              . "$test_dir/"
    
    # Create deployment archive
    cd "$test_dir"
    tar -czf "../deployment-test.tar.gz" .
    cd ..
    
    # Check archive
    local archive_size=$(du -h "deployment-test.tar.gz" | cut -f1)
    local file_count=$(tar -tzf "deployment-test.tar.gz" | wc -l)
    
    info "Archive created: $archive_size ($file_count files)"
    
    # Cleanup
    rm -rf "$test_dir"
    rm -f "deployment-test.tar.gz"
    
    success "Code packaging test completed"
}

# 测试文件传输
test_file_transfer() {
    log "Testing file transfer..."
    
    # Create test file
    echo "Test file content $(date)" > test-file.txt
    
    # Upload file
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no \
        test-file.txt "$SERVER_USER@$SERVER_HOST:/tmp/"
    
    # Verify file
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no \
        "$SERVER_USER@$SERVER_HOST" "test -f /tmp/test-file.txt && echo 'File uploaded successfully'"
    
    # Cleanup
    rm -f test-file.txt
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no \
        "$SERVER_USER@$SERVER_HOST" "rm -f /tmp/test-file.txt"
    
    success "File transfer test completed"
}

# 测试环境变量设置
test_environment_variables() {
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        echo "=== Environment Variables Test ==="
        
        # Set test environment variables
        export DJANGO_SETTINGS_MODULE=config.settings.development
        export DEBUG=True
        export ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
        
        export DB_NAME=qatoolbox
        export DB_USER=qatoolbox
        export DB_PASSWORD=qatoolbox123
        export DB_HOST=localhost
        export DB_PORT=5432
        
        export REDIS_URL=redis://localhost:6379/0
        
        # Verify environment variables
        echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
        echo "DEBUG: $DEBUG"
        echo "DB_NAME: $DB_NAME"
        echo "DB_USER: $DB_USER"
        echo "REDIS_URL: $REDIS_URL"
        
        echo "Environment variables test completed"
EOF
}

# 测试进程管理
test_process_management() {
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        echo "=== Process Management Test ==="
        
        # Check current processes
        echo "Current Gunicorn processes:"
        ps aux | grep gunicorn | grep -v grep || echo "No Gunicorn processes found"
        
        # Test process management commands
        echo "Testing process management..."
        
        # Test killall command
        killall gunicorn 2>/dev/null || echo "No Gunicorn processes to kill"
        sleep 2
        killall -9 gunicorn 2>/dev/null || echo "No Gunicorn processes to force kill"
        
        echo "Process management test completed"
EOF
}

# 测试网络连接
test_network_connectivity() {
    log "Testing network connectivity..."
    
    # Test server connectivity
    if ping -c 3 "$SERVER_HOST" > /dev/null 2>&1; then
        success "Server ping successful"
    else
        warning "Server ping failed"
    fi
    
    # Test HTTP connectivity
    if curl -f -s --max-time 10 "http://$SERVER_HOST/" > /dev/null 2>&1; then
        success "HTTP connectivity successful"
    else
        warning "HTTP connectivity failed"
    fi
    
    # Test domain connectivity
    if curl -f -s --max-time 10 "http://shenyiqing.xin/" > /dev/null 2>&1; then
        success "Domain connectivity successful"
    else
        warning "Domain connectivity failed"
    fi
}

# 测试Python环境
test_python_environment() {
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
        echo "=== Python Environment Test ==="
        
        # Check Python version
        python3 --version
        
        # Check pip
        pip3 --version
        
        # Test virtual environment creation
        echo "Testing virtual environment creation..."
        TEST_VENV_DIR="/tmp/test-venv-$(date +%s)"
        python3 -m venv "$TEST_VENV_DIR"
        
        if [ -d "$TEST_VENV_DIR" ]; then
            echo "Virtual environment created successfully"
            rm -rf "$TEST_VENV_DIR"
        else
            echo "Virtual environment creation failed"
            exit 1
        fi
        
        # Test pip install with break-system-packages
        echo "Testing pip install with --break-system-packages..."
        pip3 install --upgrade pip --break-system-packages || echo "Pip upgrade failed"
        
        echo "Python environment test completed"
EOF
}

# 主测试函数
main() {
    echo -e "${CYAN}"
    echo "🚀 Advanced Deployment Test Suite"
    echo "=================================="
    echo -e "${NC}"
    echo "Server: $SERVER_HOST"
    echo "User: $SERVER_USER"
    echo "Deploy Path: $DEPLOY_PATH"
    echo "Python Version: $PYTHON_VERSION"
    echo ""
    
    # 运行所有测试
    run_test "Dependencies Check" "check_dependencies"
    run_test "SSH Connection" "test_ssh_connection"
    run_test "Server Environment" "test_server_environment"
    run_test "Code Packaging" "test_code_packaging"
    run_test "File Transfer" "test_file_transfer"
    run_test "Environment Variables" "test_environment_variables"
    run_test "Process Management" "test_process_management"
    run_test "Network Connectivity" "test_network_connectivity"
    run_test "Python Environment" "test_python_environment"
    
    # 测试结果总结
    echo ""
    echo -e "${CYAN}📊 Test Results Summary${NC}"
    echo "=========================="
    echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        success "🎉 All tests passed! Deployment should work successfully."
        echo ""
        info "Next steps:"
        echo "1. Ensure all GitHub Secrets are configured"
        echo "2. Push the advanced-deploy.yml workflow to .github/workflows/"
        echo "3. Monitor the deployment in GitHub Actions"
    else
        error "Some tests failed. Please fix the issues before deploying."
    fi
}

# 错误处理
trap 'error "Script interrupted"' INT TERM

# 运行主函数
main "$@"
