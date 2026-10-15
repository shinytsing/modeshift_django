"""Check observable testcase-output quality without invoking an LLM."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

CASE_HEADING = re.compile(r"(?m)^###\s+(TC-[\w-]+)\s*[：:]\s*(\S.*?)\s*$")
REQUIRED_FIELDS = ("测试场景", "前置条件", "测试步骤", "预期结果", "优先级", "测试类型")
PLACEHOLDER = re.compile(r"此处省略|待补充|同上格式|\.\.\.|……")


def evaluate_output(output: str, required_terms: list[str]) -> list[str]:
    """Return actionable reasons for a failed offline quality gate."""
    issues: list[str] = []
    headings = list(CASE_HEADING.finditer(output))
    if not headings:
        return ["没有识别到任何 TC- 用例标题"]

    ids = [match.group(1) for match in headings]
    if len(ids) != len(set(ids)):
        issues.append("存在重复的用例 ID")
    for term in required_terms:
        if term not in output:
            issues.append(f"未覆盖必需概念：{term}")

    for index, heading in enumerate(headings):
        case_id = heading.group(1)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(output)
        block = output[heading.end() : end]
        for field in REQUIRED_FIELDS:
            if not re.search(rf"(?m)^\*\*{field}\*\*\s*[：:]\s*\S", block):
                issues.append(f"{case_id} 缺少有效的{field}")
        if not re.search(r"(?m)^1[.、]\s*\S", block):
            issues.append(f"{case_id} 没有可执行的第 1 步")
        if not re.search(r"\*\*优先级\*\*\s*[：:]\s*P[012]\b", block):
            issues.append(f"{case_id} 优先级不是 P0/P1/P2")
        if PLACEHOLDER.search(block):
            issues.append(f"{case_id} 包含省略或待补充内容")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a saved real-model testcase output")
    parser.add_argument("output", type=Path, help="UTF-8 Markdown output saved from the model")
    parser.add_argument("--requirements", type=Path, required=True, help="JSON with required_terms")
    args = parser.parse_args()
    requirements = json.loads(args.requirements.read_text(encoding="utf-8"))
    issues = evaluate_output(args.output.read_text(encoding="utf-8"), requirements["required_terms"])
    for issue in issues:
        print(f"FAIL: {issue}")
    if not issues:
        print("PASS: structural and required-concept checks")
    return bool(issues)


if __name__ == "__main__":
    raise SystemExit(main())
