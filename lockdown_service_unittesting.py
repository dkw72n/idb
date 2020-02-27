import unittest
import time

from device_service import DeviceService
from lockdown_service import LockdownService

from libimobiledevice import plist_new_string,plist_new_bool

class LockdownServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.device_service = DeviceService()
        self.lockdown_service = LockdownService()

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

    def test_new_client(self):
        device = self._create_device()
        client = self.lockdown_service.new_client(device)
        print("client", client)
        self.assertIsNotNone(client)
        self.lockdown_service.free_client(client)
        self.device_service.free_device(device)

    def test_get_value(self):
        device = self._create_device()
        client = self.lockdown_service.new_client(device)
        print("client", client)
        self.assertIsNotNone(client)
        #values = self.lockdown_service.get_value(client, "ProductVersion")
        values = self.lockdown_service.get_value(client, None)
        print("values", type(values), values)
        # self.assertTrue("DeviceName" in values)
        # self.assertTrue("UniqueDeviceID" in values)
        # self.assertTrue("ProductVersion" in values)
        self.lockdown_service.free_client(client)
        self.device_service.free_device(device)

    def test_get_domain_value(self):
        device = self._create_device()
        client = self.lockdown_service.new_client(device)
        print("client", client)
        self.assertIsNotNone(client)
        #values = self.lockdown_service.get_value(client, "ProductVersion")
        values = self.lockdown_service.get_domain_Value(client,"com.apple.iTunes", None)
        print("values", type(values), values)
       
        self.lockdown_service.free_client(client)
        self.device_service.free_device(device)

    def test_set_domain_value(self):
        device = self._create_device()
        client = self.lockdown_service.new_client(device)
        print("client", client)
        self.assertIsNotNone(client)
        #values = self.lockdown_service.get_value(client, "ProductVersion")
        values = self.lockdown_service.get_domain_Value(client,None, None)
        #print("before values", type(values), values)
        
    
        #self.lockdown_service.set_domain_Value(client,"com.apple.mobile.wireless_lockdown","EnableWifiConnections",plist_new_bool(0))
        self.lockdown_service.set_domain_Value(client,None,"DeviceName",plist_new_string("DeviceName".encode("utf-8")))
        values = self.lockdown_service.get_domain_Value(client,None, None)
        print("after values", type(values), values)
        self.lockdown_service.free_client(client)
        self.device_service.free_device(device)

if __name__ == '__main__':
    unittest.main()