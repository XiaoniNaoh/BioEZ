# 贡献指南

BioEZ 是一套中文生物类课程笔记。**你只需要把内容写好、提交**——目录清单、页面导航、两个站点的构建和检查，都由脚本和 CI 自动完成。

**这份指南怎么读**

| 你的情况 | 看这一节 |
| --- | --- |
| 第一次贡献，想跟着做一遍 | **一、从零开始**（用 Obsidian + GitHub Desktop，不用命令行） |
| 想知道提交之后系统做了什么 | **1.9 提交之后会发生什么** |
| 想知道文章怎么写、文件怎么命名 | **二、文章风格**、**三、文件命名** |
| 只是想报个错，不想装软件 | **四、其他贡献方式** |
| 想改脚本、主题、站点配置 | **七、进阶：BioEZ 是怎么跑起来的** |

---

## 一、从零开始：Obsidian + GitHub Desktop

全程只需要两个图形界面软件，**不需要会用命令行**。下面以"第一次贡献"为例走一遍。

### 1.1 要装什么

- **Obsidian**：写文章用。
- **GitHub Desktop**：把改动提交、同步到 GitHub。
- 一个 **GitHub 账号**（免费）。

### 1.2 先把仓库"复制"到你自己的账号（Fork）

打开 <https://github.com/XiaoniNaoh/BioEZ>，点右上角的 **Fork**，得到 `你的用户名/BioEZ`。

> 为什么不能直接改原仓库？因为你没有它的写入权限。Fork 相当于"我复制一份到自己名下改，改好了再申请合并回去"。

### 1.3 把这副本下载到电脑（Clone）

1. 打开 **GitHub Desktop** → 菜单 **File → Clone repository**。
2. 在列表里选 **你 Fork 的那一份**（`你的用户名/BioEZ`）。
3. 选一个本地目录 → 点 **Clone**。

### 1.4 用 Obsidian 打开它

Obsidian → **Open folder as vault** → 选中刚才 Clone 下来的文件夹。

第一次打开会问"是否信任此仓库的作者"，选**信任**（否则一些功能会受限）。

### 1.5 写一篇，或者改一篇

- **改**：直接在 Obsidian 里打开对应文件编辑。
- **新**：按第三节的命名规则新建文件（名字写错后面检查会报错）。
- 内容风格照着第二节来就行。

> Obsidian 会在仓库里建一个 `.obsidian` 文件夹（你自己的界面配置）。它不影响内容，已经在 `.gitignore` 里，不用管它。

### 1.6 提交前：跑一次「准备提交」

文章写好后，还有几件小事需要工具帮忙：给文章补上元数据、在开头插入「课程导航」、更新课程目录。

**这些不会自动发生**——GitHub 和 Quartz 都只会**读**你的笔记，不会**回写**你的文件。所以提交前先跑一次准备脚本，两种方式随你挑：

**方式一：双击运行（macOS，推荐）**

在仓库根目录双击 **`准备提交.command`**。会弹出一个终端窗口，自动跑完并把结果显示出来，按任意键关闭。

**方式二：终端命令**

```bash
cd "/Users/naohinc./档案馆/6 代码/BioEZ"      # 换成你自己的 clone 路径
python3 scripts/prepare_contribution.py
```

它会依次做这几件事：

| 步骤 | 作用 |
| --- | --- |
| 补齐元数据 | 给没写 frontmatter 的文章补上（只补缺，**不覆盖**你已经写好的） |
| 生成导航与目录 | 把「课程导航」块写进文章，同时更新 `COURSE_INDEX.md`、课程清单与 README |
| 刷新图片清单与质量报告 | 免得 CI 因为"报告过期"而失败 |
| 跑一遍检查 | 元数据、生成一致性、教学图、链接与图片、单元测试，有问题一次性告诉你 |

看到 **`全部完成 ✓`** 就可以提交了；如果显示 **`有步骤没通过`**，按提示改好再跑一次。

> 它**不写正文**，也**不替你提交**：正文还是在 Obsidian 里写，Commit / Push 还是在 GitHub Desktop 里点。

### 1.7 提交并推送（commit → push）

回到 **GitHub Desktop**：

1. 左侧会列出你改了哪些文件（点一下能看具体改了什么）。
2. 左下角的 **Summary** 里写一句话说明（格式见第五节）。
3. 点 **Commit to main** —— 这一步叫 **commit（提交）**，把改动记进本地的历史。
4. 点顶部 **Push origin** —— 这一步叫 **push（推送）**，把本地提交送到 GitHub 上。

