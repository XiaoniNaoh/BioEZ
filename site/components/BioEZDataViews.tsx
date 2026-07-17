import { readFileSync } from "node:fs"
import { join } from "node:path"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { FilePath, FullSlug, resolveRelative, slugifyFilePath } from "../util/path"
import styles from "./styles/bioez-data-views.scss"

type JsonObject = Record<string, unknown>

type Lesson = {
  id: string
  title: string
  path: string
  chapter: string
  order: string
  contentType: string
  status: string
  difficulty?: number
  importance?: number
  estimatedMinutes?: number
  summary: string
  lastScientificReview: string
}

type Course = {
  slug: string
  title: string
  directory: string
  description: string
  progress: string
  indexPath: string
  lessonCount: number
  pageCount: number
  estimatedMinutes: number
  lessons: Lesson[]
}

type Finding = {
  code: string
  severity: string
  path: string
  line?: number
  target: string
  message: string
}

type SiteData = {
  courses: Course[]
  summary: Record<string, number>
  findings: Finding[]
  qualityGeneratedAt?: string
  warnings: string[]
}

const isObject = (value: unknown): value is JsonObject =>
  typeof value === "object" && value !== null && !Array.isArray(value)
const text = (value: unknown, fallback = "") =>
  typeof value === "string" || typeof value === "number" ? String(value) : fallback
const number = (value: unknown, fallback = 0) =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback
const objects = (value: unknown): JsonObject[] =>
  Array.isArray(value) ? value.filter(isObject) : []

function readJson(filename: string, warnings: string[]): unknown {
  const dataDir = process.env.BIOEZ_DATA_DIR
  if (!dataDir) {
    warnings.push("未设置 BIOEZ_DATA_DIR，站点以无数据模式构建。")
    return undefined
  }

  try {
    return JSON.parse(readFileSync(join(dataDir, filename), "utf8"))
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error)
    warnings.push(`${filename} 不可用：${reason}`)
    return undefined
  }
}

function normalizeLesson(raw: JsonObject): Lesson {
  return {
    id: text(raw.id),
    title: text(raw.title, text(raw.id, "未命名页面")),
    path: text(raw.path),
    chapter: text(raw.chapter, "其他"),
    order: text(raw.order),
    contentType: text(raw.content_type, "lesson"),
    status: text(raw.status, "draft"),
    difficulty: typeof raw.difficulty === "number" ? raw.difficulty : undefined,
    importance: typeof raw.importance === "number" ? raw.importance : undefined,
    estimatedMinutes: typeof raw.estimated_minutes === "number" ? raw.estimated_minutes : undefined,
    summary: text(raw.summary),
    lastScientificReview: text(raw.last_scientific_review),
  }
}

function normalizeCourse(raw: JsonObject): Course {
  const lessons = objects(raw.lessons).map(normalizeLesson)
  return {
    slug: text(raw.slug),
    title: text(raw.title, text(raw.slug, "未命名课程")),
    directory: text(raw.directory),
    description: text(raw.description),
    progress: text(raw.progress, "serializing"),
    indexPath: text(raw.index_path),
    lessonCount: number(
      raw.lesson_count,
      lessons.filter((lesson) => lesson.contentType === "lesson").length,
    ),
    pageCount: number(raw.page_count, lessons.length),
    estimatedMinutes: number(raw.estimated_minutes),
    lessons,
  }
}

function loadData(): SiteData {
  const warnings: string[] = []
  const courseJson = readJson("courses.json", warnings)
  const qualityJson = readJson("quality-report.json", warnings)
  const courseRoot = isObject(courseJson) ? courseJson : {}
  const qualityRoot = isObject(qualityJson) ? qualityJson : {}

  const summary: Record<string, number> = {}
  if (isObject(qualityRoot.summary)) {
    for (const [key, value] of Object.entries(qualityRoot.summary)) {
      if (typeof value === "number" && Number.isFinite(value)) summary[key] = value
    }
  }

  const findings = objects(qualityRoot.findings).map((raw) => ({
    code: text(raw.code, "finding"),
    severity: text(raw.severity, "warning"),
    path: text(raw.path),
    line: typeof raw.line === "number" ? raw.line : undefined,
    target: text(raw.target),
    message: text(raw.message, "未提供说明"),
  }))

  return {
    courses: objects(courseRoot.courses).map(normalizeCourse),
    summary,
    findings,
    qualityGeneratedAt: text(qualityRoot.generated_at) || undefined,
    warnings,
  }
}

const DATA = loadData()

function pathHref(props: QuartzComponentProps, sourcePath: string) {
  if (
    !sourcePath ||
    !props.fileData.slug ||
    sourcePath.startsWith("/") ||
    sourcePath.includes("..") ||
    /^https?:\/\//.test(sourcePath)
  ) {
    return undefined
  }
  const clean = sourcePath.replaceAll("\\", "/").replace(/^\/+/, "")
  const filePath = (clean.endsWith(".md") ? clean : `${clean}.md`) as FilePath
  return resolveRelative(props.fileData.slug, slugifyFilePath(filePath))
}

