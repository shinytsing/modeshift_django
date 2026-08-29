#!/usr/bin/env python3
"""
使用Python Playwright生成Boss直聘二维码
"""
import asyncio
import os
from playwright.async_api import async_playwright

async def generate_boss_qr_code(qr_image_path: str, task_id: str = None):
    """使用Playwright生成Boss直聘二维码"""
    try:
        print(f"开始生成Boss直聘二维码: {qr_image_path}")

        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 访问Boss直聘登录页面
            await page.goto("https://www.zhipin.com/web/user/?ka=header-login", timeout=60000)
            await page.wait_for_load_state("networkidle", timeout=30000)

            print("页面加载完成，查找二维码登录按钮...")

            # 点击二维码登录按钮
            try:
                # 尝试多个可能的选择器
                qr_selectors = [
                    ".login-tabs .tab-item:last-child",
                    ".login-tabs .tab-item:nth-child(2)",
                    "[data-ka='login-qrcode']",
                    ".qrcode-tab",
                    ".scan-login"
                ]

                clicked = False
                for selector in qr_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            await element.click()
                            print(f"点击二维码登录按钮成功: {selector}")
                            clicked = True
                            break
                    except Exception as e:
                        print(f"选择器 {selector} 失败: {e}")
                        continue

                if not clicked:
                    print("未找到二维码登录按钮，尝试直接查找二维码")

            except Exception as e:
                print(f"点击二维码按钮失败: {e}")

            # 等待二维码加载
            await page.wait_for_timeout(3000)

            # 查找二维码元素
            qr_selectors = [
                ".qrcode-img img",
                ".qr-code img",
                ".login-qr img",
                ".qrcode-img",
                "[class*='qr'] img",
                "img[src*='qr']",
                "img[alt*='二维码']"
            ]

            qr_element = None
            for selector in qr_selectors:
                try:
                    qr_element = await page.query_selector(selector)
                    if qr_element:
                        print(f"找到二维码元素: {selector}")
                        break
                except Exception as e:
                    continue

            if qr_element:
                # 截图二维码
                await qr_element.screenshot(path=qr_image_path)
                print(f"二维码截图成功: {qr_image_path}")
            else:
                # 如果找不到二维码，截图整个页面
                await page.screenshot(path=qr_image_path)
                print(f"全页面截图: {qr_image_path}")

            await browser.close()
            return True

    except Exception as e:
        print(f"生成二维码失败: {e}")
        return False

def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python generate_qr.py <输出路径> [任务ID]")
        sys.exit(1)

    qr_path = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else "test"

    # 确保目录存在
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)

    # 运行异步函数
    success = asyncio.run(generate_boss_qr_code(qr_path, task_id))

    if success:
        print("✅ 二维码生成成功!")
    else:
        print("❌ 二维码生成失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
