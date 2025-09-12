#!/usr/bin/env python3
"""
增强版旅游数据服务 - 使用DeepSeek和其他免费API的真实数据
"""

import logging
from datetime import datetime
from typing import Dict, List

import requests

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTravelService:
    """增强版旅游数据服务 - 使用真实API数据"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )

        # 初始化大模型服务
        self.llm_available = True
        try:
            from .llm_service import generate_travel_guide
            self.generate_travel_guide = generate_travel_guide
            logger.info("✅ 大模型服务初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ 大模型服务初始化失败: {e}")
            self.llm_available = False

        # 免费API配置
        self.free_apis = {
            "weather": "wttr.in",
            "geocoding": "nominatim.openstreetmap.org",
            "places": "api.opentripmap.com",
            "wikipedia": "zh.wikipedia.org",
            "currency": "api.exchangerate-api.com",
            "timezone": "worldtimeapi.org",
        }

    def get_real_travel_guide(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """获取真实旅游攻略数据"""
        try:
            logger.info(f"🔍 开始为{destination}生成真实旅游攻略...")

            # 1. 获取基础地理信息
            geo_info = self._get_geolocation_info(destination)

            # 2. 获取真实天气数据
            weather_info = self._get_real_weather_data(destination, geo_info)

            # 3. 获取真实景点数据
            attractions_data = self._get_real_attractions_data(destination, geo_info)

            # 4. 获取真实美食数据
            food_data = self._get_real_food_data(destination)

            # 5. 获取真实交通数据
            transport_data = self._get_real_transport_data(destination, geo_info)

            # 6. 获取真实住宿数据
            accommodation_data = self._get_real_accommodation_data(destination, budget_range)

            # 7. 使用DeepSeek生成增强内容
            enhanced_content = self._generate_enhanced_content_with_deepseek(
                destination, travel_style, budget_range, travel_duration, interests, attractions_data, food_data, weather_info
            )

            # 8. 合成最终攻略
            final_guide = self._synthesize_final_guide(
                destination,
                travel_style,
                budget_range,
                travel_duration,
                interests,
                geo_info,
                weather_info,
                attractions_data,
                food_data,
                transport_data,
                accommodation_data,
                enhanced_content,
            )

            logger.info("✅ 真实旅游攻略生成完成！")
            return final_guide

        except Exception as e:
            logger.error(f"❌ 真实旅游攻略生成失败: {e}")
            # 如果真实数据获取失败，使用DeepSeek生成基础攻略
            return self._generate_fallback_with_deepseek(destination, travel_style, budget_range, travel_duration, interests)

    def _get_geolocation_info(self, destination: str) -> Dict:
        """获取真实地理信息"""
        try:
            # 使用OpenStreetMap Nominatim API (免费)
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": destination, "format": "json", "limit": 1, "addressdetails": 1}

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    location = data[0]
                    return {
                        "lat": float(location["lat"]),
                        "lon": float(location["lon"]),
                        "display_name": location["display_name"],
                        "country": location.get("address", {}).get("country", ""),
                        "state": location.get("address", {}).get("state", ""),
                        "city": location.get("address", {}).get("city", ""),
                        "postcode": location.get("address", {}).get("postcode", ""),
                    }
        except Exception as e:
            logger.warning(f"地理信息获取失败: {e}")

        return {"lat": 0, "lon": 0, "display_name": destination}

    def _get_real_weather_data(self, destination: str, geo_info: Dict) -> Dict:
        """获取真实天气数据"""
        try:
            # 使用wttr.in API获取天气
            url = f"https://wttr.in/{destination}?format=j1"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                current = data["current_condition"][0]
                forecast = data["weather"][0]

                return {
                    "current": {
                        "temperature": float(current["temp_C"]),
                        "feels_like": float(current["FeelsLikeC"]),
                        "weather": current.get("lang_zh", [{"value": current["weatherDesc"][0]["value"]}])[0]["value"],
                        "humidity": int(current["humidity"]),
                        "wind_speed": float(current["windspeedKmph"]),
                        "visibility": float(current["visibility"]),
                        "pressure": float(current["pressure"]),
                    },
                    "forecast": {
                        "max_temp": float(forecast["hourly"][0]["tempC"]),
                        "min_temp": float(forecast["hourly"][0]["tempC"]),
                        "weather": forecast["hourly"][0]["weatherDesc"][0]["value"],
                        "chance_of_rain": int(forecast["hourly"][0]["chanceofrain"]),
                    },
                    "location": destination,
                    "last_updated": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.warning(f"天气数据获取失败: {e}")

        return {"error": "天气数据获取失败"}

    def _get_real_attractions_data(self, destination: str, geo_info: Dict) -> Dict:
        """获取真实景点数据"""
        try:
            attractions = []

            # 使用OpenTripMap API获取景点
            if geo_info.get("lat") and geo_info.get("lon"):
                url = "https://api.opentripmap.com/0.1/zh/places/radius"
                params = {
                    "radius": 10000,  # 10公里半径
                    "lon": geo_info["lon"],
                    "lat": geo_info["lat"],
                    "kinds": "cultural,historic,architecture,interesting_places,museums,monuments_and_memorials",
                    "limit": 20,
                    "format": "json",
                }

                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for place in data.get("features", []):
                        props = place.get("properties", {})
                        attractions.append(
                            {
                                "name": props.get("name", ""),
                                "type": props.get("kinds", ""),
                                "description": props.get("wikipedia_extracts", {}).get("text", ""),
                                "rating": props.get("rate", 0),
                                "distance": props.get("distance", 0),
                                "coordinates": place.get("geometry", {}).get("coordinates", []),
                            }
                        )

            # 使用维基百科获取景点信息
            wiki_attractions = self._get_wikipedia_attractions(destination)
            attractions.extend(wiki_attractions)

            return {"attractions": attractions, "total_count": len(attractions), "source": "OpenTripMap + Wikipedia"}

        except Exception as e:
            logger.warning(f"景点数据获取失败: {e}")

        return {"attractions": [], "total_count": 0, "error": "景点数据获取失败"}

    def _get_wikipedia_attractions(self, destination: str) -> List[Dict]:
        """从维基百科获取景点信息"""
        try:
            # 使用维基百科API搜索景点
            search_url = "https://zh.wikipedia.org/api/rest_v1/page/search/"
            params = {"q": f"{destination} 景点", "limit": 10}

            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                attractions = []

                for page in data.get("pages", []):
                    if "景点" in page.get("title", "") or "旅游" in page.get("title", ""):
                        attractions.append(
                            {
                                "name": page.get("title", ""),
                                "type": "wikipedia",
                                "description": page.get("extract", ""),
                                "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            }
                        )

                return attractions
        except Exception as e:
            logger.warning(f"维基百科景点获取失败: {e}")

        return []

    def _get_real_food_data(self, destination: str) -> Dict:
        """获取真实美食数据"""
        try:
            # 使用维基百科搜索美食信息
            search_url = "https://zh.wikipedia.org/api/rest_v1/page/search/"
            params = {"q": f"{destination} 美食 小吃", "limit": 15}

            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                foods = []

                for page in data.get("pages", []):
                    title = page.get("title", "")
                    if any(keyword in title for keyword in ["美食", "小吃", "菜", "面", "汤"]):
                        foods.append(
                            {
                                "name": title,
                                "description": page.get("extract", ""),
                                "type": "local_food",
                                "source": "wikipedia",
                            }
                        )

                return {"foods": foods, "total_count": len(foods), "source": "Wikipedia"}
        except Exception as e:
            logger.warning(f"美食数据获取失败: {e}")

        return {"foods": [], "total_count": 0, "error": "美食数据获取失败"}

    def _get_real_transport_data(self, destination: str, geo_info: Dict) -> Dict:
        """获取真实交通数据"""
        try:
            # 使用OpenTripMap获取交通信息
            if geo_info.get("lat") and geo_info.get("lon"):
                url = "https://api.opentripmap.com/0.1/zh/places/radius"
                params = {
                    "radius": 5000,
                    "lon": geo_info["lon"],
                    "lat": geo_info["lat"],
                    "kinds": "transport",
                    "limit": 10,
                    "format": "json",
                }

                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    transport_points = []

                    for place in data.get("features", []):
                        props = place.get("properties", {})
                        transport_points.append(
                            {
                                "name": props.get("name", ""),
                                "type": props.get("kinds", ""),
                                "distance": props.get("distance", 0),
                            }
                        )

                    return {
                        "transport_points": transport_points,
                        "airport_info": self._get_airport_info(destination),
                        "public_transport": self._get_public_transport_info(destination),
                    }
        except Exception as e:
            logger.warning(f"交通数据获取失败: {e}")

        return {"error": "交通数据获取失败"}

    def _get_airport_info(self, destination: str) -> Dict:
        """获取机场信息"""
        try:
            # 使用维基百科搜索机场信息
            search_url = "https://zh.wikipedia.org/api/rest_v1/page/search/"
            params = {"q": f"{destination} 机场", "limit": 5}

            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                airports = []

                for page in data.get("pages", []):
                    title = page.get("title", "")
                    if "机场" in title:
                        airports.append(
                            {
                                "name": title,
                                "description": page.get("extract", ""),
                                "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            }
                        )

                return {"airports": airports}
        except Exception as e:
            logger.warning(f"机场信息获取失败: {e}")

        return {"airports": []}

    def _get_public_transport_info(self, destination: str) -> Dict:
        """获取公共交通信息"""
        try:
            # 使用维基百科搜索公共交通信息
            search_url = "https://zh.wikipedia.org/api/rest_v1/page/search/"
            params = {"q": f"{destination} 地铁 公交", "limit": 5}

            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                transport_info = []

                for page in data.get("pages", []):
                    title = page.get("title", "")
                    if any(keyword in title for keyword in ["地铁", "公交", "交通"]):
                        transport_info.append(
                            {
                                "name": title,
                                "description": page.get("extract", ""),
                                "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            }
                        )

                return {"transport_info": transport_info}
        except Exception as e:
            logger.warning(f"公共交通信息获取失败: {e}")

        return {"transport_info": []}

    def _get_real_accommodation_data(self, destination: str, budget_range: str) -> Dict:
        """获取真实住宿数据"""
        try:
            # 使用维基百科搜索酒店信息
            search_url = "https://zh.wikipedia.org/api/rest_v1/page/search/"
            params = {"q": f"{destination} 酒店 住宿", "limit": 10}

            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                hotels = []

                for page in data.get("pages", []):
                    title = page.get("title", "")
                    if any(keyword in title for keyword in ["酒店", "宾馆", "住宿"]):
                        hotels.append(
                            {
                                "name": title,
                                "description": page.get("extract", ""),
                                "type": "hotel",
                                "budget_level": self._determine_budget_level(title, budget_range),
                                "url": page.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            }
                        )

                return {"hotels": hotels, "total_count": len(hotels), "budget_range": budget_range}
        except Exception as e:
            logger.warning(f"住宿数据获取失败: {e}")

        return {"hotels": [], "total_count": 0, "error": "住宿数据获取失败"}

    def _determine_budget_level(self, hotel_name: str, budget_range: str) -> str:
        """根据酒店名称和预算范围确定预算等级"""
        luxury_keywords = ["豪华", "五星", "国际", "度假村", "精品"]
        budget_keywords = ["经济", "青年", "快捷", "连锁"]

        if any(keyword in hotel_name for keyword in luxury_keywords):
            return "high"
        elif any(keyword in hotel_name for keyword in budget_keywords):
            return "low"
        else:
            return budget_range

    def _generate_enhanced_content_with_deepseek(
        self,
        destination: str,
        travel_style: str,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
        attractions_data: Dict,
        food_data: Dict,
        weather_info: Dict,
    ) -> Dict:
        """使用DeepSeek生成增强内容"""
        if not self.llm_available:
            return {}

        try:
            # 构建包含真实数据的提示词
            attractions_text = "\n".join(
                [f"- {att['name']}: {att['description'][:100]}..." for att in attractions_data.get("attractions", [])[:5]]
            )
            foods_text = "\n".join(
                [f"- {food['name']}: {food['description'][:100]}..." for food in food_data.get("foods", [])[:5]]
            )

            weather_text = ""
            if "current" in weather_info:
                current = weather_info["current"]
                weather_text = f"当前天气: {current['weather']}, 温度: {current['temperature']}°C, 湿度: {current['humidity']}%"

            interests_text = "、".join(interests) if interests else "通用"

            prompt = f"""基于以下真实数据为{destination}生成详细的旅游攻略：

