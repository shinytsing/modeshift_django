# ModeShift Django：单 VMware 虚拟机部署手册

记录日期：2026-10-04（北京时间）。本文描述当前实现，不把计划中的能力当作已实现能力。

本文档记录当前已经验证过的生产部署方案。后续维护部署时，优先阅读本文档和以下实际执行文件：

- `.github/workflows/vmware-deploy.yml`
- `scripts/deploy-public-vm.sh`
- `docker/docker-compose.prod.yml`
- `docker/Dockerfile.prod`

## 1. 当前部署结论

项目目前只有一台 VMware Ubuntu 虚拟机，因此采用“单机自托管 Runner + 本地 Docker 构建 + 本地 Compose 启动”的方案。

```text
提交 main
  ↓
GitHub Actions QA
  ↓
VMware Runner 拉取当前 commit
  ↓
VMware 本地 Docker 缓存构建
  ↓
VMware 本地 Compose 启动
  ↓
VMware 本机健康检查
  ↓
GitHub Actions 回传 success/failure + 邮件通知
```

构建和运行都在同一台 VMware 上，所以当前方案不再执行 GHCR 上传和下载。镜像只在 VMware 本地使用，tag 仍然使用 commit SHA，便于定位和回滚。

最近一次真实验证成功的流水线：

