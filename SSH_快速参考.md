# SSH密钥连接 - 快速参考

## 🚀 快速连接

```bash
# 方法1: 直接连接
ssh -i ~/.ssh/server_key root@47.103.143.152

# 方法2: 使用别名（推荐）
ssh myserver
```

## ⚙️ SSH配置 (~/.ssh/config)

```
Host myserver
    HostName 47.103.143.152
    User root
    IdentityFile ~/.ssh/server_key
    Port 22
```

## 📁 文件传输

```bash
# 上传文件
scp -i ~/.ssh/server_key file.txt root@47.103.143.152:/path/

# 下载文件
scp -i ~/.ssh/server_key root@47.103.143.152:/path/file.txt ./

# 使用别名
scp file.txt myserver:/path/
```

## 🔧 常用命令

```bash
# 检查服务状态
ssh myserver "systemctl status nginx"

# 执行远程命令
ssh myserver "ls -la /var/log/"

# 重启服务
ssh myserver "systemctl restart gunicorn"
```

## 🛡️ 安全信息

- **密钥文件**: ~/.ssh/server_key
- **服务器**: 47.103.143.152
- **用户**: root
- **认证**: 仅密钥认证（密码已禁用）

## 🔍 故障排除

```bash
# 检查连接
ssh -v myserver

# 修复权限
chmod 600 ~/.ssh/server_key
chmod 700 ~/.ssh/

# 检查服务
ssh myserver "systemctl status ssh"
```

## 🆘 紧急连接

如果SSH无法连接，使用VNC：
1. 阿里云控制台 → ECS实例
2. 远程连接 → VNC远程连接
3. 用户名: root
4. 密码: GJc9d5&b5z

---
**支持VPN切换IP，密钥认证不受IP变化影响**
