import io
import unittest
from unittest.mock import patch

import gemini_client


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *_): pass


class GeminiClientTests(unittest.TestCase):
    @patch("gemini_client.urllib.request.urlopen", return_value=Response(b'{"totalTokens":12}'))
    def test_count_tokens(self, _):
        self.assertEqual(gemini_client.count_tokens("hello", model="m", api_key="k"), 12)


if __name__ == "__main__": unittest.main()
