import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import gemini_quota, job_store


class QuotaTests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(); self.db=job_store.init(Path(self.temp.name)/"q.db")
    def tearDown(self): self.db.close(); self.temp.cleanup()
    def test_policy_and_reconcile(self):
        item=gemini_quota.reserve_quota(self.db,job_id=None,model="m",estimated_tokens=80,token_limit=100,now=datetime(2026,1,1,tzinfo=timezone.utc))
        gemini_quota.reconcile(self.db,item,70)
        with self.assertRaises(gemini_quota.QuotaHoldError): gemini_quota.reserve_quota(self.db,job_id=None,model="m",estimated_tokens=11,token_limit=100,now=datetime(2026,1,1,tzinfo=timezone.utc))
    def test_missing_config_holds(self):
        with self.assertRaises(gemini_quota.QuotaHoldError): gemini_quota.reserve_quota(self.db,job_id=None,model="m",estimated_tokens=1,token_limit=0)


if __name__ == "__main__": unittest.main()

