import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
from libimobiledevice import SyslogRelayError, SyslogRelayReceiveCb
from libimobiledevice import syslog_relay_client_start_service, syslog_relay_client_free, syslog_relay_start_capture, syslog_relay_stop_capture
from libimobiledevice import plist_free
from utils import read_data_from_plist_ptr, compare_version, read_buffer_from_pointer

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class SyslogRelayService(Service):
    """
    系统日志服务, 负责获取系统日志
    """

    def __init__(self):
        self._callback = None

    def new_client(self, device):
        """
        创建 syslog relay client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: syslog relay client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = syslog_relay_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != SyslogRelayError.SYSLOG_RELAY_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放mobile image mounter client
        :param client: mobile image mounter client(C对象）
        :return: bool 是否成功
        """
        ret = syslog_relay_client_free(client)
        return ret == SyslogRelayError.SYSLOG_RELAY_E_SUCCESS

    def start_capture(self, client, listener):
        def callback(char_data, user_data):
            listener(char_data, user_data)
        user_data = c_void_p()
        self._callback = SyslogRelayReceiveCb(callback)
        ret = syslog_relay_start_capture(client, self._callback, user_data)
        return ret == SyslogRelayError.SYSLOG_RELAY_E_SUCCESS

    def stop_capture(self, client):
        ret = syslog_relay_stop_capture(client)
        return ret == SyslogRelayError.SYSLOG_RELAY_E_SUCCESS
