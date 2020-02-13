import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
# lockdown
from libimobiledevice import InstProxyError
from libimobiledevice import instproxy_client_start_service, instproxy_client_free, instproxy_browse, instproxy_client_options_new, instproxy_client_options_add, instproxy_client_options_set_return_attributes, instproxy_client_options_free
from libimobiledevice import plist_free, plist_to_bin, plist_to_bin_free, plist_to_xml, plist_to_xml_free
import plistlib

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

def read_buffer_from_pointer(pointer, length):
    return bytes(cast(pointer, POINTER(c_char))[:length])
    #return bytes(cast(pointer, POINTER(c_byte))[:length])


class InstallationProxyService(Service):
    """
    InstallationProxy服务，负责获取已安装应用列表等事宜
    """

    def new_client(self, device):
        """
        创建installation proxy client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: lockdown client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = instproxy_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != InstProxyError.INSTPROXY_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放installation proxy
        :param client: installation proxy client(C对象）
        :return: bool 是否成功
        """
        ret = instproxy_client_free(client)
        return ret != InstProxyError.INSTPROXY_E_SUCCESS

    def browse(self, client, application_type):
        """
        获取已安装应用列表
        :param client: installation proxyclient(C对象)
        :param application_type: 应用类型："User" 用户应用, "System" 系统应用
        :return: 应用列表
        """
        p_list_p = c_void_p()
        client_opts_p = instproxy_client_options_new()
        instproxy_client_options_add(client_opts_p, "ApplicationType".encode("utf-8"), application_type.encode("utf-8"), None)
        instproxy_client_options_set_return_attributes(client_opts_p,
                                                       "CFBundleIdentifier".encode("utf-8"),
                                                       "CFBundleExecutable".encode("utf-8"),
                                                       "CFBundleName".encode("utf-8"),
                                                       "CFBundleVersion".encode("utf-8"),
                                                       "CFBundleShortVersionString".encode("utf-8"),
                                                       "Path".encode("utf-8"),
                                                       None) # TODO: 目前暂未找到ctypes如何支持可变参数，因此这里参数个数是硬写的，如果需要增加参考需要同步修改ctypes配置
        instproxy_browse(client, client_opts_p, pointer(p_list_p))
        # TODO: p_list_p is null?

        plist_bin_p = c_void_p()
        length = c_int()
        plist_to_bin(p_list_p, pointer(plist_bin_p), pointer(length))

        buffer = read_buffer_from_pointer(plist_bin_p, length.value)
        # print("buffer.length", len(buffer))
        app_list = None
        if buffer and len(buffer) > 0:
            app_list = plistlib.loads(buffer)
        plist_to_bin_free(plist_bin_p)
        plist_free(p_list_p)
        instproxy_client_options_free(client_opts_p)
        return app_list