- Commit：`ef2ecefb0563973020f23a038a96ed5b867e5cd9`
- Run：[37199597201](https://github.com/shinytsing/modeshift_django/actions/runs/37199597201)

## 2. GitHub 到 VMware 的执行机制

这不是 SSH 连接。VMware 中安装并运行了 GitHub Actions self-hosted Runner。Runner 主动连接 GitHub，等待任务；GitHub 分配任务后，Runner 在 VMware 本地执行 shell 和 Docker 命令，然后把步骤日志、结果和最终 job 状态回传 GitHub。

当前的“回调”分为三层：

1. 每个 Actions step 将日志和结果回传 GitHub。
2. `deploy` job 根据 VMware 本机 `/health/` 检查决定成功或失败。
3. `notify` job 根据 `qa/build/deploy` 三个结果发送最终邮件。

## 3. 关键文件

| 文件 | 作用 |
| --- | --- |
| `.github/workflows/vmware-deploy.yml` | push 到 `main` 后的完整流水线 |
| `docker/Dockerfile.prod` | 生产镜像和多阶段依赖构建 |
| `docker/docker-compose.prod.yml` | PostgreSQL、Redis、Django、Nginx 编排 |
| `scripts/deploy-public-vm.sh` | VMware 上的本地镜像检查、启动、健康检查、回滚 |
| `docker/nginx.prod.conf` | 公网 Nginx 入口配置 |
| `docs/VMWARE_SINGLE_HOST_DEPLOYMENT.md` | 本部署手册 |

## 4. Workflow 结构

主文件为 `.github/workflows/vmware-deploy.yml`，触发条件是：

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

含义：

- 推送 `main` 自动部署。
- 其他分支不自动部署。
- GitHub Actions 页面可以手工执行 `workflow_dispatch`。

Workflow 使用并发控制：

```yaml
concurrency:
  group: vmware-deploy-main
  cancel-in-progress: true
```

同一时间只允许一个 main 部署。连续快速提交时，旧的未完成部署会取消，避免多个版本同时操作生产容器。

### 4.1 QA job

QA job 在 GitHub 托管的 `ubuntu-latest` 上运行，主要内容：

- Python 3.11
- Node 20
- Python 应用和 QA 依赖
- Playwright Chromium
- Black 格式检查
- `python qa/scripts/run_suite.py`
- 上传 `qa/artifacts/` 证据

QA 失败时，构建和部署 job 不会执行。

### 4.2 VMware 构建 job

构建 job 使用以下 Runner 标签：

```yaml
runs-on: [self-hosted, linux, x64, vmware]
```

执行步骤：

1. 在 VMware 的持久化 workspace checkout 当前 commit。
2. 通过 `docker build` 使用 VMware 本地 Docker layer cache。
3. 生成本地镜像：`ghcr.io/shinytsing/modeshift_django:<commit-sha>`。
4. 将 Compose、Nginx 和部署脚本作为 job output 传给 deploy job。

当前构建 job 明确不执行：

- `docker login ghcr.io`
- `docker push`
- 从 GHCR 拉取应用镜像

镜像名称带 `ghcr.io` 只是为了兼容现有 Compose 配置，不代表镜像已经上传到 GHCR。

### 4.3 VMware 部署 job

部署 job 也运行在同一个 VMware Runner 标签上，执行步骤：

1. 恢复本次构建对应的 Compose、Nginx 和部署脚本。
2. 检查 `QATOOLBOX_IMAGE` 是否存在于本机 Docker。
3. 本地镜像不存在时直接失败，不再绕路访问 GHCR。
4. 执行 `docker compose up -d --no-build db redis web nginx`。
5. 使用 `curl --noproxy '*'` 检查 `http://127.0.0.1:8080/health/`。
6. 检查容器内 DeepSeek Key 是否存在并进行 DeepSeek 预检。
7. 健康检查成功后，job 标记为 success。

## 5. VMware Runner 和网络

VMware 必须保持 Ubuntu、Docker daemon 和 GitHub Runner 在线。GitHub 仓库的 `Settings -> Actions -> Runners` 页面中，Runner 应显示 `Online`。

当前诊断得到的网络参数：

```text
VM IP：192.168.27.128
宿主机代理：192.168.27.1:7890
```

VMware job 使用：

```yaml
HTTP_PROXY: http://192.168.27.1:7890
HTTPS_PROXY: http://192.168.27.1:7890
ALL_PROXY: http://192.168.27.1:7890
```

不要同时添加小写的 `http_proxy`、`https_proxy`、`all_proxy`。GitHub Actions 环境变量名大小写不敏感，重复定义会使 workflow 解析失败。

### Dockerfile 中的代理

`docker/Dockerfile.prod` 的 builder、application、production 三个阶段都声明 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY` 构建参数。apt 和 pip 命令执行前会导出代理变量。

这是必要的，因为 VMware 当前使用 Docker Legacy Builder，只设置 workflow shell 环境不能保证 Dockerfile 每个阶段都能访问代理。

## 6. Docker Compose 服务和数据

生产编排文件是 `docker/docker-compose.prod.yml`：

| 服务 | 容器名 | 作用 |
| --- | --- | --- |
| `db` | `modeshift_postgres` | PostgreSQL |
| `redis` | `modeshift_redis` | Redis |
| `web` | `modeshift_web` | Django + Gunicorn |
| `nginx` | `modeshift_nginx` | 公网反向代理 |

持久化 volume：

- `postgres_data`
- `redis_data`
- `static_volume`
- `media_volume`

发布新版本只替换 web 镜像，不删除数据库、Redis、静态文件或媒体卷。

## 7. Secrets 和环境变量

以下敏感值应配置在 GitHub 仓库 `Settings -> Secrets and variables -> Actions`，不能提交到 Git：

| Secret | 用途 |
| --- | --- |
| `DEEPSEEK_API_KEY` | 注入生产 web 容器并做部署后预检 |
| `EMAIL_HOST`、`EMAIL_PORT` | SMTP 主机和端口 |
| `EMAIL_USE_TLS` | SMTP TLS 开关 |
| `EMAIL_HOST_USER`、`EMAIL_HOST_PASSWORD` | SMTP 认证 |
| `DEFAULT_FROM_EMAIL`、`NOTIFICATION_EMAIL` | 发件地址和收件地址 |

本文档不记录任何 API Key、密码、Cookie、Session 或 Token 的实际值。

部署脚本在 VMware 上优先使用 `$HOME/modeshift_django/.env`、`.env.vm`、`.env.production`。如果都不存在，会生成最小环境文件。部署时 GitHub Secret `DEEPSEEK_API_KEY` 会传入 web 容器，脚本只检查它是否存在并进行 API 预检，不打印完整 Key。

## 8. 回滚机制

部署前，`scripts/deploy-public-vm.sh` 会读取当前 `modeshift_web` 容器使用的镜像。新版本启动后如果 30 次本机健康检查全部失败，并且旧镜像仍存在，脚本会恢复旧镜像并重新启动 web/nginx。

重要限制：当前是替换 web 容器后检查健康，不是蓝绿发布；切换期间可能短暂不可用。回滚只是尝试恢复旧镜像，尚未再次验证回滚后的健康状态。Compose 启动命令失败、任务被取消、DeepSeek 后置检查失败时，当前没有统一的自动回滚处理。脚本记录的旧镜像使用容器的镜像名称；若旧容器使用可变的 `:main` 标签，标签可能已指向新镜像，应人工核对镜像 ID。不要把当前机制理解为所有错误都能自动恢复。

web 启动命令会执行数据库迁移。镜像回滚不会回滚数据库、配置或数据卷；不向后兼容的数据库迁移需要单独的备份和恢复方案。不要在生产环境主动制造失败来验证回滚，应在隔离环境演练。

手工查看当前版本：`docker inspect --format '{{.Config.Image}}' modeshift_web`。

查看本机缓存：`docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}'`。

## 9. 日常发布

正常发布命令是：`git status`、`git add <changed-files>`、`git commit -m "描述本次变更"`、`git push origin main`。

然后在 GitHub 的 `Actions -> Deploy to VMware Ubuntu` 观察四个阶段：

1. `QA gate — API contracts and UI smoke`
2. `Build cached production image on VMware`
3. `Start locally built Docker application on VMware`
4. `Email final pipeline result`

