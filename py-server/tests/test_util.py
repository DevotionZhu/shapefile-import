import unittest

from shape_importer.util import groupsgen


class UtilTest(unittest.TestCase):

    def test_simple(self):
        self.assertEqual("42 is the answer", str(42) + " " + "is the answer")


class Util1Test(unittest.TestCase):

    def test_simple1(self):
        self.assertEqual("42 is the answer", str(42) + " " + "is the answer")
