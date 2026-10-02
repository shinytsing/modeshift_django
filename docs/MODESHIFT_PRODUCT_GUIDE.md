# ModeShift 产品功能说明书

> 这是一份“当前代码事实清单”，用于知识库检索和测试用例生成。只记录仓库中能由路由、视图、模板、模型或配置确认的功能，不把规划、旧链接或注释代码当成已上线能力。
>
> 盘点时间：2026-09-24。默认站点：Django 应用；本地验收地址：`http://127.0.0.1:8081/`。

## 1. 产品结构

ModeShift 是一个 Django Web 应用，功能由以下几类入口组成：

| 领域 | 页面入口 | 主要能力 |
| --- | --- | --- |
| 工具中心 | `/tools/` | 进入工作、生活、训练、Cyberpunk、Emo 等模式和具体工具 |
| 工作/QA | `/tools/work/`、`/tools/test_case_generator/` | AI 测试用例、RAG 知识库、文件转换、任务管理、网页采集等 |
| 生活 | `/tools/life/`、`/tools/diary/` | 目标、日记、旅行、吃饭选择和日常记录 |
| 训练 | `/tools/training/`、`/tools/fitness/` | 健身、训练计划、动作工具和记录 |
| Emo/创作 | `/tools/emo/`、`/tools/creative_writer/` | 情绪日记、创意写作、故事板、冥想和关系探索 |
| 社区/聊天 | `/tools/chat/`、`/tools/heart_link/`、`/tools/travel_posts/` | 聊天室、匹配、旅行帖子和互动 |
| 账号/内容 | `/users/`、`/content/` | 登录、注册、个人资料、文章、反馈、公告 |

页面和 API 默认受 Django 登录状态及各视图自己的权限判断控制。外部服务是否可用，还取决于部署环境的密钥、依赖和服务进程。

## 2. 测试用例生成器（当前重点功能）

### 2.1 页面与输入

页面：`/tools/test_case_generator/`

页面当前包含：

1. **产品需求**：输入本次要生成测试用例的功能、模块或需求。
2. **知识库搜索**：先按极客、生活、狂暴、Emo 四个模式筛选，再输入页面、功能名或知识点，搜索独立文档卡片。
3. **自定义提示词**：完全保留用户输入的补充 Prompt；不填写时使用系统默认生成规则，但默认规则不会写回或覆盖输入框里的内容。
4. **生成模型**：从服务端模型目录中选择当前可用的模型，例如已配置的 DeepSeek，或正在运行的本机 Ollama 模型。
5. **开始生成**：创建异步任务，页面轮询任务状态并展示结果。
6. **结果操作**：复制结果、下载 TXT、下载 XMind、下载飞书 `.mm` 文件。

### 2.2 知识库交互

知识库不是把整站说明书直接铺在生成页面中，而是按“模式 → 页面 → 功能模块”拆成独立文档卡片。当前共享目录包含：极客模式的测试用例生成器/PDF 转换器/3D 简历/网页爬虫/ZIP 文件处理；生活模式的生活日记/FitMatrix/冥想指南/音乐疗愈/美食选择器；狂暴模式的自我分析/故事板/命运分析；Emo 模式的情感日记/创意写作。

每个条目对应一个 `RequirementDocument` 和独立检索分块，不再把所有功能合并成一份“当前网站能力”文档。按模式筛选后再搜索，可以缩小到具体页面和功能模块。

交互流程：

1. 用户搜索关键词。
2. 页面展示匹配的文档卡片。卡片仅展示标题、来源和短摘要。
3. 点击卡片或“查看详情”，打开文档详情弹窗，按需查看完整文本、来源类型和分块数量。
4. 用户可以点击“加入提示词”，也可以把卡片拖进自定义提示词输入框。
5. 页面在提示词区显示已加入的文档 chip；生成时提交文档 ID，不重复提交全文。
6. 服务端根据文档 ID 校验权限并读取文档内容，作为生成上下文传给选定模型。

加入文档只会把用户选中的文档 ID 作为上下文提交，不会把整站文档全文自动塞进 Prompt；服务端会按权限读取选中文档。加入文档会在提示词中留下类似下面的引用说明，同时保留结构化文档 ID：

```text
【知识库参考文档：文档名称】
请结合该文档中与当前需求相关的实际功能、流程和约束生成测试用例。
```

### 2.3 生成接口与任务生命周期

