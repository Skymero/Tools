import unittest
from scene_audio import paragraphs


class SceneAudioTests(unittest.TestCase):
    def test_paragraph_split(self): self.assertEqual(paragraphs(" A\r\n\r\n B "),["A","B"])


if __name__ == "__main__": unittest.main()

