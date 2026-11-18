import unittest
from unittest.mock import patch

import create_mp4


class CreateMp4Tests(unittest.TestCase):
    def test_filter_has_dimensions(self):
        value = create_mp4._video_filter({"motion": "static", "intensity": .05}, 1080, 1920, 30)
        self.assertIn("1080:1920", value)
    @patch("create_mp4.shutil.which", return_value=None)
    def test_missing_tool_is_clear(self, _):
        with self.assertRaisesRegex(create_mp4.RenderError, "ffmpeg"): create_mp4._tool("ffmpeg")
    def test_default_duration_tolerance_allows_one_frame_per_segment(self):
        self.assertAlmostEqual(create_mp4._render_duration_tolerance(14, 30), 14 / 30)
    def test_explicit_duration_tolerance_is_preserved(self):
        self.assertEqual(create_mp4._render_duration_tolerance(14, 30, 0.1), 0.1)


if __name__ == "__main__": unittest.main()

