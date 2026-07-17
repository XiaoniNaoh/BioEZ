#!/usr/bin/env python3
"""Reject newly added repository assets that violate BioEZ hygiene policy."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MIB = 1024 * 1024
MAX_IMAGE_BYTES = 2 * MIB
MAX_FILE_BYTES = 5 * MIB
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}


@dataclass(frozen=True)
class Finding:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def normalize_relative(path: str | Path) -> str:
    normalized = PurePosixPath(str(path).replace("\\", "/")).as_posix()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def check_path(path: Path, relative: str | Path | None = None) -> list[Finding]:
    relative_path = normalize_relative(relative if relative is not None else path.relative_to(ROOT))
    pure = PurePosixPath(relative_path)

    if relative_path == "00 参考资料" or relative_path.startswith("00 参考资料/"):
        return [Finding(relative_path, "禁止将教材或参考资料全文加入源码库")]
    if relative_path.startswith(".obsidian/plugins/"):
        return [Finding(relative_path, "Obsidian 插件必须由应用安装，不在仓库中打包")]
    if pure.parent == PurePosixPath(".obsidian") and pure.name.startswith("workspace") and pure.suffix == ".json":
        return [Finding(relative_path, "Obsidian 个人工作区状态不应进入仓库")]
    if pure.suffix.casefold() == ".pdf":
        return [Finding(relative_path, "PDF 应作为 Release 资产发布，仓库只保留可编辑源文件")]
    if not path.is_file():
        return []

    size = path.stat().st_size
    limit = MAX_IMAGE_BYTES if pure.suffix.casefold() in IMAGE_SUFFIXES else MAX_FILE_BYTES
    if size > limit:
        return [Finding(relative_path, f"文件为 {size / MIB:.2f} MiB，超过 {limit / MIB:.0f} MiB 限制")]
    return []


def changed_paths(base: str, head: str) -> list[tuple[Path, str]]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "-z", "--diff-filter=ACMR", f"{base}...{head}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    relatives = [os.fsdecode(item) for item in result.stdout.split(b"\0") if item]
    return [(ROOT / relative, relative) for relative in relatives]


def validate_paths(paths: Iterable[tuple[Path, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for path, relative in paths:
        findings.extend(check_path(path, relative))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--paths", nargs="+", type=Path, help="要检查的本地文件")
    source.add_argument("--base", help="Git 对比的基础提交")
    parser.add_argument("--head", default="HEAD", help="Git 对比的目标提交（默认 HEAD）")
    args = parser.parse_args(argv)

    if args.paths:
        paths = []
        for path in args.paths:
            absolute = path if path.is_absolute() else ROOT / path
            try:
                relative = str(absolute.relative_to(ROOT))
            except ValueError:
                relative = path.name
            paths.append((absolute, relative))
    else:
        paths = changed_paths(args.base, args.head)

    findings = validate_paths(paths)
    for finding in findings:
        print(f"ERROR: {finding}")
    if findings:
        print(f"\n仓库卫生检查失败：{len(findings)} 个错误。")
        return 1
    print(f"仓库卫生检查通过：{len(paths)} 个新增或修改文件，0 个错误。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
