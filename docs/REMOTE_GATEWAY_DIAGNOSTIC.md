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
