# BioEZ

<pre><center>
   ___       _                ___      ____
  | _ )     (_)      ___     | __|    |_  /
  | _ \     | |     / _ \    | _|      / /
  |___/    _|_|_    \___/    |___|    /___|
_|"""""| _|"""""| _|"""""| _|"""""| _|"""""|
"`-0-0-' "`-0-0-' "`-0-0-' "`-0-0-' "`-0-0-'
</pre></center>

面向生物相关课程的中文学习资料库。内容用 Markdown 写成，按课程分册，提供稳定的目录与前后篇导航，遵循 CC BY-SA 4.0 许可开放。在线版由 Quartz 构建并部署到 GitHub Pages。

## 这是什么

- 覆盖食品分析与检验、微生物学、分子生物学、植物学、生物化学与食品化学、生信入门等课程。
- 正文含公式、图表与示例，适合考研复习和日常自学。
- 每门课有独立的 `COURSE_INDEX.md` 作为入口，便于按章节阅读。

## 怎么用

**在线浏览**：<https://xiaoninaoh.github.io/BioEZ/>

**本地阅读**：

```bash
git clone https://github.com/XiaoniNaoh/BioEZ.git
```

用 Obsidian 或 Typora 打开仓库根目录即可。想快速定位内容，从各课程的 `COURSE_INDEX.md` 进入，或用下方的「内容目录」。

## 内容目录

<!-- BEGIN AUTO-GENERATED COURSE CATALOG -->
<!-- 此区域由 scripts/build_course_catalog.py 自动生成，请勿手工编辑。 -->

课程页均提供稳定目录与前后篇导航。历史正文正在逐篇科学审校，页面状态以元数据为准。

### 🎊 已完成教程

- **[食品分析与检验 宝宝教程](<01 食品分析与检验 宝宝教程/COURSE_INDEX.md>)** — 7 篇 · 预计 40 分钟 · 作者：小倪
  从食品分析的基本原理出发，介绍样品、数据处理与常见成分分析方法。

- **[微生物学 宝宝教程](<02 微生物学 宝宝教程/COURSE_INDEX.md>)** — 11 篇 · 预计 1 小时 19 分钟 · 作者：小倪
  介绍微生物学基础、遗传代谢、生态、免疫与食品相关应用。

- **[分子生物学 重蓝点手册](<03 分子生物学 重蓝点手册/COURSE_INDEX.md>)** — 37 篇 · 预计 4 小时 20 分钟 · 作者：小倪
  围绕 DNA、RNA、蛋白质、基因表达调控和分子生物学技术构建系统学习路径。

### ✍️ 正在连载教程

- **[五年本科 三年细胞（科普）](<04 五年本科 三年细胞 （科普）/COURSE_INDEX.md>)** — 1 篇 · 预计 10 分钟 · 作者：小倪
  以科普方式介绍细胞的结构、功能和生命活动。

- **[植物学 步步糕大一轮复习讲义](<05 植物学 步步糕大一轮复习讲义/COURSE_INDEX.md>)** — 3 篇 · 预计 38 分钟 · 作者：小倪
  面向植物学入门与复习，梳理植物细胞、组织及后续主题。

- **[生物化学与食品化学 考研帮帮忙](<06 生物化学与食品化学 考研帮帮忙/COURSE_INDEX.md>)** — 23 篇 · 预计 2 小时 2 分钟 · 作者：脆弱的百里橘、小倪
  围绕生物化学与食品化学的核心知识点提供考研复习材料。

- **[LLM 时代的生信入门](<07 LLM 时代的生信入门/COURSE_INDEX.md>)** — 7 篇 · 预计 47 分钟 · 作者：脆弱的百里橘
  以单细胞分析为主线，介绍生物信息学数据准备、分析与可视化。

<!-- END AUTO-GENERATED COURSE CATALOG -->

## 如何贡献

欢迎通过 Pull Request 补充、修订或校正内容。

1. Fork 本仓库。
2. 新建分支，例如 `git checkout -b add-xxx`。
3. 修改后推送分支并提交 Pull Request。
4. 若改动涉及课程列表、导航或顺序，请先本地运行以下命令再提交，否则 CI 会失败：
   ```bash
   python3 scripts/build_course_catalog.py
   python3 scripts/check_content_resources.py --json-report data/quality-report.json
   ```

## 常见问题

**可以分享或改编这些内容吗？**
可以。按 CC BY-SA 4.0 许可证注明出处即可。

**内容适合谁？**
大多基于大学课程，但用通俗语言讲解，考研复习与自学都适用。

## 许可证

本项目以 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 发布。

BioEZ © 2025 by Xulei Ni & Hongyu Ying

## 联系

- 反馈与建议：GitHub Issues。
- 小倪：nixulei@snnu.edu.cn
- 脆弱的百里橘：Sarster@foxmail.com

## 鸣谢

感谢陕西师范大学食品工程与营养科学学院、河北医科大学、复旦大学与骆莹老师的协助与指正。
