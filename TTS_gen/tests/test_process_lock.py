import tempfile
import unittest
from pathlib import Path
from process_lock import AlreadyRunningError, ProcessLock


class LockTests(unittest.TestCase):
    def test_contention(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"x.lock"
            with ProcessLock(path):
                with self.assertRaises(AlreadyRunningError): ProcessLock(path).__enter__()
            self.assertFalse(path.exists())


if __name__ == "__main__": unittest.main()
