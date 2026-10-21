"""Run AI-authored JSON cases through a fixed, trusted test harness."""

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import calculate


CASES_FILE = ROOT / "artifacts" / "ai_test_cases.json"


class GeneratedCases(unittest.TestCase):
    pass


def add_case(index: int, case: dict) -> None:
    def test(self):
        expected = case["expected"]
        if isinstance(expected, dict):
            with self.assertRaisesRegex(ValueError, expected["message"]):
                calculate(case["operation"], case["left"], case["right"])
        else:
            actual = calculate(case["operation"], case["left"], case["right"])
            self.assertTrue(math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9),
                            f"expected {expected}, got {actual}")
    setattr(GeneratedCases, f"test_ai_case_{index:02d}", test)


def main() -> int:
    payload = json.loads(CASES_FILE.read_text(encoding="utf-8-sig"))
    for index, case in enumerate(payload["cases"], start=1):
        add_case(index, case)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GeneratedCases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
