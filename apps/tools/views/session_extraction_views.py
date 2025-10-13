"""
Session提取视图
提供手动提取Boss直聘session的API接口
"""

import json
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from ..services.local_session_extractor import LocalSessionExtractor

logger = logging.getLogger(__name__)


def session_extractor_page(request):
    """Session提取器页面"""
    return render(request, "tools/session_extractor.html")


def cookie_extractor_page(request):
    """Cookie提取器页面"""
    return render(request, "tools/cookie_extractor.html")

def cookie_extractor_simple_page(request):
    """简单Cookie提取器页面"""
    return render(request, "tools/cookie_extractor.html")


@csrf_exempt
@require_http_methods(["GET"])
def extract_boss_session_api(request):
    """提取Boss直聘session API"""
    try:
        logger.info("🔍 开始提取Boss直聘session...")
        
        extractor = LocalSessionExtractor()
        result = extractor.get_all_boss_sessions()
        
        if result.get('success'):
            best_result = result['best_result']
            cookies = best_result['cookies']
            
            logger.info(f"✅ 成功提取到{len(cookies)}个cookies")
            
            return JsonResponse({
                "success": True,
                "message": f"成功从{best_result['browser']}浏览器提取到{len(cookies)}个cookies",
                "browser": best_result['browser'],
                "cookie_count": len(cookies),
                "cookies": cookies,
                "all_results": result.get('all_results', {})
            })
        else:
            logger.warning(f"❌ 提取失败: {result.get('error')}")
            return JsonResponse({
                "success": False,
                "error": result.get('error'),
                "suggestion": result.get('suggestion', '请先在浏览器中登录Boss直聘')
            })
            
    except Exception as e:
        logger.error(f"提取session失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"提取失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
def test_boss_session_api(request):
    """测试Boss直聘session有效性API"""
    try:
        data = json.loads(request.body)
        cookies = data.get('cookies', {})
        
        if not cookies:
            return JsonResponse({
                "success": False,
                "error": "未提供cookies"
            })
        
        logger.info(f"🔍 测试{len(cookies)}个cookies的有效性...")
        
        # 使用requests测试cookies
        import requests
        
        session = requests.Session()
        
        # 设置cookies
        for name, value in cookies.items():
            session.cookies.set(name, value, domain='.zhipin.com')
        
        # 测试访问Boss直聘主页
        test_url = "https://www.zhipin.com/web/geek/jobs"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = session.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 检查是否包含登录用户信息
            login_indicators = [
                'user-info', 'user-avatar', 'geek-info', 'geek-name',
                'user-name', 'user-profile', 'login-success'
            ]
            
            is_logged_in = any(indicator in content for indicator in login_indicators)
            
            if is_logged_in:
                logger.info("✅ cookies验证成功，用户已登录")
                return JsonResponse({
                    "success": True,
                    "valid": True,
                    "message": "cookies有效，用户已登录",
                    "status_code": response.status_code,
                    "url": response.url
                })
            else:
                logger.warning("❌ cookies可能已过期，未检测到登录状态")
                return JsonResponse({
                    "success": True,
                    "valid": False,
                    "message": "cookies可能已过期，未检测到登录状态",
                    "status_code": response.status_code,
                    "url": response.url
                })
        else:
            logger.warning(f"❌ 请求失败，状态码: {response.status_code}")
            return JsonResponse({
                "success": True,
                "valid": False,
                "message": f"请求失败，状态码: {response.status_code}",
                "status_code": response.status_code
            })
            
    except Exception as e:
        logger.error(f"测试session失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"测试失败: {str(e)}"
        })


@csrf_exempt
@require_http_methods(["POST"])
def use_extracted_session_api(request):
    """使用提取的session进行投递API"""
    try:
        data = json.loads(request.body)
        cookies = data.get('cookies', {})
        
        if not cookies:
            return JsonResponse({
                "success": False,
                "error": "未提供cookies"
            })
        
        logger.info(f"🚀 使用提取的session进行投递...")
        
        # 调用job_search_service使用提取的cookies
        from ..services.job_search_service import JobSearchService
        
        service = JobSearchService()
        
        # 创建模拟的登录状态检测结果
        mock_login_status = {
            "success": True,
            "is_logged_in": True,
            "found_indicator": "local_session",
            "login_confidence": 95,
            "message": "使用提取的session",
            "token_info": cookies,
            "browser": "extracted",
            "cookie_count": len(cookies)
        }
        
        # 使用提取的cookies进行投递
        result = service._start_real_boss_search_with_extracted_cookies(
            cookies, 
            ["测试工程师"], 
            ["武汉"], 
            [15], 
            "您好！我有三年测试经验，计算机本科\n个人网站shenyiqing.xin，善用大模型工具解决问题\n具备丰富的社交软件测试经验，[青藤之恋]app.\n独立负责过 Web 、移动端、h5，服务端的核心测试工作。有性能，api和ui自动化测试经验，并且因此获得了飞书的效率先锋证书\n对cicd有实践部署经验", 
            True, 
            request.user
        )
        
        return JsonResponse({
            "success": True,
            "message": f"成功使用{len(cookies)}个cookies进行投递",
            "cookies_used": len(cookies),
            "login_status": mock_login_status,
            "delivery_result": result
        })
        
    except Exception as e:
        logger.error(f"使用session投递失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"投递失败: {str(e)}"
        })
