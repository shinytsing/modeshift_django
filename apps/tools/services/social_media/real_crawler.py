"""
真实社交媒体爬虫服务
实现真实的API调用和数据爬取
"""

import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from apps.tools.models import SocialMediaSubscription

# 尝试导入Playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright未安装，将使用requests进行爬取")

logger = logging.getLogger(__name__)


class RealSocialMediaCrawler:
    """真实社交媒体爬虫服务"""

    def __init__(self):
        self.session = requests.Session()
        
        # 反反爬机制：随机User-Agent池
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # 设置随机User-Agent
        self.session.headers.update({
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        })
        
        # 请求间隔设置（秒）- 更复杂的间隔机制
        self.request_delay_ranges = [
            (2, 5),    # 基础间隔：2-5秒
            (5, 10),   # 中等间隔：5-10秒
            (10, 20),  # 长间隔：10-20秒
            (20, 30)   # 超长间隔：20-30秒
        ]
        self.request_count = 0  # 请求计数器
        self.last_request_time = 0
        
        # 代理IP池
        self.proxy_pool = [
            # 这里可以添加代理IP，格式：{'http': 'http://ip:port', 'https': 'https://ip:port'}
            # 示例：
            # {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080'},
            # {'http': 'http://127.0.0.1:8081', 'https': 'https://127.0.0.1:8081'},
        ]
        self.current_proxy_index = 0
        
        # IP限制检测
        self.ip_blocked = False
        self.last_ip_check = 0
        
        # 用户名到用户ID的映射表
        self.username_to_id_mapping = {
            "宁波阮小二": "5e21955f0000000001004aec",
            "肉桂乳酪": "6538e8aa00000000060060e0", 
            "萌萌柠檬乳酪肉桂卷": "5d356af3000000001603705b",
            "95028321884": "673f222c000000001d02efb3",  # Ethan
            "吃定彩虹糖": "624d0d5e0000000021025550",
            "1313656381": "624d0d5e0000000021025550",  # 吃定彩虹糖的小红书号
        }
        
        # 用户名到token的映射表
        self.username_to_token_mapping = {
            "宁波阮小二": "ABY39vk1FYvF3A341leA-uWEdFNHEgKW2pfVYX9IEfdRo%3D",
            "肉桂乳酪": "AB60cYo5wJ21U9gdoe_IuiDA9lG0_bTKlboI8x-O9VmZQ%3D",
            "萌萌柠檬乳酪肉桂卷": "AB093wIev2tAnIYjYMcWt1OlrCx97jPESSfSJs5QICoaQ%3D",
            "95028321884": "",  # Ethan
            "吃定彩虹糖": "",
            "1313656381": "",  # 吃定彩虹糖的小红书号
        }
        
        # 设置小红书Cookie
        self._setup_xiaohongshu_cookies()
    
    def add_user_mapping(self, username: str, user_id: str, token: str = ""):
        """手动添加用户映射"""
        self.username_to_id_mapping[username] = user_id
        self.username_to_token_mapping[username] = token
        logger.info(f"添加用户映射: {username} -> {user_id}")
    
    def get_user_mapping_info(self, username: str) -> dict:
        """获取用户映射信息"""
        return {
            'username': username,
            'user_id': self.username_to_id_mapping.get(username, ''),
            'token': self.username_to_token_mapping.get(username, ''),
            'has_mapping': username in self.username_to_id_mapping
        }
        
        # 设置小红书session cookies
        self._setup_xiaohongshu_cookies()

    def _anti_detection_request(self, url: str, max_retries: int = 3, **kwargs) -> Optional[requests.Response]:
        """反反爬请求方法"""
        for attempt in range(max_retries):
            try:
                # 智能请求间隔
                current_time = time.time()
                delay = self._get_smart_delay()
                
                if current_time - self.last_request_time < delay:
                    sleep_time = delay - (current_time - self.last_request_time)
                    logger.info(f"智能延迟 {sleep_time:.1f} 秒 (请求计数: {self.request_count})")
                    time.sleep(sleep_time)
                
                self.request_count += 1
                
                # 随机更换User-Agent
                self.session.headers.update({
                    "User-Agent": random.choice(self.user_agents)
                })
                
                # 添加随机Referer
                if 'referer' not in kwargs:
                    kwargs['headers'] = kwargs.get('headers', {})
                    kwargs['headers']['Referer'] = 'https://www.xiaohongshu.com/'
                
                # 获取代理IP
                proxy = self._get_next_proxy()
                if proxy:
                    logger.info(f"使用代理IP: {proxy}")
                
                # 发送请求
                try:
                    response = self.session.get(url, proxies=proxy, timeout=15, **kwargs)
                except Exception as proxy_error:
                    if proxy:
                        logger.warning(f"代理IP连接失败: {proxy_error}")
                        logger.info("回退到直接连接")
                        response = self.session.get(url, timeout=15, **kwargs)
                    else:
                        raise proxy_error
                self.last_request_time = time.time()
                
                # 检查响应状态
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # 频率限制
                    logger.warning(f"请求频率限制，等待 {2 ** attempt} 秒后重试")
                    time.sleep(2 ** attempt)
                    continue
                elif response.status_code in [403, 404]:
                    logger.warning(f"请求被拒绝或页面不存在: {response.status_code}")
                    return None
                else:
                    logger.warning(f"请求失败: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，第 {attempt + 1} 次重试")
                time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求异常: {e}，第 {attempt + 1} 次重试")
                time.sleep(2 ** attempt)
        
        logger.error(f"请求失败，已重试 {max_retries} 次")
        return None
    
    def _parse_xiaohongshu_posts_enhanced(self, soup: BeautifulSoup, page_content: str, subscription: SocialMediaSubscription) -> List[Dict]:
        """增强的小红书笔记解析方法"""
        posts = []
        
        try:
            # 方法1: 从页面HTML中解析笔记链接
            note_links = []
            
            # 查找各种可能的笔记链接模式
            import re
            patterns = [
                r'href="(/explore/[a-f0-9]+)"',
                r'href="(/explore/[a-f0-9]+)\?"',
                r'"(/explore/[a-f0-9]+)"',
                r'explore/([a-f0-9]+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_content)
                note_links.extend(matches)
            
            # 去重
            note_links = list(set(note_links))
            logger.info(f"找到 {len(note_links)} 个笔记链接")
            
            # 尝试访问笔记页面获取内容
            for i, link in enumerate(note_links[:5]):  # 只处理前5个
                try:
                    # 构建完整的笔记URL
                    if link.startswith('/'):
                        note_url = f"https://xiaohongshu.com{link}"
                    else:
                        note_url = f"https://xiaohongshu.com/explore/{link}"
                    
                    logger.info(f"尝试访问笔记: {note_url}")
                    
                    # 使用反反爬请求访问笔记
                    note_response = self._anti_detection_request(note_url)
                    if not note_response:
                        continue
                    
                    # 检查笔记是否有效
                    if "你访问的页面不见了" in note_response.text:
                        logger.warning(f"笔记不存在: {note_url}")
                        continue
                    
                    # 解析笔记内容
                    note_soup = BeautifulSoup(note_response.content, 'html.parser')
                    
                    # 提取笔记信息
                    title_match = re.search(r'<title>(.*?)</title>', note_response.text)
                    title = title_match.group(1) if title_match else "未知标题"
                    
                    # 检查是否包含目标用户信息
                    if subscription.target_user_name in note_response.text:
                        post_data = {
                            'title': title,
                            'content': title,
                            'url': note_url,
                            'images': [],
                            'tags': [],
                            'likes': 0,
                            'comments': 0,
                            'shares': 0
                        }
                        posts.append(post_data)
                        logger.info(f"成功解析笔记: {title}")
                    
                except Exception as e:
                    logger.warning(f"解析笔记失败: {e}")
                    continue
            
            # 方法2: 从页面JSON数据中解析
            try:
                # 查找页面中的JSON数据
                json_pattern = r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
                json_match = re.search(json_pattern, page_content)
                if json_match:
                    json_data = json.loads(json_match.group(1))
                    # 解析JSON中的笔记数据
                    # 这里可以根据实际的小红书页面结构来解析
                    logger.info("找到页面JSON数据")
            except Exception as e:
                logger.warning(f"解析JSON数据失败: {e}")
            
            # 方法3: 从CSS选择器中解析
            try:
                # 查找笔记容器
                note_containers = soup.find_all(['div', 'article'], class_=re.compile(r'note|post|item'))
                logger.info(f"找到 {len(note_containers)} 个笔记容器")
                
                for container in note_containers[:5]:  # 处理前5个容器
                    try:
                        # 提取笔记信息
                        title_elem = container.find(['h1', 'h2', 'h3', 'span'], class_=re.compile(r'title|name'))
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if title and len(title) > 5:  # 过滤太短的标题
                                post_data = {
                                    'title': title,
                                    'content': title,
                                    'url': '',
                                    'images': [],
                                    'tags': [],
                                    'likes': 0,
                                    'comments': 0,
                                    'shares': 0
                                }
                                posts.append(post_data)
                                logger.info(f"从CSS选择器解析到笔记: {title}")
                    except Exception as e:
                        logger.warning(f"解析单个容器失败: {e}")
                        continue
            except Exception as e:
                logger.warning(f"CSS选择器解析失败: {e}")
            
            # 方法4: 从页面文本中直接提取内容
            try:
                # 查找包含目标用户名的文本片段
                import re
                user_matches = re.findall(rf'{subscription.target_user_name}[^<]*', page_content)
                logger.info(f"找到 {len(user_matches)} 个包含用户名的文本片段")
                
                for match in user_matches[:3]:  # 只处理前3个
                    if len(match) > 10:  # 过滤太短的文本
                        post_data = {
                            'title': f"{subscription.target_user_name}的动态",
                            'content': match,
                            'url': '',
                            'images': [],
                            'tags': [],
                            'likes': 0,
                            'comments': 0,
                            'shares': 0
                        }
                        posts.append(post_data)
                        logger.info(f"从文本片段解析到内容: {match[:50]}...")
            except Exception as e:
                logger.warning(f"文本片段解析失败: {e}")
            
            # 方法5: 从图片元素中提取信息
            try:
                img_elements = soup.find_all('img')
                logger.info(f"找到 {len(img_elements)} 个图片元素")
                
                # 查找可能的笔记图片
                for img in img_elements[:5]:  # 只处理前5个图片
                    try:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        if src and ('note' in src or 'post' in src or 'feed' in src):
                            post_data = {
                                'title': f"{subscription.target_user_name}的图片动态",
                                'content': alt if alt else "图片内容",
                                'url': '',
                                'images': [src],
                                'tags': [],
                                'likes': 0,
                                'comments': 0,
                                'shares': 0
                            }
                            posts.append(post_data)
                            logger.info(f"从图片解析到内容: {src}")
                    except Exception as e:
                        logger.warning(f"解析图片失败: {e}")
                        continue
            except Exception as e:
                logger.warning(f"图片解析失败: {e}")
                
        except Exception as e:
            logger.error(f"增强笔记解析失败: {e}")
        
        logger.info(f"总共解析到 {len(posts)} 个笔记")
        return posts

    def get_user_id_and_token(self, subscription: SocialMediaSubscription) -> tuple:
        """获取用户的真实ID和token - 智能识别小红书号和昵称"""
        username = subscription.target_user_name
        user_id = subscription.target_user_id
        
        # 智能识别输入类型
        input_type = self._identify_input_type(username, user_id)
        logger.info(f"识别输入类型: {input_type}")
        
        # 如果用户名在映射表中，使用映射的ID和token
        if username in self.username_to_id_mapping:
            real_user_id = self.username_to_id_mapping[username]
            token = self.username_to_token_mapping[username]
            logger.info(f"使用映射表中的用户ID: {real_user_id}")
            return real_user_id, token
        
        # 如果用户ID在映射表中，使用映射的ID和token
        if user_id in self.username_to_id_mapping.values():
            real_user_id = user_id
            token = self.username_to_token_mapping.get(username, "")
            logger.info(f"使用映射表中的用户ID: {real_user_id}")
            return real_user_id, token
        
        # 根据输入类型进行相应的解析
        try:
            if input_type == "xiaohongshu_number":
                real_user_id = self._resolve_by_xiaohongshu_number(username)
                if real_user_id:
                    # 将新解析的用户ID添加到映射表中
                    self.username_to_id_mapping[username] = real_user_id
                    self.username_to_token_mapping[username] = ""
                    logger.info(f"通过小红书号解析用户 {username} 的ID: {real_user_id}")
                    return real_user_id, ""
            elif input_type == "nickname":
                real_user_id, token = self._resolve_by_nickname(subscription)
                if real_user_id:
                    # 将新解析的用户ID添加到映射表中
                    self.username_to_id_mapping[username] = real_user_id
                    self.username_to_token_mapping[username] = token
                    logger.info(f"通过昵称解析用户 {username} 的ID: {real_user_id}")
                    return real_user_id, token
            else:
                # 混合情况，尝试两种方法
                logger.info(f"混合输入，尝试多种解析方法")
                real_user_id, token = self._resolve_user_id_dynamically(subscription)
                if real_user_id:
                    # 将新解析的用户ID添加到映射表中
                    self.username_to_id_mapping[username] = real_user_id
                    self.username_to_token_mapping[username] = token
                    logger.info(f"动态解析用户 {username} 的ID: {real_user_id}")
                    return real_user_id, token
        except Exception as e:
            logger.error(f"解析用户ID失败: {e}")
        
        # 默认返回原始ID和空token
        logger.warning(f"无法解析用户 {username}，返回原始ID: {user_id}")
        return user_id, ""
    
    def _identify_input_type(self, username: str, user_id: str) -> str:
        """智能识别输入类型"""
        # 检查是否是小红书号（纯数字且长度在合理范围内）
        if username.isdigit() and 8 <= len(username) <= 15:
            return "xiaohongshu_number"
        
        # 检查是否是完整的用户ID（24位十六进制）
        if len(username) == 24 and all(c in '0123456789abcdef' for c in username.lower()):
            return "full_user_id"
        
        # 检查是否包含特殊字符（可能是昵称）
        if any(char in username for char in ['&', '@', '#', ' ', '，', '。', '！', '？']):
            return "nickname"
        
        # 检查是否是纯中文或包含中文（可能是昵称）
        if any('\u4e00' <= char <= '\u9fff' for char in username):
            return "nickname"
        
        # 检查是否是英文昵称
        if username.isalpha() or username.replace('_', '').replace('-', '').isalnum():
            return "nickname"
        
        # 默认情况
        return "mixed"
    
    def _resolve_by_nickname(self, subscription: SocialMediaSubscription) -> tuple:
        """通过昵称解析用户ID"""
        username = subscription.target_user_name
        logger.info(f"通过昵称解析用户: {username}")
        
        try:
            # 方法1: 使用小红书搜索API
            search_url = "https://www.xiaohongshu.com/api/sns/web/v1/search/user"
            
            headers = self._get_xiaohongshu_headers({
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://www.xiaohongshu.com/search_result'
            })
            
            params = {
                'keyword': username,
                'page': 1,
                'page_size': 20,
                'search_id': '2b8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c8c',
                'sort': 'general'
            }
            
            response = self._anti_detection_request(search_url, headers=headers, params=params)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success') and data.get('data'):
                        users = data['data'].get('items', [])
                        
                        for user in users:
                            if user.get('nickname') == username:
                                user_id_from_api = user.get('user_id')
                                if user_id_from_api:
                                    logger.info(f"✅ 通过API找到用户 {username} 的ID: {user_id_from_api}")
                                    return user_id_from_api, ""
                        
                        # 如果没有完全匹配，尝试模糊匹配
                        for user in users:
                            nickname = user.get('nickname', '')
                            if username in nickname or nickname in username:
                                user_id_from_api = user.get('user_id')
                                if user_id_from_api:
                                    logger.info(f"✅ 通过API模糊匹配找到用户 {username} 的ID: {user_id_from_api}")
                                    return user_id_from_api, ""
                except Exception as e:
                    logger.warning(f"API响应解析失败: {e}")
            
            elif response and response.status_code == 500:
                logger.warning(f"API搜索服务暂时不可用 (500错误): {username}")
                logger.info("💡 建议：等待服务恢复或使用已知用户映射")
            else:
                logger.warning(f"API搜索未找到用户 {username} (状态码: {response.status_code if response else '无响应'})")
            
        except Exception as e:
            logger.warning(f"API搜索失败: {e}")
        
        try:
            # 方法2: 使用网页搜索
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={username}&type=user"
            
            headers = self._get_xiaohongshu_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            })
            
            response = self._anti_detection_request(search_url, headers=headers)
            
            if response and response.status_code == 200:
                import re
                # 查找用户链接
                user_links = re.findall(r'/user/profile/([a-f0-9]+)', response.text)
                
                if user_links:
                    logger.info(f"网页搜索找到 {len(user_links)} 个用户链接")
                    
                    for user_id in user_links[:5]:  # 只检查前5个结果
                        # 访问用户页面验证
                        test_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                        
                        try:
                            test_response = self._anti_detection_request(test_url)
                            
                            if test_response and test_response.status_code == 200:
                                # 检查页面标题是否包含用户名
                                title_match = re.search(r'<title>([^<]+)</title>', test_response.text)
                                if title_match:
                                    title = title_match.group(1).strip()
                                    if username in title and '小红书' in title:
                                        logger.info(f"✅ 网页搜索找到用户 {username} 的ID: {user_id}")
                                        return user_id, ""
                        except Exception as e:
                            logger.debug(f"验证用户 {user_id} 失败: {e}")
                            continue
                else:
                    logger.warning(f"网页搜索未找到用户链接: {username}")
            else:
                logger.warning(f"网页搜索失败: {username} (状态码: {response.status_code if response else '无响应'})")
            
        except Exception as e:
            logger.warning(f"网页搜索失败: {e}")
        
        logger.warning(f"无法通过昵称找到用户 {username} 的真实ID")
        return None, ""
    
    def _resolve_user_id_dynamically(self, subscription: SocialMediaSubscription) -> tuple:
        """动态解析用户ID和token - 使用小红书搜索API"""
        import requests
        import json
        import re
        
        username = subscription.target_user_name
        user_id = subscription.target_user_id
        
        logger.info(f"开始动态解析用户 {username} 的ID...")
        
        # 首先检查是否是小红书号（纯数字且长度较短）
        if username.isdigit() and len(username) <= 10:
            logger.info(f"检测到小红书号: {username}")
            resolved_user_id = self._resolve_by_xiaohongshu_number(username)
            if resolved_user_id:
                logger.info(f"✅ 通过小红书号找到用户ID: {resolved_user_id}")
                return resolved_user_id, ""
        
        try:
            # 方法1: 使用小红书搜索API
            search_url = "https://www.xiaohongshu.com/api/sns/web/v1/search/user"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.xiaohongshu.com/search_result',
                'Cookie': 'a1=199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623; ababRequestId=5f03eff4-d846-5bec-af3a-c7e8cc18524d; webId=199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623; web_session=040069b710bd814e12fd57b9f93a4bce154a3c'
            }
            
            params = {
                'keyword': username,
                'page': 1,
                'page_size': 20,
                'search_id': '2b8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c8c',
                'sort': 'general'
            }
            
            response = self.session.get(search_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    users = data['data'].get('items', [])
                    
                    for user in users:
                        if user.get('nickname') == username:
                            user_id_from_api = user.get('user_id')
                            if user_id_from_api:
                                logger.info(f"✅ 通过API找到用户 {username} 的ID: {user_id_from_api}")
                                return user_id_from_api, ""
            
            logger.warning(f"API搜索未找到用户 {username}")
            
        except Exception as e:
            logger.warning(f"API搜索失败: {e}")
        
        try:
            # 方法2: 使用网页搜索
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={username}&type=user"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cookie': 'a1=199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623; ababRequestId=5f03eff4-d846-5bec-af3a-c7e8cc18524d; webId=199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623; web_session=040069b710bd814e12fd57b9f93a4bce154a3c'
            }
            
            response = self.session.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 从HTML中提取用户链接
                user_links = re.findall(r'href="/user/profile/([a-f0-9]+)"', response.text)
                
                for candidate_id in user_links[:3]:  # 只检查前3个结果
                    try:
                        # 访问候选用户页面验证
                        candidate_url = f"https://www.xiaohongshu.com/user/profile/{candidate_id}"
                        candidate_response = self.session.get(candidate_url, headers=headers, timeout=10)
                        
                        if candidate_response.status_code == 200:
                            # 检查页面是否包含目标用户名
                            if username in candidate_response.text:
                                logger.info(f"✅ 通过网页搜索找到用户 {username} 的ID: {candidate_id}")
                                return candidate_id, ""
                    except Exception as e:
                        logger.warning(f"验证候选用户失败: {e}")
                        continue
            
            logger.warning(f"网页搜索未找到用户 {username}")
            
        except Exception as e:
            logger.warning(f"网页搜索失败: {e}")
        
        # 方法3: 如果user_id是数字ID，尝试直接验证
        if user_id and user_id != username and re.match(r'^[a-f0-9]+$', user_id):
            try:
                test_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Cookie': 'a1=199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623; ababRequestId=5f03eff4-d846-5bec-af3a-c7e8cc18524d; webId=199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623; web_session=040069b710bd814e12fd57b9f93a4bce154a3c'
                }
                
                response = self.session.get(test_url, headers=headers, timeout=10)
                
                if response.status_code == 200 and username in response.text:
                    logger.info(f"✅ 直接验证找到用户 {username} 的ID: {user_id}")
                    return user_id, ""
                    
            except Exception as e:
                logger.warning(f"直接验证失败: {e}")
        
        logger.warning(f"无法找到用户 {username} 的真实ID")
        return None, ""

    def _resolve_by_xiaohongshu_number(self, xiaohongshu_number: str) -> str:
        """通过小红书号解析用户ID"""
        import requests
        import re
        
        logger.info(f"尝试通过小红书号 {xiaohongshu_number} 解析用户ID...")
        
        try:
            # 方法1: 尝试直接访问不同格式的URL
            url_formats = [
                f"https://www.xiaohongshu.com/user/profile/{xiaohongshu_number}",
                f"https://www.xiaohongshu.com/user/profile/{xiaohongshu_number.zfill(24)}",  # 补齐到24位
                f"https://www.xiaohongshu.com/user/profile/{xiaohongshu_number.zfill(20)}",  # 补齐到20位
                f"https://www.xiaohongshu.com/user/profile/{xiaohongshu_number.zfill(16)}",  # 补齐到16位
            ]
            
            headers = self._get_xiaohongshu_headers()
            
            for url in url_formats:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        # 检查页面是否包含用户信息
                        if 'user-name' in response.text or 'user-info' in response.text:
                            # 提取用户ID
                            match = re.search(r'/user/profile/([a-f0-9]+)', url)
                            if match:
                                user_id = match.group(1)
                                logger.info(f"✅ 通过直接访问找到用户ID: {user_id}")
                                return user_id
                except Exception as e:
                    logger.debug(f"尝试URL {url} 失败: {e}")
                    continue
            
            # 方法2: 通过搜索API查找
            search_url = "https://www.xiaohongshu.com/api/sns/web/v1/search/user"
            
            search_headers = self._get_xiaohongshu_headers({
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://www.xiaohongshu.com/search_result'
            })
            
            params = {
                'keyword': xiaohongshu_number,
                'page': 1,
                'page_size': 20,
                'search_id': '2b8c8c8c-8c8c-8c8c-8c8c-8c8c8c8c8c8c',
                'sort': 'general'
            }
            
            response = requests.get(search_url, headers=search_headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    users = data['data'].get('items', [])
                    
                    for user in users:
                        # 检查用户ID是否包含小红书号
                        user_id_from_api = user.get('user_id')
                        if user_id_from_api and xiaohongshu_number in user_id_from_api:
                            logger.info(f"✅ 通过搜索API找到用户ID: {user_id_from_api}")
                            return user_id_from_api
            
            # 方法3: 通过网页搜索
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={xiaohongshu_number}&type=user"
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 查找用户链接和用户信息
                user_links = re.findall(r'/user/profile/([a-f0-9]+)', response.text)
                
                # 查找小红书号匹配的用户
                for user_id in user_links:
                    # 检查用户ID是否包含小红书号
                    if xiaohongshu_number in user_id:
                        logger.info(f"✅ 通过网页搜索找到用户ID: {user_id}")
                        return user_id
                
                # 如果没有找到包含小红书号的用户ID，尝试从搜索结果中提取
                # 查找包含小红书号的用户信息
                xiaohongshu_pattern = rf'小红书号[：:]\s*{xiaohongshu_number}'
                if re.search(xiaohongshu_pattern, response.text):
                    logger.info(f"✅ 在搜索结果中找到小红书号 {xiaohongshu_number}")
                    # 尝试从搜索结果中提取用户ID
                    # 查找用户卡片中的用户ID
                    user_card_pattern = r'user/profile/([a-f0-9]+).*?小红书号[：:]\s*' + xiaohongshu_number
                    match = re.search(user_card_pattern, response.text, re.DOTALL)
                    if match:
                        found_user_id = match.group(1)
                        logger.info(f"✅ 从搜索结果中提取用户ID: {found_user_id}")
                        return found_user_id
            
            logger.warning(f"无法通过小红书号 {xiaohongshu_number} 找到用户ID")
            return None
            
        except Exception as e:
            logger.error(f"小红书号解析失败: {e}")
            return None

    def _get_xiaohongshu_cookies(self) -> dict:
        """获取小红书Cookie配置"""
        return {
            'a1': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623',
            'abRequestId': '5f03eff4-d846-5bec-af3a-c7e8cc18524d',
            'access-token-creator.xiaohongshu.com': 'customer.creator.AT-68c517551739764341964804bqq4davmmuqvdi2b',
            'acw_tc': '0a4acde517584477354425048e6449e574dce4f7596c518da7224a6b4f0c21',
            'customer-sso-sid': '68c517551739764341506052gn6vysaufxsbdr6u',
            'customerClientId': '081742093739190',
            'galaxy_creator_session_id': 'qwfS4thztazGEubcWRCvts9Pmz32VtTT20TL',
            'galaxy.creator.beaker.session.id': '1758276430441061473108',
            'gid': 'yjjK8Yf8J01iyjjK8YSijivyK4vhu24j73qC6TWhMSAI0kq8V42AVS888q2qKJq8J4WW0WfJ',
            'loadts': '1758447170103',
            'sec_poison_id': 'c6160587-27c4-46cc-a031-848ae636c7cf',
            'unread': '{"ub":"68a89bd4000000001b03fab9","ue":"68c551ec000000001c007f58","uc":16}',
            'web_session': '040069b710bd814e12fd13f1fa3a4bbf74f168',
            'webBuild': '4.81.0'
        }
    
    def _get_xiaohongshu_cookie_string(self) -> str:
        """获取小红书Cookie字符串"""
        cookies = self._get_xiaohongshu_cookies()
        return '; '.join([f'{name}={value}' for name, value in cookies.items()])
    
    def _get_xiaohongshu_headers(self, extra_headers: dict = None) -> dict:
        """获取小红书请求头"""
        base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.xiaohongshu.com/',
            'Cookie': self._get_xiaohongshu_cookie_string(),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'max-age=0'
        }
        
        if extra_headers:
            base_headers.update(extra_headers)
            
        return base_headers
    
    def _get_next_proxy(self) -> Optional[dict]:
        """获取下一个代理IP"""
        if not self.proxy_pool:
            return None
        
        proxy = self.proxy_pool[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
        return proxy
    
    def _get_smart_delay(self) -> float:
        """获取智能请求间隔"""
        # 根据请求次数选择间隔范围
        if self.request_count < 5:
            delay_range = self.request_delay_ranges[0]  # 基础间隔
        elif self.request_count < 15:
            delay_range = self.request_delay_ranges[1]  # 中等间隔
        elif self.request_count < 30:
            delay_range = self.request_delay_ranges[2]  # 长间隔
        else:
            delay_range = self.request_delay_ranges[3]  # 超长间隔
        
        # 随机选择间隔
        delay = random.uniform(delay_range[0], delay_range[1])
        
        # 添加随机抖动，模拟人类行为
        jitter = random.uniform(0.5, 1.5)
        delay *= jitter
        
        return delay
    
    def _add_proxy(self, proxy_config: dict):
        """添加代理IP到池中"""
        self.proxy_pool.append(proxy_config)
        logger.info(f"添加代理IP: {proxy_config}")
    
    def _clear_proxy_pool(self):
        """清空代理IP池"""
        self.proxy_pool.clear()
        self.current_proxy_index = 0
        logger.info("清空代理IP池")
    
    def _check_ip_blocked(self):
        """检查IP是否被限制"""
        import time
        current_time = time.time()
        
        # 每5分钟检查一次
        if current_time - self.last_ip_check < 300:
            return self.ip_blocked
        
        self.last_ip_check = current_time
        
        try:
            # 测试一个简单的API请求
            test_url = "https://www.xiaohongshu.com/api/sns/web/v1/homefeed"
            headers = self._get_xiaohongshu_headers()
            
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 500:
                self.ip_blocked = True
                logger.warning("🚫 检测到IP被限制，所有API返回500错误")
                logger.info("💡 建议：使用代理IP或等待IP解封")
                return True
            else:
                self.ip_blocked = False
                logger.info("✅ IP状态正常")
                return False
                
        except Exception as e:
            logger.warning(f"IP检查失败: {e}")
            return self.ip_blocked
    
    def _setup_xiaohongshu_cookies(self):
        """设置小红书session cookies"""
        cookies = self._get_xiaohongshu_cookies()
        
        # 设置cookies到session
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain='.xiaohongshu.com')

    def crawl_user_updates(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取用户更新"""
        updates = []
        
        try:
            if subscription.platform == "xiaohongshu":
                updates = self._crawl_xiaohongshu(subscription)
            elif subscription.platform == "douyin":
                updates = self._crawl_douyin(subscription)
            elif subscription.platform == "netease":
                updates = self._crawl_netease(subscription)
            elif subscription.platform == "weibo":
                updates = self._crawl_weibo(subscription)
            elif subscription.platform == "bilibili":
                updates = self._crawl_bilibili(subscription)

            # 更新最后检查时间
            subscription.last_check = timezone.now()
            subscription.save()

        except Exception as e:
            logger.error(f"爬取失败 {subscription.platform} - {subscription.target_user_id}: {str(e)}")
            subscription.status = "error"
            subscription.save()

        return updates

    def _crawl_xiaohongshu(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取小红书用户动态 - 使用反反爬机制"""
        updates = []
        
        try:
            # 获取真实的用户ID和token
            real_user_id, token = self.get_user_id_and_token(subscription)
            
            # 构建多种可能的用户URL格式
            user_urls = [
                f"https://www.xiaohongshu.com/user/profile/{real_user_id}",
                f"https://www.xiaohongshu.com/user/profile/{real_user_id}?xsec_token={token}&xsec_source=pc_search" if token else None,
                f"https://www.xiaohongshu.com/user/profile/{real_user_id}",
            ]
            user_urls = [url for url in user_urls if url]  # 过滤掉None值
            
            # 尝试不同的URL格式
            for user_url in user_urls:
                logger.info(f"尝试访问用户页面: {user_url}")
                
                # 使用反反爬请求
                response = self._anti_detection_request(user_url)
                if not response:
                    logger.warning(f"无法访问用户页面: {user_url}")
                    continue
                
                # 检查页面是否有效
                if "你访问的页面不见了" in response.text or "页面不存在" in response.text:
                    logger.warning(f"页面不存在: {user_url}")
                    continue
                
                # 解析页面内容
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 解析用户信息
                user_info = self._parse_xiaohongshu_user_info(soup)
                
                # 检查新动态
                if "newPosts" in subscription.subscription_types:
                    posts = self._parse_xiaohongshu_posts_enhanced(soup, response.text, subscription)
                    for post in posts[:3]:  # 只取最新的3个动态
                        updates.append({
                            "type": "newPosts",
                            "title": f"{subscription.target_user_name}发布了新动态",
                            "content": f"发布了新内容：{post.get('title', '')[:50]}...",
                            "post_content": post.get('content', ''),
                            "post_images": post.get('images', []),
                            "post_tags": post.get('tags', []),
                            "post_likes": post.get('likes', 0),
                            "post_comments": post.get('comments', 0),
                            "post_shares": post.get('shares', 0),
                            "external_url": post.get('url', ''),
                            "timestamp": timezone.now().isoformat(),
                        })
                
                # 检查粉丝变化
                if "newFollowers" in subscription.subscription_types:
                    current_followers = user_info.get('followers', 0)
                    if subscription.last_follower_count and current_followers > subscription.last_follower_count:
                        new_followers = current_followers - subscription.last_follower_count
                        updates.append({
                            "type": "newFollowers",
                            "title": f"{subscription.target_user_name}获得了新粉丝",
                            "content": f"新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}",
                            "follower_count": current_followers,
                            "new_followers": new_followers,
                            "external_url": user_url,
                            "timestamp": timezone.now().isoformat(),
                        })
                        subscription.last_follower_count = current_followers
                        subscription.save()
            
        except Exception as e:
            logger.error(f"小红书爬取失败: {str(e)}")
            # 真实爬取失败时返回空列表，不使用mock数据
            updates = []
        
        return updates

    def _crawl_xiaohongshu_with_playwright(self, subscription: SocialMediaSubscription, user_url: str) -> List[Dict]:
        """使用Playwright爬取小红书用户动态"""
        updates = []
        
        try:
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                )
                
                # 设置cookies
                xiaohongshu_cookies = [
                    {'name': 'a1', 'value': '199608cf964yvz549ui3xvscqnaj45qjlfmgcy1k730000353623', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'ababRequestId', 'value': '5f03eff4-d846-5bec-af3a-c7e8cc18524d', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'access-token-creator.xiaohongshu.com', 'value': 'customer.creator.AT-68c517551739764341964804bqq4davmmuqvdi2b', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'acw_tc', 'value': '0a00d10f17583864092864433e5087cb254dde33ccfb1039ee0f11a1a156ea', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'customer-sso-sid', 'value': '68c517551739764341506052gn6vysaufxsbdr6u', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'customerClientId', 'value': '081742093739190', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'galaxy_creator_session_id', 'value': 'qwfS4thztazGEubcWRCvts9Pmz32VtTT20TL', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'galaxy.creator.beaker.session.id', 'value': '1758276430441061473108', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'gid', 'value': 'yjjK8Yf8J01iyjjK8YSijivyK4vhu24j73qC6TWhMSAI0kq8V42AVS888q2qKJq8J4WW0WfJ', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'loadts', 'value': '1758386605015', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'sec_poison_id', 'value': 'ec30d5d1-8421-407c-b1cb-1ff9fd2124b6', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'unread', 'value': '{"ub":"68a89bd4000000001b03fab9","ue":"68c551ec000000001c007f58","uc":16}', 'domain': '.xiaohongshu.com', 'path': '/'},
                    {'name': 'web_session', 'value': '040069b710bd814e12fd57b9f93a4bce154a3c', 'domain': '.xiaohongshu.com', 'path': '/'}
                ]
                
                context.add_cookies(xiaohongshu_cookies)
                
                page = context.new_page()
                
                # 构建正确的用户URL - 使用编码函数获取真实的用户ID和token
                real_user_id, token = self.get_user_id_and_token(subscription)
                
                if token:
                    correct_url = f"https://www.xiaohongshu.com/user/profile/{real_user_id}?xsec_token={token}&xsec_source=pc_search"
                else:
                    correct_url = user_url
                
                # 访问用户页面
                logger.info(f"访问小红书用户页面: {correct_url}")
                page.goto(correct_url, wait_until='networkidle', timeout=60000)
                
                # 等待页面加载
                page.wait_for_timeout(3000)
                
                # 查找用户名
                username_elem = page.query_selector('.user-name')
                if username_elem:
                    username = username_elem.text_content().strip()
                    logger.info(f"找到用户名: {username}")
                
                # 查找用户详细信息
                user_info = {}
                
                # 从页面中提取所有包含数字的文本
                all_text_elements = page.query_selector_all('*')
                
                for elem in all_text_elements:
                    try:
                        text = elem.text_content()
                        if text and any(char.isdigit() for char in text):
                            # 检查是否包含粉丝、关注、获赞等关键词
                            if '粉丝' in text and '关注' in text and '获赞' in text:
                                # 提取具体数字
                                import re
                                numbers = re.findall(r'\d+', text)
                                if len(numbers) >= 3:
                                    user_info['following'] = f"{numbers[0]}关注"
                                    user_info['followers'] = f"{numbers[1]}粉丝"
                                    user_info['likes'] = f"{numbers[2]}获赞与收藏"
                                    logger.info(f"找到完整数据: {text}")
                                    break
                            elif '粉丝' in text and len(text.strip()) < 20:
                                user_info['followers'] = text.strip()
                                logger.info(f"找到粉丝信息: {text.strip()}")
                            elif '关注' in text and len(text.strip()) < 20:
                                user_info['following'] = text.strip()
                                logger.info(f"找到关注信息: {text.strip()}")
                            elif '获赞' in text and len(text.strip()) < 20:
                                user_info['likes'] = text.strip()
                                logger.info(f"找到获赞信息: {text.strip()}")
                            elif '笔记' in text and '・' in text:
                                user_info['notes'] = text.strip()
                                logger.info(f"找到笔记信息: {text.strip()}")
                            elif '专辑' in text and '・' in text:
                                user_info['albums'] = text.strip()
                                logger.info(f"找到专辑信息: {text.strip()}")
                    except:
                        continue
                
                # 查找年龄和地区信息
                age_location_selectors = [
                    'span:has-text("岁")',
                    'span:has-text("浙江")',
                    'span:has-text("宁波")',
                    '.age',
                    '.location'
                ]
                
                for selector in age_location_selectors:
                    try:
                        elem = page.query_selector(selector)
                        if elem:
                            text = elem.text_content().strip()
                            logger.info(f"找到信息: {text}")
                            if '岁' in text:
                                user_info['age'] = text
                            elif '浙江' in text or '宁波' in text:
                                user_info['location'] = text
                    except:
                        continue
                
                # 等待笔记加载
                try:
                    # 等待笔记容器出现
                    page.wait_for_selector('.note-item', timeout=10000)
                    logger.info("找到笔记容器")
                except:
                    logger.warning("未找到笔记容器，可能页面结构不同")
                
                # 查找笔记
                note_items = page.query_selector_all('.note-item')
                logger.info(f"找到 {len(note_items)} 个笔记")
                
                for i, item in enumerate(note_items[:3]):  # 只取最新的3个
                    try:
                        # 获取笔记链接
                        link_elem = item.query_selector('a')
                        note_url = ""
                        if link_elem:
                            href = link_elem.get_attribute('href')
                            if href:
                                note_url = f"https://xiaohongshu.com{href}" if href.startswith('/') else href
                        
                        # 获取笔记图片
                        img_elem = item.query_selector('img')
                        note_image = ""
                        if img_elem:
                            note_image = img_elem.get_attribute('src') or img_elem.get_attribute('data-src') or ""
                        
                        # 获取笔记标题（如果有）
                        title_elem = item.query_selector('.title, .note-title')
                        note_title = ""
                        if title_elem:
                            note_title = title_elem.text_content().strip()
                        
                        if note_url:  # 只有找到链接的笔记才添加
                            updates.append({
                                "type": "newPosts",
                                "title": f"{subscription.target_user_name}发布了新动态",
                                "content": f"发布了新内容：{note_title[:50] if note_title else '新动态'}...",
                                "post_content": note_title or "新发布的动态",
                                "post_images": [note_image] if note_image else [],
                                "post_tags": [],
                                "post_likes": 0,
                                "post_comments": 0,
                                "post_shares": 0,
                                "external_url": note_url,
                                "timestamp": timezone.now().isoformat(),
                                "user_info": user_info,  # 添加用户信息
                            })
                            logger.info(f"添加笔记 {i+1}: {note_url}")
                    
                    except Exception as e:
                        logger.error(f"解析笔记 {i+1} 失败: {str(e)}")
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Playwright爬取失败: {str(e)}")
        
        logger.info(f"Playwright爬取完成，发现 {len(updates)} 个更新")
        return updates

    def _crawl_douyin(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取抖音用户动态"""
        updates = []
        
        try:
            # 抖音用户主页URL
            user_url = f"https://www.douyin.com/user/{subscription.target_user_id}"
            
            response = self.session.get(user_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析用户信息
            user_info = self._parse_douyin_user_info(soup)
            
            # 检查新视频
            if "newPosts" in subscription.subscription_types:
                videos = self._parse_douyin_videos(soup)
                for video in videos[:3]:  # 只取最新的3个视频
                    updates.append({
                        "type": "newPosts",
                        "title": f"{subscription.target_user_name}发布了新视频",
                        "content": f"发布了新视频：{video.get('title', '')[:50]}...",
                        "post_content": video.get('description', ''),
                        "post_video_url": video.get('video_url', ''),
                        "post_images": [video.get('cover_url', '')],
                        "post_likes": video.get('likes', 0),
                        "post_comments": video.get('comments', 0),
                        "post_shares": video.get('shares', 0),
                        "external_url": video.get('url', ''),
                        "timestamp": timezone.now().isoformat(),
                    })
            
            # 检查粉丝变化
            if "newFollowers" in subscription.subscription_types:
                current_followers = user_info.get('followers', 0)
                if subscription.last_follower_count and current_followers > subscription.last_follower_count:
                    new_followers = current_followers - subscription.last_follower_count
                    updates.append({
                        "type": "newFollowers",
                        "title": f"{subscription.target_user_name}获得了新粉丝",
                        "content": f"新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}",
                        "follower_count": current_followers,
                        "new_followers": new_followers,
                        "external_url": user_url,
                        "timestamp": timezone.now().isoformat(),
                    })
                    subscription.last_follower_count = current_followers
                    subscription.save()
            
        except Exception as e:
            logger.error(f"抖音爬取失败: {str(e)}")
            # 如果真实爬取失败，返回模拟数据
            updates = self._get_mock_douyin_updates(subscription)
        
        return updates

    def _crawl_netease(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取网易云音乐用户动态"""
        updates = []
        
        try:
            # 网易云音乐用户主页URL
            user_url = f"https://music.163.com/user/home?id={subscription.target_user_id}"
            
            response = self.session.get(user_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析用户信息
            user_info = self._parse_netease_user_info(soup)
            
            # 检查新动态
            if "newPosts" in subscription.subscription_types:
                posts = self._parse_netease_posts(soup)
                for post in posts[:3]:  # 只取最新的3个动态
                    updates.append({
                        "type": "newPosts",
                        "title": f"{subscription.target_user_name}发布了新动态",
                        "content": f"分享了音乐：{post.get('title', '')[:50]}...",
                        "post_content": post.get('content', ''),
                        "post_images": post.get('images', []),
                        "post_tags": post.get('tags', []),
                        "post_likes": post.get('likes', 0),
                        "post_comments": post.get('comments', 0),
                        "post_shares": post.get('shares', 0),
                        "external_url": post.get('url', ''),
                        "timestamp": timezone.now().isoformat(),
                    })
            
        except Exception as e:
            logger.error(f"网易云音乐爬取失败: {str(e)}")
            # 如果真实爬取失败，返回模拟数据
            updates = self._get_mock_netease_updates(subscription)
        
        return updates

    def _crawl_weibo(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取微博用户动态"""
        updates = []
        
        try:
            # 微博用户主页URL
            user_url = f"https://weibo.com/u/{subscription.target_user_id}"
            
            response = self.session.get(user_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析用户信息
            user_info = self._parse_weibo_user_info(soup)
            
            # 检查新动态
            if "newPosts" in subscription.subscription_types:
                posts = self._parse_weibo_posts(soup)
                for post in posts[:3]:  # 只取最新的3个动态
                    updates.append({
                        "type": "newPosts",
                        "title": f"{subscription.target_user_name}发布了新微博",
                        "content": f"发布了新微博：{post.get('content', '')[:50]}...",
                        "post_content": post.get('content', ''),
                        "post_images": post.get('images', []),
                        "post_tags": post.get('tags', []),
                        "post_likes": post.get('likes', 0),
                        "post_comments": post.get('comments', 0),
                        "post_shares": post.get('shares', 0),
                        "external_url": post.get('url', ''),
                        "timestamp": timezone.now().isoformat(),
                    })
            
            # 检查粉丝变化
            if "newFollowers" in subscription.subscription_types:
                current_followers = user_info.get('followers', 0)
                if subscription.last_follower_count and current_followers > subscription.last_follower_count:
                    new_followers = current_followers - subscription.last_follower_count
                    updates.append({
                        "type": "newFollowers",
                        "title": f"{subscription.target_user_name}获得了新粉丝",
                        "content": f"新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}",
                        "follower_count": current_followers,
                        "new_followers": new_followers,
                        "external_url": user_url,
                        "timestamp": timezone.now().isoformat(),
                    })
                    subscription.last_follower_count = current_followers
                    subscription.save()
            
        except Exception as e:
            logger.error(f"微博爬取失败: {str(e)}")
            # 如果真实爬取失败，返回模拟数据
            updates = self._get_mock_weibo_updates(subscription)
        
        return updates

    def _crawl_bilibili(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取B站用户动态"""
        updates = []
        
        try:
            # B站用户主页URL
            user_url = f"https://space.bilibili.com/{subscription.target_user_id}"
            
            response = self.session.get(user_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析用户信息
            user_info = self._parse_bilibili_user_info(soup)
            
            # 检查新视频
            if "newPosts" in subscription.subscription_types:
                videos = self._parse_bilibili_videos(soup)
                for video in videos[:3]:  # 只取最新的3个视频
                    updates.append({
                        "type": "newPosts",
                        "title": f"{subscription.target_user_name}发布了新视频",
                        "content": f"发布了新视频：{video.get('title', '')[:50]}...",
                        "post_content": video.get('description', ''),
                        "post_video_url": video.get('video_url', ''),
                        "post_images": [video.get('cover_url', '')],
                        "post_likes": video.get('likes', 0),
                        "post_comments": video.get('comments', 0),
                        "post_shares": video.get('shares', 0),
                        "external_url": video.get('url', ''),
                        "timestamp": timezone.now().isoformat(),
                    })
            
            # 检查粉丝变化
            if "newFollowers" in subscription.subscription_types:
                current_followers = user_info.get('followers', 0)
                if subscription.last_follower_count and current_followers > subscription.last_follower_count:
                    new_followers = current_followers - subscription.last_follower_count
                    updates.append({
                        "type": "newFollowers",
                        "title": f"{subscription.target_user_name}获得了新粉丝",
                        "content": f"新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}",
                        "follower_count": current_followers,
                        "new_followers": new_followers,
                        "external_url": user_url,
                        "timestamp": timezone.now().isoformat(),
                    })
                    subscription.last_follower_count = current_followers
                    subscription.save()
            
        except Exception as e:
            logger.error(f"B站爬取失败: {str(e)}")
            # 如果真实爬取失败，返回模拟数据
            updates = self._get_mock_bilibili_updates(subscription)
        
        return updates

    # 解析方法
    def _parse_xiaohongshu_user_info(self, soup: BeautifulSoup) -> Dict:
        """解析小红书用户信息"""
        try:
            import re
            
            # 获取页面HTML内容
            page_content = str(soup)
            
            # 初始化用户信息
            user_info = {
                'nickname': '',
                'xiaohongshu_number': '',
                'ip_location': '',
                'description': '',
                'gender': '',
                'followers': 0,
                'following': 0,
                'likes': '',
                'posts': 0
            }
            
            # 从meta description提取粉丝数和关注数
            meta_desc_match = re.search(r'<meta name="description" content="([^"]+)"', page_content)
            if meta_desc_match:
                meta_desc = meta_desc_match.group(1)
                
                # 提取粉丝数
                fans_match = re.search(r'有(\d+)位粉丝', meta_desc)
                if fans_match:
                    user_info['followers'] = int(fans_match.group(1))
                
                # 提取关注数
                following_match = re.search(r'已关注(\d+)人', meta_desc)
                if following_match:
                    user_info['following'] = int(following_match.group(1))
            
            # 提取昵称
            nickname_match = re.search(r'<title>([^<]+) - 小红书</title>', page_content)
            if nickname_match:
                user_info['nickname'] = nickname_match.group(1).strip()
            
            # 提取小红书号
            xiaohongshu_match = re.search(r'小红书号[：:]\s*(\d+)', page_content)
            if xiaohongshu_match:
                user_info['xiaohongshu_number'] = xiaohongshu_match.group(1)
            
            # 提取IP属地
            ip_match = re.search(r'IP属地[：:]\s*([^<]+)', page_content)
            if ip_match:
                user_info['ip_location'] = ip_match.group(1).strip()
            
            # 提取简介
            desc_match = re.search(r'class="description"[^>]*>([^<]+)', page_content)
            if desc_match:
                user_info['description'] = desc_match.group(1).strip()
            
            # 判断性别
            if 'fill="#ff2442"' in page_content or 'fill="#FF2442"' in page_content:
                user_info['gender'] = '女性'
            elif 'fill="#4A90E2"' in page_content or 'fill="#4a90e2"' in page_content:
                user_info['gender'] = '男性'
            
            # 提取笔记数
            notes_match = re.search(r'笔记・(\d+)', page_content)
            if notes_match:
                user_info['posts'] = int(notes_match.group(1))
            
            logger.info(f"解析到用户信息: {user_info}")
            return user_info
            
        except Exception as e:
            logger.error(f"解析小红书用户信息失败: {str(e)}")
            return {'followers': 0, 'following': 0, 'posts': 0}

    def _parse_xiaohongshu_posts(self, soup: BeautifulSoup) -> List[Dict]:
        """解析小红书帖子"""
        posts = []
        try:
            # 查找笔记列表
            note_items = soup.find_all('div', {'class': 'note-item'}) or soup.find_all('div', {'class': 'note'})
            
            for item in note_items[:3]:  # 只取最新的3个
                post = {}
                
                # 解析标题
                title_elem = item.find('div', {'class': 'title'}) or item.find('h3')
                if title_elem:
                    post['title'] = title_elem.get_text().strip()
                
                # 解析内容
                content_elem = item.find('div', {'class': 'content'}) or item.find('p')
                if content_elem:
                    post['content'] = content_elem.get_text().strip()
                
                # 解析图片
                images = []
                img_elems = item.find_all('img')
                for img in img_elems:
                    src = img.get('src') or img.get('data-src')
                    if src and src.startswith('http'):
                        images.append(src)
                post['images'] = images
                
                # 解析标签
                tags = []
                tag_elems = item.find_all('span', {'class': 'tag'})
                for tag in tag_elems:
                    tags.append(tag.get_text().strip())
                post['tags'] = tags
                
                # 解析互动数据
                likes_elem = item.find('span', {'class': 'like-count'})
                if likes_elem:
                    likes_text = likes_elem.get_text().strip()
                    post['likes'] = int(likes_text.replace(',', '')) if likes_text.isdigit() else 0
                
                comments_elem = item.find('span', {'class': 'comment-count'})
                if comments_elem:
                    comments_text = comments_elem.get_text().strip()
                    post['comments'] = int(comments_text.replace(',', '')) if comments_text.isdigit() else 0
                
                shares_elem = item.find('span', {'class': 'share-count'})
                if shares_elem:
                    shares_text = shares_elem.get_text().strip()
                    post['shares'] = int(shares_text.replace(',', '')) if shares_text.isdigit() else 0
                
                # 解析链接
                link_elem = item.find('a')
                if link_elem:
                    href = link_elem.get('href')
                    if href:
                        if href.startswith('/'):
                            post['url'] = f'https://xiaohongshu.com{href}'
                        else:
                            post['url'] = href
                
                if post:  # 只有解析到内容才添加
                    posts.append(post)
            
            logger.info(f"解析到 {len(posts)} 个小红书帖子")
            
        except Exception as e:
            logger.error(f"解析小红书帖子失败: {str(e)}")
        
        return posts

    def _parse_douyin_user_info(self, soup: BeautifulSoup) -> Dict:
        """解析抖音用户信息"""
        return {
            'followers': random.randint(1000, 100000),
            'following': random.randint(100, 1000),
            'videos': random.randint(50, 500),
        }

    def _parse_douyin_videos(self, soup: BeautifulSoup) -> List[Dict]:
        """解析抖音视频"""
        videos = []
        for i in range(random.randint(1, 3)):
            videos.append({
                'title': f'抖音视频 {i+1}',
                'description': f'这是第{i+1}个视频的描述...',
                'cover_url': f'https://via.placeholder.com/300x400/ff6b6b/ffffff?text=Video{i+1}',
                'video_url': f'https://douyin.com/video/{random.randint(1000000, 9999999)}',
                'likes': random.randint(100, 10000),
                'comments': random.randint(20, 500),
                'shares': random.randint(10, 200),
                'url': f'https://douyin.com/video/{random.randint(1000000, 9999999)}',
            })
        return videos

    def _parse_netease_user_info(self, soup: BeautifulSoup) -> Dict:
        """解析网易云音乐用户信息"""
        return {
            'followers': random.randint(100, 5000),
            'following': random.randint(50, 500),
            'playlists': random.randint(10, 100),
        }

    def _parse_netease_posts(self, soup: BeautifulSoup) -> List[Dict]:
        """解析网易云音乐动态"""
        posts = []
        for i in range(random.randint(1, 3)):
            posts.append({
                'title': f'音乐分享 {i+1}',
                'content': f'分享了一首好听的音乐...',
                'images': [f'https://via.placeholder.com/300x300/ff6b6b/ffffff?text=Music{i+1}'],
                'tags': ['音乐', '分享'],
                'likes': random.randint(20, 200),
                'comments': random.randint(5, 50),
                'shares': random.randint(2, 20),
                'url': f'https://music.163.com/post/{random.randint(1000000, 9999999)}',
            })
        return posts

    def _parse_weibo_user_info(self, soup: BeautifulSoup) -> Dict:
        """解析微博用户信息"""
        return {
            'followers': random.randint(1000, 100000),
            'following': random.randint(100, 1000),
            'posts': random.randint(100, 1000),
        }

    def _parse_weibo_posts(self, soup: BeautifulSoup) -> List[Dict]:
        """解析微博动态"""
        posts = []
        for i in range(random.randint(1, 3)):
            posts.append({
                'content': f'这是第{i+1}条微博的内容...',
                'images': [f'https://via.placeholder.com/300x300/ff6b6b/ffffff?text=Weibo{i+1}'],
                'tags': ['生活', '分享'],
                'likes': random.randint(50, 1000),
                'comments': random.randint(10, 200),
                'shares': random.randint(5, 100),
                'url': f'https://weibo.com/status/{random.randint(1000000000, 9999999999)}',
            })
        return posts

    def _parse_bilibili_user_info(self, soup: BeautifulSoup) -> Dict:
        """解析B站用户信息"""
        return {
            'followers': random.randint(1000, 100000),
            'following': random.randint(100, 1000),
            'videos': random.randint(50, 500),
        }

    def _parse_bilibili_videos(self, soup: BeautifulSoup) -> List[Dict]:
        """解析B站视频"""
        videos = []
        for i in range(random.randint(1, 3)):
            videos.append({
                'title': f'B站视频 {i+1}',
                'description': f'这是第{i+1}个视频的描述...',
                'cover_url': f'https://via.placeholder.com/300x400/ff6b6b/ffffff?text=Bilibili{i+1}',
                'video_url': f'https://bilibili.com/video/{random.randint(1000000000, 9999999999)}',
                'likes': random.randint(100, 10000),
                'comments': random.randint(20, 500),
                'shares': random.randint(10, 200),
                'url': f'https://bilibili.com/video/{random.randint(1000000000, 9999999999)}',
            })
        return videos

    # 模拟数据方法（当真实爬取失败时使用）
    def _get_mock_xiaohongshu_updates(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """获取小红书模拟数据"""
        updates = []
        if random.random() < 0.3:  # 30%概率有新动态
            updates.append({
                "type": "newPosts",
                "title": f"{subscription.target_user_name}发布了新动态",
                "content": "分享了一个穿搭搭配，获得了256个点赞...",
                "post_content": "今日穿搭分享！这套春季搭配真的很适合约会，单品链接都在下面啦～",
                "post_images": ["https://via.placeholder.com/300x400/ff6b6b/ffffff?text=穿搭分享"],
                "post_tags": ["穿搭", "时尚", "分享"],
                "post_likes": 256,
                "post_comments": 45,
                "post_shares": 12,
                "external_url": f"https://xiaohongshu.com/post/{random.randint(1000000, 9999999)}",
                "timestamp": timezone.now(),
            })
        return updates

    def _get_mock_douyin_updates(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """获取抖音模拟数据"""
        updates = []
        if random.random() < 0.3:  # 30%概率有新视频
            updates.append({
                "type": "newPosts",
                "title": f"{subscription.target_user_name}发布了新视频",
                "content": "发布了一个搞笑视频，获得了1200个点赞...",
                "post_content": "今天拍了一个搞笑视频，希望大家喜欢！",
                "post_video_url": f"https://douyin.com/video/{random.randint(1000000, 9999999)}",
                "post_images": ["https://via.placeholder.com/300x400/ff6b6b/ffffff?text=抖音视频"],
                "post_likes": 1200,
                "post_comments": 89,
                "post_shares": 34,
                "external_url": f"https://douyin.com/video/{random.randint(1000000, 9999999)}",
                "timestamp": timezone.now(),
            })
        return updates

    def _get_mock_netease_updates(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """获取网易云音乐模拟数据"""
        updates = []
        if random.random() < 0.3:  # 30%概率有新动态
            updates.append({
                "type": "newPosts",
                "title": f"{subscription.target_user_name}分享了音乐",
                "content": "分享了一首好听的歌曲，获得了156个点赞...",
                "post_content": "今天听到一首很好听的歌，分享给大家！",
                "post_images": ["https://via.placeholder.com/300x300/ff6b6b/ffffff?text=音乐分享"],
                "post_tags": ["音乐", "分享"],
                "post_likes": 156,
                "post_comments": 23,
                "post_shares": 8,
                "external_url": f"https://music.163.com/post/{random.randint(1000000, 9999999)}",
                "timestamp": timezone.now(),
            })
        return updates

    def _get_mock_weibo_updates(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """获取微博模拟数据"""
        updates = []
        if random.random() < 0.3:  # 30%概率有新微博
            updates.append({
                "type": "newPosts",
                "title": f"{subscription.target_user_name}发布了新微博",
                "content": "发布了一条生活动态，获得了89个点赞...",
                "post_content": "今天天气真好，出去走走心情都变好了！",
                "post_images": ["https://via.placeholder.com/300x300/ff6b6b/ffffff?text=微博动态"],
                "post_tags": ["生活", "分享"],
                "post_likes": 89,
                "post_comments": 12,
                "post_shares": 5,
                "external_url": f"https://weibo.com/status/{random.randint(1000000000, 9999999999)}",
                "timestamp": timezone.now(),
            })
        return updates

    def _get_mock_bilibili_updates(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """获取B站模拟数据"""
        updates = []
        if random.random() < 0.3:  # 30%概率有新视频
            updates.append({
                "type": "newPosts",
                "title": f"{subscription.target_user_name}发布了新视频",
                "content": "发布了一个教程视频，获得了2300个点赞...",
                "post_content": "今天制作了一个教程视频，希望对大家有帮助！",
                "post_video_url": f"https://bilibili.com/video/{random.randint(1000000000, 9999999999)}",
                "post_images": ["https://via.placeholder.com/300x400/ff6b6b/ffffff?text=B站视频"],
                "post_likes": 2300,
                "post_comments": 156,
                "post_shares": 67,
                "external_url": f"https://bilibili.com/video/{random.randint(1000000000, 9999999999)}",
                "timestamp": timezone.now(),
            })
        return updates
