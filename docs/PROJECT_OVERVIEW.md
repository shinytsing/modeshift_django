# Modeshift 项目总览

更新时间：2026-10-29（Asia/Shanghai）

## 总体架构

Windows 宿主机运行 VMware Ubuntu；Ubuntu 虚拟机运行项目服务、构建环境和 GitHub self-hosted Runner。Windows 负责保持虚拟机运行、提供 SSH 转发和管理虚拟机；Ubuntu 负责运行应用与部署任务。

## 项目与服务

- Git 仓库：`shinytsing/modeshift_django`
- Web：Django 应用，公网地址为 `https://shenyiqing.xyz/`
- 反向代理：Nginx
- 数据库：PostgreSQL
- 缓存与队列：Redis
- 小红书服务：xiaohongshu MCP
- 定时任务：`creator_watch`
- CI/CD：GitHub Actions，self-hosted Runner 名称为 `vmware-ubuntu`

小红书相关功能包括短链解析、用户资料读取、二维码登录和邮件通知。MCP 登录状态与运行日志保存在虚拟机环境中。

## 虚拟机连接

- 用户：`shenshen`
- 虚拟机地址：`192.168.27.132`
- SSH 端口：`22`
- Windows 宿主机 WLAN 地址：`192.168.0.103`
- SSH 转发：`192.168.0.103:2222 -> 192.168.27.132:22`

Mac 通过 Windows 转发连接：

```bash
ssh -p 2222 shenshen@192.168.0.103
```

如果 Mac 与 VMware NAT 网段已有路由，也可以直连：

```bash
ssh shenshen@192.168.27.132
```

## 当前运行状态

- 虚拟机 SSH 22 端口可达。
- Windows 2222 转发已恢复监听。
- Windows 总内存约 15.8 GB，可用内存约 0.8 GB。
- `vmware-vmx` 约占用 5.7 GB 内存；内存紧张时会影响构建、MCP、定时任务和网页响应。
- 降低虚拟机内存需要先关闭虚拟机，再在 VMware 设置中调整。

## 运维原则

1. 先确认虚拟机地址和 SSH 指纹，再连接或部署。
2. 构建失败时先检查 Runner、磁盘空间、内存和容器状态。
3. 小红书接口失败时同时查看 Web、Nginx 和 MCP 日志，并记录状态码、Content-Type 与耗时。
4. 不把密码、Cookie、Token、私钥写入 Git 或日志。
