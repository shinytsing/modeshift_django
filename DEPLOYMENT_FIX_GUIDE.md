# 部署问题修复指南

## 问题概述

在最近的部署过程中遇到了以下问题：

1. **GitHub连接失败** - 无法连接到 `github.com:443`
2. **502 Bad Gateway错误** - nginx无法连接到Django应用
3. **部署脚本健壮性不足** - 网络问题时继续执行导致问题

## 解决方案

### 1. 健壮部署脚本 (`deploy-robust.sh`)

这是一个改进的部署脚本，具有以下特性：

- ✅ **网络连接检查** - 部署前检查网络连接
- ✅ **智能代码更新** - GitHub连接失败时使用本地代码
- ✅ **服务状态验证** - 确保服务正常启动
- ✅ **健康检查** - 部署后验证服务可用性
- ✅ **错误处理** - 完善的错误处理和日志记录

**使用方法：**
```bash
./deploy-robust.sh
```

### 2. 502错误修复工具 (`fix-502-error.sh`)

专门用于诊断和修复502错误的工具：

**诊断502错误：**
```bash
./fix-502-error.sh diagnose
```

**完整修复：**
```bash
./fix-502-error.sh fix
```

**快速修复：**
```bash
./fix-502-error.sh quick
```

### 3. 改进的GitHub Actions工作流

新的工作流文件 `.github/workflows/robust-deploy.yml` 包含：

- ✅ **网络连接检查** - 部署前验证网络连接
- ✅ **代码质量检查** - 完整的代码质量验证
- ✅ **健壮部署流程** - 处理网络连接问题
- ✅ **部署后测试** - 验证服务功能
- ✅ **状态通知** - 部署结果通知

## 立即修复当前问题

### 步骤1：诊断问题
```bash
# 在服务器上执行
./fix-502-error.sh diagnose
```

### 步骤2：修复502错误
```bash
# 完整修复
./fix-502-error.sh fix

# 或者快速修复
./fix-502-error.sh quick
```

### 步骤3：验证修复结果
```bash
# 检查服务状态
curl -I https://shenyiqing.xin/health/

# 检查首页
curl -I https://shenyiqing.xin/
```

## 预防措施

### 1. 使用健壮部署脚本
```bash
# 替换原有的部署脚本
./deploy-robust.sh
```

### 2. 定期健康检查
```bash
# 创建定期健康检查脚本
cat > health-check.sh << 'EOF'
#!/bin/bash
if ! curl -f https://shenyiqing.xin/health/ > /dev/null 2>&1; then
    echo "健康检查失败，尝试修复..."
    ./fix-502-error.sh quick
fi
EOF

chmod +x health-check.sh
```

### 3. 监控和日志
```bash
# 查看服务日志
tail -f logs/gunicorn_error.log

# 查看nginx日志
tail -f /var/log/nginx/error.log

# 检查进程状态
ps aux | grep gunicorn
```

## 常见问题解决

### Q1: GitHub连接失败
**原因：** 网络限制、DNS问题或防火墙
**解决：** 使用本地代码继续部署，或配置代理

### Q2: 502 Bad Gateway
**原因：** Django应用未启动或端口未监听
**解决：** 使用 `fix-502-error.sh` 诊断和修复

### Q3: 服务启动失败
**原因：** 依赖问题、配置错误或端口冲突
**解决：** 检查日志，重新安装依赖，重启服务

### Q4: 健康检查失败
**原因：** 服务未完全启动或配置问题
**解决：** 增加等待时间，检查服务状态

## 部署最佳实践

1. **部署前检查**
   - 验证网络连接
   - 检查磁盘空间
   - 确认服务状态

2. **部署过程**
   - 使用健壮部署脚本
   - 监控部署日志
   - 验证每个步骤

3. **部署后验证**
   - 执行健康检查
   - 测试核心功能
   - 监控服务状态

4. **回滚准备**
   - 备份当前版本
   - 准备回滚脚本
   - 记录部署状态

## 联系支持

如果问题仍然存在，请提供以下信息：

1. 错误日志 (`logs/gunicorn_error.log`)
2. nginx错误日志 (`/var/log/nginx/error.log`)
3. 服务状态 (`ps aux | grep gunicorn`)
4. 网络连接测试结果

---

**最后更新：** 2025年9月8日
**版本：** 1.0.0
