import json
import tempfile
import unittest
from pathlib import Path

from timeline_validator import ValidationError, validate_scene_plan, validate_timeline


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        (self.root / "a.png").write_bytes(b"x"); (self.root / "b.png").write_bytes(b"x")

    def tearDown(self): self.temp.cleanup()

    def test_valid_timeline(self):
        value = {"scenes": [
            {"image": "a.png", "start": 0, "end": 1, "motion": "static", "intensity": .05},
            {"image": "b.png", "start": 1, "end": 2, "motion": "push_in", "intensity": .05}]}
        self.assertEqual(len(validate_timeline(value, self.root, audio_duration=2)["scenes"]), 2)

    def test_unknown_key_rejected(self):
        value = {"scenes": [{"image": "a.png", "start": 0, "end": 1,
                              "motoin": "static", "motion": "static", "intensity": .05}]}
        with self.assertRaisesRegex(ValidationError, "motoin"): validate_timeline(value, self.root)

    def test_scene_plan_range(self):
        good = {"scenes": [{"paragraph_start": 1, "paragraph_end": 2, "image_id": "a",
                             "motion": "static", "intensity": .05}]}
        validate_scene_plan(good, 2, {"a"})
        good["scenes"][0]["paragraph_start"] = 2
        with self.assertRaisesRegex(ValidationError, "gapped"): validate_scene_plan(good, 2, {"a"})


if __name__ == "__main__": unittest.main()

