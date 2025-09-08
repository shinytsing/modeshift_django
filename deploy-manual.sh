#!/bin/bash

# 手动部署方法集合
# 使用方法: ./deploy-manual.sh

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

echo "🛠️ 手动部署方法集合"
echo "=================="
echo ""

# 方法1: 本地构建后上传
deploy_local_build() {
    log_info "方法1: 本地构建后上传"
    
    # 本地构建
    log_info "本地构建项目..."
    python3 -m venv venv_local
    source venv_local/bin/activate
    pip install -r requirements.txt
    python manage.py collectstatic --noinput
    
    # 打包项目
    log_info "打包项目..."
    tar -czf modeshift_django.tar.gz \
        --exclude='venv' \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        .
    
    # 上传到服务器
    log_info "上传到服务器..."
    scp modeshift_django.tar.gz root@47.103.143.152:/tmp/
    
    # 在服务器上解压和部署
    log_info "在服务器上部署..."
    ssh root@47.103.143.152 "
        cd /root &&
        rm -rf modeshift_django_backup &&
        mv modeshift_django modeshift_django_backup &&
        cd /tmp &&
        tar -xzf modeshift_django.tar.gz -C /root/modeshift_django &&
        cd /root/modeshift_django &&
        python3 -m venv venv &&
        venv/bin/python -m pip install -r requirements.txt &&
        venv/bin/python manage.py migrate --noinput &&
        pkill -TERM -f gunicorn || true &&
        sleep 3 &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
        sudo nginx -s reload &&
        echo '✅ 本地构建部署完成'
    "
    
    # 清理本地文件
    rm -f modeshift_django.tar.gz
    rm -rf venv_local
    
    log_success "本地构建部署完成"
}

# 方法2: 使用rsync同步
deploy_with_rsync() {
    log_info "方法2: 使用rsync同步"
    
    # 检查rsync是否安装
    if ! command -v rsync > /dev/null; then
        log_error "rsync未安装，请安装: sudo apt-get install rsync"
        return 1
    fi
    
    # 同步代码到服务器
    log_info "同步代码到服务器..."
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='logs' \
        ./ root@47.103.143.152:/root/modeshift_django/
    
    # 在服务器上部署
    log_info "在服务器上部署..."
    ssh root@47.103.143.152 "
        cd /root/modeshift_django &&
        echo '🐍 更新虚拟环境...' &&
        if [ ! -d 'venv' ]; then
            python3 -m venv venv
        fi &&
        venv/bin/python -m pip install -r requirements.txt --quiet &&
        echo '📁 Django操作...' &&
        venv/bin/python manage.py collectstatic --noinput &&
        venv/bin/python manage.py migrate --noinput &&
        echo '🔄 重启服务...' &&
        pkill -TERM -f gunicorn || true &&
        sleep 3 &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
        sudo nginx -s reload &&
        echo '✅ rsync部署完成'
    "
    
    log_success "rsync部署完成"
}

# 方法3: 使用scp传输
deploy_with_scp() {
    log_info "方法3: 使用scp传输"
    
    # 创建临时目录
    TEMP_DIR="/tmp/modeshift_deploy_$(date +%s)"
    mkdir -p "$TEMP_DIR"
    
    # 复制项目文件
    log_info "准备项目文件..."
    cp -r . "$TEMP_DIR/"
    cd "$TEMP_DIR"
    
    # 清理不需要的文件
    rm -rf .git venv __pycache__ *.pyc .env logs
    
    # 压缩项目
    log_info "压缩项目..."
    tar -czf modeshift_django.tar.gz .
    
    # 传输到服务器
    log_info "传输到服务器..."
    scp modeshift_django.tar.gz root@47.103.143.152:/tmp/
    
    # 在服务器上部署
    log_info "在服务器上部署..."
    ssh root@47.103.143.152 "
        cd /root/modeshift_django &&
        echo '备份当前版本...' &&
        tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz . &&
        echo '解压新版本...' &&
        tar -xzf /tmp/modeshift_django.tar.gz &&
        echo '更新依赖...' &&
        venv/bin/python -m pip install -r requirements.txt --quiet &&
        echo 'Django操作...' &&
        venv/bin/python manage.py collectstatic --noinput &&
        venv/bin/python manage.py migrate --noinput &&
        echo '重启服务...' &&
        pkill -TERM -f gunicorn || true &&
        sleep 3 &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
        sudo nginx -s reload &&
        echo '✅ scp部署完成'
    "
    
    # 清理临时文件
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
    log_success "scp部署完成"
}

