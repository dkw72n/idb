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


class ImageMounterService(Service):
    """
    镜像加载管理服务, 负责镜像加载相关事宜
    """

    def __init__(self):
        pass

    def lookup_image(self, image):
        pass # TODO

    def upload_image(self, image):
        pass # TODO

    def mount_image(self, image):
        pass # TODO

    def hangup(self, image):
        pass # TODO



