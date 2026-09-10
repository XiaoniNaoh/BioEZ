# Markdown 资源治理报告

本报告记录资源治理基线、处理策略和可重复验证结果。机器可读的当前结果见 [`data/quality-report.json`](../data/quality-report.json)。

## 处理结果

| 检查项 | 基线 | 当前 | 处理 |
|---|---:|---:|---|
| 幕布远程图像 | 11 | 0 | 不再分发许可未知的原图；用 11 个可复现项目自制 SVG 替换 |
| 外部 Icons8 AI 图标 | 31 | 0 | 改为纯文本 AI 辅助说明，不将 AI 辅助与科学审校混同 |
| 图像引用缺少有意义的 alt | 9 | 0 | 为所有图像补充描述性替代文本 |
| 本地图像资产 | 20 | 31 | 保留 20 张既有 scRNAseq 截图，新增 11 个自制 SVG |
| 未引用本地图像 | 20 | 0 | 20 张截图全部接入新的 BIF B-2 实操教程 |
| 断链 / 歧义 Wikilink | 0 | 0 | 全库扫描 Markdown 链接、Wikilink 页面与标题锚点 |
| 孤立教程页 | 29 | 0 | 通过课程清单、自动目录与前后篇导航统一接入 |

## 新教程页

`07 LLM 时代的生信入门/BIF B-2 scRNAseq 入门到 UMAP 注释.md` 按以下分析链路组织了原本未引用的 20 张截图：

```text
R / RStudio 环境
  → Seurat 对象与 QC
  → 标准化与高变基因
  → PCA 与 PC 选择
  → Louvain 聚类与 UMAP
  → Marker 基因与细胞类型注释
```

页面对每个阶段都说明了图像用来检查什么、不能推断什么，并明确截图不能代替数据、代码与 `sessionInfo()`。

## 来源与授权状态

- 11 个替代 SVG 由仓库脚本原始生成，使用 CC BY-SA 4.0，固定种子为 `20260717`。原幕布 URL 只作为热链替换审计记录，原图未进入最终仓库。
- 20 张 scRNAseq PNG 是仓库既有资产。原始作者、捕获日期和生成脚本无记录，因此清单标记为 `origin_status: unknown` 与 `license: not-asserted`，未被伪装成已授权内容。这 20 项属于**已确认提醒**，默认不在检查输出里重复列出（要查看加 `--show-acknowledged`），其状态以 `assets/image-sources.json` 为准。

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 scripts/generate_teaching_figures.py --check
python3 scripts/build_image_manifest.py --check
python3 scripts/check_content_resources.py --check-report data/quality-report.json
```

链接、远程图像、alt、未引用资产、孤立页、来源清单和 SHA-256 使用 Python 标准库检查；CI 不需额外安装依赖。
