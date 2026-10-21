import unittest

from generate_tests import parse_json_object


class ParseModelOutputTests(unittest.TestCase):
    def test_parses_plain_json(self):
        self.assertEqual(parse_json_object('{"cases": []}'), {"cases": []})

    def test_parses_fenced_json(self):
        self.assertEqual(parse_json_object('```json\n{"cases": []}\n```'), {"cases": []})

    def test_rejects_missing_json(self):
        with self.assertRaises(ValueError):
            parse_json_object("no structured answer")


if __name__ == "__main__":
    unittest.main()
