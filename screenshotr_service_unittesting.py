import unittest
import os
import time
from tempfile import NamedTemporaryFile

from screenshotr_service import ScreenshotrService
from device_service import DeviceService


class ScreenshotrServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.screenshotr_service = ScreenshotrService()
        self.device_service = DeviceService()

    def _create_device(self):
        udid = self._get_udid()
        device = self.device_service.new_device(udid)
        print("device", device)
        self.assertIsNotNone(device)
        return device

    def _get_udid(self):
        device_service = DeviceService()
        device_list = device_service.get_device_list()
        self.assertIsNotNone(device_list)
        self.assertTrue(len(device_list) > 0)
        return device_list[0]['udid']

    def test_take_screenshot(self):
        device = self._create_device()
        client = self.screenshotr_service.new_client(device)
        self.assertIsNotNone(client)

        imgdata, file_ext = self.screenshotr_service.take_screenshot(client)
        self.assertIsNotNone(imgdata)
        print("imgdata:", imgdata)
        self.screenshotr_service.free_client(client)

        if file_ext == ".data":
            print("WARNING: screenshot data has unexpected image format.")

        tmpfile = NamedTemporaryFile(suffix=file_ext, delete=False)
        tmpfile.write(imgdata)
        tmpfile.close()
        print("png file %s" % tmpfile.name)


if __name__ == '__main__':
    unittest.main()