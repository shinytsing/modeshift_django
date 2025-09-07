from django.core.management.base import BaseCommand

from apps.tools.models import FoodItem


class Command(BaseCommand):
    help = "为所有食物添加完整的营养信息"

    def handle(self, *args, **options):
        # 完整的食物营养信息数据
        nutrition_data = {
            # 中餐
            "宫保鸡丁": {
                "calories": 320,
                "protein": 25,
                "fat": 18,
                "carbohydrates": 15,
                "fiber": 2,
                "sugar": 8,
                "sodium": 850,
            },
            "麻婆豆腐": {
                "calories": 280,
                "protein": 18,
                "fat": 22,
                "carbohydrates": 8,
                "fiber": 3,
                "sugar": 2,
                "sodium": 1200,
            },
            "红烧肉": {"calories": 450, "protein": 28, "fat": 35, "carbohydrates": 5, "fiber": 1, "sugar": 3, "sodium": 680},
            "糖醋里脊": {
                "calories": 380,
                "protein": 22,
                "fat": 20,
                "carbohydrates": 25,
                "fiber": 1,
                "sugar": 15,
                "sodium": 720,
            },
            "鱼香肉丝": {
                "calories": 290,
                "protein": 20,
                "fat": 16,
                "carbohydrates": 18,
                "fiber": 2,
                "sugar": 10,
                "sodium": 890,
            },
            "回锅肉": {"calories": 420, "protein": 25, "fat": 32, "carbohydrates": 8, "fiber": 2, "sugar": 4, "sodium": 950},
            "水煮鱼": {"calories": 310, "protein": 35, "fat": 18, "carbohydrates": 5, "fiber": 2, "sugar": 2, "sodium": 1100},
            "辣子鸡": {"calories": 340, "protein": 28, "fat": 22, "carbohydrates": 8, "fiber": 2, "sugar": 3, "sodium": 780},
            "白切鸡": {"calories": 280, "protein": 35, "fat": 15, "carbohydrates": 2, "fiber": 0, "sugar": 1, "sodium": 450},
            "叉烧肉": {"calories": 380, "protein": 25, "fat": 28, "carbohydrates": 12, "fiber": 1, "sugar": 8, "sodium": 1200},
            "北京烤鸭": {"calories": 450, "protein": 35, "fat": 30, "carbohydrates": 8, "fiber": 1, "sugar": 2, "sodium": 680},
            "炸酱面": {"calories": 420, "protein": 18, "fat": 15, "carbohydrates": 55, "fiber": 4, "sugar": 8, "sodium": 1200},
            "东坡肉": {"calories": 520, "protein": 30, "fat": 42, "carbohydrates": 6, "fiber": 1, "sugar": 4, "sodium": 850},
            "剁椒鱼头": {
                "calories": 280,
                "protein": 32,
                "fat": 16,
                "carbohydrates": 5,
                "fiber": 2,
                "sugar": 2,
                "sodium": 1100,
            },
            "青椒肉丝": {"calories": 260, "protein": 22, "fat": 18, "carbohydrates": 8, "fiber": 2, "sugar": 3, "sodium": 680},
            "番茄炒蛋": {"calories": 220, "protein": 15, "fat": 16, "carbohydrates": 8, "fiber": 2, "sugar": 5, "sodium": 450},
            "蛋炒饭": {"calories": 380, "protein": 12, "fat": 15, "carbohydrates": 55, "fiber": 2, "sugar": 3, "sodium": 680},
            "小龙虾": {"calories": 180, "protein": 28, "fat": 8, "carbohydrates": 2, "fiber": 0, "sugar": 1, "sodium": 450},
            "火锅": {"calories": 350, "protein": 25, "fat": 22, "carbohydrates": 15, "fiber": 4, "sugar": 5, "sodium": 1200},
            "酸菜鱼": {"calories": 290, "protein": 32, "fat": 16, "carbohydrates": 8, "fiber": 2, "sugar": 3, "sodium": 1100},
            "豆浆油条": {
                "calories": 320,
                "protein": 12,
                "fat": 18,
                "carbohydrates": 35,
                "fiber": 3,
                "sugar": 8,
                "sodium": 680,
            },
            "煎蛋三明治": {
                "calories": 280,
                "protein": 15,
                "fat": 12,
                "carbohydrates": 32,
                "fiber": 2,
                "sugar": 5,
                "sodium": 450,
            },
            "中式炒面": {
                "calories": 420,
                "protein": 18,
                "fat": 22,
                "carbohydrates": 45,
                "fiber": 3,
                "sugar": 8,
                "sodium": 1200,
            },
            # 西餐
            "意大利面": {"calories": 380, "protein": 12, "fat": 8, "carbohydrates": 65, "fiber": 4, "sugar": 6, "sodium": 680},
            "披萨": {"calories": 450, "protein": 18, "fat": 22, "carbohydrates": 48, "fiber": 3, "sugar": 8, "sodium": 1200},
            "汉堡包": {"calories": 520, "protein": 25, "fat": 28, "carbohydrates": 42, "fiber": 2, "sugar": 8, "sodium": 850},
            "牛排": {"calories": 380, "protein": 45, "fat": 22, "carbohydrates": 0, "fiber": 0, "sugar": 0, "sodium": 450},
            "美式烤肋排": {
                "calories": 420,
                "protein": 35,
                "fat": 28,
                "carbohydrates": 8,
                "fiber": 1,
                "sugar": 6,
                "sodium": 680,
            },
            "法式吐司": {
                "calories": 320,
                "protein": 12,
                "fat": 18,
                "carbohydrates": 28,
                "fiber": 2,
                "sugar": 12,
                "sodium": 450,
            },
            "法式洋葱汤": {
                "calories": 180,
                "protein": 8,
                "fat": 12,
                "carbohydrates": 15,
                "fiber": 3,
                "sugar": 8,
                "sodium": 1200,
            },
            "三明治": {"calories": 280, "protein": 15, "fat": 12, "carbohydrates": 32, "fiber": 3, "sugar": 5, "sodium": 680},
            "沙拉": {"calories": 120, "protein": 8, "fat": 8, "carbohydrates": 12, "fiber": 4, "sugar": 6, "sodium": 450},
            "烤鸡": {"calories": 320, "protein": 35, "fat": 18, "carbohydrates": 2, "fiber": 0, "sugar": 1, "sodium": 680},
            "奶油蘑菇汤": {
                "calories": 220,
                "protein": 8,
                "fat": 18,
                "carbohydrates": 12,
                "fiber": 2,
                "sugar": 4,
                "sodium": 850,
            },
            "墨西哥卷饼": {
                "calories": 380,
                "protein": 22,
                "fat": 18,
                "carbohydrates": 35,
                "fiber": 4,
                "sugar": 6,
                "sodium": 1200,
            },
            # 日料
            "寿司": {"calories": 280, "protein": 25, "fat": 8, "carbohydrates": 35, "fiber": 2, "sugar": 8, "sodium": 680},
            "拉面": {"calories": 420, "protein": 18, "fat": 15, "carbohydrates": 55, "fiber": 3, "sugar": 8, "sodium": 1200},
            "天妇罗": {"calories": 380, "protein": 12, "fat": 25, "carbohydrates": 32, "fiber": 2, "sugar": 4, "sodium": 850},
            "味增汤": {"calories": 80, "protein": 6, "fat": 4, "carbohydrates": 8, "fiber": 2, "sugar": 2, "sodium": 1200},
            "饭团": {"calories": 180, "protein": 4, "fat": 2, "carbohydrates": 35, "fiber": 1, "sugar": 1, "sodium": 450},
            "咖喱饭": {"calories": 420, "protein": 15, "fat": 18, "carbohydrates": 55, "fiber": 4, "sugar": 8, "sodium": 850},
            "刺身": {"calories": 120, "protein": 25, "fat": 2, "carbohydrates": 0, "fiber": 0, "sugar": 0, "sodium": 450},
            "乌冬面": {"calories": 380, "protein": 12, "fat": 8, "carbohydrates": 65, "fiber": 3, "sugar": 6, "sodium": 1200},
            "日式拉面": {
                "calories": 420,
                "protein": 18,
                "fat": 15,
                "carbohydrates": 55,
                "fiber": 3,
                "sugar": 8,
                "sodium": 1200,
            },
            # 韩料
            "韩式烤肉": {"calories": 380, "protein": 35, "fat": 22, "carbohydrates": 8, "fiber": 2, "sugar": 4, "sodium": 680},
            "泡菜汤": {"calories": 120, "protein": 8, "fat": 6, "carbohydrates": 12, "fiber": 3, "sugar": 4, "sodium": 1200},
            "紫菜包饭": {"calories": 220, "protein": 8, "fat": 4, "carbohydrates": 38, "fiber": 2, "sugar": 6, "sodium": 680},
            "韩式炸鸡": {
                "calories": 420,
                "protein": 25,
                "fat": 28,
                "carbohydrates": 22,
                "fiber": 2,
                "sugar": 8,
                "sodium": 850,
            },
            "韩式炒年糕": {
                "calories": 280,
                "protein": 8,
                "fat": 8,
                "carbohydrates": 45,
                "fiber": 2,
                "sugar": 12,
                "sodium": 680,
            },
            "韩式拌饭": {
                "calories": 380,
                "protein": 15,
                "fat": 18,
                "carbohydrates": 42,
                "fiber": 4,
                "sugar": 8,
                "sodium": 850,
            },
            "韩式泡菜汤": {
                "calories": 120,
                "protein": 8,
                "fat": 6,
                "carbohydrates": 12,
                "fiber": 3,
                "sugar": 4,
                "sodium": 1200,
            },
            # 泰餐
            "泰式咖喱": {
                "calories": 320,
                "protein": 18,
                "fat": 22,
                "carbohydrates": 18,
                "fiber": 4,
                "sugar": 8,
                "sodium": 850,
            },
            "冬阴功汤": {
                "calories": 180,
                "protein": 12,
                "fat": 12,
                "carbohydrates": 15,
                "fiber": 3,
                "sugar": 6,
                "sodium": 1200,
            },
            "泰式炒河粉": {
                "calories": 380,
                "protein": 15,
                "fat": 18,
                "carbohydrates": 45,
                "fiber": 3,
                "sugar": 8,
                "sodium": 1200,
            },
            "泰式青咖喱": {
                "calories": 280,
                "protein": 16,
                "fat": 20,
                "carbohydrates": 12,
                "fiber": 3,
                "sugar": 6,
                "sodium": 850,
            },
            # 其他
            "印度咖喱": {
                "calories": 320,
                "protein": 18,
                "fat": 22,
                "carbohydrates": 18,
                "fiber": 4,
                "sugar": 8,
                "sodium": 850,
            },
            "蔬菜沙拉": {"calories": 80, "protein": 4, "fat": 4, "carbohydrates": 8, "fiber": 3, "sugar": 4, "sodium": 450},
            "水果拼盘": {"calories": 120, "protein": 2, "fat": 1, "carbohydrates": 28, "fiber": 4, "sugar": 22, "sodium": 5},
        }

        updated_count = 0
        not_found_count = 0

        for food_name, nutrition in nutrition_data.items():
            try:
                food = FoodItem.objects.get(name=food_name)
                food.calories = nutrition["calories"]
                food.protein = nutrition["protein"]
                food.fat = nutrition["fat"]
                food.carbohydrates = nutrition["carbohydrates"]
                food.fiber = nutrition["fiber"]
                food.sugar = nutrition["sugar"]
                food.sodium = nutrition["sodium"]
                food.save()

                self.stdout.write(self.style.SUCCESS(f'✅ 更新: {food_name} - 卡路里: {nutrition["calories"]}千卡'))
                updated_count += 1

            except FoodItem.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠️ 未找到: {food_name}"))
                not_found_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n📊 更新完成! 成功更新: {updated_count}个食物, 未找到: {not_found_count}个食物"))
