#!/bin/bash
# 重新部署分析功能到服务器

set -e

echo "🚀 重新部署分析功能到服务器..."

# 服务器信息
SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"
DOMAIN="shenyiqing.xin"

# 本地项目路径
LOCAL_PROJECT_PATH="/Users/gaojie/Desktop/PycharmProjects/modeshift_django"

echo "📋 部署信息:"
echo "  服务器: $SERVER_IP"
echo "  域名: $DOMAIN"

# 检查本地文件是否存在
echo "🔍 检查本地文件..."
required_files=(
    "apps/tools/services/server_analytics_service.py"
    "apps/tools/models/analytics_models.py"
    "apps/tools/views/analytics_views.py"
    "apps/tools/management/commands/collect_analytics_data.py"
    "templates/analytics/dashboard.html"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$LOCAL_PROJECT_PATH/$file" ]; then
        echo "❌ 文件不存在: $file"
        exit 1
    fi
    echo "✅ $file"
done

# 创建临时目录
TEMP_DIR="/tmp/analytics_redeploy_$(date +%s)"
mkdir -p "$TEMP_DIR"

echo "📦 准备部署文件..."

# 复制文件到临时目录
cp "$LOCAL_PROJECT_PATH/apps/tools/services/server_analytics_service.py" "$TEMP_DIR/"
cp "$LOCAL_PROJECT_PATH/apps/tools/models/analytics_models.py" "$TEMP_DIR/"
cp "$LOCAL_PROJECT_PATH/apps/tools/views/analytics_views.py" "$TEMP_DIR/"
cp "$LOCAL_PROJECT_PATH/apps/tools/management/commands/collect_analytics_data.py" "$TEMP_DIR/"
mkdir -p "$TEMP_DIR/templates/analytics"
cp "$LOCAL_PROJECT_PATH/templates/analytics/dashboard.html" "$TEMP_DIR/templates/analytics/"

# 创建修改后的urls.py（只包含分析相关的路由）
echo "📝 创建分析功能URL配置..."
cat > "$TEMP_DIR/analytics_urls.py" << 'EOF'
# 分析功能URL配置
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View

# 导入分析视图
from apps.tools.views.analytics_views import (
    AnalyticsDashboardAPI,
    AnalyticsReportsAPI,
    ErrorAnalysisAPI,
    ExportDataAPI,
    HistoricalDataAPI,
    PerformanceAlertsAPI,
    RealTimeStatsAPI,
    UserBehaviorAPI,
)

def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def analytics_dashboard_view(request):
    """分析仪表盘视图"""
    return render(request, "analytics/dashboard.html")

# 分析功能URL配置
analytics_urlpatterns = [
    # 分析仪表盘页面
    path("analytics/dashboard/", analytics_dashboard_view, name="analytics_dashboard"),
    
    # 分析API路由
    path("api/analytics/dashboard/", AnalyticsDashboardAPI.as_view(), name="analytics_dashboard_api"),
    path("api/analytics/realtime/", RealTimeStatsAPI.as_view(), name="analytics_realtime_api"),
    path("api/analytics/historical/", HistoricalDataAPI.as_view(), name="analytics_historical_api"),
    path("api/analytics/errors/", ErrorAnalysisAPI.as_view(), name="analytics_errors_api"),
    path("api/analytics/alerts/", PerformanceAlertsAPI.as_view(), name="analytics_alerts_api"),
    path("api/analytics/reports/", AnalyticsReportsAPI.as_view(), name="analytics_reports_api"),
    path("api/analytics/export/", ExportDataAPI.as_view(), name="analytics_export_api"),
    path("api/analytics/user-behavior/", UserBehaviorAPI.as_view(), name="analytics_user_behavior_api"),
]
EOF

# 创建服务器部署脚本
echo "📝 创建服务器部署脚本..."
cat > "$TEMP_DIR/deploy_to_server.sh" << 'EOF'
#!/bin/bash
# 在服务器上执行的部署脚本

set -e

echo "🚀 在服务器上部署分析功能..."

# 进入项目目录
cd /root/modeshift_django

# 激活虚拟环境
source venv/bin/activate

# 停止Gunicorn服务
echo "⏹️ 停止Gunicorn服务..."
pkill -f gunicorn || true
sleep 3

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p apps/tools/models
mkdir -p apps/tools/views
mkdir -p apps/tools/management/commands
mkdir -p templates/analytics

# 复制新文件
echo "📋 复制新文件..."
cp /tmp/analytics_redeploy/server_analytics_service.py apps/tools/services/
cp /tmp/analytics_redeploy/analytics_models.py apps/tools/models/
cp /tmp/analytics_redeploy/analytics_views.py apps/tools/views/
cp /tmp/analytics_redeploy/collect_analytics_data.py apps/tools/management/commands/
cp /tmp/analytics_redeploy/dashboard.html templates/analytics/

# 备份原始urls.py
echo "💾 备份原始urls.py..."
cp apps/tools/urls.py apps/tools/urls.py.backup.$(date +%Y%m%d_%H%M%S)

# 添加分析功能路由到urls.py
echo "🔗 添加分析功能路由..."
cat >> apps/tools/urls.py << 'URLS_EOF'

# 分析功能路由
from apps.tools.views.analytics_views import (
    AnalyticsDashboardAPI,
    AnalyticsReportsAPI,
    ErrorAnalysisAPI,
    ExportDataAPI,
    HistoricalDataAPI,
    PerformanceAlertsAPI,
    RealTimeStatsAPI,
    UserBehaviorAPI,
)

def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def analytics_dashboard_view(request):
    """分析仪表盘视图"""
    return render(request, "analytics/dashboard.html")

# 分析功能路由
urlpatterns += [
    path("analytics/dashboard/", analytics_dashboard_view, name="analytics_dashboard"),
    path("api/analytics/dashboard/", AnalyticsDashboardAPI.as_view(), name="analytics_dashboard_api"),
    path("api/analytics/realtime/", RealTimeStatsAPI.as_view(), name="analytics_realtime_api"),
    path("api/analytics/historical/", HistoricalDataAPI.as_view(), name="analytics_historical_api"),
    path("api/analytics/errors/", ErrorAnalysisAPI.as_view(), name="analytics_errors_api"),
    path("api/analytics/alerts/", PerformanceAlertsAPI.as_view(), name="analytics_alerts_api"),
    path("api/analytics/reports/", AnalyticsReportsAPI.as_view(), name="analytics_reports_api"),
    path("api/analytics/export/", ExportDataAPI.as_view(), name="analytics_export_api"),
    path("api/analytics/user-behavior/", UserBehaviorAPI.as_view(), name="analytics_user_behavior_api"),
]
URLS_EOF

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python3 manage.py makemigrations tools
python3 manage.py migrate

# 收集静态文件
echo "📦 收集静态文件..."
python3 manage.py collectstatic --noinput

# 测试Django配置
echo "🧪 测试Django配置..."
python3 manage.py check

# 测试分析命令
echo "🧪 测试分析数据收集命令..."
python3 manage.py collect_analytics_data --once

# 启动Gunicorn服务
echo "▶️ 启动Gunicorn服务..."
nohup gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 --max-requests 1000 --max-requests-jitter 100 --access-logfile logs/gunicorn_access.log --error-logfile logs/gunicorn_error.log wsgi:application > gunicorn.log 2>&1 &

# 等待服务启动
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "✅ Django服务启动成功"
else
    echo "❌ Django服务启动失败"
    echo "📝 错误日志:"
    tail -20 gunicorn.log
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

# 设置定时任务收集数据
echo "⏰ 设置定时任务..."
(crontab -l 2>/dev/null; echo "*/5 * * * * cd /root/modeshift_django && source venv/bin/activate && python3 manage.py collect_analytics_data --once") | crontab -

echo "🎉 分析功能部署完成！"
echo "📊 访问地址: http://shenyiqing.xin/tools/analytics/dashboard/"
echo "🔧 管理员权限: 需要登录管理员账户"
EOF

# 检查是否安装了sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ 需要安装sshpass: brew install sshpass"
    echo "或者手动执行以下步骤:"
    echo "1. 将 $TEMP_DIR 目录复制到服务器"
    echo "2. 在服务器上执行: bash /tmp/analytics_redeploy/deploy_to_server.sh"
    exit 1
fi

echo "🔐 连接到服务器..."

# 传输文件到服务器
echo "📤 传输文件到服务器..."
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r "$TEMP_DIR"/* $SERVER_USER@$SERVER_IP:/tmp/analytics_redeploy/

echo "🚀 在服务器上执行部署..."
# 执行部署脚本
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'bash /tmp/analytics_redeploy/deploy_to_server.sh'

echo "🧹 清理临时文件..."
# 清理服务器上的临时文件
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'rm -rf /tmp/analytics_redeploy'

# 清理本地临时文件
rm -rf "$TEMP_DIR"

echo "🎉 重新部署完成！"
echo "📊 分析仪表盘: http://$DOMAIN/tools/analytics/dashboard/"
echo "🔧 需要管理员权限访问"
echo "⏰ 数据收集: 每5分钟自动收集一次"