> commit 和 push 的区别：commit 是"在本机存档"，push 是"把这个存档上传到 GitHub"。只 commit 不 push，别人看不到。

### 1.8 发起合并请求（Pull Request）

Push 完成后，GitHub Desktop 会提示 **Create Pull Request**（或 **Preview Pull Request**），点它会在浏览器里打开一个页面：

1. 填一句说明：你改了什么、为什么改。
2. 点 **Create pull request** 提交。

这就是 **PR（Pull Request，合并请求）**：你请求维护者把你这份改动合并进正式仓库。

### 1.9 提交之后会发生什么（原理）

维护者点了合并（或者你自己就是维护者）之后，事情全在云端自动发生：

```text
你 push 的改动
      │
      ▼
① GitHub：合并进 main 分支，留下一条历史记录
      │
      ▼
② GitHub Actions（自动检查，约几十秒）
      ├─ 元数据检查：每篇的 frontmatter 是否完整、编号有没有撞车
      ├─ 资源检查：链接是否有效、图片是否有说明、来源是否记录
      └─ 仓库规范检查：有没有误传大文件、二进制、无授权的素材
      │
      ▼（检查通过后，两条流水线同时开始，互不影响）
      ├─ ③ Quartz   → 重建「课程地图」→ 发布到 GitHub Pages
      └─ ④ VitePress → 重建「课程 Wiki」→ 上传服务器 → 刷新 nginx
      │
      ▼
⑤ 大约 1～2 分钟后，两个站点都更新了
```

**① GitHub 做了什么**

把你的改动合并进 `main` 分支，并记下"谁、什么时候、改了什么"。同时它在云端开一台临时机器跑下面的流程——**你自己的电脑不需要做任何构建**。

**② 自动检查做了什么**

确认每篇笔记的"身份证"（frontmatter：课程、章节、编号、标题、难度、阅读时长等）填全了、编号没重复；确认正文里的链接没指向不存在的文件、图片都有说明文字。哪里不对，PR 上会标红并给出原因，你照着改完再 push 一次就行。

**③ Quartz 做了什么（课程地图）**

Quartz 负责发布到 **GitHub Pages**：

1. 下载一个**固定版本**的 Quartz（`v4.5.2`），保证每次构建结果一致。
2. 套上仓库 `site/` 里的配置（站点名、主题、布局）。
3. 把你的 Markdown 和图片喂进去，生成一整套静态网页。
4. 发布到 <https://xiaoninaoh.github.io/BioEZ/>。

**④ VitePress 做了什么（课程 Wiki）**

VitePress 负责发布到 **wiki.bioez.xyz**：

1. 先把内容整理成站点源码：自动生成首页、全部课程页、关于页，并整理出左侧目录。
2. 编译成静态网站。
3. 打包上传到服务器对应的目录，最后让 nginx 重新加载。
4. 更新 <https://wiki.bioez.xyz/>。

**⑤ 最后你会看到什么**

- 两个站点都更新了，你的文章出现在：首页的课程卡片、左侧按「课程 → 章节 → 文章」分组的目录、以及每页顶部的「上一篇 · 课程目录 · 下一篇」。
- 这些目录和导航**都是脚本自动生成的**，你不需要去别的地方手动补链接。
- 如果检查失败：**两个站点都不会更新**，继续保持上一次正常的样子；修好再推一次即可。

### 1.10 以后每次怎么改

重复这个循环就行：

1. 打开 GitHub Desktop，先点 **Fetch origin**；如果提示落后，点 **Pull**（把别人的新改动同步下来）。
2. 在 Obsidian 里改。
3. 双击 **`准备提交.command`**（或跑一次脚本），看到 `全部完成 ✓`。
4. GitHub Desktop 里 **Commit** → **Push**。
5. 在 GitHub 上开一个新的 Pull Request（GitHub Desktop 会提示入口）。

> 如果你被加成了仓库协作者（有写权限），可以不用 Fork，直接 Clone 原仓库，改完 Push 即可。

---

## 二、文章风格

目标是**好读、好查**，不是正式教材。

**结构**

- 标题写在正文最上面：`# 微生物学 章节一：绪论`（课程名 + 章节号 + 小节名）。
- 标题下面紧跟一行标签：`#微生物学 #食品 #科学史 #绪论`。
- 小节用编号层级：`## 1.1 微生物学基本概念`、`### 1.2.1 微生物的特点`。
- 开头可以有一句口语化的引入，比如 `> 这是这个系列的第一章~`。
- 大段落之间用一行 `---` 分隔。

