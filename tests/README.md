# 测试框架文档

## 概述

这是一个完整的测试框架，包含Playwright UI测试、WebSocket接口测试、性能测试，并使用pytest进行集成。

## 测试框架结构

```
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # pytest全局配置和fixtures
├── test_utilities.py             # 测试工具和辅助函数
├── run_tests.py                  # Python测试运行器
├── run_tests.sh                  # Shell测试运行脚本
├── ui/                           # UI测试
│   ├── conftest.py              # UI测试配置
│   ├── test_basic_ui.py         # 基础UI测试
│   └── test_advanced_ui.py      # 高级UI测试
├── websocket/                    # WebSocket测试
│   ├── conftest.py              # WebSocket测试配置
│   ├── test_basic_websocket.py  # 基础WebSocket测试
│   └── test_advanced_websocket.py # 高级WebSocket测试
├── performance/                  # 性能测试
│   ├── conftest.py              # 性能测试配置
│   ├── test_load_testing.py     # 负载测试
│   ├── test_stress_testing.py   # 压力测试
│   └── test_benchmark_testing.py # 基准测试
├── reports/                     # 测试报告目录
│   ├── html-report.html         # HTML测试报告
│   ├── coverage/                # 覆盖率报告
│   └── screenshots/             # 截图目录
└── test_data/                   # 测试数据目录
```

## 测试类型

### 1. UI测试 (Playwright)

**功能覆盖：**
- 基础UI功能测试
- 响应式设计测试
- 表单交互测试
- 认证相关UI测试
- 工具页面UI测试
- 错误处理UI测试
- 高级UI功能测试
- 动态内容加载测试
- 模态对话框测试
- 下拉菜单测试
- 标签页和手风琴组件测试
- 交互功能测试（拖拽、键盘导航、鼠标交互）
- UI性能测试

**运行方式：**
```bash
# 运行所有UI测试
python -m pytest tests/ui/ -m ui

# 运行基础UI测试
python -m pytest tests/ui/test_basic_ui.py

# 运行高级UI测试
python -m pytest tests/ui/test_advanced_ui.py
```

### 2. WebSocket测试

**功能覆盖：**
- WebSocket连接测试
- 认证测试
- 房间加入测试
- 心跳机制测试
- 消息发送和接收测试
- 多用户交互测试
- 用户加入/离开通知测试
- 消息广播测试
- 打字状态测试
- 已读状态测试
- 在线状态测试
- 视频通话功能测试
- 并发操作测试
- 性能测试
- 错误处理测试

**运行方式：**
```bash
# 运行所有WebSocket测试
python -m pytest tests/websocket/ -m websocket

# 运行基础WebSocket测试
python -m pytest tests/websocket/test_basic_websocket.py

# 运行高级WebSocket测试
python -m pytest tests/websocket/test_advanced_websocket.py
```

### 3. 性能测试

**功能覆盖：**

#### 负载测试
- 首页负载测试
- API端点负载测试
- 工具页面负载测试
- 持续负载测试
- 并发用户测试
- 混合流量模式测试
- 资源利用率测试

#### 压力测试
- 高并发压力测试
- 突发流量压力测试
- 内存压力测试
- 连接压力测试
- 极限测试
- 压力后恢复能力测试
- 资源耗尽测试

#### 基准测试
- 响应时间基准测试
- 吞吐量基准测试
- 资源使用基准测试
- 可扩展性测试
- 性能回归测试

**运行方式：**
```bash
# 运行所有性能测试
python -m pytest tests/performance/ -m performance

# 运行负载测试
python -m pytest tests/performance/test_load_testing.py

# 运行压力测试
python -m pytest tests/performance/test_stress_testing.py

# 运行基准测试
python -m pytest tests/performance/test_benchmark_testing.py
```

## 配置和依赖

### 必需依赖

```bash
pip install pytest pytest-asyncio pytest-django pytest-cov pytest-html playwright aiohttp channels
```

### 环境变量

```bash
# 测试基础URL
export TEST_BASE_URL=http://localhost:8000

# 测试超时时间
export TEST_TIMEOUT=30

# 最大重试次数
export TEST_MAX_RETRIES=3

# 并发用户数
export TEST_CONCURRENT_USERS=10

# 测试持续时间
export TEST_DURATION=60

# 性能阈值
export TEST_PERFORMANCE_THRESHOLD=2.0

# 成功率阈值
export TEST_SUCCESS_RATE_THRESHOLD=95.0
```