| 用途 | 方法与路径 | 说明 |
| --- | --- | --- |
| 读取可用模型 | `GET /tools/api/llm/models/` | 返回当前可用的 DeepSeek、Ollama 等模型 |
| 创建异步生成 | `POST /tools/api/async/generate-testcases/` | 提交 `requirement`、`prompt`、`model_id`、`knowledge_document_ids` |
| 查询任务 | `GET /tools/api/async/task/<task_id>/` | 返回进度、状态、结果、选定模型和引用来源 |
| 任务列表 | `GET /tools/api/async/tasks/` | 查看当前用户任务 |
| 删除任务 | `POST /tools/api/async/task/delete/` | 删除任务记录 |
| 下载结果 | `GET /tools/api/async/task/<task_id>/download/<format_type>/` | 下载不同格式的生成结果 |

任务状态由异步任务管理器维护，常见状态包括准备中、处理中、已完成和失败。前端每 2 秒查询一次状态；页面关闭后，服务端任务仍由后台进程继续执行。

### 2.4 生成结果到自动化执行

生成完成后，原始 Markdown 用例仍保留为人工执行用例（PMD）。用户可以点击“执行自动化用例”，选择：

- **自动识别 API/UI**：让模型逐条判断是否存在可执行的接口或页面步骤。
- **仅 API 自动化**：仅执行能转换为同源 HTTP 请求的用例。
- **仅 UI 自动化**：仅执行能转换为页面打开、点击、输入和断言的用例。

执行链路不是运行模型生成的代码，而是：

```text
Markdown 用例 + 原始需求/提示词
        ↓
大模型输出受限 JSON 执行计划
        ↓
服务端校验同源目标、动作白名单和断言
        ↓
requests 执行 API；Playwright 执行 UI
        ↓
返回通过、失败、人工/跳过数量和逐用例证据
```

无法从原用例确认接口地址、请求参数、页面定位器或断言的用例不会被臆造执行，会在报告中标记为“人工执行（PMD）”。默认只允许本机或 Docker 内部目标；API 的 POST、PUT、PATCH、DELETE 需要用户主动勾选“允许 API 写操作”。

执行接口：

| 用途 | 方法与路径 |
| --- | --- |
| 创建执行任务 | `POST /tools/api/async/execute-testcases/` |
| 查询执行进度/报告 | `GET /tools/api/async/execution/<execution_id>/` |
| 停止执行 | `POST /tools/api/async/execution/<execution_id>/stop/` |

## 3. 需求知识库与 RAG

### 3.1 文档类型与数据

知识库模型为 `RequirementDocument` 和 `RequirementChunk`：

- 支持 Markdown、TXT、PDF、DOCX 文档。
- 文档保存提取后的全文，并按约 800 字符切分，保留重叠内容。
- 每个分块保存本地确定性向量，用于本地相似度检索，不依赖额外向量服务。
- `owner IS NULL` 表示共享系统文档；有 owner 的文档只属于对应用户。
- 系统会同步按模式、页面和功能模块拆分的共享文档；整站能力文档和整本产品说明书只作为代码事实文档保留，不再作为单个检索卡片。

### 3.2 API

| 用途 | 方法与路径 | 说明 |
| --- | --- | --- |
| 上传文档 | `POST /tools/api/rag/documents/` | 上传并分块索引文档 |
| 文档详情 | `GET /tools/api/rag/documents/<document_id>/` | 只允许共享文档或当前用户自己的文档 |
| 文档卡片搜索 | `GET /tools/api/rag/documents/search/?q=关键词&mode=极客模式` | 返回按模式过滤后的文档 ID、标题、摘要、来源和匹配分数；`mode` 可选 |
| 分块搜索 | `GET /tools/api/rag/search/?q=问题` | 返回匹配分块及来源 |
| 同步系统能力 | `POST /tools/api/rag/site-capabilities/` | 刷新网站能力和产品说明书索引 |
| RAG 直接生成 | `POST /tools/api/rag/generate/` | 按请求检索分块后调用 DeepSeek 生成 |

所有 RAG 接口都要求登录。文档搜索和页面访问会自动检查并刷新共享系统文档，因此产品说明书修改后会在下一次同步时进入知识库。

## 4. AI 能力与模型配置

- 页面级 AI 助手挂载在公共基础模板，接口为 `/tools/api/ai-assistant/`，功能目录为 `/tools/api/ai-assistant/features/`。
- 测试用例生成器通过统一模型目录读取可用服务，不在前端写死“可选但不可用”的模型。
- DeepSeek 是否出现在目录中，取决于服务端 `DEEPSEEK_API_KEY` 等配置是否加载成功。
- Ollama 模型只有在应用能够访问本机 Ollama API 且模型目录可读取时才会显示。
- RAG 直接生成使用 DeepSeek；异步测试用例生成使用前端选择的 `model_id`。

