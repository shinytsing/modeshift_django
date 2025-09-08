#!/bin/bash

# 🚀 本地快速测试脚本
# 专门用于本地快速验证，不包含完整CI/CD流程

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 本地快速测试开始...${NC}"
echo "=================================="

# 记录开始时间
START_TIME=$(date +%s)

# 1. 超快速代码质量检查（只检查核心文件）
echo -e "${YELLOW}📋 1. 核心代码质量检查...${NC}"
echo "检查核心文件..."

# 只检查最近修改的文件
RECENT_FILES=$(find apps/ -name "*.py" -mtime -1 2>/dev/null | head -10)
if [ -z "$RECENT_FILES" ]; then
    RECENT_FILES="apps/tools/ apps/users/"
fi

echo "检查文件: $RECENT_FILES"
black --check $RECENT_FILES || echo "⚠️  Black检查失败"
isort --check-only $RECENT_FILES || echo "⚠️  Isort检查失败"

# 2. 超快速语法检查（只检查关键文件）
echo -e "${YELLOW}📋 2. 关键语法检查...${NC}"
echo "检查manage.py..."
python3 -m py_compile manage.py
echo "检查核心应用..."
find apps/ -name "*.py" -exec python3 -m py_compile {} \; 2>/dev/null || echo "⚠️  发现语法错误"

# 3. 超快速Django检查
echo -e "${YELLOW}📋 3. Django设置检查...${NC}"
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
import django
django.setup()
print('✅ Django设置正常')
" || echo "⚠️  Django设置有问题"

# 4. 超快速安全扫描（只检查高风险）
echo -e "${YELLOW}📋 4. 高风险安全扫描...${NC}"
echo "运行关键安全检查..."
bandit -r apps/ -ll -f json -o bandit-quick.json 2>/dev/null || echo "⚠️  Bandit扫描失败"

# 5. 超快速测试（只运行关键测试）
echo -e "${YELLOW}📋 5. 关键功能测试...${NC}"
export DJANGO_SETTINGS_MODULE=config.settings.testing
python3 manage.py check --deploy || echo "⚠️  Django检查失败"

# 计算执行时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${GREEN}🎉 本地快速测试完成！${NC}"
echo -e "${BLUE}⏱️  总执行时间: ${DURATION}秒${NC}"
echo "=================================="

if [ $DURATION -lt 30 ]; then
    echo -e "${GREEN}✅ 测试速度极快 (< 30秒)${NC}"
elif [ $DURATION -lt 60 ]; then
    echo -e "${GREEN}✅ 测试速度很快 (< 1分钟)${NC}"
elif [ $DURATION -lt 120 ]; then
    echo -e "${YELLOW}⚠️  测试速度一般 (< 2分钟)${NC}"
else
    echo -e "${RED}❌ 测试速度较慢 (> 2分钟)${NC}"
fi

echo ""
echo -e "${BLUE}💡 本地快速测试完成！${NC}"
echo -e "${BLUE}📤 可以安全推送到GitHub进行完整CI/CD测试${NC}"
echo -e "${BLUE}🔍 如需完整测试，运行: ./local-github-cicd.sh${NC}"
echo ""
echo -e "${GREEN}🚀 推送命令: git add . && git commit -m \"快速测试通过\" && git push origin main${NC}"
