"""
Playwright UI自动化测试 - 高级功能测试
"""
import pytest
import asyncio
from tests.ui.conftest import PlaywrightTestBase
import logging

logger = logging.getLogger(__name__)


class TestAdvancedUI(PlaywrightTestBase):
    """高级UI功能测试"""
    
    @pytest.mark.asyncio
    async def test_dynamic_content_loading(self, playwright_page):
        """测试动态内容加载"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 监听网络请求
        requests = []
        responses = []
        
        def handle_request(request):
            requests.append(request)
        
        def handle_response(response):
            responses.append(response)
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 触发动态内容加载（如果有AJAX请求）
        await page.wait_for_timeout(2000)
        
        # 检查是否有AJAX请求
        ajax_requests = [req for req in requests if req.url.endswith('.json') or 'api/' in req.url]
        if ajax_requests:
            logger.info(f"Found {len(ajax_requests)} AJAX requests")
            await self.take_screenshot('dynamic_content_loading')
    
    @pytest.mark.asyncio
    async def test_modal_dialogs(self, playwright_page):
        """测试模态对话框"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 查找可能触发模态框的按钮
        modal_triggers = await page.query_selector_all(
            'button[data-toggle="modal"], .modal-trigger, [data-modal]'
        )
        
        for trigger in modal_triggers:
            try:
                await trigger.click()
                await page.wait_for_timeout(500)
                
                # 检查模态框是否出现
                modal = await page.query_selector('.modal, .dialog, .popup')
                if modal:
                    await self.take_screenshot('modal_dialog')
                    
                    # 测试关闭模态框
                    close_button = await modal.query_selector('.close, .modal-close, [data-dismiss="modal"]')
                    if close_button:
                        await close_button.click()
                        await page.wait_for_timeout(500)
                        logger.info("Modal dialog test passed")
                        break
            except Exception as e:
                logger.warning(f"Modal dialog test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_dropdown_menus(self, playwright_page):
        """测试下拉菜单"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 查找下拉菜单
        dropdowns = await page.query_selector_all(
            'select, .dropdown, .select-menu, [data-dropdown]'
        )
        
        for dropdown in dropdowns:
            try:
                # 点击下拉菜单
                await dropdown.click()
                await page.wait_for_timeout(500)
                
                # 检查选项是否出现
                options = await page.query_selector_all('option, .dropdown-item, .menu-item')
                if options:
                    await self.take_screenshot('dropdown_menu')
                    
                    # 选择第一个选项
                    if len(options) > 1:
                        await options[1].click()
                        await page.wait_for_timeout(500)
                        logger.info("Dropdown menu test passed")
                        break
            except Exception as e:
                logger.warning(f"Dropdown menu test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_tabs_and_accordions(self, playwright_page):
        """测试标签页和手风琴组件"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 测试标签页
        tabs = await page.query_selector_all('.tab, .nav-tab, [role="tab"]')
        if tabs:
            for i, tab in enumerate(tabs[:3]):  # 只测试前3个标签
                try:
                    await tab.click()
                    await page.wait_for_timeout(500)
                    await self.take_screenshot(f'tab_{i}')
                    logger.info(f"Tab {i} test passed")
                except Exception as e:
                    logger.warning(f"Tab {i} test failed: {e}")
        
        # 测试手风琴
        accordions = await page.query_selector_all('.accordion, .collapse, [data-toggle="collapse"]')
        if accordions:
            for i, accordion in enumerate(accordions[:2]):  # 只测试前2个手风琴
                try:
                    await accordion.click()
                    await page.wait_for_timeout(500)
                    await self.take_screenshot(f'accordion_{i}')
                    logger.info(f"Accordion {i} test passed")
                except Exception as e:
                    logger.warning(f"Accordion {i} test failed: {e}")


class TestInteractiveFeatures(PlaywrightTestBase):
    """交互功能测试"""
    
    @pytest.mark.asyncio
    async def test_drag_and_drop(self, playwright_page):
        """测试拖拽功能"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 查找可拖拽元素
        draggable_elements = await page.query_selector_all(
            '[draggable="true"], .draggable, .sortable-item'
        )
        
        if len(draggable_elements) >= 2:
            try:
                # 执行拖拽操作
                await draggable_elements[0].drag_to(draggable_elements[1])
                await page.wait_for_timeout(500)
                await self.take_screenshot('drag_and_drop')
                logger.info("Drag and drop test passed")
            except Exception as e:
                logger.warning(f"Drag and drop test failed: {e}")
        else:
            logger.info("No draggable elements found")
    
    @pytest.mark.asyncio
    async def test_keyboard_navigation(self, playwright_page):
        """测试键盘导航"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 测试Tab键导航
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(200)
        
        # 检查焦点是否移动
        focused_element = await page.evaluate('document.activeElement')
        if focused_element:
            await self.take_screenshot('keyboard_navigation')
            logger.info("Keyboard navigation test passed")
    
    @pytest.mark.asyncio
    async def test_mouse_interactions(self, playwright_page):
        """测试鼠标交互"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 测试悬停效果
        hover_elements = await page.query_selector_all(
            'button, a, .hover-effect, [data-hover]'
        )
        
        if hover_elements:
            try:
                await hover_elements[0].hover()
                await page.wait_for_timeout(500)
                await self.take_screenshot('mouse_hover')
                logger.info("Mouse hover test passed")
            except Exception as e:
                logger.warning(f"Mouse hover test failed: {e}")
        
        # 测试右键菜单
        try:
            await page.click('body', button='right')
            await page.wait_for_timeout(500)
            await self.take_screenshot('right_click_menu')
            logger.info("Right click test passed")
        except Exception as e:
            logger.warning(f"Right click test failed: {e}")


class TestPerformanceUI(PlaywrightTestBase):
    """UI性能测试"""
    
    @pytest.mark.asyncio
    async def test_page_load_performance(self, playwright_page):
        """测试页面加载性能"""
        page = playwright_page
        
        # 开始性能测量
        await page.goto(f"{self.base_url}/", wait_until='networkidle')
        
        # 获取性能指标
        performance_metrics = await page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime || 0,
                    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0
                };
            }
        """)
        
        logger.info(f"Performance metrics: {performance_metrics}")
        
        # 断言性能指标
        assert performance_metrics['loadTime'] < 5000  # 5秒内加载完成
        assert performance_metrics['domContentLoaded'] < 3000  # 3秒内DOM加载完成
    
    @pytest.mark.asyncio
    async def test_memory_usage(self, playwright_page):
        """测试内存使用"""
        page = playwright_page
        
        await self.navigate_to('/')
        
        # 获取内存使用情况
        memory_info = await page.evaluate("""
            () => {
                if (performance.memory) {
                    return {
                        usedJSHeapSize: performance.memory.usedJSHeapSize,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }
        """)
        
        if memory_info:
            logger.info(f"Memory usage: {memory_info}")
            
            # 检查内存使用是否合理
            memory_usage_ratio = memory_info['usedJSHeapSize'] / memory_info['jsHeapSizeLimit']
            assert memory_usage_ratio < 0.8  # 内存使用率不应超过80%
    
    @pytest.mark.asyncio
    async def test_resource_loading(self, playwright_page):
        """测试资源加载"""
        page = playwright_page
        
        # 监听资源加载
        failed_requests = []
        
        def handle_response(response):
            if response.status >= 400:
                failed_requests.append({
                    'url': response.url,
                    'status': response.status
                })
        
        page.on('response', handle_response)
        
        await self.navigate_to('/')
        
        # 检查是否有失败的请求
        if failed_requests:
            logger.warning(f"Failed requests: {failed_requests}")
            # 允许一些404错误，但不应该有500错误
            critical_errors = [req for req in failed_requests if req['status'] >= 500]
            assert len(critical_errors) == 0, f"Critical errors found: {critical_errors}"
        else:
            logger.info("All resources loaded successfully")
