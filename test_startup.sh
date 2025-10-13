#!/bin/bash

# QAToolBox 启动测试脚本
echo "🧪 测试QAToolBox项目启动..."

# 检查Python环境
echo "1️⃣ 检查Python环境..."
python3 --version

# 检查Django配置
echo "2️⃣ 检查Django配置..."
python3 manage.py check

# 检查数据库迁移
echo "3️⃣ 检查数据库迁移..."
python3 manage.py showmigrations --plan

# 检查静态文件
echo "4️⃣ 检查静态文件收集..."
python3 manage.py collectstatic --dry-run --noinput

# 检查环境激活脚本
echo "5️⃣ 检查环境激活脚本..."
if [ -f "scripts/setup/activate_env.sh" ]; then
    echo "✅ 环境激活脚本存在: scripts/setup/activate_env.sh"
else
    echo "❌ 环境激活脚本不存在"
fi

# 检查Docker配置
echo "6️⃣ 检查Docker配置..."
if [ -f "docker/docker-compose.yml" ]; then
    echo "✅ Docker配置文件存在: docker/docker-compose.yml"
else
    echo "❌ Docker配置文件不存在"
fi

# 检查关键目录
echo "7️⃣ 检查关键目录结构..."
for dir in apps config templates static docs scripts tests logs data archive docker; do
    if [ -d "$dir" ]; then
        echo "✅ $dir 目录存在"
    else
        echo "❌ $dir 目录不存在"
    fi
done

echo ""
echo "🎉 启动测试完成！"
echo "💡 如果所有检查都通过，项目应该可以正常启动"
echo "🚀 使用以下命令启动项目："
echo "   - 开发环境: source scripts/setup/activate_env.sh && python manage.py runserver"
echo "   - Docker环境: cd docker && docker-compose up -d"
