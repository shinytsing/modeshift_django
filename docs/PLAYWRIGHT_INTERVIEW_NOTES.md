# Playwright 面试背诵卡（Python）

更新：2026-10-06。学习顺序：Playwright → API 自动化 → pytest → 大模型测试。

用法：先背“回答”，再看“为什么”；基本操作亲手写。项目事实只说实际验证过的内容，不编造耗时和收益。

## 来源说明

[腾讯测开公开面经汇总](https://www.nowcoder.com/discuss/924819162159927296?sourceSSR=post)标注 2026-07-17，列出 UI 稳定性与维护成本、25 条 Playwright 用例耗时、接口与 UI 的取舍、CI/CD、Allure、Docker。它是网友汇总，非腾讯官方题库，真实性无法独立核实。下面标注“补充”的问题用于准备追问，不能声称是该场原题。

## 1. UI 自动化不稳定、维护成本高，怎么办？【面经题】

**回答：** 我先按定位、等待、数据和环境分类。定位优先用角色、标签或约定的 test id；等待具体响应和页面结果；每条用例隔离浏览器状态和测试数据；公共页面操作集中维护。失败保存 Trace、截图、请求响应，先定位原因，再决定是否重跑，保留首次失败证据。

**为什么：** 改定位解决结构变化，条件等待解决加载时序，数据隔离解决相互影响。重跑通过不能证明问题消失。

**项目落点：** `qa/ui/test_testing_dashboard.py` 已有按按钮角色定位、等待执行接口和页面状态的代码；运行效果需要实际验证。

## 2. 为什么不用 sleep？自动等待等什么？【补充】

**回答：** 固定 sleep 太短容易失败，太长浪费时间。我用 Playwright 的操作自动等待和 expect 条件断言。click 会等待元素唯一、可见、位置稳定、能接收点击且启用，但不保证业务完成；业务完成用页面结果或特定接口响应判断。

**为什么：** 等实际条件，比猜加载秒数可靠。`domcontentloaded` 也不意味着异步数据已经渲染。

```python
page.get_by_role("button", name="执行测试").click()
expect(page.locator("#test-status")).to_have_text("就绪")
```

此处“就绪”只验证最终 UI 状态；要证明本次确实提交，还要关联本次请求。

官方：[自动等待](https://playwright.dev/python/docs/actionability)。

## 3. 元素怎么定位？为什么少用绝对 XPath？【补充】

**回答：** 按角色和名称定位按钮，按 label 定位表单；缺少稳定语义时使用 test id 或稳定 CSS。绝对 XPath 强依赖 DOM 层级，页面结构调整就容易失效。文案也会变，因此定位要结合产品约定；多匹配时缩小到对应区域，不能随便用 first 掩盖歧义。

```python
page.get_by_role("button", name="执行测试", exact=True).click()
page.get_by_label("功能测试").uncheck()
```

**为什么：** 角色定位表达用户意图，test id 提供稳定测试契约；不存在“永远不变”的定位方法。

官方：[定位器](https://playwright.dev/python/docs/locators)。

## 4. 点击后怎么等待接口？【补充】

**回答：** 先注册 expect_response，再触发点击。用 URL 和请求方法匹配目标响应，随后校验状态码、业务内容和页面结果。

```python
with page.expect_response(
    lambda r: r.url.endswith("/api/tests/run/")
    and r.request.method == "POST"
) as info:
    page.get_by_role("button", name="执行测试").click()

response = info.value
assert response.status == 200
assert response.json()["test_types"] == ["api"]
```

**为什么：** 点击后才监听可能错过快速响应。HTTP 200 也不能单独证明业务正确。上面的数据断言前提是页面只选择了接口测试。

项目：`qa/ui/test_testing_dashboard.py`。官方：[网络控制](https://playwright.dev/python/docs/network)。

## 5. POM 怎么分层？【补充】

**回答：** 页面对象集中维护定位和页面操作；测试用例负责业务流程和结果断言；测试数据、环境配置单独管理。页面组件重复时抽公共组件，避免把所有功能塞进一个 BasePage。

**为什么：** 页面变化时集中修改，减少重复；用例仍能清晰表达测什么。页面对象可以暴露状态或提供页面级检查方法，不必机械禁止任何断言。

这是设计方案，不代表当前项目已经完整实现该结构。

官方：[POM](https://playwright.dev/python/docs/pom)。

## 6. 怎么复用登录态？【补充】

**回答：** 登录后保存 storage_state，新建 context 时加载。登录功能本身保留独立测试；其他业务测试复用状态。状态过期重新获取，不同角色分开保存，修改同一账号数据的并发测试使用独立账号。

```python
# 前提：context 已登录
context.storage_state(path="state.json")
other_context = browser.new_context(storage_state="state.json")
```

**为什么：** 减少重复登录，但浏览器隔离不会隔离服务器里的账号数据。状态文件含敏感登录信息，不提交 Git。storage_state 默认覆盖 Cookie/localStorage，sessionStorage 需要额外处理；IndexedDB 按需要启用保存。

官方：[认证状态](https://playwright.dev/python/docs/auth)。

## 7. 产品、脚本和环境问题怎么区分？【补充】

**回答：** 我结合 Trace、DOM、接口响应和服务日志判断。实际行为违背确认过的需求才算产品问题；定位或预期写错属于脚本问题；依赖不可用、测试数据缺失等可能属于环境问题。超时和断言失败都只是现象，不能直接分类。

**为什么：** 产品故障也可能导致元素找不到；错误断言也会失败。需要证据串起操作、请求和页面结果。

官方：[Trace Viewer](https://playwright.dev/python/docs/trace-viewer)。

## 8. 接口测试与 UI 测试怎么取舍？【面经题】

**回答：** 接口覆盖业务规则、参数边界、权限和异常组合；UI 覆盖关键用户流程、页面交互和前后端联动。接口一般反馈快、维护成本低，UI 更接近用户但易受页面变化影响，所以通常接口用例更多。

**为什么：** 同一业务的所有组合都走 UI，会增加运行和维护成本；只测接口又会漏掉按钮、表单和页面渲染问题。

项目：`qa/api/` 与 `qa/ui/` 已分目录，测试看板 UI 用例同时观察浏览器请求。

## 9. 25 条用例多久？如何优化？【面经题】

**回答：** 我会给出实测的环境、浏览器、是否有头、并发数、总耗时、单用例慢点及首次通过率。优化重复登录和造数、固定等待、慢依赖，随后在数据隔离和机器容量允许时并行执行。

**为什么：** 用例数量相同，业务链路和运行环境不同，耗时会相差很大。没测过就说“这个数字我需要实测”，不编秒数。

项目测量入口：`python3 qa/run_ui.py`。读取报告中的用例耗时，并区分启动服务与测试执行时间。Python pytest 并行通常使用 pytest-xdist，不能直接照搬 Playwright 的 JavaScript runner 配置。

## 10. CI、Docker、Allure 怎么讲？【面经题】

**回答：** 流水线获取代码、安装依赖、启动测试环境、健康检查、执行测试，再归档报告与失败证据，并按规则决定是否放行。Docker 统一依赖和浏览器环境；Allure 展示结果、步骤、耗时和附件，但报告生成成功不等于测试通过。

**为什么：** 固定环境减少本地和 CI 差异，失败证据支持排查，质量门禁防止已知回归进入后续发布。

项目已有入口：`qa/scripts/run_suite.py`；报告目录：`qa/artifacts/`。实际 CI 配置需要单独阅读核实。

## 11. 网络 Mock 有什么用途和局限？【补充】

**回答：** 用 page.route 控制接口成功、失败和超时等响应，验证前端展示和错误处理；同时保留真实接口联调用例。Mock 测试验证前端对约定响应的处理，不能证明后端实现正确。

**为什么：** 可控响应能稳定复现罕见异常，真实联调能发现接口契约漂移。

项目阅读入口：`qa/ui/test_testcase_knowledge_selection.py`。官方：[网络 Mock](https://playwright.dev/python/docs/network)。

## 12. Browser、Context、Page 的区别？【补充】

**回答：** Browser 是浏览器实例；Context 是隔离的浏览器会话；Page 是会话里的标签页。不同测试可以复用 Browser，但使用独立 Context 隔离 Cookie 和存储。

**为什么：** 少重复启动浏览器，同时减少浏览器状态串扰。服务器侧测试数据仍需另外隔离。

官方：[测试隔离](https://playwright.dev/python/docs/browser-contexts)。

## 必须亲手写的最小代码

先会这几个动作，再写完整流程。`page` 已创建且目标页面已加载时执行；以下是项目语法示例，非独立可执行脚本。

```python
from playwright.sync_api import expect

page.goto("http://127.0.0.1:8000/testing-dashboard/")
expect(page.get_by_role("heading", name="测试手法展示中心")).to_be_visible()
page.get_by_label("功能测试").uncheck()
expect(page.get_by_label("接口测试")).to_be_checked()
```

第一轮只背第 1、2、3、4、7 题。第二轮背其余题。每题用自己的话讲 30～60 秒；遇到项目追问，打开对应源码复习，再通过实际运行补充证据。
