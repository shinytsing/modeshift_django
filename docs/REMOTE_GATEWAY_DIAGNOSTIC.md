# Remote Gateway / Xiaohongshu MCP diagnostic handoff

更新时间：2026-10-24（Asia/Shanghai）

## 现象

线上 `https://shenyiqing.xyz` 使用小红书短链 `https://xhslink.cn/o/74T7wCY5jR4` 查询主页时，页面提示：

> 服务返回的数据无法解析

同一个短链在本地环境可以解析。这个提示通常表示上游返回了 HTML、空响应或网关错误，而不是合法 JSON；需要看线上 Web 和 MCP 的运行时日志确认实际状态码和 Content-Type。

## 已确认

- GitHub 部署提交：`7bbbc91d33fcea46f5933157171bd6f52d9ee052`
- 部署运行：`40065096056`
- 该次部署结果：成功
- 部署时确认 `docker-xiaohongshu-mcp-1` 为 Healthy，`creator_watch` 已启动
- 公网 `/health/` 返回 HTTP 200
- 本地同短链解析成功；本地 MCP `/health` 返回 healthy
- 线上运行时请求日志尚未取得，因为 SSH 主机指纹发生变化，客户端安全校验拒绝连接

## SSH 指纹变更

本机旧记录：

```text
SHA256:vRg0L4fGWzuK2W3EOUVIkQx8twTU+yvA9ZjLOpKJeCE
```

当前服务器公开的 ED25519 指纹：

```text
SHA256:VUlFIvvYzzdG4d5m9mu2s+EziCKxMQbbPzTUQIBdfNI
```

必须先在服务器控制台或可信管理渠道确认新指纹属于目标服务器，再更新客户端 `known_hosts`。不要使用 `StrictHostKeyChecking=no` 绕过校验。

