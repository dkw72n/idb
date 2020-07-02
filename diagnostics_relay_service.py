import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
from libimobiledevice import DiagnosticsRelayError
from libimobiledevice import diagnostics_relay_client_start_service, diagnostics_relay_client_free, diagnostics_relay_goodbye, diagnostics_relay_query_ioregistry_entry
from libimobiledevice import plist_free
from utils import read_data_from_plist_ptr, compare_version, read_buffer_from_pointer

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class DiagnosticsRelayService(Service):
    """
    收集诊断信息, 负责获取电池等数据
    """

    def new_client(self, device):
        """
        创建diagnostics relay client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: diagnostics relay client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = diagnostics_relay_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != DiagnosticsRelayError.DIAGNOSTICS_RELAY_E_SUCCESS:
            return None
        return client

    def goodbye(self, client):
        """
        断开diagnostics relay client连接
        :param client: diagnostics relay client(C对象）
        :return: bool 是否成功
        """
        ret = diagnostics_relay_goodbye(client)
        return ret == DiagnosticsRelayError.DIAGNOSTICS_RELAY_E_SUCCESS

    def free_client(self, client):
        """
        释放diagnostics relay  client
        :param client: diagnostics relay client(C对象）
        :return: bool 是否成功
        """
        ret = diagnostics_relay_client_free(client)
        return ret == DiagnosticsRelayError.DIAGNOSTICS_RELAY_E_SUCCESS

    def query_ioregistry_entry(self, client, name, clazz):
        plist_p = c_void_p()
        ret = diagnostics_relay_query_ioregistry_entry(client, name.encode("utf-8"), clazz.encode("utf-8"), pointer(plist_p))
        if ret != DiagnosticsRelayError.DIAGNOSTICS_RELAY_E_SUCCESS:
            return False, "Can not query ioregistry entry, error code %d" % ret

        data = read_data_from_plist_ptr(plist_p)
        plist_free(plist_p)

        if data is None:
            return False, "Can not parse plist result"
        return True, data
