import unittest
import time

from device_manager import DeviceManager


class DeviceChangeListener(object):

    def on_device_connect(self, device):
        print("connect", device, device.device_info)

    def on_device_disconnect(self, device):
        print("disconnect", device, device.device_info)


class DeviceServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.device_manager = DeviceManager()

    def test_get_connected_devices(self):
        devices = self.device_manager.get_connected_devices()
        print("devices", devices)
        self.assertIsNotNone(devices)
        self.assertTrue(len(devices) > 0)

    def test_listener(self):
        listener = DeviceChangeListener()
        self.device_manager.register_device_change_listener(listener)
        while True:
            pass

if __name__ == '__main__':
    unittest.main()