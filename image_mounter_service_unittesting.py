import unittest
import time

from image_mounter_service import ImageMounterService


class ImageMounterServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.image_mounter_service = ImageMounterService()

    def test_lookup_image(self):
        pass # TODO


if __name__ == '__main__':
    unittest.main()