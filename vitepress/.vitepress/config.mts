import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitepress'

const courses: any[] = JSON.parse(
  readFileSync(fileURLToPath(new URL('../../data/courses.json', import.meta.url)), 'utf8'),
).courses ?? []

const toLink = (p: string) => '/' + p.replace(/\.md$/, '')

// 用文件名（不含扩展名）作为侧栏文字，保留编制的前缀，如「MB 01 绪论」「MMB 02-1 染色体」
const stem = (p: string) => p.split('/').pop()!.replace(/\.md$/, '')

// 不发布的文件（与 scripts/stage.mjs 的 SKIP 保持一致）
const SKIP = ['模板', '一本全']
const published = (p: string) => !SKIP.some((s) => p.includes(s))

const sidebar = courses
  .filter((c) => c && c.directory)
  .map((c) => {
    const items: any[] = []
    if (c.index_path) items.push({ text: '课程目录', link: toLink(c.index_path) })

    const top: any[] = []
    const groups = new Map<string, any[]>()
    for (const l of (c.lessons ?? []).filter((l: any) => published(l.path))) {
      const prefix = c.directory + '/'
      const rel: string = l.path.startsWith(prefix) ? l.path.slice(prefix.length) : l.path
      const segs = rel.split('/')
      const item = { text: stem(l.path), link: toLink(l.path) }
      if (segs.length > 1) {
        const key = segs[0]
        if (!groups.has(key)) groups.set(key, [])
        groups.get(key)!.push(item)
      } else {
        top.push(item)
      }
    }
    items.push(...top)
    for (const [name, sub] of groups) items.push({ text: name, items: sub })
    // 课名前加目录序号（如「02」），便于一眼分辨
    const num = (c.directory.match(/^(\d+)/) || [])[1]
    return { text: num ? `${num} ${c.title}` : c.title, items }
  })

export default defineConfig({
  lang: 'zh-CN',
  title: 'BioEZ',
  titleTemplate: ':title · BioEZ',
  description: '面向生物相关课程的中文学习资料库',
  srcDir: './content',
  cleanUrls: true,
  ignoreDeadLinks: true,
  lastUpdated: true,
  markdown: {
    lineNumbers: true,
    math: true,
    image: { lazyLoading: true },
  },
  themeConfig: {
    siteTitle: 'BioEZ Wiki',
    nav: [
      { text: '主页', link: '/' },
      { text: '全部课程', link: '/courses' },
      { text: '关于', link: '/about' },
    ],
    sidebar,
    outline: { level: [2, 3], label: '页面导航' },
    lastUpdated: { text: '最后更新' },
    darkModeSwitchLabel: '外观',
    sidebarMenuLabel: '目录',
    returnToTopLabel: '返回顶部',
    docFooter: { prev: '上一页', next: '下一页' },
    footer: {
      message: 'CC BY-SA 4.0',
      copyright: 'Copyright © BioEZ',
    },
    search: { provider: 'local' },
  },
})
