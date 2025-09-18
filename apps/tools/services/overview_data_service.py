import json
import logging
import time
from datetime import datetime
from typing import Dict, Optional

from django.conf import settings

import requests

from .llm_service import get_llm_service

logger = logging.getLogger(__name__)


class OverviewDataService:
    """WanderAI Overview数据服务 - 使用DeepSeek和免费API获取基本信息、天气、汇率、时区信息"""

    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30

        # 使用统一的LLM服务
        self.llm_service = get_llm_service()

        # 免费API配置
        self.weather_api_url = "http://wttr.in"
        self.currency_api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.timezone_api_url = "http://worldtimeapi.org/api"

    def get_overview_data(self, destination: str) -> Optional[Dict]:
        """获取目的地overview数据，包括基本信息、天气、汇率、时区"""
        try:
            logger.info(f"🔍 获取{destination}的overview数据...")
            start_time = time.time()

            # 1. 使用DeepSeek获取基本信息
            destination_info = self._get_destination_info_from_llm(destination)

            # 2. 使用免费API获取天气信息
            weather_info = self._get_weather_info(destination)

            # 3. 获取汇率信息
            currency_info = self._get_currency_info(destination)

            # 4. 获取时区信息
            timezone_info = self._get_timezone_info(destination)

            # 合并所有数据
            overview_data = {
                "destination_info": destination_info,
                "weather_info": weather_info,
                "currency_info": currency_info,
                "timezone_info": timezone_info,
                "last_updated": datetime.now().isoformat(),
                "data_source": "deepseek_and_free_apis",
            }

            generation_time = time.time() - start_time
            logger.info(f"✅ {destination} overview数据获取完成，耗时: {generation_time:.2f}秒")

            return overview_data

        except Exception as e:
            logger.error(f"❌ 获取{destination} overview数据失败: {e}")
            return self._get_fallback_overview_data(destination)

    def _get_destination_info_from_llm(self, destination: str) -> Dict:
        """使用LLM服务获取目的地基本信息"""
        try:
            logger.info(f"🤖 使用LLM服务获取{destination}基本信息...")

            prompt = f"""请严格按照以下JSON格式返回{destination}的基本信息，不要添加任何其他文字或解释：

```json
{{
    "country": "所属国家或地区名称",
    "languages": ["主要语言1", "主要语言2"],
    "population": "人口数量（如：1000万）",
    "area": "面积（如：1000平方公里）",
    "capital": "是否为首都（是/否）",
    "timezone": "时区（如：UTC+8）",
    "famous_for": "主要特色或著名景点",
    "best_visit_time": "最佳旅游时间"
}}
```

要求：
1. 必须返回有效的JSON格式
2. 所有字段都必须填写
3. 不要包含代码块标记
4. 信息要准确真实"""

            # 使用LLM服务生成内容
            content = self.llm_service.generate_content(
                prompt, 
                system_prompt="你是一个专业的旅游信息助手，请严格按照JSON格式返回信息。",
                max_tokens=2000,
                temperature=0.3
            )

            # 尝试解析JSON，处理可能的代码块标记
            try:
                # 清理内容，移除可能的代码块标记
                clean_content = content.strip()
                if clean_content.startswith("```json"):
                    clean_content = clean_content[7:]
                if clean_content.startswith("```"):
                    clean_content = clean_content[3:]
                if clean_content.endswith("```"):
                    clean_content = clean_content[:-3]
                clean_content = clean_content.strip()

                destination_data = json.loads(clean_content)
                logger.info(f"✅ LLM服务成功获取{destination}基本信息")
                return destination_data
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ LLM服务返回数据非JSON格式: {e}")
                logger.warning(f"原始内容: {content[:200]}...")
                return self._get_fallback_destination_info(destination)

        except Exception as e:
            logger.error(f"❌ LLM服务调用失败: {e}")
            return self._get_fallback_destination_info(destination)

    def _get_weather_info(self, destination: str) -> Dict:
        """获取天气信息"""
        try:
            logger.info(f"🌤️ 获取{destination}天气信息...")

            # 使用wttr.in API获取天气
            url = f"{self.weather_api_url}/{destination}?format=j1"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                current = data.get("current_condition", [{}])[0]

                return {
                    "temperature": int(current.get("temp_C", 20)),
                    "weather": current.get("weatherDesc", [{}])[0].get("value", "晴朗"),
                    "humidity": int(current.get("humidity", 70)),
                    "wind_speed": int(current.get("windspeedKmph", 10)),
                    "feels_like": int(current.get("FeelsLikeC", 22)),
                    "description": self._get_weather_description(destination),
                }
            else:
                return self._get_fallback_weather_info()

        except Exception as e:
            logger.warning(f"⚠️ 天气信息获取失败: {e}")
            return self._get_fallback_weather_info()

    def _get_currency_info(self, destination: str) -> Dict:
        """获取汇率信息"""
        try:
            logger.info(f"💱 获取{destination}汇率信息...")

            # 根据目的地确定货币
            currency_mapping = {
                "北京": "CNY",
                "上海": "CNY",
                "杭州": "CNY",
                "西安": "CNY",
                "成都": "CNY",
                "东京": "JPY",
                "首尔": "KRW",
                "曼谷": "THB",
                "新加坡": "SGD",
                "巴黎": "EUR",
                "伦敦": "GBP",
                "纽约": "USD",
                "洛杉矶": "USD",
            }

            local_currency = currency_mapping.get(destination, "CNY")

            # 如果是人民币，直接返回
            if local_currency == "CNY":
                return {
                    "currency": "人民币 (CNY)",
                    "rate": "1 USD = 7.2 CNY",
                    "exchange_tips": "建议在银行或正规兑换点兑换",
                    "local_currency": "CNY",
                }

            # 获取汇率数据
            response = self.session.get(self.currency_api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})

                if local_currency in rates:
                    rate = rates[local_currency]
                    return {
                        "currency": f"{self._get_currency_name(local_currency)} ({local_currency})",
                        "rate": f"1 USD = {rate} {local_currency}",
                        "exchange_tips": f"建议在银行或正规兑换点兑换{local_currency}",
                        "local_currency": local_currency,
                    }

            return self._get_fallback_currency_info()

        except Exception as e:
            logger.warning(f"⚠️ 汇率信息获取失败: {e}")
            return self._get_fallback_currency_info()

    def _get_timezone_info(self, destination: str) -> Dict:
        """获取时区信息"""
        try:
            logger.info(f"🕐 获取{destination}时区信息...")

            # 时区映射
            timezone_mapping = {
                "北京": "Asia/Shanghai",
                "上海": "Asia/Shanghai",
                "杭州": "Asia/Shanghai",
                "西安": "Asia/Shanghai",
                "成都": "Asia/Shanghai",
                "东京": "Asia/Tokyo",
                "首尔": "Asia/Seoul",
                "曼谷": "Asia/Bangkok",
                "新加坡": "Asia/Singapore",
                "巴黎": "Europe/Paris",
                "伦敦": "Europe/London",
                "纽约": "America/New_York",
                "洛杉矶": "America/Los_Angeles",
            }

            timezone = timezone_mapping.get(destination, "Asia/Shanghai")

            # 尝试时区API，快速失败机制
            apis = [
                f"{self.timezone_api_url}/timezone/{timezone}",
            ]

            for api_url in apis:
                try:
                    logger.info(f"🔄 尝试时区API: {api_url}")
                    response = self.session.get(api_url, timeout=3)  # 进一步减少超时时间到3秒

                    if response.status_code == 200:
                        data = response.json()

                        # 处理不同API的响应格式
                        if "datetime" in data:  # worldtimeapi.org
                            logger.info(f"✅ 成功从 {api_url} 获取时区信息")
                            return {
                                "timezone": data.get("timezone", "UTC+8"),
                                "current_time": data.get("datetime", "2024-01-01T14:30:00")[11:16],
                                "daylight_saving": "是" if data.get("dst", False) else "无",
                                "utc_offset": data.get("utc_offset", "+08:00"),
                            }

                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ 时区API {api_url} 超时，快速失败")
                except requests.exceptions.ConnectionError as e:
                    logger.warning(f"🔌 时区API {api_url} 连接错误: {e}")
                except Exception as api_error:
                    logger.warning(f"⚠️ 时区API {api_url} 失败: {api_error}")

            # 所有API都失败，使用本地时间作为备用
            logger.warning("⚠️ 所有时区API都失败，使用本地时间")
            return self._get_fallback_timezone_info()

        except Exception as e:
            logger.warning(f"⚠️ 时区信息获取失败: {e}")
            return self._get_fallback_timezone_info()

    def _get_weather_description(self, destination: str) -> str:
        """获取天气描述"""
        descriptions = {
            "北京": "春季气候宜人，适合旅游",
            "上海": "夏季湿热，建议避开正午出行",
            "杭州": "春秋两季气候宜人，是旅游的最佳时节",
            "西安": "春秋季节气候宜人，适合游览古迹",
            "成都": "气候温和，全年适合旅游",
        }
        return descriptions.get(destination, "气候宜人，适合旅游")

    def _get_currency_name(self, currency_code: str) -> str:
        """获取货币名称"""
        currency_names = {
            "CNY": "人民币",
            "JPY": "日元",
            "KRW": "韩元",
            "THB": "泰铢",
            "SGD": "新加坡元",
            "EUR": "欧元",
            "GBP": "英镑",
            "USD": "美元",
        }
        return currency_names.get(currency_code, "当地货币")

    def _get_fallback_destination_info(self, destination: str) -> Dict:
        """获取备用目的地信息"""
        fallback_data = {
            "北京": {
                "country": "中国",
                "languages": ["中文", "英语"],
                "population": "2154万",
                "area": "16410平方公里",
                "capital": "是",
                "timezone": "UTC+8",
                "famous_for": "历史文化古都，紫禁城",
                "best_visit_time": "春秋两季",
            },
            "上海": {
                "country": "中国",
                "languages": ["中文", "英语"],
                "population": "2487万",
                "area": "6340平方公里",
                "capital": "否",
                "timezone": "UTC+8",
                "famous_for": "国际大都市，外滩夜景",
                "best_visit_time": "春秋两季",
            },
            "杭州": {
                "country": "中国",
                "languages": ["中文", "英语"],
                "population": "1194万",
                "area": "16596平方公里",
                "capital": "否",
                "timezone": "UTC+8",
                "famous_for": "西湖风景，人间天堂",
                "best_visit_time": "春秋两季",
            },
            "西安": {
                "country": "中国",
                "languages": ["中文", "英语"],
                "population": "1295万",
                "area": "10108平方公里",
                "capital": "否",
                "timezone": "UTC+8",
                "famous_for": "兵马俑，古都长安",
                "best_visit_time": "春秋两季",
            },
            "成都": {
                "country": "中国",
                "languages": ["中文", "英语"],
                "population": "2094万",
                "area": "14335平方公里",
                "capital": "否",
                "timezone": "UTC+8",
                "famous_for": "大熊猫，川菜美食",
                "best_visit_time": "全年",
            },
        }

        return fallback_data.get(
            destination,
            {
                "country": "未知",
                "languages": ["中文"],
                "population": "未知",
                "area": "未知",
                "capital": "否",
                "timezone": "UTC+8",
                "famous_for": "当地特色",
                "best_visit_time": "春秋两季",
            },
        )

    def _get_fallback_weather_info(self) -> Dict:
        """获取备用天气信息"""
        return {
            "temperature": 25,
            "weather": "晴朗",
            "humidity": 70,
            "wind_speed": 10,
            "feels_like": 28,
            "description": "气候宜人，适合旅游",
        }

    def _get_fallback_currency_info(self) -> Dict:
        """获取备用汇率信息"""
        return {
            "currency": "人民币 (CNY)",
            "rate": "1 USD = 7.2 CNY",
            "exchange_tips": "建议在银行或正规兑换点兑换",
            "local_currency": "CNY",
        }

    def _get_fallback_timezone_info(self) -> Dict:
        """获取备用时区信息"""
        return {
            "timezone": "UTC+8 (北京时间)",
            "current_time": datetime.now().strftime("%H:%M"),
            "daylight_saving": "无",
            "utc_offset": "+08:00",
        }

    def _get_fallback_overview_data(self, destination: str) -> Dict:
        """获取完整的备用overview数据"""
        return {
            "destination_info": self._get_fallback_destination_info(destination),
            "weather_info": self._get_fallback_weather_info(),
            "currency_info": self._get_fallback_currency_info(),
            "timezone_info": self._get_fallback_timezone_info(),
            "last_updated": datetime.now().isoformat(),
            "data_source": "fallback_data",
        }
