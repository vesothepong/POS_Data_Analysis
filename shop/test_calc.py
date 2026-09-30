import unittest

from . import calc


class CartMathTests(unittest.TestCase):
    def test_totals_and_subtotals(self):
        items, total = calc.cart_totals([{"quantity": 2, "price": 10.0}, {"quantity": 3, "price": 5.5}])
        self.assertEqual([it["subtotal"] for it in items], [20.0, 16.5])
        self.assertEqual(total, 36.5)

    def test_empty_cart(self):
        items, total = calc.cart_totals([])
        self.assertEqual((items, total), ([], 0))


if __name__ == "__main__":
    unittest.main()