服务器控制台核验命令：

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
```

## 远程机器检查清单

在服务器上执行，不要把 Cookie、Token 或私钥写入日志：

```bash
docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'
docker compose ps
docker compose logs --tail=200 web
docker compose logs --tail=200 xiaohongshu-mcp
curl -i --max-time 10 http://127.0.0.1:18060/health/
curl -i --max-time 10 https://shenyiqing.xyz/health/
```

重点确认：

1. MCP 容器是否仍为 healthy，端口是否监听；
2. MCP 的登录状态是否过期；`/health` 正常不等于小红书会话有效；
3. profile 请求实际返回的 HTTP 状态码、Content-Type 和前 200 个响应字符；
4. Nginx/Django 是否在 MCP 未登录或上游 502 时返回了 HTML，导致前端 JSON 解析失败；
5. 服务器磁盘空间是否不足（上次部署时使用率约 90%）。

## 当前判断

最可能是线上 MCP 的小红书浏览器会话已过期，或网关在 MCP 返回错误时把 HTML 错误页传给了前端。需要运行时日志才能定案；不要只根据部署成功或 `/health` 结果判断 profile 链路正常。

## 安全边界

本文不包含任何登录 Cookie、CSRF 值、MCP Token、邮箱密码或 SSH 私钥。处理完成后应轮换曾经在聊天或终端中暴露过的会话 Cookie。


## 2026-10-25：请远程 GPT 配置虚拟机 SSH 连接

### 最新事实（覆盖前文旧的阻塞描述）

- 用户已确认信任公网主机 `47.103.143.152` 的新指纹，本机 known_hosts 已更新。
- 对该公网地址的 SSH 已通过主机校验，但现有密钥连接 root、ubuntu、shenshen 都返回 `Permission denied (publickey)`。
- 不能据此认定 `47.103.143.152` 就是 VMware 虚拟机；其主机指纹也不能用来验证另一台虚拟机。
- GitHub Runner `vmware-ubuntu` 刚检查为 online、空闲，标签为 self-hosted / Linux / X64 / vmware。
- 历史虚拟机地址 `192.168.27.128` 从 Mac 访问 SSH 22 和 HTTP 8080 都超时，当前地址待确认。
- 部署目录：`/home/shenshen/modeshift_django`。最近一次部署运行 `40066439568` 成功，公网 `/health/` 本次检查正常。
- 用户明确表示已完成小红书登录，仍遇到“服务返回的数据无法解析”。未取得运行时证据，不能直接归因为登录过期；应记录请求状态码、Content-Type、耗时、错误类型并关联 Web/MCP/Nginx 日志。

### 请在实际 VMware 虚拟机上核对并反馈

```bash
hostname
whoami
hostname -I
ip -brief address
ss -ltn | grep ':22 '
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
```

反馈下面四项即可（不提供密码、私钥、Cookie 或 Token）：

| 字段 | 远程填写 |
| --- | --- |
| Mac 实际可达的主机地址 / VPN 地址 | 待确认 |
| SSH 端口 | 待确认 |
| SSH 用户名 | 待确认 |
| 该主机 ED25519 公钥指纹 | 待确认 |

局域网地址只有在双方网络互通时才可用。若不互通，先确认现有 VPN 或端口映射，不要默认开放公网 root/密码登录，也不要把 SSH 私钥提交到仓库。

### 授权此 Mac 的公钥

仅在确认是目标虚拟机后，以准备授权的普通部署用户执行；不要在错误账号下执行：

```bash
install -d -m 700 "$HOME/.ssh"
touch "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"
```

将下面完整一行加入该用户的 `~/.ssh/authorized_keys`，已有相同 key 时不要重复加入。这是可公开的公钥，不是私钥：

```text
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDznHxX4i3kiJTSErx298Uj5O1U6S6ZuSBmivLSYfTUooYd4pS4QtReCv3TfAeB3IYshOVKq04HdTEShR1HffoSmxK/2C8jnVIwWEza+KmFITAEsYJmjCiVOv0FMhJsyV5gtX01FoELY8TNjtMwGisWTcDOH0r+mPS75cVDKvdKQUdB4QrafRKIGzt/B6rOx96gvzdTwR0ooGXKqOmrRcgVghAFXEOpMk8DWKM/jviMCOIPor4BUFJTKtfhhK2z8VhCtmFHkUcBQtg5dVv8PADtShEvLsTnFZqxRWYvmpdKfET9ybVEhnFJX755DjWvCpOQ3t00dSJhzU5SHSXRfspZnLG13fU5R6v9y+UClrmjnKGmvU5ycTXZ6ejTk0L086gW2gehBXLRlkYuZleo0aQ9WelWd7ChBAfHoDzwsmHhPRf/6EniyG2A78cIKQ1tU3fj4y7EpDW4d4Q1ljSA06TW9Hz3cFaIpNlAEnEe8wj7SV5NirVoNXuY37jizowklmpXR8lBrNFmzoyeEGp5V96S2TVbbtrC9J2Ti+s715U74fsqI+YZNZsDyMnrJElmGB+RBTHuj65DreSxZ0ChkG0GpN7MTkNGSvGjye1V6mNYyU9Ex+3KMutCJB1S9KJO0Rwi/YVfx3vxmnTcFz5xMqh0HhAFBIEwifjdfWJESCwkYw== modeshift-mac-debug
```

公钥 SHA256 指纹（与服务器的主机指纹用途不同）：

```text
SHA256:RTj/fZr8z9DPB4LLSxJxKQQxjeFDJMEjvGGTVlYqLKA
```

完成后在仓库文档中反馈上述连接信息和授权结果，本机即可使用现有私钥连接并读取运行时日志。无需新增管理员账号、上传私钥、关闭主机校验或重建应用。

### 应用日志检查注意

MCP 在 Compose 私网中，宿主机未必发布 18060；宿主机访问该端口失败不等于 MCP 未启动。先执行 `docker ps` 确认真实容器名，再使用容器内 health 检查或从 web 容器调用已配置的 MCP 地址。不要打印环境变量全集、Cookie 文件或完整带签名的请求链接。

上次部署日志（10 月 24 日）显示根盘已用 93%、可用约 5.8 GB；这是历史数据，请重新核对，不要直接清理数据库或持久化卷。

## 2026-10-25 18:44 CST：虚拟机侧实测反馈

用户已明确授权安装本文 Mac 公钥，并将以下连接与诊断信息提交到此仓库。

- 实际主机：shenshen-VMware-Virtual-Platform。
- SSH：shenshen@192.168.27.132，端口 22；ens33 为 192.168.27.132/24，VMware NAT 默认网关为 192.168.27.2。Windows 宿主机已成功登录。
- VM ED25519 主机公钥指纹：SHA256:CvKYaiePUs28jP0z3PRCniGx3uRT4lADza4RuZmx8yk。
- Mac 公钥 modeshift-mac-debug 已安装到 /home/shenshen/.ssh/authorized_keys；安装前后均核验 SHA256:RTj/fZr8z9DPB4LLSxJxKQQxjeFDJMEjvGGTVlYqLKA。所有者 shenshen，目录权限 700，文件权限 600；未读取私钥。
- Mac 跨网连接未验证：虚拟机无运行中的 Tailscale / ZeroTier，未证实 47.103.143.152 与该 VM 的映射关系。需先确保 Mac 有到此 NAT 私网的路由、VPN 或已验证跳板，不能将公钥安装视为跨网已连通。
- 同网或已有私网路由时，可使用 Mac 对应私钥连接 ssh shenshen@192.168.27.132，并核验上述 VM 主机指纹；不要使用公网主机指纹核验此 VM。
- 当前 docker-web-1、docker-creator_watch-1、docker-xiaohongshu-mcp-1、PostgreSQL、Redis 均 healthy。Web/worker 镜像标签为 main，标签本身不足以确定构建提交。
- VM 本机 http://127.0.0.1:8000/health/ 返回 HTTP 200、application/json，耗时约 0.012 秒。
- Nginx 曾重启并报 host not found in upstream "web:8000"：其 modeshift_network 与 Web 的 docker_default 分离。已接入 docker_default 并启动，从 Nginx 内请求 http://127.0.0.1/health/ 返回 healthy JSON。后续部署文件应保持同网，避免重建复发。
- VM 请求公网 https://shenyiqing.xyz/health/ 本次 10 秒超时，外部客户端可达性未验证。
- 最近一小时未检出可关联的新 profile 请求，本次未重现短链问题，不能据此归因为登录过期；后续仍需关联状态码、Content-Type、耗时与 Web/MCP/Nginx 日志，禁止输出 Cookie、Token 或完整签名链接。
- 根盘实测总量 79 GB、已用 69 GB、可用 5.8 GB、使用率 93%；未清理数据库或持久化卷。


## 2026-10-25：Mac 到虚拟机的网络实测及下一步交接

用户要求将本次网络诊断发到 Git，交给 Windows / 虚拟机侧 GPT 继续配置。

### Mac 侧最新实测

- Mac 活跃 IPv4：`192.168.0.100`，网卡 `en0`，默认网关 `192.168.0.1`。
- `route -n get 192.168.27.132` 显示流量走 `en0 -> 192.168.0.1`，没有到 VMware NAT 网段的专用路由。
- 系统当前路由表没有到 `192.168.27.0/24` 的 VPN 路由；未确认现有 VPN 提供设备间私网互通。
- 到 `192.168.27.132:22` 的 TCP / SSH 连接超时；到 `192.168.27.132:8000` 的 HTTP 连接也超时。尚未进入 SSH 身份认证阶段，不能归因为公钥未授权。
- 同一 Wi-Fi 或使用同一 VPN 产品，不自动意味着 Mac 可以访问 Windows 内部 VMware NAT 网络。
- 局域网邻居 `192.168.0.102` 的 22、2222 端口拒绝连接；尚未确认该地址是否属于 Windows 宿主机，不要直接当作宿主机地址配置。

### 请 Windows 侧 GPT 处理

1. 在实际 Windows 宿主机上执行 `ipconfig`，确认活跃 Wi-Fi / 以太网的 IPv4 地址（不要使用 VMware VMnet 网卡地址），反馈该地址。
2. 核对 Windows 能继续通过 `shenshen@192.168.27.132:22` 访问目标虚拟机。
3. 优先复用已有可用的 VPN 路由或 SSH 转发；如果确实没有，配置 Windows 局域网端口转发：`Windows实际LAN地址:2222 -> 192.168.27.132:22`。先检查端口占用及现有转发，不覆盖其他规则。
4. 可使用 VMware NAT 端口转发，或 Windows 自带 `netsh interface portproxy`；只选一种，不同时叠加。使用 portproxy 时核对 IP Helper 服务是否运行。
5. 只绑定 Windows 实际局域网地址，防火墙入站仅允许 Mac 的 `192.168.0.100` 访问 TCP 2222；不要关闭整个防火墙，不要配置路由器公网映射，也不要开放 root / 密码登录。
6. 完成后从 Mac 验证端口、核对下述虚拟机指纹，再进行公钥认证。转发不会改变 SSH 服务端主机密钥，不要使用公网服务器指纹代替。

端口转发的目标 VM 主机指纹（来自上一节远程核验）：

```text
SHA256:CvKYaiePUs28jP0z3PRCniGx3uRT4lADza4RuZmx8yk
```

Mac 最终连接形式（Windows 实际地址待远程反馈）：

```bash
ssh -o IdentitiesOnly=yes -i ~/.ssh/qatoolbox_deploy -p 2222 shenshen@<Windows实际LAN地址>
```

### 请在本文反馈结果

- Windows 实际 LAN IPv4：待填写
- 端口转发方式、监听地址与端口：待填写
- 转发目标：`192.168.27.132:22`（配置时重新确认 VM 地址未变化）
- 防火墙来源限制：待填写
- Windows 到 VM SSH 结果：待填写
- Mac 到转发端口及 SSH 结果：需 Mac 实测后填写，不能仅凭转发创建成功就写已连通

本次 Mac 侧仅做只读网络诊断，未修改本机路由、VPN、Windows 防火墙或虚拟机网络模式。VMware NAT 目标 IP、Mac 源 IP 和 Windows LAN IP 如因 DHCP 改变，应相应核对规则，不要为方便直接放开所有来源。


## 2026-10-25：统一启动的已验证修复（替代前文临时方案）

Mac 已通过 Windows `192.168.0.103:2222` 成功连接 VMware，主机指纹与前述 VM 指纹一致。

反复启动异常的根因：systemd 使用 `modeshift_deploy/.env.vm`，GitHub 发布使用
`modeshift_django/.env`，Worker 使用独立 runtime JSON，导致镜像、凭据、网络互相覆盖。
现在生产统一为 `/home/shenshen/modeshift_django/.env`、Compose 项目 `docker`、网络
`modeshift_network`、入口 `scripts/start-production-stack.sh start`。

- Web/Worker 共享同一镜像、环境变量和媒体卷。
- GitHub 发布调用共享入口；开机服务 `modeshift-project.service` 也已覆盖为同一入口。
- 旧 `.env.vm`、独立 Worker runtime JSON 仅保留作备份，不再启动它们。
- 已实测共享入口重复启动及 systemd restart 成功，六个核心容器 healthy。
- Web/Worker 实际镜像和环境完全一致，唯一 Worker/Beat 返回 pong；原有数据库、Redis、媒体和 MCP Cookie 卷名称均未改变。
- Nginx 的 8080 健康请求已返回正常 JSON，不再使用旧 Web IP。
- 配置回归测试 7 项通过；详细入口和 systemd 配置见 `docs/VMWARE_SINGLE_HOST_DEPLOYMENT.md` 最新章节。
- 迁移前的私有备份位于服务器 `/home/shenshen/modeshift_django/.startup-unification-backup-20261025-192203`，不要上传备份中的凭据。

尚未重启整台虚拟机，也未验证定时邮件真实送达；不要把服务重启验证当作这两项的证据。
磁盘空间仍需单独处理，本次未清理数据或持久化卷。


## 2026-10-25：磁盘告警处理与部署保护

现场根盘约 98%、仅剩约 2 GiB。Docker 旧镜像和构建缓存是主要占用，业务卷合计约 510 MB。
已保留所有容器引用的镜像、最近两个版本和回滚记录，清理无容器引用的更旧 ModeShift SHA 镜像及未用构建缓存。
清理后 `df -h /` 约 70%、可用约 23 GiB，应用内 `disk_usage` 约 66%（文件系统预留空间导致两者口径不同）。
Web、Worker、Nginx、PostgreSQL、Redis 和 MCP 仍全部 healthy；Worker 监控返回 up。
数据库、Redis、媒体文件、MCP Cookie 和私有配置未清理。

部署已增加 `scripts/maintenance/prepare_docker_disk.py`：Web/MCP 构建前、部署前和部署成功后共用磁盘门禁。
不足 8 GiB 时仅按明确的保留规则回收镜像/缓存；清理后仍不足就失败，不继续写满根盘。
`docs/VMWARE_SINGLE_HOST_DEPLOYMENT.md` 已记录统一启动入口、systemd 配置、空间门禁及手动维护命令。
清理缓存后下一次构建会重新生成缓存，可能变慢。不能将这次容量记录当作长期实时数值。