# 方法4: 使用git clone
deploy_with_git_clone() {
    log_info "方法4: 使用git clone"
    
    # 在服务器上直接克隆
    log_info "在服务器上克隆项目..."
    ssh root@47.103.143.152 "
        cd /root &&
        echo '备份当前版本...' &&
        if [ -d 'modeshift_django' ]; then
            mv modeshift_django modeshift_django_backup_$(date +%Y%m%d_%H%M%S)
        fi &&
        echo '克隆最新代码...' &&
        git clone https://github.com/shinytsing/modeshift_django.git &&
        cd modeshift_django &&
        echo '设置虚拟环境...' &&
        python3 -m venv venv &&
        venv/bin/python -m pip install -r requirements.txt &&
        echo 'Django操作...' &&
        venv/bin/python manage.py collectstatic --noinput &&
        venv/bin/python manage.py migrate --noinput &&
        echo '启动服务...' &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
        sudo nginx -s reload &&
        echo '✅ git clone部署完成'
    "
    
    log_success "git clone部署完成"
}

# 方法5: 使用wget下载
deploy_with_wget() {
    log_info "方法5: 使用wget下载"
    
    # 创建发布包
    log_info "创建发布包..."
    python3 -c "
import zipfile
import os
import shutil

# 创建临时目录
temp_dir = '/tmp/modeshift_release'
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir)

# 复制文件
for root, dirs, files in os.walk('.'):
    for file in files:
        if not any(x in root for x in ['.git', 'venv', '__pycache__', '.env', 'logs']):
            src = os.path.join(root, file)
            dst = os.path.join(temp_dir, src[2:])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

# 创建zip文件
with zipfile.ZipFile('/tmp/modeshift_django.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_dir)
            zipf.write(file_path, arcname)

shutil.rmtree(temp_dir)
print('发布包创建完成')
"
    
    # 上传到服务器
    log_info "上传到服务器..."
    scp /tmp/modeshift_django.zip root@47.103.143.152:/tmp/
    
    # 在服务器上部署
    log_info "在服务器上部署..."
    ssh root@47.103.143.152 "
        cd /root &&
        echo '备份当前版本...' &&
        if [ -d 'modeshift_django' ]; then
            mv modeshift_django modeshift_django_backup_$(date +%Y%m%d_%H%M%S)
        fi &&
        echo '解压新版本...' &&
        unzip -q /tmp/modeshift_django.zip -d modeshift_django &&
        cd modeshift_django &&
        echo '设置环境...' &&
        python3 -m venv venv &&
        venv/bin/python -m pip install -r requirements.txt &&
        echo 'Django操作...' &&
        venv/bin/python manage.py collectstatic --noinput &&
        venv/bin/python manage.py migrate --noinput &&
        echo '启动服务...' &&
        nohup venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 wsgi:application --daemon &&
        sudo nginx -s reload &&
        echo '✅ wget部署完成'
    "
    
    # 清理临时文件
    rm -f /tmp/modeshift_django.zip
    
    log_success "wget部署完成"
}

# 主菜单
show_menu() {
    echo "请选择手动部署方法:"
    echo "1. 本地构建后上传"
    echo "2. 使用rsync同步"
    echo "3. 使用scp传输"
    echo "4. 使用git clone"
    echo "5. 使用wget下载"
    echo "6. 退出"
    echo ""
    read -p "请输入选择 (1-6): " choice
    
    case $choice in
        1)
            deploy_local_build
            ;;
        2)
            deploy_with_rsync
            ;;
        3)
            deploy_with_scp
            ;;
        4)
            deploy_with_git_clone
            ;;
        5)
            deploy_with_wget
            ;;
        6)
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
