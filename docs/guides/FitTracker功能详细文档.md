# 🟢 FitTracker - 健康管理App功能详细文档

## 📋 项目概述

**FitTracker** 是一个专业的健康管理应用，专注于健身追踪、营养管理、健康数据分析和运动计划制定。作为QAToolBox项目拆分出的独立App，FitTracker旨在为健身爱好者和健康管理用户提供全方位的健康管理解决方案。

## 🎯 目标用户

- **健身爱好者**: 需要系统化训练计划和进度追踪
- **健康管理用户**: 关注身体健康指标和营养摄入
- **运动达人**: 需要专业的运动数据分析和建议
- **减脂/增肌人群**: 需要科学的饮食和训练指导

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django 4.2 + Python 3.12
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **任务队列**: Celery
- **Web服务器**: Nginx + Gunicorn

### 前端技术栈
- **模板引擎**: Django Templates
- **CSS框架**: Bootstrap 5
- **JavaScript**: 原生JS + jQuery
- **图表**: Chart.js
- **图标**: Font Awesome

## 🚀 核心功能模块

---

## 1. 🏋️‍♂️ 健身中心

### 1.1 训练会话管理

#### 功能特性
- **训练类型支持**: 
  - 力量训练 (Strength Training)
  - 有氧运动 (Cardio)
  - 柔韧性训练 (Flexibility)
  - 平衡训练 (Balance)
  - 混合训练 (Mixed)

- **强度等级分类**:
  - 轻度 (Light)
  - 中度 (Moderate)
  - 高强度 (Intense)
  - 极限 (Extreme)

#### 数据模型
```python
class EnhancedFitnessWorkoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES)
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField(default=0)
    heart_rate_avg = models.IntegerField(default=0)
    heart_rate_max = models.IntegerField(default=0)
    exercises = models.JSONField(default=list)
    notes = models.TextField(blank=True, null=True)
    audio_recording_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 核心功能
- **训练记录**: 记录每次训练的详细信息
- **动作追踪**: JSON格式存储训练动作和组数
- **心率监测**: 记录平均心率和最大心率
- **卡路里计算**: 自动计算消耗的卡路里
- **音频记录**: 支持训练过程中的喘息录音
- **训练笔记**: 记录训练感受和注意事项

### 1.2 训练计划系统

#### 训练模式支持
- **五分化训练**: 经典五分化力量训练，适合中高级训练者
- **三分化训练**: 推拉腿三分化训练
- **推拉腿训练**: Push/Pull/Legs训练模式
- **有氧训练**: 心肺功能训练
- **功能性训练**: 注重实用性和运动表现

#### 训练计划编辑器
- **可视化编辑**: 直观的训练计划编辑界面
- **模块化结构**: 热身、主训练、辅助、冷却模块
- **强度管理**: 训练强度和时间管理
- **目标设定**: 个性化训练目标设定

#### 训练模板系统
- **预设模板**: 丰富的训练模板库
- **模板应用**: 一键应用和自定义模板
- **计划分享**: 训练计划分享和导入功能
- **模式切换**: 灵活的训练模式切换

### 1.3 健身工具集

#### BMI计算器
- **精确计算**: 基于身高体重计算BMI
- **健康评估**: BMI分类和健康风险评估
- **理想体重**: 计算理想体重范围
- **健康建议**: 个性化的健康建议

#### 心率计算器
- **最大心率**: 基于年龄计算最大心率
- **目标心率**: 不同强度下的目标心率区间
- **Karvonen公式**: 更精确的心率计算
- **训练建议**: 基于心率的训练强度建议

#### 1RM计算器
- **多种公式**: 支持Epley、Brzycki、Lombardi、O'Connor公式
- **重复次数预测**: 根据目标重量预测重复次数
- **训练建议**: 不同目标的训练重量建议
- **RPE调整**: 基于主观疲劳度的重量调整

#### 配速计算器
- **配速分析**: 计算跑步配速和速度
- **时间预估**: 不同距离的时间预估
- **训练配速**: 轻松跑、节奏跑、间歇跑配速建议
- **配速分析**: 配速水平评估

---

## 2. 🍎 营养管理

### 2.1 营养教练服务

#### 核心功能
- **BMR计算**: 使用Mifflin-St Jeor公式计算基础代谢率
- **TDEE计算**: 根据活动水平计算每日总能量消耗
- **热量调整**: 根据健身目标调整热量摄入
- **宏量营养素**: 计算蛋白质、碳水、脂肪分配

#### AI营养计划生成
- **DeepSeek集成**: 使用AI生成个性化饮食计划
- **一周计划**: 生成7天完整饮食计划
- **营养分析**: 每餐的营养成分分析
- **个性化定制**: 考虑饮食偏好和过敏限制

#### 数据模型
```python
class NutritionCoachService:
    def calculate_bmr(self, age: int, gender: str, weight: float, height: float) -> float
    def calculate_tdee(self, bmr: float, activity_level: str) -> float
    def adjust_calories_for_goal(self, tdee: float, goal: str, intensity: str) -> float
    def calculate_macros(self, calories: float, goal: str) -> Dict[str, float]
    def generate_meal_plan_with_deepseek(self, user_data: Dict) -> Dict
