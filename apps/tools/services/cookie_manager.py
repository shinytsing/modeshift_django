"""
Cookie管理服务 - 基于最佳实践的Cookie持久化存储和管理
"""
import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class CookieManager:
    """Cookie管理器 - 实现Cookie的持久化存储和自动管理"""
    
    def __init__(self, cookie_dir: str = "cookies"):
        """
        初始化Cookie管理器
        
        Args:
            cookie_dir: Cookie文件存储目录
        """
        self.cookie_dir = Path(cookie_dir)
        self.cookie_dir.mkdir(exist_ok=True)
        
        # Boss直聘Cookie文件路径
        self.boss_cookie_file = self.cookie_dir / "boss_zhipin_cookies.json"
        
        logger.info(f"🍪 Cookie管理器初始化完成，存储目录: {self.cookie_dir}")
    
    def save_cookies(self, cookies: List[Dict], platform: str = "boss") -> bool:
        """
        保存Cookie到文件
        
        Args:
            cookies: Cookie列表，每个Cookie包含name, value, domain, path等字段
            platform: 平台名称 (boss, 51job, lagou等)
            
        Returns:
            bool: 保存是否成功
        """
        try:
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            
            # 处理Cookie数据，确保格式正确
            processed_cookies = []
            for cookie in cookies:
                processed_cookie = {
                    "name": cookie.get("name", ""),
                    "value": cookie.get("value", ""),
                    "domain": cookie.get("domain", ""),
                    "path": cookie.get("path", "/"),
                    "secure": cookie.get("secure", False),
                    "httpOnly": cookie.get("httpOnly", False),
                    "expires": cookie.get("expires"),
                    "saved_at": datetime.now().isoformat(),
                    "expires_at": self._calculate_expires_at(cookie.get("expires"))
                }
                processed_cookies.append(processed_cookie)
            
            # 保存到文件
            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(processed_cookies, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Cookie已保存到文件: {cookie_file} (共{len(processed_cookies)}个)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存Cookie失败: {str(e)}")
            return False
    
    def load_cookies(self, platform: str = "boss") -> List[Dict]:
        """
        从文件加载Cookie
        
        Args:
            platform: 平台名称
            
        Returns:
            List[Dict]: Cookie列表
        """
        try:
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            
            if not cookie_file.exists():
                logger.info(f"📁 Cookie文件不存在: {cookie_file}")
                return []
            
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            logger.info(f"✅ 从文件加载Cookie: {cookie_file} (共{len(cookies)}个)")
            return cookies
            
        except Exception as e:
            logger.error(f"❌ 加载Cookie失败: {str(e)}")
            return []
    
    def is_cookie_valid(self, platform: str = "boss") -> bool:
        """
        检查Cookie文件是否存在且有效
        
        Args:
            platform: 平台名称
            
        Returns:
            bool: Cookie是否有效
        """
        try:
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            
            if not cookie_file.exists():
                logger.info(f"📁 Cookie文件不存在: {cookie_file}")
                return False
            
            # 检查文件是否为空
            if cookie_file.stat().st_size == 0:
                logger.warning(f"⚠️ Cookie文件为空: {cookie_file}")
                return False
            
            # 检查Cookie是否过期
            cookies = self.load_cookies(platform)
            if not cookies:
                return False
            
            # 检查是否有有效的Cookie
            valid_cookies = [c for c in cookies if self._is_cookie_not_expired(c)]
            if not valid_cookies:
                logger.warning(f"⚠️ 所有Cookie已过期: {cookie_file}")
                return False
            
            logger.info(f"✅ Cookie文件有效: {cookie_file} (有效Cookie: {len(valid_cookies)}个)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 检查Cookie有效性失败: {str(e)}")
            return False
    
    def convert_playwright_cookies(self, playwright_cookies: List[Any]) -> List[Dict]:
        """
        将Playwright Cookie对象转换为标准格式
        
        Args:
            playwright_cookies: Playwright Cookie对象列表
            
        Returns:
            List[Dict]: 标准格式的Cookie列表
        """
        cookies = []
        for cookie in playwright_cookies:
            cookie_dict = {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "secure": cookie.secure,
                "httpOnly": cookie.httpOnly,
                "expires": cookie.expires
            }
            cookies.append(cookie_dict)
        
        return cookies
    
    def convert_to_playwright_cookies(self, cookies: List[Dict]) -> List[Dict]:
        """
        将标准格式Cookie转换为Playwright格式
        
        Args:
            cookies: 标准格式的Cookie列表
            
        Returns:
            List[Dict]: Playwright格式的Cookie列表
        """
        playwright_cookies = []
        for cookie in cookies:
            playwright_cookie = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie["path"],
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False)
            }
            
            # 处理过期时间
            if cookie.get("expires"):
                playwright_cookie["expires"] = cookie["expires"]
            
            playwright_cookies.append(playwright_cookie)
        
        return playwright_cookies
    
    def _calculate_expires_at(self, expires: Optional[float]) -> Optional[str]:
        """
        计算Cookie过期时间
        
        Args:
            expires: 过期时间戳
            
        Returns:
            Optional[str]: ISO格式的过期时间
        """
        if expires:
            try:
                # 如果是时间戳，转换为datetime
                if isinstance(expires, (int, float)):
                    expires_dt = datetime.fromtimestamp(expires)
                else:
                    expires_dt = datetime.fromisoformat(str(expires))
                
                return expires_dt.isoformat()
            except Exception:
                # 如果转换失败，设置为7天后
                return (datetime.now() + timedelta(days=7)).isoformat()
        
        # 如果没有过期时间，设置为7天后
        return (datetime.now() + timedelta(days=7)).isoformat()
    
    def _is_cookie_not_expired(self, cookie: Dict) -> bool:
        """
        检查Cookie是否未过期
        
        Args:
            cookie: Cookie字典
            
        Returns:
            bool: Cookie是否未过期
        """
        try:
            expires_at = cookie.get("expires_at")
            if not expires_at:
                return True  # 没有过期时间，认为有效
            
            expires_dt = datetime.fromisoformat(expires_at)
            return datetime.now() < expires_dt
            
        except Exception:
            return True  # 解析失败，认为有效
    
    def clear_cookies(self, platform: str = "boss") -> bool:
        """
        清除指定平台的Cookie文件
        
        Args:
            platform: 平台名称
            
        Returns:
            bool: 清除是否成功
        """
        try:
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            
            if cookie_file.exists():
                cookie_file.unlink()
                logger.info(f"🗑️ Cookie文件已删除: {cookie_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 清除Cookie失败: {str(e)}")
            return False
    
    def get_cookie_info(self, platform: str = "boss") -> Dict[str, Any]:
        """
        获取Cookie文件信息
        
        Args:
            platform: 平台名称
            
        Returns:
            Dict[str, Any]: Cookie文件信息
        """
        try:
            cookie_file = self.cookie_dir / f"{platform}_cookies.json"
            
            info = {
                "file_exists": cookie_file.exists(),
                "file_path": str(cookie_file),
                "file_size": 0,
                "cookie_count": 0,
                "valid_cookie_count": 0,
                "last_modified": None,
                "is_valid": False
            }
            
            if cookie_file.exists():
                info["file_size"] = cookie_file.stat().st_size
                info["last_modified"] = datetime.fromtimestamp(
                    cookie_file.stat().st_mtime
                ).isoformat()
                
                cookies = self.load_cookies(platform)
                info["cookie_count"] = len(cookies)
                info["valid_cookie_count"] = len([
                    c for c in cookies if self._is_cookie_not_expired(c)
                ])
                info["is_valid"] = self.is_cookie_valid(platform)
            
            return info
            
        except Exception as e:
            logger.error(f"❌ 获取Cookie信息失败: {str(e)}")
            return {"error": str(e)}


# 全局Cookie管理器实例
cookie_manager = CookieManager()