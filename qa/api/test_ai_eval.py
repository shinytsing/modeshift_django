"""Offline regression examples for the testcase-output quality gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from qa.ai_eval.evaluate import evaluate_output

REQUIREMENTS = json.loads(
    (Path(__file__).resolve().parents[1] / "ai_eval" / "login_otp_expired.json").read_text(encoding="utf-8")
)

GOOD_OUTPUT = """# 测试用例文档
### TC-登录-001：过期的旧验证码不可登录
**测试场景**：用户输入已过期的旧验证码。
**前置条件**：已获取验证码且它已经过期。
**测试步骤**：
1. 输入旧验证码并提交登录。
2. 查看提示。
**预期结果**：登录被拒绝，页面提示重新获取验证码。
**优先级**：P0
**测试类型**：异常
"""


@pytest.mark.ai_eval
def test_reviewed_case_passes_offline_gate():
    assert evaluate_output(GOOD_OUTPUT, REQUIREMENTS["required_terms"]) == []


@pytest.mark.ai_eval
def test_duplicate_or_incomplete_case_fails_offline_gate():
    bad_output = GOOD_OUTPUT + "\n### TC-登录-001：重复\n**预期结果**：同上格式\n"
    issues = evaluate_output(bad_output, REQUIREMENTS["required_terms"])
    assert "存在重复的用例 ID" in issues
    assert any("缺少有效的测试场景" in issue for issue in issues)
    assert any("包含省略或待补充内容" in issue for issue in issues)


@pytest.mark.ai_eval
def test_missing_requirement_concept_fails_offline_gate():
    issues = evaluate_output(GOOD_OUTPUT, ["短信限流"])
    assert issues == ["未覆盖必需概念：短信限流"]
