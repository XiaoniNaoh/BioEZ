#!/usr/bin/env node
// 把 Obsidian 库中的课程内容暂存到 vitepress/content/，供 VitePress 构建。
// 内容原样保留（中文与空格文件名），与 Quartz 发布保持一致。
import {
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import { dirname, extname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const PROJECT = resolve(HERE, '..') // vitepress/
const REPO = resolve(PROJECT, '..') // 库根目录
const CONTENT = join(PROJECT, 'content')
const DATA = join(REPO, 'data')

const ALLOWED = new Set(['.md', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.avif'])
const SKIP = ['模板', '一本全']

function copyTree(src, dst) {
  for (const entry of readdirSync(src, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue
    if (SKIP.some((s) => entry.name.includes(s))) continue
    const from = join(src, entry.name)
    const to = join(dst, entry.name)
    if (entry.isDirectory()) {
      mkdirSync(to, { recursive: true })
      copyTree(from, to)
    } else if (entry.isFile() && ALLOWED.has(extname(entry.name).toLowerCase())) {
      mkdirSync(dirname(to), { recursive: true })
      cpSync(from, to)
    }
  }
}

const courses = existsSync(join(DATA, 'courses.json'))
  ? JSON.parse(readFileSync(join(DATA, 'courses.json'), 'utf8')).courses ?? []
  : []

const contributors = existsSync(join(DATA, 'contributors.json'))
  ? JSON.parse(readFileSync(join(DATA, 'contributors.json'), 'utf8')).contributors ?? []
  : []

// 团队页用到的图标：内联 SVG，避免浏览器运行时去 api.iconify.design 取图（国内可能取不到）
const ICON_SVG = {
  github:
    '<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><path fill="currentColor" d="M12 .297c-6.63 0-12 5.373-12 12c0 5.303 3.438 9.8 8.205 11.385c.6.113.82-.258.82-.577c0-.285-.01-1.04-.015-2.04c-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729c1.205.084 1.838 1.236 1.838 1.236c1.07 1.835 2.809 1.305 3.495.998c.108-.776.417-1.305.76-1.605c-2.665-.3-5.466-1.332-5.466-5.93c0-1.31.465-2.38 1.235-3.22c-.135-.303-.54-1.523.105-3.176c0 0 1.005-.322 3.3 1.23c.96-.267 1.98-.399 3-.405c1.02.006 2.04.138 3 .405c2.28-1.552 3.285-1.23 3.285-1.23c.645 1.653.24 2.873.12 3.176c.765.84 1.23 1.91 1.23 3.22c0 4.61-2.805 5.625-5.475 5.92c.42.36.81 1.096.81 2.22c0 1.606-.015 2.896-.015 3.286c0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',
  site: '<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20a14.5 14.5 0 0 0 0-20M2 12h20"/></g></svg>',
}

// 课程入口的相对路径（含 .md），以及编码后的站点路由（空格/中文需转义，否则 Markdown 链接解析失败）
const indexPath = (c) => c.index_path || `${c.directory}/COURSE_INDEX.md`
const route = (p) => encodeURI('/' + p.replace(/\.md$/, ''))


// 课程图标：统一的线性 SVG（描边 1.6、跟随 currentColor），替代原来的 emoji
const SVG_OPEN =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
const svg = (inner) => `${SVG_OPEN}${inner}</svg>`
const COURSE_SVG = {
  'food-analysis': svg(
    '<path d="M9 3h6"/><path d="M10 3v5.4L5.7 16.2A3.2 3.2 0 0 0 8.5 21h7a3.2 3.2 0 0 0 2.8-4.8L14 8.4V3"/><path d="M7.3 14.6h9.4"/>',
  ),
  microbiology: svg(
    '<circle cx="12" cy="12" r="6.2"/><path d="M12 5.8V2.8M12 21.2v-3M5.8 12h-3M21.2 12h-3"/><circle cx="10.4" cy="10.6" r="1" fill="currentColor" stroke="none"/><circle cx="13.6" cy="13.4" r="1" fill="currentColor" stroke="none"/>',
  ),
  'molecular-biology': svg(
    '<path d="M8.6 2.8c0 4.6 6.8 5.2 6.8 9.2s-6.8 4.6-6.8 9.2"/><path d="M15.4 2.8c0 4.6-6.8 5.2-6.8 9.2s6.8 4.6 6.8 9.2"/><path d="M9.7 7h4.6M9.3 12h5.4M9.7 17h4.6"/>',
  ),
  'cell-biology': svg(
    '<circle cx="12" cy="12" r="8.4"/><circle cx="10.3" cy="11.2" r="2.9"/><path d="M15.6 16.4c1 .6 2.1.6 3 0"/>',
  ),
  botany: svg(
    '<path d="M20.4 3.6c0 9.2-4.8 14-11 14-2 0-3.6-.6-4.6-1.8C4.8 8.6 10.2 3.6 20.4 3.6z"/><path d="M4.8 20.4c2-4.8 5.4-8.4 10-10.8"/>',
  ),
  'biochemistry-food-chemistry': svg(
    '<path d="M12 2.8l6.2 3.6v7.2L12 17.2l-6.2-3.6V6.4z"/><path d="M12 17.2v1.4"/><circle cx="12" cy="20" r="1.4"/>',
  ),
  bioinformatics: svg(
    '<path d="M4 4.6v14.8h16"/><path d="M8.4 16.6v-5.2M12.4 16.6V9.4M16.4 16.6v-3.4"/>',
  ),
  'food-flavor-chemistry': svg(
    '<path d="M12 3.4c3.5 3.9 5.3 7 5.3 9.5a5.3 5.3 0 0 1-10.6 0c0-2.5 1.8-5.6 5.3-9.5z"/><path d="M9.6 14.2a2.6 2.6 0 0 0 1.6 2"/>',
  ),
}
const courseIcon = (c) => COURSE_SVG[c.slug] ?? ''


rmSync(CONTENT, { recursive: true, force: true })
mkdirSync(CONTENT, { recursive: true })

// 目录改名后若未重新生成 data/courses.json，这里会直接失败，
// 避免静默发布出「只剩几门课」的残缺站点。
const missing = courses.filter((c) => c && c.directory && !existsSync(join(REPO, c.directory)))
if (missing.length > 0) {
  console.error('✖ 以下课程目录不存在（通常是把文件夹改名后，没有重新生成 data/courses.json）：')
  for (const c of missing) console.error(`    - ${c.directory}`)
  console.error('  请先在仓库根目录运行：')
  console.error('    python3 scripts/migrate_course_metadata.py')
  console.error('    python3 scripts/build_course_catalog.py')
  process.exit(1)
}

let copied = 0
for (const c of courses) {
  const dir = join(REPO, c.directory)
  if (existsSync(dir)) {
    copyTree(dir, join(CONTENT, c.directory))
    copied++
  }
}
for (const extra of ['资料卡与图库', 'assets']) {
  const dir = join(REPO, extra)
  if (existsSync(dir)) copyTree(dir, join(CONTENT, extra))
}

const features = courses
  .map((c) => {
    const n = c.lesson_count ?? (c.lessons?.length ?? 0)
    const mins = c.estimated_minutes ?? '?'
    const desc = (c.description || '').replace(/\n/g, ' ')
    return `  - icon: '${courseIcon(c)}'\n    title: ${c.title}\n    details: ${desc}（${n} 篇 · 约 ${mins} 分钟）\n    link: ${route(indexPath(c))}`
  })
  .join('\n')

writeFileSync(
  join(CONTENT, 'index.md'),
  `---
layout: home
title: BioEZ · 生物学宝宝教程
titleTemplate: false
pageClass: aurora-home
hero:
  name: BioEZ
  text: 生物学宝宝教程
  tagline: 适合全年龄段、入口即化的生物、食品背景的知识维基。
  actions:
    - theme: brand
      text: 开始学习
      link: /courses
    - theme: alt
      text: 关于本站
      link: /about
features:
${features}
---

## 这里有什么

几门生物课的笔记，按课程分册整理。每门课有一份课程目录，写着篇数、预计阅读时间和先后顺序；每页顶部有「上一篇 · 课程目录 · 下一篇」，可以顺着读，也可以挑着看。想先看看有哪些课，走[全部课程](/courses)。

> [!TIP]
> 内容还在补，早先整理的篇目会陆续回看修订。右上角可以切换深色和浅色。

## 另一摊

课程以外的东西都写在主站 [bioez.xyz](https://bioez.xyz)。那边没编目录，翻到哪算哪。
`,
)

writeFileSync(
  join(CONTENT, 'courses.md'),
  `# 全部课程

${courses
  .map(
    (c, i) => {
      const done = c.progress === 'completed'
      const badge = done ? '<Badge type="tip" text="已完成" />' : '<Badge type="warning" text="连载中" />'
      return `## ${i + 1}. <span class="course-icon">${courseIcon(c)}</span> ${c.title} ${badge}\n\n${c.description || ''}\n\n- 篇数：${c.lesson_count ?? (c.lessons?.length ?? 0)}　·　预计阅读：${c.estimated_minutes ?? '?'} 分钟\n- [进入课程 →](${route(indexPath(c))})\n`
    },
  )
  .join('\n')}
`,
)

writeFileSync(
  join(CONTENT, 'about.md'),
  `---
title: 关于本站
pageClass: aurora-about
prev: false
next: false
---

# 关于本站

这里是小倪整理的生物类课程笔记，内容是课堂笔记和复习提纲，原先放在 Obsidian 里，现在搬到网上。按课程分册，每页有前后篇导航，可以顺着读，也可以跳着看。

## 都有什么

<div class="aurora-grid">
${courses
  .map((c) => {
    const desc = (c.description || '').replace(/\\n/g, ' ')
    return `  <a class="aurora-chip" href="${route(indexPath(c))}">
    <span class="aurora-chip-icon">${courseIcon(c)}</span>
    <b>${c.title}</b>
    <span class="aurora-chip-desc">${desc}</span>
  </a>`
  })
  .join('\n')}
</div>

每门课另有一份「课程目录」，写明篇数、预计阅读时间和先后顺序。

## 怎么用

<div class="aurora-steps">
  <div class="aurora-step">
    <span class="aurora-step-no">01</span>
    <b>挑一门课</b>
    <p>从首页卡片或顶部「全部课程」进任意一门课。</p>
  </div>
  <div class="aurora-step">
    <span class="aurora-step-no">02</span>
    <b>顺着读</b>
    <p>每页顶部有「上一篇 · 课程目录 · 下一篇」，可以一路翻下去。</p>
  </div>
  <div class="aurora-step">
    <span class="aurora-step-no">03</span>
    <b>换外观</b>
    <p>右上角可以切换深色和浅色，晚上看字不刺眼。</p>
  </div>
</div>

## 关于更新

内容还在补，早先整理的篇目也会陆续回看修订。发现写错或讲得不清楚的地方，可以到仓库提 Issue，或直接提交修改。

## 谁在维护

由两个人一起整理，分工和联系方式见[团队页面](/team)。

## 许可与出处

除特别注明外，本站内容以 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.zh) 许可开放：转载时注明出处，并以相同方式共享即可。

- 仓库：<https://github.com/XiaoniNaoh/BioEZ>
- 在线版：<https://wiki.bioez.xyz/>
`,
)

// 团队页（数据来自 data/contributors.json）
// 头像本地化：从 vitepress/team-avatars/ 拷到 content/public/team/，
// 避免依赖 github.com 的头像（国内经常加载不出来）；没有本地头像时回退到 GitHub。
const AVATAR_DIR = join(PROJECT, 'team-avatars')
const PUBLIC_TEAM = join(CONTENT, 'public', 'team')
mkdirSync(PUBLIC_TEAM, { recursive: true })

// 站点图标（导航 logo、favicon）：放在 vitepress/site-assets/，构建时复制到 public 根目录。
// 本地化保存，不直接引用 bioez.xyz 上的文件，站点之间互不牵连。
const SITE_ASSETS = join(PROJECT, 'site-assets')
const PUBLIC_DIR_ROOT = join(CONTENT, 'public')
if (existsSync(SITE_ASSETS)) {
  mkdirSync(PUBLIC_DIR_ROOT, { recursive: true })
  cpSync(SITE_ASSETS, PUBLIC_DIR_ROOT, {
    recursive: true,
    filter: (src) => !src.split('/').pop().startsWith('.'),
  })
}

const localAvatars = new Set()
for (const c of contributors) {
  const source = join(AVATAR_DIR, `${c.github}.png`)
  if (existsSync(source)) {
    cpSync(source, join(PUBLIC_TEAM, `${c.github}.png`))
    localAvatars.add(c.github)
  }
}

const teamMembers = contributors.map((c) => ({
  avatar: localAvatars.has(c.github) ? `/team/${c.github}.png` : `https://github.com/${c.github}.png`,
  name: c.name,
  title: c.title ?? '',
  desc: c.desc ?? '',
  links: (c.links ?? []).map((l) => ({ icon: { svg: ICON_SVG[l.icon] ?? '' }, link: l.link })),
}))

