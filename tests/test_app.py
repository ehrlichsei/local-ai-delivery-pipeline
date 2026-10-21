import unittest

from app import calculate


class CalculateTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(calculate("add", 2, 3), 5)

    def test_divide_by_zero_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "zero"):
            calculate("divide", 1, 0)


if __name__ == "__main__":
    unittest.main()
