import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
# lockdown
from libimobiledevice import SbservicesError
from libimobiledevice import sbservices_client_start_service, sbservices_client_free, sbservices_get_icon_pngdata, libimobiledevice_free
from libimobiledevice import plist_free, plist_to_bin, plist_to_bin_free, plist_to_xml, plist_to_xml_free
import plistlib

from utils import read_buffer_from_pointer

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class SpringBoardService(Service):
    """
    SprintBoard服务，负责获取应用图标
    """

    def new_client(self, device):
        """
        创建SprintBoard client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: SprintBoard client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = sbservices_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != SbservicesError.SBSERVICES_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放SprintBoard Client
        :param client: SprintBoard client(C对象）
        :return: bool 是否成功
        """
        ret = sbservices_client_free(client)
        return ret == SbservicesError.SBSERVICES_E_SUCCESS

    def get_icon_pngdata(self, client, bundle_id):
        """
        获取应用图标
        :param client: SprintBoard client(C对象)
        :param bundle_id: 应用ID
        :return: 应用图标(PNG data)
        """
        pngdata_p = c_void_p()
        pngsize = c_uint64()

        ret = sbservices_get_icon_pngdata(client, bundle_id.encode("utf-8"), pointer(pngdata_p), pointer(pngsize))
        if ret != SbservicesError.SBSERVICES_E_SUCCESS:
            return None

        buffer = read_buffer_from_pointer(pngdata_p, pngsize.value)
        # print("buffer.length", len(buffer))

        libimobiledevice_free(pngdata_p)
        return buffer
