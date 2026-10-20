# 博主更新 Agent

## 当前未解决的问题（2026-10-18）

1. **本机 QQ SMTP 已验收，生产 SMTP 仍未验收。** 2026-10-18 本机项目测试邮件接口通过 QQ SMTP 返回 200，QQ 收件箱实际收到发件人为 `1009383129@qq.com` 的邮件，真实封面与小红书链接可见。授权码保存在 macOS 钥匙串，不写入项目文件。生产容器还没有用同一链路做收件验收。
2. **生产和 Windows 尚未验收。** 博主更新功能仍是本地未提交代码，当前 `HEAD` (`f669e78`) 没有每日检查命令和邮件投递模块；公开 VM 还不能运行这个新功能。Docker 配置与本地测试通过，不等于公开 VM 或 Windows Docker Desktop 已运行成功；需在目标机器检查 MCP、定时 Worker、网页查询、站内提醒和真实 SMTP。
3. **小红书账号仍有平台限制风险。** MCP 本地健康检查为 200，只证明进程可用；缓存的登录记录不能证明当前仍已登录。限流和缓存只能降低请求量，不能保证不被封控。

## 最近更新图片链路（2026-10-18）

页面不再使用项目素材演示快照。每日快照仍保存在 `SocialMediaSubscription.last_profile_data` 中用于差异判断，但页面只横向展示最近一次非空更新批次。例如昨天没有新增、今天新增两篇，页面只展示今天两篇。新的非空批次会替换旧批次。小红书历史数据里的 HTTP CDN 地址在输出时转换为同域 HTTPS 地址，不修改原始快照。

同一次检查发现的多篇新增内容合成一条站内提醒和一封邮件。HTML 邮件与站内提醒包含本批更新的真实标题、真实封面和原文链接；用户可点击图片或标题跳到平台原文。封面缺失或加载失败时显示“封面暂不可用，请刷新快照”，不留下破图空白。
小红书封面在页面中通过登录用户可访问的同源代理读取，邮件中作为 CID 内嵌图片附件，避免平台 CDN 防盗链导致破图。

协作沟通按项目根目录 [`AGENTS.md`](../AGENTS.md) 执行：先报问题和证据，明确未验证项，回复简短。

入口：`/tools/peep/`，使用 Model Shift 登录账号。生活模式 `/tools/life_mode/` 提供“博主更新提醒”卡片入口。页面只列出该账号自己的 `SocialMediaSubscription`，包括旧订阅；旧订阅没有真实快照时会显示“尚未建立真实快照”。粘贴主页链接会自动建立关注；按昵称搜索时，Agent 先搜索，只有昵称精确匹配才自动关注；找不到时建议粘贴完整主页链接。关注开始时只建立基线，不发送“新增”提醒。

## 数据源

| 平台 | 主页内容 | 首次订阅 |
| --- | --- | --- |
| 小红书 | 独立 `xiaohongshu-mcp` 服务，需要管理员扫码登录及带 `xsec_token` 的主页链接 | 保存可见笔记基线 |
| B 站 | `bilibili-cli` 的用户资料和最近视频；接口可能返回 412 平台风控 | 读到视频列表后保存最近 30 条视频基线；遇 412 暂停请求 1 小时 |
| 网易云音乐 | 网易云公开用户资料与动态接口 | 保存最近 30 条动态基线 |
| 抖音、微博 | 暂无可验证的稳定主页数据源 | 页面提示待配置，不生成模拟内容 |

小红书 MCP 的 Cookie 仍由 MCP 自己保存在受限文件中。Django 另将最近一次登录状态检查结果写入现有 `SocialMediaPlatformConfig.crawler_config.mcp_login_state`，包含状态、检查时间、简短错误和上次成功时间，不写入 Cookie、Token 或二维码。页面先显示上次记录，再做实时验证；实时检查失败时会显示历史成功时间，但不会把它当作当前已登录。

