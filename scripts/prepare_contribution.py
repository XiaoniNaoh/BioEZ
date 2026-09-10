#!/usr/bin/env python3
"""准备提交：把该自动生成的东西生成好，再整体检查一遍。

给不想记命令的人用。写完文章后跑一次（macOS 上可以直接双击仓库根目录的
「准备提交.command」），然后回到 GitHub Desktop 填一句说明、Commit、Push 即可。

它做两件事：

1. 写入：补齐缺少的 frontmatter、生成「课程导航」与课程目录、更新课程清单、
   刷新图片来源清单与资源质量报告。
2. 检查：把 CI 会跑的那几项在本地先跑一遍（元数据、生成一致性、教学图、
   图片清单、链接与图片、单元测试），有错就告诉你哪里不对。

用法：

    python3 scripts/prepare_contribution.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 会修改文件的步骤，按顺序执行；任一步失败就停下来（避免生成出半成品）
WRITE_STEPS: list[tuple[str, list[str]]] = [
    ("补齐缺少的元数据（frontmatter）", ["scripts/migrate_course_metadata.py"]),
    ("生成课程导航 / 课程目录 / 课程清单", ["scripts/build_course_catalog.py"]),
    ("刷新图片来源清单", ["scripts/build_image_manifest.py"]),
    (
        "刷新资源质量报告",
        ["scripts/check_content_resources.py", "--json-report", "data/quality-report.json"],
    ),
]

# 只读检查，全部跑完再汇总（一次能看到所有问题）
CHECK_STEPS: list[tuple[str, list[str]]] = [
    ("元数据校验", ["scripts/validate_content.py", "--all"]),
    ("生成一致性检查", ["scripts/build_course_catalog.py", "--check"]),
    ("教学图可复现性", ["scripts/generate_teaching_figures.py", "--check"]),
    ("图片清单一致性", ["scripts/build_image_manifest.py", "--check"]),
    (
        "链接与图片检查",
        ["scripts/check_content_resources.py", "--check-report", "data/quality-report.json"],
    ),
    ("单元测试", ["-m", "unittest", "discover", "-s", "tests"]),
]


def run(args: list[str]) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()


def tail(text: str, lines: int = 6) -> str:
    rows = [row for row in text.splitlines() if row.strip()]
    return "\n".join(rows[-lines:])


def changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=false", "status", "--short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return [row for row in (result.stdout or "").splitlines() if row.strip()]


def main() -> int:
    print("=" * 56)
    print("准备提交：先把该生成的东西生成好，再检查一遍")
    print("=" * 56)

    print("\n【第一步】自动生成（会修改文件）")
    for label, args in WRITE_STEPS:
        ok, output = run(args)
        if ok:
            detail = tail(output, 1)
            print(f"  ✓ {label}" + (f" —— {detail}" if detail else ""))
        else:
            print(f"  ✗ {label} 失败：\n")
            print(output or "（没有输出）")
            print("\n请先按上面的提示修好，再重新运行本脚本。")
            return 1

    print("\n【第二步】检查（不会修改文件）")
    failures: list[tuple[str, str]] = []
    for label, args in CHECK_STEPS:
        ok, output = run(args)
        if ok:
            detail = tail(output, 1)
            print(f"  ✓ {label}" + (f" —— {detail}" if detail else ""))
        else:
            print(f"  ✗ {label}")
            failures.append((label, output))

    files = changed_files()
    print("\n" + "-" * 56)
    if failures:
        print(f"检查未通过（{len(failures)} 项）：\n")
        for label, output in failures:
            print(f"### {label}")
            print(output or "（没有输出）")
            print()
        print("修好后重新运行本脚本即可。")
        return 1

    if not files:
        print("没有发现需要提交的改动——这次应该只是查看，没有改内容。")
        return 0

    print(f"全部完成 ✓  本次改动了 {len(files)} 个文件：\n")
    for row in files[:30]:
        print(f"    {row}")
    if len(files) > 30:
        print(f"    …… 另有 {len(files) - 30} 个")
    print()
    print("下一步：回到 GitHub Desktop，填一句提交说明 → Commit → Push。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
