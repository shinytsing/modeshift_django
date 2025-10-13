#!/bin/bash
# ModeShift Django 项目环境激活脚本
# 使用方法: source activate_env.sh

echo "🚀 激活ModeShift Django开发环境..."

# 检查venv目录是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误: venv目录不存在"
    echo "请先运行: python -m venv venv"
    return 1
fi

# 激活虚拟环境
source venv/bin/activate

# 显示环境信息
echo "✅ 虚拟环境已激活"
echo "📍 Python路径: $(which python)"
echo "🐍 Python版本: $(python --version)"
echo "🌐 Django版本: $(python -c 'import django; print(django.get_version())')"
echo ""
echo "📦 可用的质量检查工具:"
echo "  - black (代码格式化)"
echo "  - flake8 (代码检查)"
echo "  - bandit (安全扫描)"
echo "  - mypy (类型检查)"
echo "  - safety (依赖漏洞扫描)"
echo "  - pylint (代码分析)"
echo "  - coverage (测试覆盖率)"
echo ""
echo "🎯 常用命令:"
echo "  - python manage.py runserver  # 启动开发服务器"
echo "  - python manage.py test       # 运行测试"
echo "  - black .                     # 格式化代码"
echo "  - flake8 .                    # 检查代码"
echo "  - bandit -r apps/             # 安全扫描"
echo ""
echo "💡 提示: 使用 'deactivate' 退出虚拟环境"
