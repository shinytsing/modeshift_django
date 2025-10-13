from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def cookie_test_page(request):
    """Cookie测试页面"""
    return render(request, 'tools/cookie_test_page.html')