```

### 2.2 饮食记录系统

#### 餐食记录
- **多餐支持**: 早餐、午餐、晚餐、加餐记录
- **食物数据库**: 丰富的食物营养成分数据库
- **营养成分**: 详细的营养成分分析
- **卡路里追踪**: 实时卡路里摄入追踪

#### 体重追踪
- **体重记录**: 定期体重记录
- **体脂率**: 体脂率变化追踪
- **趋势分析**: 体重变化趋势分析
- **目标设定**: 体重目标设定和进度追踪

#### 营养提醒
- **用餐提醒**: 定时用餐时间提醒
- **训练提醒**: 训练前后营养补充提醒
- **水分提醒**: 定时水分补充提醒
- **个性化提醒**: 基于用户习惯的个性化提醒

---

## 3. 📊 健康数据分析

### 3.1 身体成分分析

#### 体脂率计算
- **海军公式**: 使用美国海军公式计算体脂率
- **性别差异**: 男女不同的体脂率标准
- **健康分类**: 体脂率健康水平分类
- **趋势追踪**: 体脂率变化趋势分析

#### 身体指标
- **BMI分析**: 身体质量指数分析
- **腰臀比**: 腰臀比计算和风险评估
- **瘦体重**: 瘦体重和脂肪重量分析
- **健康建议**: 基于身体成分的健康建议

### 3.2 运动数据分析

#### 卡路里计算
- **MET值**: 不同运动类型的代谢当量
- **精确计算**: 基于体重、时长、强度的卡路里计算
- **强度分析**: 不同强度下的卡路里消耗
- **运动建议**: 基于卡路里目标的运动建议

#### 蛋白质需求
- **基础需求**: 每公斤体重的蛋白质需求
- **活动调整**: 根据活动水平调整蛋白质需求
- **目标调整**: 根据健身目标调整蛋白质摄入
- **来源建议**: 不同蛋白质来源的建议

#### 水分需求
- **基础需求**: 每公斤体重的水分需求
- **活动调整**: 根据活动水平调整水分需求
- **气候因素**: 考虑气候因素的水分需求
- **运动补充**: 运动期间的水分补充建议

---

## 4. 🏆 成就系统

### 4.1 健身成就

#### 成就类型
- **训练成就**: 基于训练次数和强度的成就
- **时间成就**: 基于训练时长的成就
- **重量成就**: 基于重量提升的成就
- **坚持成就**: 基于连续训练天数的成就

#### 徽章系统
- **等级徽章**: 不同等级的健身徽章
- **特殊徽章**: 特殊训练成就的徽章
- **里程碑徽章**: 重要里程碑的纪念徽章
- **挑战徽章**: 完成挑战获得的徽章

### 4.2 进度追踪

#### 力量档案
- **1RM记录**: 各动作的1RM记录
- **进步追踪**: 力量提升进度追踪
- **目标设定**: 力量目标设定
- **建议生成**: 基于进步的训练建议

#### 训练统计
- **月度统计**: 月度训练数据统计
- **年度统计**: 年度训练数据统计
- **类型分布**: 训练类型分布分析
- **趋势分析**: 训练趋势分析

---

## 5. 👥 健身社区

### 5.1 社区功能

#### 动态分享
- **训练分享**: 分享训练成果和心得
- **图片上传**: 支持训练照片上传
- **视频分享**: 支持训练视频分享
- **互动评论**: 社区用户互动评论

#### 经验交流
- **经验分享**: 分享健身经验和技巧
- **问答互动**: 健身问题问答
- **专家指导**: 专业教练指导
- **学习资源**: 健身知识学习资源

### 5.2 挑战活动

#### 挑战类型
- **减脂挑战**: 减脂目标挑战
- **增肌挑战**: 增肌目标挑战
- **耐力挑战**: 耐力训练挑战
- **坚持挑战**: 连续训练挑战

#### 活动管理
- **活动发布**: 发布挑战活动
- **参与报名**: 用户参与挑战报名
- **进度追踪**: 挑战进度追踪
- **奖励发放**: 完成挑战的奖励

---

## 📱 用户界面设计

### 主题色彩方案
```css
/* 主色调 - 活力绿色 */
--primary-green: #22c55e;       /* 活力绿 */
--primary-green-light: #4ade80; /* 浅绿 */
--primary-green-dark: #16a34a;  /* 深绿 */

