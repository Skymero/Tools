import unittest
from google_drive_auth import AuthAttentionError
from google_drive_client import RetryableDriveError, classify_error, normalize_google_doc


class Error:
    def __init__(self, status): self.resp = type("Response", (), {"status": status})()


class DriveClientTests(unittest.TestCase):
    def test_classification(self):
        self.assertIs(classify_error(Error(429)), RetryableDriveError)
        self.assertIs(classify_error(Error(500)), RetryableDriveError)
        self.assertIs(classify_error(Error(401)), AuthAttentionError)
    def test_doc_normalization(self):
        self.assertEqual(normalize_google_doc(" A\r\n\r\n\r\nB "), "A\n\nB\n")


if __name__ == "__main__": unittest.main()

