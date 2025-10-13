# 🧪 全栈可交互自动化测试系统

## 📋 项目概述

这是一个完整的全栈自动化测试系统，专为 Django 项目（shenyiqing.xin）设计。系统支持功能、接口、安全、性能、UI 五类测试，提供实时进度显示和可视化报告。

## 🎯 核心特性

- ✅ **五类测试支持**: 功能、接口、安全、性能、UI 自动化测试
- 🔄 **实时进度显示**: WebSocket 实时推送测试执行进度
- 📊 **可视化仪表盘**: React + Chart.js 展示测试结果统计
- 🚀 **一键触发测试**: 前端按钮触发后端测试执行
- 📈 **历史报告管理**: 查看历史测试记录和趋势
- 🌐 **GitHub Pages 部署**: 自动部署到 GitHub Pages 展示

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django REST Framework
- **语言**: Python 3.9+
- **测试**: pytest + allure
- **实时通信**: WebSocket (Django Channels)
- **任务队列**: Celery (可选)

### 前端技术栈
- **框架**: React 18
- **样式**: TailwindCSS
- **图表**: Chart.js
- **动画**: Framer Motion
- **HTTP客户端**: Axios
- **实时通信**: Socket.io-client

## 📂 项目结构

```
testing_system/
├── backend/                    # Django 后端
│   ├── manage.py
│   ├── requirements.txt
│   ├── testing_system/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/                    # API 应用
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   └── consumers.py        # WebSocket 消费者
│   ├── core/                   # 核心功能
│   │   ├── tasks.py           # 测试任务执行
│   │   ├── utils.py           # 工具函数
│   │   └── models.py          # 数据模型
│   └── static/                 # 静态文件
├── frontend/                   # React 前端
│   ├── package.json
│   ├── src/
│   │   ├── components/         # 组件
│   │   │   ├── Dashboard.jsx
│   │   │   ├── RunTest.jsx
│   │   │   ├── ReportViewer.jsx
│   │   │   └── History.jsx
│   │   ├── pages/             # 页面
│   │   │   ├── Home.jsx
│   │   │   └── App.jsx
│   │   ├── api/               # API 调用
│   │   │   └── client.js
│   │   └── utils/             # 工具函数
│   └── public/
├── tests/                      # 测试用例
│   ├── functional/             # 功能测试
│   ├── api/                    # 接口测试
│   ├── performance/            # 性能测试
│   ├── security/               # 安全测试
│   ├── ui/                     # UI 测试
│   └── reports/               # 测试报告
│       ├── allure-results/
│       ├── allure-report/
│       ├── screenshots/
│       └── logs/
├── .github/                    # GitHub Actions
│   └── workflows/
│       ├── test.yml
│       └── deploy.yml
├── docs/                       # 文档
│   ├── api.md
│   ├── deployment.md
│   └── dashboard.png
└── docker-compose.yml          # Docker 配置
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo>
cd testing_system

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 2. 启动服务

```bash
# 启动后端服务
cd backend
python manage.py runserver 8000

# 启动前端服务
cd frontend
npm start
```

### 3. 访问系统

- **前端仪表盘**: http://localhost:3000
- **后端API**: http://localhost:8000/api/
- **测试报告**: http://localhost:8000/reports/

## 📊 功能演示

### 测试执行流程

1. **启动测试**: 点击"立即执行测试"按钮
2. **实时进度**: 查看测试执行进度条
3. **结果展示**: 查看测试结果统计图表
4. **详细报告**: 查看 Allure HTML 报告

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/tests/run` | POST | 启动测试 |
| `/api/tests/status` | GET | 获取测试状态 |
| `/api/tests/result` | GET | 获取测试结果 |
| `/api/tests/history` | GET | 获取历史记录 |
| `/api/tests/report` | GET | 获取报告路径 |

## 🎯 面试亮点

### 技术亮点
- **全栈开发**: Django + React 完整技术栈
- **实时通信**: WebSocket 实现实时进度推送
- **测试架构**: 五类测试完整覆盖
- **可视化**: Chart.js 数据可视化
- **自动化**: GitHub Actions CI/CD

### 业务价值
- **效率提升**: 一键执行所有测试
- **质量保证**: 全面的测试覆盖
- **可视化**: 直观的测试结果展示
- **可扩展**: 模块化设计，易于扩展

## 📈 部署说明

### GitHub Pages 部署

```bash
# 构建前端
cd frontend
npm run build

# 部署到 GitHub Pages
npm install -g gh-pages
gh-pages -d build
```

### Docker 部署

```bash
# 使用 Docker Compose
docker-compose up -d
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

---

**项目作者**: 高级测试架构师  
**最后更新**: 2024年12月29日  
**版本**: v1.0