"""
代理池服务 - 用于绕过IP封禁
"""
import random
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ProxyPoolService:
    """代理池服务"""
    
    def __init__(self):
        # 代理池配置
        self.proxy_list = [
            # 本地代理
            {'server': 'http://127.0.0.1:7890', 'type': 'local', 'weight': 3},
            {'server': 'http://127.0.0.1:8080', 'type': 'local', 'weight': 2},
            {'server': 'http://127.0.0.1:1080', 'type': 'local', 'weight': 2},
            
            # 无代理
            {'server': None, 'type': 'direct', 'weight': 1},
            
            # 可以添加更多代理
            # {'server': 'http://proxy1.example.com:8080', 'type': 'remote', 'weight': 1},
            # {'server': 'http://proxy2.example.com:8080', 'type': 'remote', 'weight': 1},
        ]
        
        # 代理使用统计
        self.proxy_stats = {}
        for proxy in self.proxy_list:
            key = proxy['server'] or 'direct'
            self.proxy_stats[key] = {
                'success_count': 0,
                'failure_count': 0,
                'last_used': None,
                'blocked': False
            }
    
    def get_random_proxy(self) -> Optional[Dict]:
        """获取随机代理"""
        try:
            # 过滤掉被封禁的代理
            available_proxies = [
                proxy for proxy in self.proxy_list 
                if not self.proxy_stats.get(proxy['server'] or 'direct', {}).get('blocked', False)
            ]
            
            if not available_proxies:
                logger.warning("⚠️ 所有代理都被封禁，使用直连")
                return {'server': None, 'type': 'direct', 'weight': 1}
            
            # 根据权重选择代理
            weighted_proxies = []
            for proxy in available_proxies:
                weight = proxy['weight']
                for _ in range(weight):
                    weighted_proxies.append(proxy)
            
            selected_proxy = random.choice(weighted_proxies)
            proxy_key = selected_proxy['server'] or 'direct'
            
            # 更新使用统计
            self.proxy_stats[proxy_key]['last_used'] = self._get_current_time()
            
            logger.info(f"🌐 选择代理: {proxy_key} (类型: {selected_proxy['type']})")
            return selected_proxy
            
        except Exception as e:
            logger.error(f"获取代理失败: {str(e)}")
            return {'server': None, 'type': 'direct', 'weight': 1}
    
    def mark_proxy_success(self, proxy_server: Optional[str]):
        """标记代理成功"""
        try:
            key = proxy_server or 'direct'
            if key in self.proxy_stats:
                self.proxy_stats[key]['success_count'] += 1
                logger.info(f"✅ 代理 {key} 使用成功")
        except Exception as e:
            logger.error(f"标记代理成功失败: {str(e)}")
    
    def mark_proxy_failure(self, proxy_server: Optional[str], reason: str = "unknown"):
        """标记代理失败"""
        try:
            key = proxy_server or 'direct'
            if key in self.proxy_stats:
                self.proxy_stats[key]['failure_count'] += 1
                logger.warning(f"❌ 代理 {key} 使用失败: {reason}")
                
                # 如果失败次数过多，标记为封禁
                failure_count = self.proxy_stats[key]['failure_count']
                if failure_count >= 3:  # 连续失败3次
                    self.proxy_stats[key]['blocked'] = True
                    logger.warning(f"🚫 代理 {key} 被封禁")
        except Exception as e:
            logger.error(f"标记代理失败失败: {str(e)}")
    
    def get_proxy_stats(self) -> Dict:
        """获取代理统计信息"""
        return self.proxy_stats.copy()
    
    def reset_proxy_stats(self):
        """重置代理统计"""
        for key in self.proxy_stats:
            self.proxy_stats[key] = {
                'success_count': 0,
                'failure_count': 0,
                'last_used': None,
                'blocked': False
            }
        logger.info("🔄 代理统计已重置")
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 全局代理池实例
proxy_pool = ProxyPoolService()
