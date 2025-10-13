# 测试文件整理说明

## 📁 测试文件目录结构

```
test_files/
├── unit_tests/           # 单元测试
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_core.py
│   ├── test_basic.py
│   ├── test_login*.py
│   ├── test_cookie*.py
│   └── test_token*.py
├── integration_tests/    # 集成测试
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_job*.py
│   ├── test_*oauth*.py
│   └── test_*social*.py
├── e2e_tests/           # 端到端测试
│   ├── test_user_flows.py
│   ├── test_user_flows_async.py
│   └── test_playwright*.py
├── api_tests/           # API测试
│   ├── test_aimlapi*.py
│   └── test_*api*.py
├── security_tests/      # 安全测试
│   └── test_security*.py
├── performance_tests/   # 性能测试
│   └── (待添加性能测试文件)
├── legacy_tests/        # 历史测试文件
│   ├── test_*crawler*.py
│   ├── test_*delivery*.py
│   ├── test_*.txt
│   ├── test_*.html
│   └── apps/tools/management/commands/test_*.py
└── config/              # 测试配置
    ├── test_minimal.py
    └── test_dependencies.py
```

## 🗂️ 文件分类说明

### ✅ 保留的重要测试文件

#### 单元测试 (unit_tests/)
- **test_models.py** - 模型测试
- **test_views.py** - 视图测试
- **test_core.py** - 核心功能测试
- **test_login*.py** - 登录相关测试
- **test_cookie*.py** - Cookie管理测试
- **test_token*.py** - Token管理测试

#### 集成测试 (integration_tests/)
- **test_api.py** - API集成测试
- **test_database.py** - 数据库集成测试
- **test_job*.py** - 工作搜索功能测试
- **test_*oauth*.py** - OAuth认证测试
- **test_*social*.py** - 社交功能测试

#### 端到端测试 (e2e_tests/)
- **test_user_flows.py** - 用户流程测试
- **test_playwright*.py** - Playwright自动化测试

#### API测试 (api_tests/)
- **test_aimlapi*.py** - AIMLAPI接口测试
- **test_*api*.py** - 其他API接口测试

### 🗑️ 移动到legacy_tests的文件

#### 爬虫相关测试
- test_*crawler*.py - 各种爬虫测试文件
- test_*delivery*.py - 投递相关测试文件

#### 临时测试文件
- test_*.txt - 测试结果文件
- test_*.html - 测试页面文件
- apps/tools/management/commands/test_*.py - 管理命令测试

## 🚀 使用建议

### 运行测试
```bash
# 运行单元测试
python -m pytest test_files/unit_tests/

# 运行集成测试
python -m pytest test_files/integration_tests/

# 运行端到端测试
python -m pytest test_files/e2e_tests/

# 运行API测试
python -m pytest test_files/api_tests/

# 运行安全测试
python -m pytest test_files/security_tests/
```

### 测试配置
- 使用 `test_files/config/test_minimal.py` 作为测试环境配置
- 使用 `test_files/config/test_dependencies.py` 检查测试依赖

### 清理建议
- **legacy_tests/** 文件夹中的文件可以定期清理
- 保留重要的测试结果文件作为参考
- 删除过时的爬虫和投递测试文件

## 📊 测试文件统计

| 测试类型 | 文件数量 | 状态 |
|----------|----------|------|
| 单元测试 | 15+ | ✅ 活跃 |
| 集成测试 | 10+ | ✅ 活跃 |
| 端到端测试 | 5+ | ✅ 活跃 |
| API测试 | 8+ | ✅ 活跃 |
| 安全测试 | 2+ | ✅ 活跃 |
| 性能测试 | 0 | ⚠️ 待添加 |
| 历史测试 | 50+ | 🗑️ 可清理 |

## 🔧 后续优化建议

1. **添加性能测试**: 创建Locust性能测试文件
2. **完善安全测试**: 添加OWASP安全检查
3. **清理历史文件**: 定期清理legacy_tests中的过时文件
4. **统一测试配置**: 创建统一的测试配置文件
5. **添加测试文档**: 为每个测试模块添加说明文档

---

**整理时间**: 2024年12月29日  
**整理人**: 测试工程师  
**版本**: v1.0
