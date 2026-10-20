# 小红书博主更新 Agent

页面：`/tools/peep/`（旧地址 `/tools/xiaohongshu-agent/` 保留重定向）。Model Shift 用户登录后，可以搜索博主或粘贴包含 `xsec_token` 的主页链接，选择作者并订阅。首次订阅只建立当天基线；之后按日保存读取到的笔记 ID、标题、封面和链接。网页对话实时读取主页并与昨天的快照比较；企业微信消息返回最近一次每日检查的结果及时间。新增笔记显示封面、标题、正文摘要和原链接。

## 本地小红书 MCP

上游是 [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)，本地验证固定在 commit `7797fd375aba02dcd33afe143f6bee13e5870859`。仓库内的 [`docs/patches/xhs-mcp-readiness.patch`](patches/xhs-mcp-readiness.patch) 是针对上游页面等待超时/空数据的本地补丁；安装时在该固定 commit 上应用。上游对应 [搜索问题 #813](https://github.com/xpzouying/xiaohongshu-mcp/issues/813) 和 [主页问题 #871](https://github.com/xpzouying/xiaohongshu-mcp/issues/871) 仍未完全解决，所以补丁也不保证平台当前页面始终可读。Agent 仅调用搜索、主页、笔记详情和登录状态/二维码的 HTTP 接口。MCP 本身有发布、评论等写接口，必须仅绑定 `127.0.0.1`，并设置随机 Bearer Token；不要直接对外开放端口。

```bash
cd /path/to/xiaohongshu-mcp
git checkout 7797fd375aba02dcd33afe143f6bee13e5870859
git apply /path/to/modeshift_django/docs/patches/xhs-mcp-readiness.patch
go build -o xiaohongshu-mcp .
AUTH_TOKEN=<private-random-token> COOKIES_PATH=/private/path/cookies.json ./xiaohongshu-mcp -port 127.0.0.1:18060
```

Django 进程设置相同的 `XHS_MCP_TOKEN`，可选 `XHS_MCP_BASE_URL`（默认 `http://127.0.0.1:18060`）。Cookie 文件和 Token 不应放进仓库。Model Shift 管理员可从页面获取小红书登录二维码。普通用户无法触发登录操作。MCP 扫码登录后，用户可查询它有权访问的主页。

页面打开时只读取已保存的登录状态；管理员点击“刷新登录状态”才向 MCP 发起新的检查。单次查询由 Redis 互斥和至少 2 秒间隔控制，小红书 MCP 每天默认最多 80 次请求，超限时停止读取并显示原因。此上限可通过 `XHS_MCP_DAILY_REQUEST_LIMIT` 配置，不能保证平台绝不限制账号。

生产 Docker 和 Windows Docker Desktop 使用 [`docker/docker-compose.creator-watch.yml`](../docker/docker-compose.creator-watch.yml) 叠加生产 Compose。先在上游固定 commit 应用补丁，再在该上游目录构建 `docker build --platform linux/amd64 -t modeshift-xhs-mcp:patched-7797fd3 .`。项目根目录私有 `.env` 中配置 `XHS_MCP_TOKEN` 和 `XHS_MCP_BASE_URL=http://xiaohongshu-mcp:18060`，两个 Compose 文件一起启动。Windows Docker Desktop 使用 Linux 容器；这个 MCP 镜像当前固定 `linux/amd64`，ARM 机器可能需要模拟运行。MCP 不映射宿主机端口，Cookie 位于 `xhs_mcp_data` 命名卷，首次启动需由管理员重新扫码。VMware GitHub Actions 在设置 `XHS_MCP_TOKEN` Secret 后自动构建上述固定版本镜像并启用 overlay。

## 每日检查

服务器每天运行一次：

```bash
python3 manage.py check_xhs_watches
```

可用 `--user-id 123` 限定用户。若服务器运行 `config.celery` 的 Celery Worker 和 Beat，已配置每天 08:05（Asia/Shanghai）自动执行；否则将此命令放入服务器 cron/systemd 定时器，二选一以免重复运行。命令会保存当天快照、记录新笔记通知，并向配置过且尚未收到该笔记的邮箱和企业微信账号发送消息。网页查询也会检查并发送尚未通知的新增笔记。开发环境默认使用控制台邮件后端，不会真正投递邮件。

比较依据是上游这次加载到的公开/可访问笔记 ID，不是小红书账号的全部历史笔记总数。主页成功读取结果缓存 5 分钟，同一失败查询短时间退避；MCP 调用使用同机文件锁串行执行，每次调用至少间隔 2 秒，定时命令在不同作者之间另加 2–5 秒间隔。文件锁默认位于系统临时目录，也可设置 `XHS_MCP_LOCK_FILE`；多台服务器共用同一 MCP 时应改用共享锁和共享限流。接口的用户级节流依赖 Django 缓存，生产环境若使用 DummyCache 则不会生效，应配置共享缓存。这些措施只能降低访问频率，不能保证账号不会被平台限制。上游返回空笔记列表时暂不建立快照，以免把加载失败误报为“0 篇”。没有昨天快照时会明确显示首次基线或上次记录日期；无法读取、登录过期、列表不完整时不能把结果解释为账号绝对没有更新。一个订阅最多保留最近 8 天的快照。

## 邮箱

用户在“我的订阅”中填写每个博主的通知邮箱，留空可关闭。可填写 QQ 邮箱等有效邮箱。服务器需配置真实 SMTP 后端及 `EMAIL_HOST`、`EMAIL_PORT`、`EMAIL_HOST_USER`、`EMAIL_HOST_PASSWORD`、`DEFAULT_FROM_EMAIL` 等设置。邮箱地址只保存在该订阅的 `last_profile_data` 中；每篇新笔记只向每个渠道发送一次。2026-10-17 本地对 QQ SMTP 和现有生产 SMTP 配置的测试均在认证阶段被服务器断开，未确认测试邮件送达；需修复邮件服务凭据后再实测。

## 企业微信应用

企业微信自建应用需要在服务器配置：

- `XHS_WECOM_CORP_ID`：企业 ID。
- `XHS_WECOM_APP_SECRET`：应用 Secret。
- `XHS_WECOM_AGENT_ID`：应用 AgentId。
- `XHS_WECOM_CALLBACK_TOKEN` 和 `XHS_WECOM_ENCODING_AES_KEY`：应用接收消息回调设置。
- `XHS_WECOM_USER_MAP`：JSON 字典，Model Shift 用户数字 ID 到企业微信成员 UserID，例如 `{"123":"zhangsan"}`。由管理员维护，避免用户填入他人的接收 ID。

将企业微信应用的接收消息 URL 设置为 `https://<your-domain>/tools/api/xiaohongshu-agent/wecom/callback/`，在企业微信管理后台完成 URL 验证。回调验证 SHA1 签名、AES 加密消息和企业 ID，再按映射查找 Model Shift 用户。员工在应用里发送“博主昵称今天更新了吗”，系统返回最近一次检查结果和检查时间。回调使用缓存结果以满足平台的响应时限；若要看实时状态，请用网页对话框。新笔记推送使用企业微信应用消息接口。应用必须对这些成员可见，且服务器需能访问企业微信 API。

目前本地没有企业微信应用凭据和公开 HTTPS 回调地址，因此可验证回调算法与内部逻辑，真实消息收发需要配置后联调。

## 接口权限

- 搜索、主页、订阅、消息、通知邮箱：需 Model Shift 登录和 CSRF。
- 登录状态/二维码：仅 staff。
- 企业微信回调：通过企业微信签名、AES 和企业 ID 验证，不使用 Django Session。
- 用户只能读取和修改自己的订阅。MCP Token 与 Cookie 不返回给浏览器。