## 5. 工具中心已实现入口

以下页面路由在 `apps/tools/urls.py` 中存在：

| 类别 | 页面 |
| --- | --- |
| 测试与效率 | `/tools/test_case_generator/`、`/tools/task_manager/`、`/tools/homework_grading/` |
| 文档与文件 | `/tools/pdf_converter/`、`/tools/audio_converter/` |
| 内容生成 | `/tools/redbook_generator/`、`/tools/creative_writer/`、`/tools/storyboard/` |
| 网页与求职 | `/tools/web_crawler/`、`/tools/job-search/`、`/tools/java-job/` |
| 生活 | `/tools/diary/`、`/tools/travel_guide/`、`/tools/food_randomizer/` |
| 健身 | `/tools/fitness/`、`/tools/fitness/tools/`、`/tools/training_plan_editor/` |
| 音乐与练习 | `/tools/music_healing/`、`/tools/guitar-training/` |
| 社区 | `/tools/chat/`、`/tools/heart_link/`、`/tools/travel_posts/` |

部分工具依赖系统命令、第三方 API、浏览器自动化或外部账号。路由存在表示代码提供入口，不代表所有部署环境都已经配置好外部依赖。

## 6. 日记、生活和训练

- 日记页面提供快速保存、心情保存、图片上传、模板、日历、历史、周报和成就接口。
- 生活模块包含目标创建、旅行攻略、旅行帖子、地点和吃饭随机选择等页面/API。
- 健身模块包含个人资料、体重记录、训练计划、动作工具、BMI、训练计时器、营养计算、训练记录和身体分析。
- 吉他模块包含训练首页、按练习类型/难度进入练习、进度、乐理和曲库。

这些功能的数据由 Django 模型保存，用户登录后按用户维度读取和修改。

## 7. 聊天、社区与内容

- 聊天入口：`/tools/chat/`；支持房间、消息、图片、音频、文件、视频和在线状态等接口。
- 心动链接：`/tools/heart_link/`；包含创建、取消、状态、聊天和清理流程。
- 旅行社区：`/tools/travel_posts/`；包含列表、创建、详情、点赞、收藏、评论和城市接口。
- 内容中心：`/content/`；包含文章列表、详情、创建、编辑、删除、建议、反馈和公告。

## 8. 账号与会话

| 能力 | 入口 |
| --- | --- |
| 登录/注册/退出 | `/users/login/`、`/users/register/`、`/users/logout/` |
| 个人资料 | `/users/profile/`、`/users/profile/edit/` |
| 登录状态 | `/users/api/session-status/` |
| 延长会话 | `/users/api/extend-session/` |
| API 退出 | `/users/api/logout/` |
| 主题与头像 | `/users/theme/`、`/users/upload_avatar/` |

当前配置支持长期会话策略：当 `AUTH_TOKEN_PERSIST_FOREVER` 开启时，会话、保存的 Cookie/Token 不按原来的短期时间戳自动过期；实际仍受用户主动退出、管理员操作、密钥失效和部署清理影响。

## 9. 共享数据与权限边界

1. 普通用户只能读取自己的私有 RAG 文档和共享系统文档。
2. 测试用例生成任务按当前用户创建和查询。
3. 上传文档会保存原文件、提取文本和分块数据；删除文档时由关联关系清理分块。
4. 外部账号 Cookie、Session 和 API Key 属于敏感配置，不应写入产品文档或前端提示词。
5. 生产环境是否可用，以环境变量、Docker 服务状态、数据库迁移和外部依赖状态为准。

## 10. 代码索引

- 页面与 API 路由：`apps/tools/urls.py`
- 测试用例页面：`templates/tools/test_case_generator.html`
- 异步生成接口：`apps/tools/async_test_cases_api.py`
- RAG 视图：`apps/tools/views/rag_views.py`
- RAG 服务：`apps/tools/services/rag_service.py`
- LLM 服务：`apps/tools/services/llm_service.py`
- RAG 模型：`apps/tools/models/rag_models.py`
- 用户会话：`apps/users/views.py`、`apps/users/middleware.py`

## 11. 以测试用例生成器为例的完整流程

```text
用户打开 /tools/test_case_generator/
        ↓
搜索关键词 → GET 文档卡片
        ↓
点击卡片 → GET 文档详情 → 详情弹窗
        ↓
点击加入或拖入 prompt → 保存文档 ID + 显示引用 chip
        ↓
选择当前可用模型 + 输入产品需求
        ↓
POST 异步生成任务
        ↓
轮询任务状态 → 展示结果/引用来源 → 下载
```
