# 贡献指南

BioEZ 是一套中文生物类课程笔记：正文用 Markdown 写，目录与导航由脚本生成，构建和发布交给 CI。欢迎纠错、补充教程、改进配图，或者帮忙修工程问题。

## 可以怎么参与

- **报错**：概念、数据、图注、链接有问题。
- **补正文**：新增一节，或把某段讲得更清楚。
- **出配图与例题**：自制示意图、习题与解答。
- **改工程**：脚本、CI、站点样式。

不确定要不要做，先在 [Issues](https://github.com/XiaoniNaoh/BioEZ/issues) 里说一下即可。

## 先把仓库跑起来

需要 Git 和任意 Markdown 编辑器（Obsidian、Typora、VS Code 都可以）。

```bash
git clone https://github.com/YOUR_USERNAME/BioEZ.git
cd BioEZ
```

直接用 Obsidian 打开仓库根目录就能开始写。想在本地预览站点，见 [VitePress 课程站说明](docs/vitepress-wiki.md)。

## 仓库结构

```text
01 食品分析与检验/ … 07 LLM 时代的生信入门/   # 课程正文，按课程分目录
        └── COURSE_INDEX.md                    # 课程入口（脚本生成，勿手改）
data/course-config.json                        # 课程清单（人工维护：slug / 标题 / 目录 / 前缀 / 简介）
data/courses.json                              # 由脚本汇总生成，勿手改
scripts/                                       # 目录、校验、构建脚本
site/                                          # Quartz 站点配置
vitepress/                                     # VitePress 站点与构建脚本
docs/                                          # 维护者文档
```

> `08 食品风味化学与分析`、`09 益生菌` 目前属于未发布模块，暂不进仓库、也不上站。

## 写正文

- 语言尽量直白；专业词第一次出现时给出解释。
- 新建页面建议从 [教程模板](docs/tutorial-template.md) 起步，并遵循 [Frontmatter 规范](docs/content-frontmatter.md)。
- 每页顶部的「课程导航」、每门课的 `COURSE_INDEX.md`、README 的课程清单和 `data/courses.json` 都由脚本生成，**不要手工编辑**。
- 用 Wikilink 时先确认目标文件存在；能从元数据算出来的信息（篇数、难度、前后篇）不要手抄，让脚本生成。
- 涉及事实的地方，尽量给出教科书、论文、标准或权威数据库的出处。

## 新增、改名或移动课程时

1. 在 `data/course-config.json` 里登记 slug、标题、目录名、前缀与简介。
2. 依次运行：

```bash
python3 scripts/migrate_course_metadata.py      # 补齐并刷新每页 frontmatter
python3 scripts/build_course_catalog.py         # 生成 COURSE_INDEX / README / courses.json / 页面导航
python3 scripts/validate_content.py --all       # 校验 frontmatter 与页面 ID
python3 scripts/build_course_catalog.py --check # 确认生成结果没有漂移
```

> 目录改名后如果没同步 `data/course-config.json`，构建会**直接报错**。这是刻意设计的，免得发出"缺了几门课"的站点。

## 图片、引用与版权

- 只提交自己制作的、公共领域的，或明确允许在 CC BY-SA 4.0 项目中再分发的素材。
- 不要上传未授权的教材全文、扫描件、课件或付费数据库内容；改用 DOI / ISBN / 出版社页面链接。
- 图片要有有意义的 `alt`，图注注明作者、来源链接与许可证；尽量不要热链第三方资源。
- 图片优先用压缩过的 WebP / AVIF / SVG，单张建议小于 2 MB。
- PDF 导出物与大型可复现数据放 GitHub Releases 或可追溯的数据仓库；源码库只保留来源、许可、下载方式与校验和。详见 [仓库资源与版权政策](docs/repository-hygiene.md)。

## 关于 AI 辅助

AI 可以用来打草稿、整理结构和检查表达，但**不能替代作者核对内容**。

- 提交前请自己核对事实、引用与版权。
- 不要在页面开头放"AI 生成摘要"这类块；需要摘要就直接写进正文。
- 用了什么模型、怎么用的，在 PR 描述里说明即可；**AI 的名字不能当作作者或审校记录**。

## 本地检查

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_content.py --all
python3 scripts/build_course_catalog.py --check
python3 scripts/check_content_resources.py
python3 scripts/check_repository_hygiene.py --base origin/main --head HEAD
```

只改了某几篇、还没提交时，可以只校验这几篇：

```bash
python3 scripts/validate_content.py --paths "path/to/tutorial.md"
```

## 提交 Pull Request

1. 从 `main` 开一个分支：`git checkout -b fix/typo-in-mmb-03`
2. 改完后跑一遍上面的检查。
3. 提交并推送，然后开 PR，说明改了什么、为什么改。
4. CI 会自动跑内容校验、资源检查，并构建两个站点。

## 发布到哪里

同一份正文会同时发布到两个地方，互不影响：

| 站点 | 构建方式 | 地址 |
| --- | --- | --- |
| 课程地图（数字花园） | Quartz → GitHub Pages | <https://xiaoninaoh.github.io/BioEZ/> |
| 课程 Wiki | VitePress → 服务器 | <https://wiki.bioez.xyz/> |

## 许可证

本项目采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可。提交贡献即表示你同意自己的贡献以同一许可发布。
