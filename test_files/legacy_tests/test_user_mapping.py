import logging
from django.core.management.base import BaseCommand
from apps.tools.services.social_media.real_crawler import RealSocialMediaCrawler
from apps.tools.models import SocialMediaSubscription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '测试用户映射和爬虫功能'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='要测试的用户名或小红书号')
        parser.add_argument('--crawl', action='store_true', help='是否执行完整的爬虫测试')

    def handle(self, *args, **options):
        username = options['username']
        should_crawl = options.get('crawl', False)

        crawler = RealSocialMediaCrawler()

        try:
            # 创建订阅对象
            subscription = SocialMediaSubscription(
                user_id=1,
                platform='xiaohongshu',
                target_user_id=username,
                target_user_name=username
            )

            self.stdout.write('=' * 80)
            self.stdout.write(f'🔍 测试用户: {username}')
            self.stdout.write('=' * 80)

            # 测试用户ID解析
            self.stdout.write('\n🆔 用户ID解析测试:')
            resolved_user_id, token = crawler.get_user_id_and_token(subscription)
            
            self.stdout.write(f'  - 原始输入: {username}')
            self.stdout.write(f'  - 解析结果: {resolved_user_id}')
            self.stdout.write(f'  - Token: {token}')

            if resolved_user_id and resolved_user_id != username:
                self.stdout.write(self.style.SUCCESS('✅ 用户ID解析成功'))
                
                if should_crawl:
                    # 执行完整的爬虫测试
                    self.stdout.write('\n🌐 执行完整爬虫测试:')
                    
                    user_url = f'https://www.xiaohongshu.com/user/profile/{resolved_user_id}'
                    self.stdout.write(f'  - 访问URL: {user_url}')
                    
                    try:
                        response = crawler._anti_detection_request(user_url)
                        if response and response.status_code == 200:
                            self.stdout.write(self.style.SUCCESS('✅ 页面访问成功'))
                            
                            # 检查页面标题
                            import re
                            title_match = re.search(r'<title>([^<]+)</title>', response.text)
                            if title_match:
                                title = title_match.group(1).strip()
                                self.stdout.write(f'📄 页面标题: {title}')
                                
                                if username in title or '小红书' in title:
                                    self.stdout.write(self.style.SUCCESS('✅ 成功访问用户页面'))
                                    
                                    # 解析用户信息
                                    from bs4 import BeautifulSoup
                                    soup = BeautifulSoup(response.text, 'html.parser')
                                    user_info = crawler._parse_xiaohongshu_user_info(soup)
                                    
                                    self.stdout.write('\n👤 用户信息:')
                                    self.stdout.write(f'  - 昵称: {user_info.get("nickname", "无")}')
                                    self.stdout.write(f'  - 小红书号: {user_info.get("xiaohongshu_number", "无")}')
                                    self.stdout.write(f'  - IP属地: {user_info.get("ip_location", "无")}')
                                    self.stdout.write(f'  - 简介: {user_info.get("description", "无")}')
                                    self.stdout.write(f'  - 性别: {user_info.get("gender", "无")}')
                                    self.stdout.write(f'  - 关注数: {user_info.get("following", "无")}')
                                    self.stdout.write(f'  - 粉丝数: {user_info.get("followers", "无")}')
                                    self.stdout.write(f'  - 获赞与收藏: {user_info.get("likes", "无")}')
                                    self.stdout.write(f'  - 笔记数: {user_info.get("posts", "无")}')
                                    
                                    # 测试动态内容解析
                                    self.stdout.write('\n📝 动态内容解析:')
                                    posts = crawler._parse_xiaohongshu_posts_enhanced(soup, response.text, subscription)
                                    self.stdout.write(f'  - 找到 {len(posts)} 条动态')
                                    
                                    if len(posts) > 0:
                                        self.stdout.write('  - 最新动态示例:')
                                        for i, post in enumerate(posts[:3], 1):
                                            self.stdout.write(f'    {i}. 标题: {post.get("title", "无标题")}')
                                            self.stdout.write(f'       内容: {post.get("content", "无内容")[:80]}...')
                                            self.stdout.write(f'       点赞: {post.get("likes", "无")}')
                                            self.stdout.write(f'       评论: {post.get("comments", "无")}')
                                            self.stdout.write(f'       发布时间: {post.get("publish_time", "无时间")}')
                                            self.stdout.write()
                                    else:
                                        self.stdout.write('  - 暂无动态内容')
                                else:
                                    self.stdout.write(self.style.WARNING('⚠️ 页面标题不匹配'))
                            else:
                                self.stdout.write(self.style.ERROR('❌ 无法获取页面标题'))
                        else:
                            self.stdout.write(self.style.ERROR(f'❌ 页面访问失败: {response.status_code if response else "无响应"}'))
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ 页面访问异常: {e}'))
                        logger.error(f'页面访问异常: {e}', exc_info=True)
                else:
                    self.stdout.write('\n💡 提示: 使用 --crawl 参数执行完整的爬虫测试')
            else:
                self.stdout.write(self.style.ERROR('❌ 用户ID解析失败'))
                self.stdout.write('💡 可能原因:')
                self.stdout.write('  - 用户不存在')
                self.stdout.write('  - 需要手动添加用户映射')
                self.stdout.write('  - 搜索功能失效')

            # 显示映射信息
            mapping_info = crawler.get_user_mapping_info(username)
            self.stdout.write('\n📋 映射信息:')
            self.stdout.write(f'  - 用户名: {mapping_info.get("username", "无")}')
            self.stdout.write(f'  - 用户ID: {mapping_info.get("user_id", "无")}')
            self.stdout.write(f'  - Token: {mapping_info.get("token", "无")}')
            self.stdout.write(f'  - 映射来源: {mapping_info.get("source", "无")}')

        except Exception as e:
            logger.error(f'测试用户映射失败: {e}')
            self.stdout.write(self.style.ERROR(f'❌ 测试失败: {e}'))

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('🏁 测试完成')
        self.stdout.write('=' * 80)
