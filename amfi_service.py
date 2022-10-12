import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
from libimobiledevice import AMFIError
from libimobiledevice import amfi_client_start_service, amfi_client_free, amfi_set_developer_mode
from libimobiledevice import plist_free
from utils import read_data_from_plist_ptr, compare_version


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))



class AMFIService(Service):
    """
    AMFI
    """

    def new_client(self, device):
        """
        创建amfi client, 用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: amfi client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = amfi_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != AMFIError.AMFI_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放amfi client
        :param client: amfi client(C对象）
        :return: bool 是否成功
        """
        ret = amfi_client_free(client)
        return ret == AMFIError.AMFI_E_SUCCESS

    def set_developer_mode(self, client, mode):
        """
        设置 显示/隐藏"开发者模式"菜单
        :param client: amfi client(C对象)
        :param mode: 0: reveal toggle in settings;
                     1: enable developer mode (only if no passcode is set);
                     2: answers developer mode enable prompt post-restart ?
        :return: 返回码
        """
        ret = amfi_set_developer_mode(client, mode)
        return ret

