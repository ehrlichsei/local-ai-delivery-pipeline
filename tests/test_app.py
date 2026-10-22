import unittest

from app import calculate


class CalculateTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(calculate("add", 2, 3), 5)

    def test_subtract(self):
        self.assertEqual(calculate("subtract", 8, 3), 5)

    def test_multiply(self):
        self.assertEqual(calculate("multiply", 4, 3), 12)

    def test_divide(self):
        self.assertEqual(calculate("divide", 12, 3), 4)

    def test_power(self):
        self.assertEqual(calculate("power", 2, 3), 8)

    def test_power_zero_exponent(self):
        self.assertEqual(calculate("power", 7, 0), 1)

    def test_modulo_positive_remainder(self):
        self.assertEqual(calculate("modulo", 5, 3), 2)

    def test_modulo_negative_left(self):
        self.assertEqual(calculate("modulo", -5, 3), 1)

    def test_divide_by_zero_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "zero"):
            calculate("divide", 1, 0)

    def test_modulo_by_zero_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "zero"):
            calculate("modulo", 5, 0)

    def test_unknown_operation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown operation"):
            calculate("unknown", 1, 2)


if __name__ == "__main__":
    unittest.main()
