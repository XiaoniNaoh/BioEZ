import unittest
from pathlib import Path

from scripts.build_course_catalog import clean_legacy_navigation, update_readme
from scripts.course_catalog import (
    Course,
    default_metadata,
    normalize_token,
    render_frontmatter,
)
from scripts.validate_content import parse_frontmatter


BIOINFORMATICS = Course(
    slug="bioinformatics",
    title="LLM 时代的生信入门",
    directory="07 LLM 时代的生信入门",
    prefix="BIF",
    description="测试课程",
    progress="serializing",
    authors=("作者",),
    audience=("undergraduate",),
)


class MetadataMigrationTests(unittest.TestCase):
    def test_normalizes_numeric_and_lettered_orders(self):
        self.assertEqual(normalize_token("02-1"), "02-01")
        self.assertEqual(normalize_token("SP1"), "sp-01")
        self.assertEqual(normalize_token("B-2"), "b-02")

    def test_derives_bioinformatics_practical_chapter(self):
        path = Path("07 LLM 时代的生信入门/BIF B-2 scRNAseq 入门到 UMAP 注释.md")
        metadata = default_metadata(path, BIOINFORMATICS, "#生信 #单细胞分析\n")
        self.assertEqual(metadata["id"], "bif-b-02")
        self.assertEqual(metadata["chapter"], "scRNAseq 实操")
        self.assertEqual(metadata["content_type"], "lesson")

    def test_route_map_uses_course_index_content_type(self):
        path = Path("07 LLM 时代的生信入门/BIF 00 目录与更新计划.md")
        metadata = default_metadata(path, BIOINFORMATICS, "#生信\n")
        self.assertEqual(metadata["content_type"], "course-index")
        self.assertEqual(metadata["chapter"], "课程导航")

    def test_rendered_frontmatter_round_trips_through_validator_parser(self):
        path = Path("07 LLM 时代的生信入门/BIF A-1 示例.md")
        metadata = default_metadata(path, BIOINFORMATICS, "#生信\n")
        parsed, error = parse_frontmatter(render_frontmatter(metadata) + "\n# 示例\n")
        self.assertIsNone(error)
        self.assertEqual(parsed, metadata)


class GeneratedContentTests(unittest.TestCase):
    def test_removes_only_legacy_navigation_lines(self):
        body = "# 标题\n> 上一节链接🔗 [[A]]\n正文中的下一代不应删除。\n> 下一节链接🔗 [[B]]\n"
        cleaned = clean_legacy_navigation(body)
        self.assertNotIn("上一节链接", cleaned)
        self.assertNotIn("下一节链接", cleaned)
        self.assertIn("下一代不应删除", cleaned)

    def test_readme_catalog_replacement_is_repeatable(self):
        original = "# Repo\n\n## 📚 项目目录\n\n旧内容\n\n## 🌏 更新日志\n\n日志\n"
        catalog = "<!-- BEGIN AUTO-GENERATED COURSE CATALOG -->\n新内容\n<!-- END AUTO-GENERATED COURSE CATALOG -->"
        first = update_readme(original, catalog)
        second = update_readme(first, catalog)
        self.assertEqual(first, second)
        self.assertNotIn("旧内容", first)


if __name__ == "__main__":
    unittest.main()
