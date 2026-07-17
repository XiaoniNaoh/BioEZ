import tempfile
import unittest
from pathlib import Path

from scripts.validate_content import parse_frontmatter, validate_file


VALID = """---
id: mmb-02-02
title: DNA 的结构
course: molecular-biology
chapter: 染色体与 DNA
order: 2.2
status: scientific-review
audience:
  - undergraduate
difficulty: 2
importance: 3
estimated_minutes: 15
prerequisites:
  - mmb-02-01
next:
  - mmb-02-03
tags:
  - DNA
authors:
  - 小倪
reviewers: []
last_scientific_review: null
summary: DNA 结构入门。
references: []
content_type: lesson
---
# DNA 的结构
"""


class FrontmatterTests(unittest.TestCase):
    def write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def test_parses_scalar_and_list_values(self):
        data, error = parse_frontmatter(VALID)
        self.assertIsNone(error)
        self.assertEqual(data["difficulty"], 2)
        self.assertEqual(data["audience"], ["undergraduate"])
        self.assertIsNone(data["last_scientific_review"])

    def test_reports_missing_frontmatter(self):
        data, error = parse_frontmatter("# 没有元数据")
        self.assertIsNone(data)
        self.assertIn("缺少", error)

    def test_accepts_valid_draft(self):
        _, findings = validate_file(self.write(VALID))
        self.assertEqual(findings, [])

    def test_rejects_out_of_range_rating(self):
        _, findings = validate_file(self.write(VALID.replace("difficulty: 2", "difficulty: 6")))
        self.assertTrue(any("difficulty" in finding.message for finding in findings))

    def test_published_content_requires_review_record(self):
        _, findings = validate_file(self.write(VALID.replace("status: scientific-review", "status: published")))
        self.assertTrue(any("published" in finding.message for finding in findings))

    def test_rejects_invalid_content_type(self):
        _, findings = validate_file(self.write(VALID.replace("content_type: lesson", "content_type: handout")))
        self.assertTrue(any("content_type" in finding.message for finding in findings))


if __name__ == "__main__":
    unittest.main()
