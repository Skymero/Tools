import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_drive_queue


class EmptyClient:
    def list_children(self, _): return []


class QueueTests(unittest.TestCase):
    def test_no_work(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {
                "DRIVE_INCOMING_FOLDER_ID": "in", "DRIVE_FINISHED_FOLDER_ID": "out"}):
            self.assertEqual(run_drive_queue.process_once(EmptyClient(), work_root=Path(d)/"work", db_path=Path(d)/"state.db"), "no-work")

    def test_snapshot_rejects_multiple_chapters(self):
        class Client:
            def download(self, _id, destination, google_doc=False): Path(destination).write_text("x", encoding="utf-8")
        files = [{"id":"1","name":"chapter.txt","mimeType":"text/plain"},
                 {"id":"2","name":"Chapter","mimeType":"application/vnd.google-apps.document"}]
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(RuntimeError, "multiple chapter"):
                run_drive_queue._snapshot(Client(), files, Path(d)/"job")


if __name__ == "__main__": unittest.main()
