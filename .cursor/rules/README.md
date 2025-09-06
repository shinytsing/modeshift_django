# Cursor规则集合

本项目集成了基于awesome-cursorrules的语言特定规则，为Django项目提供全面的AI编程辅助。

## 📁 规则文件结构

```
.cursor/rules/
├── README.md                    # 本文件
├── language-specific.mdc        # 语言特定规则总览
├── ai-programming-rules.mdc     # AI编程核心规则
├── project-structure.mdc        # 项目结构指南
├── coding-standards.mdc         # 通用编码标准
├── api-keys-security.mdc        # API密钥安全管理
├── cicd-deployment.mdc          # CI/CD和部署流程
├── testing-standards.mdc        # 测试标准
├── django-patterns.mdc          # Django开发模式
├── python-specific.mdc          # Python语言规则
├── javascript-typescript.mdc    # JS/TS语言规则
├── html-css.mdc                 # HTML/CSS规则
├── yaml-json.mdc                # 配置文件规则
└── shell-scripts.mdc            # Shell脚本规则
```

## 🎯 规则分类

### 核心规则 (alwaysApply: true)
- **ai-programming-rules.mdc** - AI编程核心原则
- **project-structure.mdc** - 项目结构指南
- **language-specific.mdc** - 语言特定规则总览

### 语言特定规则 (globs)
- **python-specific.mdc** - `*.py` 文件
- **javascript-typescript.mdc** - `*.js,*.ts,*.jsx,*.tsx` 文件
- **html-css.mdc** - `*.html,*.css,*.scss,*.sass,*.less` 文件
- **yaml-json.mdc** - `*.yml,*.yaml,*.json` 文件
- **shell-scripts.mdc** - `*.sh,*.bash,*.zsh,*.fish` 文件

### 功能特定规则 (description)
- **coding-standards.mdc** - 通用编码标准
- **api-keys-security.mdc** - API密钥安全管理
- **cicd-deployment.mdc** - CI/CD和部署流程
- **testing-standards.mdc** - 测试标准
- **django-patterns.mdc** - Django开发模式

## 🚀 使用方法

### 自动应用
Cursor会根据文件类型自动应用相应的规则：
- 编辑Python文件时，自动应用Python最佳实践
- 编写前端代码时，自动应用JavaScript/TypeScript规范
- 修改配置文件时，自动应用YAML/JSON格式要求

### 手动引用
在需要特定规则时，可以在注释中引用：
```python
# 遵循 python-specific 规则
def example_function():
    pass
```

## 📋 规则内容概览

### AI编程核心规则
- 代码复用优先原则
- 模块化设计原则
- API接口稳定性
- 测试代码与被测试代码分离原则
- 数据结构重复检查原则

### Python特定规则
- 类型注解要求
- 文档字符串规范
- Django最佳实践
- 测试框架使用
- 性能优化建议

### JavaScript/TypeScript规则
- 类型安全编程
- React组件规范
- 现代ES特性使用
- 性能优化技巧
- 测试最佳实践

### HTML/CSS规则
- 语义化HTML
- 现代CSS特性
- 响应式设计
- 可访问性要求
- 性能优化

### 配置文件规则
- YAML格式规范
- JSON结构要求
- 环境配置管理
- 验证和工具使用

### Shell脚本规则
- 错误处理机制
- 安全性要求
- 进程管理
- 日志和调试

## 🔧 自定义规则

### 添加新规则
1. 在 `.cursor/rules/` 目录下创建新的 `.mdc` 文件
2. 设置适当的 `globs` 或 `description` 字段
3. 编写规则内容
4. 更新本README文件

### 修改现有规则
1. 编辑对应的 `.mdc` 文件
2. 确保规则与项目需求一致
3. 测试规则的有效性
4. 更新相关文档

## 📚 参考资源

- [Awesome Cursor Rules](https://github.com/claire-gong-18/awesome-cursorrules)
- [Cursor AI Documentation](https://cursor.sh/docs)
- [Django Best Practices](https://docs.djangoproject.com/)
- [Python PEP 8](https://pep8.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 修改规则文件
4. 测试规则效果
5. 提交Pull Request

## 📝 更新日志

### v1.0.0 (2024-12-29)
- 初始版本发布
- 集成awesome-cursorrules
- 添加语言特定规则
- 完善Django项目支持
