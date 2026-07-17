#!/usr/bin/env python3
"""Shared helpers for BioEZ course metadata and generated catalogs."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:  # Support both direct script execution and package-style unit-test imports.
    from scripts.validate_content import REQUIRED_FIELDS, parse_frontmatter
except ModuleNotFoundError:  # pragma: no cover - exercised by direct CLI execution
    from validate_content import REQUIRED_FIELDS, parse_frontmatter


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path("data/course-config.json")
CATALOG_PATH = Path("data/courses.json")
INDEX_NAME = "COURSE_INDEX.md"
NAV_START = "<!-- BEGIN AUTO-GENERATED NAVIGATION -->"
NAV_END = "<!-- END AUTO-GENERATED NAVIGATION -->"
README_START = "<!-- BEGIN AUTO-GENERATED COURSE CATALOG -->"
README_END = "<!-- END AUTO-GENERATED COURSE CATALOG -->"


@dataclass(frozen=True)
class Course:
    slug: str
    title: str
    directory: str
    prefix: str
    description: str
    progress: str
    authors: tuple[str, ...]
    audience: tuple[str, ...]


@dataclass
class Lesson:
    path: Path
    course: Course
    metadata: dict[str, Any]
    body: str


def load_courses(root: Path = ROOT) -> list[Course]:
    data = json.loads((root / CONFIG_PATH).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("courses"), list):
        raise ValueError(f"{CONFIG_PATH} 必须使用 schema_version 1 并包含 courses 列表")
    courses: list[Course] = []
    for item in data["courses"]:
        courses.append(Course(
            slug=item["slug"],
            title=item["title"],
            directory=item["directory"],
            prefix=item["prefix"],
            description=item["description"],
            progress=item["progress"],
            authors=tuple(item["authors"]),
            audience=tuple(item["audience"]),
        ))
    if len({course.slug for course in courses}) != len(courses):
        raise ValueError("course-config.json 中的课程 slug 必须唯一")
    return courses


def is_lesson_path(path: Path) -> bool:
    """Return whether a Markdown file is course content rather than scaffolding."""
    if path.suffix.lower() != ".md":
        return False
    name = path.name
    return (
        "模板" not in name
        and "一本全" not in name
        and name != INDEX_NAME
    )


def discover_lesson_paths(root: Path, course: Course) -> list[Path]:
    directory = root / course.directory
    if not directory.is_dir():
        raise ValueError(f"课程目录不存在：{course.directory}")
    return sorted(path for path in directory.rglob("*.md") if is_lesson_path(path))


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Return parsed frontmatter and the byte-equivalent Markdown body."""
    normalized = text.lstrip("\ufeff")
    if not normalized.startswith("---\n") and not normalized.startswith("---\r\n"):
        return None, text.lstrip("\ufeff")
    match = re.match(r"\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)", normalized, re.DOTALL)
    if not match:
        raise ValueError("Frontmatter 缺少结束分隔符 ---")
    metadata, error = parse_frontmatter(normalized)
    if error:
        raise ValueError(error)
    return metadata, normalized[match.end():]


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def render_frontmatter(metadata: dict[str, Any]) -> str:
    """Serialize the schema's small, deterministic YAML subset."""
    keys = list(REQUIRED_FIELDS) + sorted(set(metadata) - set(REQUIRED_FIELDS))
    lines = ["---"]
    for key in keys:
        if key not in metadata:
            continue
        value = metadata[key]
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                lines.extend(f"  - {yaml_scalar(item)}" for item in value)
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def filename_parts(path: Path, course: Course) -> tuple[str, str]:
    stem = path.stem
    prefix = f"{course.prefix} "
    if not stem.startswith(prefix):
        raise ValueError(f"文件名必须以 {prefix!r} 开头：{path}")
    remainder = stem[len(prefix):].strip()
    token, separator, title = remainder.partition(" ")
    if not separator or not title.strip():
        raise ValueError(f"文件名必须同时包含顺序编号和标题：{path}")
    return token, title.strip()


def normalize_token(token: str) -> str:
    pieces = re.findall(r"[A-Za-z]+|\d+", token)
    if not pieces:
        raise ValueError(f"无法识别课程顺序编号：{token}")
    return "-".join(piece.lower() if piece.isalpha() else f"{int(piece):02d}" for piece in pieces)