// 团队页的站点概况：从课程清单里现算，不手写数字
const totalLessons = courses.reduce((n, c) => n + (c.lesson_count ?? (c.lessons?.length ?? 0)), 0)
const totalMinutes = courses.reduce((n, c) => n + (c.estimated_minutes ?? 0), 0)
const totalHours = Math.round(totalMinutes / 60)

writeFileSync(
  join(CONTENT, 'team.md'),
  `---
layout: page
pageClass: aurora-team
---

<script setup>
import { VPTeamPage, VPTeamPageTitle, VPTeamMembers } from 'vitepress/theme'

const members = ${JSON.stringify(teamMembers, null, 2)}
</script>

<VPTeamPage>
  <VPTeamPageTitle>
    <template #title>
      <span class="aurora-kicker">Team</span>
      关于我们
    </template>
    <template #lead>
      BioEZ 的课程笔记由两个人一起整理。
    </template>
  </VPTeamPageTitle>

  <VPTeamMembers size="medium" :members="members" />
</VPTeamPage>

<div class="aurora-extra">
  <div class="aurora-stats">
    <div class="aurora-stat">
      <b>${courses.length}</b>
      <span>门课程</span>
    </div>
    <div class="aurora-stat">
      <b>${totalLessons}</b>
      <span>篇正文</span>
    </div>
    <div class="aurora-stat">
      <b>${totalHours}</b>
      <span>小时阅读量</span>
    </div>
    <div class="aurora-stat">
      <b>2</b>
      <span>套站点</span>
    </div>
  </div>

  <div class="aurora-roles">
    <div class="aurora-role">
      <span class="aurora-role-tag">小倪</span>
      <b>其余课程与本站</b>
      <p>除生信部分以外的课程正文、排版与更新，以及本站（wiki.bioez.xyz）的维护。</p>
    </div>
    <div class="aurora-role">
      <span class="aurora-role-tag">脆弱的百里橘</span>
      <b>生信部分与课程地图</b>
      <p>「LLM 时代的生信入门」部分由他编写；Quartz 课程地图与构建流程也由他搭建。</p>
    </div>
  </div>

  <div class="aurora-cta">
    <div>
      <b>发现错误，或者想补一节？</b>
      <p>仓库开着，Issue 和 Pull Request 都收。</p>
    </div>
    <a href="https://github.com/XiaoniNaoh/BioEZ" target="_blank" rel="noopener">去 GitHub</a>
  </div>

  <p class="aurora-foot">
    课程以外的内容写在<a href="https://bioez.xyz" target="_blank" rel="noopener">主站</a>。
  </p>
</div>
`,
)

console.log(`已暂存 ${copied} 门课程到 content/`)
