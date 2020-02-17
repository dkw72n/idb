import unittest
import os
import time
from tempfile import NamedTemporaryFile

from image_mounter_service import ImageMounterService
from device_service import DeviceService


class ImageMounterServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.image_mounter_service = ImageMounterService()
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

    def test_lookup_image(self):
        device = self._create_device()
        client = self.image_mounter_service.new_client(device)
        self.assertIsNotNone(client)

        product_version = "13.2"
        image_type = "Developer"

        image_mounted, error = self.image_mounter_service.lookup_image(client, image_type, product_version)
        print(error)
        self.assertIsNone(error)
        self.assertTrue(image_mounted)
        self.image_mounter_service.hangup(client)
        self.image_mounter_service.free_client(client)

    def test_upload_and_mount_image(self):
        device = self._create_device()
        client = self.image_mounter_service.new_client(device)
        self.assertIsNotNone(client)

        image_type = "Developer"
        image_file = r"F:\lds\DeviceSupport\DeviceSupport\13.3\DeveloperDiskImage.dmg"
        image_signature_file = r"F:\lds\DeviceSupport\DeviceSupport\13.3\DeveloperDiskImage.dmg.signature"

        result = self.image_mounter_service.upload_image(client, image_type, image_file, image_signature_file)
        print("result", result)
        self.assertTrue(result)

        image_type = "Developer"
        image_path = "/private/var/mobile/Media/PublicStaging/staging.dimage"
        image_signature_file = r"F:\lds\DeviceSupport\DeviceSupport\13.3\DeveloperDiskImage.dmg.signature"

        result, error = self.image_mounter_service.mount_image(client, image_type, image_path, image_signature_file)
        print("result", result, error)
        self.assertIsNone(error)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()