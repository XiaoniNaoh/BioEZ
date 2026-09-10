# VitePress 课程站（wiki.bioez.xyz）

课程内容由 VitePress 构建，自动发布到香港服务器的 **https://wiki.bioez.xyz/**。

## 日常工作流

1. **在 Obsidian 里写笔记**（就在本仓库，课程文件夹下）。
2. 用 **GitHub Desktop** 提交并 push 到 `main`。
3. GitHub Actions 自动运行 `Deploy BioEZ Wiki (VitePress)`：构建 VitePress → 部署到香港服务器。

无需在本地做任何构建，push 完等一两分钟即可在 <https://wiki.bioez.xyz/> 看到更新。

## 结构

```
vitepress/
├── package.json                 # VitePress 依赖与脚本
├── .vitepress/
│   ├── config.mts               # 站点配置；侧栏从 data/courses.json 自动生成
│   └── theme/custom.css         # 淡雅鼠尾草绿主题
├── scripts/stage.mjs            # 把课程内容暂存为 VitePress 源（content/）
└── content/                     # 构建时生成，不进仓库
```

- 侧栏不需要手工维护：新增/移动笔记后，先跑 `python3 scripts/build_course_catalog.py` 重新生成 `data/courses.json`，侧栏会随之更新。
- 页面导航（上一篇/课程目录/下一篇）来自笔记里自动生成的导航块。
- 图片用相对路径引用（如 `![说明](<图片目录/x.png>)`），构建时会一并处理。

## 本地预览（可选）

```bash
cd vitepress
npm install
npm run dev      # 本地开发预览
npm run build    # 本地构建
```

> 本地安装会在 `vitepress/node_modules/` 生成依赖，已被 `.gitignore` 忽略。
> 若 Obsidian 变卡，可在 Obsidian 设置里把 `vitepress/node_modules` 加入「排除的文件」。

## 部署细节

- 构建产物：`vitepress/.vitepress/dist`
- 服务器目录：`/opt/1panel/apps/openresty/openresty/www/sites/wiki.bioez.xyz/`
- CI 通过 GitHub Secrets 里的 `WIKI_SSH_HOST` / `WIKI_SSH_USER` / `WIKI_SSH_KEY` 登录服务器部署。
- 服务器为直连（灰云、绕过 Cloudflare），HTTPS 用 Let's Encrypt 证书。

## 与 Quartz 并行

两条发布流水线互不影响，push 到 `main` 时同时触发，共用同一份课程内容与 `data/courses.json`：

| 流水线 | Workflow | 发布目标 |
| --- | --- | --- |
| Quartz（原有） | `.github/workflows/quartz-pages.yml` | GitHub Pages：<https://xiaoninaoh.github.io/BioEZ/> |
| VitePress（新增） | `.github/workflows/vitepress-deploy.yml` | 香港服务器：<https://wiki.bioez.xyz/> |

定位：Quartz 面向公开的开源阅读（GitHub Pages，数字花园），VitePress 面向自有站点的 wiki。
写一次笔记，两条线同时更新。