**文字**

- 说人话。抽象概念先给比喻或场景，再上定义和公式。
- 专业词第一次出现时给出中英对照：`微生物 microbe, microorganism`。
- 关键处用粗体强调：**必须借助显微镜**。
- 用提示框写补充信息：`> [!NOTE]`、`> [!TIP]`、`> [!WARNING]`、`> [!CAUTION]`（最常用 NOTE 和 TIP）。

**排版**

- 表格、公式（`$$ … $$` 或行内 `$ … $`）、代码块都可以用。
- 图片用相对路径，并且**要写有意义的 alt**：`![三个变量的散点图矩阵](../assets/generated/scatterplot-matrix.svg)`。
- 每页顶部的「课程导航」（`<!-- BEGIN AUTO-GENERATED NAVIGATION -->`）是脚本生成的，**不要手改**。

## 三、文件命名

命名不是装饰，脚本靠它推导课程、章节和排序，写错会直接报错。

**课程目录**：`两位序号 + 空格 + 课程名`。

```text
01 食品分析与检验/     02 微生物学/     03 分子生物学/
04 细胞生物学/         05 植物学/       06 生物化学与食品化学/
07 LLM 时代的生信入门/
```

**文件名**：`前缀 编号 标题.md`，三者缺一不可。

```text
MB 01 绪论.md
FAI SP1 专题一：水分分析.md          # SP = 专题
MMB 06-2 乳糖操纵子与负控诱导系统.md   # 章-节
BOT A-1 植物的细胞.md                # A 篇第 1 讲
```

各课程前缀（定义在 `data/course-config.json`）：

| 课程 | 前缀 |
| --- | --- |
| 食品分析与检验 | `FAI` |
| 微生物学 | `MB` |
| 分子生物学 | `MMB` |
| 细胞生物学 | `CB` |
| 植物学 | `BOT` |
| 生物化学与食品化学 | `BC` |
| LLM 时代的生信入门 | `BIF` |

**内容多的课程用二级目录分章**：

```text
03 分子生物学/
├── COURSE_INDEX.md
└── MMB 02 染色体与DNA/
    ├── MMB 02-1 染色体.md
    └── MMB 02-2 DNA 的结构.md
```

目录名是 `前缀 章号 章名`，子文件名是 `前缀 章-节 标题.md`。

另外：每门课根目录的 `COURSE_INDEX.md` 是课程入口，**由脚本生成，不要手改**。`08`、`09` 两个目录是暂不发布的模块，先不要往仓库里加。

## 四、其他贡献方式

