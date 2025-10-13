#!/bin/bash
# 修复分析功能部署问题

set -e

echo "🔧 修复分析功能部署问题..."

# 服务器信息
SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"
DOMAIN="shenyiqing.xin"

# 本地项目路径
LOCAL_PROJECT_PATH="/Users/gaojie/Desktop/PycharmProjects/modeshift_django"

echo "📋 修复信息:"
echo "  服务器: $SERVER_IP"
echo "  域名: $DOMAIN"

# 检查是否安装了sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ 需要安装sshpass: brew install sshpass"
    echo "或者手动执行以下步骤:"
    echo "1. SSH连接到服务器: ssh root@$SERVER_IP"
    echo "2. 执行修复脚本"
    exit 1
fi

echo "🔐 连接到服务器进行诊断..."

# 诊断服务器状态
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'SSH_EOF'
    echo "🔍 诊断服务器状态..."
    
    # 进入项目目录
    cd /root/modeshift_django
    
    # 检查Django服务状态
    echo "📊 Django服务状态:"
    ps aux | grep -E "(runserver|gunicorn)" | grep -v grep || echo "没有找到Django服务"
    
    # 检查端口占用
    echo "🌐 端口占用情况:"
    netstat -tlnp | grep :8000 || echo "端口8000未被占用"
    
    # 检查文件是否存在
    echo "📁 检查分析功能文件:"
    ls -la apps/tools/services/server_analytics_service.py 2>/dev/null && echo "✅ 分析服务文件存在" || echo "❌ 分析服务文件不存在"
    ls -la apps/tools/models/analytics_models.py 2>/dev/null && echo "✅ 分析模型文件存在" || echo "❌ 分析模型文件不存在"
    ls -la apps/tools/views/analytics_views.py 2>/dev/null && echo "✅ 分析视图文件存在" || echo "❌ 分析视图文件不存在"
    ls -la templates/analytics/dashboard.html 2>/dev/null && echo "✅ 仪表盘模板存在" || echo "❌ 仪表盘模板不存在"
    
    # 检查URL配置
    echo "🔗 检查URL配置:"
    grep -n "analytics" apps/tools/urls.py | head -5 || echo "❌ URL配置中没有找到analytics路由"
    
    # 检查Django配置
    echo "⚙️ Django配置检查:"
    python manage.py check --deploy 2>&1 | head -10 || echo "Django配置检查失败"
    
    # 检查数据库迁移状态
    echo "🗄️ 数据库迁移状态:"
    python manage.py showmigrations tools | tail -10 || echo "迁移状态检查失败"
    
    # 检查日志
    echo "📝 最近的错误日志:"
    tail -20 django.log 2>/dev/null || echo "没有找到django.log文件"
    
    echo "✅ 诊断完成"
SSH_EOF

echo ""
echo "🚀 开始修复部署..."

# 创建修复脚本
cat > /tmp/fix_analytics.sh << 'EOF'
#!/bin/bash
# 在服务器上执行的修复脚本

set -e

echo "🔧 在服务器上修复分析功能..."

# 进入项目目录
cd /root/modeshift_django

# 激活虚拟环境
source venv/bin/activate

# 停止所有Django服务
echo "⏹️ 停止Django服务..."
pkill -f "python manage.py runserver" || true
pkill -f "gunicorn" || true
sleep 2

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p apps/tools/models
mkdir -p apps/tools/views
mkdir -p apps/tools/management/commands
mkdir -p templates/analytics

# 检查并修复文件
echo "📋 检查文件..."

# 如果文件不存在，从备份恢复或重新创建
if [ ! -f "apps/tools/services/server_analytics_service.py" ]; then
    echo "❌ 分析服务文件不存在，需要重新部署"
    exit 1
fi

if [ ! -f "apps/tools/models/analytics_models.py" ]; then
    echo "❌ 分析模型文件不存在，需要重新部署"
    exit 1
fi

if [ ! -f "apps/tools/views/analytics_views.py" ]; then
    echo "❌ 分析视图文件不存在，需要重新部署"
    exit 1
fi

if [ ! -f "templates/analytics/dashboard.html" ]; then
    echo "❌ 仪表盘模板不存在，需要重新部署"
    exit 1
fi

# 检查URL配置
echo "🔗 检查URL配置..."
if ! grep -q "analytics" apps/tools/urls.py; then
    echo "❌ URL配置中缺少analytics路由"
    exit 1
fi

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python manage.py makemigrations tools
python manage.py migrate

# 收集静态文件
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput

# 测试Django配置
echo "🧪 测试Django配置..."
python manage.py check

# 测试分析命令
echo "🧪 测试分析数据收集命令..."
python manage.py collect_analytics_data --once

# 启动Django服务
echo "▶️ 启动Django服务..."
nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &

# 等待服务启动
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "✅ Django服务启动成功"
else
    echo "❌ Django服务启动失败"
    echo "📝 错误日志:"
    tail -20 django.log
    exit 1
fi

# 测试分析API
echo "🧪 测试分析API..."
if curl -f http://localhost:8000/tools/api/analytics/dashboard/ > /dev/null 2>&1; then
    echo "✅ 分析API可访问"
else
    echo "❌ 分析API不可访问"
    echo "📝 尝试访问API的响应:"
    curl -v http://localhost:8000/tools/api/analytics/dashboard/ 2>&1 | head -10
fi

echo "🎉 修复完成！"
echo "📊 分析仪表盘: http://shenyiqing.xin/tools/analytics/dashboard/"
echo "🔧 需要管理员权限访问"
EOF

# 传输并执行修复脚本
echo "📤 传输修复脚本到服务器..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no /tmp/fix_analytics.sh $SERVER_USER@$SERVER_IP:/tmp/

echo "🚀 在服务器上执行修复..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'bash /tmp/fix_analytics.sh'

# 清理临时文件
rm -f /tmp/fix_analytics.sh

echo ""
echo "🎉 修复完成！"
echo "📊 请访问: http://$DOMAIN/tools/analytics/dashboard/"
echo "🔧 需要管理员权限访问"
echo ""
echo "如果仍然无法访问，请检查："
echo "1. 是否已登录管理员账户"
echo "2. 服务器防火墙设置"
echo "3. Nginx配置（如果使用）"
