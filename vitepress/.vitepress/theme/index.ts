import DefaultTheme from 'vitepress/theme'
import './custom.css'

// 目录条目一律单行，超长的会被截成「…」。
// 悬浮时把这一行「长出去」：在条目位置画一层同样行高、同样字体的浮层，
// 内容就是完整标题——看起来就是省略号被就地展开、突破了目录宽度。
// （不用浏览器原生 title，那个有约一秒延迟。）

let box: HTMLDivElement | undefined
let current: HTMLElement | null = null

function ensureBox() {
  if (!box) {
    box = document.createElement('div')
    box.className = 'sidebar-expand'
    box.setAttribute('aria-hidden', 'true')
    document.body.append(box)
  }
  return box
}

function hideExpand() {
  current = null
  box?.classList.toggle('is-open', false)
}

function showExpand(el: HTMLElement) {
  // 没被截断的不用展开
  if (!el.textContent?.trim() || el.scrollWidth <= el.clientWidth + 1) return hideExpand()

  const b = ensureBox()
  const r = el.getBoundingClientRect()
  const cs = getComputedStyle(el)

  // 连内部标记一起复制：这样「课程目录」的胶囊、文件的小圆点都还在
  b.innerHTML = el.innerHTML
  b.style.fontFamily = cs.fontFamily
  b.style.fontSize = cs.fontSize
  b.style.fontWeight = cs.fontWeight
  b.style.letterSpacing = cs.letterSpacing
  b.style.color = cs.color
  b.style.height = `${Math.round(r.height)}px`
  b.style.lineHeight = `${Math.round(r.height)}px`

  // 文件那一档前面有个小圆点，浮层里也要有，否则展开时会跳一下
  const item = el.closest('.VPSidebarItem')
  const isFile = !!item && !item.classList.contains('level-0') && !item.querySelector(':scope > .items > *')
  b.classList.toggle('has-dot', isFile)
  b.classList.add('is-open')

  // 从文字左缘（留出 8px 内边距）往右长；右边装不下就整体左移并夹在视口内
  const width = b.getBoundingClientRect().width
  const maxRight = window.innerWidth - 12
  let left = r.left - 8
  if (left + width > maxRight) left = Math.max(12, maxRight - width)
  b.style.left = `${Math.round(left)}px`
  b.style.top = `${Math.round(r.top)}px`
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
      if (el) showExpand(el)
      else hideExpand()
    })
    document.addEventListener('click', hideExpand, true)
    window.addEventListener('scroll', hideExpand, true)
    window.addEventListener('resize', hideExpand)
  },
}
