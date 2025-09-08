# 🚀 多种部署连接方法指南

## 📋 概述

本项目提供了多种部署连接方法，每种方法都有其特定的优势和适用场景。您可以根据网络环境、服务器配置和个人偏好选择最适合的部署方法。

## 🛠️ 可用的部署方法

### 1. **SSH直接连接部署** (`deploy-ssh-direct.sh`)

**适用场景**: 网络稳定，有SSH密钥或密码访问权限

**方法类型**:
- SSH密钥连接 (推荐)
- 密码连接
- expect自动输入密码

**使用方法**:
```bash
./deploy-ssh-direct.sh
```

**优势**:
- ✅ 直接连接，速度快
- ✅ 支持多种认证方式
- ✅ 实时反馈部署状态

### 2. **Docker容器部署** (`deploy-docker.sh`)

**适用场景**: 需要容器化部署，环境隔离要求高

**方法类型**:
- 本地Docker构建并推送
- 服务器端Docker构建
- Docker Hub推送部署
- Docker Swarm集群部署

**使用方法**:
```bash
./deploy-docker.sh
```

**优势**:
- ✅ 环境一致性
- ✅ 易于回滚
- ✅ 支持集群部署

### 3. **Webhook触发部署** (`deploy-webhook.py`)

**适用场景**: 需要自动化部署，支持GitHub Webhook

**方法类型**:
- SSH直接部署
- API调用部署
- GitHub Actions触发

**使用方法**:
```bash
python3 deploy-webhook.py
```

**优势**:
- ✅ 自动化程度高
- ✅ 支持多种触发方式
- ✅ 实时状态监控

### 4. **手动部署方法** (`deploy-manual.sh`)

**适用场景**: 网络不稳定，需要分步操作

**方法类型**:
- 本地构建后上传
- 使用rsync同步
- 使用scp传输
- 使用git clone
- 使用wget下载

**使用方法**:
```bash
./deploy-manual.sh
```

**优势**:
- ✅ 适应性强
- ✅ 支持断点续传
- ✅ 多种传输方式

### 5. **统一部署管理器** (`deploy-manager.sh`)

**适用场景**: 需要统一管理多种部署方法

**功能**:
- 部署方法选择
- 状态检查
- 部署回滚
- 混合部署策略

**使用方法**:
```bash
./deploy-manager.sh
```

**优势**:
- ✅ 统一管理界面
- ✅ 智能故障转移
- ✅ 完整的部署生命周期管理

## 🎯 推荐使用策略

### 根据网络环境选择

| 网络环境 | 推荐方法 | 备选方法 |
|---------|---------|---------|
| 稳定网络 | SSH直接连接 | Docker部署 |
| 不稳定网络 | 手动部署 | Webhook部署 |
| 企业内网 | Docker部署 | 手动部署 |
| 公网环境 | GitHub Actions | SSH直接连接 |

### 根据部署频率选择

| 部署频率 | 推荐方法 | 原因 |
|---------|---------|------|
| 频繁部署 | Webhook触发 | 自动化程度高 |
| 偶尔部署 | SSH直接连接 | 简单直接 |
| 批量部署 | Docker部署 | 环境一致性好 |
| 紧急部署 | 手动部署 | 灵活可控 |

## 🔧 配置要求

### 通用配置
- 服务器IP: `47.103.143.152`
- 用户名: `root`
- 部署路径: `/root/modeshift_django`
- 网站URL: `https://shenyiqing.xin`

### 方法特定配置

#### SSH部署
- SSH密钥或密码
- 网络连接稳定

#### Docker部署
- Docker和Docker Compose
- 足够的磁盘空间

#### Webhook部署
- Python 3.6+
- Flask库
- GitHub Token (可选)

#### 手动部署
- rsync, scp, wget等工具
- 足够的本地存储空间

## 🚀 快速开始

### 1. 选择部署方法
```bash
# 查看所有可用方法
ls -la deploy-*.sh deploy-*.py

# 使用统一管理器
./deploy-manager.sh
```

### 2. 检查依赖
```bash
# 检查SSH连接
ssh root@47.103.143.152 "echo 'SSH连接正常'"

# 检查Docker
docker --version

# 检查Python
python3 --version
```

### 3. 执行部署
```bash
# 方法1: SSH部署
./deploy-ssh-direct.sh

# 方法2: Docker部署
./deploy-docker.sh

# 方法3: 手动部署
./deploy-manual.sh
```

## 🔍 故障排除

### 常见问题

#### 1. SSH连接失败
```bash
# 检查SSH密钥
ssh-add -l

# 测试连接
ssh -v root@47.103.143.152
```

#### 2. Docker构建失败
```bash
# 检查Docker状态
docker info

# 清理Docker缓存
docker system prune -f
```

#### 3. 网络连接问题
```bash
# 检查网络连接
ping 47.103.143.152

# 检查DNS解析
nslookup github.com
```

### 日志查看
```bash
# 查看部署日志
tail -f logs/gunicorn_error.log

# 查看nginx日志
tail -f /var/log/nginx/error.log
```

## 📊 性能对比

| 方法 | 速度 | 稳定性 | 复杂度 | 自动化 |
|------|------|--------|--------|--------|
| SSH直接连接 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Docker部署 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Webhook触发 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 手动部署 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ |

## 🎉 总结

通过提供多种部署方法，您可以：

1. **根据环境选择最适合的方法**
2. **在一种方法失败时快速切换到其他方法**
3. **享受不同方法的优势**
4. **提高部署的成功率和效率**

建议从**统一部署管理器**开始，它会引导您选择最适合的部署方法。

---

**最后更新**: 2025年9月8日  
**版本**: 1.0.0