function findingHref(props: QuartzComponentProps, sourcePath: string) {
  if (!sourcePath || sourcePath.startsWith("/") || sourcePath.includes("..")) return undefined
  const clean = sourcePath.replaceAll("\\", "/")
  const extension = clean.includes(".") ? clean.slice(clean.lastIndexOf(".")).toLowerCase() : ".md"
  const publishedExtensions = new Set([
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".avif",
  ])
  if (!publishedExtensions.has(extension)) return undefined

  const filePath = clean as FilePath
  return resolveRelative(props.fileData.slug!, slugifyFilePath(filePath))
}

const progressLabel: Record<string, string> = {
  completed: "已完成",
  serializing: "连载中",
}

function CourseTree(props: QuartzComponentProps) {
  if (DATA.courses.length === 0) {
    return (
      <section class="bioez-data-empty" role="status">
        <h2>课程地图尚未生成</h2>
        <p>缺少有效的 data/courses.json。正文与左侧文件导航仍可正常使用。</p>
      </section>
    )
  }

  return (
    <section class="bioez-course-map" aria-labelledby="course-map-title">
      <div class="bioez-section-heading">
        <div>
          <p class="bioez-eyebrow">结构化课程目录</p>
          <h2 id="course-map-title">选择一条学习路线</h2>
        </div>
        <a
          class="internal bioez-dashboard-link"
          href={resolveRelative(props.fileData.slug!, "dashboard" as FullSlug)}
        >
          查看维护看板
        </a>
      </div>
      <div class="bioez-course-grid">
        {DATA.courses.map((course) => {
          const chapters = new Map<string, Lesson[]>()
          for (const lesson of course.lessons.filter((item) => item.contentType === "lesson")) {
            const group = chapters.get(lesson.chapter) ?? []
            group.push(lesson)
            chapters.set(lesson.chapter, group)
          }
          const startPath = course.indexPath || course.lessons[0]?.path
          const startHref = pathHref(props, startPath)
          return (
            <details class="bioez-course-card">
              <summary>
                <span>
                  <strong>{course.title}</strong>
                  <small>{course.description || course.directory}</small>
                </span>
                <span class={`bioez-progress bioez-progress-${course.progress}`}>
                  {progressLabel[course.progress] ?? course.progress}
                </span>
              </summary>
              <div class="bioez-course-meta">
                <span>{course.lessonCount} 节</span>
                {course.estimatedMinutes > 0 && <span>约 {course.estimatedMinutes} 分钟</span>}
                {startHref && (
                  <a class="internal" href={startHref}>
                    进入课程
                  </a>
                )}
              </div>
              {[...chapters].map(([chapter, lessons]) => (
                <div class="bioez-chapter">
                  <h3>{chapter}</h3>
                  <ol>
                    {lessons.map((lesson) => {
                      const href = pathHref(props, lesson.path)
                      return (
                        <li>
                          {href ? (
                            <a class="internal" href={href}>
                              {lesson.title}
                            </a>
                          ) : (
                            lesson.title
                          )}
                          <span class="bioez-lesson-meta">
                            {lesson.estimatedMinutes ? `${lesson.estimatedMinutes} 分钟` : ""}
                            {lesson.difficulty ? ` · 难度 ${lesson.difficulty}` : ""}
                          </span>
                        </li>
                      )
                    })}
                  </ol>
                </div>
              ))}
            </details>
          )
        })}
      </div>
    </section>
  )
}

const coverageColumns = [
  ["published", "已发布"],
  ["difficulty", "难度"],
  ["importance", "重要性"],
  ["minutes", "阅读时长"],
  ["summary", "摘要"],
  ["review", "科学复审"],
] as const

function ratio(course: Course, key: (typeof coverageColumns)[number][0]) {
  const lessons = course.lessons.filter((lesson) => lesson.contentType === "lesson")
  if (lessons.length === 0) return 0
  const count = lessons.filter((lesson) => {
    if (key === "published") return lesson.status === "published"
    if (key === "difficulty") return lesson.difficulty !== undefined
    if (key === "importance") return lesson.importance !== undefined
    if (key === "minutes") return (lesson.estimatedMinutes ?? 0) > 0
    if (key === "summary") return lesson.summary.length > 0
    return lesson.lastScientificReview.length > 0
  }).length
  return Math.round((count / lessons.length) * 100)
}

function coverageClass(value: number) {
  if (value === 0) return "level-0"
  if (value < 50) return "level-1"
  if (value < 80) return "level-2"
  if (value < 100) return "level-3"
  return "level-4"
}

