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

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 常见报错 → 具体怎么改。命中的会打印成「修复建议」，让人一眼知道下一步做什么。
ADVICE_RULES: list[tuple[str, str]] = [
    (
        r"缺少文件顶部 Frontmatter",
        "这篇还没有元数据。先确认文件名是「前缀 编号 标题.md」（例如 `MB 12 微生物与抗生素.md`），"
        "再重新运行本脚本——它会自动补上 frontmatter。",
    ),
    (
        r"文件名必须以",
        "文件名前缀不对。每门课有固定前缀（FAI / MB / MMB / CB / BOT / BC / BIF），"
        "文件名必须以「前缀 + 空格」开头，例如 `MB 01 绪论.md`。",
    ),
    (
        r"文件名必须同时包含顺序编号和标题",
        "文件名要同时有编号和标题，例如 `MB 12 微生物与抗生素.md`、`BC 2-5 水分活度.md`、`BOT A-1 植物的细胞.md`。",
    ),
    (
        r"课程目录不存在",
        "目录名和 `data/course-config.json` 里的 `directory` 对不上。如果你改过课程目录名，"
        "要同步更新这个配置文件里的 `directory` 字段。",
    ),
    (
        r"本地图像不存在|HTML 图像目标不存在|图像语法指向了非图像文件",
        "图片路径不对——最常见的原因是**把笔记移到子目录后没改相对路径**。按当前位置写："
        "在 `BC 1 蛋白质专题/` 这样的子目录里，引用仓库根目录的图要写 `../../assets/generated/xxx.svg`。",
    ),
    (
        r"Markdown 本地链接目标不存在",
        "链接指向的文件不存在。改成相对当前位置的正确路径（注意笔记移动后要多退一层 `../`），"
        "或者确认目标文件确实已经提交。",
    ),
    (
        r"本地图像未被任何 Markdown 页面引用",
        "这张图没有任何页面引用它：要么在正文里用上，要么删掉。"
        "如果上面还有一条「本地图像不存在」，说明是图片路径写错导致的连带报错，先修那条。",
    ),
    (
        r"图像未记录在\s*assets/image-sources\.json",
        "新增的图片要在来源清单里登记：运行 `python3 scripts/build_image_manifest.py`，"
        "然后在 `assets/image-sources.json` 里补上来源与许可。",
    ),
    (
        r"图像来源清单与当前资产不一致|图像路径在清单中重复|清单中的图像文件不存在|SHA-256 与来源清单不一致",
        "图片清单和实际文件不同步：运行 `python3 scripts/build_image_manifest.py` 刷新清单（本脚本也会自动跑）。",
    ),
    (
        r"last_scientific_review 必须是",
        "把这个字段改成 `null`，或写成 `2026-01-01` 这样的日期。",
    ),
    (
        r"需要重新生成|生成一致性检查失败",
        "有自动生成的文件不是最新：重新运行本脚本即可（它会重新生成目录、导航和课程清单）。"
        "如果还是失败，多半是课程目录改名后没有同步 `data/course-config.json`。",
    ),
    (
        r"quality report is stale",
        "质量报告过期：重新运行本脚本，它会自动刷新 `data/quality-report.json`。",
    ),
    (
        r"可复现图像检查|教学 SVG",
        "教学图和脚本生成的结果不一致：运行 `python3 scripts/generate_teaching_figures.py` 重新生成。",
    ),
    (
        r"没有入站链接",
        "这篇没有任何页面链接到它。跑一次生成脚本通常就会把它接进课程目录；"
        "如果它本来就不该发布（比如草稿页），可以忽略。",
    ),
    (
        r"FAILED|Traceback|unittest",
        "单元测试或脚本本身报错：看上面的失败信息，修好对应脚本后重跑 `python3 -m unittest discover -s tests -v`。",
    ),
]


def advice_for(output: str) -> list[str]:
    tips: list[str] = []
    for pattern, tip in ADVICE_RULES:
        if re.search(pattern, output) and tip not in tips:
            tips.append(tip)
    return tips


def print_advice(output: str) -> None:
    print("\n" + "-" * 56)
    print("修复建议：")
    tips = advice_for(output)
    if tips:
        for index, tip in enumerate(tips, 1):
            print(f"  {index}. {tip}")
    else:
        print("  没有匹配到已知的错误类型。可以把上面的报错发给维护者，")
        print("  或对照 docs/content-frontmatter.md、docs/repository-hygiene.md 自查。")
    print("\n改好后重新运行本脚本（或双击「准备提交.command」）即可。")


# 会修改文件的步骤，按顺序执行；任一步失败就停下来（避免生成出半成品）
WRITE_STEPS: list[tuple[str, list[str]]] = [
    ("补齐缺少的元数据（frontmatter）", ["scripts/migrate_course_metadata.py"]),
    ("生成课程导航 / 课程目录 / 课程清单", ["scripts/build_course_catalog.py"]),
    ("刷新图片来源清单", ["scripts/build_image_manifest.py"]),
    (
        "刷新资源质量报告（含链接与图片检查）",
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
    print("（某一步没通过时，会给出对应的修复建议）")
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
            print_advice(output)
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
        print_advice("\n".join(output for _, output in failures))
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
