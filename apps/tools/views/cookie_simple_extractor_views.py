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
def cookie_simple_extractor_page(request):
    """简单Cookie提取器页面"""
    return render(request, 'tools/cookie_simple_extractor.html')

@csrf_exempt
@require_http_methods(["POST"])
def simple_extract_cookies_api(request):
    """简单提取Boss直聘cookies的API - 基于用户提供的cookies格式"""
    try:
        data = json.loads(request.body)
        cookies_text = data.get('cookies_text', '').strip()
        
        if not cookies_text:
            return JsonResponse({
                "success": False,
                "error": "请输入cookies内容",
                "cookies": {}
            })
        
        logger.info("🔄 开始解析用户提供的cookies...")
        
        # 解析cookies文本
        cookies_dict = {}
        boss_cookies = []
        
        # 支持多种格式的cookies输入
        lines = cookies_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 处理制表符分隔的格式（如你提供的格式）
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    value = parts[1].strip()
                    domain = parts[2].strip() if len(parts) > 2 else '.zhipin.com'
                    
                    if name and value and '.zhipin.com' in domain:
                        cookies_dict[name] = value
                        boss_cookies.append({
                            'name': name,
                            'value': value,
                            'domain': domain,
                            'path': '/',
                            'expires': '',
                            'httpOnly': False,
                            'secure': True,
                            'sameSite': 'Lax'
                        })
                        logger.info(f"   {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
            
            # 处理分号分隔的格式
            elif '=' in line:
                equal_index = line.find('=')
                name = line[:equal_index].strip()
                value = line[equal_index + 1:].strip()
                
                if name and value:
                    cookies_dict[name] = value
                    boss_cookies.append({
                        'name': name,
                        'value': value,
                        'domain': '.zhipin.com',
                        'path': '/',
                        'expires': '',
                        'httpOnly': False,
                        'secure': True,
                        'sameSite': 'Lax'
                    })
                    logger.info(f"   {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
        
        if cookies_dict:
            logger.info(f"✅ 成功解析到 {len(cookies_dict)} 个Boss直聘cookies")
            
            # 保存cookies到数据库
            from ..services.cookie_storage_service import get_cookie_storage_service
            cookie_service = get_cookie_storage_service(request.user)
            cookie_service.save_cookies('boss', cookies_dict)
            logger.info(f"✅ 已保存cookies到数据库")
            
            return JsonResponse({
                "success": True,
                "message": f"成功解析到 {len(cookies_dict)} 个Boss直聘cookies",
                "cookies": cookies_dict,
                "cookies_detail": boss_cookies,
                "count": len(cookies_dict)
            })
        else:
            logger.warning("⚠️ 未解析到有效的Boss直聘cookies")
            return JsonResponse({
                "success": False,
                "error": "未解析到有效的Boss直聘cookies，请检查格式",
                "cookies": {}
            })
            
    except Exception as e:
        logger.error(f"❌ 解析cookies失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"解析cookies失败: {str(e)}",
            "cookies": {}
        })

@csrf_exempt
@require_http_methods(["POST"])
def start_job_search_with_simple_cookies_api(request):
    """使用简单提取的cookies开始投递任务"""
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
        
        logger.info(f"🚀 开始使用简单提取的cookies进行投递...")
        
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
            logger.info(f"✅ 使用简单提取的cookies投递成功: {result.get('message', '')}")
            result['login_detected'] = True
            result['login_message'] = '使用简单提取的cookies成功启动投递任务'
            result['session_source'] = 'simple_extracted'
            result['cookie_count'] = len(saved_cookies)
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.error(f"❌ 使用简单提取的cookies投递失败: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": f"投递失败: {str(e)}",
            "applied_count": 0,
            "total_found": 0
        })
