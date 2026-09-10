# 贡献指南

BioEZ 是一套中文生物类课程笔记，正文用 Markdown 写，目录和站点由脚本与 CI 自动生成。欢迎纠错、补内容、改进配图或工程。

---

## 一、文章风格

目标是**好读、好查**，不是正式教材。写的时候照着下面这几条来，风格就会统一：

**结构**

- 标题写在正文最上面：`# 微生物学 章节一：绪论`（课程名 + 章节号 + 小节名）。
- 标题下面紧跟一行标签，用 `#` 连写：`#微生物学 #食品 #科学史 #绪论`。
- 小节用编号层级：`## 1.1 微生物学基本概念`、`### 1.2.1 微生物的特点`。
- 开头常有一句口语化的引入，比如 `> 这是这个系列的第一章~`，让读者知道从哪开始。
- 大段落之间用一行 `---` 分隔。

**文字**

- 说人话。抽象概念先给比喻或场景，再上定义和公式。
- 专业词第一次出现时给出中英对照：`微生物 microbe, microorganism`。
- 关键处用粗体强调：**必须借助显微镜**。
- 用 Obsidian / GitHub 的提示框写补充信息：`> [!NOTE]`、`> [!TIP]`、`> [!WARNING]`、`> [!CAUTION]`（正文里最常用的是 NOTE 和 TIP）。

**排版**

- 表格、公式（`$$ … $$`）、代码块都可以用，公式需要行内写 `$ … $`。
- 图片用相对路径，并且**必须写有意义的 alt**：`![三个变量的散点图矩阵](../assets/generated/scatterplot-matrix.svg)`。
- 每页顶部有一段「课程导航」（`<!-- BEGIN AUTO-GENERATED NAVIGATION -->`），**由脚本生成，不要手改**。

## 二、文件命名惯例

命名规则不是装饰，脚本靠它推导课程、章节和排序，写错会直接报错。

**课程目录**

```text
01 食品分析与检验/
02 微生物学/
03 分子生物学/
04 细胞生物学/
05 植物学/
06 生物化学与食品化学/
07 LLM 时代的生信入门/
```

目录名是「两位序号 + 空格 + 课程名」。**01–07 是已发布课程**；`08`、`09` 目前是未发布模块，先不进仓库、也不上站。

**文件名**

统一格式：`前缀 编号 标题.md`，三者缺一不可。

```text
MB 01 绪论.md
FAI SP1 专题一：水分分析.md          # SP = 专题
MMB 06-2 乳糖操纵子与负控诱导系统.md   # 章-节
BOT A-1 植物的细胞.md                # A 篇第 1 讲
```

各课程前缀一一对应（定义在 `data/course-config.json`）：

| 课程 | 前缀 |
| --- | --- |
| 食品分析与检验 | `FAI` |
| 微生物学 | `MB` |
| 分子生物学 | `MMB` |
| 细胞生物学 | `CB` |
| 植物学 | `BOT` |
| 生物化学与食品化学 | `BC` |
| LLM 时代的生信入门 | `BIF` |

**内容多的课程，用二级目录分章**

```text
03 分子生物学/
├── COURSE_INDEX.md
└── MMB 02 染色体与DNA/
    ├── MMB 02-1 染色体.md
    └── MMB 02-2 DNA 的结构.md
```

目录名 = `前缀 章号 章名`，子文件名 = `前缀 章-节 标题.md`。

**每门课根目录的 `COURSE_INDEX.md`** 是课程入口，同样由脚本生成，不要手改。

## 三、如何贡献

### 只是想报个错

