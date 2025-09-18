#!/bin/bash
# 部署服务器分析功能到生产环境

set -e

echo "🚀 开始部署服务器分析功能..."

# 服务器信息
SERVER_IP="47.103.143.152"
SERVER_USER="root"
SERVER_PASSWORD="GJc9d5&b5z"
DOMAIN="shenyiqing.xin"

# 本地项目路径
LOCAL_PROJECT_PATH="/Users/gaojie/Desktop/PycharmProjects/modeshift_django"

# 服务器项目路径
SERVER_PROJECT_PATH="/root/modeshift_django"

echo "📋 部署信息:"
echo "  服务器: $SERVER_IP"
echo "  域名: $DOMAIN"
echo "  本地路径: $LOCAL_PROJECT_PATH"
echo "  服务器路径: $SERVER_PROJECT_PATH"

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
TEMP_DIR="/tmp/analytics_deploy_$(date +%s)"
mkdir -p "$TEMP_DIR"

echo "📦 准备部署文件..."

# 复制文件到临时目录
cp -r "$LOCAL_PROJECT_PATH/apps/tools/services/server_analytics_service.py" "$TEMP_DIR/"
cp -r "$LOCAL_PROJECT_PATH/apps/tools/models/analytics_models.py" "$TEMP_DIR/"
cp -r "$LOCAL_PROJECT_PATH/apps/tools/views/analytics_views.py" "$TEMP_DIR/"
cp -r "$LOCAL_PROJECT_PATH/apps/tools/management/commands/collect_analytics_data.py" "$TEMP_DIR/"
mkdir -p "$TEMP_DIR/templates/analytics"
cp -r "$LOCAL_PROJECT_PATH/templates/analytics/dashboard.html" "$TEMP_DIR/templates/analytics/"

# 创建修改后的urls.py
echo "📝 创建修改后的urls.py..."
cp "$LOCAL_PROJECT_PATH/apps/tools/urls.py" "$TEMP_DIR/urls.py"

