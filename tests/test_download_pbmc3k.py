import hashlib
import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.download_pbmc3k import extract_verified, sha256_file, verify_files


class DownloadPbmc3kTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_sha256_file(self):
        path = self.root / "value.txt"
        path.write_bytes(b"BioEZ")
        self.assertEqual(sha256_file(path), hashlib.sha256(b"BioEZ").hexdigest())

    def test_verify_files_reports_missing_and_mismatch(self):
        (self.root / "bad.txt").write_bytes(b"bad")
        expected = {
            "missing.txt": hashlib.sha256(b"missing").hexdigest(),
            "bad.txt": hashlib.sha256(b"good").hexdigest(),
        }
        errors = verify_files(self.root, expected)
        self.assertEqual(len(errors), 2)

    def test_extract_verified_selects_and_checks_members(self):
        archive = self.root / "sample.tar.gz"
        payload = b"verified matrix"
        with tarfile.open(archive, "w:gz") as bundle:
            member = tarfile.TarInfo("source/matrix.mtx")
            member.size = len(payload)
            bundle.addfile(member, io.BytesIO(payload))
            ignored = tarfile.TarInfo("source/ignored.txt")
            ignored.size = 7
            bundle.addfile(ignored, io.BytesIO(b"ignored"))
        output = self.root / "output"
        mapping = {
            "source/matrix.mtx": ("matrix.mtx", hashlib.sha256(payload).hexdigest()),
        }
        extract_verified(archive, output, mapping)
        self.assertEqual((output / "matrix.mtx").read_bytes(), payload)
        self.assertFalse((output / "ignored.txt").exists())


if __name__ == "__main__":
    unittest.main()
