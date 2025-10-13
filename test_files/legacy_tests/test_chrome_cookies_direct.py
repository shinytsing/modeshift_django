#!/usr/bin/env python3
"""
直接测试Chrome cookies
"""
import sqlite3
import os
import tempfile
import shutil

def test_chrome_cookies():
    """测试Chrome cookies"""
    try:
        # Chrome cookie文件路径
        cookie_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies")
        
        if not os.path.exists(cookie_path):
            print(f"Cookie文件不存在: {cookie_path}")
            return
        
        print(f"检查cookie文件: {cookie_path}")
        
        # 复制cookie文件到临时目录
        temp_cookie = tempfile.mktemp()
        shutil.copy2(cookie_path, temp_cookie)
        
        try:
            # 连接SQLite数据库
            conn = sqlite3.connect(temp_cookie)
            cursor = conn.cursor()
            
            # 查询Boss直聘相关的cookies
            cursor.execute("""
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, creation_utc
                FROM cookies 
                WHERE (host_key LIKE '%zhipin.com%' OR host_key LIKE '%boss.com%' OR host_key LIKE '%.zhipin.com%')
                AND name IN ('wt2', 'zp_at', '__zp_stoken__', 'bst', 'wbg', '__a', '__c', '__g')
                ORDER BY creation_utc DESC
            """)
            
            cookies = cursor.fetchall()
            
            print(f"找到 {len(cookies)} 个Boss直聘cookies:")
            for cookie in cookies:
                name, value, domain, path, expires, secure, httponly, created = cookie
                print(f"  {name}: {value[:50]}... (domain: {domain}, expires: {expires})")
            
            conn.close()
            
        except Exception as e:
            print(f"处理cookie文件失败: {str(e)}")
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_cookie)
            except:
                pass
            
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_chrome_cookies()