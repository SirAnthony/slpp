#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import six

from slpp import slpp

"""
Tests for slpp
"""


# Utility functions

def is_iterator(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def differ(value, origin):
    if type(value) is not type(origin):
        raise AssertionError('Types does not match: {0}, {1}'.format(type(value), type(origin)))

    if isinstance(origin, dict):
        for key, item in origin.items():
            try:
                differ(value[key], item)
            except KeyError:
                raise AssertionError('''{0} not match original: {1}; Key: {2}, item: {3}'''.format(
                    value, origin, key, item))
        return

    if isinstance(origin, six.string_types):
        assert value == origin, '{0} not match original: {1}.'.format(value, origin)
        return

    if is_iterator(origin):
        for i in range(0, len(origin)):
            try:
                differ(value[i], origin[i])
            except IndexError:
                raise AssertionError(
                    '{0} not match original: {1}. Item {2} not found'.format(
                        value, origin, origin[i]))
        return

    assert value == origin, '{0} not match original: {1}.'.format(value, origin)


class TestUtilityFunctions(unittest.TestCase):

    def test_is_iterator(self):
        self.assertTrue(is_iterator(list()))
        self.assertFalse(is_iterator(int))

    def test_differ(self):
        # Same:
        differ(1, 1)
        differ([2, 3], [2, 3])
        differ({'1': 3, '4': '6'}, {'4': '6', '1': 3})
        differ('4', '4')

        # Different:
        self.assertRaises(AssertionError, differ, 1, 2)
        self.assertRaises(AssertionError, differ, [2, 3], [3, 2])
        self.assertRaises(AssertionError, differ, {'6': 4, '3': '1'}, {'4': '6', '1': 3})
        self.assertRaises(AssertionError, differ, '4', 'no')


class TestSLPP(unittest.TestCase):

    def test_numbers(self):
        # Integer and float:
        self.assertEqual(slpp.decode('3'), 3)
        self.assertEqual(slpp.decode('4.1'), 4.1)
        self.assertEqual(slpp.encode(3), '3')
        self.assertEqual(slpp.encode(4.1), '4.1')

        # Negative float:
        self.assertEqual(slpp.decode('-0.45'), -0.45)
        self.assertEqual(slpp.encode(-0.45), '-0.45')

        # Scientific:
        self.assertEqual(slpp.decode('3e-7'), 3e-7)
        self.assertEqual(slpp.decode('-3.23e+17'), -3.23e+17)
        self.assertEqual(slpp.encode(3e-7), '3e-07')
        self.assertEqual(slpp.encode(-3.23e+17), '-3.23e+17')

        # Hex:
        self.assertEqual(slpp.decode('0x3a'), 0x3a)

        differ(slpp.decode('''{
            ID = 0x74fa4cae,
            Version = 0x07c2,
            Manufacturer = 0x21544948
        }'''), {
            'ID': 0x74fa4cae,
            'Version': 0x07c2,
            'Manufacturer': 0x21544948
        })

    def test_bool(self):
        self.assertEqual(slpp.encode(True), 'true')
        self.assertEqual(slpp.encode(False), 'false')

        self.assertEqual(slpp.decode('true'), True)
        self.assertEqual(slpp.decode('false'), False)

    def test_nil(self):
        self.assertEqual(slpp.encode(None), 'nil')
        self.assertEqual(slpp.decode('nil'), None)

    def test_table(self):
        # Bracketed string key:
        self.assertEqual(slpp.decode('{[10] = 1}'), {10: 1})

        # Void table:
        self.assertEqual(slpp.decode('{nil}'), [])

        # Values-only table:
        self.assertEqual(slpp.decode('{"10"}'), ["10"])

        # Last zero
        self.assertEqual(slpp.decode('{0, 1, 0}'), [0, 1, 0])

    def test_string(self):
        # Escape test:
        self.assertEqual(slpp.decode(r"'test\'s string'"), "test's string")

        # Add escaping on encode:
        self.assertEqual(slpp.encode({'a': 'func("call()");'}), '{\n\ta = "func(\\"call()\\");"\n}')

    def test_basic(self):
        # No data loss:
        data = '{ array = { 65, 23, 5 }, dict = { string = "value", array = { 3, 6, 4}, mixed = { 43, 54.3, false, string = "value", 9 } } }'
        d = slpp.decode(data)
        differ(d, slpp.decode(slpp.encode(d)))

    def test_unicode(self):
        if six.PY2:
            self.assertEqual(slpp.encode(u'Привет'), '"\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82"')
        if six.PY3:
            self.assertEqual(slpp.encode(u'Привет'), '"Привет"')
        self.assertEqual(slpp.encode({'s': u'Привет'}), '{\n\ts = "Привет"\n}')


if __name__ == '__main__':
    unittest.main()
