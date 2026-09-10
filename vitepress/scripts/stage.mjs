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

// 课程图标统一维护在 data/course-config.json 的 icon 字段（首页卡片、侧栏、课程列表共用）
const courseConfig = existsSync(join(DATA, 'course-config.json'))
  ? JSON.parse(readFileSync(join(DATA, 'course-config.json'), 'utf8')).courses ?? []
  : []
const COURSE_ICONS = Object.fromEntries(courseConfig.map((c) => [c.slug, c.icon ?? '📘']))

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
    const icon = COURSE_ICONS[c.slug] ?? '📘'
    const desc = (c.description || '').replace(/\n/g, ' ')
    return `  - icon: ${icon}\n    title: ${c.title}\n    details: ${desc}（${n} 篇 · 约 ${mins} 分钟）\n    link: ${route(indexPath(c))}`
  })
  .join('\n')

writeFileSync(
  join(CONTENT, 'index.md'),
  `---
layout: home
title: BioEZ · 生物学宝宝教程
titleTemplate: false
hero:
  name: BioEZ
  text: 生物学宝宝教程
  tagline: 面向生物相关课程的中文学习资料库 —— 按课程分册，配好目录与前后篇导航。
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

## 从这里开始

1. **选一门课** —— 点上面任意一张卡片，或浏览 [全部课程](/courses)
2. **按目录读** —— 每门课都有一份「课程目录」，顺着读即可
3. **跟着导航走** —— 每页顶部都有「上一篇 · 课程目录 · 下一篇」

> [!TIP]
> 内容持续更新。右上角可切换深色 / 浅色，长时间阅读更舒服。
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
      const icon = c.icon ?? COURSE_ICONS[c.slug] ?? '📘'
      return `## ${i + 1}. ${icon} ${c.title} ${badge}\n\n${c.description || ''}\n\n- 篇数：${c.lesson_count ?? (c.lessons?.length ?? 0)}　·　预计阅读：${c.estimated_minutes ?? '?'} 分钟\n- [进入课程 →](${route(indexPath(c))})\n`
    },
  )
  .join('\n')}
`,
)

writeFileSync(
  join(CONTENT, 'about.md'),
  `# 关于本站

这是小倪整理的一套生物类课程笔记：课堂讲义、复习提纲，还有平时自己做的一些整理。原先都放在 Obsidian 里，现在一并搬到网上，自己随时能翻，也方便同学和同好直接用。

## 都有什么

${courses.map((c) => `- **${c.title}**：${(c.description || '').replace(/\\n/g, ' ')}`).join('\n')}

每门课都有一份独立的「课程目录」，写明了几篇、大概要读多久、先后顺序怎么排。可以顺着读，也可以挑感兴趣的章节跳着看。

## 怎么用

- 从首页卡片或顶部「全部课程」进入任意一门课；
- 每页顶部都有「上一篇 · 课程目录 · 下一篇」，顺着往下翻就行；
- 右上角能切换深色和浅色，晚上看字不刺眼。

## 关于更新

内容一直在补，也一直在改。有些篇目是早先整理的，后面会陆续回看和修订。要是发现哪里写错、或者讲得不清楚，欢迎到仓库提 Issue，也欢迎直接提交修改。

## 谁在维护

这套笔记由两个人一起整理，分工与联系方式见[团队页面](/team)。

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

writeFileSync(
  join(CONTENT, 'team.md'),
  `---
layout: page
---

<script setup>
import { VPTeamPage, VPTeamPageTitle, VPTeamMembers } from 'vitepress/theme'

const members = ${JSON.stringify(teamMembers, null, 2)}
</script>

<VPTeamPage>
  <VPTeamPageTitle>
    <template #title>关于我们</template>
    <template #lead>
      BioEZ 是一套中文生物类课程笔记，由两个人协作完成。
    </template>
  </VPTeamPageTitle>

  <VPTeamMembers size="medium" :members="members" />
</VPTeamPage>
`,
)

console.log(`已暂存 ${copied} 门课程到 content/`)
