#!/usr/bin/env python3
"""Generate BioEZ course indexes, navigation, README catalog, and JSON manifest."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

try:  # Support both direct script execution and package-style unit-test imports.
    from scripts.course_catalog import (
        CATALOG_PATH,
        INDEX_NAME,
        NAV_END,
        NAV_START,
        README_END,
        README_START,
        ROOT,
        Course,
        Lesson,
        lessons_by_course,
        load_courses,
        parse_lessons,
        render_frontmatter,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised by direct CLI execution
    from course_catalog import (
        CATALOG_PATH,
        INDEX_NAME,
        NAV_END,
        NAV_START,
        README_END,
        README_START,
        ROOT,
        Course,
        Lesson,
        lessons_by_course,
        load_courses,
        parse_lessons,
        render_frontmatter,
    )


LEGACY_NAVIGATION = re.compile(
    r"(?m)^>\s*(?:(?:上一|下一)(?:讲|章|节)链接|前往(?:上一|下一)章)[^\n]*(?:\n|$)"
)
GENERATED_NAVIGATION = re.compile(
    rf"(?:\n*){re.escape(NAV_START)}.*?{re.escape(NAV_END)}(?:\n*)",
    re.DOTALL,
)
STATUS_LABELS = {
    "draft": "草稿",
    "editorial-review": "待编辑审阅",
    "scientific-review": "",
    "published": "已发布",
}


def relative_markdown_path(source: Path, target: Path) -> str:
    return Path(os.path.relpath(target, start=source.parent)).as_posix()


def markdown_link(label: str, destination: str) -> str:
    return f"[{label}](<{destination}>)"


def clean_legacy_navigation(body: str) -> str:
    body = GENERATED_NAVIGATION.sub("\n", body)
    body = LEGACY_NAVIGATION.sub("", body)
    return body.lstrip("\r\n")


def render_navigation(
    lesson: Lesson,
    index_path: Path,
    previous: Lesson | None,
    following: Lesson | None,
) -> str:
    links: list[str] = []
    if previous is not None:
        links.append(markdown_link(
            f"← 上一篇：{previous.metadata['title']}",
            relative_markdown_path(lesson.path, previous.path),
        ))
    links.append(markdown_link("课程目录", relative_markdown_path(lesson.path, index_path)))
    if following is not None:
        links.append(markdown_link(
            f"下一篇：{following.metadata['title']} →",
            relative_markdown_path(lesson.path, following.path),
        ))
    return "\n".join((
        NAV_START,
        "> [!NOTE] 课程导航",
        f"> {' · '.join(links)}",
        NAV_END,
    ))


def desired_lesson_text(
    lesson: Lesson,
    index_path: Path,
    previous: Lesson | None,
    following: Lesson | None,
) -> str:
    body = clean_legacy_navigation(lesson.body)
    navigation = render_navigation(lesson, index_path, previous, following)
    return f"{render_frontmatter(lesson.metadata)}\n\n{navigation}\n\n{body}"


def validate_catalog(lessons: list[Lesson], courses: list[Course]) -> None:
    known_courses = {course.slug for course in courses}
    known_ids: dict[str, Lesson] = {}
    for lesson in lessons:
        metadata = lesson.metadata
        missing = [field for field in (
            "id", "title", "course", "chapter", "order", "status", "difficulty",
            "importance", "estimated_minutes", "prerequisites", "next", "content_type",
        ) if field not in metadata]
        if missing:
            raise ValueError(f"{lesson.path.relative_to(ROOT)} 缺少字段：{', '.join(missing)}")
        if metadata["course"] != lesson.course.slug or metadata["course"] not in known_courses:
            raise ValueError(f"{lesson.path.relative_to(ROOT)} 的 course 与所属目录不一致")
        if metadata["content_type"] not in {"lesson", "course-index"}:
            raise ValueError(f"{lesson.path.relative_to(ROOT)} 的 content_type 无效")
        identifier = metadata["id"]
        if identifier in known_ids:
            other = known_ids[identifier].path.relative_to(ROOT)
            raise ValueError(f"重复 id {identifier}：{other} 与 {lesson.path.relative_to(ROOT)}")
        known_ids[identifier] = lesson


def prepare_navigation(grouped: dict[str, list[Lesson]], courses: list[Course], root: Path) -> dict[Path, str]:
    desired: dict[Path, str] = {}
    for course in courses:
        pages = grouped.get(course.slug, [])
        sequence = [page for page in pages if page.metadata["content_type"] == "lesson"]
        position = {page.path: index for index, page in enumerate(sequence)}
        index_path = root / course.directory / INDEX_NAME
        for page in pages:
            if page.path in position:
                index = position[page.path]
                previous = sequence[index - 1] if index else None
                following = sequence[index + 1] if index + 1 < len(sequence) else None
            else:
                previous = following = None
            page.metadata["next"] = [following.metadata["id"]] if following else []
            desired[page.path] = desired_lesson_text(page, index_path, previous, following)
    return desired


def lesson_record(lesson: Lesson, root: Path) -> dict[str, Any]:
    metadata = lesson.metadata
    return {
        "id": metadata["id"],
        "title": metadata["title"],
        "path": lesson.path.relative_to(root).as_posix(),
        "content_type": metadata["content_type"],
        "chapter": metadata["chapter"],
        "order": str(metadata["order"]),
        "status": metadata["status"],
        "difficulty": metadata["difficulty"],
        "importance": metadata["importance"],
        "estimated_minutes": metadata["estimated_minutes"],
        "prerequisites": metadata["prerequisites"],
        "next": metadata["next"],
        "tags": metadata["tags"],
        "authors": metadata["authors"],
        "reviewers": metadata["reviewers"],
        "last_scientific_review": metadata["last_scientific_review"],
        "summary": metadata["summary"],
    }


def catalog_document(grouped: dict[str, list[Lesson]], courses: list[Course], root: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for course in courses:
        pages = grouped.get(course.slug, [])
        lesson_pages = [page for page in pages if page.metadata["content_type"] == "lesson"]
        records.append({
            "slug": course.slug,
            "title": course.title,
            "directory": course.directory,
            "description": course.description,
            "progress": course.progress,
            "authors": list(course.authors),
            "audience": list(course.audience),
            "index_path": f"{course.directory}/{INDEX_NAME}",
            "page_count": len(pages),
            "lesson_count": len(lesson_pages),
            "estimated_minutes": sum(page.metadata["estimated_minutes"] for page in lesson_pages),
            "lessons": [lesson_record(page, root) for page in pages],
        })
    return {
        "schema_version": 1,
        "generated_by": "scripts/build_course_catalog.py",
        "courses": records,
    }


def render_course_index(course: Course, pages: list[Lesson], root: Path) -> str:
    lessons = [page for page in pages if page.metadata["content_type"] == "lesson"]
    route_maps = [page for page in pages if page.metadata["content_type"] == "course-index"]
    minutes = sum(page.metadata["estimated_minutes"] for page in lessons)
    lines = [
        "<!-- 此文件由 scripts/build_course_catalog.py 自动生成，请勿手工编辑。 -->",
        "",
        f"# {course.title}",
        "",
        course.description,
        "",
        f"- 课程进度：{'已完成' if course.progress == 'completed' else '连载中'}",
        f"- 已有正文：{len(lessons)} 篇",
        f"- 预计阅读：{minutes} 分钟",
        f"- 作者：{'、'.join(course.authors)}",
    ]
    if route_maps:
        lines.extend(("", "## 课程路线图", ""))
        for page in route_maps:
            destination = page.path.relative_to(root / course.directory).as_posix()
            lines.append(f"- {markdown_link(page.metadata['title'], destination)}")

    chapters: OrderedDict[str, list[Lesson]] = OrderedDict()
    for page in lessons:
        chapters.setdefault(page.metadata["chapter"], []).append(page)
    lines.extend(("", "## 学习目录"))
    for chapter, chapter_lessons in chapters.items():
        lines.extend(("", f"### {chapter}", ""))
        for number, page in enumerate(chapter_lessons, 1):
            destination = page.path.relative_to(root / course.directory).as_posix()
            status = STATUS_LABELS.get(page.metadata["status"], page.metadata["status"])
            suffix = f" · {status}" if status else ""
            lines.append(
                f"{number}. {markdown_link(page.metadata['title'], destination)} — "
                f"{page.metadata['estimated_minutes']} 分钟 · 难度 {page.metadata['difficulty']}/5{suffix}"
            )
    lines.extend(("", "[返回项目首页](<../README.md>)", ""))
    return "\n".join(lines)


def readable_duration(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} 分钟"
    hours, remainder = divmod(minutes, 60)
    return f"{hours} 小时" if remainder == 0 else f"{hours} 小时 {remainder} 分钟"


def render_readme_catalog(grouped: dict[str, list[Lesson]], courses: list[Course]) -> str:
    lines = [
        README_START,
        "<!-- 此区域由 scripts/build_course_catalog.py 自动生成，请勿手工编辑。 -->",
        "",
        "课程页均提供稳定目录与前后篇导航。",
    ]
    for progress, heading in (("completed", "🎊 已完成教程"), ("serializing", "✍️ 正在连载教程")):
        lines.extend(("", f"### {heading}"))
        for course in courses:
            if course.progress != progress:
                continue
            pages = grouped.get(course.slug, [])
            lessons = [page for page in pages if page.metadata["content_type"] == "lesson"]
            minutes = sum(page.metadata["estimated_minutes"] for page in lessons)
            destination = f"{course.directory}/{INDEX_NAME}"
            lines.extend((
                "",
                f"- **{markdown_link(course.title, destination)}** — "
                f"{len(lessons)} 篇 · 预计 {readable_duration(minutes)} · 作者：{'、'.join(course.authors)}",
                f"  {course.description}",
            ))
    lines.extend(("", README_END))
    return "\n".join(lines)


def update_readme(original: str, catalog: str) -> str:
    if README_START in original and README_END in original:
        pattern = re.compile(rf"{re.escape(README_START)}.*?{re.escape(README_END)}", re.DOTALL)
        return pattern.sub(catalog, original)
    section = re.search(r"(?m)^## 📚 项目目录\s*$", original)
    following = re.search(r"(?m)^## 🌏 更新日志\s*$", original)
    if not section or not following or following.start() <= section.end():
        raise ValueError("README.md 缺少“项目目录”或“更新日志”章节")
    return original[:section.end()] + "\n\n" + catalog + "\n\n" + original[following.start():]


def generated_outputs(root: Path = ROOT) -> dict[Path, str]:
    courses = load_courses(root)
    lessons = parse_lessons(root)
    validate_catalog(lessons, courses)
    grouped = lessons_by_course(lessons)
    outputs = prepare_navigation(grouped, courses, root)

    document = catalog_document(grouped, courses, root)
    outputs[root / CATALOG_PATH] = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    for course in courses:
        outputs[root / course.directory / INDEX_NAME] = render_course_index(
            course, grouped.get(course.slug, []), root,
        )
    readme = root / "README.md"
    outputs[readme] = update_readme(readme.read_text(encoding="utf-8"), render_readme_catalog(grouped, courses))
    return outputs


def build(root: Path = ROOT, *, check: bool = False) -> list[Path]:
    stale: list[Path] = []
    for path, desired in generated_outputs(root).items():
        original = path.read_text(encoding="utf-8") if path.exists() else None
        if original == desired:
            continue
        stale.append(path)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(desired, encoding="utf-8")
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="仅检查生成文件和导航是否为最新")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        stale = build(root, check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if args.check and stale:
        for path in stale:
            print(f"需要重新生成：{path.relative_to(root)}")
        print(f"生成一致性检查失败：{len(stale)} 个文件不是最新状态。")
        return 1
    if args.check:
        print("生成一致性检查通过：课程清单、目录、导航和 README 均为最新。")
    else:
        print(f"生成完成：更新 {len(stale)} 个文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
