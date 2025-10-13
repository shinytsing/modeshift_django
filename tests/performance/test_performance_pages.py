"""
Django网站性能测试 - 页面性能测试
项目：shenyiqing.xin
功能：测试各个页面的性能指标
"""

import pytest
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.performance
class TestPagePerformance:
    """页面性能测试类"""
    
    def test_homepage_load_time(self, selenium_driver):
        """测试首页加载时间"""
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/')
        
        # 等待页面完全加载
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert load_time < 3.0, f"首页加载时间过长: {load_time:.2f}秒"
        print(f"首页加载时间: {load_time:.2f}秒")
    
    def test_login_page_load_time(self, selenium_driver):
        """测试登录页面加载时间"""
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/login/')
        
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert load_time < 2.0, f"登录页面加载时间过长: {load_time:.2f}秒"
        print(f"登录页面加载时间: {load_time:.2f}秒")
    
    def test_register_page_load_time(self, selenium_driver):
        """测试注册页面加载时间"""
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/register/')
        
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert load_time < 2.0, f"注册页面加载时间过长: {load_time:.2f}秒"
        print(f"注册页面加载时间: {load_time:.2f}秒")
    
    def test_admin_page_load_time(self, selenium_driver):
        """测试管理员页面加载时间"""
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/admin/')
        
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert load_time < 3.0, f"管理员页面加载时间过长: {load_time:.2f}秒"
        print(f"管理员页面加载时间: {load_time:.2f}秒")
    
    def test_api_response_time(self):
        """测试API响应时间"""
        start_time = time.time()
        response = requests.get('http://localhost:8000/api/auth/status/')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response_time < 1.0, f"API响应时间过长: {response_time:.2f}秒"
        print(f"API响应时间: {response_time:.2f}秒")
    
    def test_form_submission_time(self, selenium_driver):
        """测试表单提交时间"""
        selenium_driver.get('http://localhost:8000/contact/')
        
        # 填写表单
        name_field = selenium_driver.find_element(By.NAME, "name")
        email_field = selenium_driver.find_element(By.NAME, "email")
        message_field = selenium_driver.find_element(By.NAME, "message")
        
        name_field.send_keys("Performance Test User")
        email_field.send_keys("perf@example.com")
        message_field.send_keys("This is a performance test message")
        
        # 提交表单并测量时间
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        
        start_time = time.time()
        submit_button.click()
        
        # 等待响应
        WebDriverWait(selenium_driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located((By.CLASS_NAME, "success")),
                EC.presence_of_element_located((By.CLASS_NAME, "error")),
                EC.url_contains("success")
            )
        )
        
        end_time = time.time()
        submission_time = end_time - start_time
        
        assert submission_time < 2.0, f"表单提交时间过长: {submission_time:.2f}秒"
        print(f"表单提交时间: {submission_time:.2f}秒")
    
    def test_database_query_performance(self, authenticated_client):
        """测试数据库查询性能"""
        start_time = time.time()
        response = authenticated_client.get('/api/users/')
        end_time = time.time()
        
        query_time = end_time - start_time
        
        assert query_time < 1.0, f"数据库查询时间过长: {query_time:.2f}秒"
        print(f"数据库查询时间: {query_time:.2f}秒")
    
    def test_static_file_loading_time(self, selenium_driver):
        """测试静态文件加载时间"""
        selenium_driver.get('http://localhost:8000/')
        
        # 测量CSS文件加载时间
        start_time = time.time()
        selenium_driver.execute_script("""
            var link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/main.css';
            document.head.appendChild(link);
        """)
        
        # 等待CSS加载完成
        WebDriverWait(selenium_driver, 5).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        end_time = time.time()
        css_load_time = end_time - start_time
        
        assert css_load_time < 1.0, f"CSS文件加载时间过长: {css_load_time:.2f}秒"
        print(f"CSS文件加载时间: {css_load_time:.2f}秒")
    
    def test_javascript_execution_time(self, selenium_driver):
        """测试JavaScript执行时间"""
        selenium_driver.get('http://localhost:8000/')
        
        # 测量JavaScript执行时间
        start_time = time.time()
        selenium_driver.execute_script("""
            // 模拟一些JavaScript操作
            var elements = document.querySelectorAll('*');
            var count = elements.length;
            console.log('Element count:', count);
        """)
        end_time = time.time()
        
        js_execution_time = end_time - start_time
        
        assert js_execution_time < 0.5, f"JavaScript执行时间过长: {js_execution_time:.2f}秒"
        print(f"JavaScript执行时间: {js_execution_time:.2f}秒")
    
    def test_image_loading_time(self, selenium_driver):
        """测试图片加载时间"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找页面中的图片
        images = selenium_driver.find_elements(By.TAG_NAME, "img")
        
        if images:
            start_time = time.time()
            
            # 等待所有图片加载完成
            for img in images:
                WebDriverWait(selenium_driver, 5).until(
                    lambda driver, img=img: driver.execute_script(
                        "return arguments[0].complete", img
                    )
                )
            
            end_time = time.time()
            image_load_time = end_time - start_time
            
            assert image_load_time < 2.0, f"图片加载时间过长: {image_load_time:.2f}秒"
            print(f"图片加载时间: {image_load_time:.2f}秒")
        else:
            print("页面中没有图片")
    
    def test_concurrent_user_simulation(self):
        """测试并发用户模拟"""
        import threading
        import time
        
        def simulate_user():
            """模拟单个用户"""
            start_time = time.time()
            response = requests.get('http://localhost:8000/')
            end_time = time.time()
            return end_time - start_time, response.status_code
        
        # 创建多个线程模拟并发用户
        threads = []
        results = []
        
        def thread_worker():
            load_time, status_code = simulate_user()
            results.append((load_time, status_code))
        
        # 启动10个并发用户
        for i in range(10):
            thread = threading.Thread(target=thread_worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 分析结果
        assert len(results) == 10, "并发用户数量不正确"
        
        avg_load_time = sum(result[0] for result in results) / len(results)
        success_count = sum(1 for result in results if result[1] == 200)
        
        assert avg_load_time < 3.0, f"并发用户平均加载时间过长: {avg_load_time:.2f}秒"
        assert success_count >= 8, f"并发用户成功率过低: {success_count}/10"
        
        print(f"并发用户平均加载时间: {avg_load_time:.2f}秒")
        print(f"并发用户成功率: {success_count}/10")
    
    def test_memory_usage(self, selenium_driver):
        """测试内存使用情况"""
        selenium_driver.get('http://localhost:8000/')
        
        # 获取页面内存使用情况
        memory_info = selenium_driver.execute_script("""
            if (performance.memory) {
                return {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                };
            }
            return null;
        """)
        
        if memory_info:
            used_mb = memory_info['used'] / (1024 * 1024)
            total_mb = memory_info['total'] / (1024 * 1024)
            
            assert used_mb < 50, f"内存使用过多: {used_mb:.2f}MB"
            print(f"内存使用: {used_mb:.2f}MB / {total_mb:.2f}MB")
        else:
            print("无法获取内存信息")
    
    def test_network_requests_count(self, selenium_driver):
        """测试网络请求数量"""
        selenium_driver.get('http://localhost:8000/')
        
        # 获取网络请求统计
        network_info = selenium_driver.execute_script("""
            if (performance.getEntriesByType) {
                var entries = performance.getEntriesByType('resource');
                return {
                    count: entries.length,
                    total_size: entries.reduce((sum, entry) => sum + (entry.transferSize || 0), 0)
                };
            }
            return null;
        """)
        
        if network_info:
            assert network_info['count'] < 50, f"网络请求数量过多: {network_info['count']}"
            print(f"网络请求数量: {network_info['count']}")
            print(f"总传输大小: {network_info['total_size']} bytes")
        else:
            print("无法获取网络请求信息")
    
    def test_page_size_optimization(self, selenium_driver):
        """测试页面大小优化"""
        selenium_driver.get('http://localhost:8000/')
        
        # 获取页面大小
        page_size = len(selenium_driver.page_source)
        
        assert page_size < 500000, f"页面大小过大: {page_size} bytes"
        print(f"页面大小: {page_size} bytes")
    
    def test_caching_effectiveness(self, selenium_driver):
        """测试缓存效果"""
        # 第一次访问
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/')
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        first_load_time = time.time() - start_time
        
        # 第二次访问（应该使用缓存）
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/')
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        second_load_time = time.time() - start_time
        
        # 第二次访问应该更快
        assert second_load_time < first_load_time, "缓存效果不明显"
        print(f"首次加载时间: {first_load_time:.2f}秒")
        print(f"缓存加载时间: {second_load_time:.2f}秒")
        print(f"缓存提升: {((first_load_time - second_load_time) / first_load_time * 100):.1f}%")
    
    def test_mobile_performance(self, selenium_driver):
        """测试移动端性能"""
        # 设置移动端用户代理
        selenium_driver.execute_cdp_cmd('Emulation.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        })
        
        # 设置移动端视口
        selenium_driver.set_window_size(375, 667)
        
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/')
        
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        end_time = time.time()
        mobile_load_time = end_time - start_time
        
        assert mobile_load_time < 4.0, f"移动端加载时间过长: {mobile_load_time:.2f}秒"
        print(f"移动端加载时间: {mobile_load_time:.2f}秒")
    
    def test_error_page_performance(self, selenium_driver):
        """测试错误页面性能"""
        start_time = time.time()
        selenium_driver.get('http://localhost:8000/nonexistent-page/')
        
        # 等待错误页面加载
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        end_time = time.time()
        error_page_load_time = end_time - start_time
        
        assert error_page_load_time < 2.0, f"错误页面加载时间过长: {error_page_load_time:.2f}秒"
        print(f"错误页面加载时间: {error_page_load_time:.2f}秒")
    
    def test_large_data_handling(self, authenticated_client):
        """测试大数据处理性能"""
        # 测试大量数据查询
        start_time = time.time()
        response = authenticated_client.get('/api/users/?page_size=100')
        end_time = time.time()
        
        large_data_time = end_time - start_time
        
        assert large_data_time < 2.0, f"大数据处理时间过长: {large_data_time:.2f}秒"
        print(f"大数据处理时间: {large_data_time:.2f}秒")
    
    def test_search_performance(self, selenium_driver):
        """测试搜索性能"""
        selenium_driver.get('http://localhost:8000/')
        
        # 查找搜索框
        search_input = selenium_driver.find_element(By.CSS_SELECTOR, "input[type='search'], input[name='q']")
        
        start_time = time.time()
        search_input.send_keys("performance test")
        search_input.submit()
        
        # 等待搜索结果
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
        )
        
        end_time = time.time()
        search_time = end_time - start_time
        
        assert search_time < 3.0, f"搜索时间过长: {search_time:.2f}秒"
        print(f"搜索时间: {search_time:.2f}秒")
    
    def test_form_validation_performance(self, selenium_driver):
        """测试表单验证性能"""
        selenium_driver.get('http://localhost:8000/register/')
        
        # 填写表单
        username_field = selenium_driver.find_element(By.NAME, "username")
        email_field = selenium_driver.find_element(By.NAME, "email")
        password_field = selenium_driver.find_element(By.NAME, "password1")
        
        start_time = time.time()
        
        # 快速输入数据
        username_field.send_keys("testuser")
        email_field.send_keys("test@example.com")
        password_field.send_keys("testpass123")
        
        # 提交表单
        submit_button = selenium_driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_button.click()
        
        # 等待验证结果
        WebDriverWait(selenium_driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located((By.CLASS_NAME, "success")),
                EC.presence_of_element_located((By.CLASS_NAME, "error")),
                EC.url_contains("success")
            )
        )
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        assert validation_time < 2.0, f"表单验证时间过长: {validation_time:.2f}秒"
        print(f"表单验证时间: {validation_time:.2f}秒")
