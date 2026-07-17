# 贡献指南

BioEZ 欢迎错误修正、新教程、图表和工程改进。教程是可公开传播的科学内容，因此可追溯性、版权和审校记录与文字风格同样重要。

## 如何贡献

您可以通过以下方式为 BioEZ 做出贡献：

- 报告教程中的错误或问题。
- 建议新的教程主题或对现有教程的改进。
- 编写新的教程或更新现有教程。
- 改进项目的文档。

## 设置开发环境

要开始贡献，请确保您已经安装了 Git 和一个 Markdown 编辑器（如 Obsidian、Typora 或 Visual Studio Code），然后按照以下步骤操作：

1. 在 GitHub 上 Fork BioEZ 仓库到您的账户。
2. 克隆 Fork 的仓库到本地：
   ```bash
   git clone https://github.com/YOUR_USERNAME/BioEZ.git
   ```
   请将 YOUR_USERNAME 替换为您的 GitHub 用户名。
3. 打开克隆的仓库文件夹，使用 Markdown 编辑器编辑文件。

## 编写与元数据

- 使用清晰、简洁的语言，首次出现的专业词给出定义。
- 新建教程使用 [教程模板](docs/tutorial-template.md)，并遵循 [Frontmatter 规范](docs/content-frontmatter.md)。
- 使用 Obsidian Wikilink 时确保目标文件存在；不要手工复制难度、重要性等可从元数据生成的信息。
- 事实性主张应引用教科书、同行评议论文、标准或权威数据库。

## 科学审校

内容状态依次为 `draft` → `editorial-review` → `scientific-review` → `published`。发布页面必须记录审校者和日期。修改核心结论后，页面应退回 `scientific-review`，直到再次审校。

## 图片、引用与版权

- 仅提交自制资料、公共领域资料，或明确允许在 CC BY-SA 4.0 项目中再分发的素材。
- 不上传未经授权的教材全文、扫描书、课件或付费数据库内容；改用 DOI、ISBN、出版社或图书馆页面。
- 图片必须包含有意义的 `alt` 文本，图注注明作者、来源链接和许可证。避免依赖可失效的第三方热链。
- 优先提交压缩后的 WebP/AVIF/SVG；单张图片建议小于 2 MB。
- PDF 导出物和大型可复现数据应发布到 GitHub Releases 或可追溯的数据仓库，源码库只保留来源、许可、下载方法和校验和。详见 [仓库资源与版权政策](docs/repository-hygiene.md)。

## AI 辅助内容

AI 可用于头脑风暴、结构编辑和草稿，但不能代替科学审校。贡献者必须核对事实、引用和版权，并在 PR 中说明使用的模型、用途和人工复核范围。AI 名称或图标不应被当作审校记录。

## 本地检查

```bash
python3 -m unittest discover -s tests -v
# 检查本次添加或修改的资源
python3 scripts/check_repository_hygiene.py --base origin/main --head HEAD
# 未提交时，显式列出本次修改的教程
python3 scripts/validate_content.py --paths "path/to/tutorial.md"
# 提交后，模拟 PR 的增量检查
python3 scripts/validate_content.py --base origin/main --head HEAD
```

## 提交 Pull Request

提交贡献时，请遵循以下步骤：

1. 在您的 Fork 仓库中创建一个新的分支：
   ```bash
   git checkout -b feature/add-new-tutorial
   ```
2. 在该分支上进行您的更改。
3. 运行内容检查，然后提交更改并编写清晰的提交消息：
   ```bash
   git commit -m 'Add new tutorial: Genetics'
   ```
4. 将您的分支推送到 GitHub：
   ```bash
   git push origin feature/add-new-tutorial
   ```
5. 在 GitHub 上提交一个 Pull Request，描述您的更改和目的。
6. 等待项目维护者的审查和合并。

## 报告问题

如果您发现教程中的错误或有改进建议，请在 [GitHub Issues](https://github.com/XiaoniNaoh/BioEZ/issues) 中提交问题报告。请提供详细的信息，包括问题的描述、复现步骤（如果适用）以及任何相关的截图或文件。

## 建议新功能

如果您有新的教程主题或功能建议，请在 [GitHub Issues](https://github.com/XiaoniNaoh/BioEZ/issues) 中提交建议。请描述您的想法以及它将如何改进项目。

## 许可证

BioEZ 项目采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可证。提交贡献即表示您同意您的贡献也在此许可证下发布。