/* 辅助色 */
--accent-green: #10b981;        /* 翠绿 */
--accent-green-light: #34d399; /* 浅翠绿 */
--accent-green-dark: #059669;   /* 深翠绿 */

/* 自然色调 */
--nature-blue: #0ea5e9;
--nature-yellow: #eab308;
--nature-orange: #f97316;
--nature-purple: #8b5cf6;

/* 背景色 */
--nature-bg: #f0fdf4;
--nature-bg-light: #f7fee7;
--nature-bg-dark: #dcfce7;
```

### 界面布局
- **主容器**: 清新自然的渐变背景
- **导航栏**: 活力绿色渐变导航
- **卡片设计**: 清新背景，自然阴影
- **按钮样式**: 自然渐变，活力阴影
- **图标风格**: 自然图标，有机形状

---

## 🔧 API接口设计

### 健身工具API

#### BMI计算API
```python
POST /api/fitness/calculate-bmi/
{
    "height": 175,  // 厘米
    "weight": 70    // 公斤
}

Response:
{
    "success": true,
    "data": {
        "bmi": 22.9,
        "category": "正常体重",
        "health_risk": "正常",
        "suggestion": "保持健康的生活方式，定期运动",
        "ideal_weight_range": {"min": 56.7, "max": 73.5}
    }
}
```

#### 心率计算API
```python
POST /api/fitness/calculate-heart-rate/
{
    "age": 25,
    "resting_hr": 60,
    "activity_level": "moderate"
}

Response:
{
    "success": true,
    "data": {
        "max_heart_rate": 195,
        "resting_heart_rate": 60,
        "heart_rate_reserve": 135,
        "target_ranges": {...},
        "karvonen_ranges": {...},
        "recommended_range": {"min": 141, "max": 154}
    }
}
```

#### 1RM计算API
```python
POST /api/fitness/calculate-one-rm/
{
    "weight": 100,
    "reps": 8,
    "formula": "epley"
}

Response:
{
    "success": true,
    "data": {
        "input_weight": 100,
        "input_reps": 8,
        "formula_used": "埃普勒公式",
        "one_rep_max": 126.7,
        "rep_weights": {...},
        "training_recommendations": {...}
    }
}
```

### 营养管理API

#### 营养计划生成API
```python
POST /api/nutrition/generate-meal-plan/
{
    "age": 25,
    "gender": "male",
    "height": 175,
    "weight": 70,
    "goal": "gain_muscle",
    "activity_level": "moderate",
    "dietary_preferences": ["高蛋白"],
    "allergies": ["海鲜"]
}