const summaryLabels: Record<string, string> = {
  markdown_files: "Markdown 页面",
  broken_links: "断链",
  ambiguous_wikilinks: "歧义 Wikilink",
  remote_images: "外部图片",
  missing_alt: "缺少替代文本",
  unreferenced_assets: "未引用资源",
  orphan_pages: "孤立页面",
  image_assets: "本地图片",
  image_references: "图片引用",
}

function Dashboard(props: QuartzComponentProps) {
  const cards = Object.entries(DATA.summary).filter(([key]) => key in summaryLabels)
  const lessons = DATA.courses.flatMap((course) =>
    course.lessons.filter((lesson) => lesson.contentType === "lesson"),
  )
  const oneYearAgo = new Date()
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1)
  const reviewed = lessons.filter((lesson) => lesson.lastScientificReview.length > 0)
  const staleReviews = reviewed.filter((lesson) => {
    const date = new Date(lesson.lastScientificReview)
    return !Number.isNaN(date.getTime()) && date < oneYearAgo
  })
  const courseMetrics = [
    ["正文总数", lessons.length, false],
    ["已发布", lessons.filter((lesson) => lesson.status === "published").length, false],
    ["已有科学复审", reviewed.length, false],
    ["超一年未复审", staleReviews.length, staleReviews.length > 0],
    ["从未科学复审", lessons.length - reviewed.length, lessons.length - reviewed.length > 0],
  ] as const
  return (
    <section class="bioez-dashboard" aria-labelledby="quality-title">
      {DATA.warnings.length > 0 && (
        <aside class="bioez-data-warning" role="status">
          <strong>数据降级模式</strong>
          <ul>
            {DATA.warnings.map((warning) => (
              <li>{warning}</li>
            ))}
          </ul>
        </aside>
      )}

      <div class="bioez-section-heading">
        <div>
          <p class="bioez-eyebrow">维护者视图</p>
          <h2 id="quality-title">内容质量概览</h2>
        </div>
        <a class="internal" href={resolveRelative(props.fileData.slug!, "index" as FullSlug)}>
          返回课程地图
        </a>
      </div>

      {DATA.courses.length > 0 && (
        <div class="bioez-metric-grid bioez-course-metrics">
          {courseMetrics.map(([label, value, hasFindings]) => (
            <article class={`bioez-metric ${hasFindings ? "has-findings" : ""}`}>
              <strong>{value}</strong>
              <span>{label}</span>
            </article>
          ))}
        </div>
      )}

      {cards.length > 0 ? (
        <div class="bioez-metric-grid">
          {cards.map(([key, value]) => (
            <article
              class={`bioez-metric ${value > 0 && key !== "markdown_files" && key !== "image_assets" && key !== "image_references" ? "has-findings" : ""}`}
            >
              <strong>{value}</strong>
              <span>{summaryLabels[key]}</span>
            </article>
          ))}
        </div>
      ) : (
        <p class="bioez-data-empty">
          quality-report.json 尚未生成；下面的覆盖率仍由课程清单实时计算。
        </p>
      )}

      <h2>课程元数据覆盖热图</h2>
      <div class="bioez-heatmap-wrap">
        <table class="bioez-heatmap">
          <thead>
            <tr>
              <th scope="col">课程</th>
              {coverageColumns.map(([, label]) => (
                <th scope="col">{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {DATA.courses.map((course) => (
              <tr>
                <th scope="row">{course.title}</th>
                {coverageColumns.map(([key, label]) => {
                  const value = ratio(course, key)
                  return (
                    <td
                      class={coverageClass(value)}
                      aria-label={`${course.title} ${label} ${value}%`}
                    >
                      {value}%
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>待处理发现</h2>
      {DATA.findings.length > 0 ? (
        <ol class="bioez-findings">
          {DATA.findings.slice(0, 30).map((finding) => (
            <li class={`severity-${finding.severity}`}>
              <span>{finding.severity}</span>
              <div>
                <strong>{finding.message}</strong>
                <small>
                  {findingHref(props, finding.path) ? (
                    <a class="internal" href={findingHref(props, finding.path)}>
                      {finding.path}
                      {finding.line ? `:${finding.line}` : ""}
                    </a>
                  ) : (
                    <>
                      {finding.path}
                      {finding.line ? `:${finding.line}` : ""}
                    </>
                  )}
                  {finding.target ? ` · ${finding.target}` : ""}
                </small>
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <p>报告中没有待处理发现。</p>
      )}
    </section>
  )
}

export default (() => {
  const BioEZDataViews: QuartzComponent = (props: QuartzComponentProps) => {
    const view = props.fileData.frontmatter?.bioezView
    if (view === "courses") return <CourseTree {...props} />
    if (view === "dashboard") return <Dashboard {...props} />
    return null
  }

  BioEZDataViews.css = styles
  return BioEZDataViews
}) satisfies QuartzComponentConstructor