# 创建数据库迁移文件
echo "📝 创建数据库迁移文件..."
cat > "$TEMP_DIR/0001_analytics_models.py" << 'EOF'
# Generated migration for analytics models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('cpu_percent', models.FloatField(verbose_name='CPU使用率')),
                ('memory_percent', models.FloatField(verbose_name='内存使用率')),
                ('disk_percent', models.FloatField(verbose_name='磁盘使用率')),
                ('load_average', models.JSONField(blank=True, null=True, verbose_name='负载平均值')),
                ('network_bytes_sent', models.BigIntegerField(verbose_name='网络发送字节数')),
                ('network_bytes_recv', models.BigIntegerField(verbose_name='网络接收字节数')),
            ],
            options={
                'verbose_name': '服务器指标',
                'verbose_name_plural': '服务器指标',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='DatabaseMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('db_size', models.CharField(max_length=50, verbose_name='数据库大小')),
                ('total_connections', models.IntegerField(verbose_name='总连接数')),
                ('active_connections', models.IntegerField(verbose_name='活跃连接数')),
                ('idle_connections', models.IntegerField(verbose_name='空闲连接数')),
                ('slow_queries', models.IntegerField(verbose_name='慢查询数')),
                ('dead_tuples', models.IntegerField(verbose_name='死元组数')),
            ],
            options={
                'verbose_name': '数据库指标',
                'verbose_name_plural': '数据库指标',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ApplicationMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('total_requests', models.IntegerField(verbose_name='总请求数')),
                ('successful_requests', models.IntegerField(verbose_name='成功请求数')),
                ('failed_requests', models.IntegerField(verbose_name='失败请求数')),
                ('avg_response_time', models.FloatField(verbose_name='平均响应时间')),
                ('max_response_time', models.FloatField(verbose_name='最大响应时间')),
                ('active_users', models.IntegerField(verbose_name='活跃用户数')),
                ('new_users', models.IntegerField(verbose_name='新用户数')),
            ],
            options={
                'verbose_name': '应用指标',
                'verbose_name_plural': '应用指标',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='发生时间')),
                ('error_type', models.CharField(choices=[('api_error', 'API错误'), ('database_error', '数据库错误'), ('system_error', '系统错误'), ('authentication_error', '认证错误'), ('permission_error', '权限错误'), ('validation_error', '验证错误'), ('external_service_error', '外部服务错误')], max_length=50, verbose_name='错误类型')),
                ('severity', models.CharField(choices=[('low', '低'), ('medium', '中'), ('high', '高'), ('critical', '严重')], max_length=20, verbose_name='严重程度')),
                ('message', models.TextField(verbose_name='错误消息')),
                ('stack_trace', models.TextField(blank=True, null=True, verbose_name='堆栈跟踪')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('endpoint', models.CharField(blank=True, max_length=255, null=True, verbose_name='端点')),
                ('user_agent', models.TextField(blank=True, null=True, verbose_name='用户代理')),
                ('resolved', models.BooleanField(default=False, verbose_name='是否已解决')),
                ('resolved_at', models.DateTimeField(blank=True, null=True, verbose_name='解决时间')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user', verbose_name='相关用户')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_errors', to='auth.user', verbose_name='解决人')),
            ],
            options={
                'verbose_name': '错误日志',
                'verbose_name_plural': '错误日志',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='PerformanceAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='告警时间')),
                ('alert_type', models.CharField(choices=[('cpu_high', 'CPU使用率过高'), ('memory_high', '内存使用率过高'), ('disk_high', '磁盘使用率过高'), ('response_time_slow', '响应时间过慢'), ('error_rate_high', '错误率过高'), ('connection_high', '连接数过高'), ('database_slow', '数据库查询缓慢')], max_length=50, verbose_name='告警类型')),
                ('status', models.CharField(choices=[('active', '活跃'), ('acknowledged', '已确认'), ('resolved', '已解决'), ('dismissed', '已忽略')], default='active', max_length=20, verbose_name='状态')),
                ('title', models.CharField(max_length=255, verbose_name='告警标题')),
                ('message', models.TextField(verbose_name='告警消息')),
                ('threshold_value', models.FloatField(verbose_name='阈值')),
                ('actual_value', models.FloatField(verbose_name='实际值')),
                ('severity', models.CharField(choices=[('low', '低'), ('medium', '中'), ('high', '高'), ('critical', '严重')], max_length=20, verbose_name='严重程度')),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True, verbose_name='确认时间')),
                ('resolved_at', models.DateTimeField(blank=True, null=True, verbose_name='解决时间')),
                ('acknowledged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='acknowledged_alerts', to='auth.user', verbose_name='确认人')),
            ],
            options={
                'verbose_name': '性能告警',
                'verbose_name_plural': '性能告警',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='AnalyticsReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('daily', '日报'), ('weekly', '周报'), ('monthly', '月报'), ('custom', '自定义')], max_length=20, verbose_name='报告类型')),
                ('title', models.CharField(max_length=255, verbose_name='报告标题')),
                ('description', models.TextField(blank=True, null=True, verbose_name='报告描述')),
                ('start_date', models.DateTimeField(verbose_name='开始时间')),
                ('end_date', models.DateTimeField(verbose_name='结束时间')),
                ('data', models.JSONField(verbose_name='报告数据')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('is_public', models.BooleanField(default=False, verbose_name='是否公开')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='创建人')),
            ],
            options={
                'verbose_name': '分析报告',
                'verbose_name_plural': '分析报告',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserBehaviorMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='日期')),
                ('page_views', models.IntegerField(default=0, verbose_name='页面浏览量')),
                ('session_duration', models.IntegerField(default=0, verbose_name='会话时长(秒)')),
                ('api_calls', models.IntegerField(default=0, verbose_name='API调用次数')),
                ('login_count', models.IntegerField(default=0, verbose_name='登录次数')),
                ('last_activity', models.DateTimeField(verbose_name='最后活动时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户行为指标',
                'verbose_name_plural': '用户行为指标',
                'ordering': ['-date', '-last_activity'],
            },
        ),
        migrations.CreateModel(
            name='SystemHealthScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='评分时间')),
                ('overall_score', models.FloatField(verbose_name='总体评分')),
                ('performance_score', models.FloatField(verbose_name='性能评分')),
                ('reliability_score', models.FloatField(verbose_name='可靠性评分')),
                ('security_score', models.FloatField(verbose_name='安全性评分')),
                ('user_experience_score', models.FloatField(verbose_name='用户体验评分')),
                ('details', models.JSONField(verbose_name='详细评分')),
            ],
            options={
                'verbose_name': '系统健康评分',
                'verbose_name_plural': '系统健康评分',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='servermetrics',
            index=models.Index(fields=['timestamp'], name='apps_tools_servermetrics_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='databasemetrics',
            index=models.Index(fields=['timestamp'], name='apps_tools_databasemetrics_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='applicationmetrics',
            index=models.Index(fields=['timestamp'], name='apps_tools_applicationmetrics_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='errorlog',
            index=models.Index(fields=['timestamp'], name='apps_tools_errorlog_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='errorlog',
            index=models.Index(fields=['error_type'], name='apps_tools_errorlog_error_type_idx'),
        ),
        migrations.AddIndex(
            model_name='errorlog',
            index=models.Index(fields=['severity'], name='apps_tools_errorlog_severity_idx'),
        ),
        migrations.AddIndex(
            model_name='errorlog',
            index=models.Index(fields=['resolved'], name='apps_tools_errorlog_resolved_idx'),
        ),
        migrations.AddIndex(
            model_name='performancealert',
            index=models.Index(fields=['timestamp'], name='apps_tools_performancealert_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='performancealert',
            index=models.Index(fields=['alert_type'], name='apps_tools_performancealert_alert_type_idx'),
        ),
        migrations.AddIndex(
            model_name='performancealert',
            index=models.Index(fields=['status'], name='apps_tools_performancealert_status_idx'),
        ),
        migrations.AddIndex(
            model_name='performancealert',
            index=models.Index(fields=['severity'], name='apps_tools_performancealert_severity_idx'),
        ),
        migrations.AddIndex(
            model_name='analyticsreport',
            index=models.Index(fields=['report_type'], name='apps_tools_analyticsreport_report_type_idx'),
        ),
        migrations.AddIndex(
            model_name='analyticsreport',
            index=models.Index(fields=['start_date', 'end_date'], name='apps_tools_analyticsreport_start_end_date_idx'),
        ),
        migrations.AddIndex(
            model_name='analyticsreport',
            index=models.Index(fields=['created_by'], name='apps_tools_analyticsreport_created_by_idx'),
        ),
        migrations.AddIndex(
            model_name='userbehaviormetrics',
            index=models.Index(fields=['date'], name='apps_tools_userbehaviormetrics_date_idx'),
        ),
        migrations.AddIndex(
            model_name='userbehaviormetrics',
            index=models.Index(fields=['user', 'date'], name='apps_tools_userbehaviormetrics_user_date_idx'),
        ),
        migrations.AddIndex(
            model_name='systemhealthscore',
            index=models.Index(fields=['timestamp'], name='apps_tools_systemhealthscore_timestamp_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='userbehaviormetrics',
            unique_together={('user', 'date')},
        ),
    ]
EOF

# 创建部署脚本
echo "📝 创建部署脚本..."
cat > "$TEMP_DIR/deploy_analytics_server.sh" << 'EOF'
#!/bin/bash
# 在服务器上执行的部署脚本

set -e

echo "🚀 在服务器上部署分析功能..."

# 进入项目目录
cd /root/modeshift_django

# 激活虚拟环境
source venv/bin/activate

# 停止Django服务
echo "⏹️ 停止Django服务..."
pkill -f "python manage.py runserver" || true
pkill -f "gunicorn" || true

# 备份当前文件
echo "💾 备份当前文件..."
mkdir -p /root/backup_$(date +%Y%m%d_%H%M%S)
cp -r apps/tools/services/server_analytics_service.py /root/backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp -r apps/tools/models/analytics_models.py /root/backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp -r apps/tools/views/analytics_views.py /root/backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp -r apps/tools/management/commands/collect_analytics_data.py /root/backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p apps/tools/models
mkdir -p apps/tools/views
mkdir -p apps/tools/management/commands
mkdir -p templates/analytics

# 复制新文件
echo "📋 复制新文件..."
cp /tmp/analytics_deploy/server_analytics_service.py apps/tools/services/
cp /tmp/analytics_deploy/analytics_models.py apps/tools/models/
cp /tmp/analytics_deploy/analytics_views.py apps/tools/views/
cp /tmp/analytics_deploy/collect_analytics_data.py apps/tools/management/commands/
cp /tmp/analytics_deploy/dashboard.html templates/analytics/
cp /tmp/analytics_deploy/urls.py apps/tools/

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python manage.py makemigrations tools
python manage.py migrate

# 收集静态文件
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput

# 测试数据收集命令
echo "🧪 测试数据收集命令..."
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
    tail -20 django.log
    exit 1
fi

# 设置定时任务收集数据
echo "⏰ 设置定时任务..."
(crontab -l 2>/dev/null; echo "*/5 * * * * cd /root/modeshift_django && source venv/bin/activate && python manage.py collect_analytics_data --once") | crontab -

echo "🎉 分析功能部署完成！"
echo "📊 访问地址: http://shenyiqing.xin/tools/analytics/dashboard/"
echo "🔧 管理员权限: 需要登录管理员账户"
EOF

# 创建SSH连接脚本
echo "📝 创建SSH连接脚本..."
cat > "$TEMP_DIR/connect_and_deploy.sh" << EOF
#!/bin/bash
# SSH连接并部署

echo "🔐 连接到服务器..."

# 使用sshpass进行密码认证
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'SSH_EOF'
    # 在服务器上创建临时目录
    mkdir -p /tmp/analytics_deploy
    
    # 退出SSH，准备文件传输
SSH_EOF

echo "📤 传输文件到服务器..."
# 传输文件
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r "$TEMP_DIR"/* $SERVER_USER@$SERVER_IP:/tmp/analytics_deploy/

echo "🚀 在服务器上执行部署..."
# 执行部署脚本
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'bash /tmp/analytics_deploy/deploy_analytics_server.sh'

echo "🧹 清理临时文件..."
# 清理服务器上的临时文件
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP 'rm -rf /tmp/analytics_deploy'

echo "✅ 部署完成！"
echo "📊 分析仪表盘: http://$DOMAIN/tools/analytics/dashboard/"
echo "🔧 需要管理员权限访问"
EOF

# 检查是否安装了sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ 需要安装sshpass: brew install sshpass"
    echo "或者手动执行以下步骤:"
    echo "1. 将 $TEMP_DIR 目录复制到服务器"
    echo "2. 在服务器上执行: bash /tmp/analytics_deploy/deploy_analytics_server.sh"
    exit 1
fi

# 执行部署
echo "🚀 开始部署..."
bash "$TEMP_DIR/connect_and_deploy.sh"

# 清理本地临时文件
echo "🧹 清理本地临时文件..."
rm -rf "$TEMP_DIR"

echo "🎉 部署完成！"
echo "📊 分析仪表盘: http://$DOMAIN/tools/analytics/dashboard/"
echo "🔧 需要管理员权限访问"
echo "⏰ 数据收集: 每5分钟自动收集一次"
echo "📈 功能包括:"
echo "   - 用户访问量统计"
echo "   - API调用分析"
echo "   - 系统性能监控"
echo "   - 错误日志分析"
echo "   - 实时数据展示"
echo "   - 历史数据查询"
echo "   - 数据导出功能"
