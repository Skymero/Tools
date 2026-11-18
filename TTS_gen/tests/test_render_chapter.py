import json
import tempfile
import unittest
from pathlib import Path

import render_chapter


class RenderChapterTests(unittest.TestCase):
    def test_missing_timeline_records_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "chapter.txt").write_text("hello", encoding="utf-8"); (root / "images").mkdir()
            with self.assertRaises(FileNotFoundError): render_chapter.render_job(root)
            state = json.loads((root / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "failed")

    def test_invalid_job_json_records_failure_and_releases_log(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / "job.json").write_text("{", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError): render_chapter.render_job(root)
            self.assertEqual(json.loads((root / "state.json").read_text(encoding="utf-8"))["status"], "failed")


if __name__ == "__main__": unittest.main()
