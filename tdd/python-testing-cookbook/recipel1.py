#!/usr/bin/env python
#-*-coding=utf-8-*-

import sys
import unittest


class RomanNumeralConverter(object):

    def __init__(self, roman_numeral=None):
        self.roman_numeral = roman_numeral
        self.digit_map = {
            'M': 1000,
            'D': 500,
            'C': 100,
            'L': 50,
            'X': 10,
            'V': 5,
            'I': 1,
        }

    def convert_to_decimal(self, roman_numeral=None):
        if roman_numeral:
            self.roman_numeral = roman_numeral

        val = 0
        for char in self.roman_numeral:
            val += self.digit_map[char]

        return val


class RomanNumeralConverterTest(unittest.TestCase):

    def setUp(self):
        self.cvt = RomanNumeralConverter()

    def tearDown(self):
        self.cvt = None

    def test_parsing_millenia_by_cvt(self):
        self.assertEquals(1000, self.cvt.convert_to_decimal('L'))

    def test_parsing_millenia(self):
        value = RomanNumeralConverter('M')
        self.assertEquals(1000, value.convert_to_decimal())

    def test_parsing_century(self):
        value = RomanNumeralConverter('C')
        self.assertEquals(100, value.convert_to_decimal())

    def test_parsing_half_century(self):
        value = RomanNumeralConverter('L')
        self.assertEquals(50, value.convert_to_decimal())

    def test_empty_roman_numeral(self):
        value = RomanNumeralConverter('')
        self.assertTrue(value.convert_to_decimal() == 0)
        self.assertFalse(value.convert_to_decimal() > 0)

    def test_no_roman_numeral(self):
        value = RomanNumeralConverter(None)
        self.assertRaises(TypeError, value.convert_to_decimal)

    def test_fail_message(self):
        value = RomanNumeralConverter(None)
        try:
            value.convert_to_decimal()
            self.fail('Expected a TypeError')
        except TypeError:
            pass


class RomanNumeralComboTest(unittest.TestCase):
    
    def setUp(self):
        self.cvt = RomanNumeralConverter()

    def test_multi_millenia(self):
        self.assertEquals(4000, self.cvt.convert_to_decimal('MMMM'))


if __name__ == '__main__':
    suite = unittest.TestSuite()
    if len(sys.argv) == 1:
        suite1 = unittest.TestLoader().loadTestsFromTestCase( \
                RomanNumeralConverterTest)

        suite2 = unittest.TestLoader().loadTestsFromTestCase( \
                RomanNumeralComboTest)

        suite = unittest.TestSuite([suite1, suite2])
    else:
        # .venv/bin/python chapter1.py test_empty_roman_numeral
        for test_name in sys.argv[1:]:
            suite.addTest(RomanNumeralConverterTest(test_name))

    unittest.TextTestRunner(verbosity=2).run(suite)
