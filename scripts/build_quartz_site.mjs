#!/usr/bin/env node
import { execFileSync, spawnSync } from "node:child_process"
import {
  copyFileSync,
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
} from "node:fs"
import { dirname, extname, join, relative, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const QUARTZ_VERSION = "v4.5.2"
// Peeled commit behind the annotated v4.5.2 tag.
const QUARTZ_COMMIT = "4923affa7722dfc751f1074348e6dad214fe0c08"
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const CACHE = resolve(process.env.QUARTZ_CACHE_DIR ?? join(ROOT, ".cache", "quartz-v4.5.2"))
const CONTENT = join(ROOT, ".cache", "site-content")
const OUTPUT = resolve(process.env.QUARTZ_OUTPUT_DIR ?? join(ROOT, "public"))
const DATA = resolve(process.env.BIOEZ_DATA_DIR ?? join(ROOT, "data"))
const args = new Set(process.argv.slice(2))

function run(command, commandArgs, options = {}) {
  const result = spawnSync(command, commandArgs, { stdio: "inherit", ...options })
  if (result.status !== 0) process.exit(result.status ?? 1)
}

function ensureQuartz() {
  if (!existsSync(join(CACHE, ".git"))) {
    mkdirSync(dirname(CACHE), { recursive: true })
    run("git", [
      "clone",
      "--depth",
      "1",
      "--branch",
      QUARTZ_VERSION,
      "https://github.com/jackyzha0/quartz.git",
      CACHE,
    ])
  }

  const actual = execFileSync("git", ["rev-parse", "HEAD"], { cwd: CACHE, encoding: "utf8" }).trim()
  if (actual !== QUARTZ_COMMIT) {
    throw new Error(`Quartz checkout mismatch: expected ${QUARTZ_COMMIT}, found ${actual}`)
  }
}

function applyOverlay() {
  copyFileSync(join(ROOT, "site", "quartz.config.ts"), join(CACHE, "quartz.config.ts"))
  copyFileSync(join(ROOT, "site", "quartz.layout.ts"), join(CACHE, "quartz.layout.ts"))
  copyFileSync(
    join(ROOT, "site", "components", "BioEZDataViews.tsx"),
    join(CACHE, "quartz", "components", "BioEZDataViews.tsx"),
  )
  copyFileSync(
    join(ROOT, "site", "styles", "bioez-data-views.scss"),
    join(CACHE, "quartz", "components", "styles", "bioez-data-views.scss"),
  )
}

const allowedExtensions = new Set([".md", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif"])

function copyPublishedTree(source, target) {
  for (const entry of readdirSync(source, { withFileTypes: true })) {
    if (entry.name.startsWith(".")) continue
    const from = join(source, entry.name)
    const to = join(target, entry.name)
    if (entry.isDirectory()) {
      copyPublishedTree(from, to)
    } else if (
      entry.isFile() &&
      allowedExtensions.has(extname(entry.name).toLowerCase()) &&
      !entry.name.includes("模板") &&
      !entry.name.includes("一本全")
    ) {
      mkdirSync(dirname(to), { recursive: true })
      copyFileSync(from, to)
    }
  }
}

function manifestDirectories() {
  const manifest = join(DATA, "courses.json")
  if (!existsSync(manifest)) return []
  try {
    const parsed = JSON.parse(readFileSync(manifest, "utf8"))
    if (!Array.isArray(parsed.courses)) return []
    return parsed.courses
      .map((course) => (course && typeof course.directory === "string" ? course.directory : ""))
      .filter((directory) => directory && !directory.includes("..") && existsSync(join(ROOT, directory)))
  } catch {
    return []
  }
}

function prepareContent() {
  rmSync(CONTENT, { recursive: true, force: true })
  mkdirSync(CONTENT, { recursive: true })

  const configured = manifestDirectories()
  const discovered = readdirSync(ROOT, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && /^(?:0[1-9]|[1-8]\d)\s/.test(entry.name))
    .map((entry) => entry.name)
  const courseDirectories = [...new Set(configured.length > 0 ? configured : discovered)]

  for (const directory of courseDirectories) {
    copyPublishedTree(join(ROOT, directory), join(CONTENT, directory))
  }
  if (existsSync(join(ROOT, "资料卡与图库"))) {
    copyPublishedTree(join(ROOT, "资料卡与图库"), join(CONTENT, "资料卡与图库"))
  }

  cpSync(join(ROOT, "site", "pages"), CONTENT, { recursive: true })
  for (const filename of ["courses.json", "quality-report.json"]) {
    const source = join(DATA, filename)
    if (existsSync(source)) {
      mkdirSync(join(CONTENT, "data"), { recursive: true })
      copyFileSync(source, join(CONTENT, "data", filename))
    }
  }

  const staged = readdirSync(CONTENT, { recursive: true }).length
  console.log(`Prepared ${staged} staged entries from ${courseDirectories.length} courses.`)
}

ensureQuartz()
applyOverlay()
prepareContent()

if (!args.has("--skip-install")) {
  run("npm", ["ci", "--no-audit", "--no-fund"], { cwd: CACHE })
}

if (args.has("--check")) {
  run("npm", ["run", "check"], { cwd: CACHE })
}

const buildArgs = ["quartz/bootstrap-cli.mjs", "build", "--directory", CONTENT, "--output", OUTPUT]
if (args.has("--serve")) buildArgs.push("--serve")
run(process.execPath, buildArgs, {
  cwd: CACHE,
  env: {
    ...process.env,
    BIOEZ_DATA_DIR: DATA,
  },
})

console.log(`Quartz ${QUARTZ_VERSION} (${QUARTZ_COMMIT.slice(0, 12)}) built ${relative(ROOT, OUTPUT)}.`)
