"""Pure standard-library tests; no TeX installation needed for these."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTest(unittest.TestCase):
    def run_stage(self, temp: Path, pdf=True, html=True):
        src = temp / "landing"
        src.mkdir()
        if html:
            (src / "index.html").write_text("<title>Diabat</title>", encoding="utf8")
        (src / "style.css").write_text("body {}", encoding="utf8")
        source_pdf = temp / "main.pdf"
        if pdf:
            source_pdf.write_bytes(b"%PDF-fixture\n")
        target = temp / "output"
        env = dict(os.environ, PDF_SOURCE=str(source_pdf), SITE_SOURCE=str(src),
                   SITE_DEST=str(target), GITHUB_SHA="test-commit")
        result = subprocess.run(["bash", str(ROOT / "tools/stage-pages.sh")],
                                cwd=ROOT, env=env, text=True, capture_output=True)
        return result, source_pdf, target

    def test_happy_path_single_release(self):
        with tempfile.TemporaryDirectory() as d:
            result, source, target = self.run_stage(Path(d))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(source.read_bytes(), (target / "diabat.pdf").read_bytes())
            self.assertTrue((target / ".nojekyll").is_file())
            self.assertTrue((target / "style.css").exists())
            self.assertEqual(json.loads((target / "build-info.json").read_text())["source_commit"],
                             "test-commit")
            result = subprocess.run(["python3", str(ROOT / "tools/validate-site.py"),
                                     str(target), str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_fails_without_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            result, _, _ = self.run_stage(Path(d), pdf=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing or empty compiled PDF", result.stderr)

    def test_fails_without_index(self):
        with tempfile.TemporaryDirectory() as d:
            result, _, _ = self.run_stage(Path(d), html=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no index.html", result.stderr)

    def test_rejects_tampered_site_pdf(self):
        with tempfile.TemporaryDirectory() as d:
            result, source, target = self.run_stage(Path(d))
            self.assertEqual(result.returncode, 0, result.stderr)
            (target / "diabat.pdf").write_bytes(b"DIFFERENT")
            result = subprocess.run(["python3", str(ROOT / "tools/validate-site.py"),
                                     str(target), str(source)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("do not match", result.stderr)


if __name__ == "__main__":
    unittest.main()
