import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
# lockdown
from libimobiledevice import LockdowndError
from libimobiledevice import lockdownd_client_new, lockdownd_client_free, lockdownd_get_value
from libimobiledevice import plist_free, plist_to_bin, plist_to_bin_free, plist_to_xml, plist_to_xml_free
from bpylist import archiver, bplist
import plistlib

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

def read_buffer_from_pointer(pointer, length):
    return bytes(cast(pointer, POINTER(c_char))[:length])
    #return bytes(cast(pointer, POINTER(c_byte))[:length])

class LockdownService(Service):
    """
    Lockdown服务，负责获取设备属性
    """

    def new_client(self, device):
        """
        创建lockdown client，用于调用lockdown服务的其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: lockdown client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = lockdownd_client_new(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != LockdowndError.LOCKDOWN_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放lockdown client
        :param client: lockdown client(C对象）
        :return: bool 是否成功
        """
        ret = lockdownd_client_free(client)
        return ret != LockdowndError.LOCKDOWN_E_SUCCESS

    def get_value(self, client, key):
        """
        获取设备属性值
        :param client: lockdown client(C对象)
        :param key: 属性名称
        :return: 属性值
        """
        values = None
        p_list_p = c_void_p()
        ret = lockdownd_get_value(client, None, key.encode("utf-8") if key else None, pointer(p_list_p))
        if ret != LockdowndError.LOCKDOWN_E_SUCCESS:
            return None, "Can not new idevice"

        plist_bin_p = c_void_p()
        length = c_int()
        plist_to_bin(p_list_p, pointer(plist_bin_p), pointer(length))
        #print("length", length.value)

        buffer = read_buffer_from_pointer(plist_bin_p, length.value)
        #print("buffer.length", len(buffer))
        if buffer and len(buffer) > 0:
            values = plistlib.loads(buffer)
        plist_to_bin_free(plist_bin_p)
        plist_free(p_list_p)
        return values


"""
get_value:
{
    'BasebandCertId': 2315222105,
    'BasebandKeyHashInformation': {
        'AKeyStatus': 2,
        'SKeyHash': b'\xbb\xef\xedp,/i\x0f\xb5c\xdbx\xd0\x8e2z\x00\x84\x98\x1d\xbc\x98\x02\xe5i\x13\xa1h\x85F\x05j',
        'SKeyStatus': 0
    },
    'BasebandSerialNumber': b"'C\xde\x01",
    'BasebandVersion': '5.30.01',
    'BoardId': 6,
    'BuildVersion': '17C54', 
    'CPUArchitecture': 'arm64', 
    'ChipID': 32789,
    'DeviceClass': 'iPhone',
    'DeviceColor': '1', 
    'DeviceName': "San's iPhone",
    'DieID': 7157468793159726,
    'HardwareModel': 'D22AP', 
    'HasSiDP': True, 
    'PartitionType': 'GUID_partition_scheme',
    'ProductName': 'iPhone OS',
    'ProductType': 'iPhone10,3',
    'ProductVersion': '13.3',
    'ProductionSOC': True,
    'ProtocolVersion': '2',
    'SupportedDeviceFamilies': [1],
    'TelephonyCapability': True,
    'UniqueChipID': 7157468793159726,
    'UniqueDeviceID': '97006ebdc8bc5daed2e354f4addae4fd2a81c52d',
    'WiFiAddress': 'e4:9a:dc:b4:ba:94'
}
"""