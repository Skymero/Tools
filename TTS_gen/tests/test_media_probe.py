import shutil
import unittest
from unittest.mock import patch

from media_probe import MediaVerificationError, duration_seconds, probe_media, verify_chapter_output


class MediaProbeTests(unittest.TestCase):
    @patch("media_probe.subprocess.run")
    @patch("media_probe.shutil.which", return_value="ffprobe")
    def test_probe_json(self, _which, run):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "x.mp4"; path.write_bytes(b"x")
            run.return_value.returncode = 0
            run.return_value.stdout = '{"format":{"duration":"1"},"streams":[]}'
            self.assertEqual(duration_seconds(probe_media(path)), 1)
    def test_missing_rejected(self):
        with self.assertRaises(MediaVerificationError): probe_media("missing.mp4")
    @patch("media_probe.probe_media")
    def test_scene_quantization_tolerance_accepted(self, probe):
        probe.return_value = {
            "format": {"duration": "1183.125"},
            "streams": [
                {"codec_type": "video", "codec_name": "h264", "width": 1080, "height": 1920,
                 "avg_frame_rate": "30/1", "duration": "1183.066667"},
                {"codec_type": "audio", "codec_name": "aac", "duration": "1183.125"},
            ],
        }
        verify_chapter_output("x.mp4", {"duration_tolerance": 14 / 30})


if __name__ == "__main__": unittest.main()

