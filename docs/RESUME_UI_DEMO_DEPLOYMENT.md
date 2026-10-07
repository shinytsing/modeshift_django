# 简历 UI 自动化演示部署

入口：简历技能卡片 → 执行 UI 自动化 → POST /resume-3d/run-ui/。
执行固定的 qa/ui/test_authenticated_bmi_flow.py 中
test_user_registers_logs_in_and_calculates_bmi_through_the_visible_ui 用例，不接受访客指定脚本或命令。
它就是 testing-system.yml 和 vmware-deploy.yml 通过 qa/scripts/run_suite.py 收集的注册、登录、个人资料与 BMI UI 门禁用例。
简历入口的测试只验证下载、弹窗和执行入口，业务操作不再另写一套。

## 本机与线上

macOS 本机开发使用可见 Chrome；线上使用服务器端无头 Chromium。
访客浏览器只展示结果，不会被 Playwright 直接接管。
当前返回真实 pytest 文本日志，截图/录像展示尚未接入。

## 安装和配置

在运行 Django 的同一 Python 环境安装：

```bash
python -m pip install -r qa/requirements.txt
python -m playwright install --with-deps chromium
```

浏览器安装必须对服务运行用户可见，或在容器中设置统一 PLAYWRIGHT_BROWSERS_PATH。
仓库当前 Docker 配置需另行接入 qa 依赖及 Playwright 浏览器，单独安装系统 chromium 不等于安装 Playwright 期望的版本。

配置环境变量：

```text
RESUME_UI_DEMO_ENABLED=1
RESUME_UI_DEMO_BASE_URL=http://127.0.0.1:8000
```

BASE_URL 必须指向部署后的演示实例，由运维固定配置；反向代理的公网端口不一定等于 Django 的内部监听端口。
此用例每次会创建 qa-e2e- 开头的测试账号，现有用例不自动删除账号。请使用独立演示实例并定期清理 QA 数据。
若目标不是本机地址，还需明确设置 QA_ALLOW_AUTH_MUTATIONS=1；未允许造数时入口直接拒绝执行，不能把跳过用例显示成通过。
应用与代理请求超时需超过 90 秒执行上限，并保留接收浏览器页面请求的并发容量，不能用唯一同步 worker 阻塞全部服务。

## 当前范围

当前接口同步等待结果，锁仅防止同一 Python 进程内并发启动。小范围演示可使用单进程多线程服务；公网多人访问前应接入任务队列、跨进程互斥、频率限制与结果查询，避免堆积浏览器进程。
此改动只增加运行配置支持，没有实际修改生产容器或部署线上服务。
