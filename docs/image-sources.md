# 图像来源与许可记录

机器可读的逐文件记录位于 [`assets/image-sources.json`](../assets/image-sources.json)，由 [`scripts/build_image_manifest.py`](../scripts/build_image_manifest.py) 生成。清单不包含时间戳，因此在资产未变化时输出稳定。

## 幕布热链的处理

原教程引用了 11 个幕布图像 URL，但 URL 未提供可核验的作者和再分发许可。本仓库**不保存这些原图的副本**，而是用项目自制的可复现 SVG 替换。旧 URL 只作为“替换了哪个热链”的审计记录，不是新 SVG 的内容来源。

| 项目自制图 | 替换的旧热链 | 生成器 | 许可 |
|---|---|---|---|
| `amino-acid-structure.svg` | `095e…a383.png` | `generate_teaching_figures.py` | CC BY-SA 4.0 |
| `carbohydrate-catabolism.svg` | `9eea…a7a.jpg` | 同上 | CC BY-SA 4.0 |
| `boxplot-anatomy.svg` | `890d…04035.png` | 同上 | CC BY-SA 4.0 |
| `boxplot-examples.svg` | `a30a…827bd.png` | 同上 | CC BY-SA 4.0 |
| `histogram-example.svg` | `f878…73f98.png` | 同上 | CC BY-SA 4.0 |
| `scatterplot-example.svg` | `f2be…0534cd.png` | 同上 | CC BY-SA 4.0 |
| `scatterplot-matrix.svg` | `3f3b…5a74.png` | 同上 | CC BY-SA 4.0 |
| `cluster-marker-heatmap.svg` | `1be6…e6.png` | 同上 | CC BY-SA 4.0 |
| `multi-group-heatmap.svg` | `9165…9c.png` | 同上 | CC BY-SA 4.0 |
| `clinical-expression-heatmap.svg` | `7946…0b.png` | 同上 | CC BY-SA 4.0 |
| `volcano-plot-anatomy.svg` | `03fb…008.png` | 同上 | CC BY-SA 4.0 |

所有 SVG 内部都包含可访问的 `<title>`/`<desc>` 和 CC BY-SA 4.0 元数据。生成器使用固定种子 `20260717`，不需要第三方 Python 包。

## 仓库既有的 20 张 scRNAseq 截图

这 20 张 PNG 在本次整理前已存在于项目仓库，但原仓库没有记录原始作者、捕获日期和生成脚本。清单对此如实记录为：

- `source_type: existing-project-asset`
- `custody_status: existing-in-project-repository`
- `origin_status: unknown`
- `license: not-asserted`

它们现已全部用于 `BIF B-2 scRNAseq 入门到 UMAP 注释.md`，每张图都有替代文本和教学解读。“已被引用”不等于“已确认来源”；后续如果无法补齐来源，应优先用保留分析代码新生成的图替换。

## 复现与漂移检查

从仓库根目录运行：

```bash
python3 scripts/generate_teaching_figures.py --check
python3 scripts/build_image_manifest.py --check
python3 scripts/check_content_resources.py
```

第一条检查 11 个 SVG 是否与生成器字节级一致；第二条检查清单与当前文件 SHA-256 是否一致；第三条检查链接、图像替代文本、远程图像、未引用资产和孤立页。
