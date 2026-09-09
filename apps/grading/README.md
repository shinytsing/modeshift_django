# 作业批改与智能组卷系统

## 功能概述

本系统提供完整的作业批改和智能组卷功能，包括：

1. **作业上传**：支持图片（JPG/PNG）和PDF文件上传
2. **OCR识别**：自动识别题目内容，包括数学公式
3. **自动批改**：支持选择题、填空题、主观题的自动批改
4. **题库匹配**：与外部题库系统对接，获取标准答案
5. **错题分析**：自动识别错题并推荐相似题目
6. **智能组卷**：根据错题自动生成练习卷
7. **试卷导出**：支持PDF和JPG格式导出

## 系统架构

```
apps/grading/
├── models.py              # 数据模型
├── serializers.py         # API序列化器
├── views.py               # API视图
├── urls.py                # URL配置
├── tasks.py               # Celery异步任务
├── admin.py               # Django管理后台
├── tests.py               # 单元测试
├── services/              # 业务逻辑服务
│   ├── ocr_service.py         # OCR识别服务
│   ├── grader_service.py      # 批改逻辑服务
│   ├── question_bank_service.py  # 题库交互服务
│   └── export_service.py      # 导出服务
└── utils/                 # 工具函数
```

## 安装依赖

```bash
pip install -r requirements.txt
```

### 额外依赖

1. **Tesseract OCR**（用于图片文字识别）：
   ```bash
   # macOS
   brew install tesseract tesseract-lang

   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

   # Windows
   # 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. **Poppler**（用于PDF转图片）：
   ```bash
   # macOS
   brew install poppler

   # Ubuntu/Debian
   sudo apt-get install poppler-utils

   # Windows
   # 下载安装包：http://blog.alivate.com.au/poppler-windows/
   ```

3. **Celery + Redis**（用于异步任务）：
   ```bash
   # macOS
   brew install redis
   brew services start redis

   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis

   # Windows
   # 下载安装包：https://github.com/microsoftarchive/redis/releases
   ```

## 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# OCR服务配置（可选，不配置则使用Tesseract）
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key

# LLM服务配置（用于主观题批改）
DEEPSEEK_API_KEY=your_deepseek_api_key
LLM_API_URL=https://api.deepseek.com/v1/chat/completions

# 题库系统配置
QUESTION_BANK_API_URL=http://localhost:8080/api/questions
QUESTION_BANK_API_KEY=your_question_bank_api_key

# Redis配置
REDIS_URL=redis://localhost:6379/3

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/3
CELERY_RESULT_BACKEND=redis://localhost:6379/3
```

## 数据库迁移

```bash
python manage.py makemigrations grading
python manage.py migrate grading
```

## 启动服务

### 1. 启动Django服务器

```bash
python manage.py runserver
```

### 2. 启动Celery Worker

```bash
celery -A config worker -l info
```

### 3. 启动Celery Beat（可选，用于定时任务）

```bash
celery -A config beat -l info
```

## API接口

### 1. 上传作业

```http
POST /api/grading/submissions/upload/
Content-Type: multipart/form-data

file: <作业文件>
student_id: <学生ID>（可选）
```

**响应**：
```json
{
  "success": true,
  "task_id": "uuid-string",
  "submission_id": 123,
  "message": "作业上传成功，正在处理中"
}
```

### 2. 查询批改结果

```http
GET /api/grading/submissions/result/?task_id=<task_id>
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": 123,
    "task_id": "uuid-string",
    "status": "completed",
    "total_score": 85.0,
    "max_score": 100.0,
    "questions": [
      {
        "question_number": 1,
        "question_type": "choice",
        "is_correct": true,
        "score": 10.0,
        "max_score": 10.0,
        "feedback": "回答正确！",
        "similar_questions": []
      }
    ],
    "wrong_question_ids": [2, 3],
    "similar_questions": [...]
  }
}
```

### 3. 生成试卷

