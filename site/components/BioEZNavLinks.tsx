import { FullSlug, resolveRelative, simplifySlug } from "../util/path"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"
import style from "./styles/bioez-nav.scss"

type NavEntry = {
  /** 导航文字 */
  text: string
  /** 站内页面（slug），与 href 二选一 */
  slug?: string
  /** 站外链接 */
  href?: string
}

// 顶栏导航。站内页面用 slug，链接在渲染时按当前页深度换算成相对地址，
// 这样站点既可以挂在 xiaoninaoh.github.io/BioEZ/ 下，也可以换到自有域名。
const ENTRIES: NavEntry[] = [
  { text: "主页", slug: "index" },
  { text: "内容质量看板", slug: "dashboard" },
  { text: "资料卡与图库", slug: "资料卡与图库/index" },
  { text: "博客", href: "https://bioez.xyz" },
]

function isActive(current: string, entry: NavEntry): boolean {
  if (!entry.slug) return false
  const target = simplifySlug(entry.slug as FullSlug)
  if (target === "/") return current === "/"
  return current === target || current.startsWith(`${target}/`)
}

const NavLinks: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
  const current = simplifySlug(fileData.slug!)

  return (
    <nav class={classNames(displayClass, "bioez-nav-links")} aria-label="站点导航">
      {ENTRIES.map((entry) => {
        const external = entry.href !== undefined
        const href = entry.href ?? resolveRelative(fileData.slug!, entry.slug as FullSlug)
        return (
          <a
            href={href}
            class={isActive(current, entry) ? "active" : undefined}
            {...(external ? { target: "_blank", rel: "noopener" } : {})}
          >
            {entry.text}
          </a>
        )
      })}
    </nav>
  )
}

NavLinks.css = style

export default (() => NavLinks) satisfies QuartzComponentConstructor