def chapter_for(path: Path, course: Course, order: str) -> str:
    first = order.split("-", 1)[0]
    if course.slug == "food-analysis":
        return "分析专题" if first == "sp" else "分析基础"
    if course.slug == "microbiology":
        return "课程正文"
    if course.slug == "molecular-biology":
        parent = path.parent.name
        parent = re.sub(r"^MMB\s+(?:\d+|SP)\s*", "", parent, flags=re.IGNORECASE)
        parent = parent.replace("染色体与DNA", "染色体与 DNA")
        return parent or "课程正文"
    if course.slug == "cell-biology":
        return "课程正文"
    if course.slug == "botany":
        return f"{first.upper()} 篇"
    if course.slug == "biochemistry-food-chemistry":
        return {
            "01": "蛋白质",
            "02": "水",
            "03": "糖类",
            "04": "脂质",
            "05": "酶",
            "06": "核酸",
            "07": "糖代谢",
            "sp": "专题",
        }.get(first, "课程正文")
    if course.slug == "bioinformatics":
        return "scRNAseq 实操" if first == "b" else "单细胞分析"
    return "课程正文"


def extract_tags(body: str, course: Course) -> list[str]:
    tags: list[str] = []
    for line in body.splitlines()[:80]:
        for tag in re.findall(r"(?<!\S)#([^#\s]+)", line):
            clean = tag.rstrip("，。；、,:;!！?？")
            if clean and clean not in tags:
                tags.append(clean)
    return tags or [course.title]


def extract_rating(body: str, label: str, symbol: str, default: int = 3) -> int:
    match = re.search(rf"{re.escape(label)}[^\n]*?({re.escape(symbol)}+)", body)
    return min(5, len(match.group(1))) if match else default


def estimate_minutes(body: str) -> int:
    text = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    units = len(re.findall(r"[\u3400-\u9fff]", text)) + len(re.findall(r"[A-Za-z0-9]+", text))
    return max(5, math.ceil(units / 250))


def default_metadata(path: Path, course: Course, body: str) -> dict[str, Any]:
    token, title = filename_parts(path, course)
    order = normalize_token(token)
    content_type = "course-index" if "目录与更新计划" in path.name else "lesson"
    return {
        "id": f"{course.prefix.lower()}-{order}",
        "title": title,
        "course": course.slug,
        "chapter": "课程导航" if content_type == "course-index" else chapter_for(path, course, order),
        "order": order,
        "status": "scientific-review",
        "audience": list(course.audience),
        "difficulty": extract_rating(body, "难度", "🌿"),
        "importance": extract_rating(body, "重要性", "🌟"),
        "estimated_minutes": estimate_minutes(body),
        "prerequisites": [],
        "next": [],
        "tags": extract_tags(body, course),
        "authors": list(course.authors),
        "reviewers": [],
        "last_scientific_review": None,
        "summary": f"介绍《{course.title}》中的“{title}”主题。",
        "references": [],
        "content_type": content_type,
    }


def natural_order(value: Any) -> tuple[tuple[int, Any], ...]:
    parts = re.findall(r"[A-Za-z]+|\d+", str(value))
    return tuple((0, int(part)) if part.isdigit() else (1, part.casefold()) for part in parts)


def parse_lessons(root: Path = ROOT) -> list[Lesson]:
    lessons: list[Lesson] = []
    for course in load_courses(root):
        for path in discover_lesson_paths(root, course):
            metadata, body = split_frontmatter(path.read_text(encoding="utf-8"))
            if metadata is None:
                raise ValueError(f"缺少 Frontmatter：{path.relative_to(root)}")
            lessons.append(Lesson(path=path, course=course, metadata=metadata, body=body))
    return lessons


def lessons_by_course(lessons: Iterable[Lesson]) -> dict[str, list[Lesson]]:
    grouped: dict[str, list[Lesson]] = {}
    for lesson in lessons:
        grouped.setdefault(lesson.course.slug, []).append(lesson)
    for items in grouped.values():
        items.sort(key=lambda lesson: (natural_order(lesson.metadata.get("order", "")), lesson.path.as_posix()))
    return grouped