对话输入平台和昵称，例如“B 站罗翔说刑法今天更新了吗？”。Agent 按当前账号已订阅的用户匹配。每日快照与昨天比较；昨天没有记录时使用上一次记录并明确给出日期；完全没有旧快照时只建立基线，不宣称“未更新”。结果附上新增内容标题、简介、链接和本次可见数量。源列表只加载最近一部分，不能代表用户的全部历史内容或平台总笔记数。读取失败时不会写入空基线。主页读取缓存 5 分钟，页面查询有限流，定时任务每日执行一次。

当天已有完成的检查结果时，普通对话直接返回当天保存的真实快照，不再次访问平台；只有包含“立即刷新”、“重新检查”或“强制刷新”时才重新读取。同一天重新读取如果只返回了当天完整快照的子集，保留信息更完整的快照，避免平台分页或风控导致数据倒退。

新增内容按内容 ID 去重后进入现有站内未读消息提醒，点击跳转到 Agent 页面。通用聊天室过期清理不会删除博主更新提醒；邮件和企业微信仍是可选渠道。管理员登录状态只在手动刷新时向 MCP 发请求，普通打开页面只显示保存的上次状态，避免每次进页面都访问小红书。

小红书所有 MCP 调用共用 Redis 互斥、至少 2 秒间隔，并有默认每天 80 次的访问上限（`XHS_MCP_DAILY_REQUEST_LIMIT` 可调，超限时停止访问并明确报错）。定时检查在不同作者之间再随机等待 2–5 秒，主页结果缓存 5 分钟，失败会短暂退避。这些限制降低请求量，无法保证平台不会限制账号；真正被限制或登录失效时会停止当前读取，不会伪造“没有更新”。

页面在没有上一次记录时显示“对比日期：没有”“上次可见：没有”；真正记录了零条时才显示“0 条”。

## 服务器和 Windows 部署

生产使用 `docker/docker-compose.prod.yml` 与 `docker/docker-compose.creator-watch.yml` 两个 Compose 文件。Windows 使用 Docker Desktop 的 Linux 容器和 WSL2；服务器使用 Linux Docker。MCP 只暴露在 Compose 内网，Cookie 存于 `xhs_mcp_data` 命名卷；不要将 MCP 的 18060 端口映射到公网。`XHS_MCP_TOKEN` 必须是私有随机值，写入未入库的 `.env` 或 VMware 的 GitHub Actions Secret。旧机器的 Cookie 不会自动迁移，新实例启动后管理员要在网页重新扫码。登录状态检查失败时页面仍保留上次检查结果，但不会将历史成功当作当前登录。

VMware 工作流在配置 `XHS_MCP_TOKEN` Secret 后，会从固定的上游 commit `7797fd375aba02dcd33afe143f6bee13e5870859` 构建并应用仓库内补丁，部署脚本先确认该镜像存在，再启动 MCP、Web 和每日检查 Worker。没有配置该 Secret 时，旧部署继续运行，但小红书源不可用。首次构建需要 VM 能访问上游 Git 仓库和浏览器下载地址；构建失败时工作流会报错。部署后检查 `docker compose --env-file .env -f docker/docker-compose.prod.yml -f docker/docker-compose.creator-watch.yml ps`，并在 Agent 页面检查当前登录状态、做一次真实主页读取。自动重启依赖容器的 `restart: unless-stopped`；若服务器启动脚本使用 `docker compose down --remove-orphans`，还需将 overlay 加到启动脚本中，以免移除 MCP 容器。

Windows Docker Desktop 本地启动时，先按 `docs/xiaohongshu-profile-agent.md` 的固定版本和补丁构建 MCP 镜像，在项目根目录的 `.env` 设置 `DJANGO_SECRET_KEY`、`XHS_MCP_TOKEN`，然后运行 `docker compose --env-file .env -f docker/docker-compose.prod.yml -f docker/docker-compose.creator-watch.yml up -d --build`。首次启动还需完成数据库初始化、网页管理员登录和小红书扫码。原生 Windows Python 可以导入该服务并使用 Windows 文件锁；每日定时任务建议仍由 Linux 容器运行。尚未在 Windows 主机或公开 VM 上完成真实运行验收，不能把配置检查当作端到端验证。

