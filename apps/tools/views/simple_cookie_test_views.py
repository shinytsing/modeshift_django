from django.shortcuts import render

def simple_cookie_test_page(request):
    """简单Cookie测试页面"""
    return render(request, 'tools/simple_cookie_test.html')
