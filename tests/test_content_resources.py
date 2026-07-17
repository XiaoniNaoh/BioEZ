import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.check_content_resources import main, scan_repository


class ContentResourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, relative: str, content: str | bytes = "") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def write_generated_manifest(self, relative: str, content: bytes) -> None:
        self.write("scripts/generator.py", "# deterministic test generator\n")
        manifest = {
            "schema_version": 2,
            "assets": [{
                "path": relative,
                "source_type": "project-generated",
                "generated_by": "scripts/generator.py",
                "generator_seed": 1,
                "sha256": hashlib.sha256(content).hexdigest(),
                "license": "CC-BY-SA-4.0",
            }],
        }
        self.write("assets/image-sources.json", json.dumps(manifest))

    def codes(self):
        return [finding.code for finding in scan_repository(self.root).findings]

    def test_accepts_resolved_wikilink_local_image_and_manifest(self):
        image = b"<svg/>"
        self.write("assets/generated/figure.svg", image)
        self.write_generated_manifest("assets/generated/figure.svg", image)
        self.write("01 Course/00 目录.md", "[[Lesson]]\n")
        self.write("01 Course/Lesson.md", "# Lesson\n\n![有意义的替代文本](../assets/generated/figure.svg)\n")
        report = scan_repository(self.root)
        self.assertEqual(report.summary["errors"], 0)
        self.assertEqual(report.summary["orphan_pages"], 0)
        self.assertEqual(report.summary["unreferenced_assets"], 0)

    def test_reports_remote_image_missing_alt_and_broken_targets(self):
        self.write(
            "01 Course/Lesson.md",
            "![](https://example.test/image.png)\n[[Missing page]]\n[missing](missing.md)\n",
        )
        codes = self.codes()
        self.assertIn("remote-image", codes)
        self.assertIn("missing-alt", codes)
        self.assertIn("broken-wikilink", codes)
        self.assertIn("broken-link", codes)

    def test_ignores_link_examples_inside_code(self):
        self.write(
            "docs/example.md",
            "```markdown\n![](https://example.test/image.png)\n[[Missing]]\n```\n`[[Also missing]]`\n",
        )
        report = scan_repository(self.root)
        self.assertEqual(report.summary["remote_images"], 0)
        self.assertEqual(report.summary["broken_links"], 0)

    def test_reports_ambiguous_wikilink_and_missing_heading(self):
        self.write("01 Course/One/Topic.md", "# First\n")
        self.write("01 Course/Two/Topic.md", "# Second\n")
        self.write("01 Course/Source.md", "[[Topic]]\n[[One/Topic#Absent]]\n")
        codes = self.codes()
        self.assertIn("ambiguous-wikilink", codes)
        self.assertIn("broken-heading", codes)

    def test_reports_unreferenced_asset_and_checksum_drift(self):
        image = b"<svg>changed</svg>"
        self.write("assets/generated/figure.svg", image)
        self.write_generated_manifest("assets/generated/figure.svg", b"<svg>original</svg>")
        codes = self.codes()
        self.assertIn("unreferenced-asset", codes)
        self.assertIn("checksum-mismatch", codes)

    def test_records_existing_project_asset_as_unknown_origin_warning(self):
        image = b"png"
        relative = "01 Course/image.png"
        self.write(relative, image)
        self.write("01 Course/Lesson.md", "![质控截图](image.png)\n")
        manifest = {
            "schema_version": 2,
            "assets": [{
                "path": relative,
                "source_type": "existing-project-asset",
                "custody_status": "existing-in-project-repository",
                "origin_status": "unknown",
                "sha256": hashlib.sha256(image).hexdigest(),
                "license": "not-asserted",
            }],
        }
        self.write("assets/image-sources.json", json.dumps(manifest))
        report = scan_repository(self.root)
        self.assertIn("origin-metadata-missing", [finding.code for finding in report.findings])
        self.assertEqual(report.summary["license_review_required"], 1)

    def test_report_schema_is_stable(self):
        self.write("README.md", "# Test\n")
        payload = scan_repository(self.root).to_dict()
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(set(payload), {"schema_version", "summary", "findings", "orphans", "unreferenced_assets"})
        for key in ("markdown_files", "image_assets", "remote_images", "orphan_pages", "errors", "warnings"):
            self.assertIn(key, payload["summary"])

    def test_committed_report_drift_check(self):
        self.write("README.md", "# Test\n")
        arguments = ["--root", str(self.root)]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(arguments + ["--json-report", "data/quality-report.json"]), 0)
            self.assertEqual(main(arguments + ["--check-report", "data/quality-report.json"]), 0)
            self.write("README.md", "# Changed\n\n[missing](missing.md)\n")
            self.assertEqual(main(arguments + ["--check-report", "data/quality-report.json"]), 1)


if __name__ == "__main__":
    unittest.main()
