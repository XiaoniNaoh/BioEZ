# PBMC3k 教学数据

BioEZ 不再将 28 MiB 的解压数据直接存入 Git。运行以下命令会从 10x Genomics 官方地址下载并校验压缩包，然后只解压 Seurat/Read10X 所需的三个文件：

```bash
python3 scripts/download_pbmc3k.py
```

默认输出目录是 `07 LLM 时代的生信入门/scRNAseq 入门-数据/`。

## 来源与许可

- 数据集：[3k PBMCs from a Healthy Donor](https://www.10xgenomics.com/datasets/3-k-pbm-cs-from-a-healthy-donor-1-standard-1-1-0)
- 发布者：10x Genomics
- 许可：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 版本：Cell Ranger 1.1.0，2,700 个检出细胞

官方页面标明该数据集使用 CC BY 4.0。请在教学产物中归因 10x Genomics，并保留上述数据集链接。

## 完整性

下载脚本校验官方压缩包的 SHA-256，并再分别校验 `matrix.mtx`、`genes.tsv` 和 `barcodes.tsv`。机器可读记录见 [`data/assets.json`](../../data/assets.json)。
