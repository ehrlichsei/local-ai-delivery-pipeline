import io
import json
import os
import unittest
from unittest.mock import patch

from gemini_client import generate, parse_json_object


class ParseModelOutputTests(unittest.TestCase):
    def test_parses_plain_json(self):
        self.assertEqual(parse_json_object('{"cases": []}'), {"cases": []})

    def test_parses_fenced_json(self):
        self.assertEqual(parse_json_object('```json\n{"cases": []}\n```'), {"cases": []})

    def test_rejects_missing_json(self):
        with self.assertRaises(ValueError):
            parse_json_object("no structured answer")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"})
    @patch("gemini_client.urllib.request.urlopen")
    def test_calls_gemini_and_extracts_text(self, mock_urlopen):
        response = io.BytesIO(json.dumps({
            "candidates": [{"content": {"parts": [{"text": "{\"cases\":[]}"}]}}]
        }).encode())
        mock_urlopen.return_value = response

        result = generate("prompt", system="system")

        self.assertEqual(result, '{"cases":[]}')
        request = mock_urlopen.call_args.args[0]
        self.assertIn("/models/test-model:generateContent", request.full_url)
        self.assertEqual(request.get_header("X-goog-api-key"), "test-key")


if __name__ == "__main__":
    unittest.main()
