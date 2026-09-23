import DefaultTheme from 'vitepress/theme'
import './custom.css'

// 目录条目现在一律单行，超长的会被截成「…」。
// 这里只给「确实被截断」的条目补上 title，鼠标悬浮就能看到全名；
// 没被截断的条目不加 title，避免多余的提示框。

let timer: number | undefined

function markTruncated() {
  timer = undefined
  document.querySelectorAll<HTMLElement>('.VPSidebar .VPSidebarItem .text').forEach((el) => {
    const full = (el.textContent || '').trim()
    if (el.scrollWidth > el.clientWidth + 1) {
      if (el.getAttribute('title') !== full) el.setAttribute('title', full)
    } else if (el.hasAttribute('title')) {
      el.removeAttribute('title')
    }
  })
}

function schedule() {
  if (typeof window === 'undefined') return
  if (timer) window.clearTimeout(timer)
  timer = window.setTimeout(markTruncated, 80)
}

export default {
  extends: DefaultTheme,
  setup() {
    if (typeof window === 'undefined') return
    schedule()
    // 路由切换、展开/收起文件夹、窗口缩放都会让侧栏重排
    new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true })
    window.addEventListener('resize', schedule)
  },
}
