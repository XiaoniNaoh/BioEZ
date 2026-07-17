import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import BioEZDataViews from "./quartz/components/BioEZDataViews"

export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [BioEZDataViews()],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/XiaoniNaoh/BioEZ",
      "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
  }),
}

const navigation = [
  Component.PageTitle(),
  Component.MobileOnly(Component.Spacer()),
  Component.Flex({
    components: [
      { Component: Component.Search(), grow: true },
      { Component: Component.Darkmode() },
      { Component: Component.ReaderMode() },
    ],
  }),
  Component.Explorer({ folderDefaultState: "collapsed", useSavedState: true }),
]

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
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