Response:
{
    "success": true,
    "data": {
        "daily_calories": 2500,
        "macros": {"protein": 175, "carbs": 281, "fat": 83},
        "meal_plan": [...],
        "bmr": 1750,
        "tdee": 2713
    }
}
```

---

## 🗄️ 数据库设计

### 核心数据表

#### 健身训练会话表
```sql
CREATE TABLE enhanced_fitness_workout_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    workout_type VARCHAR(20) NOT NULL,
    intensity VARCHAR(20) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    calories_burned INTEGER DEFAULT 0,
    heart_rate_avg INTEGER DEFAULT 0,
    heart_rate_max INTEGER DEFAULT 0,
    exercises JSONB DEFAULT '[]',
    notes TEXT,
    audio_recording_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 健身用户档案表
```sql
CREATE TABLE enhanced_fitness_user_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES auth_user(id),
    age INTEGER DEFAULT 25,
    gender VARCHAR(10) DEFAULT 'male',
    height FLOAT DEFAULT 170.0,
    weight FLOAT DEFAULT 70.0,
    body_fat_percentage FLOAT,
    bmr FLOAT,
    goal VARCHAR(20) DEFAULT 'maintain',
    intensity VARCHAR(20) DEFAULT 'balanced',
    activity_level VARCHAR(20) DEFAULT 'moderate',
    dietary_preferences JSONB DEFAULT '[]',
    allergies JSONB DEFAULT '[]',
    training_days_per_week INTEGER DEFAULT 3,
    training_intensity VARCHAR(20) DEFAULT 'moderate',
    training_duration INTEGER DEFAULT 60
);
```

#### 力量档案表
```sql
CREATE TABLE enhanced_fitness_strength_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES auth_user(id),
    bench_press_1rm FLOAT DEFAULT 0,
    squat_1rm FLOAT DEFAULT 0,
    deadlift_1rm FLOAT DEFAULT 0,
    overhead_press_1rm FLOAT DEFAULT 0,
    pull_up_max INTEGER DEFAULT 0,
    push_up_max INTEGER DEFAULT 0,
    plank_max_seconds INTEGER DEFAULT 0,
    total_volume FLOAT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);
```

---

## 🚀 部署和运维

### Docker容器化
```yaml
# docker-compose.yml
version: '3.8'
services:
  fittracker-web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/fittracker
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fittracker
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### CI/CD流程
- **代码检查**: flake8, black, isort, mypy
- **安全扫描**: bandit, safety
- **测试覆盖**: pytest, coverage
- **自动部署**: GitHub Actions
- **健康检查**: 服务健康状态监控

---

## 📈 商业化建议

### 会员体系
- **免费版**: 基础功能，每日限制
- **基础会员**: ¥29.9/月，完整健身追踪
- **高级会员**: ¥59.9/月，AI营养计划
- **专业会员**: ¥99.9/月，专业教练指导

### 功能付费
- **AI营养计划**: 按次付费生成个性化饮食计划
- **专业分析**: 深度身体成分分析
- **训练计划**: 专业训练计划定制
- **数据导出**: 训练数据导出功能

### 企业服务
- **健身房管理**: 健身房会员管理系统
- **教练平台**: 专业教练管理平台
- **企业健康**: 企业员工健康管理
- **API服务**: 提供健身数据API服务

---

## 🎯 总结

FitTracker是一个功能完整、技术先进的健康管理应用，具备以下核心优势：

### 核心优势
1. **专业性强**: 基于科学的健身和营养理论
2. **功能完整**: 涵盖训练、营养、分析、社区等全方位功能
3. **技术先进**: 使用AI技术提供个性化服务
4. **用户体验**: 直观易用的界面设计
5. **数据安全**: 完善的用户数据保护机制

### 市场定位
- **目标市场**: 健身爱好者、健康管理用户
- **竞争优势**: 专业的健身工具集、AI营养计划、完整的健康数据分析
- **商业模式**: 会员订阅 + 功能付费 + 企业服务

### 发展前景
FitTracker具备成为专业健康管理平台的所有要素，通过持续的功能优化和用户体验改进，有望在健康管理领域占据重要地位。

---

**注意**: 本文档基于当前项目代码分析生成，实际开发过程中可能需要根据用户反馈和市场需求进行调整优化。
