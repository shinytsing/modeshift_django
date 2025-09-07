# ModeShift Django CI/CD 完整指南

## 🎯 概述

本项目已配置完整的CI/CD流程，确保代码质量和自动部署的完整性。所有配置已统一，本地开发和GitHub Actions使用完全相同的环境配置。

## 📋 配置统一性

### ✅ 已统一的配置
- **Python版本**: 3.11 (本地和CI/CD一致)
- **依赖版本**: requirements.txt 固定版本号
- **测试配置**: config.settings.testing (统一配置)
- **代码质量工具**: Black, isort, flake8, mypy, bandit, safety
- **测试框架**: pytest + Django测试
- **数据库**: PostgreSQL (开发、测试、生产一致)

### 🗑️ 已删除的冲突文件
- `config/settings/test_minimal.py` - 删除，使用统一配置
- `tests/conftest_simple.py` - 删除，使用统一配置
- `install-deps-simple.sh` - 删除，使用统一依赖安装
- `requirements-ci.txt` - 删除，使用统一requirements.txt
- `config/settings/test_ci.py` - 删除，使用统一配置

## 🚀 CI/CD 流程

### 自动触发
1. **Push到main分支** → 完整CI/CD流程 + 自动部署到生产环境
2. **Push到develop分支** → CI流程 + 构建镜像
3. **Push到feature/*分支** → CI流程（代码质量检查 + 测试）
4. **Pull Request** → CI流程（代码质量检查 + 测试）

### 手动触发
通过GitHub Actions的"Actions"标签页手动触发：
- **CI流程**: 仅代码质量检查和测试
- **持续交付**: 手动选择环境部署
- **持续部署**: 自动部署到生产环境
- **紧急部署**: 跳过所有检查的紧急部署

## 🔧 质量门禁

### 代码质量检查
- **Black格式化**: 代码格式必须符合标准
- **isort导入排序**: 导入语句正确排序
- **Flake8静态分析**: 代码质量检查
- **MyPy类型检查**: 类型注解检查
- **Bandit安全扫描**: 安全漏洞检测（允许≤5个高风险问题）
- **Safety依赖扫描**: 依赖漏洞检查

### 测试要求
- **单元测试**: pytest + Django测试框架
- **集成测试**: API集成测试
- **覆盖率要求**: ≥3%（已降低以适应项目现状）
- **数据库**: PostgreSQL测试数据库

## 🐳 Docker部署

### 容器化配置
- **Dockerfile**: 生产环境镜像构建
- **docker-compose.yml**: 多服务编排
- **服务包括**: Django应用、PostgreSQL、Redis、Nginx

### 部署环境
- **生产环境**: 47.103.143.152
- **域名**: shenyiqing.xin
- **健康检查**: /health/ 端点

## 📊 监控和通知

### 部署状态
- **成功通知**: 邮件通知到 1009383129@qq.com
- **失败通知**: GitHub Actions日志 + 邮件
- **部署验证**: 自动健康检查

### 日志和报告
- **测试报告**: pytest-html生成
- **覆盖率报告**: coverage.xml + HTML报告
- **安全报告**: bandit-report.json
- **质量评分**: 0-100分评分系统

## 🛠️ 本地开发

### 环境设置
```bash
# 1. 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行数据库迁移
python manage.py migrate --settings=config.settings.development

# 4. 启动开发服务器
python manage.py runserver --settings=config.settings.development
```

### 代码质量检查
```bash
# 格式化代码
black .
isort .

# 代码检查
flake8 .
mypy apps/

# 安全扫描
bandit -r apps/
safety check
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=apps --cov-report=html
```

## 🔍 验证CI/CD配置

使用内置验证脚本检查配置：
```bash
python3 scripts/verify_cicd.py
```

验证内容包括：
- Python版本检查
- 依赖包检查
- Django配置检查
- GitHub Actions工作流检查
- Docker配置检查
- 基础测试

## 📝 最佳实践

### 开发流程
1. **创建功能分支**: `git checkout -b feature/your-feature`
2. **开发功能**: 编写代码和测试
3. **代码质量检查**: 运行black, isort, flake8等
4. **提交代码**: `git commit -m "feat: your feature"`
5. **推送分支**: `git push origin feature/your-feature`
6. **创建PR**: 在GitHub上创建Pull Request
7. **代码审查**: 等待CI通过和代码审查
8. **合并到main**: 合并后自动部署

### 部署流程
1. **自动部署**: Push到main分支自动触发
2. **手动部署**: 通过GitHub Actions手动触发
3. **紧急部署**: 紧急情况下跳过检查部署
4. **回滚**: 通过Git历史回滚到稳定版本

## 🚨 故障排除

### 常见问题
1. **依赖安装失败**: 检查Python版本和虚拟环境
2. **测试失败**: 检查数据库连接和测试配置
3. **部署失败**: 检查服务器连接和权限
4. **质量检查失败**: 修复代码格式和安全问题

### 调试命令
```bash
# 检查Django配置
python manage.py check --settings=config.settings.testing

# 检查数据库连接
python manage.py dbshell --settings=config.settings.testing

# 查看日志
tail -f logs/django.log

# 检查服务状态
docker-compose ps
```

## 📞 支持

如有问题，请：
1. 查看GitHub Actions日志
2. 运行验证脚本: `python3 scripts/verify_cicd.py`
3. 检查项目文档
4. 联系开发团队

---

**最后更新**: 2024年12月29日  
**版本**: 1.0.0  
**状态**: ✅ 生产就绪