**只想报个错**：在 [Issues](https://github.com/XiaoniNaoh/BioEZ/issues) 里说清楚"哪一篇、哪一句、为什么不对"，能给出处（教材、论文、标准）最好。

**不想装软件，只想改几个字**：

1. 在 GitHub 上打开那个 `.md` 文件，点右上角**铅笔图标**。
2. 直接改，拉到底部写一句说明，点 **Commit changes**（GitHub 会自动帮你 Fork 并提交）。
3. 回到仓库首页，点出现的 **Compare & pull request**，填一句说明后提交。

**已经有 Fork 的仓库**：走第一节的 1.10 循环即可。

## 五、提交信息怎么写

一句话够用，格式是 `类型: 说明`：

| 类型 | 用在 |
| --- | --- |
| `content` | 新增或修订正文 |
| `fix` | 修正错误 |
| `docs` | 文档、贡献指南 |
| `style` | 样式、主题、排版 |
| `chore` | 杂项（重命名、生成文件等） |

例子：`content(MB 05): 补全微生物生长曲线一节`、`fix(BC 2-2): 修正水分活度数值`。

再记两条：**一次提交只做一件事**；**提交前先按 1.6 跑一次「准备提交」**，否则新增或改名的文章不会进目录，CI 也会失败。

## 六、对 AI 的限制

AI 是工具，不是作者。

**可以用**：打草稿、整理结构、润色表达、翻译、写代码，或者让它帮你检查前后矛盾和术语不一致。

**不可以**：

- 把 AI 生成的内容**未经核对**就当成事实提交。
- 用 AI 的名字充当作者或审校记录。
- 让 AI 编造引用、数据、图片出处——查不到出处的，就不要写。

**必须做**：自己核对事实、引用和版权；在 PR 描述里说明用了哪个模型、用它做了什么、人工核对到什么程度。

---

## 七、进阶：BioEZ 是怎么跑起来的

这一节给想改脚本、改站点或接手维护的人。

### 7.1 一份内容，两个站点

所有内容只有一份，就是各课程目录里的 Markdown。它会被发布到两个地方：

| 站点 | 构建方式 | 地址 |
| --- | --- | --- |
| 课程地图（数字花园） | Quartz | <https://xiaoninaoh.github.io/BioEZ/> |
| 课程 Wiki | VitePress | <https://wiki.bioez.xyz/> |

两条流水线互相独立，push 到 `main` 会同时触发，互不影响。**如果检查失败，两个站都不会更新**，线上会保持上一次正常的样子。

### 7.2 内容管线（脚本）

**唯一的人工数据源**是 `data/course-config.json`：课程 slug、标题、目录名、前缀、简介、进度、作者都记在这里。

由脚本生成、**不要手工编辑**的东西：每门课的 `COURSE_INDEX.md`、每页顶部的「课程导航」块、README 里的课程清单、`data/courses.json`、`data/quality-report.json`。

脚本分工：

| 脚本 | 作用 |
| --- | --- |
| `scripts/prepare_contribution.py` | **一键准备提交**（就是 1.6 用的那个）：串起下面的迁移与生成步骤，再跑一遍本地检查 |
| `scripts/course_catalog.py` | 共享库：解析 frontmatter、校验命名、推导默认元数据、序列化回文件 |
| `scripts/migrate_course_metadata.py` | 给老页面**补**缺失的 frontmatter 字段（只补缺，不覆盖已有值） |
| `scripts/build_course_catalog.py` | 生成目录、课程清单、页面导航；`--check` 只检查是否有漂移 |
| `scripts/validate_content.py` | 校验 frontmatter 与页面 ID；支持 `--all` / `--paths` / `--base --head` |
| `scripts/check_content_resources.py` | 检查链接、图片、图片来源与孤立页；`--json-report` 写报告，`--check-report` 查漂移，`--show-acknowledged` 查看已确认提醒（默认不列出） |
| `scripts/build_image_manifest.py` | 维护 `assets/image-sources.json` 图片清单 |
| `scripts/generate_teaching_figures.py` | 生成 / 校验可复现的教学 SVG 图 |
| `scripts/check_repository_hygiene.py` | 仓库规范（大文件、二进制、许可） |
| `scripts/build_quartz_site.mjs` | 构建 Quartz 站点（见 7.3） |

日常提交只需要一条命令（就是 1.6 里的那个，它把下面这些串起来跑，并额外刷新图片清单与质量报告）：

```bash
python3 scripts/prepare_contribution.py
```

想手动逐步来，也可以按顺序单独执行：

```bash
python3 scripts/migrate_course_metadata.py      # 新页面补元数据
python3 scripts/build_course_catalog.py         # 生成目录 / 清单 / 导航
python3 scripts/validate_content.py --all       # 校验元数据
python3 scripts/build_course_catalog.py --check # 确认没有生成漂移
python3 scripts/check_content_resources.py --json-report data/quality-report.json
```

> 目录改名后若没同步 `data/course-config.json`，构建会**直接报错**——这是刻意的，避免发出"缺了几门课"的站点。

### 7.3 Quartz → GitHub Pages

入口是 `scripts/build_quartz_site.mjs`，它做的事：

1. 把**固定版本**的 Quartz（`v4.5.2`，commit `4923affa7722dfc751f1074348e6dad214fe0c08`）clone 到 `.cache/quartz-v4.5.2`，并校验 commit 一致，保证构建可复现。
2. 用仓库里的覆盖文件替换 Quartz 默认配置：
   - `site/quartz.config.ts`（站点名、主题、字体）
   - `site/quartz.layout.ts`（页面布局）
   - `site/components/BioEZDataViews.tsx`（首页数据视图组件）
   - `site/styles/bioez-data-views.scss`（对应样式）
3. 把课程目录、`assets/`、`资料卡与图库/` 和 `site/pages/` 拷进 `.cache/site-content`，作为站点内容源。
4. 在 Quartz 目录里 `npm ci`，然后执行 `quartz/bootstrap-cli.mjs build --directory .cache/site-content --output public`。
5. 产物落在 `public/`（已被 `.gitignore` 忽略，不进仓库）。

CI 在 `.github/workflows/quartz-pages.yml`：push 到 `main` 后安装 Node 22 / Python 3.12 → 先跑资源质量报告 → `node scripts/build_quartz_site.mjs --check` → `actions/upload-pages-artifact` 上传 `public/` → `actions/deploy-pages@v4` 发布到 GitHub Pages。（PR 时只构建、不发布。）

本地复现：

```bash
node scripts/build_quartz_site.mjs              # 构建到 public/
node scripts/build_quartz_site.mjs --check      # 额外跑 Quartz 自带检查
node scripts/build_quartz_site.mjs --serve      # 本地起服务预览
QUARTZ_OUTPUT_DIR=/tmp/quartz-out node scripts/build_quartz_site.mjs   # 换输出目录
```

### 7.4 VitePress → wiki.bioez.xyz

工程在 `vitepress/`。

**`vitepress/scripts/stage.mjs`（准备内容）**

- 读 `data/courses.json`，把每门课的目录、`assets/`、`资料卡与图库/` 拷进 `vitepress/content/`（每次构建先清空重建）。
- 生成首页 `index.md`（hero + 每门课一张卡片，卡片图标由脚本里的 `ICONS` 表按 slug 决定）、`courses.md`（全部课程列表）和 `about.md`（关于本站）。
- **课程目录缺失时直接报错退出**，避免静默发出残缺站点。

**`vitepress/.vitepress/config.mts`（站点配置）**

- 侧栏完全由 `data/courses.json` 生成：课程层可折叠（只有当前这门自动展开），章节层（如 `MMB 02 染色体与DNA`）也可折叠。
- 链接会做 URL 编码，避免中文与空格路径的链接失效。
- 导航、搜索、页脚、语言等站点文案都在这里。

**`vitepress/.vitepress/theme/custom.css`（主题）**

- 只改主色与少量呼应（当前主色是薄荷绿 `#4DCBA0`），字体、字间距、行距等**排版沿用 VitePress 默认**。

**常用命令**（在 `vitepress/` 目录下执行）

```bash
npm install        # 首次安装依赖
npm run dev        # 本地开发预览
npm run build      # 构建：先 stage 再 vitepress build，产物在 .vitepress/dist
npm run preview    # 预览构建结果
npm run stage      # 只跑内容暂存，不构建
```

**CI 与部署**（`.github/workflows/vitepress-deploy.yml`）：`npm install` → `npm run build` → 把 `.vitepress/dist` 打成压缩包 → 用 SSH 上传并解包到 `/opt/1panel/apps/openresty/openresty/www/sites/wiki.bioez.xyz`（保留 `ssl/`、`log/`）→ `docker exec 1Panel-openresty-YVEg /usr/local/openresty/nginx/sbin/nginx -s reload` 重载 OpenResty。凭据放在仓库 Secrets：`WIKI_SSH_HOST`、`WIKI_SSH_USER`、`WIKI_SSH_KEY`。站点是**直连**（DNS 灰云、绕过 Cloudflare），HTTPS 用 Let's Encrypt 证书。

> `vitepress/content/` 是构建产物（已被 `.gitignore` 忽略）。资源检查脚本也把 `vitepress/` 排除在外，避免把这份副本当成正文重复统计。

### 7.5 CI 都会跑什么

| 工作流 | 触发 | 做什么 |
| --- | --- | --- |
| `content-quality.yml` | push `main`；相关文件的 PR | `validate_content.py --all` 校验元数据 |
| `content-resources.yml` | push `main`；相关文件的 PR | 图片清单漂移、教学图可复现性、链接与图片检查 |
| `repository-hygiene.yml` | push `main`；所有 PR | 仓库规范（大文件、二进制、许可） |
| `quartz-pages.yml` | push `main`（PR 只构建） | 构建并发布 Quartz 到 GitHub Pages |
| `vitepress-deploy.yml` | push `main` | 构建并发布 VitePress 到 wiki.bioez.xyz |

### 7.6 进阶贡献可以改什么

- **改文章样式**：`vitepress/.vitepress/theme/custom.css`（VitePress 侧）、`site/styles/bioez-data-views.scss`（Quartz 侧）。
- **改首页**：`vitepress/scripts/stage.mjs` 里生成 `index.md` 的模板；课程图标映射是文件开头的 `ICONS`。
- **改侧栏规则**：`vitepress/.vitepress/config.mts`。
- **新增或改名课程**：先改 `data/course-config.json`，再按 7.2 的命令跑一遍并提交生成物。
- **改校验规则**：动 `scripts/*.py` 时请**先补 `tests/` 下的测试**，再跑：

  ```bash
  python3 -m unittest discover -s tests -v
  ```

## 许可证

本项目采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 许可。提交贡献即表示你同意自己的贡献以同一许可发布。
