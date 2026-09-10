import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitepress'

const courses: any[] = JSON.parse(
  readFileSync(fileURLToPath(new URL('../../data/courses.json', import.meta.url)), 'utf8'),
).courses ?? []

const toLink = (p: string) => '/' + p.replace(/\.md$/, '')

const sidebar = courses
  .filter((c) => c && c.directory)
  .map((c) => ({
    text: c.title,
    collapsed: false,
    items: [
      ...(c.index_path ? [{ text: '课程目录', link: toLink(c.index_path) }] : []),
      ...(c.lessons ?? []).map((l: any) => ({ text: l.title, link: toLink(l.path) })),
    ],
  }))

export default defineConfig({
  lang: 'zh-CN',
  title: 'BioEZ',
  titleTemplate: ':title · BioEZ',
  description: '面向生物相关课程的中文学习资料库',
  srcDir: './content',
  cleanUrls: true,
  ignoreDeadLinks: true,
  lastUpdated: true,
  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    [
      'link',
      {
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
        rel: 'stylesheet',
      },
    ],
  ],
  markdown: {
    lineNumbers: true,
    math: true,
    theme: { light: 'material-theme-lighter', dark: 'material-theme-darker' },
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
