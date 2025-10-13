# 🚀 部署脚本总览

## 📋 服务器信息
- **服务器**: 47.103.143.152
- **域名**: shenyiqing.xin
- **用户**: root
- **密码**: GJc9d5&b5z

## 🛠️ 可用脚本

### 1. 连接测试
```bash
./test-server-connection.sh
```
- 测试到服务器的SSH连接
- 显示服务器基本信息
- 验证部署环境

### 2. 一键部署
```bash
./deploy-now.sh
```
- 最简单的部署方式
- 自动执行完整部署流程
- 适合快速部署

### 3. 完整部署
```bash
./deploy-server-venv.sh
```
- 详细的虚拟环境部署
- 包含完整的错误处理
- 适合生产环境部署

### 4. 状态检查
```bash
./check-server-status.sh
```
- 检查所有服务状态
- 显示健康检查结果
- 查看日志和资源使用

## 🔄 部署流程

### 步骤1: 测试连接
```bash
./test-server-connection.sh
```

### 步骤2: 执行部署
```bash
./deploy-now.sh
```

### 步骤3: 检查状态
```bash
./check-server-status.sh
```

## 🌐 部署后访问

- **主站**: https://shenyiqing.xin
- **管理后台**: https://shenyiqing.xin/admin/
- **健康检查**: https://shenyiqing.xin/health/
- **服务器直连**: http://47.103.143.152:8000

## 👤 默认账号

- **用户名**: admin
- **密码**: admin123

## 📝 重要文件

- **部署指南**: `SERVER_DEPLOYMENT_GUIDE.md`
- **环境配置**: `env.production`
- **Docker配置**: `docker-compose.yml`
- **Nginx配置**: `nginx.production.conf`

## 🚨 注意事项

1. **首次部署前**请先运行连接测试
2. **部署过程中**请保持网络连接稳定
3. **部署完成后**请检查服务状态
4. **生产环境**请修改默认密码和密钥

## 🔧 故障排除

如果部署失败，请：
1. 检查服务器连接: `./test-server-connection.sh`
2. 查看部署日志: `/var/log/deploy.log`
3. 检查服务状态: `./check-server-status.sh`
4. 查看错误日志: `/var/log/gunicorn_error.log`

---

**准备好部署了吗？运行 `./deploy-now.sh` 开始！** 🚀
