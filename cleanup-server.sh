#!/bin/bash

# 服务器磁盘清理脚本
# 使用方法: ./cleanup-server.sh

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

echo "🧹 服务器磁盘清理工具"
echo "===================="
echo ""

# 检查磁盘空间
check_disk_space() {
    log_info "检查磁盘空间..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        echo '📊 磁盘使用情况:'
        df -h
        echo ''
        echo '📁 目录大小排序 (前10个):'
        du -h / 2>/dev/null | sort -hr | head -10 || echo '无法获取目录大小信息'
    "
}

# 清理Docker相关文件
cleanup_docker() {
    log_info "清理Docker相关文件..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        echo '🐳 清理Docker...'
        docker system prune -af || echo 'Docker清理失败'
        docker volume prune -f || echo 'Docker卷清理失败'
        docker network prune -f || echo 'Docker网络清理失败'
        echo '✅ Docker清理完成'
    "
}

# 清理系统日志
cleanup_logs() {
    log_info "清理系统日志..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        echo '📋 清理系统日志...'
        # 清理系统日志
        journalctl --vacuum-time=7d || echo '系统日志清理失败'
        # 清理旧日志文件
        find /var/log -name '*.log' -type f -mtime +7 -delete || echo '旧日志文件清理失败'
        find /var/log -name '*.gz' -type f -mtime +7 -delete || echo '旧压缩日志清理失败'
        echo '✅ 系统日志清理完成'
    "
}

# 清理临时文件
cleanup_temp() {
    log_info "清理临时文件..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        echo '🗑️ 清理临时文件...'
        # 清理/tmp目录
        rm -rf /tmp/* || echo '临时文件清理失败'
        # 清理用户临时文件
        rm -rf /root/.cache/* || echo '用户缓存清理失败'
        # 清理apt缓存
        apt-get clean || echo 'APT缓存清理失败'
        apt-get autoclean || echo 'APT自动清理失败'
        echo '✅ 临时文件清理完成'
    "
}

# 清理项目相关文件
cleanup_project() {
    log_info "清理项目相关文件..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        cd $DEPLOY_PATH &&
        echo '📁 清理项目文件...'
        # 清理Python缓存
        find . -name '__pycache__' -type d -exec rm -rf {} + || echo 'Python缓存清理失败'
        find . -name '*.pyc' -type f -delete || echo 'Python字节码清理失败'
        # 清理日志文件
        rm -rf logs/* || echo '项目日志清理失败'
        # 清理媒体文件缓存
        rm -rf media/temp_* || echo '临时媒体文件清理失败'
        # 清理备份文件
        rm -f backup_*.tar.gz || echo '备份文件清理失败'
        echo '✅ 项目文件清理完成'
    "
}

# 清理虚拟环境
cleanup_venv() {
    log_info "清理虚拟环境..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        cd $DEPLOY_PATH &&
        echo '🐍 清理虚拟环境...'
        if [ -d 'venv' ]; then
            echo '备份当前虚拟环境...'
            tar -czf venv_backup_$(date +%Y%m%d_%H%M%S).tar.gz venv/ || echo '虚拟环境备份失败'
            echo '删除虚拟环境...'
            rm -rf venv/ || echo '虚拟环境删除失败'
            echo '✅ 虚拟环境清理完成'
        else
            echo '虚拟环境不存在，跳过清理'
        fi
    "
}

# 清理大文件
cleanup_large_files() {
    log_info "清理大文件..."
    ssh -o StrictHostKeyChecking=no $USERNAME@$HOST "
        echo '📦 查找大文件...'
        echo '大于100MB的文件:'
        find / -type f -size +100M 2>/dev/null | head -10 || echo '未找到大文件'
        echo ''
        echo '大于50MB的文件:'
        find / -type f -size +50M 2>/dev/null | head -20 || echo '未找到大文件'
        echo ''
        echo '⚠️ 请手动检查并删除不需要的大文件'
    "
}

# 完整清理
full_cleanup() {
    log_info "执行完整清理..."
    
    cleanup_docker
    cleanup_logs
    cleanup_temp
    cleanup_project
    cleanup_venv
    
    log_success "完整清理完成"
}

# 快速清理
quick_cleanup() {
    log_info "执行快速清理..."
    
    cleanup_temp
    cleanup_project
    
    log_success "快速清理完成"
}

# 主菜单
show_menu() {
    echo "请选择清理操作:"
    echo "1. 检查磁盘空间"
    echo "2. 快速清理 (临时文件 + 项目文件)"
    echo "3. 完整清理 (Docker + 日志 + 临时文件 + 项目文件 + 虚拟环境)"
    echo "4. 清理Docker"
    echo "5. 清理系统日志"
    echo "6. 清理临时文件"
    echo "7. 清理项目文件"
    echo "8. 清理虚拟环境"
    echo "9. 查找大文件"
    echo "10. 退出"
    echo ""
    read -p "请输入选择 (1-10): " choice
    
    case $choice in
        1)
            check_disk_space
            ;;
        2)
            quick_cleanup
            ;;
        3)
            full_cleanup
            ;;
        4)
            cleanup_docker
            ;;
        5)
            cleanup_logs
            ;;
        6)
            cleanup_temp
            ;;
        7)
            cleanup_project
            ;;
        8)
            cleanup_venv
            ;;
        9)
            cleanup_large_files
            ;;
        10)
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
