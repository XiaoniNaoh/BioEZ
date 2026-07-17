# 仓库资源与版权政策

BioEZ 的 Git 仓库是教程源文件库，不是教材、课件或通用网盘。仓库的 CC BY-SA 4.0 许可证只覆盖 BioEZ 有权授权的内容，不会自动覆盖第三方教材。

## 本次清理的范围

- 从当前版本删除 `00 参考资料/` 中 49 本未附公开再分发授权的完整教材 PDF，合计约 1.71 GiB。
- 删除 `.obsidian/workspace.json`；它是个人界面状态，还保留了已删教材的本地记录。
- 删除仓库中打包的 `.obsidian/plugins/`；插件应由 Obsidian 自行安装和更新，教程不依赖这些插件语法。

教程正文、README 和课程索引均未链接上述 49 个 PDF，因此删除不会造成已知的内容断链。

## 可接受的资源

- 原创或具有明确兼容许可证的 Markdown、SVG 和压缩图片。
- 完成课程所需的小型、可复现数据，同时提供来源、许可证、生成方法和校验和。
- 参考文献的 DOI、PMID、ISBN、出版社或图书馆链接，而不是未授权全文。

## 不应进入 Git 的资源

- 无明确再分发授权的教材、扫描件、课件和付费内容。
- PDF 等可由 Markdown 或其他源文件重建的导出物。需要下载版时应使用 GitHub Releases。
- Obsidian 工作区状态、缓存和打包的第三方插件。

## 自动门禁

`scripts/check_repository_hygiene.py` 对 PR 新增或修改的文件执行以下规则：

| 规则 | 限制 |
| --- | --- |
| 教材目录 | 禁止 `00 参考资料/` |
| PDF | 禁止加入或更新；改用 Release 资产 |
| Obsidian 本地状态 | 禁止 `workspace*.json` 和 `.obsidian/plugins/` |
| 图片 | 单文件最大 2 MiB |
| 其他文件 | 单文件最大 5 MiB |

门禁是增量的，不会因未触碰的历史资产阻断 PR。原有三份项目 PDF 导出物已迁移到 [`content-assets-v1`](https://github.com/XiaoniNaoh/BioEZ/releases/tag/content-assets-v1) Release；PBMC3k 数据改为从 10x Genomics 官方源下载并执行 SHA-256 校验，详见 [PBMC3k 数据说明](datasets/pbmc3k.md)。

## Git 历史

普通删除提交只会缩小当前源码树和 GitHub 源码压缩包，旧提交仍会保留教材 blob，完整 clone 仍需下载它们。需在独立维护窗口按 [Git 历史清理手册](history-cleanup-runbook.md) 重写历史。
