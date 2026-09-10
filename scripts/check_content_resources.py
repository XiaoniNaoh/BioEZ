#!/usr/bin/env python3
"""Check BioEZ Markdown links, images, orphan pages, and image provenance."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
IGNORED_DIRECTORIES = {
    ".cache",
    ".git",
    ".obsidian",
    ".playwright-cli",
    "node_modules",
    "public",
    # vitepress/ 是站点工程，其 content/ 下是课程正文的构建副本，
    # 不应参与内容资源检查（CI 中也不存在该目录）。
    "vitepress",
    # 08 / 09 为暂不发布模块，仅存在于本地，不参与检查（CI 中也不存在）。
    "08 食品风味化学与分析",
    "09 益生菌",
    "__pycache__",
}
COURSE_DIRECTORY = re.compile(r"^0[1-7] ")
WIKILINK_RE = re.compile(r"(?P<embed>!)?\[\[(?P<target>[^\]\n]+)\]\]")
MARKDOWN_LINK_RE = re.compile(
    r"(?P<image>!)?\[(?P<label>[^\]\n]*)\]\(\s*"
    r"(?P<destination><[^>\n]+>|[^\s)\n]+)"
    r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'))?\s*\)"
)
HTML_IMAGE_RE = re.compile(r"<img\b(?P<attributes>[^>]*)>", re.IGNORECASE)
HTML_ATTRIBUTE_RE = re.compile(
    r"(?P<name>[A-Za-z_:][\w:.-]*)\s*=\s*(?:\"(?P<double>[^\"]*)\"|'(?P<single>[^']*)'|(?P<bare>[^\s>]+))"
)
HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*#*\s*$", re.MULTILINE)
UNINFORMATIVE_ALT = {"", "图", "图片", "截图", "image", "img", "picture"}


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    path: str
    line: int
    message: str
    target: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity,
            "path": self.path,
            "line": self.line,
            "message": self.message,
        }
        if self.target is not None:
            result["target"] = self.target
        return result

    def __str__(self) -> str:
        target = f" [{self.target}]" if self.target else ""
        return f"{self.path}:{self.line}: {self.message}{target}"


# 已确认、长期存在、不影响发布的提醒：默认不出现在输出与报告里，避免每次刷屏。
# 每条都要写清 code 与匹配范围，以及为什么可以忽略；用 --show-acknowledged 可以查看。
ACKNOWLEDGED_FINDINGS: tuple[dict[str, str], ...] = (
    {
        "code": "origin-metadata-missing",
        "path_prefix": "07 LLM 时代的生信入门/scRNAseq 入门-图片/",
        "reason": "仓库既有截图的原始来源待补；已在 assets/image-sources.json 记录 custody_status，未冒充已授权",
    },
    {
        "code": "orphan-page",
        "path": "03 分子生物学/MMB 99 分子生物学｜一本全.md",
        "reason": "「一本全」草稿页，构建时有意排除，不进入课程目录",
    },
)


def is_acknowledged(finding: "Finding") -> bool:
    """该条提醒是否属于「已知且可忽略」。"""
    for rule in ACKNOWLEDGED_FINDINGS:
        if rule.get("code") != finding.code:
            continue
        if "path" in rule and rule["path"] == finding.path:
            return True
        if "path_prefix" in rule and finding.path.startswith(rule["path_prefix"]):
            return True
    return False


@dataclass(frozen=True)
class ScanReport:
    summary: dict[str, int]
    findings: tuple[Finding, ...]
    orphans: tuple[str, ...]
    unreferenced_assets: tuple[str, ...]
    acknowledged: tuple[Finding, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "orphans": list(self.orphans),
            "unreferenced_assets": list(self.unreferenced_assets),
        }


def repository_files(root: Path) -> Iterable[Path]:
    """Yield repository files while pruning application and build directories."""
    for current, directories, filenames in os.walk(root):
        directories[:] = sorted(name for name in directories if name not in IGNORED_DIRECTORIES)
        base = Path(current)
        for filename in sorted(filenames):
            yield base / filename


def _masked(value: str) -> str:
    return "".join("\n" if character == "\n" else " " for character in value)


def mask_code_and_comments(text: str) -> str:
    """Mask code fences, inline code, and comments without changing offsets."""
    output: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence is None and marker:
            fence = marker.group(1)[0]
            output.append(_masked(line))
            continue
        if fence is not None:
            output.append(_masked(line))
            if re.match(rf"^\s*{re.escape(fence)}{{3,}}", line):
                fence = None
            continue
        output.append(line)
    masked = "".join(output)
    masked = re.sub(r"<!--[\s\S]*?-->", lambda match: _masked(match.group(0)), masked)
    masked = re.sub(r"(`+)([^\n]*?)\1", lambda match: _masked(match.group(0)), masked)
    return masked


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def relative_string(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def clean_destination(destination: str) -> str:
    destination = html.unescape(destination.strip())
    if destination.startswith("<") and destination.endswith(">"):
        destination = destination[1:-1]
    return unquote(destination)


def is_remote(destination: str) -> bool:
    return urlsplit(destination).scheme.casefold() in {"http", "https"}


def normalize_alt(label: str) -> str:
    return re.sub(r"[\s\W_]+", "", label, flags=re.UNICODE).casefold()


def has_meaningful_alt(label: str) -> bool:
    return normalize_alt(label) not in UNINFORMATIVE_ALT


def normalized_heading(value: str) -> str:
    value = re.sub(r"[*_`~]", "", value)
    value = re.sub(r"\[([^]]+)]\([^)]*\)", r"\1", value)
    return " ".join(value.split()).casefold()


def headings(path: Path) -> set[str]:
    try:
        text = mask_code_and_comments(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        return set()
    return {normalized_heading(match.group("title")) for match in HEADING_RE.finditer(text)}


def resolve_standard_path(root: Path, source: Path, destination: str) -> Path | None:
    clean = clean_destination(destination)
    if not clean or clean.startswith("#") or is_remote(clean):
        return None
    parsed = urlsplit(clean)
    if parsed.scheme or clean.startswith("//"):
        return None
    raw_path = parsed.path
    if not raw_path:
        return source
    candidates = [root / raw_path.lstrip("/")] if raw_path.startswith("/") else [source.parent / raw_path]
    if not Path(raw_path).suffix:
        candidates.extend(path.with_suffix(".md") for path in tuple(candidates))
    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if resolved.exists():
            return resolved
    return candidates[0].resolve() if candidates else None


def build_name_index(paths: Iterable[Path], root: Path) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    by_stem: dict[str, list[Path]] = {}
    by_relative: dict[str, list[Path]] = {}
    for path in paths:
        by_stem.setdefault(path.stem.casefold(), []).append(path)
        relative = relative_string(path, root)
        keys = {relative.casefold(), str(PurePosixPath(relative).with_suffix("")).casefold()}
        for key in keys:
            by_relative.setdefault(key, []).append(path)
    return by_stem, by_relative


def resolve_wikilink(
    root: Path,
    source: Path,
    target: str,
    by_stem: dict[str, list[Path]],
    by_relative: dict[str, list[Path]],
) -> list[Path]:
    target = unquote(target.strip().replace("\\", "/"))
    if not target:
        return [source]
    relative_key = target.lstrip("/").casefold()
    relative_keys = {relative_key}
    if Path(target).suffix:
        relative_keys.add(str(PurePosixPath(relative_key).with_suffix("")))
    else:
        relative_keys.add(f"{relative_key}.md")
    matches: set[Path] = set()
    for key in relative_keys:
        matches.update(by_relative.get(key, []))

    direct_candidates = [source.parent / target, root / target.lstrip("/")]
    if not Path(target).suffix:
        direct_candidates.extend(path.with_suffix(".md") for path in tuple(direct_candidates))
    for candidate in direct_candidates:
        if candidate.exists():
            matches.add(candidate.resolve())
    if not matches:
        matches.update(by_stem.get(Path(target).stem.casefold(), []))
    return sorted(matches, key=lambda path: relative_string(path, root))


def is_course_page(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if not relative.parts or not COURSE_DIRECTORY.match(relative.parts[0]):
        return False
    if "模板" in path.name or "目录" in path.name or "更新计划" in path.name:
        return False
    return path.suffix.casefold() == ".md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_image_manifest(root: Path, image_assets: set[Path]) -> tuple[list[Finding], int, int]:
    findings: list[Finding] = []
    manifest_path = root / "assets/image-sources.json"
    repository_images = {relative_string(path, root) for path in image_assets}
    if not manifest_path.exists():
        if repository_images:
            findings.append(Finding(
                "missing-image-manifest", "error", "assets/image-sources.json", 1,
                "仓库中有图像，但缺少来源与校验清单",
            ))
        return findings, 0, 0

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [Finding("invalid-image-manifest", "error", "assets/image-sources.json", 1, f"无法读取清单: {exc}")], 0, 0
    entries = data.get("assets") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return [Finding("invalid-image-manifest", "error", "assets/image-sources.json", 1, "assets 必须是数组")], 0, 0

    seen: set[str] = set()
    license_review = 0
    required = {"path", "source_type", "sha256", "license"}
    for index, entry in enumerate(entries, 1):
        line = index + 3
        if not isinstance(entry, dict) or not required.issubset(entry):
            findings.append(Finding("invalid-image-manifest", "error", "assets/image-sources.json", line, f"第 {index} 项缺少必填字段"))
            continue
        relative = str(entry["path"])
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            findings.append(Finding("invalid-image-manifest", "error", "assets/image-sources.json", line, "path 必须是仓库内相对路径", relative))
            continue
        if relative in seen:
            findings.append(Finding("duplicate-image-manifest", "error", "assets/image-sources.json", line, "图像路径在清单中重复", relative))
            continue
        seen.add(relative)
        path = root / relative
        if not path.is_file():
            findings.append(Finding("missing-manifest-asset", "error", "assets/image-sources.json", line, "清单中的图像文件不存在", relative))
        elif not re.fullmatch(r"[0-9a-f]{64}", str(entry["sha256"])):
            findings.append(Finding("invalid-checksum", "error", "assets/image-sources.json", line, "sha256 必须是 64 位小写十六进制字符", relative))
        elif sha256(path) != entry["sha256"]:
            findings.append(Finding("checksum-mismatch", "error", relative, 1, "文件 SHA-256 与来源清单不一致", str(entry["sha256"])))

        source_type = entry["source_type"]
        if source_type == "project-generated":
            generator = entry.get("generated_by")
            if not isinstance(generator, str) or not (root / generator).is_file():
                findings.append(Finding("missing-generator", "error", "assets/image-sources.json", line, "项目自制图缺少可用的 generated_by 脚本", relative))
            if entry["license"] != "CC-BY-SA-4.0":
                findings.append(Finding("invalid-generated-license", "error", "assets/image-sources.json", line, "项目自制图必须明确标记 CC-BY-SA-4.0", relative))
            legacy_url = entry.get("replaces_legacy_url")
            if legacy_url is not None and not is_remote(str(legacy_url)):
                findings.append(Finding("invalid-legacy-url", "error", "assets/image-sources.json", line, "replaces_legacy_url 必须是 HTTP(S) 审计链接", relative))
        elif source_type == "existing-project-asset":
            if entry.get("custody_status") != "existing-in-project-repository" or entry.get("origin_status") != "unknown":
                findings.append(Finding("invalid-origin-record", "error", "assets/image-sources.json", line, "仓库既有图像必须如实记录 custody_status 和 origin_status", relative))
            license_review += 1
            findings.append(Finding("origin-metadata-missing", "warning", relative, 1, "仓库既有截图的原始作者、捕获日期和生成脚本尚未记录"))
        else:
            findings.append(Finding("invalid-source-type", "error", "assets/image-sources.json", line, "source_type 不受支持", relative))

    for relative in sorted(repository_images - seen):
        findings.append(Finding("untracked-image", "error", relative, 1, "图像未记录在 assets/image-sources.json"))
    for relative in sorted(seen - repository_images):
        if not (root / relative).is_file():
            continue
        findings.append(Finding("non-image-manifest-entry", "error", relative, 1, "来源清单条目不是受支持的图像类型"))
    return findings, len(entries), license_review


def scan_repository(root: Path = ROOT) -> ScanReport:
    root = root.resolve()
    all_files = list(repository_files(root))
    markdown_files = [path for path in all_files if path.suffix.casefold() == ".md"]
    image_assets = {path.resolve() for path in all_files if path.suffix.casefold() in IMAGE_SUFFIXES}
    markdown_by_stem, markdown_by_relative = build_name_index(markdown_files, root)
    image_by_stem, image_by_relative = build_name_index(image_assets, root)
    all_by_stem = {key: list(value) for key, value in markdown_by_stem.items()}
    all_by_relative = {key: list(value) for key, value in markdown_by_relative.items()}
    for key, values in image_by_stem.items():
        all_by_stem.setdefault(key, []).extend(values)
    for key, values in image_by_relative.items():
        all_by_relative.setdefault(key, []).extend(values)

    findings: list[Finding] = []
    referenced_images: set[Path] = set()
    course_pages = {path.resolve() for path in markdown_files if is_course_page(path, root)}
    inbound: dict[Path, set[Path]] = {path: set() for path in course_pages}
    heading_cache: dict[Path, set[str]] = {}
    counters = {"wikilinks": 0, "markdown_links": 0, "image_references": 0, "remote_images": 0, "missing_alt": 0}

    for source in markdown_files:
        source = source.resolve()
        source_relative = relative_string(source, root)
        try:
            original = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(Finding("unreadable-markdown", "error", source_relative, 1, f"无法读取 UTF-8 Markdown: {exc}"))
            continue
        text = mask_code_and_comments(original)

        for match in WIKILINK_RE.finditer(text):
            counters["wikilinks"] += 1
            line = line_number(text, match.start())
            raw = match.group("target")
            target_and_alias = raw.split("|", 1)
            target_with_heading = target_and_alias[0].strip()
            alias = target_and_alias[1].strip() if len(target_and_alias) == 2 else ""
            target_name, separator, heading_name = target_with_heading.partition("#")
            candidates = resolve_wikilink(root, source, target_name, all_by_stem, all_by_relative)
            if not candidates:
                findings.append(Finding("broken-wikilink", "error", source_relative, line, "Wikilink 目标不存在", target_with_heading))
                continue
            if len(candidates) > 1:
                choices = ", ".join(relative_string(path, root) for path in candidates)
                findings.append(Finding("ambiguous-wikilink", "error", source_relative, line, f"Wikilink 目标不唯一: {choices}", target_with_heading))
                continue
            target_path = candidates[0].resolve()
            is_image = bool(match.group("embed")) and target_path.suffix.casefold() in IMAGE_SUFFIXES
            if is_image:
                counters["image_references"] += 1
                referenced_images.add(target_path)
                if not has_meaningful_alt(alias):
                    counters["missing_alt"] += 1
                    findings.append(Finding("missing-alt", "error", source_relative, line, "Obsidian 图像嵌入缺少有意义的别名文本", target_with_heading))
            elif target_path in inbound and target_path != source:
                inbound[target_path].add(source)
            if heading_name and target_path.suffix.casefold() == ".md":
                heading_cache.setdefault(target_path, headings(target_path))
                if normalized_heading(heading_name) not in heading_cache[target_path]:
                    findings.append(Finding("broken-heading", "error", source_relative, line, "Wikilink 标题锚点不存在", target_with_heading))

        for match in MARKDOWN_LINK_RE.finditer(text):
            destination = clean_destination(match.group("destination"))
            line = line_number(text, match.start())
            if match.group("image"):
                counters["image_references"] += 1
                label = match.group("label")
                if not has_meaningful_alt(label):
                    counters["missing_alt"] += 1
                    findings.append(Finding("missing-alt", "error", source_relative, line, "Markdown 图像缺少有意义的替代文本", destination))
                if is_remote(destination):
                    counters["remote_images"] += 1
                    findings.append(Finding("remote-image", "error", source_relative, line, "远程图像必须本地化并记录来源", destination))
                    continue
                target_path = resolve_standard_path(root, source, destination)
                if target_path is None or not target_path.is_file():
                    findings.append(Finding("missing-image", "error", source_relative, line, "本地图像不存在", destination))
                elif target_path.suffix.casefold() not in IMAGE_SUFFIXES:
                    findings.append(Finding("invalid-image-target", "error", source_relative, line, "图像语法指向了非图像文件", destination))
                else:
                    referenced_images.add(target_path.resolve())
                continue

            counters["markdown_links"] += 1
            if is_remote(destination) or destination.startswith("#"):
                continue
            parsed = urlsplit(destination)
            if parsed.scheme or destination.startswith("//"):
                continue
            target_path = resolve_standard_path(root, source, destination)
            if target_path is None or not target_path.exists():
                findings.append(Finding("broken-link", "error", source_relative, line, "Markdown 本地链接目标不存在", destination))
            elif target_path.resolve() in inbound and target_path.resolve() != source:
                inbound[target_path.resolve()].add(source)

        for match in HTML_IMAGE_RE.finditer(text):
            line = line_number(text, match.start())
            attributes: dict[str, str] = {}
            for attribute in HTML_ATTRIBUTE_RE.finditer(match.group("attributes")):
                value = attribute.group("double") or attribute.group("single") or attribute.group("bare") or ""
                attributes[attribute.group("name").casefold()] = html.unescape(value)
            destination = attributes.get("src", "")
            counters["image_references"] += 1
            if not has_meaningful_alt(attributes.get("alt", "")):
                counters["missing_alt"] += 1
                findings.append(Finding("missing-alt", "error", source_relative, line, "HTML 图像缺少有意义的 alt", destination or None))
            if is_remote(destination):
                counters["remote_images"] += 1
                findings.append(Finding("remote-image", "error", source_relative, line, "远程 HTML 图像必须本地化并记录来源", destination))
            else:
                target_path = resolve_standard_path(root, source, destination)
                if target_path is None or not target_path.is_file():
                    findings.append(Finding("missing-image", "error", source_relative, line, "HTML 图像目标不存在", destination or None))
                elif target_path.suffix.casefold() in IMAGE_SUFFIXES:
                    referenced_images.add(target_path.resolve())

    unreferenced = tuple(sorted(relative_string(path, root) for path in image_assets - referenced_images))
    for relative in unreferenced:
        findings.append(Finding("unreferenced-asset", "error", relative, 1, "本地图像未被任何 Markdown 页面引用"))

    orphan_paths = tuple(sorted(relative_string(path, root) for path, sources in inbound.items() if not sources))
    for relative in orphan_paths:
        findings.append(Finding("orphan-page", "warning", relative, 1, "教程页没有入站链接，应接入课程目录或学习路径"))

    manifest_findings, manifest_assets, license_review = check_image_manifest(root, image_assets)
    findings.extend(manifest_findings)
    findings.sort(key=lambda item: (item.severity != "error", item.path, item.line, item.code))
    acknowledged = tuple(finding for finding in findings if is_acknowledged(finding))
    findings = [finding for finding in findings if not is_acknowledged(finding)]
    orphan_paths = tuple(finding.path for finding in findings if finding.code == "orphan-page")
    broken_codes = {"broken-link", "broken-wikilink", "broken-heading", "missing-image", "invalid-image-target"}
    summary = {
        "markdown_files": len(markdown_files),
        "wikilinks": counters["wikilinks"],
        "markdown_links": counters["markdown_links"],
        "image_references": counters["image_references"],
        "image_assets": len(image_assets),
        "manifest_assets": manifest_assets,
        "remote_images": counters["remote_images"],
        "missing_alt": counters["missing_alt"],
        "broken_links": sum(finding.code in broken_codes for finding in findings),
        "ambiguous_wikilinks": sum(finding.code == "ambiguous-wikilink" for finding in findings),
        "unreferenced_assets": len(unreferenced),
        "orphan_pages": len(orphan_paths),
        "license_review_required": license_review,
        "errors": sum(finding.severity == "error" for finding in findings),
        "warnings": sum(finding.severity == "warning" for finding in findings),
        "acknowledged": len(acknowledged),
    }
    return ScanReport(summary, tuple(findings), orphan_paths, unreferenced, acknowledged)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="要检查的仓库根目录")
    report_output = parser.add_mutually_exclusive_group()
    report_output.add_argument("--json-report", type=Path, help="写入机器可读 JSON 报告")
    report_output.add_argument("--check-report", type=Path, help="检查已提交 JSON 报告是否漂移")
    parser.add_argument("--strict-orphans", action="store_true", help="将孤立教程页也视为失败")
    parser.add_argument("--show-acknowledged", action="store_true", help="同时列出已知且可忽略的提醒")
    args = parser.parse_args(argv)

    report = scan_repository(args.root)
    serialized = json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"
    if args.json_report:
        report_path = args.json_report if args.json_report.is_absolute() else args.root / args.json_report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(serialized, encoding="utf-8")
    if args.check_report:
        report_path = args.check_report if args.check_report.is_absolute() else args.root / args.check_report
        if not report_path.is_file() or report_path.read_text(encoding="utf-8") != serialized:
            print(f"ERROR: quality report is stale: {report_path}")
            return 1

    for finding in report.findings:
        print(f"{finding.severity.upper()}: {finding}")
    if args.show_acknowledged:
        for finding in report.acknowledged:
            print(f"（已确认）{finding.severity.upper()}: {finding}")
    summary = report.summary
    ignored = summary.get("acknowledged", 0)
    suffix = f"（另有 {ignored} 条已确认提醒，未列出）" if ignored else ""
    print(
        "\n资源检查完成："
        f"{summary['markdown_files']} 个 Markdown，{summary['image_assets']} 个图像资产，"
        f"{summary['errors']} 个错误，{summary['warnings']} 个警告{suffix}。"
    )
    blocking = summary["errors"] > 0 or (args.strict_orphans and summary["orphan_pages"] > 0)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
