#!/usr/bin/env python3
"""Download the official 10x Genomics PBMC3k matrix with SHA-256 checks."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import BinaryIO, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "07 LLM 时代的生信入门" / "scRNAseq 入门-数据"
URL = "https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz"
ARCHIVE_SHA256 = "847d6ebd9a1ec9a768f2be7e40ca42cbfe75ebeb6d76a4c24167041699dc28b5"
ARCHIVE_MEMBERS = {
    "filtered_gene_bc_matrices/hg19/matrix.mtx": (
        "matrix.mtx",
        "7d92358b9d29128a225c50f2a662d6ccca9c71bc665e0af82692ed1361eb94e4",
    ),
    "filtered_gene_bc_matrices/hg19/genes.tsv": (
        "genes.tsv",
        "8778dd78085086be6dcafa8334f95f7cf76b25526e8ef2b63186db5127a1492c",
    ),
    "filtered_gene_bc_matrices/hg19/barcodes.tsv": (
        "barcodes.tsv",
        "58c2a224a2b4258f7e8799a18890bda6d23824b247b80db2b08a0dcc36a4c660",
    ),
}
EXPECTED_FILES = {destination: digest for destination, digest in ARCHIVE_MEMBERS.values()}


def sha256_stream(stream: BinaryIO, destination: BinaryIO | None = None) -> str:
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
        if destination is not None:
            destination.write(chunk)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    with path.open("rb") as source:
        return sha256_stream(source)


def verify_files(directory: Path, expected: Mapping[str, str] = EXPECTED_FILES) -> list[str]:
    errors: list[str] = []
    for name, expected_digest in expected.items():
        path = directory / name
        if not path.is_file():
            errors.append(f"{name}: 缺失")
        elif (actual := sha256_file(path)) != expected_digest:
            errors.append(f"{name}: SHA-256 不匹配（{actual}）")
    return errors


def download_archive(destination: Path, url: str = URL) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "BioEZ-data-fetcher/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output, length=1024 * 1024)


def extract_verified(
    archive: Path,
    output: Path,
    members: Mapping[str, tuple[str, str]] = ARCHIVE_MEMBERS,
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as bundle:
        available = {member.name: member for member in bundle.getmembers()}
        missing = sorted(set(members) - set(available))
        if missing:
            raise ValueError(f"压缩包缺少文件: {', '.join(missing)}")
        for archive_name, (destination_name, expected_digest) in members.items():
            member = available[archive_name]
            if not member.isfile():
                raise ValueError(f"{archive_name} 不是普通文件")
            source = bundle.extractfile(member)
            if source is None:
                raise ValueError(f"无法读取 {archive_name}")
            destination = output / destination_name
            temporary = output / f".{destination_name}.tmp"
            with source, temporary.open("wb") as target:
                actual_digest = sha256_stream(source, target)
            if actual_digest != expected_digest:
                temporary.unlink(missing_ok=True)
                raise ValueError(f"{archive_name} SHA-256 不匹配: {actual_digest}")
            temporary.replace(destination)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="解压目录")
    parser.add_argument("--archive", type=Path, help="使用已下载压缩包，不访问网络")
    parser.add_argument("--force", action="store_true", help="即使现有文件通过校验也重新解压")
    args = parser.parse_args(argv)

    if not args.force and not verify_files(args.output):
        print(f"PBMC3k 数据已存在且校验通过: {args.output}")
        return 0

    temporary_archive: Path | None = None
    try:
        if args.archive:
            archive = args.archive.expanduser().resolve()
        else:
            handle = tempfile.NamedTemporaryFile(prefix="pbmc3k-", suffix=".tar.gz", delete=False)
            handle.close()
            temporary_archive = Path(handle.name)
            print(f"正在从 10x Genomics 下载: {URL}")
            download_archive(temporary_archive)
            archive = temporary_archive
        actual_archive_digest = sha256_file(archive)
        if actual_archive_digest != ARCHIVE_SHA256:
            print(f"ERROR: 压缩包 SHA-256 不匹配: {actual_archive_digest}", file=sys.stderr)
            return 1
        extract_verified(archive, args.output)
        errors = verify_files(args.output)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"PBMC3k 已下载并校验通过: {args.output}")
        return 0
    except (OSError, tarfile.TarError, urllib.error.URLError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if temporary_archive is not None:
            temporary_archive.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