也可以在 workflow 页面选择 `Run workflow` 手工触发 main 部署。

## 10. VMware 本地检查命令

进入目录：`cd "$HOME/modeshift_django"`。

查看服务：`docker compose --env-file .env -f docker/docker-compose.prod.yml ps`。

查看日志：`docker compose --env-file .env -f docker/docker-compose.prod.yml logs --tail=200 web nginx`。

检查入口：`curl --noproxy '*' -fsS http://127.0.0.1:8080/health/`。

检查缓存和磁盘：`docker system df`、`df -h /var/lib/docker`。

不要直接执行无条件的 `docker system prune -a`，否则可能删除回滚镜像和构建层。

## 11. 常见故障

### Runner Offline 或 workflow queued

检查 VMware 是否开机、Docker 是否运行、Runner 服务是否运行，以及 Runner 是否仍有 `self-hosted/linux/x64/vmware` 四个标签。

### Checkout 很慢或失败

在 VMware 中执行 `curl -I --max-time 10 -x http://192.168.27.1:7890 https://github.com` 和 `curl -I --max-time 10 -x http://192.168.27.1:7890 https://api.github.com`。如果宿主机代理端口变化，需要同步修改 `.github/workflows/vmware-deploy.yml`。

### 本地镜像不存在

出现 `Locally built image is missing` 时，说明 build job 和 deploy job 没使用同一个 Docker daemon，或构建 job 没完成。检查 `docker info` 和 `docker image ls`。

### Docker 构建超过 20 分钟

第一次构建可能较慢，因为需要下载 Python 基础镜像、Debian 依赖、Chromium 和字体。后续应命中 VMware 本地 Docker layer cache。优先检查 `docker system df` 和磁盘空间，不要先删除全部缓存。

### 健康检查返回 502

健康检查已经使用 `curl --noproxy '*'`，避免把本地请求发给外部代理。继续查看 Compose 状态和 `web`、`nginx` 日志。

### DeepSeek 预检失败

确认 GitHub Secret 名称为 `DEEPSEEK_API_KEY`，Key 没过期且没有写入代码。只检查容器中变量是否存在：`docker compose --env-file .env -f docker/docker-compose.prod.yml exec -T web sh -c 'test -n "${DEEPSEEK_API_KEY:-}"'`。

## 12. 方案边界和维护原则

本次验证的耗时基线（Run `37199597201`）：QA 212 秒，VMware checkout 104 秒，Docker 缓存构建 23 秒，部署脚本 10 秒。整体约 6 分钟，不承诺每次一样快。首次依赖构建曾触发 20 分钟上限，保留下来的中间层使后续重跑命中缓存。

排障历史：

- 大源码 artifact 传输和 GitHub 直连很慢，改为 VMware 持久化 workspace checkout，并使用宿主机代理。
- Buildx 工具下载失败，改用本机现有 Docker 引擎。
- Legacy Builder 不支持 `--progress=plain`，移除该参数。
- apt/pip 未正确使用代理，给各 Dockerfile 阶段声明代理参数并导出小写代理变量。
- localhost 健康请求误经外网代理返回 502，增加 `curl --noproxy '*'`。
- 同机镜像绕经 GHCR 浪费时间，移除应用镜像登录、推送和拉取步骤。

本地 Git 同步注意：本次 Mac 上的 `git commit/write-tree` 曾卡住，最终通过 GitHub Git 数据 API 创建提交并以非强制方式更新 main。远程已更新不代表本地 HEAD 自动同步；本地可能仍有已暂存的同一批改动。下一次工作前先核对 HEAD、origin/main 和暂存区，不要重复提交或直接重置。必要时先保存本地差异，再执行安全的 fetch 和快进同步。本文档提交为 `54f82220c5381710e4059070ca49b63e8fcab03d`，其触发的 Run `37201543979` 也已验证成功。

当前单 VM 方案可以做到自动触发、自动拉代码、本地缓存构建、自动启动、健康检查、GitHub 状态回传和失败回滚；但不能提供多机高可用、数据库跨机器容灾或主机故障自动接管。

以后增加第二台服务器，再考虑独立构建机、私有 Registry、蓝绿部署或滚动发布。当前只有一台 VMware 时，本地构建、本地启动是速度和复杂度最合适的方案。

维护部署逻辑时遵守：

1. 不把 API Key、密码、Cookie、Session 写入 workflow 或文档。
2. 不恢复不必要的 GHCR push/pull 链路。
3. 不删除 Docker 缓存或数据库卷，除非明确确认影响。
4. 修改脚本后执行 `bash -n scripts/deploy-public-vm.sh`。
5. 修改 workflow 后验证 YAML，并运行一次真实 Actions 流程。
6. 只有 VMware 内部健康检查成功，才认为部署成功。
7. 每次发布保留 commit SHA，便于定位版本和回滚。
