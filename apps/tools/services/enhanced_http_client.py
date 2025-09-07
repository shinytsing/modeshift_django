#!/usr/bin/env python3
"""
增强的HTTP客户端 - 集成代理池和反爬虫机制
"""

import logging
import random
import time
from typing import Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .proxy_pool import proxy_pool

logger = logging.getLogger(__name__)


class EnhancedHTTPClient:
    """增强的HTTP客户端，支持代理轮换和反爬虫"""

    def __init__(self, use_proxy: bool = True, max_retries: int = 3):
        self.use_proxy = use_proxy
        self.max_retries = max_retries
        self.session = None
        self.current_proxy = None
        self.request_count = 0
        self.proxy_rotation_interval = 10  # 每10个请求轮换代理

        self._init_session()

    def _init_session(self):
        """初始化会话"""
        self.session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 设置默认请求头
        self._update_headers()

    def _update_headers(self):
        """更新请求头"""
        self.session.headers.update(
            {
                "User-Agent": proxy_pool.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

    def _get_proxy(self) -> Optional[Dict]:
        """获取代理配置"""
        if not self.use_proxy:
            return None

        # 检查是否需要轮换代理
        if self.current_proxy is None or self.request_count % self.proxy_rotation_interval == 0:
            new_proxy = proxy_pool.get_proxy_for_requests()
            if new_proxy:
                self.current_proxy = new_proxy
                logger.info(f"🔄 切换代理: {new_proxy['info'].proxy}")
            else:
                logger.warning("⚠️ 无可用代理，使用直连")
                self.current_proxy = None

        return self.current_proxy

    def _add_random_delay(self):
        """添加随机延迟避免被检测"""
        delay = random.uniform(0.5, 2.5)  # 0.5-2.5秒随机延迟，更贴近真实用户行为
        time.sleep(delay)

    def _get_random_headers(self) -> Dict[str, str]:
        """获取随机化的请求头"""
        base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": random.choice(
                ["zh-CN,zh;q=0.9,en;q=0.8", "en-US,en;q=0.9,zh-CN;q=0.8", "zh-CN,zh;q=0.8,en-US;q=0.7,en;q=0.5"]
            ),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": random.choice(["document", "empty", "image"]),
            "Sec-Fetch-Mode": random.choice(["navigate", "cors", "no-cors"]),
            "Sec-Fetch-Site": random.choice(["none", "same-origin", "cross-site"]),
            "Sec-Fetch-User": "?1",
            "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store"]),
            "Pragma": "no-cache",
        }

        # 随机添加一些可选头部
        optional_headers = {
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": f'"{random.choice(["Windows", "macOS", "Linux"])}"',
            "X-Requested-With": "XMLHttpRequest" if random.random() < 0.3 else None,
            "Referer": f'https://www.{random.choice(["google", "bing", "baidu"])}.com/' if random.random() < 0.4 else None,
        }

        for key, value in optional_headers.items():
            if value and random.random() < 0.7:  # 70%概率添加可选头部
                base_headers[key] = value

        return base_headers

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """增强的GET请求"""
        return self._make_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """增强的POST请求"""
        return self._make_request("POST", url, **kwargs)

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """执行HTTP请求，包含代理fallback机制"""
        self.request_count += 1

        # 添加随机延迟
        self._add_random_delay()

        # 更新请求头（每次请求随机化）
        if "headers" not in kwargs:
            kwargs["headers"] = {}

        # 合并随机头部
        random_headers = self._get_random_headers()
        for key, value in random_headers.items():
            if key not in kwargs["headers"]:
                kwargs["headers"][key] = value

        # 确保User-Agent是随机的
        kwargs["headers"]["User-Agent"] = proxy_pool.get_random_user_agent()

        # 设置超时
        if "timeout" not in kwargs:
            kwargs["timeout"] = 20

        # 首先尝试使用代理
        if self.use_proxy:
            proxy_config = self._get_proxy()
            if proxy_config:
                kwargs_with_proxy = kwargs.copy()
                kwargs_with_proxy["proxies"] = {"http": proxy_config["http"], "https": proxy_config["https"]}

                # 尝试使用代理请求
                response = self._try_request_with_config(method, url, proxy_config, **kwargs_with_proxy)
                if response:
                    return response

                logger.warning("🔄 代理请求失败，切换到直连模式")

        # 代理失败或不使用代理时，尝试直连
        return self._try_direct_request(method, url, **kwargs)

    def _try_request_with_config(self, method: str, url: str, proxy_config: Dict, **kwargs) -> Optional[requests.Response]:
        """使用指定配置尝试请求"""
        for attempt in range(2):  # 代理模式下减少重试次数
            try:
                logger.debug(f"🔒 {method} {url} via proxy {proxy_config['info'].proxy} (尝试 {attempt + 1}/2)")

                if method.upper() == "GET":
                    response = self.session.get(url, **kwargs)
                elif method.upper() == "POST":
                    response = self.session.post(url, **kwargs)
                else:
                    response = self.session.request(method, url, **kwargs)

                # 检查响应状态
                if response.status_code == 200:
                    logger.debug(f"✅ 代理请求成功: {url}")
                    return response
                elif response.status_code == 404:
                    logger.warning(f"❌ 页面不存在 ({response.status_code}): {url}")
                    return response  # 404是有效响应，不重试
                elif response.status_code == 403:
                    logger.warning(f"🚫 代理被拒绝 ({response.status_code}): {url}")
                    # 标记代理失败
                    proxy_pool.mark_proxy_failed(proxy_config["info"].proxy)
                    self.current_proxy = None
                    break  # 跳出循环，尝试直连
                else:
                    logger.warning(f"⚠️ 代理返回异常状态码 ({response.status_code}): {url}")

            except (requests.exceptions.ProxyError, requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"🔌 代理连接问题: {e}")
                # 标记代理失败
                proxy_pool.mark_proxy_failed(proxy_config["info"].proxy)
                self.current_proxy = None
                break  # 跳出循环，尝试直连

            except Exception as e:
                logger.warning(f"⚠️ 代理请求异常: {e}")
                if attempt == 1:  # 最后一次尝试
                    break

            # 短暂等待后重试
            if attempt < 1:
                time.sleep(1)

        return None

    def _try_direct_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """尝试直连请求"""
        # 移除代理配置
        kwargs.pop("proxies", None)

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"🌐 {method} {url} via direct (尝试 {attempt + 1}/{self.max_retries})")

                if method.upper() == "GET":
                    response = self.session.get(url, **kwargs)
                elif method.upper() == "POST":
                    response = self.session.post(url, **kwargs)
                else:
                    response = self.session.request(method, url, **kwargs)

                # 检查响应状态
                if response.status_code == 200:
                    logger.debug(f"✅ 直连请求成功: {url}")
                    return response
                elif response.status_code == 404:
                    logger.warning(f"❌ 页面不存在 ({response.status_code}): {url}")
                    return response  # 404是有效响应，不重试
                elif response.status_code == 403:
                    logger.warning(f"🚫 直连也被拒绝 ({response.status_code}): {url}")
                    # 403可能是IP被封，稍等重试
                    if attempt < self.max_retries - 1:
                        wait_time = (attempt + 1) * 3
                        logger.info(f"⏱️ IP可能被限制，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                else:
                    logger.warning(f"⚠️ 直连异常状态码 ({response.status_code}): {url}")

            except requests.exceptions.Timeout as e:
                logger.warning(f"⏰ 直连超时: {e}")

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"🔌 直连连接错误: {e}")

            except Exception as e:
                logger.warning(f"⚠️ 直连请求异常: {e}")

            # 等待后重试
            if attempt < self.max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.info(f"⏱️ 等待 {wait_time} 秒后重试直连...")
                time.sleep(wait_time)

        logger.error(f"❌ 所有请求方式都失败: {url}")
        return None

    def get_stats(self) -> Dict:
        """获取客户端统计信息"""
        return {
            "total_requests": self.request_count,
            "use_proxy": self.use_proxy,
            "current_proxy": self.current_proxy["info"].proxy if self.current_proxy else None,
            "proxy_pool_stats": proxy_pool.get_stats(),
        }


# 创建全局客户端实例
http_client = EnhancedHTTPClient(use_proxy=True)
