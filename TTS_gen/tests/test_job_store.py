import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

import job_store


class JobStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.db = job_store.init(Path(self.temp.name) / "state.db")
    def tearDown(self): self.db.close(); self.temp.cleanup()
    def test_create_transition_and_reserve(self):
        files = [{"id": "b", "name": "b", "modifiedTime": "2"}, {"id": "a", "name": "a", "modifiedTime": "1"}]
        fp = job_store.fingerprint(files)
        job_id = job_store.create_job(self.db, "folder", fp, files)
        self.assertEqual(job_id, job_store.create_job(self.db, "folder", fp, files))
        self.assertTrue(job_store.transition(self.db, job_id, "discovered", "snapshotting"))
        self.assertFalse(job_store.transition(self.db, job_id, "discovered", "ready"))
        reservation = job_store.reserve(self.db, job_id, "model", 10, datetime.now(timezone.utc).isoformat())
        self.assertGreater(reservation, 0)


if __name__ == "__main__": unittest.main()

