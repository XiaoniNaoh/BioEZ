import DefaultTheme from 'vitepress/theme'
import './custom.css'

// 目录条目一律单行，超长的会被截成「…」。
// 悬浮时把这一行「就地展开」：在条目位置画一层同样行高、同样字体的浮层，
// 从文字左缘往右长、突破目录宽度显示全名。
// 鼠标移开不马上收，留 3 秒——连续滑过多个条目时，前几个的全名会一起挂着。

const BOX_CLASS = 'sidebar-expand'
const KEEP_MS = 3000
const MAX_SHOWN = 8

const free: HTMLDivElement[] = []
const shown = new Map<HTMLElement, { box: HTMLDivElement; timer?: number }>()
let hovered: HTMLElement | null = null

function takeBox() {
  const pooled = free.pop()
  if (pooled) return pooled
  const box = document.createElement('div')
  box.className = BOX_CLASS
  box.setAttribute('aria-hidden', 'true')
  document.body.append(box)
  return box
}

// 贴到条目上：行高与这一行一致，字体照抄该行；从文字左缘往右长
function place(el: HTMLElement, box: HTMLDivElement) {
  const r = el.getBoundingClientRect()
  const cs = getComputedStyle(el)
  box.style.fontFamily = cs.fontFamily
  box.style.fontSize = cs.fontSize
  box.style.fontWeight = cs.fontWeight
  box.style.letterSpacing = cs.letterSpacing
  box.style.color = cs.color
  box.style.height = `${Math.round(r.height)}px`
  box.style.lineHeight = `${Math.round(r.height)}px`

  const width = box.getBoundingClientRect().width
  const maxRight = window.innerWidth - 12
  let left = r.left - 8
  if (left + width > maxRight) left = Math.max(12, maxRight - width)
  box.style.left = `${Math.round(left)}px`
  box.style.top = `${Math.round(r.top)}px`
}

function hide(el: HTMLElement) {
  const entry = shown.get(el)
  if (!entry) return
  window.clearTimeout(entry.timer)
  entry.box.classList.remove('is-open')
  shown.delete(el)
  if (hovered === el) hovered = null
  // 等淡出（0.45s）结束再回收到空闲池，免得复用的时候闪一下
  window.setTimeout(() => {
    if (!entry.box.classList.contains('is-open')) free.push(entry.box)
  }, 520)
}

function show(el: HTMLElement) {
  let entry = shown.get(el)
  if (entry) {
    window.clearTimeout(entry.timer)
    entry.timer = undefined
  } else {
    // 挂太多会糊成一片，超上限就把最早的那条收掉
    if (shown.size >= MAX_SHOWN) {
      const oldest = shown.keys().next().value as HTMLElement | undefined
      if (oldest) hide(oldest)
    }
    entry = { box: takeBox() }
    // 连内部标记一起复制：「课程目录」的胶囊、文件的小圆点都还在
    entry.box.innerHTML = el.innerHTML
    const item = el.closest('.VPSidebarItem')
    const isFile =
      !!item && !item.classList.contains('level-0') && !item.querySelector(':scope > .items > *')
    entry.box.classList.toggle('has-dot', isFile)
    shown.set(el, entry)
  }
  place(el, entry.box)
  entry.box.classList.add('is-open')
}

// 鼠标离开这一条：留 3 秒再收
function keep(el: HTMLElement) {
  const entry = shown.get(el)
  if (!entry || entry.timer) return
  entry.timer = window.setTimeout(() => hide(el), KEEP_MS)
}

function hideAll() {
  for (const el of [...shown.keys()]) hide(el)
  hovered = null
}

// 页面（或侧栏自己）滚动时：浮层跟着条目走，条目滚出视口就收
function followScroll() {
  for (const [el, entry] of [...shown]) {
    const r = el.getBoundingClientRect()
    if (r.bottom < 0 || r.top > window.innerHeight) hide(el)
    else place(el, entry.box)
  }
}

function isTruncated(el: HTMLElement) {
  return !!el.textContent?.trim() && el.scrollWidth > el.clientWidth + 1
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
      if (el === hovered) return
      // 换了目标：上一个开始计时（3 秒内仍然挂着）
      if (hovered) keep(hovered)
      hovered = el && isTruncated(el) ? el : null
      if (hovered) show(hovered)
    })
    document.addEventListener('click', hideAll, true)
    window.addEventListener('scroll', followScroll, true)
    window.addEventListener('resize', followScroll)
  },
}
