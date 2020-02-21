import unittest
import os
import time
from tempfile import NamedTemporaryFile

from afc_service import AfcService
from device_service import DeviceService


class AfcServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.afc_service = AfcService()
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

    def test_read_directory(self):
        device = self._create_device()
        client = self.afc_service.new_client(device)
        self.assertIsNotNone(client)

        dir_list = self.afc_service.read_directory(client, ".")
        self.assertIsNotNone(dir_list)

        for file in dir_list:
            print(file['filename'], file['st_ifmt'], file['st_size'])
            if file['st_ifmt'] == "S_IFDIR":
                sub_dir_list = self.afc_service.read_directory(client, file['filepath'])
                for subfile in sub_dir_list:
                    print("\t", subfile['filename'], subfile['st_ifmt'], subfile['st_size'])

        self.afc_service.free_client(client)
        self.device_service.free_device(device)

    def test_read_file(self):
        device = self._create_device()
        client = self.afc_service.new_client(device)
        self.assertIsNotNone(client)

        filename = "./Downloads/downloads.28.sqlitedb"
        afc_file = self.afc_service.open_file(client, filename, "r")
        while True:
            buffer = afc_file.read(1024)
            if not buffer:
                print("EOF")
                break
            print(buffer)
        afc_file.close()

        self.afc_service.free_client(client)
        self.device_service.free_device(device)

    def test_make_directory(self):
        device = self._create_device()
        client = self.afc_service.new_client(device)
        self.assertIsNotNone(client)

        dirname = "./Downloads/Test/Test1/Test2/Test3"
        success = self.afc_service.make_directory(client, dirname)
        self.assertTrue(success)

        self.afc_service.free_client(client)
        self.device_service.free_device(device)

    def test_remove_path(self):
        device = self._create_device()
        client = self.afc_service.new_client(device)
        self.assertIsNotNone(client)

        dirname = "./Downloads/Test/Test1/Test2/Test3"
        success = self.afc_service.remove_path(client, dirname)
        self.assertTrue(success)

        self.afc_service.free_client(client)
        self.device_service.free_device(device)

    def test_write_file(self):
        device = self._create_device()
        client = self.afc_service.new_client(device)
        self.assertIsNotNone(client)

        filename = "./Downloads/test.txt"
        afc_file = self.afc_service.open_file(client, filename, "w")
        afc_file.write(b"test")
        afc_file.close()

        self.afc_service.free_client(client)
        self.device_service.free_device(device)


if __name__ == '__main__':
    unittest.main()