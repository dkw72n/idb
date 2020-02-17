import unittest
import os
import time
from tempfile import NamedTemporaryFile

from utils import compare_version

class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_compare_version(self):
        self.assertTrue(compare_version("2", "1") > 0)
        self.assertTrue(compare_version("2", "1.0") > 0)
        self.assertTrue(compare_version("2", "1.0.3") > 0)

        self.assertTrue(compare_version("2.0", "1") > 0)
        self.assertTrue(compare_version("2.0", "1.0") > 0)
        self.assertTrue(compare_version("2.0", "1.0.3") > 0)

        self.assertTrue(compare_version("2.0.0", "1") > 0)
        self.assertTrue(compare_version("2.0.0", "1.0") > 0)
        self.assertTrue(compare_version("2.0.0", "1.0.3") > 0)

        # self.assertTrue(compare_version("1.0", "1.0.0") == 0)


if __name__ == '__main__':
    unittest.main()