#!/usr/bin/env python3
"""
测试用例生成器Mock模式完整流程测试
用于验证整个流程是否正常工作（不依赖真实API）
"""

import json
import requests
import time
import os
from datetime import datetime

# 服务器配置
BASE_URL = "https://shenyiqing.xin"
TEST_REQUIREMENT = "用户登录系统功能测试"
TEST_PROMPT = """作为资深测试工程师，请根据以下产品需求生成完整的测试用例：

## 重要要求
⚠️ **绝对禁止使用"此处省略"、"等等"、"..."等任何形式的省略表述**
⚠️ **必须生成足够数量的测试用例，不能因为长度限制而减少**
⚠️ **优先保证完整性和数量，速度其次**
⚠️ **每个用例都必须完整，不能中途截断**
⚠️ **严格按照指定格式输出，不要乱**

## 测试用例要求
1. **功能测试**：核心功能、主要业务流程、数据处理
2. **界面测试**：关键UI交互、用户体验、页面跳转
3. **异常测试**：重要错误处理、边界条件、异常流程
4. **安全测试**：基本数据安全、权限控制、输入验证
5. **性能测试**：基本性能指标、响应时间

## 用例结构（每个用例必须包含）
- **用例ID**：TC-模块-序号（如：TC-登录-001）
- **用例标题**：简洁明确的功能描述
- **测试场景**：具体的业务场景
- **前置条件**：系统状态、数据准备
- **测试步骤**：详细的操作步骤（1.2.3...）
- **预期结果**：具体的验证点
- **优先级**：P0/P1/P2（P0最高）
- **测试类型**：功能/界面/异常/安全/性能

## 数量要求（必须满足）
- **每个功能模块至少8个用例，推荐10-15个**
- **总用例数量至少50个，推荐55-60个**
- **用例分布：正向60% + 异常25% + 边界15%**
- **必须覆盖所有核心功能和关键场景**
- **如果遇到token限制，请生成最重要的用例，确保完整性**

## 输出格式（严格按照此格式）
```
# 测试用例文档

## 模块1：[模块名称]
### TC-001：[用例标题]
**测试场景**：[具体场景]
**前置条件**：[系统状态和数据准备]
**测试步骤**：
1. [步骤1]
2. [步骤2]
3. [步骤3]
**预期结果**：[具体验证点]
**优先级**：P0/P1/P2
**测试类型**：[功能/界面/异常/安全/性能]

### TC-002：[用例标题]
[同上格式]

...（继续该模块的其他用例）

## 模块2：[模块名称]
### TC-XXX：[用例标题]
[同上格式]

...（继续其他模块）

## 总结
- 总用例数量：[数字]个
- 功能模块数量：[数字]个
- 测试覆盖情况：[覆盖的功能点]
- 测试类型分布：[正向/异常/边界测试分布]
```

## 完整性保证
- 每个用例必须包含完整的测试步骤
- 预期结果必须具体可验证
- 不能使用任何省略表述
- 严格按照格式输出，不要乱
- 最后必须有总结部分

产品需求：{requirement}

请严格按照上述格式生成完整、充足的测试用例，确保数量和质量都满足要求。"""

