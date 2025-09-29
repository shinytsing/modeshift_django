# SSH密钥连接使用说明书

## 📋 概述

本说明介绍如何使用SSH密钥安全连接到服务器 `47.103.143.152`。SSH密钥认证比密码认证更安全，且支持动态IP访问。

## 🔑 密钥信息

- **服务器IP**: 47.103.143.152
- **用户名**: root
- **密钥文件**: ~/.ssh/server_key
- **密钥类型**: ED25519
- **公钥指纹**: SHA256:MUxaHTipaZs2pZk/3a8HhI+M8VPfDh54d4TO1O7CFzM

## 🚀 快速连接

### 方法1：直接使用密钥文件
```bash
ssh -i ~/.ssh/server_key root@47.103.143.152
```

### 方法2：配置SSH客户端（推荐）

#### 创建SSH配置文件
```bash
# 编辑SSH配置文件
nano ~/.ssh/config

# 添加以下内容：
Host myserver
    HostName 47.103.143.152
    User root
    IdentityFile ~/.ssh/server_key
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

#### 使用配置连接
```bash
# 直接使用别名连接
ssh myserver
```

## 🔧 常用命令

### 连接服务器
```bash
ssh myserver
```

### 执行远程命令
```bash
ssh myserver "ls -la"
ssh myserver "systemctl status nginx"
```

### 文件传输
```bash
# 上传文件到服务器
scp -i ~/.ssh/server_key local_file.txt root@47.103.143.152:/path/to/destination/

# 从服务器下载文件
scp -i ~/.ssh/server_key root@47.103.143.152:/path/to/file.txt ./local_destination/

# 使用别名传输
scp file.txt myserver:/path/to/destination/
```

### 目录同步
```bash
# 同步本地目录到服务器
rsync -avz -e "ssh -i ~/.ssh/server_key" ./local_dir/ root@47.103.143.152:/path/to/remote_dir/

# 使用别名同步
rsync -avz myserver:/path/to/remote_dir/ ./local_dir/
```

## 🛡️ 安全特性

### 已配置的安全措施
- ✅ **密钥认证**: 已启用，禁用密码登录
- ✅ **防火墙**: 已禁用（可根据需要重新配置）
- ✅ **SSH服务**: 运行正常

### 安全建议
1. **保护密钥文件**: 确保 `~/.ssh/server_key` 文件权限为 600
2. **定期更换密钥**: 建议每6个月更换一次密钥对
3. **监控登录日志**: 定期检查 `/var/log/auth.log`

## 🔄 密钥管理

### 检查密钥权限
```bash
ls -la ~/.ssh/server_key
# 应该显示: -rw------- 1 user user 411 date time ~/.ssh/server_key
```

### 修复权限
```bash
chmod 600 ~/.ssh/server_key
chmod 700 ~/.ssh/
```

### 生成新密钥（如需要）
```bash
# 生成新密钥对
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/server_key_new

# 上传新公钥到服务器
ssh-copy-id -i ~/.ssh/server_key_new.pub root@47.103.143.152
```

## 🌐 VPN使用

### 支持动态IP
- ✅ **VPN切换**: 支持随时切换VPN
- ✅ **IP变化**: 密钥认证不受IP变化影响
- ✅ **多地点**: 可在任何地点安全连接

### 使用步骤
1. 连接VPN
2. 直接使用 `ssh myserver` 连接
3. 无需重新配置密钥

## 📱 移动设备使用

### iOS (Termius, Prompt)
1. 导入密钥文件到应用
2. 配置连接：
   - Host: 47.103.143.152
   - User: root
   - Key: 选择导入的密钥

### Android (Termux, JuiceSSH)
```bash
# 在Termux中
cp /sdcard/server_key ~/.ssh/
chmod 600 ~/.ssh/server_key
ssh -i ~/.ssh/server_key root@47.103.143.152
```

## 🔍 故障排除

### 连接被拒绝
```bash
# 检查SSH服务状态
ssh myserver "systemctl status ssh"

# 检查防火墙状态
ssh myserver "iptables -L -n"
```

### 密钥认证失败
```bash
# 检查密钥权限
ls -la ~/.ssh/server_key

# 测试连接（详细输出）
ssh -v -i ~/.ssh/server_key root@47.103.143.152
```

### 权限问题
```bash
# 修复SSH目录权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/server_key
chmod 644 ~/.ssh/server_key.pub
```

## 📞 紧急情况

### 无法连接时的备选方案
1. **VNC连接**: 通过阿里云控制台VNC远程连接
2. **重置密钥**: 通过VNC重新配置SSH密钥
3. **恢复密码登录**: 临时启用密码认证

### 紧急VNC连接步骤
1. 登录阿里云控制台
2. 找到ECS实例 (47.103.143.152)
3. 点击"远程连接" → "VNC远程连接"
4. 用户名: root
5. 密码: GJc9d5&b5z

## 📝 配置文件示例

### ~/.ssh/config
```
Host myserver
    HostName 47.103.143.152
    User root
    IdentityFile ~/.ssh/server_key
    Port 22
    ServerAliveInterval 60
    ServerAliveCountMax 3
    Compression yes
    ControlMaster auto
    ControlPath ~/.ssh/master-%r@%h:%p
    ControlPersist 10m
```

## 🎯 最佳实践

1. **使用别名**: 配置SSH别名简化连接
2. **连接复用**: 使用ControlMaster复用连接
3. **定期备份**: 备份密钥文件到安全位置
4. **监控日志**: 定期检查服务器访问日志
5. **更新密钥**: 定期更换SSH密钥

---

## 📞 技术支持

如有问题，请检查：
1. 网络连接是否正常
2. 密钥文件权限是否正确
3. 服务器SSH服务是否运行
4. 防火墙规则是否正确

**配置日期**: 2025-09-19  
**服务器**: shenyiqing.xin (47.103.143.152)  
**维护者**: 系统管理员