## 运行测试

### 使用Python脚本

```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定类型测试
python tests/run_tests.py --type ui
python tests/run_tests.py --type websocket
python tests/run_tests.py --type performance

# 运行特定测试
python tests/run_tests.py --test tests/ui/test_basic_ui.py

# 运行带标记的测试
python tests/run_tests.py --markers "ui and not slow"

# 生成报告
python tests/run_tests.py --summary
```

### 使用Shell脚本

```bash
# 运行所有测试
./tests/run_tests.sh

# 运行特定类型测试
./tests/run_tests.sh ui
./tests/run_tests.sh websocket
./tests/run_tests.sh performance

# 运行特定测试
./tests/run_tests.sh -t tests/ui/test_basic_ui.py

# 运行带标记的测试
./tests/run_tests.sh -m "ui and not slow"

# 检查依赖
./tests/run_tests.sh -c

# 生成报告
./tests/run_tests.sh -r

# 清理测试数据
./tests/run_tests.sh -l
```

### 使用pytest直接运行

```bash
# 运行所有测试
python -m pytest tests/ --verbose --html=tests/reports/html-report.html

# 运行UI测试
python -m pytest tests/ui/ -m ui --html=tests/reports/ui-report.html

# 运行WebSocket测试
python -m pytest tests/websocket/ -m websocket --html=tests/reports/websocket-report.html

# 运行性能测试
python -m pytest tests/performance/ -m performance --html=tests/reports/performance-report.html

# 运行带覆盖率的测试
python -m pytest tests/ --cov=apps --cov-report=html:tests/reports/coverage
```

## 测试报告

测试完成后会生成以下报告：

- **HTML报告**: `tests/reports/html-report.html`
- **UI测试报告**: `tests/reports/ui-report.html`
- **WebSocket测试报告**: `tests/reports/websocket-report.html`
- **性能测试报告**: `tests/reports/performance-report.html`
- **覆盖率报告**: `tests/reports/coverage/index.html`
- **JUnit XML**: `tests/reports/junit.xml`
- **总结报告**: `tests/reports/summary-report.md`

## 测试标记

- `ui`: UI测试
- `websocket`: WebSocket测试
- `performance`: 性能测试
- `integration`: 集成测试
- `smoke`: 冒烟测试
- `slow`: 慢速测试
- `regression`: 回归测试

## 最佳实践

1. **测试前准备**：
   - 确保Django服务器正在运行
   - 确保Redis服务正在运行（WebSocket测试需要）
   - 检查所有依赖是否已安装

2. **测试执行**：
   - 先运行冒烟测试确保基本功能正常
   - 然后运行集成测试
   - 最后运行性能测试

3. **测试维护**：
   - 定期更新测试用例
   - 保持测试数据的时效性
   - 及时修复失败的测试

4. **性能测试注意事项**：
   - 性能测试可能需要较长时间
   - 建议在测试环境中运行
   - 注意系统资源使用情况

## 故障排除

### 常见问题

1. **Django服务器未运行**
   ```bash
   python manage.py runserver
   ```

2. **Redis服务未运行**
   ```bash
   redis-server
   ```

3. **Playwright浏览器未安装**
   ```bash
   playwright install
   ```

4. **依赖缺失**
   ```bash
   pip install -r requirements.txt
   ```

### 调试技巧

1. **查看详细输出**：
   ```bash
   python -m pytest tests/ -v -s
   ```

2. **运行单个测试**：
   ```bash
   python -m pytest tests/ui/test_basic_ui.py::TestBasicUI::test_homepage_loads -v -s
   ```

3. **查看测试覆盖率**：
   ```bash
   python -m pytest tests/ --cov=apps --cov-report=term-missing
   ```

## 扩展测试框架

### 添加新的测试类型

1. 在`tests/`目录下创建新的测试目录
2. 创建`conftest.py`配置文件
3. 添加测试文件
4. 更新`pytest.ini`中的标记定义
5. 更新运行脚本

### 添加新的测试工具

1. 在`tests/test_utilities.py`中添加新的工具函数
2. 在相应的`conftest.py`中添加fixtures
3. 更新文档

## 贡献指南

1. 遵循现有的代码风格
2. 添加适当的测试用例
3. 更新相关文档
4. 确保所有测试通过
5. 提交前运行完整的测试套件
