"""
test numbers
"""
from django.test import SimpleTestCase

from app import calc

class TestCalc(SimpleTestCase):
    """test addition numbers."""

    def test_number(self):
        """function test addi num."""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)
