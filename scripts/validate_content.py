#!/usr/bin/env python3
"""Incrementally validate BioEZ Markdown frontmatter without third-party packages."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
COURSE_DIRECTORY = re.compile(r"^0[1-7] ")
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_STATUS = {"draft", "editorial-review", "scientific-review", "published"}
REQUIRED_FIELDS = (
    "id", "title", "course", "chapter", "order", "status", "audience",
    "difficulty", "importance", "estimated_minutes", "prerequisites", "next",
    "tags", "authors", "reviewers", "last_scientific_review", "summary", "references",
)
LIST_FIELDS = {"audience", "prerequisites", "next", "tags", "authors", "reviewers", "references"}


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str

    def __str__(self) -> str:
        try:
            display = self.path.relative_to(ROOT)
        except ValueError:
            display = self.path
        return f"{display}: {self.message}"


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"null", "~"}:
        return None
    if value == "[]":
        return []
    if value in {"true", "false"}:
        return value == "true"
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """Parse the small YAML subset used by the schema."""
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "缺少文件顶部 Frontmatter"
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None, "Frontmatter 缺少结束分隔符 ---"

    data: dict[str, Any] = {}
    current_list: str | None = None
    for number, raw in enumerate(lines[1:end], 2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.+?)\s*$", raw)
        if item and current_list:
            data[current_list].append(_scalar(item.group(1)))
            continue
        field = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*?)\s*$", raw)
        if not field:
            return None, f"Frontmatter 第 {number} 行语法不受支持"
        key, raw_value = field.groups()
        if key in data:
            return None, f"Frontmatter 字段 {key} 重复"
        if raw_value:
            data[key] = _scalar(raw_value)
            current_list = None
        else:
            data[key] = []
            current_list = key
    return data, None


def is_content_path(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    return path.suffix.lower() == ".md" and bool(relative.parts) and bool(COURSE_DIRECTORY.match(relative.parts[0])) and "模板" not in path.name


def validate_file(path: Path) -> tuple[dict[str, Any] | None, list[Finding]]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, [Finding(path, f"无法读取 UTF-8 文件: {exc}")]

    data, parse_error = parse_frontmatter(text)
    if parse_error:
        return None, [Finding(path, parse_error)]
    assert data is not None

    for field in REQUIRED_FIELDS:
        if field not in data:
            findings.append(Finding(path, f"缺少必填字段 {field}"))

    if findings:
        return data, findings

    if not isinstance(data["id"], str) or not ID_PATTERN.fullmatch(data["id"]):
        findings.append(Finding(path, "id 必须是由小写字母、数字和单个连字号分隔的稳定标识"))
    for field in ("title", "course", "chapter", "summary"):
        if not isinstance(data[field], str) or not data[field].strip():
            findings.append(Finding(path, f"{field} 必须是非空字符串"))
    if data["status"] not in ALLOWED_STATUS:
        findings.append(Finding(path, f"status 必须是 {', '.join(sorted(ALLOWED_STATUS))} 之一"))
    for field in LIST_FIELDS:
        if not isinstance(data[field], list):
            findings.append(Finding(path, f"{field} 必须是列表"))
    for field in ("difficulty", "importance"):
        if not isinstance(data[field], int) or isinstance(data[field], bool) or not 1 <= data[field] <= 5:
            findings.append(Finding(path, f"{field} 必须是 1–5 的整数"))
    minutes = data["estimated_minutes"]
    if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes <= 0:
        findings.append(Finding(path, "estimated_minutes 必须是大于 0 的整数"))

    review_date = data["last_scientific_review"]
    if review_date is not None:
        if not isinstance(review_date, str):
            findings.append(Finding(path, "last_scientific_review 必须是 YYYY-MM-DD 或 null"))
        else:
            try:
                dt.date.fromisoformat(review_date)
            except ValueError:
                findings.append(Finding(path, "last_scientific_review 必须是有效的 YYYY-MM-DD 日期"))
    if data["status"] == "published" and (not data["reviewers"] or review_date is None):
        findings.append(Finding(path, "published 页面必须记录 reviewers 和 last_scientific_review"))
    return data, findings


def changed_paths(base: str, head: str) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "-z", "--diff-filter=ACMR", f"{base}...{head}", "--", "*.md"],
        cwd=ROOT, check=True, capture_output=True,
    )
    return [ROOT / os.fsdecode(item) for item in result.stdout.split(b"\0") if item]


def find_duplicate_metadata() -> list[Finding]:
    seen_ids: dict[str, Path] = {}
    seen_titles: dict[str, Path] = {}
    findings: list[Finding] = []
    for path in ROOT.rglob("*.md"):
        if not is_content_path(path):
            continue
        data, error = parse_frontmatter(path.read_text(encoding="utf-8"))
        if error or not data or not isinstance(data.get("id"), str):
            continue
        identifier = data["id"]
        if identifier in seen_ids:
            findings.append(Finding(path, f"id {identifier} 与 {seen_ids[identifier].relative_to(ROOT)} 重复"))
        else:
            seen_ids[identifier] = path
        title = data.get("title")
        if not isinstance(title, str):
            continue
        normalized_title = " ".join(title.split()).casefold()
        if normalized_title in seen_titles:
            findings.append(Finding(path, f"title {title} 与 {seen_titles[normalized_title].relative_to(ROOT)} 重复"))
        else:
            seen_titles[normalized_title] = path
    return findings


def validate_paths(paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        path = path if path.is_absolute() else ROOT / path
        if path.exists() and is_content_path(path):
            _, file_findings = validate_file(path)
            findings.extend(file_findings)
    findings.extend(find_duplicate_metadata())
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--paths", nargs="+", type=Path, help="要检查的 Markdown 路径")
    source.add_argument("--base", help="Git 对比的基础提交")
    parser.add_argument("--head", default="HEAD", help="Git 对比的目标提交（默认 HEAD）")
    args = parser.parse_args(argv)

    paths = args.paths if args.paths else changed_paths(args.base, args.head)
    content_paths = [path for path in paths if is_content_path(path if path.is_absolute() else ROOT / path)]
    if not content_paths:
        print("没有需要检查的教程 Markdown 文件。")
        return 0
    findings = validate_paths(content_paths)
    for finding in findings:
        print(f"ERROR: {finding}")
    if findings:
        print(f"\n检查失败：{len(findings)} 个错误。")
        return 1
    print(f"检查通过：{len(content_paths)} 个教程文件，0 个错误。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
