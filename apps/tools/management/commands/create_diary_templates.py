from django.core.management.base import BaseCommand

from apps.tools.models.diary_models import DailyQuestion, DiaryTemplate


class Command(BaseCommand):
    help = "创建默认的日记模板和每日问题"

    def handle(self, *args, **options):
        # 创建默认模板
        templates = [
            {
                "name": "今天小确幸",
                "description": "记录今天的小确幸时刻",
                "content": "今天{最开心的事}，让我感到{心情}。{感想}",
                "category": "情感",
                "icon": "🌈",
            },
            {
                "name": "三件事总结",
                "description": "总结今天的三件重要事情",
                "content": "今天做了三件事：{第一件事}，{第二件事}，{第三件事}。最有意义的是{感悟}",
                "category": "总结",
                "icon": "📋",
            },
            {
                "name": "感恩日记",
                "description": "记录今天感恩的事情",
                "content": "今天我感谢{感谢的人或事}，因为{原因}。这让我觉得{感受}",
                "category": "感恩",
                "icon": "🙏",
            },
            {
                "name": "学习记录",
                "description": "记录今天学到的东西",
                "content": "今天我学会了{新技能或知识}，通过{学习方式}。{收获和感想}",
                "category": "学习",
                "icon": "📚",
            },
            {
                "name": "美食日记",
                "description": "记录今天的美食体验",
                "content": "今天吃了{美食名称}，在{地点}。味道{评价}，{感想}",
                "category": "生活",
                "icon": "🍽️",
            },
            {
                "name": "运动打卡",
                "description": "记录今天的运动情况",
                "content": "今天运动了{运动类型}，持续{时长}。感觉{身体状态}，{心情}",
                "category": "健康",
                "icon": "💪",
            },
            {
                "name": "阅读笔记",
                "description": "记录今天的阅读收获",
                "content": "今天读了{书名或文章}，最有启发的内容是{内容摘要}。{个人思考}",
                "category": "学习",
                "icon": "📖",
            },
            {
                "name": "人际互动",
                "description": "记录今天的人际交往",
                "content": "今天和{人物}进行了{互动类型}。我们聊了{话题}，{感受和收获}",
                "category": "社交",
                "icon": "👥",
            },
        ]

        for template_data in templates:
            template, created = DiaryTemplate.objects.get_or_create(name=template_data["name"], defaults=template_data)
            if created:
                self.stdout.write(f"创建模板: {template.name}")
            else:
                self.stdout.write(f"模板已存在: {template.name}")

        # 创建每日问题
        questions = [
            {"question": "如果今天是一种食物，它会是什么？", "category": "想象"},
            {"question": "今天最让你印象深刻的颜色是？", "category": "感官"},
            {"question": "今天你最想感谢的人是谁？", "category": "感恩"},
            {"question": "如果给今天的天空起个名字，会叫什么？", "category": "想象"},
            {"question": "今天学到了什么新东西吗？", "category": "学习"},
            {"question": "今天最有趣的对话是什么？", "category": "社交"},
            {"question": "如果今天有个标题，会是什么？", "category": "总结"},
            {"question": "今天最想重新体验的时刻是？", "category": "回味"},
            {"question": "今天的你和昨天相比有什么不同？", "category": "反思"},
            {"question": "今天最想对自己说的话是什么？", "category": "自省"},
            {"question": "今天看到的最美好的事物是？", "category": "发现"},
            {"question": "今天的心情如果是天气，会是怎样的？", "category": "情感"},
            {"question": "今天最让你会心一笑的瞬间是？", "category": "快乐"},
            {"question": "如果今天是一首歌，会是什么风格？", "category": "想象"},
            {"question": "今天最让你感到温暖的事情是？", "category": "温暖"},
            {"question": "今天你做的最勇敢的事是什么？", "category": "勇气"},
            {"question": "今天最想记住的细节是？", "category": "记忆"},
            {"question": "今天让你感到惊讶的事情是？", "category": "惊喜"},
            {"question": "如果今天有一个颜色代表，会是什么？", "category": "感受"},
            {"question": "今天最想分享给朋友的事情是？", "category": "分享"},
        ]

        for question_data in questions:
            question, created = DailyQuestion.objects.get_or_create(question=question_data["question"], defaults=question_data)
            if created:
                self.stdout.write(f"创建问题: {question.question[:30]}...")

        self.stdout.write(self.style.SUCCESS(f"成功创建了 {len(templates)} 个模板和 {len(questions)} 个每日问题"))
