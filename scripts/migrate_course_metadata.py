#!/usr/bin/env python3
"""Add schema-compliant Frontmatter to legacy BioEZ course lessons."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:  # Support both direct script execution and package-style unit-test imports.
    from scripts.course_catalog import (
        ROOT,
        default_metadata,
        discover_lesson_paths,
        load_courses,
        render_frontmatter,
        split_frontmatter,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised by direct CLI execution
    from course_catalog import (
        ROOT,
        default_metadata,
        discover_lesson_paths,
        load_courses,
        render_frontmatter,
        split_frontmatter,
    )


def migrate(root: Path = ROOT, *, check: bool = False) -> tuple[int, list[Path]]:
    migrated = 0
    stale: list[Path] = []
    for course in load_courses(root):
        for path in discover_lesson_paths(root, course):
            original = path.read_text(encoding="utf-8")
            metadata, body = split_frontmatter(original)
            if metadata is None:
                metadata = default_metadata(path, course, body)
                desired = f"{render_frontmatter(metadata)}\n\n{body.lstrip(chr(10))}"
                migrated += 1
            else:
                defaults = default_metadata(path, course, body)
                missing = [key for key in defaults if key not in metadata]
                if not missing:
                    continue
                for key in missing:
                    metadata[key] = defaults[key]
                desired = f"{render_frontmatter(metadata)}\n\n{body.lstrip(chr(10))}"
            if desired != original:
                stale.append(path)
                if not check:
                    path.write_text(desired, encoding="utf-8")
    return migrated, stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="仅检查是否仍有页面需要迁移")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    migrated, stale = migrate(args.root.resolve(), check=args.check)
    if args.check and stale:
        for path in stale:
            print(f"需要迁移：{path.relative_to(args.root.resolve())}")
        print(f"检查失败：{len(stale)} 个课程页面缺少完整 Frontmatter。")
        return 1
    if args.check:
        print("迁移检查通过：所有课程页面均包含完整 Frontmatter。")
    else:
        print(f"迁移完成：新增 {migrated} 篇 Frontmatter，更新 {len(stale)} 个文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