直接在 [Issues](https://github.com/XiaoniNaoh/BioEZ/issues) 里说：哪一篇、哪一句、为什么不对。能给出处（教材、论文、标准）最好。

### 想直接改（最简单的方式，不用装任何东西）

1. 在 GitHub 上打开要改的那个 `.md` 文件。
2. 点右上角的**铅笔图标**开始编辑。
3. 改完拉到下面，写一句说明，点 **Commit changes**——GitHub 会自动帮你 Fork 一份并提交。
4. 回到仓库首页，会出现 **Compare & pull request** 按钮，点它，填一句话说明，提交即可。

### 想认真写一篇（本地方式）

1. Fork 本仓库，然后 `git clone` 到你自己的电脑。
2. 用 **Obsidian** 打开仓库根目录（推荐），或者 Typora / VS Code。
3. 新建或修改文章，**命名按第二节的规则**。
4. 提交：

   ```bash
   git add "02 微生物学/MB 12 新的小节.md"
   git commit -m "content(MB): 新增微生物与抗生素一节"
   git push
   ```

5. 回到 GitHub 发起 Pull Request。

### 提交信息怎么写

一句话够用，格式是 `类型: 说明`。类型用这几个：

| 类型 | 用在 |
| --- | --- |
| `content` | 新增或修订正文 |
| `fix` | 修正错误 |
| `docs` | 文档、贡献指南 |
| `style` | 样式、主题、排版 |
| `chore` | 杂项（重命名、生成文件等） |

例子：`content(MB 05): 补全微生物生长曲线一节`、`fix(BC 2-2): 修正水分活度数值`。

### 几条约定

- **一个小改动就是一次提交**，一个 PR 只做一件事，别把不相干的东西混在一起。
- 不用自己跑脚本，CI 会检查。**但如果新增、改名或移动了课程/文件，请先跑一遍第五节的命令**，否则 CI 会失败。
- 提交前先看一眼自己改的段落读起来顺不顺——这比格式更重要。

## 四、对 AI 的限制

AI 是工具，不是作者。

**可以用**

- 打草稿、整理结构、润色表达、翻译、写代码。
- 让它帮你检查有没有前后矛盾、术语不一致。

**不可以**

- 把 AI 生成的内容**未经核对**就当成事实提交。
- 在页面开头放「AI 生成摘要 / 主要内容 / 知识点 / 评级」这类块。**本站曾有一批这样的页首块，已全部移除**，请不要再加。
- 用 AI 的名字充当作者或审校记录。
- 让 AI 编造引用、数据、图片出处。查不到出处的，就不要写。

**必须做**

- 自己核对事实、引用和版权。
- 在 PR 描述里说明：用了哪个模型、用它做了什么、人工核对到什么程度。

---

## 五、进阶：BioEZ 是怎么跑起来的

这一节给想改脚本、改站点或接手维护的人。

### 5.1 一份内容，两个站点

所有内容只有一份，就是各课程目录里的 Markdown。它会被发布到两个地方：

| 站点 | 构建方式 | 地址 |
| --- | --- | --- |
| 课程地图（数字花园） | Quartz | <https://xiaoninaoh.github.io/BioEZ/> |
| 课程 Wiki | VitePress | <https://wiki.bioez.xyz/> |

两条流水线互相独立，push 到 `main` 会同时触发，互不影响。

### 5.2 内容管线（脚本）

**唯一的人工数据源**是 `data/course-config.json`：课程 slug、标题、目录名、前缀、简介、进度、作者都记在这里。

由脚本生成、**不要手工编辑**的东西：

- 每门课的 `COURSE_INDEX.md`
- 每页顶部的「课程导航」块
- README 里的课程清单
- `data/courses.json`（汇总清单，两个站点都用它）
- `data/quality-report.json`（资源检查报告）

脚本分工：

| 脚本 | 作用 |
| --- | --- |
| `scripts/course_catalog.py` | 共享库：解析 frontmatter、校验命名、推导默认元数据、序列化回文件 |
| `scripts/migrate_course_metadata.py` | 给老页面**补**缺失的 frontmatter 字段（只补缺，不覆盖已有值） |
| `scripts/build_course_catalog.py` | 生成目录、课程清单、页面导航；`--check` 只检查是否有漂移 |
| `scripts/validate_content.py` | 校验 frontmatter 与页面 ID 关系；支持 `--all` / `--paths` / `--base --head` |
| `scripts/check_content_resources.py` | 检查链接、图片、图片来源与孤立页；`--json-report` 写报告，`--check-report` 查漂移 |
| `scripts/build_image_manifest.py` | 维护 `assets/image-sources.json` 图片清单 |
| `scripts/generate_teaching_figures.py` | 生成/校验可复现的教学 SVG 图 |
| `scripts/check_repository_hygiene.py` | 仓库规范（大文件、二进制、许可） |
| `scripts/build_quartz_site.mjs` | 构建 Quartz 站点（下面详解） |

常规流程：

```bash
python3 scripts/migrate_course_metadata.py      # 新页面补元数据
python3 scripts/build_course_catalog.py         # 生成目录/清单/导航
python3 scripts/validate_content.py --all       # 校验元数据
python3 scripts/build_course_catalog.py --check # 确认没有生成漂移
python3 scripts/check_content_resources.py --json-report data/quality-report.json
```

> 目录改名后若没同步 `data/course-config.json`，构建会**直接报错**——这是刻意的，避免发出"缺了几门课"的站点。

### 5.3 Quartz → GitHub Pages

入口是 `scripts/build_quartz_site.mjs`，它做的事：

1. 把**固定版本**的 Quartz（`v4.5.2`，commit `4923affa7722dfc751f1074348e6dad214fe0c08`）clone 到 `.cache/quartz-v4.5.2`，并校验 commit 一致，保证构建可复现。
2. 用仓库里的覆盖文件替换 Quartz 默认配置：
   - `site/quartz.config.ts`（站点名、主题、字体等）
   - `site/quartz.layout.ts`（页面布局）
   - `site/components/BioEZDataViews.tsx`（首页数据视图组件）
   - `site/styles/bioez-data-views.scss`（对应样式）
3. 把课程目录、`assets/`、`资料卡与图库/` 和 `site/pages/` 拷进 `.cache/site-content`，作为站点内容源。
4. 在 Quartz 目录里 `npm ci`，然后执行 `quartz/bootstrap-cli.mjs build --directory .cache/site-content --output public`。
5. 产物落在 `public/`（已被 `.gitignore` 忽略，不进仓库）。

CI 在 `.github/workflows/quartz-pages.yml`：push 到 `main` 后安装 Node 22 / Python 3.12 → 先跑资源质量报告 → `node scripts/build_quartz_site.mjs --check` → 用 `actions/upload-pages-artifact` 上传 `public/` → `actions/deploy-pages@v4` 发布到 GitHub Pages。

本地复现：

```bash
node scripts/build_quartz_site.mjs                 # 构建到 public/
node scripts/build_quartz_site.mjs --check         # 额外跑 Quartz 自带检查
node scripts/build_quartz_site.mjs --serve         # 本地起服务预览
QUARTZ_OUTPUT_DIR=/tmp/quartz-out node scripts/build_quartz_site.mjs   # 换输出目录
```

### 5.4 VitePress → wiki.bioez.xyz

VitePress 工程在 `vitepress/`。

**`vitepress/scripts/stage.mjs`（准备内容）**

- 读 `data/courses.json`，把每门课的目录、`assets/`、`资料卡与图库/` 拷进 `vitepress/content/`（每次构建先清空重建）。
- 生成首页 `index.md`（hero + 每门课一张卡片，卡片图标由脚本里的 `ICONS` 表按 slug 决定）、`courses.md`（全部课程列表）和 `about.md`（关于本站）。
- **课程目录缺失时直接报错退出**，避免静默发出残缺站点。

**`vitepress/.vitepress/config.mts`（站点配置）**

- 侧栏完全由 `data/courses.json` 生成：课程层可折叠（只有当前这门自动展开），章节层（如 `MMB 02 染色体与DNA`）也可折叠。
- 链接会做 URL 编码，避免中文/空格路径的链接失效。
- 站点文案（导航、搜索、页脚、语言）都在这里。

**`vitepress/.vitepress/theme/custom.css`（主题）**

- 只改主色与少量呼应（当前主色是薄荷绿 `#4DCBA0`），字体、字间距、行距等**排版全部沿用 VitePress 默认**。

**常用命令**（在 `vitepress/` 目录下执行）

```bash
npm install        # 首次安装依赖
npm run dev        # 本地开发预览
npm run build      # 构建：先 stage 再 vitepress build，产物在 .vitepress/dist
npm run preview    # 预览构建结果
npm run stage      # 只跑内容暂存，不构建
```

**CI 与部署**（`.github/workflows/vitepress-deploy.yml`）

1. `npm install` → `npm run build`（在 `vitepress/` 下）。
2. 把 `.vitepress/dist` 打成压缩包。
3. 用 SSH 上传到服务器，解包到 `/opt/1panel/apps/openresty/openresty/www/sites/wiki.bioez.xyz`（保留 `ssl/`、`log/`），修权限。
4. `docker exec 1Panel-openresty-YVEg /usr/local/openresty/nginx/sbin/nginx -s reload` 重载 OpenResty。

凭据存在仓库 Secrets：`WIKI_SSH_HOST`、`WIKI_SSH_USER`、`WIKI_SSH_KEY`。站点是**直连**（DNS 灰云、绕过 Cloudflare），HTTPS 用 Let's Encrypt 证书。

> 注意：`vitepress/content/` 是构建产物（已被 `.gitignore` 忽略）。资源检查脚本也把 `vitepress/` 排除在外，避免把这份副本当成正文重复统计。

### 5.5 CI 都会跑什么

| 工作流 | 触发 | 做什么 |
| --- | --- | --- |
| `content-quality.yml` | push `main`；相关文件的 PR | `validate_content.py --all` 校验元数据 |
| `content-resources.yml` | push `main`；相关文件的 PR | 图片清单漂移、教学图可复现性、链接与图片检查 |
| `repository-hygiene.yml` | push `main`；所有 PR | 仓库规范（大文件、二进制、许可） |
| `quartz-pages.yml` | push `main`（PR 时只构建、不发布） | 构建并发布 Quartz 到 GitHub Pages |
| `vitepress-deploy.yml` | push `main` | 构建并发布 VitePress 到 wiki.bioez.xyz |

### 5.6 进阶贡献可以改什么

- **改文章样式**：`vitepress/.vitepress/theme/custom.css`（VitePress 侧）、`site/styles/bioez-data-views.scss`（Quartz 侧）。
- **改首页**：`vitepress/scripts/stage.mjs` 里生成 `index.md` 的模板；课程图标映射是文件开头的 `ICONS`。
- **改侧栏规则**：`vitepress/.vitepress/config.mts`。
- **新增/改名课程**：先改 `data/course-config.json`，再按 5.2 的命令跑一遍并提交生成物。
- **改校验规则**：动 `scripts/*.py` 时请**先补 `tests/` 下的测试**，再跑：

  ```bash
  python3 -m unittest discover -s tests -v
  ```

## 许可证

本项目采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可。提交贡献即表示你同意自己的贡献以同一许可发布。
