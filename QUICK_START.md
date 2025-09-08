# 🚀 一键部署快速开始

## 🎯 最简单的部署方式

### 方式一：GitHub Actions（推荐）

1. **配置Secrets**（一次性设置）
   ```
   SERVER_HOST: 47.103.143.152
   SERVER_USER: root
   SERVER_SSH_KEY: 你的SSH私钥
   DEPLOY_PATH: /root/modeshift_django
   WEB_URL: https://shenyinqing.xin
   API_URL: https://shenyinqing.xin
   ```

2. **推送代码自动部署**
   ```bash
   git push origin main
   ```

3. **查看部署结果**
   - 访问：https://github.com/shinytsing/modeshift_django/actions
   - 网站：https://shenyinqing.xin

### 方式二：本地脚本部署

1. **设置环境变量**
   ```bash
   export HOST="47.103.143.152"
   export USERNAME="root"
   export SSH_KEY="你的SSH私钥"
   export DEPLOY_PATH="/root/modeshift_django"
   export WEB_URL="https://shenyinqing.xin"
   export API_URL="https://shenyinqing.xin"
   ```

2. **执行部署**
   ```bash
   ./deploy.sh traditional
   ```

3. **测试部署**
   ```bash
   ./test-deployment.sh
   ```

## 🐳 Docker部署（高级）

1. **使用Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **查看服务状态**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

## 📊 部署方案对比

| 方案 | 速度 | 稳定性 | 复杂度 | 推荐度 |
|------|------|--------|--------|--------|
| GitHub Actions | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 本地脚本 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Docker | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🔍 健康检测

所有部署方案都包含智能健康检测：

- ✅ 首页访问测试
- ✅ 管理后台测试  
- ✅ 静态文件测试
- ✅ API接口测试
- ✅ 性能分析
- ✅ SSL证书检测

## 🛠️ 故障排除

### 常见问题

1. **SSH连接失败**
   ```bash
   # 检查SSH密钥
   ssh-keygen -l -f ~/.ssh/id_rsa
   ```

2. **部署超时**
   - 检查网络连接
   - 增加超时时间
   - 使用本地脚本部署

3. **服务启动失败**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep :8000
   ```

## 📞 技术支持

- 📖 详细文档：`DEPLOYMENT_GUIDE.md`
- 🧪 测试脚本：`./test-deployment.sh`
- 🔧 部署脚本：`./deploy.sh`

---

🎉 **选择最适合你的部署方式，开始一键部署吧！**
