import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "BioEZ",
    pageTitleSuffix: " · 生物学宝宝教程",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "zh-CN",
    baseUrl: process.env.QUARTZ_BASE_URL ?? "XiaoniNaoh.github.io/BioEZ",
    ignorePatterns: [".obsidian", "templates", "**/*模板*", "**/*一本全*"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "local",
      cdnCaching: false,
      typography: {
        title: "system-ui",
        header: "system-ui",
        body: "system-ui",
        code: "ui-monospace",
      },
      colors: {
        lightMode: {
          light: "#fbfcf8",
          lightgray: "#e4eadf",
          gray: "#a3ad9b",
          darkgray: "#415044",
          dark: "#1d2b22",
          secondary: "#26734d",
          tertiary: "#b45f3d",
          highlight: "rgba(52, 125, 82, 0.12)",
          textHighlight: "#f5df7280",
        },
        darkMode: {
          light: "#152019",
          lightgray: "#2b3b30",
          gray: "#718078",
          darkgray: "#d2ddd5",
          dark: "#f1f6f2",
          secondary: "#75c79c",
          tertiary: "#efa783",
          highlight: "rgba(117, 199, 156, 0.14)",
          textHighlight: "#8c791e80",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({ priority: ["frontmatter", "filesystem"] }),
      Plugin.SyntaxHighlighting({
        theme: { light: "github-light", dark: "github-dark" },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({ enableSiteMap: true, enableRSS: false }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config