def test_mock_flow():
    """测试Mock模式完整流程"""
    print("🧪 开始测试用例生成器Mock模式完整流程")
    print("=" * 60)
    
    # 步骤1: 创建异步任务
    print("📝 步骤1: 创建异步任务")
    create_url = f"{BASE_URL}/tools/api/async/generate-testcases/"
    
    payload = {
        "requirement": TEST_REQUIREMENT,
        "prompt": TEST_PROMPT
    }
    
    try:
        response = requests.post(create_url, json=payload, timeout=30)
        response.raise_for_status()
        
        if response.json().get("success"):
            task_id = response.json().get("task_id")
            print(f"✅ 任务创建成功，任务ID: {task_id}")
        else:
            print(f"❌ 任务创建失败: {response.json().get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 创建任务时发生错误: {e}")
        return False
    
    # 步骤2: 监控任务状态
    print("\n📊 步骤2: 监控任务状态")
    status_url = f"{BASE_URL}/tools/api/async/task/{task_id}/"
    
    max_wait_time = 120  # 最多等待2分钟
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(status_url, timeout=10)
            response.raise_for_status()
            
            task_data = response.json()
            status = task_data.get("status")
            progress = task_data.get("progress", 0)
            current_step = task_data.get("current_step", "未知")
            
            print(f"📈 任务状态: {status}, 进度: {progress}%, 当前步骤: {current_step}")
            
            if status == "completed":
                print("✅ 任务完成！")
                result = task_data.get("result")
                if result:
                    print(f"📄 生成结果长度: {len(result)} 字符")
                    # 保存结果到文件
                    with open(f"mock_test_result_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
                        f.write(result)
                    print("💾 结果已保存到文件")
                break
            elif status == "failed":
                print(f"❌ 任务失败: {task_data.get('error')}")
                return False
            
            time.sleep(5)  # 每5秒检查一次
            
        except Exception as e:
            print(f"⚠️ 检查任务状态时发生错误: {e}")
            time.sleep(5)
    
    else:
        print("⏰ 任务超时，停止监控")
        return False
    
    # 步骤3: 测试下载功能
    print("\n📥 步骤3: 测试下载功能")
    
    # 测试TXT格式下载
    print("📄 测试TXT格式下载")
    try:
        download_url = f"{BASE_URL}/tools/api/async/task/{task_id}/download/txt/"
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        if response.headers.get('content-type') == 'text/plain; charset=utf-8':
            print("✅ TXT格式下载成功")
            # 保存下载的文件
            filename = f"mock_download_txt_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"💾 TXT文件已保存: {filename}")
        else:
            print("❌ TXT格式下载失败")
            
    except Exception as e:
        print(f"❌ TXT格式下载时发生错误: {e}")
    
    # 测试XMind格式下载
    print("\n🗺️ 测试XMind格式下载")
    try:
        download_url = f"{BASE_URL}/tools/api/async/task/{task_id}/download/xmind/"
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        if 'application/vnd.xmind.workbook' in response.headers.get('content-type', ''):
            print("✅ XMind格式下载成功")
            # 保存下载的文件
            filename = f"mock_download_xmind_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xmind"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"💾 XMind文件已保存: {filename}")
        else:
            print("❌ XMind格式下载失败")
            
    except Exception as e:
        print(f"❌ XMind格式下载时发生错误: {e}")
    
    # 测试飞书格式下载
    print("\n📋 测试飞书格式下载")
    try:
        download_url = f"{BASE_URL}/tools/api/async/task/{task_id}/download/feishu/"
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        if 'text/markdown' in response.headers.get('content-type', ''):
            print("✅ 飞书格式下载成功")
            # 保存下载的文件
            filename = f"mock_download_feishu_{task_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"💾 飞书文件已保存: {filename}")
        else:
            print("❌ 飞书格式下载失败")
            
    except Exception as e:
        print(f"❌ 飞书格式下载时发生错误: {e}")
    
    # 步骤4: 检查任务列表
    print("\n📋 步骤4: 检查任务列表")
    try:
        list_url = f"{BASE_URL}/tools/api/async/tasks/"
        response = requests.get(list_url, timeout=10)
        response.raise_for_status()
        
        tasks_data = response.json()
        if tasks_data.get("success"):
            tasks = tasks_data.get("tasks", [])
            print(f"✅ 任务列表获取成功，共 {len(tasks)} 个任务")
            
            # 查找我们的任务
            our_task = None
            for task in tasks:
                if task.get("id") == task_id:
                    our_task = task
                    break
            
            if our_task:
                print(f"✅ 找到我们的任务: {our_task.get('requirement')[:50]}...")
                print(f"   状态: {our_task.get('status')}")
                print(f"   创建时间: {our_task.get('created_at')}")
                print(f"   完成时间: {our_task.get('completed_at')}")
            else:
                print("⚠️ 在任务列表中未找到我们的任务")
        else:
            print(f"❌ 获取任务列表失败: {tasks_data.get('error')}")
            
    except Exception as e:
        print(f"❌ 获取任务列表时发生错误: {e}")
    
    print("\n🎉 Mock模式完整流程测试完成！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_mock_flow()