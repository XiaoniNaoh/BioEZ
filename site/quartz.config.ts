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
        // 克制的灰阶 + 唯一一支松绿强调色（设计参考 deno.com 的文档站）。
        // 变量名沿用 Quartz 的语义：light 是页面底色、lightgray 是发丝线、
        // darkgray 是正文、dark 是标题与强调字、secondary 是链接与选中态。
        lightMode: {
          light: "#ffffff",
          lightgray: "#e4e7e9",
          gray: "#85898e",
          darkgray: "#3a4046",
          dark: "#1b1f23",
          secondary: "#116329",
          tertiary: "#0b4a1e",
          highlight: "rgba(112, 255, 175, 0.35)",
          textHighlight: "rgba(112, 255, 175, 0.6)",
        },
        darkMode: {
          light: "#17191c",
          lightgray: "#2b2f33",
          gray: "#8b9198",
          darkgray: "#c9ced3",
          dark: "#f0f2f4",
          secondary: "#70ffaf",
          tertiary: "#a5ffcb",
          highlight: "rgba(112, 255, 175, 0.2)",
          textHighlight: "rgba(112, 255, 175, 0.3)",
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
