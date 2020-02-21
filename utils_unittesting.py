import unittest
import os
import time
from tempfile import NamedTemporaryFile

from utils import compare_version, \
    aes_256_cbc_decrypt, aes_256_cbc_encrypt

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


    def test_crypto_aes_256_cbc(self):
        key = b'0' * 32
        data = bytes(map(lambda n: n%256, range(1, 10000)))
        encrypted = aes_256_cbc_encrypt(data, key)
        decrypted = aes_256_cbc_decrypt(encrypted, key)
        self.assertEqual(data, decrypted)

if __name__ == '__main__':
    unittest.main()