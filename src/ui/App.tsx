import { useMemo, useState } from 'react'
import { ArrowRight, BarChart3, CheckCircle2, Clock3, HelpCircle, RotateCcw, ShieldCheck, Sparkles, Target, Trophy, XCircle } from 'lucide-react'

type Question = {
  id: number
  category: string
  level: '基础' | '进阶' | '实战'
  question: string
  options: string[]
  answer: number
  explanation: string
  projectNote: string
}

const questions: Question[] = [
  { id: 1, category: 'pytest', level: '基础', question: 'pytest 中 conftest.py 的主要作用是什么？', options: ['存放所有测试数据', '定义共享 fixture、钩子和测试配置', '替代 pytest.ini', '专门保存失败截图'], answer: 1, explanation: 'conftest.py 会被 pytest 自动发现，适合放共享 fixture、钩子和测试环境初始化逻辑。', projectNote: '对应 qa/conftest.py、qa/api/conftest.py 和 qa/ui/conftest.py。' },
  { id: 2, category: 'pytest', level: '基础', question: '使用 yield fixture 时，yield 前后的代码分别通常承担什么职责？', options: ['前置和后置清理', '登录和断言', '参数化和收集', '报告和邮件发送'], answer: 0, explanation: 'yield 前负责准备资源，yield 后负责清理资源，例如创建并删除测试用户、启动并关闭浏览器。', projectNote: '项目中 QA 用户的精确清理就是典型的 yield fixture 场景。' },
  { id: 3, category: 'pytest', level: '进阶', question: '一个 fixture 需要在整个 pytest 会话中只初始化一次，应该选择哪个 scope？', options: ['function', 'class', 'module', 'session'], answer: 3, explanation: 'session scope 的生命周期覆盖整个测试会话，适合复用稳定的客户端、配置或连接。', projectNote: 'API 客户端或只读配置可以考虑更大的 scope；临时业务数据仍建议保持 function 隔离。' },
  { id: 4, category: '接口', level: '基础', question: '接口自动化分层时，test 文件最适合负责什么？', options: ['直接拼接所有 URL 和请求头', '维护底层 HTTP 连接', '组织业务场景并完成断言', '生成浏览器截图'], answer: 2, explanation: 'transport 负责底层请求，client 负责业务接口封装，test 层负责场景编排和断言。', projectNote: '对应 qa/api/clients/transport.py、auth.py、dashboard.py 与 qa/api/test_*.py。' },
  { id: 5, category: '接口', level: '基础', question: '为什么接口自动化不应该只断言 HTTP 状态码？', options: ['状态码不能被读取', '状态码只能说明 HTTP 层结果，不能证明业务正确', '状态码只适合 POST', '状态码会自动修改数据库'], answer: 1, explanation: 'HTTP 200 只说明请求在协议层成功，仍需验证业务 code、关键字段、数据变化和错误副作用。', projectNote: '健康检查可以断言 status；核心业务还要继续断言响应结构和业务字段。' },
  { id: 6, category: '接口', level: '进阶', question: '接口自动化中处理登录 Token 的推荐方式是什么？', options: ['写死在每个测试文件中', '提交到 Git 仓库共享', '通过登录接口动态获取并由 fixture 复用', '每次手工复制浏览器 Token'], answer: 2, explanation: 'Token 会过期且属于敏感信息，应该动态获取，并通过 fixture 或认证客户端统一注入。', projectNote: '对应 qa/api/conftest.py 和 qa/api/clients/auth.py 的认证链路。' },
  { id: 7, category: 'UI 自动化', level: '基础', question: 'Page Object 模式的核心职责划分是什么？', options: ['Page Object 放定位和页面操作，test 放业务流程和断言', 'Page Object 只放测试数据', 'test 文件只放定位器', '两者职责完全相同'], answer: 0, explanation: 'Page Object 封装页面细节，测试用例表达业务意图，这样定位器变化时维护成本更低。', projectNote: '对应 qa/ui/pages/ 和 qa/ui/test_*.py。' },
  { id: 8, category: '质量设计', level: '实战', question: '如何保证接口自动化用例之间相互独立？', options: ['依赖测试执行顺序', '使用全局变量传递上条用例的数据', '每条用例准备自己的数据并在结束后清理', '只执行通过率高的用例'], answer: 2, explanation: '独立用例可以单独执行、并行执行和失败重跑。fixture、唯一数据和精确清理是常用手段。', projectNote: '项目已经实践了 QA 注册用户的精确创建和清理。' },
  { id: 9, category: '质量设计', level: '实战', question: '什么时候适合使用 Mock Server？', options: ['验证第三方服务自身的真实稳定性', '隔离不可控依赖并构造超时、失败等异常响应', '替代所有接口测试', '只为了让报告看起来更好'], answer: 1, explanation: 'Mock 主要验证自己的系统如何处理依赖服务的不同结果，适合隔离第三方和构造难以复现的异常。', projectNote: '短信、支付、账号中心和 AI 服务都可以作为 Mock 的典型依赖。' },
  { id: 10, category: 'CI/CD', level: '进阶', question: 'pytest.ini、Allure 和 CI 平台的关系更准确的是哪一项？', options: ['pytest.ini 直接发送邮件', 'Allure 负责执行全部测试', 'pytest 执行测试，Allure 展示结果，CI 负责自动触发和归档', 'CI 只负责保存源代码'], answer: 2, explanation: 'pytest.ini 提供 pytest 配置，pytest 产生结果，Allure 生成可读报告，Jenkins 或 GitHub Actions 负责编排流程。', projectNote: '对应 qa/pytest.ini、qa/scripts/run_suite.py 和 .github/workflows/testing-system.yml。' },
  { id: 11, category: '故障排查', level: '实战', question: '一条接口用例失败时，最合理的排查顺序是什么？', options: ['先重装电脑', '先看堆栈和响应，再判断断言、代码、数据还是环境问题', '直接删除用例', '只看最终通过率'], answer: 1, explanation: '先保留证据，再定位问题类型：断言错误、请求代码错误、测试数据问题、服务问题或环境问题。', projectNote: '可以结合日志、请求响应、失败截图和单独重跑来提高定位效率。' },
  { id: 12, category: 'AI 测试', level: '实战', question: 'AI 辅助测试最需要人工把关的环节是什么？', options: ['复制粘贴代码', '业务风险、测试 oracle 和结果可信度', '生成文件名', '调整终端字体'], answer: 1, explanation: 'AI 可以加速生成和分析，但业务风险、断言是否成立、误报漏报和数据安全仍需要测试人员负责。', projectNote: '你的项目已有离线 AI 输出结构检查，可以继续扩展为测试结果和质量门禁。' },
]

