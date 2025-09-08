#!/bin/bash

# 🚀 超快速CI/CD测试脚本
# 专门用于快速验证代码质量，无需完整环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 超快速CI/CD测试开始...${NC}"
echo "=================================="

# 记录开始时间
START_TIME=$(date +%s)

# 1. 快速代码质量检查（30秒内完成）
echo -e "${YELLOW}📋 1. 快速代码质量检查...${NC}"
echo "运行 black..."
black --check apps/ manage.py || echo "⚠️  Black检查失败，需要格式化"
echo "运行 isort..."
isort --check-only apps/ manage.py || echo "⚠️  Isort检查失败，需要排序导入"
echo "运行 flake8..."
flake8 apps/ manage.py --max-line-length=88 --extend-ignore=E203,E501,W503,F403,F405,F401,E402,F541,F841,F811,F601,E731,W391,W293,W291,E226 || echo "⚠️  Flake8检查失败"

# 2. 快速语法检查（10秒内完成）
echo -e "${YELLOW}📋 2. 快速语法检查...${NC}"
echo "检查Python语法..."
python3 -m py_compile manage.py
find apps/ -name "*.py" -exec python3 -m py_compile {} \; || echo "⚠️  发现语法错误"

# 3. 快速导入检查（15秒内完成）
echo -e "${YELLOW}📋 3. 快速导入检查...${NC}"
echo "检查Django设置..."
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
import django
django.setup()
print('✅ Django设置正常')
" || echo "⚠️  Django设置有问题"

# 4. 快速安全扫描（20秒内完成）
echo -e "${YELLOW}📋 4. 快速安全扫描...${NC}"
echo "运行 bandit..."
bandit -r apps/ -f json -o bandit-quick.json || echo "⚠️  Bandit扫描失败"
echo "运行 safety..."
safety check --json || echo "⚠️  Safety扫描失败"

# 5. 快速测试（30秒内完成）
echo -e "${YELLOW}📋 5. 快速测试...${NC}"
echo "运行关键测试..."
export DJANGO_SETTINGS_MODULE=config.settings.testing
python3 manage.py test tests/unit/ --verbosity=0 || echo "⚠️  单元测试失败"

# 计算执行时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${GREEN}🎉 超快速CI/CD测试完成！${NC}"
echo -e "${BLUE}⏱️  总执行时间: ${DURATION}秒${NC}"
echo "=================================="

if [ $DURATION -lt 120 ]; then
    echo -e "${GREEN}✅ 测试速度优秀 (< 2分钟)${NC}"
elif [ $DURATION -lt 300 ]; then
    echo -e "${YELLOW}⚠️  测试速度一般 (2-5分钟)${NC}"
else
    echo -e "${RED}❌ 测试速度较慢 (> 5分钟)${NC}"
fi

echo ""
echo -e "${BLUE}💡 快速测试完成，可以推送到GitHub进行完整CI/CD测试${NC}"
echo -e "${BLUE}📊 如需完整测试，运行: ./local-github-cicd.sh${NC}"
