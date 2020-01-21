import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
# device
from libimobiledevice import IDeviceInfo, IDeviceEventCb, IDeviceOptions, IDeviceError
from libimobiledevice import idevice_get_device_list_extended, idevice_device_list_extended_free
from libimobiledevice import idevice_event_subscribe, idevice_event_unsubscribe
from libimobiledevice import idevice_new_with_options, idevice_free

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


def read_buffer_from_pointer(pointer, length):
    return bytes(cast(pointer, POINTER(c_byte))[:length])


class DeviceService(Service):
    """
    设备管理服务, 负责获取设备相关信息
    """

    def __init__(self):
        self._callback = None
        self._device_changed_listeners = []
        self._subscribed = False

    def get_device_list(self):
        """
        获取设备列表
        :return: 设备列表，没有设备时返回空集合
        """
        result = []
        device_list_p = POINTER(POINTER(IDeviceInfo))()
        device_count = c_int()
        idevice_get_device_list_extended(pointer(device_list_p), pointer(device_count))
        for i in range(device_count.value):
            device = device_list_p[i].contents
            result.append({
                "udid": device.udid.decode("UTF-8"),
                "conn_type": device.conn_type,
                "conn_data": device.conn_data,
            })
        idevice_device_list_extended_free(device_list_p)
        return result

    def new_device(self, udid):
        """
        通过udid创建新的device对象，用于调用其他接口
        :param udid:
        :return: device对象，注意该对象为C对象，请在使用完后务必调用free_device方法来回收内存
        """
        device = c_void_p()
        options = int(IDeviceOptions.IDEVICE_LOOKUP_USBMUX | IDeviceOptions.IDEVICE_LOOKUP_NETWORK)
        ret = idevice_new_with_options(pointer(device), udid.encode("utf-8"), options)
        if ret != IDeviceError.IDEVICE_E_SUCCESS:
            return None
        return device # free_device(device)

    def free_device(self, device):
        """
        释放device对象
        :param device: new_device的返回值，C对象
        :return: 是否成功
        """
        ret = idevice_free(device)
        return ret == IDeviceError.IDEVICE_E_SUCCESS

    def subscribe(self, listener):
        """
        订阅设备变化事件，在设备连接或移除时会将事件回调给监听器
        :param listener: 事件回调监听器
        :return: void
        """
        self._device_changed_listeners.append(listener)
        if not self._subscribed:
            def callback(event, user_data):
                event_obj = event.contents
                for listener in self._device_changed_listeners:
                    listener({
                        "udid": event_obj.udid,
                        "event": event_obj.event,
                        "conn_type": event_obj.conn_type,
                    })
            user_data = c_void_p()
            self._callback = IDeviceEventCb(callback)
            logging.info("idevice_event_subscribe")
            idevice_event_subscribe(self._callback, user_data)
            self._subscribed = True

    def unsubscribe(self, listener):
        """
        取消订阅设备变化事件
        :param listener: 事件回调监听器
        :return: void
        """
        self._device_changed_listeners.remove(listener)
        if len(self._device_changed_listeners) == 0 and self._subscribed:
            logging.info("idevice_event_unsubscribe")
            idevice_event_unsubscribe()
            self._subscribed = False