const categoryNames = ['全部', ...Array.from(new Set(questions.map((item) => item.category)))]

function scoreLabel(score: number) {
  if (score >= 90) return { text: '面试状态很好', tone: 'excellent' }
  if (score >= 70) return { text: '基础已经成型', tone: 'good' }
  if (score >= 60) return { text: '继续补齐薄弱点', tone: 'pass' }
  return { text: '先夯实核心概念', tone: 'needs-work' }
}

export default function App() {
  const [activeCategory, setActiveCategory] = useState('全部')
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [submitted, setSubmitted] = useState(false)
  const [showWrongOnly, setShowWrongOnly] = useState(false)
  const visibleQuestions = useMemo(() => questions.filter((question) => (activeCategory === '全部' || question.category === activeCategory) && (!showWrongOnly || (submitted && answers[question.id] !== question.answer))), [activeCategory, answers, showWrongOnly, submitted])
  const answeredCount = Object.keys(answers).length
  const correctCount = questions.filter((question) => answers[question.id] === question.answer).length
  const score = Math.round((correctCount / questions.length) * 100)
  const result = scoreLabel(score)
  const chooseAnswer = (questionId: number, optionIndex: number) => { if (!submitted) setAnswers((current) => ({ ...current, [questionId]: optionIndex })) }
  const reset = () => { setAnswers({}); setSubmitted(false); setShowWrongOnly(false); window.scrollTo({ top: 0, behavior: 'smooth' }) }

  return (
    <div className="learning-shell">
      <header className="topbar"><div className="brand-lockup"><div className="brand-mark"><Sparkles size={17} /></div><div><div className="brand-name">ModeShift Lab</div><div className="brand-subtitle">测试开发成长中心</div></div></div><div className="topbar-status"><span className="status-dot" />本地学习模式</div></header>
      <main className="page-content">
        <section className="hero-panel"><div className="hero-copy"><div className="eyebrow"><span>QA CAREER TRACK</span><span className="eyebrow-line" /></div><h1>测试开发面试<br /><em>实战试卷</em></h1><p>把 pytest、接口自动化、UI 自动化、CI/CD 和 AI 测试串成一套可复述、可实践的面试能力。</p><div className="hero-actions"><a className="primary-button" href="#paper">开始答题 <ArrowRight size={17} /></a><span className="hero-note"><ShieldCheck size={15} /> 题目按真实面试场景设计</span></div></div><div className="hero-orbit" aria-hidden="true"><div className="orbit-ring ring-one" /><div className="orbit-ring ring-two" /><div className="orbit-core"><Target size={30} /><strong>QA</strong><span>READY</span></div><div className="orbit-chip chip-top">PYTEST</div><div className="orbit-chip chip-right">API</div><div className="orbit-chip chip-bottom">CI/CD</div></div></section>
        <section className="metric-row"><div className="metric-card"><div className="metric-icon orange"><HelpCircle size={18} /></div><div><strong>{questions.length}</strong><span>道综合题</span></div></div><div className="metric-card"><div className="metric-icon blue"><Clock3 size={18} /></div><div><strong>25 min</strong><span>建议用时</span></div></div><div className="metric-card"><div className="metric-icon green"><BarChart3 size={18} /></div><div><strong>100 分</strong><span>满分标准</span></div></div><div className="metric-card progress-card"><div className="progress-label"><span>答题进度</span><strong>{answeredCount}/{questions.length}</strong></div><div className="progress-track"><span style={{ width: `${(answeredCount / questions.length) * 100}%` }} /></div></div></section>
        <section className="workbench" id="paper"><aside className="sidebar-card"><div className="section-kicker">学习导航</div><h2>一套试卷，五层能力</h2><p>先独立作答，再看解析。把不会的题记录下来，下一轮只复习薄弱项。</p><nav className="category-list" aria-label="题目分类">{categoryNames.map((category) => <button key={category} className={activeCategory === category ? 'category-item active' : 'category-item'} onClick={() => setActiveCategory(category)}><span>{category}</span><small>{category === '全部' ? questions.length : questions.filter((item) => item.category === category).length}</small></button>)}</nav><div className="sidebar-tip"><Trophy size={17} /><div><strong>面试提醒</strong><span>回答时一定要结合自己的项目文件和实际案例。</span></div></div></aside>
          <div className="paper-column"><div className="paper-heading"><div><div className="section-kicker">MOCK INTERVIEW · 01</div><h2>测试开发综合能力评估</h2><p>单选题 · 每题 {Math.round(100 / questions.length)} 分 · 共 {questions.length} 题</p></div><div className="paper-actions">{submitted && <button className={showWrongOnly ? 'filter-button selected' : 'filter-button'} onClick={() => setShowWrongOnly((value) => !value)}><XCircle size={15} />{showWrongOnly ? '显示全部' : '只看错题'}</button>}<button className="reset-button" onClick={reset}><RotateCcw size={15} />重新开始</button></div></div>
            {submitted && <div className={`result-banner ${result.tone}`}><div className="result-score"><span>本次得分</span><strong>{score}</strong><small>/ 100</small></div><div className="result-copy"><strong>{result.text}</strong><span>答对 {correctCount} 题，答错 {questions.length - correctCount} 题。建议先复习错题解析，再用自己的项目语言复述一遍。</span></div><div className="result-badge"><Trophy size={18} /> {score >= 70 ? 'PASS' : 'KEEP GOING'}</div></div>}
            <div className="question-list">{visibleQuestions.map((question, index) => { const selected = answers[question.id]; const isCorrect = selected === question.answer; return <article className={`question-card ${submitted ? (isCorrect ? 'correct' : 'wrong') : ''}`} key={question.id}><div className="question-meta"><span className="question-number">Q{String(question.id).padStart(2, '0')}</span><span className="tag">{question.category}</span><span className={`level ${question.level}`}>{question.level}</span><span className="question-index">{index + 1} / {visibleQuestions.length}</span></div><h3>{question.question}</h3><div className="option-grid">{question.options.map((option, optionIndex) => { const picked = selected === optionIndex; const answerOption = submitted && optionIndex === question.answer; return <button key={option} className={`option ${picked ? 'picked' : ''} ${answerOption ? 'answer' : ''} ${submitted && picked && !isCorrect ? 'incorrect' : ''}`} onClick={() => chooseAnswer(question.id, optionIndex)} disabled={submitted}><span className="option-letter">{String.fromCharCode(65 + optionIndex)}</span><span>{option}</span>{answerOption && <CheckCircle2 className="option-icon" size={17} />}</button> })}</div>{submitted && <div className={`explanation ${isCorrect ? 'positive' : 'negative'}`}><div className="explanation-title">{isCorrect ? <CheckCircle2 size={16} /> : <XCircle size={16} />}{isCorrect ? '回答正确' : `正确答案：${String.fromCharCode(65 + question.answer)}`}</div><p>{question.explanation}</p><small><strong>项目映射：</strong>{question.projectNote}</small></div>}</article> })}</div>
            {!submitted && <button className="submit-button" disabled={answeredCount !== questions.length} onClick={() => { setSubmitted(true); window.scrollTo({ top: 0, behavior: 'smooth' }) }}>{answeredCount === questions.length ? '提交试卷并查看解析' : `完成全部题目后提交 · 还剩 ${questions.length - answeredCount} 题`}<ArrowRight size={18} /></button>}
          </div></section>
      </main><footer className="site-footer"><span>ModeShift Lab · 测试开发学习页面</span><span>练习结果仅保存在当前页面</span></footer>
    </div>
  )
}
