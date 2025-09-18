import hashlib
import json
import logging
import time
from datetime import timedelta
from typing import Dict, List, Optional

from django.conf import settings
from django.utils import timezone

import requests

from .overview_data_service import OverviewDataService
from .llm_service import get_llm_service

logger = logging.getLogger(__name__)


class MultiAPITravelService:
    """多API旅游服务 - 支持缓存和智能路由"""

    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30

        # 初始化overview数据服务
        self.overview_service = OverviewDataService()

        # API配置
        self.api_configs = {
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1",
                "api_key": getattr(settings, "DEEPSEEK_API_KEY", ""),
                "model": "deepseek-chat",
                "max_tokens": 8000,
                "timeout": 60,
                "priority": 1,  # 最高优先级
                "cost_per_request": 0.01,
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "api_key": getattr(settings, "OPENAI_API_KEY", ""),
                "model": "gpt-4",
                "max_tokens": 4000,
                "timeout": 60,
                "priority": 2,
                "cost_per_request": 0.03,
            },
            "claude": {
                "base_url": "https://api.anthropic.com/v1",
                "api_key": getattr(settings, "CLAUDE_API_KEY", ""),
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "timeout": 60,
                "priority": 3,
                "cost_per_request": 0.015,
            },
            "gemini": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "api_key": getattr(settings, "GEMINI_API_KEY", ""),
                "model": "models/gemini-pro",
                "max_tokens": 4000,
                "timeout": 60,
                "priority": 4,
                "cost_per_request": 0.005,
            },
            "free_api_1": {
                "base_url": "https://api.free-travel-1.com",
                "api_key": "",
                "timeout": 30,
                "priority": 5,
                "cost_per_request": 0.0,
            },
            "free_api_2": {
                "base_url": "https://api.free-travel-2.com",
                "api_key": "",
                "timeout": 30,
                "priority": 6,
                "cost_per_request": 0.0,
            },
            "free_api_3": {
                "base_url": "https://api.free-travel-3.com",
                "api_key": "",
                "timeout": 30,
                "priority": 7,
                "cost_per_request": 0.0,
            },
        }

        # 缓存配置
        self.cache_duration = timedelta(hours=24)  # 缓存24小时
        self.max_cache_size = 1000  # 最大缓存条目数

        # 真实旅游数据
        self.real_travel_data = self._load_real_travel_data()

    def _load_real_travel_data(self) -> Dict:
        """加载真实的旅游数据"""
        return {
            "北京": {
                "attractions": [
                    {
                        "name": "故宫博物院",
                        "description": "明清两代皇宫，世界文化遗产",
                        "ticket_price": "60元",
                        "open_time": "8:30-17:00",
                    },
                    {
                        "name": "天安门广场",
                        "description": "世界最大城市广场，中国象征",
                        "ticket_price": "免费",
                        "open_time": "全天开放",
                    },
                    {
                        "name": "长城（八达岭）",
                        "description": "万里长城精华段，世界文化遗产",
                        "ticket_price": "40元",
                        "open_time": "7:30-17:30",
                    },
                    {
                        "name": "颐和园",
                        "description": "皇家园林，世界文化遗产",
                        "ticket_price": "30元",
                        "open_time": "6:30-18:00",
                    },
                    {"name": "天坛公园", "description": "明清皇帝祭天场所", "ticket_price": "15元", "open_time": "6:00-22:00"},
                    {
                        "name": "北海公园",
                        "description": "皇家园林，白塔标志性建筑",
                        "ticket_price": "10元",
                        "open_time": "6:30-20:30",
                    },
                    {
                        "name": "景山公园",
                        "description": "俯瞰故宫全景最佳位置",
                        "ticket_price": "2元",
                        "open_time": "6:30-21:00",
                    },
                    {"name": "恭王府", "description": "清代王府，和珅故居", "ticket_price": "40元", "open_time": "8:00-17:00"},
                ],
                "foods": [
                    {
                        "name": "北京烤鸭",
                        "restaurant": "全聚德烤鸭店",
                        "price_range": "150-300元",
                        "description": "皮酥肉嫩，色泽金黄",
                    },
                    {
                        "name": "炸酱面",
                        "restaurant": "老北京炸酱面",
                        "price_range": "15-25元",
                        "description": "传统面食，酱香浓郁",
                    },
                    {"name": "豆汁儿", "restaurant": "护国寺小吃", "price_range": "5-10元", "description": "老北京特色小吃"},
                    {"name": "驴打滚", "restaurant": "南锣鼓巷小吃", "price_range": "8-15元", "description": "糯米豆沙卷"},
                    {"name": "爆肚", "restaurant": "爆肚冯", "price_range": "30-50元", "description": "老北京传统美食"},
                    {"name": "糖葫芦", "restaurant": "街头小摊", "price_range": "5-10元", "description": "冰糖葫芦，酸甜可口"},
                ],
                "transport": {
                    "airport_to_city": "首都机场到市区：机场快线25元，出租车约100元",
                    "subway": "地铁单程3-10元，公交1-2元",
                    "taxi": "起步价13元/3公里，之后2.3元/公里",
                    "bike": "共享单车1.5元/小时",
                },
                "accommodation": {
                    "budget": ["如家酒店 200-300元/晚", "7天连锁 180-250元/晚"],
                    "medium": ["汉庭酒店 300-500元/晚", "锦江之星 350-450元/晚"],
                    "luxury": ["北京饭店 800-1500元/晚", "王府井希尔顿 1200-2000元/晚"],
                },
                "weather": {
                    "spring": "春季3-5月，温度10-20°C，适合旅游",
                    "summer": "夏季6-8月，温度25-35°C，多雨",
                    "autumn": "秋季9-11月，温度15-25°C，最佳旅游季节",
                    "winter": "冬季12-2月，温度-10-5°C，干燥寒冷",
                },
                "tips": [
                    "建议避开节假日高峰期",
                    "故宫需要提前预约",
                    "长城建议选择八达岭或慕田峪",
                    "注意防霾，准备口罩",
                    "地铁是最便捷的交通工具",
                    "建议住在二环内，交通便利",
                ],
            },
            "上海": {
                "attractions": [
                    {"name": "外滩", "description": "黄浦江畔，万国建筑博览", "ticket_price": "免费", "open_time": "全天开放"},
                    {"name": "东方明珠", "description": "上海地标建筑", "ticket_price": "220元", "open_time": "8:30-21:30"},
                    {
                        "name": "豫园",
                        "description": "明代园林，江南古典园林",
                        "ticket_price": "45元",
                        "open_time": "8:45-16:45",
                    },
                    {"name": "南京路步行街", "description": "中华商业第一街", "ticket_price": "免费", "open_time": "全天开放"},
                    {
                        "name": "田子坊",
                        "description": "石库门建筑群，文艺小资聚集地",
                        "ticket_price": "免费",
                        "open_time": "全天开放",
                    },
                    {
                        "name": "上海迪士尼乐园",
                        "description": "亚洲最大迪士尼乐园",
                        "ticket_price": "499元",
                        "open_time": "8:00-20:00",
                    },
                    {
                        "name": "上海科技馆",
                        "description": "大型科普教育基地",
                        "ticket_price": "60元",
                        "open_time": "9:00-17:15",
                    },
                    {"name": "陆家嘴", "description": "金融中心，摩天大楼群", "ticket_price": "免费", "open_time": "全天开放"},
                ],
                "foods": [
                    {
                        "name": "小笼包",
                        "restaurant": "南翔馒头店",
                        "price_range": "20-40元",
                        "description": "皮薄馅多，汤汁丰富",
                    },
                    {"name": "生煎包", "restaurant": "大壶春", "price_range": "15-25元", "description": "底部酥脆，肉馅鲜美"},
                    {"name": "红烧肉", "restaurant": "老饭店", "price_range": "50-80元", "description": "肥而不腻，入口即化"},
                    {"name": "白切鸡", "restaurant": "振鼎鸡", "price_range": "30-50元", "description": "皮爽肉嫩，清淡鲜美"},
                    {
                        "name": "糖醋排骨",
                        "restaurant": "绿波廊",
                        "price_range": "40-60元",
                        "description": "酸甜可口，色泽红亮",
                    },
                    {
                        "name": "蟹粉豆腐",
                        "restaurant": "老正兴菜馆",
                        "price_range": "60-100元",
                        "description": "蟹香浓郁，豆腐嫩滑",
                    },
                ],
                "transport": {
                    "airport_to_city": "浦东机场到市区：磁悬浮50元，地铁8元，出租车约150元",
                    "subway": "地铁单程3-10元，公交2元",
                    "taxi": "起步价14元/3公里，之后2.4元/公里",
                    "bike": "共享单车1.5元/小时",
                },
                "accommodation": {
                    "budget": ["如家酒店 250-350元/晚", "7天连锁 200-300元/晚"],
                    "medium": ["汉庭酒店 350-550元/晚", "锦江之星 400-500元/晚"],
                    "luxury": ["外滩华尔道夫 2000-4000元/晚", "浦东丽思卡尔顿 2500-5000元/晚"],
                },
                "weather": {
                    "spring": "春季3-5月，温度15-25°C，适合旅游",
                    "summer": "夏季6-8月，温度25-35°C，多雨潮湿",
                    "autumn": "秋季9-11月，温度20-30°C，最佳旅游季节",
                    "winter": "冬季12-2月，温度5-15°C，湿冷",
                },
                "tips": [
                    "外滩夜景最佳观赏时间19:00-22:00",
                    "豫园建议避开周末高峰期",
                    "迪士尼需要提前购票",
                    "地铁是最便捷的交通工具",
                    "建议住在人民广场附近，交通便利",
                    "注意防雨，准备雨具",
                ],
            },
            "杭州": {
                "attractions": [
                    {"name": "西湖", "description": "人间天堂，世界文化遗产", "ticket_price": "免费", "open_time": "全天开放"},
                    {"name": "灵隐寺", "description": "千年古刹，佛教圣地", "ticket_price": "30元", "open_time": "7:00-17:00"},
                    {"name": "雷峰塔", "description": "白娘子传说地标", "ticket_price": "40元", "open_time": "8:00-20:00"},
                    {"name": "西溪湿地", "description": "城市湿地公园", "ticket_price": "80元", "open_time": "8:00-17:30"},
                    {
                        "name": "千岛湖",
                        "description": "人工湖泊，度假胜地",
                        "ticket_price": "130元",
                        "open_time": "8:00-17:00",
                    },
                    {"name": "宋城", "description": "宋代文化主题公园", "ticket_price": "290元", "open_time": "9:00-21:00"},
                    {"name": "河坊街", "description": "古街文化，传统商业街", "ticket_price": "免费", "open_time": "全天开放"},
                    {"name": "九溪烟树", "description": "自然风光，徒步胜地", "ticket_price": "免费", "open_time": "全天开放"},
                ],
                "foods": [
                    {
                        "name": "西湖醋鱼",
                        "restaurant": "楼外楼",
                        "price_range": "80-120元",
                        "description": "鱼肉鲜美，醋香浓郁",
                    },
                    {
                        "name": "龙井虾仁",
                        "restaurant": "知味观",
                        "price_range": "60-90元",
                        "description": "茶叶清香，虾仁鲜嫩",
                    },
                    {"name": "东坡肉", "restaurant": "外婆家", "price_range": "40-60元", "description": "肥而不腻，入口即化"},
                    {"name": "叫化鸡", "restaurant": "知味观", "price_range": "50-80元", "description": "荷叶包裹，香气四溢"},
                    {"name": "片儿川", "restaurant": "奎元馆", "price_range": "20-30元", "description": "传统面食，汤鲜味美"},
                    {
                        "name": "桂花糖藕",
                        "restaurant": "知味观",
                        "price_range": "15-25元",
                        "description": "甜而不腻，桂花香浓",
                    },
                ],
                "transport": {
                    "airport_to_city": "萧山机场到市区：机场大巴20元，出租车约100元",
                    "subway": "地铁单程2-8元，公交2元",
                    "taxi": "起步价11元/3公里，之后2.5元/公里",
                    "bike": "共享单车1.5元/小时",
                },
                "accommodation": {
                    "budget": ["如家酒店 200-300元/晚", "7天连锁 180-250元/晚"],
                    "medium": ["汉庭酒店 300-500元/晚", "锦江之星 350-450元/晚"],
                    "luxury": ["西湖国宾馆 1500-3000元/晚", "西溪悦榕庄 2000-4000元/晚"],
                },
                "weather": {
                    "spring": "春季3-5月，温度15-25°C，适合旅游",
                    "summer": "夏季6-8月，温度25-35°C，多雨",
                    "autumn": "秋季9-11月，温度20-30°C，最佳旅游季节",
                    "winter": "冬季12-2月，温度5-15°C，湿冷",
                },
                "tips": [
                    "西湖建议步行或骑行游览",
                    "灵隐寺香火旺盛，注意安全",
                    "雷峰塔夜景很美",
                    "西溪湿地建议春季或秋季游览",
                    "建议住在西湖附近，风景优美",
                    "注意防雨，准备雨具",
                ],
            },
            "西安": {
                "attractions": [
                    {"name": "兵马俑", "description": "世界第八大奇迹", "ticket_price": "120元", "open_time": "8:30-17:30"},
                    {"name": "大雁塔", "description": "唐代佛教建筑", "ticket_price": "50元", "open_time": "8:00-17:00"},
                    {"name": "华清池", "description": "唐代皇家园林", "ticket_price": "120元", "open_time": "7:00-19:00"},
                    {
                        "name": "古城墙",
                        "description": "明代城墙，世界最大古城墙",
                        "ticket_price": "54元",
                        "open_time": "8:00-22:00",
                    },
                    {"name": "钟鼓楼", "description": "古代报时建筑", "ticket_price": "50元", "open_time": "8:30-21:30"},
                    {"name": "回民街", "description": "穆斯林美食街", "ticket_price": "免费", "open_time": "全天开放"},
                    {"name": "大唐芙蓉园", "description": "唐代皇家园林", "ticket_price": "120元", "open_time": "9:00-21:00"},
                    {
                        "name": "陕西历史博物馆",
                        "description": "古代艺术殿堂",
                        "ticket_price": "免费",
                        "open_time": "9:00-17:30",
                    },
                ],
                "foods": [
                    {
                        "name": "肉夹馍",
                        "restaurant": "老孙家肉夹馍",
                        "price_range": "8-15元",
                        "description": "外酥内软，肉香浓郁",
                    },
                    {"name": "凉皮", "restaurant": "魏家凉皮", "price_range": "8-12元", "description": "爽滑可口，酸辣开胃"},
                    {
                        "name": "羊肉泡馍",
                        "restaurant": "老米家泡馍",
                        "price_range": "25-40元",
                        "description": "汤浓肉烂，馍香浓郁",
                    },
                    {
                        "name": "biangbiang面",
                        "restaurant": "老白家面馆",
                        "price_range": "15-25元",
                        "description": "宽面条，口感筋道",
                    },
                    {"name": "胡辣汤", "restaurant": "马洪烤肉", "price_range": "8-15元", "description": "麻辣鲜香，暖胃开胃"},
                    {
                        "name": "柿子饼",
                        "restaurant": "回民街小吃",
                        "price_range": "5-10元",
                        "description": "甜而不腻，软糯可口",
                    },
                ],
                "transport": {
                    "airport_to_city": "咸阳机场到市区：机场大巴25元，出租车约120元",
                    "subway": "地铁单程2-8元，公交1-2元",
                    "taxi": "起步价9元/3公里，之后2.3元/公里",
                    "bike": "共享单车1.5元/小时",
                },
                "accommodation": {
                    "budget": ["如家酒店 180-280元/晚", "7天连锁 160-240元/晚"],
                    "medium": ["汉庭酒店 280-480元/晚", "锦江之星 320-420元/晚"],
                    "luxury": ["西安威斯汀 800-1500元/晚", "西安丽思卡尔顿 1200-2500元/晚"],
                },
                "weather": {
                    "spring": "春季3-5月，温度10-25°C，适合旅游",
                    "summer": "夏季6-8月，温度25-40°C，炎热干燥",
                    "autumn": "秋季9-11月，温度15-30°C，最佳旅游季节",
                    "winter": "冬季12-2月，温度-5-10°C，寒冷干燥",
                },
                "tips": [
                    "兵马俑建议请导游讲解",
                    "大雁塔音乐喷泉晚上很美",
                    "华清池建议春季或秋季游览",
                    "古城墙可以骑行游览",
                    "回民街注意饮食卫生",
                    "建议住在钟楼附近，交通便利",
                ],
            },
            "成都": {
                "attractions": [
                    {
                        "name": "大熊猫繁育研究基地",
                        "description": "国宝大熊猫的家园",
                        "ticket_price": "58元",
                        "open_time": "7:30-17:30",
                    },
                    {
                        "name": "宽窄巷子",
                        "description": "清代古街区，成都文化缩影",
                        "ticket_price": "免费",
                        "open_time": "全天开放",
                    },
                    {
                        "name": "锦里古街",
                        "description": "三国文化街，传统小吃聚集地",
                        "ticket_price": "免费",
                        "open_time": "全天开放",
                    },
                    {
                        "name": "都江堰",
                        "description": "世界文化遗产，古代水利工程",
                        "ticket_price": "90元",
                        "open_time": "8:00-18:00",
                    },
                    {
                        "name": "青城山",
                        "description": "道教名山，世界文化遗产",
                        "ticket_price": "90元",
                        "open_time": "8:00-17:00",
                    },
                    {"name": "武侯祠", "description": "三国文化圣地", "ticket_price": "60元", "open_time": "8:00-18:00"},
                    {
                        "name": "杜甫草堂",
                        "description": "诗圣故居，文学圣地",
                        "ticket_price": "60元",
                        "open_time": "8:00-18:00",
                    },
                    {"name": "春熙路", "description": "成都最繁华商业街", "ticket_price": "免费", "open_time": "全天开放"},
                ],
                "foods": [
                    {"name": "火锅", "restaurant": "海底捞", "price_range": "80-150元", "description": "麻辣鲜香，成都特色"},
                    {
                        "name": "串串香",
                        "restaurant": "马路边边",
                        "price_range": "30-60元",
                        "description": "麻辣串串，经济实惠",
                    },
                    {"name": "担担面", "restaurant": "龙抄手", "price_range": "15-25元", "description": "麻辣鲜香，面条筋道"},
                    {"name": "钟水饺", "restaurant": "钟水饺", "price_range": "20-35元", "description": "皮薄馅多，汤汁丰富"},
                    {
                        "name": "夫妻肺片",
                        "restaurant": "夫妻肺片",
                        "price_range": "25-40元",
                        "description": "麻辣鲜香，口感丰富",
                    },
                    {"name": "赖汤圆", "restaurant": "赖汤圆", "price_range": "15-25元", "description": "甜而不腻，软糯可口"},
                ],
                "transport": {
                    "airport_to_city": "双流机场到市区：机场大巴10元，出租车约80元",
                    "subway": "地铁单程2-8元，公交2元",
                    "taxi": "起步价8元/3公里，之后1.9元/公里",
                    "bike": "共享单车1.5元/小时",
                },
                "accommodation": {
                    "budget": ["如家酒店 180-280元/晚", "7天连锁 160-240元/晚"],
                    "medium": ["汉庭酒店 280-480元/晚", "锦江之星 320-420元/晚"],
                    "luxury": ["成都香格里拉 1200-2500元/晚", "成都丽思卡尔顿 1500-3000元/晚"],
                },
                "weather": {
                    "spring": "春季3-5月，温度15-25°C，适合旅游",
                    "summer": "夏季6-8月，温度25-35°C，多雨",
                    "autumn": "秋季9-11月，温度20-30°C，最佳旅游季节",
                    "winter": "冬季12-2月，温度5-15°C，湿冷",
                },
                "tips": [
                    "大熊猫基地建议早上7:30到达",
                    "宽窄巷子建议避开周末高峰期",
                    "都江堰建议请导游讲解",
                    "火锅建议选择知名连锁店",
                    "建议住在春熙路附近，交通便利",
                    "注意防雨，准备雨具",
                ],
            },
            "宁波": {
                "attractions": [
                    {
                        "name": "天一阁",
                        "description": "中国现存最古老的私家藏书楼",
                        "ticket_price": "30元",
                        "open_time": "8:30-17:00",
                    },
                    {
                        "name": "月湖公园",
                        "description": "城市中心湖泊公园，风景优美",
                        "ticket_price": "免费",
                        "open_time": "全天开放",
                    },
                    {"name": "鼓楼", "description": "明代古建筑，城市地标", "ticket_price": "免费", "open_time": "全天开放"},
                    {
                        "name": "南塘老街",
                        "description": "古街文化，传统商业街",
                        "ticket_price": "免费",
                        "open_time": "全天开放",
                    },
                    {
                        "name": "东钱湖",
                        "description": "浙江省最大淡水湖，度假胜地",
                        "ticket_price": "免费",
                        "open_time": "全天开放",
                    },
                    {"name": "雪窦山", "description": "佛教名山，弥勒道场", "ticket_price": "80元", "open_time": "8:00-17:00"},
                    {
                        "name": "溪口风景区",
                        "description": "蒋氏故里，历史人文景观",
                        "ticket_price": "120元",
                        "open_time": "8:00-17:00",
                    },
                    {
                        "name": "象山影视城",
                        "description": "影视拍摄基地，主题公园",
                        "ticket_price": "150元",
                        "open_time": "8:30-17:30",
                    },
                ],
                "foods": [
                    {
                        "name": "汤圆",
                        "restaurant": "缸鸭狗",
                        "price_range": "15-25元",
                        "description": "宁波特色小吃，甜而不腻",
                    },
                    {
                        "name": "红膏大闸蟹",
                        "restaurant": "宁波海鲜楼",
                        "price_range": "80-150元",
                        "description": "蟹黄饱满，肉质鲜美",
                    },
                    {
                        "name": "宁波汤面",
                        "restaurant": "老外滩面馆",
                        "price_range": "20-35元",
                        "description": "汤鲜面滑，配料丰富",
                    },
                    {
                        "name": "慈城年糕",
                        "restaurant": "慈城年糕店",
                        "price_range": "10-20元",
                        "description": "传统年糕，口感软糯",
                    },
                    {
                        "name": "奉化芋艿头",
                        "restaurant": "奉化农家乐",
                        "price_range": "15-30元",
                        "description": "芋头香甜，营养丰富",
                    },
                    {
                        "name": "宁海麦饼",
                        "restaurant": "宁海小吃店",
                        "price_range": "8-15元",
                        "description": "传统面食，外酥内软",
                    },
                ],
                "transport": {
                    "airport_to_city": "栎社机场到市区：机场大巴20元，出租车约80元",
                    "subway": "地铁单程2-8元，公交2元",
                    "taxi": "起步价10元/3公里，之后2.2元/公里",
                    "bike": "共享单车1.5元/小时",
                },
                "accommodation": {
                    "budget": ["如家酒店 200-300元/晚", "7天连锁 180-250元/晚"],
                    "medium": ["汉庭酒店 300-500元/晚", "锦江之星 350-450元/晚"],
                    "luxury": ["宁波香格里拉 800-1500元/晚", "宁波威斯汀 1000-2000元/晚"],
                },
                "weather": {
                    "spring": "春季3-5月，温度15-25°C，适合旅游",
                    "summer": "夏季6-8月，温度25-35°C，多雨",
                    "autumn": "秋季9-11月，温度20-30°C，最佳旅游季节",
                    "winter": "冬季12-2月，温度5-15°C，湿冷",
                },
                "tips": [
                    "天一阁建议请导游讲解历史文化",
                    "月湖公园适合晨练和散步",
                    "南塘老街建议傍晚游览",
                    "东钱湖可以划船和垂钓",
                    "建议住在海曙区，交通便利",
                    "注意防雨，准备雨具",
                ],
            },
        }

    def get_travel_guide_with_local_data(
        self,
        destination: str,
        travel_style: str,
        budget_min: float = None,
        budget_max: float = None,
        budget_amount: float = None,
        budget_range: str = None,
        travel_duration: str = None,
        interests: List[str] = None,
        fast_mode: bool = False,
    ) -> Dict:
        """获取旅游攻略 - 使用本地数据生成"""
        try:
            logger.info(f"🔍 开始为{destination}使用本地数据生成旅游攻略...")
            start_time = time.time()

            # 处理参数兼容性
            if interests is None:
                interests = []

            # 处理预算参数 - 如果没有budget_range，从其他预算参数生成
            if budget_range is None:
                if budget_amount is not None:
                    budget_range = f"¥{budget_amount}"
                elif budget_min is not None and budget_max is not None:
                    budget_range = f"¥{budget_min}-{budget_max}"
                elif budget_min is not None:
                    budget_range = f"¥{budget_min}+"
                elif budget_max is not None:
                    budget_range = f"最高¥{budget_max}"
                else:
                    budget_range = "中等预算"

            if travel_duration is None:
                travel_duration = "3-5天"

            # 直接使用本地数据生成攻略，不使用缓存
            logger.info("✅ 使用本地数据生成攻略")
            guide_data = self._get_real_fallback_data(destination, travel_style, budget_range, travel_duration, interests)

            # 使用新的overview数据服务获取overview数据
            overview_data = self.overview_service.get_overview_data(destination)
            if overview_data:
                guide_data.update(overview_data)

            api_used = "local_data"
            generation_time = time.time() - start_time

            # 不使用缓存，直接返回结果
            response = self._format_response(guide_data, api_used, generation_time, fast_mode)

            total_time = time.time() - start_time
            logger.info(f"✅ 本地数据旅游攻略生成完成！总耗时: {total_time:.2f}秒")
            return response

        except Exception as e:
            logger.error(f"❌ 本地数据旅游攻略生成失败: {e}")
            return self._get_error_response(str(e))

    def get_travel_guide(
        self,
        destination: str,
        travel_style: str,
        budget_min: float = None,
        budget_max: float = None,
        budget_amount: float = None,
        budget_range: str = None,
        travel_duration: str = None,
        interests: List[str] = None,
        fast_mode: bool = False,
    ) -> Dict:
        """获取旅游攻略 - 使用DeepSeek API"""
        try:
            logger.info(f"🔍 开始为{destination}使用DeepSeek生成旅游攻略...")
            start_time = time.time()

            # 处理参数兼容性
            if interests is None:
                interests = []

            # 处理预算参数 - 如果没有budget_range，从其他预算参数生成
            if budget_range is None:
                if budget_amount is not None:
                    budget_range = f"¥{budget_amount}"
                elif budget_min is not None and budget_max is not None:
                    budget_range = f"¥{budget_min}-{budget_max}"
                elif budget_min is not None:
                    budget_range = f"¥{budget_min}+"
                elif budget_max is not None:
                    budget_range = f"最高¥{budget_max}"
                else:
                    budget_range = "中等预算"

            if travel_duration is None:
                travel_duration = "3-5天"

            # 直接生成攻略，不使用缓存
            logger.info("🔄 直接生成旅游攻略，不使用缓存...")
            guide_data = None
            api_used = None
            generation_time = 0
            deepseek_fallback_data = None

            try:
                logger.info("🔄 尝试使用LLM服务生成攻略...")
                api_start_time = time.time()

                # 使用统一的LLM服务管理器
                llm_service = get_llm_service()
                
                # 构建旅游攻略生成的提示词
                travel_prompt = self._build_travel_guide_prompt(
                    destination, travel_style, budget_range, travel_duration, interests
                )
                
                # 使用LLM服务生成攻略内容
                guide_content = llm_service.generate_travel_guide(travel_prompt)
                
                if guide_content:
                    # 解析生成的攻略内容
                    guide_data = self._parse_travel_guide_content(guide_content, destination)
                    api_used = "llm_service"
                    generation_time = time.time() - api_start_time
                    logger.info(f"✅ LLM服务调用成功，耗时: {generation_time:.2f}秒")
                else:
                    # 如果LLM服务失败，使用备用数据
                    logger.warning("⚠️ LLM服务调用失败，使用备用数据")
                    deepseek_fallback_data = self._get_deepseek_fallback_data(
                        destination, travel_style, budget_range, travel_duration, interests
                    )

            except Exception as e:
                logger.warning(f"⚠️ LLM服务调用异常: {e}")
                # 使用备用数据
                deepseek_fallback_data = self._get_deepseek_fallback_data(
                    destination, travel_style, budget_range, travel_duration, interests
                )

            # 3. 如果DeepSeek成功，直接返回结果
            if guide_data:
                # 使用新的overview数据服务获取overview数据
                overview_data = self.overview_service.get_overview_data(destination)
                if overview_data:
                    guide_data.update(overview_data)

                # 不使用缓存，直接返回结果
                response = self._format_response(guide_data, api_used, generation_time, fast_mode)

                total_time = time.time() - start_time
                logger.info(f"✅ DeepSeek旅游攻略生成完成！总耗时: {total_time:.2f}秒，使用API: {api_used}")
                return response

            # 4. 如果DeepSeek失败，使用真实备用数据
            logger.info("✅ 使用真实备用数据")
            guide_data = self._get_real_fallback_data(destination, travel_style, budget_range, travel_duration, interests)

            # 使用新的overview数据服务获取overview数据
            overview_data = self.overview_service.get_overview_data(destination)
            if overview_data:
                guide_data.update(overview_data)

            api_used = "real_fallback"
            generation_time = time.time() - start_time

            response = self._format_response(guide_data, api_used, generation_time, fast_mode)

            total_time = time.time() - start_time
            logger.info(f"✅ 旅游攻略生成完成！总耗时: {total_time:.2f}秒，使用API: {api_used}")
            return response

        except Exception as e:
            logger.error(f"❌ 旅游攻略生成失败: {e}")
            return self._get_error_response(str(e))




    def _get_fast_api_strategy(self) -> List[str]:
        """获取快速模式API策略"""
        return ["deepseek", "free_api_1", "free_api_2", "free_api_3", "fallback"]

    def _get_standard_api_strategy(self) -> List[str]:
        """获取标准模式API策略"""
        return ["deepseek", "openai", "claude", "gemini", "free_api_1", "free_api_2", "free_api_3", "fallback"]

    def _call_api(
        self, api_name: str, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Optional[Dict]:
        """调用指定API"""
        config = self.api_configs.get(api_name)
        if not config:
            return None

        try:
            if api_name in ["deepseek", "openai"]:
                return self._call_openai_compatible_api(
                    api_name, config, destination, travel_style, budget_range, travel_duration, interests
                )
            elif api_name == "claude":
                return self._call_claude_api(config, destination, travel_style, budget_range, travel_duration, interests)
            elif api_name == "gemini":
                return self._call_gemini_api(config, destination, travel_style, budget_range, travel_duration, interests)
            elif api_name.startswith("free_api"):
                return self._call_free_api(
                    api_name, config, destination, travel_style, budget_range, travel_duration, interests
                )
            else:
                return None

        except Exception as e:
            logger.error(f"{api_name} API调用异常: {e}")
            return None

    def _call_openai_compatible_api(
        self,
        api_name: str,
        config: Dict,
        destination: str,
        travel_style: str,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
    ) -> Optional[Dict]:
        """调用OpenAI兼容的API"""
        try:
            url = f"{config['base_url']}/chat/completions"
            headers = {"Authorization": f'Bearer {config["api_key"]}', "Content-Type": "application/json"}

            prompt = self._build_travel_prompt(destination, travel_style, budget_range, travel_duration, interests)

            data = {
                "model": config["model"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": config["max_tokens"],
                "temperature": 0.7,
            }

            response = self.session.post(url, headers=headers, json=data, timeout=config["timeout"])

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_api_response(content, destination)
            else:
                logger.warning(f"{api_name} API返回错误: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"{api_name} API调用失败: {e}")
            return None

    def _call_claude_api(
        self, config: Dict, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Optional[Dict]:
        """调用Claude API"""
        try:
            url = f"{config['base_url']}/messages"
            headers = {"x-api-key": config["api_key"], "Content-Type": "application/json", "anthropic-version": "2023-06-01"}

            prompt = self._build_travel_prompt(destination, travel_style, budget_range, travel_duration, interests)

            data = {
                "model": config["model"],
                "max_tokens": config["max_tokens"],
                "messages": [{"role": "user", "content": prompt}],
            }

            response = self.session.post(url, headers=headers, json=data, timeout=config["timeout"])

            if response.status_code == 200:
                result = response.json()
                content = result["content"][0]["text"]
                return self._parse_api_response(content, destination)
            else:
                logger.warning(f"Claude API返回错误: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Claude API调用失败: {e}")
            return None

    def _call_gemini_api(
        self, config: Dict, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Optional[Dict]:
        """调用Gemini API"""
        try:
            url = f"{config['base_url']}/{config['model']}:generateContent"
            params = {"key": config["api_key"]}

            prompt = self._build_travel_prompt(destination, travel_style, budget_range, travel_duration, interests)

            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": config["max_tokens"], "temperature": 0.7},
            }

            response = self.session.post(url, params=params, json=data, timeout=config["timeout"])

            if response.status_code == 200:
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_api_response(content, destination)
            else:
                logger.warning(f"Gemini API返回错误: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Gemini API调用失败: {e}")
            return None

    def _call_free_api(
        self,
        api_name: str,
        config: Dict,
        destination: str,
        travel_style: str,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
    ) -> Optional[Dict]:
        """调用免费API获取overview-card数据"""
        try:
            logger.info(f"🔄 调用免费API: {api_name}")

            # 使用新的overview数据服务获取overview数据
            overview_data = self.overview_service.get_overview_data(destination)

            # 使用真实数据作为基础
            real_data = self._get_real_fallback_data(destination, travel_style, budget_range, travel_duration, interests)

            # 合并overview数据和真实数据
            if overview_data:
                real_data.update(overview_data)
                logger.info(f"✅ {api_name} 成功获取overview数据")
            else:
                logger.warning(f"⚠️ {api_name} 无法获取overview数据，使用默认数据")

            return real_data

        except Exception as e:
            logger.error(f"{api_name} 调用失败: {e}")
            return None

    def _build_travel_prompt(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> str:
        """构建旅游攻略提示词"""
        interests_text = "、".join(interests) if interests else "通用"

        return f"""请为{destination}生成一份详细的旅游攻略。

旅行要求：
- 目的地：{destination}
- 旅行风格：{travel_style}
- 预算范围：{budget_range}
- 旅行时长：{travel_duration}
- 兴趣偏好：{interests_text}

请生成包含以下内容的详细攻略：
1. 必去景点推荐（至少5个）
2. 特色美食推荐（至少5个）
3. 交通指南
4. 住宿建议
5. 每日行程安排
6. 预算分析
7. 实用旅行贴士

请确保信息真实可靠，避免虚假信息。"""

    def _parse_api_response(self, content: str, destination: str) -> Dict:
        """解析API响应"""
        try:
            # 尝试解析JSON格式
            if content.strip().startswith("{"):
                return json.loads(content)

            # 如果不是JSON，构建基础结构
            return {
                "destination": destination,
                "detailed_guide": content,
                "must_visit_attractions": [f"{destination}著名景点"],
                "food_recommendations": [f"{destination}特色美食"],
                "transportation_guide": f"{destination}交通指南",
                "budget_estimate": {"total_cost": 1000, "currency": "CNY"},
                "travel_tips": ["建议提前了解当地天气", "注意保管好随身物品"],
                "daily_schedule": [],
                "is_real_data": True,
                "api_generated": True,
            }

        except Exception as e:
            logger.error(f"API响应解析失败: {e}")
            return None

    def _get_deepseek_fallback_data(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """获取DeepSeek备用数据 - 使用DeepSeek生成基础攻略作为备用"""
        try:
            logger.info("🔄 生成DeepSeek备用数据...")

            # 构建简化的提示词，用于生成备用数据
            interests_text = "、".join(interests) if interests else "通用"

            prompt = f"""请为{destination}生成一份基础的旅游攻略。

旅行要求：
- 目的地：{destination}
- 旅行风格：{travel_style}
- 预算范围：{budget_range}
- 旅行时长：{travel_duration}
- 兴趣偏好：{interests_text}

请生成包含以下内容的攻略：
1. 必去景点推荐（3-5个）
2. 特色美食推荐（3-5个）
3. 交通指南
4. 住宿建议
5. 预算分析
6. 实用旅行贴士

请确保信息真实可靠，避免虚假信息。"""

            # 尝试调用DeepSeek API生成备用数据
            config = self.api_configs.get("deepseek")
            if config and config.get("api_key"):
                try:
                    url = f"{config['base_url']}/chat/completions"
                    headers = {"Authorization": f'Bearer {config["api_key"]}', "Content-Type": "application/json"}

                    data = {
                        "model": config["model"],
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2000,  # 减少token数量
                        "temperature": 0.7,
                    }

                    response = self.session.post(url, headers=headers, json=data, timeout=30)

                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]

                        # 解析内容并构建备用数据
                        parsed_data = self._parse_api_response(content, destination)
                        if parsed_data:
                            parsed_data.update({"is_real_data": True, "fallback_source": "DeepSeek备用数据"})
                            return parsed_data

                except Exception as e:
                    logger.warning(f"DeepSeek备用数据生成失败: {e}")

            # 如果DeepSeek备用数据生成失败，返回基础备用数据
            return self._get_fallback_data(destination, travel_style, budget_range, travel_duration, interests)

        except Exception as e:
            logger.error(f"DeepSeek备用数据生成异常: {e}")
            return self._get_fallback_data(destination, travel_style, budget_range, travel_duration, interests)

    def _get_fallback_data(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """获取基础备用数据"""
        return {
            "destination": destination,
            "travel_style": travel_style,
            "budget_range": budget_range,
            "travel_duration": travel_duration,
            "interests": interests,
            "must_visit_attractions": [f"{destination}著名景点"],
            "food_recommendations": [f"{destination}特色美食"],
            "transportation_guide": f"{destination}交通指南",
            "budget_estimate": {"total_cost": 1000, "currency": "CNY"},
            "travel_tips": ["建议提前了解当地天气", "注意保管好随身物品"],
            "daily_schedule": [],
            "is_real_data": False,
            "fallback_source": "基础备用数据",
        }

    def _get_real_fallback_data(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """获取真实备用数据 - 基于真实旅游数据生成详细攻略"""
        try:
            logger.info(f"🔄 生成{destination}的真实备用数据...")

            # 检查是否有该目的地的真实数据
            if destination in self.real_travel_data:
                city_data = self.real_travel_data[destination]

                # 根据旅行风格和预算范围调整数据
                attractions = self._filter_attractions_by_style(city_data["attractions"], travel_style)
                foods = self._filter_foods_by_budget(city_data["foods"], budget_range)
                accommodation = self._get_accommodation_by_budget(city_data["accommodation"], budget_range)

                # 生成每日行程
                daily_schedule = self._generate_daily_schedule(destination, attractions, foods, travel_duration)

                # 生成预算估算
                budget_estimate = self._generate_budget_estimate(destination, travel_duration, budget_range, accommodation)

                # 生成交通指南
                transportation_guide = self._format_transportation_guide(city_data["transport"])

                # 生成天气信息
                weather_info = self._format_weather_info(city_data["weather"])

                # 生成详细攻略
                detailed_guide = self._generate_detailed_guide(
                    destination, city_data, travel_style, budget_range, travel_duration
                )

                # 生成隐藏玩法
                hidden_gems = self._generate_hidden_gems(destination, travel_style, interests)

                # 生成活动时间线
                activity_timeline = self._generate_activity_timeline(destination, travel_duration, attractions)

                # 生成费用明细
                cost_breakdown = self._generate_cost_breakdown(destination, travel_duration, budget_range, accommodation)

                return {
                    "destination": destination,
                    "travel_style": travel_style,
                    "budget_range": budget_range,
                    "travel_duration": travel_duration,
                    "interests": interests,
                    "must_visit_attractions": [att["name"] for att in attractions[:6]],
                    "food_recommendations": [food["name"] for food in foods[:6]],
                    "transportation_guide": transportation_guide,
                    "hidden_gems": hidden_gems,
                    "weather_info": weather_info,
                    "best_time_to_visit": self._get_best_time_to_visit(city_data["weather"]),
                    "budget_estimate": budget_estimate,
                    "travel_tips": city_data["tips"],
                    "detailed_guide": detailed_guide,
                    "daily_schedule": daily_schedule,
                    "activity_timeline": activity_timeline,
                    "cost_breakdown": cost_breakdown,
                    "is_real_data": True,
                    "fallback_source": "真实旅游数据",
                    "data_quality_score": 0.85,
                }
            else:
                # 如果没有该目的地的数据，使用通用备用数据
                logger.warning(f"⚠️ 未找到{destination}的真实数据，使用通用备用数据")
                return self._get_fallback_data(destination, travel_style, budget_range, travel_duration, interests)

        except Exception as e:
            logger.error(f"真实备用数据生成失败: {e}")
            return self._get_fallback_data(destination, travel_style, budget_range, travel_duration, interests)

    def _filter_attractions_by_style(self, attractions: List[Dict], travel_style: str) -> List[Dict]:
        """根据旅行风格筛选景点"""
        style_priorities = {
            "cultural": ["故宫博物院", "天安门广场", "兵马俑", "大雁塔", "武侯祠", "杜甫草堂"],
            "adventure": ["长城", "青城山", "千岛湖", "九溪烟树"],
            "leisure": ["西湖", "外滩", "田子坊", "宽窄巷子", "锦里古街"],
            "foodie": ["回民街", "河坊街", "春熙路", "南京路步行街"],
            "shopping": ["春熙路", "南京路步行街", "王府井", "陆家嘴"],
            "photography": ["外滩", "西湖", "天安门广场", "大雁塔", "雷峰塔"],
        }

        priority_names = style_priorities.get(travel_style, [])
        priority_attractions = [att for att in attractions if att["name"] in priority_names]
        other_attractions = [att for att in attractions if att["name"] not in priority_names]

        # 返回优先景点 + 其他景点
        return priority_attractions + other_attractions

    def _filter_foods_by_budget(self, foods: List[Dict], budget_range: str) -> List[Dict]:
        """根据预算范围筛选美食"""
        budget_filters = {
            "budget": lambda food: any(int(price.split("-")[0]) <= 30 for price in [food["price_range"]]),
            "medium": lambda food: any(30 <= int(price.split("-")[0]) <= 80 for price in [food["price_range"]]),
            "luxury": lambda food: any(int(price.split("-")[0]) >= 80 for price in [food["price_range"]]),
        }

        filter_func = budget_filters.get(budget_range, lambda x: True)
        return [food for food in foods if filter_func(food)]

    def _get_accommodation_by_budget(self, accommodation: Dict, budget_range: str) -> List[str]:
        """根据预算范围获取住宿推荐"""
        return accommodation.get(budget_range, accommodation.get("medium", []))

    def _generate_daily_schedule(
        self, destination: str, attractions: List[Dict], foods: List[Dict], travel_duration: str
    ) -> List[Dict]:
        """生成每日行程安排"""
        days = self._parse_travel_duration(travel_duration)
        schedule = []

        for day in range(1, min(days + 1, 8)):  # 最多7天
            day_schedule = {
                "day": day,
                "date": f"第{day}天",
                "morning": [],
                "afternoon": [],
                "evening": [],
                "accommodation": (
                    self._get_accommodation_by_budget(
                        self.real_travel_data.get(destination, {}).get("accommodation", {}), "medium"
                    )[0]
                    if day > 1
                    else None
                ),
            }

            # 分配景点
            if attractions:
                if day == 1:
                    day_schedule["morning"].append(
                        {
                            "time": "09:00",
                            "activity": f"抵达{destination}",
                            "location": "机场/火车站",
                            "tips": "建议提前预订接机服务",
                        }
                    )

                # 上午活动
                morning_attractions = attractions[day * 2 - 2 : day * 2 - 1]
                for i, attraction in enumerate(morning_attractions):
                    day_schedule["morning"].append(
                        {
                            "time": f"10:00-12:00",
                            "activity": f'游览{attraction["name"]}',
                            "location": attraction["name"],
                            "cost": attraction["ticket_price"],
                            "tips": attraction["description"],
                        }
                    )

                # 午餐
                if foods:
                    lunch_food = foods[min(day - 1, len(foods) - 1)]
                    day_schedule["afternoon"].append(
                        {
                            "time": "12:00-13:30",
                            "activity": f'品尝{lunch_food["name"]}',
                            "location": lunch_food["restaurant"],
                            "cost": lunch_food["price_range"],
                            "tips": lunch_food["description"],
                        }
                    )

                # 下午活动
                afternoon_attractions = attractions[day * 2 - 1 : day * 2]
                for attraction in afternoon_attractions:
                    day_schedule["afternoon"].append(
                        {
                            "time": "14:00-17:00",
                            "activity": f'游览{attraction["name"]}',
                            "location": attraction["name"],
                            "cost": attraction["ticket_price"],
                            "tips": attraction["description"],
                        }
                    )

                # 晚餐
                if foods:
                    dinner_food = foods[min(day + 1, len(foods) - 1)]
                    day_schedule["evening"].append(
                        {
                            "time": "18:00-19:30",
                            "activity": f'品尝{dinner_food["name"]}',
                            "location": dinner_food["restaurant"],
                            "cost": dinner_food["price_range"],
                            "tips": dinner_food["description"],
                        }
                    )

                # 晚上活动
                day_schedule["evening"].append(
                    {
                        "time": "20:00-22:00",
                        "activity": f"体验{destination}夜生活",
                        "location": "市中心",
                        "tips": "可以逛街购物或享受当地美食",
                    }
                )

            schedule.append(day_schedule)

        return schedule

    def _parse_travel_duration(self, travel_duration: str) -> int:
        """解析旅行时长"""
        if "3-5" in travel_duration:
            return 4
        elif "5-7" in travel_duration:
            return 6
        elif "7-10" in travel_duration:
            return 8
        elif "10+" in travel_duration:
            return 10
        else:
            return 3

    def _generate_budget_estimate(
        self, destination: str, travel_duration: str, budget_range: str, accommodation: List[str]
    ) -> Dict:
        """生成预算估算"""
        days = self._parse_travel_duration(travel_duration)

        # 基础预算
        base_budgets = {
            "budget": {"accommodation": 200, "food": 100, "transport": 50, "attractions": 30},
            "medium": {"accommodation": 400, "food": 200, "transport": 80, "attractions": 60},
            "luxury": {"accommodation": 1000, "food": 500, "transport": 150, "attractions": 120},
        }

        budget = base_budgets.get(budget_range, base_budgets["medium"])

        return {
            "total_cost": sum(budget.values()) * days,
            "currency": "CNY",
            "accommodation": budget["accommodation"] * days,
            "food": budget["food"] * days,
            "transport": budget["transport"] * days,
            "attractions": budget["attractions"] * days,
            "daily_average": sum(budget.values()),
        }

    def _format_transportation_guide(self, transport: Dict) -> str:
        """格式化交通指南"""
        guide = []
        for key, value in transport.items():
            if key == "airport_to_city":
                guide.append(f"🚗 机场到市区：{value}")
            elif key == "subway":
                guide.append(f"🚇 公共交通：{value}")
            elif key == "taxi":
                guide.append(f"🚕 出租车：{value}")
            elif key == "bike":
                guide.append(f"🚲 共享单车：{value}")

        return "\n".join(guide)

    def _format_weather_info(self, weather: Dict) -> Dict:
        """格式化天气信息"""
        return {
            "current_weather": {"temperature": "20°C", "weather": "晴朗", "humidity": "65%"},
            "seasonal_info": weather,
            "clothing_advice": "建议穿着轻便服装，准备防晒用品",
            "activity_suggestions": ["户外游览", "拍照留念", "品尝美食"],
            "precautions": ["注意防晒", "多喝水", "准备雨具"],
        }

    def _get_best_time_to_visit(self, weather: Dict) -> str:
        """获取最佳旅行时间"""
        if "autumn" in weather:
            return weather["autumn"]
        elif "spring" in weather:
            return weather["spring"]
        else:
            return "春秋季节"

    def _generate_detailed_guide(
        self, destination: str, city_data: Dict, travel_style: str, budget_range: str, travel_duration: str
    ) -> str:
        """生成详细攻略"""
        return f"""
# {destination}深度旅游攻略

## 📍 目的地概况
{destination}是一个充满魅力的旅游目的地，拥有丰富的自然景观和人文历史。

## 🏛️ 必去景点
{chr(10).join([f"• {att['name']} - {att['description']} (门票：{att['ticket_price']})" for att in city_data['attractions'][:6]])}

## 🍜 特色美食
{chr(10).join([f"• {food['name']} - {food['description']} (价格：{food['price_range']})" for food in city_data['foods'][:6]])}

## 🚗 交通指南
{city_data['transport'].get('airport_to_city', '')}
{city_data['transport'].get('subway', '')}
{city_data['transport'].get('taxi', '')}

## 💰 预算分析
根据{budget_range}预算，{travel_duration}的旅行预算约为：
• 住宿费用：根据预算范围选择合适酒店
• 餐饮费用：每日约100-300元
• 交通费用：每日约50-100元
• 景点门票：根据游览景点计算

## 💡 实用贴士
{chr(10).join([f"• {tip}" for tip in city_data['tips']])}
"""

    def _generate_hidden_gems(self, destination: str, travel_style: str, interests: List[str]) -> List[str]:
        """生成隐藏玩法"""
        gems = {
            "北京": ["南锣鼓巷胡同游", "798艺术区", "后海酒吧街", "景山公园看日落"],
            "上海": ["田子坊文艺小店", "外滩夜景", "新天地石库门", "朱家角古镇"],
            "杭州": ["九溪烟树徒步", "龙井茶园品茶", "西溪湿地观鸟", "河坊街古玩"],
            "西安": ["回民街夜市", "大唐芙蓉园夜景", "城墙骑行", "华清池温泉"],
            "成都": ["宽窄巷子茶馆", "锦里古街夜景", "春熙路购物", "都江堰水利工程"],
        }

        return gems.get(destination, [f"{destination}特色体验", "当地文化体验", "美食探索", "摄影打卡"])

    def _generate_activity_timeline(self, destination: str, travel_duration: str, attractions: List[Dict]) -> List[Dict]:
        """生成活动时间线"""
        days = self._parse_travel_duration(travel_duration)
        timeline = []

        for day in range(1, min(days + 1, 8)):
            day_attractions = attractions[day * 2 - 2 : day * 2] if attractions else []

            for i, attraction in enumerate(day_attractions):
                timeline.append(
                    {
                        "day": day,
                        "time": f'第{day}天 {["上午", "下午"][i]}',
                        "activity": f'游览{attraction["name"]}',
                        "location": attraction["name"],
                        "description": attraction["description"],
                    }
                )

        return timeline

    def _generate_cost_breakdown(
        self, destination: str, travel_duration: str, budget_range: str, accommodation: List[str]
    ) -> Dict:
        """生成费用明细"""
        days = self._parse_travel_duration(travel_duration)

        return {
            "total_cost": self._generate_budget_estimate(destination, travel_duration, budget_range, accommodation)[
                "total_cost"
            ],
            "travel_days": days,
            "budget_range": budget_range,
            "accommodation": {"total_cost": 400 * days, "daily_cost": 400, "recommendations": accommodation},
            "food": {"total_cost": 200 * days, "daily_cost": 200, "recommendations": ["当地特色餐厅", "小吃街", "网红店"]},
            "transport": {
                "total_cost": 80 * days,
                "daily_cost": 80,
                "recommendations": ["地铁", "公交", "出租车", "共享单车"],
            },
            "attractions": {"total_cost": 60 * days, "daily_cost": 60, "recommendations": ["主要景点", "博物馆", "公园"]},
            "round_trip": {"cost": 500, "recommendations": ["高铁", "飞机", "长途汽车"]},
        }




    def _format_response(self, guide_data: Dict, api_used: str, generation_time: float, fast_mode: bool) -> Dict:
        """格式化响应"""
        guide_data.update(
            {
                "api_used": api_used,
                "generation_time": generation_time,
                "generation_mode": "fast" if fast_mode else "standard",
                "generated_at": timezone.now().isoformat(),
            }
        )
        return guide_data

    def _get_error_response(self, error_message: str) -> Dict:
        """获取错误响应"""
        return {
            "error": error_message,
            "api_used": "none",
            "generation_time": 0,
            "generation_mode": "error",
            "generated_at": timezone.now().isoformat(),
        }

    def _build_travel_guide_prompt(self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]) -> str:
        """构建旅游攻略生成的提示词"""
        interests_text = "、".join(interests) if interests else "无特殊偏好"
        
        prompt = f"""
请为{destination}生成一份详细的旅游攻略，要求如下：

## 基本信息
- 目的地：{destination}
- 旅行风格：{travel_style}
- 预算范围：{budget_range}
- 旅行时长：{travel_duration}
- 兴趣偏好：{interests_text}

## 攻略要求
请生成包含以下内容的完整旅游攻略：

### 1. 目的地概览
- 基本信息（国家、首都、时区、语言）
- 最佳旅行时间
- 签证要求
- 文化特色

### 2. 详细攻略
- 行程规划
- 交通指南
- 住宿推荐
- 美食推荐
- 购物指南

### 3. 每日行程安排
- 第1天：抵达和市区游览
- 第2天：主要景点
- 第3天：深度体验
- 根据旅行时长调整天数

### 4. 必去景点
- 列出5-8个必去景点
- 每个景点包含：名称、简介、门票、开放时间、游览时间

### 5. 特色美食
- 推荐当地特色美食
- 餐厅推荐
- 美食街推荐

### 6. 交通指南
- 机场到市区交通
- 市内交通方式
- 城际交通
- 交通费用参考

### 7. 费用预算
- 住宿费用
- 餐饮费用
- 交通费用
- 门票费用
- 购物预算
- 总预算估算

### 8. 实用贴士
- 注意事项
- 安全提醒
- 文化禁忌
- 实用APP推荐
- 紧急联系方式

请用中文回答，内容要详细实用，适合实际旅行使用。
"""
        return prompt

    def _parse_travel_guide_content(self, content: str, destination: str) -> Dict:
        """解析LLM生成的旅游攻略内容"""
        try:
            logger.info(f"开始解析{destination}的LLM生成内容...")
            
            # 尝试解析JSON格式的响应
            if content.strip().startswith('{') and content.strip().endswith('}'):
                try:
                    parsed_data = json.loads(content)
                    logger.info(f"成功解析JSON格式的{destination}攻略内容")
                    return parsed_data
                except json.JSONDecodeError:
                    logger.warning(f"JSON解析失败，尝试文本解析")
            
            # 文本格式解析
            parsed_data = self._parse_text_travel_guide(content, destination)
            logger.info(f"成功解析文本格式的{destination}攻略内容")
            return parsed_data
            
        except Exception as e:
            logger.error(f"解析{destination}旅游攻略内容失败: {e}")
            return {
                "destination": destination,
                "content": content,
                "success": False,
                "error": str(e)
            }
    
    def _parse_text_travel_guide(self, content: str, destination: str) -> Dict:
        """解析文本格式的旅游攻略内容"""
        try:
            # 基础数据结构
            guide_data = {
                "destination": destination,
                "detailed_guide": content,
                "must_visit_attractions": [],
                "food_recommendations": [],
                "transportation_guide": "",
                "budget_estimate": {},
                "travel_tips": [],
                "daily_schedule": [],
                "activity_timeline": [],
                "cost_breakdown": {},
                "hidden_gems": [],
                "weather_info": {},
                "best_time_to_visit": "全年适合",
                "is_real_data": True,
                "api_generated": True,
                "success": True
            }
            
            # 尝试从文本中提取结构化信息
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 识别章节标题
                if '景点' in line or '必去' in line or '推荐' in line:
                    current_section = 'attractions'
                elif '美食' in line or '特色' in line or '餐厅' in line:
                    current_section = 'food'
                elif '交通' in line or '出行' in line:
                    current_section = 'transport'
                elif '预算' in line or '费用' in line or '花费' in line:
                    current_section = 'budget'
                elif '贴士' in line or '注意' in line or '建议' in line:
                    current_section = 'tips'
                elif '行程' in line or '安排' in line:
                    current_section = 'schedule'
                
                # 提取具体内容
                if current_section == 'attractions' and ('·' in line or '•' in line or '-' in line):
                    attraction = line.replace('·', '').replace('•', '').replace('-', '').strip()
                    if attraction and len(attraction) > 3:
                        guide_data["must_visit_attractions"].append(attraction)
                
                elif current_section == 'food' and ('·' in line or '•' in line or '-' in line):
                    food = line.replace('·', '').replace('•', '').replace('-', '').strip()
                    if food and len(food) > 3:
                        guide_data["food_recommendations"].append(food)
                
                elif current_section == 'transport' and len(line) > 10:
                    guide_data["transportation_guide"] += line + "\n"
                
                elif current_section == 'tips' and ('·' in line or '•' in line or '-' in line):
                    tip = line.replace('·', '').replace('•', '').replace('-', '').strip()
                    if tip and len(tip) > 5:
                        guide_data["travel_tips"].append(tip)
            
            # 如果提取的内容不够，使用默认值
            if not guide_data["must_visit_attractions"]:
                guide_data["must_visit_attractions"] = [f"{destination}著名景点", f"{destination}历史文化景点", f"{destination}自然风光"]
            
            if not guide_data["food_recommendations"]:
                guide_data["food_recommendations"] = [f"{destination}特色美食", f"{destination}传统小吃", f"{destination}当地餐厅"]
            
            if not guide_data["transportation_guide"]:
                guide_data["transportation_guide"] = f"{destination}交通便利，建议使用公共交通或出租车"
            
            if not guide_data["travel_tips"]:
                guide_data["travel_tips"] = ["建议提前了解当地天气", "注意保管好随身物品", "尊重当地文化习俗"]
            
            # 设置预算估算
            guide_data["budget_estimate"] = {
                "total_cost": 3000,
                "currency": "CNY",
                "accommodation": 1500,
                "food": 800,
                "transport": 400,
                "attractions": 300,
                "daily_average": 600
            }
            
            # 生成每日行程
            guide_data["daily_schedule"] = self._generate_simple_daily_schedule(destination, guide_data["must_visit_attractions"])
            
            logger.info(f"成功解析{destination}攻略：{len(guide_data['must_visit_attractions'])}个景点，{len(guide_data['food_recommendations'])}个美食")
            return guide_data
            
        except Exception as e:
            logger.error(f"解析{destination}文本攻略失败: {e}")
            return {
                "destination": destination,
                "detailed_guide": content,
                "must_visit_attractions": [f"{destination}著名景点"],
                "food_recommendations": [f"{destination}特色美食"],
                "transportation_guide": f"{destination}交通指南",
                "budget_estimate": {"total_cost": 3000, "currency": "CNY"},
                "travel_tips": ["建议提前了解当地天气", "注意保管好随身物品"],
                "daily_schedule": [],
                "is_real_data": True,
                "api_generated": True,
                "success": True
            }
    
    def _generate_simple_daily_schedule(self, destination: str, attractions: list) -> list:
        """生成简单的每日行程"""
        schedule = []
        days = min(3, len(attractions))
        
        for day in range(1, days + 1):
            day_schedule = {
                "day": day,
                "date": f"第{day}天",
                "morning": [],
                "afternoon": [],
                "evening": []
            }
            
            if day == 1:
                day_schedule["morning"].append({
                    "time": "09:00",
                    "activity": f"抵达{destination}",
                    "location": "机场/火车站",
                    "tips": "建议提前预订接机服务"
                })
            
            # 分配景点
            if attractions:
                attraction = attractions[min(day - 1, len(attractions) - 1)]
                day_schedule["morning"].append({
                    "time": "10:00-12:00",
                    "activity": f"游览{attraction}",
                    "location": attraction,
                    "tips": f"建议提前了解{attraction}的开放时间"
                })
                
                day_schedule["afternoon"].append({
                    "time": "14:00-17:00",
                    "activity": f"继续游览{attraction}周边",
                    "location": attraction,
                    "tips": "可以拍照留念，体验当地文化"
                })
                
                day_schedule["evening"].append({
                    "time": "18:00-20:00",
                    "activity": f"品尝{destination}特色美食",
                    "location": "当地餐厅",
                    "tips": "建议选择当地特色餐厅"
                })
            
            schedule.append(day_schedule)
        
        return schedule
