import unittest
import os
import time
from tempfile import NamedTemporaryFile

from spring_board_service import SpringBoardService
from device_service import DeviceService


class SpringBoardServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.spring_board_service = SpringBoardService()
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

    def test_get_icon_pngdata(self):
        device = self._create_device()
        client = self.spring_board_service.new_client(device)
        self.assertIsNotNone(client)

        pngdata = self.spring_board_service.get_icon_pngdata(client, "com.apple.Preferences")
        self.assertIsNotNone(pngdata)
        print("pngdata:", pngdata)
        self.spring_board_service.free_client(client)

        tmpfile = NamedTemporaryFile(suffix=".png", delete=False)
        tmpfile.write(pngdata)
        tmpfile.close()
        print("png file %s" % tmpfile.name)


if __name__ == '__main__':
    unittest.main()