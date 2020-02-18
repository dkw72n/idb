import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
from libimobiledevice import MobileImageMounterError, MobileImageMounterUploadCb
from libimobiledevice import mobile_image_mounter_start_service, mobile_image_mounter_free, mobile_image_mounter_lookup_image, mobile_image_mounter_upload_image_file, mobile_image_mounter_mount_image_file, mobile_image_mounter_hangup
from libimobiledevice import plist_free
from utils import read_data_from_plist_ptr, compare_version


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))



class ImageMounterService(Service):
    """
    镜像加载管理服务, 负责镜像加载相关事宜
    """

    def new_client(self, device):
        """
        创建mobile image mounter client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: mobile image mounter client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = mobile_image_mounter_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != MobileImageMounterError.MOBILE_IMAGE_MOUNTER_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放mobile image mounter client
        :param client: mobile image mounter client(C对象）
        :return: bool 是否成功
        """
        ret = mobile_image_mounter_free(client)
        return ret == MobileImageMounterError.MOBILE_IMAGE_MOUNTER_E_SUCCESS

    def lookup_image(self, client, image_type, product_version):
        plist_p = c_void_p()

        ret = mobile_image_mounter_lookup_image(client, image_type.encode("utf-8"), pointer(plist_p))
        if ret != MobileImageMounterError.MOBILE_IMAGE_MOUNTER_E_SUCCESS:
            return False, "Can not lookup image"

        data = read_data_from_plist_ptr(plist_p)
        plist_free(plist_p)
        if not data:
            return False, "Can not parse plist result"

        if "Error" in data:
            error = data['Error']
            return False, error

        if compare_version(product_version, "10.0") >= 0:
            return "ImageSignature" in data, None
        else:
            return data['ImagePresent'] if "ImagePresent" in data else False, None

    def upload_image(self, client, image_type, image_file, image_signature_file):
        ret = mobile_image_mounter_upload_image_file(client, image_type.encode("utf-8"), image_file.encode("utf-8"), image_signature_file.encode("utf-8"))
        return ret == MobileImageMounterError.MOBILE_IMAGE_MOUNTER_E_SUCCESS

    def mount_image(self, client, image_type, image_path, image_signature_file):
        plist_p = c_void_p()

        ret = mobile_image_mounter_mount_image_file(client, image_path.encode("utf-8"),  image_signature_file.encode("utf-8"), image_type.encode("utf-8"), pointer(plist_p))
        if ret != MobileImageMounterError.MOBILE_IMAGE_MOUNTER_E_SUCCESS:
            return False

        data = read_data_from_plist_ptr(plist_p)
        if "Error" in data:
            return False, data['Error']
        return "Status" in data and data['Status'] == "Complete", None

    def hangup(self, client):
        """
        Hangs up mobile image mounter client
        :param client: mobile image mounter client(C对象）
        :return: bool 是否成功
        """
        ret = mobile_image_mounter_hangup(client)
        return ret == MobileImageMounterError.MOBILE_IMAGE_MOUNTER_E_SUCCESS


