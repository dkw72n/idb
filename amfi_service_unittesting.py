import unittest

from amfi_service import AMFIService
from device_service import DeviceService


class AMFIServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.amfi_service = AMFIService()
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

    def test_set_developer_mode(self):
        device = self._create_device()
        client = self.amfi_service.new_client(device)
        self.assertIsNotNone(client)

        mode = 0 # reveal toggle in settings
        ret = self.amfi_service.set_developer_mode(client, mode)
        print(ret)
        self.assertTrue(ret == 0)
        self.amfi_service.free_client(client)

if __name__ == '__main__':
    unittest.main()