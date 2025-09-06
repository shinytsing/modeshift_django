import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class LifeDiaryEntry(models.Model):
    """生活日记条目模型"""

    MOOD_CHOICES = [
        ("😊", "开心"),
        ("😐", "平静"),
        ("😢", "难过"),
        ("🥳", "兴奋"),
        ("😴", "疲惫"),
        ("🤔", "思考"),
        ("😍", "感动"),
        ("😤", "愤怒"),
    ]

    ENTRY_TYPE_CHOICES = [
        ("text", "文字"),
        ("image", "图片"),
        ("voice", "语音"),
        ("template", "模板"),
        ("quick", "快记"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", db_index=True)
    date = models.DateField(default=timezone.now, verbose_name="日期", db_index=True)
    title = models.CharField(max_length=200, blank=True, verbose_name="标题")
    content = models.TextField(blank=True, verbose_name="内容")
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES, verbose_name="心情")
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES, default="text", verbose_name="记录类型")

    # 多媒体内容
    image = models.ImageField(upload_to="diary/images/", blank=True, null=True, verbose_name="图片")
    voice_text = models.TextField(blank=True, verbose_name="语音转文字")
    voice_file = models.FileField(upload_to="diary/voice/", blank=True, null=True, verbose_name="语音文件")

    # 模板和问题
    template_name = models.CharField(max_length=100, blank=True, verbose_name="模板名称")
    question_answer = models.JSONField(default=dict, verbose_name="问题回答")
    daily_question = models.TextField(blank=True, verbose_name="每日问题")

    # 标签和分类
    tags = models.JSONField(default=list, verbose_name="标签")
    hobby_category = models.CharField(max_length=50, blank=True, verbose_name="爱好分类")

    # 统计信息
    word_count = models.IntegerField(default=0, verbose_name="字数")
    reading_time = models.IntegerField(default=0, verbose_name="阅读时间(分钟)")

    # 状态和隐私
    is_private = models.BooleanField(default=False, verbose_name="是否私密")
    auto_saved = models.BooleanField(default=False, verbose_name="自动保存")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "生活日记"
        verbose_name_plural = "生活日记"
        unique_together = ["user", "date"]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "mood"]),
            models.Index(fields=["user", "is_private"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.title}"

    def save(self, *args, **kwargs):
        # 自动计算字数和阅读时间
        total_text = (self.content or "") + (self.voice_text or "") + (self.title or "")
        self.word_count = len(total_text)
        self.reading_time = max(1, self.word_count // 200)  # 假设每分钟200字
        super().save(*args, **kwargs)

    def get_mood_emoji(self):
        """获取心情表情"""
        return self.mood

    def get_entry_summary(self):
        """获取日记摘要"""
        if self.entry_type == "image" and self.image:
            return "📸 分享了一张图片"
        elif self.entry_type == "voice":
            return "🎤 录制了一段语音"
        elif self.entry_type == "template":
            return f"📝 完成了{self.template_name}模板"
        elif self.entry_type == "quick":
            return "⚡ 快速记录了一下"
        else:
            return self.content[:50] + "..." if len(self.content) > 50 else self.content

    def get_word_count_display(self):
        """获取字数显示"""
        if self.word_count < 50:
            return "简短记录"
        elif self.word_count < 200:
            return "适中长度"
        else:
            return "详细记录"

    @classmethod
    def get_user_diary_stats(cls, user, days=30):
        """获取用户日记统计"""
        cache_key = f"diary_stats_{user.id}_{days}"
        result = cache.get(cache_key)

        if result is None:
            queryset = cls.objects.filter(user=user, date__gte=timezone.now().date() - timedelta(days=days))

            result = {
                "total_entries": queryset.count(),
                "total_words": queryset.aggregate(total=models.Sum("word_count"))["total"] or 0,
                "avg_words_per_entry": queryset.aggregate(avg=models.Avg("word_count"))["avg"] or 0,
                "mood_distribution": list(queryset.values("mood").annotate(count=models.Count("id"))),
                "writing_streak": cls.get_writing_streak(user),
            }
            cache.set(cache_key, result, 300)  # 缓存5分钟

        return result

    @classmethod
    def get_writing_streak(cls, user):
        """获取连续写作天数"""
        entries = cls.objects.filter(user=user).order_by("-date")
        if not entries:
            return 0

        streak = 0
        current_date = timezone.now().date()

        for entry in entries:
            if entry.date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break

        return streak

    @classmethod
    def get_random_question(cls):
        """获取随机每日问题"""
        questions = [
            "如果今天是一种食物，它会是什么？",
            "今天最让你印象深刻的颜色是？",
            "今天你最想感谢的人是谁？",
            "如果给今天的天空起个名字，会叫什么？",
            "今天学到了什么新东西吗？",
            "今天最有趣的对话是什么？",
            "如果今天有个标题，会是什么？",
            "今天最想重新体验的时刻是？",
            "今天的你和昨天相比有什么不同？",
            "今天最想对自己说的话是什么？",
            "今天看到的最美好的事物是？",
            "今天的心情如果是天气，会是怎样的？",
        ]
        return random.choice(questions)


class LifeCategory(models.Model):
    """生活分类模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(blank=True, verbose_name="描述")
    color = models.CharField(max_length=7, default="#007bff", verbose_name="颜色")
    icon = models.CharField(max_length=50, blank=True, verbose_name="图标")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "生活分类"
        verbose_name_plural = "生活分类"
        unique_together = ["user", "name"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class LifeTag(models.Model):
    """生活标签模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    name = models.CharField(max_length=50, verbose_name="标签名称")
    category = models.ForeignKey(LifeCategory, on_delete=models.CASCADE, verbose_name="分类")
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "生活标签"
        verbose_name_plural = "生活标签"
        unique_together = ["user", "name"]
        ordering = ["-usage_count", "name"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])


class DiaryAchievement(models.Model):
    """日记成就模型"""

    ACHIEVEMENT_TYPES = [
        ("streak", "连续记录"),
        ("count", "总数统计"),
        ("variety", "多样性"),
        ("consistency", "持续性"),
        ("creative", "创意性"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES, verbose_name="成就类型")
    name = models.CharField(max_length=100, verbose_name="成就名称")
    description = models.TextField(verbose_name="成就描述")
    icon = models.CharField(max_length=10, verbose_name="成就图标")
    target_value = models.IntegerField(verbose_name="目标值")
    current_value = models.IntegerField(default=0, verbose_name="当前值")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "日记成就"
        verbose_name_plural = "日记成就"
        unique_together = ["user", "name"]
        ordering = ["-is_completed", "-current_value"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def update_progress(self, value):
        """更新进度"""
        self.current_value = value
        if not self.is_completed and self.current_value >= self.target_value:
            self.is_completed = True
            self.completed_at = timezone.now()
        self.save()

    def get_progress_percentage(self):
        """获取进度百分比"""
        if self.target_value == 0:
            return 100 if self.is_completed else 0
        return min(100, (self.current_value / self.target_value) * 100)

    @classmethod
    def create_default_achievements(cls, user):
        """为用户创建默认成就"""
        default_achievements = [
            {
                "achievement_type": "streak",
                "name": "故事开端",
                "description": "连续记录3天日记",
                "icon": "🌱",
                "target_value": 3,
            },
            {
                "achievement_type": "streak",
                "name": "习惯养成",
                "description": "连续记录7天日记",
                "icon": "⭐",
                "target_value": 7,
            },
            {
                "achievement_type": "streak",
                "name": "坚持不懈",
                "description": "连续记录30天日记",
                "icon": "🏆",
                "target_value": 30,
            },
            {
                "achievement_type": "count",
                "name": "记录达人",
                "description": "总共记录50篇日记",
                "icon": "📝",
                "target_value": 50,
            },
            {
                "achievement_type": "variety",
                "name": "情绪大师",
                "description": "记录过10种不同心情",
                "icon": "🎭",
                "target_value": 10,
            },
            {
                "achievement_type": "creative",
                "name": "生活家",
                "description": "使用过所有记录方式",
                "icon": "🎨",
                "target_value": 5,
            },
        ]

        for achievement_data in default_achievements:
            cls.objects.get_or_create(user=user, name=achievement_data["name"], defaults=achievement_data)


class DiaryTemplate(models.Model):
    """日记模板模型"""

    name = models.CharField(max_length=100, verbose_name="模板名称")
    description = models.TextField(verbose_name="模板描述")
    questions = models.JSONField(default=list, verbose_name="问题列表")  # 改为questions以匹配数据库
    category = models.CharField(max_length=50, verbose_name="模板分类")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "日记模板"
        verbose_name_plural = "日记模板"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def icon(self):
        """兼容性属性，返回默认图标"""
        return "📝"

    @property
    def usage_count(self):
        """兼容性属性，返回默认使用次数"""
        return 0

    def increment_usage(self):
        """增加使用次数（兼容性方法）"""
        pass  # 数据库中暂无此字段，暂时跳过

    @classmethod
    def get_popular_templates(cls, limit=5):
        """获取热门模板"""
        return cls.objects.filter(is_active=True).order_by("name")[:limit]

    @property
    def content(self):
        """兼容性属性，将questions转换为content格式"""
        if self.questions:
            # 如果questions是列表，转换为字符串
            if isinstance(self.questions, list):
                return "\n".join([f"问题{i + 1}: {q}" for i, q in enumerate(self.questions)])
            # 如果questions是字符串，直接返回
            elif isinstance(self.questions, str):
                return self.questions
        return self.description or "无内容"


class DailyQuestion(models.Model):
    """每日问题模型"""

    question = models.TextField(verbose_name="问题内容")
    category = models.CharField(max_length=50, verbose_name="问题分类")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "每日问题"
        verbose_name_plural = "每日问题"
        ordering = ["usage_count"]

    def __str__(self):
        return self.question[:50]

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])
