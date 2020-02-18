import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
from libimobiledevice import ScreenshotrError
from libimobiledevice import screenshotr_client_start_service, screenshotr_client_free, screenshotr_take_screenshot, libimobiledevice_free
from libimobiledevice import plist_free
from utils import read_data_from_plist_ptr, compare_version, read_buffer_from_pointer

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))



class ScreenshotrService(Service):
    """
    截图服务, 负责截图
    """

    def new_client(self, device):
        """
        创建 screenshotr client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: screenshotr client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = screenshotr_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != ScreenshotrError.SCREENSHOTR_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放mobile image mounter client
        :param client: mobile image mounter client(C对象）
        :return: bool 是否成功
        """
        ret = screenshotr_client_free(client)
        return ret !=  ScreenshotrError.SCREENSHOTR_E_SUCCESS

    def take_screenshot(self, client):
        imgdata_p = c_void_p()
        imgsize = c_uint64()

        ret = screenshotr_take_screenshot(client, pointer(imgdata_p), pointer(imgsize))
        if ret != ScreenshotrError.SCREENSHOTR_E_SUCCESS:
            return None, None

        buffer = read_buffer_from_pointer(imgdata_p, imgsize.value)

        if buffer.startswith(b"\x89PNG"):
            file_ext = ".png"
        elif buffer.startswith(b"MM\x00*"):
            file_ext = ".tiff"
        else:
            file_ext = ".dat" # print("WARNING: screenshot data has unexpected image format.")

        libimobiledevice_free(imgdata_p)
        return buffer, file_ext

