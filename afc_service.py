import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
from libimobiledevice import AfcError, AfcFileMode, AfcLinkType
from libimobiledevice import afc_client_start_service, afc_client_free, afc_get_device_info, afc_get_file_info, afc_read_directory, afc_dictionary_free
from libimobiledevice import afc_file_open, afc_file_close, afc_file_read, afc_file_write
from libimobiledevice import afc_make_directory, afc_remove_path
from libimobiledevice import plist_free
from utils import read_data_from_plist_ptr, compare_version, read_buffer_from_pointer

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class AfcFile(object):

    def __init__(self, afc_client, handler):
        self._afc_client = afc_client
        self._handler = handler

    def __del__(self):
        if self._handler:
            self.close()

    def write(self, data:bytes):
        bytes_written = c_uint32()
        ret = afc_file_write(self._afc_client, self._handler, data, len(data), pointer(bytes_written))
        if ret == AfcError.AFC_E_SUCCESS:
            return bytes_written.value
        else:
            raise IOError("Can not write file, error code:%d" % ret)

    def read(self, size = -1):
        data_p = create_string_buffer(size)
        length = size
        bytes_read = c_uint32()
        ret = afc_file_read(self._afc_client, self._handler, data_p, length, pointer(bytes_read))
        if ret == AfcError.AFC_E_SUCCESS:
            buffer = read_buffer_from_pointer(data_p, bytes_read.value)
            return buffer
        elif ret == AfcError.AFC_E_END_OF_DATA:
            return None
        else:
            raise IOError("Can not read file, error code:%d" % ret)

    def close(self):
        afc_file_close(self._afc_client, self._handler)
        self._handler = None


class AfcService(Service):
    """
    文件传输服务, 负责文件操作相关
    """

    def new_client(self, device):
        """
        创建 afc client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: afc client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = afc_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        if ret != AfcError.AFC_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放mobile image mounter client
        :param client: mobile image mounter client(C对象）
        :return: bool 是否成功
        """
        ret = afc_client_free(client)
        return ret == AfcError.AFC_E_SUCCESS

    def read_directory(self, client, directory:str):
        result = []

        dir_list_p = POINTER(c_char_p)()
        ret = afc_read_directory(client, directory.encode("utf-8"), pointer(dir_list_p))

        source_dir = directory
        if not source_dir.endswith("/"):
            source_dir += "/"

        if ret == AfcError.AFC_E_SUCCESS:
            i = 0
            item = dir_list_p[i]
            while item:
                filename = item.decode("utf-8")
                if filename != "." and filename != "..":
                    filepath = source_dir + filename
                    fileinfo = self.get_file_info(client, filepath)
                    fileinfo['filename'] = filename
                    fileinfo['filepath'] = filepath
                    result.append(fileinfo)
                i += 1
                item = dir_list_p[i]
        afc_dictionary_free(dir_list_p)
        return result

    def get_file_info(self, client, filename:str):
        fileinfo = {}
        fileinfo_p = POINTER(c_char_p)()
        ret = afc_get_file_info(client, filename.encode("utf-8"), pointer(fileinfo_p))
        if ret == AfcError.AFC_E_SUCCESS:
            i = 0
            item = fileinfo_p[i]
            key = None
            while item:
                if key is None:
                    key = item.decode("utf-8")
                else:
                    fileinfo[key] = item.decode("utf-8")
                    key = None
                i += 1
                item = fileinfo_p[i]
        afc_dictionary_free(fileinfo_p)
        return fileinfo

    def open_file(self, client, filename, mode):
        handle = c_uint64()
        file_mode = AfcFileMode.AFC_FOPEN_RDONLY
        has_plus = "+" in mode
        if "r" in mode:
            if has_plus:
                file_mode |= AfcFileMode.AFC_FOPEN_RW
            else:
                file_mode |= AfcFileMode.AFC_FOPEN_RDONLY
        if "w" in mode:
            if has_plus:
                file_mode |= AfcFileMode.AFC_FOPEN_WR
            else:
                file_mode |= AfcFileMode.AFC_FOPEN_WRONLY
        if "a" in mode:
            if has_plus:
                file_mode |= AfcFileMode.AFC_FOPEN_RDAPPEND
            else:
                file_mode |= AfcFileMode.AFC_FOPEN_APPEND

        ret = afc_file_open(client, filename.encode("utf-8"), file_mode, pointer(handle))
        if ret == AfcError.AFC_E_SUCCESS:
            return AfcFile(client, handle.value)
        elif ret == AfcError.AFC_E_OBJECT_NOT_FOUND:
            raise IOError("File not found")
        else:
            raise IOError("IOError: %d" % ret)

    def make_directory(self, client, dirname):
        ret = afc_make_directory(client, dirname.encode("utf-8"))
        return ret == AfcError.AFC_E_SUCCESS

    def remove_path(self, client, dirname):
        ret = afc_remove_path(client, dirname.encode("utf-8"))
        if ret == AfcError.AFC_E_SUCCESS:
            return True
        elif ret == AfcError.AFC_E_DIR_NOT_EMPTY:
            raise IOError("Directory not empty")
        elif ret == AfcError.AFC_E_OBJECT_NOT_FOUND:
            raise IOError("File not found")
        else:
            raise IOError("IOError: %d" % ret)

