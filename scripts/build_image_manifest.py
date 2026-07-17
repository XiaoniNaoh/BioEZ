#!/usr/bin/env python3
"""Build the deterministic image provenance and checksum manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/image-sources.json"
GENERATOR = "scripts/generate_teaching_figures.py"
GENERATOR_SEED = 20260717
SCREENSHOT_DIRECTORY = "07 LLM 时代的生信入门/scRNAseq 入门-图片"

GENERATED_ASSETS = {
    "amino-acid-structure.svg": "https://api2.mubu.com/v3/document_image/095e1d00-9e3b-479a-89fc-29c64ae1a383.png",
    "carbohydrate-catabolism.svg": "https://api2.mubu.com/v3/document_image/9eeaf8e8-0b9b-4144-b404-6be28b611a7a.jpg",
    "boxplot-anatomy.svg": "https://api2.mubu.com/v3/document_image/26905802_890d76fc-fb65-4ac3-c90f-0239fe104035.png",
    "boxplot-examples.svg": "https://api2.mubu.com/v3/document_image/26905802_a30acfff-b968-40e4-948f-3b0a8b5827bd.png",
    "histogram-example.svg": "https://api2.mubu.com/v3/document_image/26905802_f87869fd-4a54-43a6-a0ad-f66f65773f98.png",
    "scatterplot-example.svg": "https://api2.mubu.com/v3/document_image/26905802_f2bea56f-a090-405f-cbb6-51d0520534cd.png",
    "scatterplot-matrix.svg": "https://api2.mubu.com/v3/document_image/26905802_3f3b6f5e-da90-4a5b-fab7-b1b409605a74.png",
    "cluster-marker-heatmap.svg": "https://api2.mubu.com/v3/document_image/26905802_1be653cb-66e6-49ff-d4a8-30a1db2f2365.png",
    "multi-group-heatmap.svg": "https://api2.mubu.com/v3/document_image/26905802_91651ae0-11df-4a2d-dc50-7187bb3adf9c.png",
    "clinical-expression-heatmap.svg": "https://api2.mubu.com/v3/document_image/26905802_794678ec-33e9-4c02-f818-2525eb412d0b.png",
    "volcano-plot-anatomy.svg": "https://api2.mubu.com/v3/document_image/26905802_03fb684e-573b-42a4-c873-036ff7039008.png",
}

EXISTING_SCREENSHOTS = (
    "PCA前5主成分摘要.png",
    "PCA肘部图（确定聚类PC数）.png",
    "PCA降维散点图.png",
    "QC指标小提琴图与散点图.png",
    "RStudio官网.png",
    "RStudio首次启动界面.png",
    "R下载页面.png",
    "R官网首页.png",
    "Seurat对象初始化摘要.png",
    "UMAP初始聚类散点图.png",
    "UMAP细胞类型注释结果.png",
    "UMAP降维过程日志.png",
    "全群Marker基因计算过程.png",
    "前15主成分热图.png",
    "各聚类top15 Marker基因片段.png",
    "数据标准化执行.png",
    "标准化后表达矩阵片段.png",
    "细胞聚类（Louvain算法）过程.png",
    "高变基因散点图（带标签）.png",
    "高变基因计算过程.png",
)


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_manifest() -> dict[str, object]:
    assets: list[dict[str, object]] = []
    for name, legacy_url in GENERATED_ASSETS.items():
        relative = f"assets/generated/{name}"
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        assets.append({
            "path": relative,
            "source_type": "project-generated",
            "generated_by": GENERATOR,
            "generator_seed": GENERATOR_SEED,
            "replaces_legacy_url": legacy_url,
            "sha256": checksum(path),
            "license": "CC-BY-SA-4.0",
        })
    for name in EXISTING_SCREENSHOTS:
        relative = f"{SCREENSHOT_DIRECTORY}/{name}"
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        assets.append({
            "path": relative,
            "source_type": "existing-project-asset",
            "custody_status": "existing-in-project-repository",
            "origin_status": "unknown",
            "sha256": checksum(path),
            "license": "not-asserted",
            "note": "原始作者、捕获日期和生成脚本未在原仓库记录；本次只建立引用与完整性记录。",
        })
    assets.sort(key=lambda entry: str(entry["path"]))
    return {"schema_version": 2, "assets": assets}


def serialized_manifest() -> str:
    return json.dumps(build_manifest(), ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="检查已提交清单是否与当前资产一致")
    args = parser.parse_args(argv)
    expected = serialized_manifest()
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            print(f"ERROR: image manifest is stale: {args.output}")
            return 1
        print("图像来源清单与当前资产一致。")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(f"已更新图像来源清单：{args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
