<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { withBase } from 'vitepress'

// 404 是全站唯一一页「没有正文」的页面，于是给它一条走廊。
// 走廊本身用 CSS 画（见 backrooms.css），这个组件只负责：挂上页面类名（用来收掉
// 侧栏与页脚的多余留白），以及桌面上跟着指针的一点视差。

let onPointerMove: ((e: PointerEvent) => void) | undefined
let raf = 0

// 「搜一个关键词」直接点开站内搜索框（就是导航栏那个搜索按钮）。
// 找不到按钮时退一步，派发主题自己监听的那个快捷键事件。
const openSearch = () => {
  const button = document.querySelector<HTMLElement>('#local-search .DocSearch-Button')
  if (button) {
    button.click()
    return
  }
  const event = new Event('keydown')
  Object.defineProperty(event, 'key', { value: 'k' })
  Object.defineProperty(event, 'metaKey', { value: true })
  window.dispatchEvent(event)
}

const calm = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
  !window.matchMedia('(hover: hover) and (pointer: fine)').matches

onMounted(() => {
  document.documentElement.classList.add('is-backrooms')
  if (calm()) return

  // 视差刻意做得很小（±7px）：走廊只是轻轻跟着手走，不做「花活」
  onPointerMove = (e) => {
    if (raf) return
    raf = requestAnimationFrame(() => {
      raf = 0
      const x = (e.clientX / window.innerWidth - 0.5) * -14
      const y = (e.clientY / window.innerHeight - 0.5) * -9
      const root = document.documentElement.style
      root.setProperty('--brk-shift-x', `${x.toFixed(1)}px`)
      root.setProperty('--brk-shift-y', `${y.toFixed(1)}px`)
    })
  }
  window.addEventListener('pointermove', onPointerMove, { passive: true })
})

onUnmounted(() => {
  const root = document.documentElement
  root.classList.remove('is-backrooms')
  root.style.removeProperty('--brk-shift-x')
  root.style.removeProperty('--brk-shift-y')
  if (onPointerMove) window.removeEventListener('pointermove', onPointerMove)
  if (raf) cancelAnimationFrame(raf)
})
</script>

<template>
  <div class="backrooms">
    <!-- 走廊：纯 CSS 单向透视。远景那道光是走廊尽头，不是装饰 -->
    <div class="brk-scene" aria-hidden="true">
      <div class="brk-room">
        <span class="brk-plane brk-wall-left"></span>
        <span class="brk-plane brk-wall-right"></span>
        <span class="brk-plane brk-ceiling"></span>
        <span class="brk-plane brk-floor"></span>
        <span class="brk-far"></span>
        <span class="brk-damp"></span>
      </div>
      <span class="brk-spill"></span>
      <span class="brk-tube brk-tube-near"></span>
      <span class="brk-tube brk-tube-mid"></span>
      <span class="brk-tube brk-tube-far"></span>
      <span class="brk-pool"></span>
      <span class="brk-grain"></span>
      <span class="brk-vignette"></span>
    </div>

    <span class="brk-tail" aria-hidden="true"></span>

    <div class="brk-body">
      <p class="brk-folio">
        <span class="brk-folio-num">404</span>
        <span class="brk-folio-rule"></span>
        <span class="brk-folio-label">尚未收录</span>
      </p>

      <h1 class="brk-title">你来到了<span class="brk-mark">后室</span></h1>

      <p class="brk-text">我趣，你怎么卡进这里的。别急，稍后再来这页看看吧。</p>

      <p class="brk-why-label">大概就这几种原因：</p>
      <ul class="brk-why">
        <li>课程改过名、文章搬过家，你手上那条旧链接就断了</li>
        <li>地址里打错了一个字，或者复制的时候少粘了一段</li>
        <li>点开的是很久以前收藏的链接，那一页还没写</li>
      </ul>

      <a class="brk-exit" :href="withBase('/')">
        <svg
          class="brk-exit-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M13.8 3.4h5.6v17.2h-5.6" />
          <g class="brk-exit-arrow">
            <path d="M3.4 12h7.3" />
            <path d="M8.2 8.5 11.7 12l-3.5 3.5" />
          </g>
        </svg>
        <span class="brk-exit-label">将军走此小道回首页</span>
      </a>

      <p class="brk-hint">
        <span>要找东西的话，</span>
        <button type="button" class="brk-hint-action" @click="openSearch">搜个关键词</button>
        <span>最快；也可以从</span>
        <a class="brk-hint-action" :href="withBase('/courses')">全部课程</a>
        <span>翻进去。</span>
      </p>

      <ul class="brk-meta">
        <li>生存难度：待定</li>
        <li>实体：暂未发现</li>
        <li>已确认出口：1</li>
      </ul>
    </div>
  </div>
</template>
