import tempfile
import unittest
from pathlib import Path

from scripts.check_repository_hygiene import MIB, check_path


class RepositoryHygieneTests(unittest.TestCase):
    def make_file(self, suffix: str = "", size: int = 1) -> Path:
        handle = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        handle.truncate(size)
        handle.close()
        path = Path(handle.name)
        self.addCleanup(path.unlink)
        return path

    def test_accepts_small_source_file(self):
        self.assertEqual(check_path(self.make_file(".md"), "course/lesson.md"), [])

    def test_rejects_pdf(self):
        findings = check_path(self.make_file(".pdf"), "exports/lesson.pdf")
        self.assertTrue(any("PDF" in finding.message for finding in findings))

    def test_rejects_reference_directory(self):
        findings = check_path(self.make_file(), "00 参考资料/book.bin")
        self.assertTrue(any("教材" in finding.message for finding in findings))

    def test_rejects_obsidian_local_state(self):
        findings = check_path(self.make_file(".json"), ".obsidian/workspace-mobile.json")
        self.assertTrue(any("工作区" in finding.message for finding in findings))

    def test_rejects_bundled_obsidian_plugin(self):
        findings = check_path(self.make_file(".js"), ".obsidian/plugins/example/main.js")
        self.assertTrue(any("插件" in finding.message for finding in findings))

    def test_rejects_oversized_image(self):
        findings = check_path(self.make_file(".png", 2 * MIB + 1), "assets/large.png")
        self.assertTrue(any("2 MiB" in finding.message for finding in findings))

    def test_rejects_oversized_other_file(self):
        findings = check_path(self.make_file(".mtx", 5 * MIB + 1), "data/matrix.mtx")
        self.assertTrue(any("5 MiB" in finding.message for finding in findings))


if __name__ == "__main__":
    unittest.main()
