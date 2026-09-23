import DefaultTheme from 'vitepress/theme'
import './custom.css'

// 目录条目一律单行，超长的会被截成「…」。
// 悬浮时不用浏览器原生 title（它有约一秒延迟），改成自己弹一个气泡：
// 立刻出现、追加在 body 上（不会被侧栏裁掉），只对确实被截断的条目弹。

let tip: HTMLDivElement | undefined
let current: HTMLElement | null = null

function ensureTip() {
  if (!tip) {
    tip = document.createElement('div')
    tip.className = 'sidebar-tip'
    tip.setAttribute('role', 'tooltip')
    document.body.append(tip)
  }
  return tip
}

function hideTip() {
  current = null
  tip?.classList.remove('is-open')
}

function showTip(el: HTMLElement) {
  const full = (el.textContent || '').trim()
  // 没被截断的不用提示
  if (!full || el.scrollWidth <= el.clientWidth + 1) return hideTip()

  const box = ensureTip()
  const r = el.getBoundingClientRect()
  box.textContent = full
  box.classList.add('is-open')

  const b = box.getBoundingClientRect()
  // 默认放在条目右侧；右边放不下就翻到左侧，并夹在视口内
  let left = r.right + 10
  if (left + b.width > window.innerWidth - 12) left = Math.max(12, r.left - b.width - 10)
  let top = r.top + r.height / 2 - b.height / 2
  top = Math.min(Math.max(12, top), Math.max(12, window.innerHeight - b.height - 12))
  box.style.left = `${left}px`
  box.style.top = `${top}px`
  current = el
}

export default {
  extends: DefaultTheme,
  setup() {
    if (typeof window === 'undefined') return
    // 用事件委托，侧栏重绘（路由切换、展开收起）也不用重新绑定
    document.addEventListener('mouseover', (e) => {
      const el = (e.target as HTMLElement | null)?.closest?.(
        '.VPSidebar .VPSidebarItem .text',
      ) as HTMLElement | null
      if (el === current) return
      if (el) showTip(el)
      else hideTip()
    })
    document.addEventListener('click', hideTip, true)
    window.addEventListener('scroll', hideTip, true)
    window.addEventListener('resize', hideTip)
  },
}