## 定时检查

`python manage.py check_creator_watches` 检查有真实数据源且状态为 active 的订阅，并为新增内容发送已配置的通知。生产 Compose 的 `creator_watch` 服务运行独立队列的 Celery Beat/Worker，每天北京时间 08:05 调用 `apps.tools.tasks.check_creator_watches_daily`。部署后应检查这个容器正在运行。旧小红书订阅若缺少主页 `xsec_token`，需要重新粘贴主页链接建立基线。

## 邮件

用户可在每张订阅卡片填写通知邮箱。生产环境必须配置 `EMAIL_HOST`、`EMAIL_PORT`、`EMAIL_USE_TLS`、`EMAIL_HOST_USER`、`EMAIL_HOST_PASSWORD`、`DEFAULT_FROM_EMAIL`；若 SMTP 凭据缺失，生产设置会继续使用控制台邮件后端，页面不会误报发送成功。Django 仅在 SMTP 后端确认发送一封时，才将对应内容 ID 记为已发送。邮箱通知与 GitHub Actions 的“发布流水线结果邮件”共用 Secrets 名称，但由不同进程发出。VMware 部署脚本会把 SMTP 配置写入 VM `.env`，容器的 `env_file` 再读取该文件。

macOS 本机可使用 QQ 邮箱 SMTP：在 QQ 邮箱的“账号与安全”生成授权码，以 `modeshift-qq-smtp` 作为 service、QQ 邮箱地址作为 account 存入 macOS 钥匙串，然后用 `scripts/run-dev-with-qq-mail.sh` 启动。脚本只把授权码注入当前 Django 进程，不写入 `.env`、代码、日志或聊天。

保存邮箱后可点“发送测试邮件”；接口只允许向当前登录用户自己订阅中保存的地址发送，每个订阅 10 分钟最多一次。SMTP 接受邮件不等于收件箱最终送达，需要再检查收件箱和垃圾箱。2026-10-18 本机已通过 `scripts/run-dev-with-qq-mail.sh` 启用 QQ SMTP，项目接口返回 200，QQ 收件箱确认收到测试邮件并显示真实图片和原文链接。普通 `python manage.py runserver` 在没有真实环境变量时仍使用控制台后端。生产容器仍需单独验收。

要验收真实投递，部署后在容器中使用 Django `send_mail` 发送一封测试邮件，并检查指定收件箱；GitHub Actions 发信成功只能证明 Actions Runner 的 SMTP 凭据与网络可用，不能单独证明容器投递成功。

### QQ 收件核验

本机收件核验直接使用已登录的 QQ 邮箱页面。第三方只读 [QQ Mail Reader](https://github.com/oceanjustinlin/qq-mail-reader) 仍不参与项目发信。项目发信由 Django SMTP 后端完成，授权码保存在 macOS 钥匙串 `modeshift-qq-smtp`，启动脚本只把它注入当前进程。

## 企业微信

继续使用 `XHS_WECOM_CORP_ID`、`XHS_WECOM_APP_SECRET`、`XHS_WECOM_AGENT_ID` 和 `XHS_WECOM_USER_MAP`。映射里的键是 Model Shift 用户 ID，值是企业微信成员 UserID；通知可用于所有已支持的平台。企业微信回调仅返回最近一次已经检查的结果，不会由外部消息触发高频抓取。


## 邮箱限频规则（2026-10-20）

每个 Model Shift 用户共用一个提醒邮箱，修改任何订阅卡片的邮箱都会更新账号级邮箱；留空关闭所有博主邮件提醒。旧配置优先使用最早订阅中已保存的邮箱。

自动更新通知与测试邮件共用每日 3 封额度，按北京时间自然日重置。发送前在数据库原子预占额度，切换订阅、修改邮箱、清缓存或重启服务不会重置当天额度。测试发送失败仍可能占用预留额度，以避免不确定投递重复发送。达到上限时测试接口返回 429；自动通知结果显示限额原因，站内提醒仍正常工作。
