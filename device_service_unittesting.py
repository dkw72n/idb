import unittest
import time

from device_service import DeviceService
from lockdown_service import LockdownService


class DeviceServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.device_service = DeviceService()

    def _get_udid(self):
        device_service = DeviceService()
        device_list = device_service.get_device_list()
        self.assertIsNotNone(device_list)
        self.assertTrue(len(device_list) > 0)
        return device_list[0]['udid']

    def test_get_device_info(self):
        device_list = self.device_service.get_device_list()
        print("device_list", device_list)
        self.assertIsNotNone(device_list, msg="Device List is None")
        self.assertTrue(len(device_list) > 0, msg="Device List is Empty")

    def test_subscribe(self):
        def on_device_changed(event):
            print("on_device_changed", event)
        self.device_service.subscribe(on_device_changed)
        retry = 0
        while retry < 20:
            print("wait for device event...", retry)
            time.sleep(1)
            retry += 1
        self.device_service.subscribe()

    def test_new_device(self):
        udid = self._get_udid()
        device = self.device_service.new_device(udid)
        print("device", device)
        self.assertIsNotNone(device)
        success = self.device_service.free_device(device)
        self.assertTrue(success)
        print("free device")


if __name__ == '__main__':
    unittest.main()