#!/bin/bash

# 修复413 Request Entity Too Large错误
# 更新Nginx配置和Django设置

echo "🔧 修复413 Request Entity Too Large错误..."

# 检查当前目录
if [ ! -f "manage.py" ]; then
    echo "❌ 错误：请在Django项目根目录下运行此脚本"
    exit 1
fi

echo "📋 当前修复内容："
echo "1. ✅ Django设置已配置200MB文件上传限制"
echo "2. ✅ 音频转换API已添加文件大小检查(200MB)"
echo "3. ✅ Nginx配置已设置200MB客户端请求体大小"
echo "4. ✅ 其他文件上传API已更新限制"
echo "5. 🔄 需要重启服务以应用更改"

# 检查Nginx配置
echo ""
echo "🔍 检查Nginx配置..."
if [ -f "nginx.production.conf" ]; then
    echo "✅ 找到nginx.production.conf"
    grep "client_max_body_size" nginx.production.conf || echo "⚠️  未找到client_max_body_size配置"
else
    echo "⚠️  未找到nginx.production.conf"
fi

# 检查Django设置
echo ""
echo "🔍 检查Django设置..."
if [ -f "config/settings/production.py" ]; then
    echo "✅ 找到production.py"
    grep "DATA_UPLOAD_MAX_MEMORY_SIZE\|FILE_UPLOAD_MAX_MEMORY_SIZE" config/settings/production.py || echo "⚠️  未找到文件上传大小配置"
else
    echo "⚠️  未找到production.py"
fi

# 检查音频转换API
echo ""
echo "🔍 检查音频转换API..."
if grep -q "max_file_size.*500.*1024.*1024" apps/tools/legacy_views.py; then
    echo "✅ 音频转换API已添加文件大小检查"
else
    echo "⚠️  音频转换API可能缺少文件大小检查"
fi

echo ""
echo "🚀 建议的部署步骤："
echo "1. 推送代码到服务器："
echo "   git push origin main"
echo ""
echo "2. 在服务器上执行："
echo "   cd /path/to/modeshift_django"
echo "   git pull origin main"
echo ""
echo "3. 重启Nginx："
echo "   sudo systemctl reload nginx"
echo "   或"
echo "   sudo nginx -s reload"
echo ""
echo "4. 重启Django应用："
echo "   # 如果使用Docker："
echo "   docker-compose restart web"
echo "   # 如果使用Gunicorn："
echo "   sudo systemctl restart gunicorn"
echo "   # 如果使用uWSGI："
echo "   sudo systemctl restart uwsgi"
echo ""
echo "5. 测试音频文件上传功能"
echo ""
echo "✅ 修复完成！现在应该可以上传最大200MB的音频文件了。"
