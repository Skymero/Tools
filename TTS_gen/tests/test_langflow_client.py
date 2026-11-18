import unittest
from langflow_client import _extract, build_input


class LangflowTests(unittest.TestCase):
    def test_nested_parser(self):
        plan={"scenes":[]}; self.assertIs(_extract({"outputs":[{"message":plan}]}),plan)
    def test_prompt_numbers_paragraphs(self):
        self.assertIn("Paragraph 2: B",build_input(["A","B"],{"x":"art"}))


if __name__ == "__main__": unittest.main()

