# BioEZ Quartz 4 站点

站点采用“固定上游 + 本仓库 overlay”，不把 Quartz 源码、`node_modules` 或构建产物提交进 BioEZ。

## 架构与版本

- 上游：<https://github.com/jackyzha0/quartz>
- 版本：`v4.5.2`
- 固定提交（annotated tag 的 peeled commit）：`4923affa7722dfc751f1074348e6dad214fe0c08`
- 本仓库只维护 `site/` 中的配置、布局、组件、样式和两个生成页面。
- `scripts/build_quartz_site.mjs` 首次构建时把上游浅克隆到 `.cache/quartz-v4.5.2`，校验提交后应用 overlay。

这种方式让上游实现与课程内容解耦；升级 Quartz 时必须同时修改脚本中的版本和提交、重新运行类型检查与完整构建，不能跟随可变分支。

## 本地构建

需要 Node.js 22+、npm 10.9.2+、Git 和网络（仅首次获取 Quartz 与安装依赖）。

```bash
node scripts/build_quartz_site.mjs --check
```

结果写入 `public/`。第一次成功后，可用 `--skip-install` 跳过重复安装；本地预览使用：

```bash
node scripts/build_quartz_site.mjs --skip-install --serve
```

构建脚本只暂存课程目录、资料卡和 Web 图片，明确不发布 PDF、数据集、Obsidian 本地状态、模板和手工聚合的“一本全”。

## 数据契约与降级

首页课程树读取 `data/courses.json`（schema v1），使用 `courses[].directory/index_path/lessons[]`。课程清单缺失或无效时，首页显示明确提示，正文与 Explorer 仍可浏览。

维护看板读取 `data/quality-report.json`（schema v1）：

- `summary`：资源检查器的数值汇总；
- `findings[]`：`code`、`severity`、`path`、`line`、`target`、`message`；
- `generated_at`：可选生成时间。

质量报告缺失时，看板显示降级提示，并继续从课程清单计算“发布状态、难度、重要性、阅读时长、摘要、科学复审”的覆盖热图。JSON 也会作为静态资源发布，便于后续独立前端或 API 使用。

## GitHub Pages

`.github/workflows/quartz-pages.yml` 在 pull request 中只构建，在 `main` 推送时构建并部署。仓库 Settings → Pages 的 Source 需要设为 **GitHub Actions**。

默认 `baseUrl` 是 `XiaoniNaoh.github.io/BioEZ`。若使用 `docs.bioez.xyz`，设置仓库变量 `QUARTZ_BASE_URL=docs.bioez.xyz`，值不带协议或首尾斜杠。

图谱组件默认显示当前页面的一跳局部图；只有用户主动点击时才显示限制为两跳的扩展图。课程树承担主导航，图谱只用于邻近概念探索。
