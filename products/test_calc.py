import unittest

from . import calc


class InventoryRuleTests(unittest.TestCase):
    def test_reorder_quantity(self):
        self.assertEqual(calc.reorder_quantity(80, 170), 90)
        self.assertEqual(calc.reorder_quantity(200, 170), 0)
        self.assertEqual(calc.reorder_quantity(5, None), 0)

    def test_status_priority(self):
        self.assertEqual(calc.inventory_status(0, 10, 50), calc.STATUS_OUT)
        self.assertEqual(calc.inventory_status(5, 10, 50), calc.STATUS_LOW)
        self.assertEqual(calc.inventory_status(80, 10, 170), calc.STATUS_REORDER)
        self.assertEqual(calc.inventory_status(200, 10, 170), calc.STATUS_OK)
        self.assertEqual(calc.inventory_status(80, 10, None), calc.STATUS_OK)


if __name__ == "__main__":
    unittest.main()
