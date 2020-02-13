import unittest
import time

from installation_proxy_service import InstallationProxyService
from device_service import DeviceService
from lockdown_service import LockdownService


class InstallationProxyServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.installation_proxy_service = InstallationProxyService()
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

    def test_browse(self):
        device = self._create_device()
        client = self.installation_proxy_service.new_client(device)

        apps = self.installation_proxy_service.browse(client, "User")
        self.assertIsNotNone(apps)
        self.assertTrue(len(apps) > 0)
        print("List of applications:")
        for app in apps:
            for key, value in app.items():
                print("%s: %s" % (key, value))
            print("")
        self.installation_proxy_service.free_client(client)


if __name__ == '__main__':
    unittest.main()