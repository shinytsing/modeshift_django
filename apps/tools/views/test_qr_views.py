"""
测试二维码API
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET"])
def test_qr_api(request):
    """测试二维码API"""
    return HttpResponse("QR API Test OK", content_type='text/plain')
