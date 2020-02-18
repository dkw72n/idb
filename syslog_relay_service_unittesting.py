import unittest
import os
import time
from tempfile import NamedTemporaryFile

from syslog_relay_service import SyslogRelayService
from device_service import DeviceService


class SyslogRelayServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.syslog_relay_service = SyslogRelayService()
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

    def test_start_capture(self):
        device = self._create_device()
        client = self.syslog_relay_service.new_client(device)
        self.assertIsNotNone(client)

        def callback(char_data, user_data):
            print(char_data, end="")
        result = self.syslog_relay_service.start_capture(client, callback)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()