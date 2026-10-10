import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import BioEZDataViews from "./quartz/components/BioEZDataViews"
import BioEZNavLinks from "./quartz/components/BioEZNavLinks"

export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  // 顶栏（站名 / 搜索 / 导航 / 主题开关）固定在页首，样式见 styles/bioez-theme.scss
  header: [
    Component.Flex({
      components: [
        { Component: Component.PageTitle() },
        { Component: BioEZNavLinks(), align: "stretch" },
        { Component: Component.Spacer(), grow: true },
        { Component: Component.Search() },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
  ],
  afterBody: [BioEZDataViews()],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/XiaoniNaoh/BioEZ",
      博客: "https://bioez.xyz",
      "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
  }),
}

// 课程树仍留在左栏；站名、搜索与开关已经搬到顶栏，这里不再重复
const navigation = [Component.Explorer({ folderDefaultState: "collapsed", useSavedState: true })]

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
  ],
  left: navigation,
  right: [
    Component.Graph({
      localGraph: { depth: 1, scale: 1.1, showTags: false },
      // 全局图只在用户主动点击后出现，并限制为两跳，避免“毛线球”。
      globalGraph: { depth: 2, scale: 0.9, showTags: false },
    }),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: navigation,
  right: [],
}
