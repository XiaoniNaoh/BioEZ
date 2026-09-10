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

// 课程入口的相对路径（含 .md），以及编码后的站点路由（空格/中文需转义，否则 Markdown 链接解析失败）
const indexPath = (c) => c.index_path || `${c.directory}/COURSE_INDEX.md`
const route = (p) => encodeURI('/' + p.replace(/\.md$/, ''))

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
    return `  - icon: 📘\n    title: ${c.title}\n    details: ${(c.description || '').replace(/\n/g, ' ')}\n    link: ${route(indexPath(c))}`
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
  tagline: 面向生物相关课程的中文学习资料库，按课程分册，提供稳定的目录与前后篇导航。
  actions:
    - theme: brand
      text: 开始学习
      link: /courses
    - theme: alt
      text: 关于
      link: /about
features:
${features}
---

## 这是什么

覆盖食品分析与检验、微生物学、分子生物学、细胞生物学、植物学、生物化学与食品化学、生信入门等课程。
正文含公式、图表与示例，适合考研复习与日常自学。每门课有独立的课程目录页作为入口。
`,
)

writeFileSync(
  join(CONTENT, 'courses.md'),
  `# 全部课程

${courses
  .map(
    (c, i) =>
      `## ${i + 1}. ${c.title}\n\n${c.description || ''}\n\n- 篇数：${c.lesson_count ?? (c.lessons?.length ?? 0)}　·　预计阅读：${c.estimated_minutes ?? '?'} 分钟\n- [进入课程 →](${route(indexPath(c))})\n`,
  )
  .join('\n')}
`,
)

writeFileSync(
  join(CONTENT, 'about.md'),
  `# 关于 BioEZ

面向生物相关课程的中文学习资料库。内容以 Markdown 写成，按课程分册，遵循 CC BY-SA 4.0 许可开放。

- 在线版：<https://wiki.bioez.xyz/>
- 许可：CC BY-SA 4.0
`,
)

console.log(`已暂存 ${copied} 门课程到 content/`)