```http
POST /api/grading/papers/generate/
Content-Type: application/json

{
  "submission_id": 123,
  "include_wrong_questions": true,
  "include_similar_questions": true,
  "max_questions": 20
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": 456,
    "pdf_file": "/media/papers/user_id/paper_456.pdf",
    "jpg_files": [
      "/media/papers/user_id/paper_456_jpg/page_1.jpg",
      "/media/papers/user_id/paper_456_jpg/page_2.jpg"
    ],
    "total_questions": 15
  }
}
```

### 4. 查询处理状态

```http
GET /api/grading/status/<task_id>/
```

**响应**：
```json
{
  "success": true,
  "status": "grading",
  "status_display": "批改中",
  "progress": {
    "ocr": true,
    "matching": true,
    "grading": false
  }
}
```

## 前端页面

访问地址：`http://localhost:8000/tools/homework_grading/`

页面功能：
1. 拖拽或点击上传作业文件
2. 实时显示处理进度
3. 查看批改结果和错题分析
4. 一键生成错题练习卷
5. 导出PDF或JPG格式试卷

## 批改逻辑

### 选择题批改
- 直接比对学生答案和正确答案
- 忽略大小写和空格
- 支持多选题（如"ABC"）

### 填空题批改
1. **数值型**：使用容差比较（±0.001）
2. **数学表达式**：使用sympy进行等价性判断
3. **文本型**：标准化标点符号后比较
4. **部分匹配**：给予部分分数

### 主观题批改
1. **使用LLM**：调用DeepSeek等LLM API进行智能批改
2. **评分维度**：
   - 逻辑结构（是否条理清晰）
   - 关键步骤（是否包含重要知识点）
   - 观点准确性（是否符合标准答案）
3. **备用方案**：关键词匹配（当LLM不可用时）

## 题库系统对接

### 题目匹配接口

```http
POST /external/question/match
Content-Type: application/json

{
  "question_stem": "题干内容",
  "question_type": "choice"
}
```

### 相似题查询接口

```http
POST /external/question/similar
Content-Type: application/json

{
  "question_id": "q001",
  "question_stem": "题干内容",
  "knowledge_points": ["Python基础", "数据类型"],
  "difficulty": "medium",
  "limit": 5
}
```

### 获取答案接口

```http
GET /external/question/<question_id>/answer
```

## 测试

运行单元测试：

```bash
python manage.py test apps.grading
```

测试覆盖：
- OCR服务测试
- 批改逻辑测试
- 题库服务测试
- 导出服务测试
- API接口测试
- 模型测试

## 性能优化

1. **异步处理**：使用Celery异步处理OCR和批改任务
2. **缓存**：使用Redis缓存题库查询结果
3. **批量处理**：支持批量查询相似题
4. **文件压缩**：导出的JPG使用适当的质量参数

## 安全考虑

1. **文件验证**：验证上传文件类型和大小
2. **用户隔离**：每个用户只能访问自己的作业
3. **API认证**：所有API需要登录认证
4. **CSRF保护**：POST请求需要CSRF Token

## 故障排查

### OCR识别失败
1. 检查Tesseract是否正确安装
2. 检查中文语言包是否安装
3. 查看日志文件中的错误信息

### 批改任务卡住
1. 检查Celery Worker是否正常运行
2. 检查Redis连接是否正常
3. 查看Celery日志

### PDF导出失败
1. 检查reportlab是否正确安装
2. 检查中文字体是否可用
3. 查看导出服务日志

### 题库API调用失败
1. 检查题库系统是否正常运行
2. 检查API URL和API Key配置
3. 查看网络连接状态

## 未来扩展

1. **支持更多题型**：判断题、连线题、排序题等
2. **手写识别**：支持手写答案的识别
3. **语音批改**：支持口语题的语音识别和批改
4. **学习分析**：基于历史数据的学习分析和建议
5. **协作批改**：支持教师人工批改和修正
6. **移动端支持**：开发移动端应用

## 联系方式

如有问题或建议，请联系开发团队。
