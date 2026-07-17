# BioEZ 内容元数据规范

BioEZ 使用 Markdown 文件顶部的 YAML Frontmatter 描述课程结构和审校状态。新建教程必须包含完整元数据；修改旧教程时，应同步完成该文件的迁移。

## 必填字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | 字符串 | 全库唯一、稳定的小写 ID，如 `mmb-02-02` |
| `title` | 字符串 | 页面标题 |
| `course` | 字符串 | 课程 slug，如 `molecular-biology` |
| `chapter` | 字符串 | 所属章节 |
| `order` | 数字或字符串 | 课程内排序值，如 `2.2` |
| `status` | 字符串 | `draft` / `editorial-review` / `scientific-review` / `published` |
| `audience` | 列表 | 目标读者，如 `undergraduate` |
| `difficulty` | 整数 | 1（最易）至 5（最难） |
| `importance` | 整数 | 1（拓展）至 5（核心） |
| `estimated_minutes` | 整数 | 预计阅读时间，必须大于 0 |
| `prerequisites` | 列表 | 前置页面 ID，无则为 `[]` |
| `next` | 列表 | 推荐后续页面 ID，无则为 `[]` |
| `tags` | 列表 | 可检索标签 |
| `authors` | 列表 | 作者 |
| `reviewers` | 列表 | 科学审校者；未审校时为 `[]` |
| `last_scientific_review` | ISO 日期或 `null` | 最近科学审校日期 |
| `summary` | 字符串 | 一句话摘要 |
| `references` | 列表 | DOI、网址或参考文献标识 |
| `content_type` | 字符串 | `lesson`（课程正文）或 `course-index`（人工维护的路线图） |

`published` 页面必须填写 `reviewers` 和 `last_scientific_review`。尚未完成审校的旧页面应标为 `scientific-review`，不应为了通过检查而虚构审校记录。

## 评分标准

- 难度 1：无前置知识；3：需要本课程基础；5：需要跨课程推导或专业实践。
- 重要性 1：拓展阅读；3：课程主干；5：理解多个后续章节所必需的核心概念。

可从 [教程模板](tutorial-template.md) 复制新页面。提交前运行：

```bash
python3 scripts/validate_content.py --paths "path/to/tutorial.md"
```

## 自动迁移与生成

课程级配置维护在 `data/course-config.json`。新增或移动页面后依次运行：

```bash
python3 scripts/migrate_course_metadata.py
python3 scripts/build_course_catalog.py
python3 scripts/validate_content.py --all
python3 scripts/build_course_catalog.py --check
```

构建脚本会更新每页 `next`、标准前后篇导航、各课程的 `COURSE_INDEX.md`、README 课程清单及 `data/courses.json`。这些生成区域不应手工编辑。
