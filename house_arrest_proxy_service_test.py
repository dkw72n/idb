import unittest
import time

from house_arrest_proxy_service import House_arrest_proxy_service
from device_service import DeviceService
from lockdown_service import LockdownService
from afc_service import AfcService


class House_arrest_proxy_serviceTestCase(unittest.TestCase):

    def setUp(self):
        self.house_arrest_proxy_service = House_arrest_proxy_service()
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

    def test_open_sand_box(self):
        device = self._create_device()

        client = self.house_arrest_proxy_service.new_client(device)
        #com.jimmy.test2 
        afcClient = self.house_arrest_proxy_service.open_sandbox_with_appid(client, 1, "com.seasun.tmgp.jx3m")

        self.afc_service = AfcService()
        tmp = self.afc_service.new_client(device)
        dir_list = self.afc_service.read_directory(afcClient, "/Documents")

        self.assertIsNotNone(device)
        self.assertIsNotNone(afcClient)
        self.assertIsNotNone(dir_list)
        self.assertIsNotNone(client)

        for file in dir_list:
            print(file['filename'])
           
        self.afc_service.free_client(afcClient)
        self.device_service.free_device(device)
        self.house_arrest_proxy_service.free_client(client)


if __name__ == '__main__':
    unittest.main()