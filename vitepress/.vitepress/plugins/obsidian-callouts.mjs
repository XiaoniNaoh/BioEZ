/**
 * Obsidian 提示块（callout）里，VitePress 认不出的那几种，交给这个插件兜底。
 *
 * VitePress 自带的识别表只到 TIP / NOTE / INFO / IMPORTANT / WARNING /
 * CAUTION / DANGER（见 vitepress 里的 markerRE），而笔记里还用了：
 *   [!ATTENTION]  7 处 —— Obsidian 里它就是 WARNING 的别名，同一个橙色三角
 *   [!EXAMPLE]    5 处 —— Obsidian 单独一类，标题多半写「举例」「记忆口诀」
 *   [!Notes]      6 处 —— 复数写法，VitePress 只认 NOTE，这里一并兜住
 * 不兜的话它们会退化成普通引用块，只剩一根竖线，看不出是提示。
 *
 * 渲染出来的结构和 VitePress 自己的 github-alert 完全一致
 * （<div class="类型 custom-block github-alert"> + .custom-block-title），
 * 所以配色、间距、深浅色都跟着现有的一套走，不用额外写样式。
 */

// 认哪几种、渲染成什么类名、没写标题时显示什么
const EXTRA_TYPES = {
  attention: { className: 'attention', label: '注意' },
  example: { className: 'example', label: '示例' },
  notes: { className: 'note', label: '笔记' },
}

export function obsidianCallouts(md, options = {}) {
  const types = { ...EXTRA_TYPES, ...(options.types || {}) }
  const names = Object.keys(types)
  const markerRE = new RegExp(`^\\[!(${names.join('|')})\\]([^\\n\\r]*)`, 'i')

  md.core.ruler.after('block', 'obsidian-callouts', (state) => {
    const tokens = state.tokens

    for (let i = 0; i < tokens.length; i++) {
      if (tokens[i].type !== 'blockquote_open') continue

      const open = tokens[i]
      let end = i + 1
      while (
        end < tokens.length &&
        (tokens[end].type !== 'blockquote_close' || tokens[end].level !== open.level)
      ) {
        end++
      }
      if (end === tokens.length) continue

      const close = tokens[end]
      const firstContent = tokens.slice(i, end + 1).find((token) => token.type === 'inline')
      if (!firstContent) continue

      const match = firstContent.content.match(markerRE)
      if (!match) continue

      const key = match[1].toLowerCase()
      const preset = types[key]
      // Obsidian 的折叠写法「> [!example]- 标题」：去掉标题前面的 - / +
      const written = match[2].trim().replace(/^[-+]/, '').trim()

      firstContent.content = firstContent.content.slice(match[0].length).trimStart()
      open.type = 'obsidian_callout_open'
      open.tag = 'div'
      open.meta = { className: preset.className, title: written || preset.label }
      close.type = 'obsidian_callout_close'
      close.tag = 'div'
    }
  })

  md.renderer.rules.obsidian_callout_open = (tokens, idx) => {
    const { className, title } = tokens[idx].meta
    return `<div class="${className} custom-block github-alert"><p class="custom-block-title">${md.utils.escapeHtml(title)}</p>\n`
  }

  md.renderer.rules.obsidian_callout_close = () => '</div>\n'
}