真实景点数据：
{attractions_text}

真实美食数据：
{foods_text}

真实天气信息：
{weather_text}

旅行要求：
- 目的地：{destination}
- 旅行风格：{travel_style}
- 预算范围：{budget_range}
- 旅行时长：{travel_duration}
- 兴趣偏好：{interests_text}

请生成包含以下内容的详细攻略：
1. 基于真实景点的推荐行程
2. 基于真实美食的餐饮建议
3. 考虑当前天气的出行建议
4. 详细的预算分析
5. 实用的旅行贴士

请确保所有建议都基于提供的真实数据，避免虚假信息。"""

            content = self.generate_travel_guide(prompt)

            return {"enhanced_content": content, "generated_at": datetime.now().isoformat(), "source": "DeepSeek AI"}

        except Exception as e:
            logger.warning(f"DeepSeek增强内容生成失败: {e}")
            return {}

    def _synthesize_final_guide(
        self,
        destination: str,
        travel_style: str,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
        geo_info: Dict,
        weather_info: Dict,
        attractions_data: Dict,
        food_data: Dict,
        transport_data: Dict,
        accommodation_data: Dict,
        enhanced_content: Dict,
    ) -> Dict:
        """合成最终攻略"""
        days = self._parse_travel_duration(travel_duration)

        # 提取景点和美食名称
        attractions = [att["name"] for att in attractions_data.get("attractions", [])]
        foods = [food["name"] for food in food_data.get("foods", [])]

        # 生成预算估算
        budget_estimate = self._generate_realistic_budget(days, budget_range, attractions_data, accommodation_data)

        # 生成每日行程
        daily_schedule = self._generate_realistic_daily_schedule(
            destination, days, attractions, foods, travel_style, weather_info
        )

        return {
            "destination": destination,
            "travel_style": travel_style,
            "budget_range": budget_range,
            "travel_duration": travel_duration,
            "interests": interests,
            # 真实数据
            "must_visit_attractions": attractions[:8],
            "food_recommendations": foods[:8],
            "weather_info": weather_info,
            "geolocation_info": geo_info,
            "transportation_guide": transport_data,
            "accommodation_data": accommodation_data,
            # 生成内容
            "budget_estimate": budget_estimate,
            "daily_schedule": daily_schedule,
            "travel_tips": self._generate_realistic_tips(destination, weather_info, attractions_data),
            "detailed_guide": enhanced_content.get("enhanced_content", ""),
            # 元数据
            "data_sources": {
                "attractions": attractions_data.get("source", ""),
                "foods": food_data.get("source", ""),
                "weather": "wttr.in",
                "geolocation": "OpenStreetMap",
                "enhanced_content": enhanced_content.get("source", ""),
            },
            "generated_at": datetime.now().isoformat(),
            "is_real_data": True,
        }

    def _parse_travel_duration(self, travel_duration: str) -> int:
        """解析旅行时长"""
        if "1天" in travel_duration or "1晚" in travel_duration:
            return 1
        elif "2天" in travel_duration or "2晚" in travel_duration:
            return 2
        elif "3天" in travel_duration or "3晚" in travel_duration:
            return 3
        elif "4天" in travel_duration or "4晚" in travel_duration:
            return 4
        elif "5天" in travel_duration or "5晚" in travel_duration:
            return 5
        else:
            return 3

    def _generate_realistic_budget(
        self, days: int, budget_range: str, attractions_data: Dict, accommodation_data: Dict
    ) -> Dict:
        """生成真实预算估算"""
        base_costs = {
            "low": {"accommodation": 150, "food": 80, "transport": 50, "attractions": 30},
            "medium": {"accommodation": 300, "food": 150, "transport": 100, "attractions": 80},
            "high": {"accommodation": 600, "food": 300, "transport": 200, "attractions": 150},
        }

        costs = base_costs.get(budget_range, base_costs["medium"])

        # 根据景点数量调整门票费用
        attraction_count = len(attractions_data.get("attractions", []))
        if attraction_count > 0:
            costs["attractions"] = min(costs["attractions"] * (attraction_count / 5), 200)

        daily_total = sum(costs.values())
        total_cost = daily_total * days

        return {
            "daily_breakdown": costs,
            "daily_total": daily_total,
            "total_cost": total_cost,
            "currency": "CNY",
            "budget_range": budget_range,
            "days": days,
        }

    def _generate_realistic_daily_schedule(
        self, destination: str, days: int, attractions: List[str], foods: List[str], travel_style: str, weather_info: Dict
    ) -> List[Dict]:
        """生成真实每日行程"""
        schedules = []

        for day in range(1, days + 1):
            # 根据天气调整行程
            weather_advice = ""
            if "current" in weather_info:
                current = weather_info["current"]
                if current["weather"] in ["雨", "雪", "雾"]:
                    weather_advice = "建议室内活动为主"
                elif current["temperature"] > 30:
                    weather_advice = "注意防暑降温"
                elif current["temperature"] < 10:
                    weather_advice = "注意保暖"

            # 分配景点和美食
            day_attractions = attractions[day - 1 :: days] if attractions else []
            day_foods = foods[day - 1 :: days] if foods else []

            schedule = {
                "day": day,
                "date": f"第{day}天",
                "weather_advice": weather_advice,
                "morning": day_attractions[:2] if day_attractions else [],
                "afternoon": day_attractions[2:4] if len(day_attractions) > 2 else [],
                "evening": day_foods[:2] if day_foods else [],
                "night": day_foods[2:4] if len(day_foods) > 2 else [],
                "total_attractions": len(day_attractions),
                "total_foods": len(day_foods),
            }

            schedules.append(schedule)

        return schedules

    def _generate_realistic_tips(self, destination: str, weather_info: Dict, attractions_data: Dict) -> List[str]:
        """生成真实旅行贴士"""
        tips = []

        # 基于天气的贴士
        if "current" in weather_info:
            current = weather_info["current"]
            if current["weather"] in ["雨", "雪"]:
                tips.append(f"今天{destination}有{current['weather']}，建议携带雨具或保暖衣物")
            if current["temperature"] > 30:
                tips.append(f"今天{destination}温度较高({current['temperature']}°C)，注意防暑降温")
            if current["humidity"] > 70:
                tips.append("湿度较大，注意防潮")

        # 基于景点的贴士
        attraction_count = len(attractions_data.get("attractions", []))
        if attraction_count > 0:
            tips.append(f"{destination}有{attraction_count}个推荐景点，建议合理安排时间")

        # 通用贴士
        tips.extend([f"建议提前了解{destination}的交通情况", "准备一些常用药品和应急用品", "注意保管好随身物品", "尊重当地文化和习俗"])

        return tips[:8]  # 限制贴士数量

    def _generate_fallback_with_deepseek(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """使用DeepSeek生成备用攻略"""
        if not self.llm_available:
            return self._generate_basic_fallback(destination, travel_style, budget_range, travel_duration, interests)

        try:
            interests_text = "、".join(interests) if interests else "通用"

            prompt = f"""请为{destination}生成一份详细的旅游攻略。

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

            content = self.generate_travel_guide(prompt)

            return {
                "destination": destination,
                "travel_style": travel_style,
                "budget_range": budget_range,
                "travel_duration": travel_duration,
                "interests": interests,
                "must_visit_attractions": [f"{destination}著名景点"],
                "food_recommendations": [f"{destination}特色美食"],
                "detailed_guide": content,
                "travel_tips": ["建议提前了解当地天气", "注意保管好随身物品"],
                "budget_estimate": {"total_cost": 1000, "currency": "CNY"},
                "daily_schedule": [],
                "is_real_data": False,
                "fallback_source": "DeepSeek AI",
                "generated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"DeepSeek备用攻略生成失败: {e}")
            return self._generate_basic_fallback(destination, travel_style, budget_range, travel_duration, interests)

    def _generate_basic_fallback(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """生成基础备用攻略"""
        return {
            "destination": destination,
            "travel_style": travel_style,
            "budget_range": budget_range,
            "travel_duration": travel_duration,
            "interests": interests,
            "must_visit_attractions": [f"{destination}著名景点"],
            "food_recommendations": [f"{destination}特色美食"],
            "detailed_guide": f"{destination}是一个美丽的旅游目的地，建议您亲自体验。",
            "travel_tips": ["建议提前了解当地天气", "注意保管好随身物品"],
            "budget_estimate": {"total_cost": 1000, "currency": "CNY"},
            "daily_schedule": [],
            "is_real_data": False,
            "fallback_source": "Basic Fallback",
            "generated_at": datetime.now().isoformat(),
        }
