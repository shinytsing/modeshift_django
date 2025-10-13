"""
本地浏览器Session提取服务
自动从本地浏览器中提取Boss直聘的登录session和cookies
"""

import json
import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class LocalSessionExtractor:
    """本地浏览器Session提取器"""
    
    def __init__(self):
        self.browser_paths = {
            'chrome': self._get_chrome_path(),
            'edge': self._get_edge_path(),
            'firefox': self._get_firefox_path(),
        }
        
    def _get_chrome_path(self) -> Optional[Path]:
        """获取Chrome浏览器路径"""
        possible_paths = [
            Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies",
            Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cookies",
            Path.home() / ".config/google-chrome/Default/Cookies",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def _get_edge_path(self) -> Optional[Path]:
        """获取Edge浏览器路径"""
        possible_paths = [
            Path.home() / "Library/Application Support/Microsoft Edge/Default/Cookies",
            Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cookies",
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return None
    
    def _get_firefox_path(self) -> Optional[Path]:
        """获取Firefox浏览器路径"""
        firefox_profiles = Path.home() / "Library/Application Support/Firefox/Profiles"
        if firefox_profiles.exists():
            for profile_dir in firefox_profiles.iterdir():
                if profile_dir.is_dir():
                    cookies_path = profile_dir / "cookies.sqlite"
                    if cookies_path.exists():
                        return cookies_path
        return None
    
    def extract_boss_cookies(self, browser: str = 'chrome') -> Dict[str, Any]:
        """从指定浏览器提取Boss直聘的cookies"""
        try:
            browser_path = self.browser_paths.get(browser)
            if not browser_path or not browser_path.exists():
                logger.warning(f"未找到{browser}浏览器的cookies文件")
                return {"success": False, "error": f"未找到{browser}浏览器"}
            
            logger.info(f"从{browser}浏览器提取Boss直聘cookies: {browser_path}")
            
            # Boss直聘相关的cookie名称
            boss_cookies = [
                '__zp_stoken__', '__a', '__c', '__g', 'wt2', 'zp_at',
                'bst', 'wbg', 'zp_token', 'zp_session'
            ]
            
            cookies = {}
            
            if browser == 'firefox':
                cookies = self._extract_firefox_cookies(browser_path, boss_cookies)
            else:
                cookies = self._extract_chrome_cookies(browser_path, boss_cookies)
            
            if cookies:
                logger.info(f"✅ 成功提取到{len(cookies)}个Boss直聘cookies")
                return {
                    "success": True,
                    "cookies": cookies,
                    "browser": browser,
                    "count": len(cookies)
                }
            else:
                logger.warning("未找到Boss直聘相关的cookies")
                return {
                    "success": False,
                    "error": "未找到Boss直聘相关的cookies",
                    "suggestion": "请先在浏览器中登录Boss直聘"
                }
                
        except Exception as e:
            logger.error(f"提取cookies失败: {str(e)}")
            return {"success": False, "error": f"提取失败: {str(e)}"}
    
    def _extract_chrome_cookies(self, cookies_path: Path, target_cookies: List[str]) -> Dict[str, str]:
        """从Chrome/Edge浏览器提取cookies"""
        try:
            # 复制cookies文件到临时位置，避免数据库锁定
            import tempfile
            import shutil
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                temp_path = temp_file.name
            
            shutil.copy2(cookies_path, temp_path)
            
            cookies = {}
            
            # 连接SQLite数据库
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            # 查询Boss直聘相关的cookies
            placeholders = ','.join(['?' for _ in target_cookies])
            query = f"""
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly
                FROM cookies 
                WHERE host_key LIKE '%zhipin.com%' 
                AND name IN ({placeholders})
            """
            
            cursor.execute(query, target_cookies)
            results = cursor.fetchall()
            
            for row in results:
                name, value, host_key, path, expires_utc, is_secure, is_httponly = row
                
                # 检查cookie是否过期
                if expires_utc and expires_utc > 0:
                    expire_time = (expires_utc - 11644473600000000) / 1000000  # 转换为Unix时间戳
                    if expire_time < time.time():
                        logger.debug(f"Cookie {name} 已过期")
                        continue
                
                cookies[name] = value
                logger.info(f"✅ 找到cookie: {name} = {value[:20]}...")
            
            conn.close()
            os.unlink(temp_path)  # 删除临时文件
            
            return cookies
            
        except Exception as e:
            logger.error(f"提取Chrome cookies失败: {str(e)}")
            return {}
    
    def _extract_firefox_cookies(self, cookies_path: Path, target_cookies: List[str]) -> Dict[str, str]:
        """从Firefox浏览器提取cookies"""
        try:
            import tempfile
            import shutil
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
                temp_path = temp_file.name
            
            shutil.copy2(cookies_path, temp_path)
            
            cookies = {}
            
            # 连接SQLite数据库
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            # 查询Boss直聘相关的cookies
            placeholders = ','.join(['?' for _ in target_cookies])
            query = f"""
                SELECT name, value, host, path, expiry, isSecure, isHttpOnly
                FROM moz_cookies 
                WHERE host LIKE '%zhipin.com%' 
                AND name IN ({placeholders})
            """
            
            cursor.execute(query, target_cookies)
            results = cursor.fetchall()
            
            for row in results:
                name, value, host, path, expiry, is_secure, is_httponly = row
                
                # 检查cookie是否过期
                if expiry and expiry > 0:
                    if expiry < time.time():
                        logger.debug(f"Cookie {name} 已过期")
                        continue
                
                cookies[name] = value
                logger.info(f"✅ 找到cookie: {name} = {value[:20]}...")
            
            conn.close()
            os.unlink(temp_path)  # 删除临时文件
            
            return cookies
            
        except Exception as e:
            logger.error(f"提取Firefox cookies失败: {str(e)}")
            return {}
    
    def extract_local_storage(self, browser: str = 'chrome') -> Dict[str, Any]:
        """从本地浏览器提取localStorage数据"""
        try:
            browser_path = self.browser_paths.get(browser)
            if not browser_path or not browser_path.exists():
                return {"success": False, "error": f"未找到{browser}浏览器"}
            
            # 获取localStorage文件路径
            if browser == 'firefox':
                return {"success": False, "error": "Firefox localStorage提取暂未实现"}
            
            # Chrome/Edge的localStorage路径
            browser_dir = browser_path.parent
            local_storage_path = browser_dir / "Local Storage/leveldb"
            
            if not local_storage_path.exists():
                logger.warning(f"未找到localStorage目录: {local_storage_path}")
                return {"success": False, "error": "未找到localStorage数据"}
            
            # 这里可以添加localStorage提取逻辑
            # 由于localStorage是LevelDB格式，提取比较复杂
            logger.info("localStorage提取功能开发中...")
            return {"success": False, "error": "localStorage提取功能开发中"}
            
        except Exception as e:
            logger.error(f"提取localStorage失败: {str(e)}")
            return {"success": False, "error": f"提取失败: {str(e)}"}
    
    def get_all_boss_sessions(self) -> Dict[str, Any]:
        """获取所有浏览器中的Boss直聘session"""
        results = {}
        
        for browser_name in self.browser_paths.keys():
            if self.browser_paths[browser_name]:
                logger.info(f"检查{browser_name}浏览器...")
                result = self.extract_boss_cookies(browser_name)
                if result.get('success'):
                    results[browser_name] = result
        
        if results:
            # 选择最佳结果（通常选择cookie最多的）
            best_browser = max(results.keys(), key=lambda k: results[k].get('count', 0))
            logger.info(f"✅ 最佳浏览器: {best_browser}, cookies数量: {results[best_browser].get('count', 0)}")
            
            return {
                "success": True,
                "best_browser": best_browser,
                "best_result": results[best_browser],
                "all_results": results
            }
        else:
            return {
                "success": False,
                "error": "未在任何浏览器中找到Boss直聘登录信息",
                "suggestion": "请先在浏览器中登录Boss直聘"
            }
    
    def format_cookies_for_requests(self, cookies: Dict[str, str]) -> Dict[str, str]:
        """将cookies格式化为requests库可用的格式"""
        return cookies
    
    def format_cookies_for_playwright(self, cookies: Dict[str, str]) -> List[Dict[str, Any]]:
        """将cookies格式化为Playwright可用的格式"""
        playwright_cookies = []
        
        for name, value in cookies.items():
            playwright_cookies.append({
                'name': name,
                'value': value,
                'domain': '.zhipin.com',
                'path': '/',
                'httpOnly': True,
                'secure': True
            })
        
        return playwright_cookies


# 使用示例
if __name__ == "__main__":
    extractor = LocalSessionExtractor()
    
    # 获取所有浏览器的Boss直聘session
    result = extractor.get_all_boss_sessions()
    
    if result.get('success'):
        best_result = result['best_result']
        cookies = best_result['cookies']
        
        print(f"找到{len(cookies)}个cookies:")
        for name, value in cookies.items():
            print(f"  {name}: {value[:30]}...")
        
        # 格式化为requests格式
        requests_cookies = extractor.format_cookies_for_requests(cookies)
        print(f"\nRequests格式: {requests_cookies}")
        
        # 格式化为Playwright格式
        playwright_cookies = extractor.format_cookies_for_playwright(cookies)
        print(f"\nPlaywright格式: {playwright_cookies}")
    else:
        print(f"提取失败: {result.get('error')}")
