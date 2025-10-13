from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def cookie_auto_extractor_page(request):
    """自动Cookie提取器页面"""
    return render(request, 'tools/cookie_auto_extractor.html')

@csrf_exempt
@require_http_methods(["POST"])
def auto_extract_cookies_api(request):
    """自动提取Boss直聘cookies的API"""
    import asyncio
    from asgiref.sync import sync_to_async
    
    async def _extract_cookies_async():
        try:
            from playwright.async_api import async_playwright
            
            logger.info("🔄 开始自动提取Boss直聘cookies...")
            
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()
                
                # 打开Boss直聘首页
                await page.goto("https://www.zhipin.com")
                logger.info("🌐 已打开Boss直聘首页")
                
                # 等待页面加载
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                # 获取所有cookies
                current_cookies = await context.cookies()
                logger.info(f"🍪 获取到 {len(current_cookies)} 个cookies")
                
                # 转换为字典格式
                cookies_dict = {}
                boss_cookies = []
                
                for cookie in current_cookies:
                    if '.zhipin.com' in cookie.get('domain', ''):
                        cookies_dict[cookie['name']] = cookie['value']
                        boss_cookies.append({
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', ''),
                            'path': cookie.get('path', '/'),
                            'expires': cookie.get('expires', ''),
                            'httpOnly': cookie.get('httpOnly', False),
                            'secure': cookie.get('secure', False),
                            'sameSite': cookie.get('sameSite', 'Lax')
                        })
                        logger.info(f"   {cookie['name']}: {cookie['value'][:50]}{'...' if len(cookie['value']) > 50 else ''}")
                
                await browser.close()
                
                if cookies_dict:
                    logger.info(f"✅ 成功提取到 {len(cookies_dict)} 个Boss直聘cookies")
                    
                    # 保存cookies到数据库
                    from ..services.cookie_storage_service import get_cookie_storage_service
                    cookie_service = get_cookie_storage_service(request.user)
                    await sync_to_async(cookie_service.save_cookies)('boss', cookies_dict)
                    logger.info(f"✅ 已保存cookies到数据库")
                    
                    return {
                        "success": True,
                        "message": f"成功提取到 {len(cookies_dict)} 个Boss直聘cookies",
                        "cookies": cookies_dict,
                        "cookies_detail": boss_cookies,
                        "count": len(cookies_dict)
                    }
                else:
                    logger.warning("⚠️ 未获取到有效的Boss直聘cookies")
                    return {
                        "success": False,
                        "error": "未获取到有效的Boss直聘cookies，请确保已登录",
                        "cookies": {}
                    }
                    
        except Exception as e:
            logger.error(f"❌ 自动提取cookies失败: {str(e)}")
            return {
                "success": False,
                "error": f"自动提取cookies失败: {str(e)}",
                "cookies": {}
            }
    
    # 运行异步函数
    try:
        result = asyncio.run(_extract_cookies_async())
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"❌ 异步执行失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"异步执行失败: {str(e)}",
            "cookies": {}
        })

@csrf_exempt
@require_http_methods(["POST"])
def start_job_search_with_extracted_cookies_api(request):
    """使用提取的cookies开始投递任务"""
    try:
        data = json.loads(request.body)
        
        # 获取投递参数
        keywords = data.get('keywords', ['Python开发'])
        cities = data.get('cities', ['北京'])
        salary_min = data.get('salary_min', 15000)
        salary_max = data.get('salary_max', 25000)
        say_hi = data.get('say_hi', '您好，我对这个职位很感兴趣')
        use_ai = data.get('use_ai', True)
        send_img_resume = data.get('send_img_resume', False)
        
        logger.info(f"🚀 开始使用提取的cookies进行投递...")
        
        # 获取保存的cookies
        from ..services.cookie_storage_service import get_cookie_storage_service
        cookie_service = get_cookie_storage_service(request.user)
        saved_cookies = cookie_service.get_cookies('boss')
        
        if not saved_cookies:
            return JsonResponse({
                "success": False,
                "error": "未找到保存的cookies，请先提取cookies",
                "applied_count": 0,
                "total_found": 0
            })
        
        # 启动投递任务
        from ..services.job_search_service import JobSearchService
        service = JobSearchService()
        
        result = service._start_real_boss_search_with_current_cookies(
            saved_cookies,
            keywords, cities, [salary_min, salary_max], say_hi, use_ai, request.user
        )
        
        if result.get('success'):
            logger.info(f"✅ 使用提取的cookies投递成功: {result.get('message', '')}")
            result['login_detected'] = True
            result['login_message'] = '使用自动提取的cookies成功启动投递任务'
            result['session_source'] = 'auto_extracted'
            result['cookie_count'] = len(saved_cookies)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"❌ 使用提取的cookies投递失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"投递失败: {str(e)}",
            "applied_count": 0,
            "total_found": 0
        })
