import os
import struct
import logging

from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at

from service import Service
from libimobiledevice import HouseArrestErrorType,afc_client_new_from_house_arrest_client, house_arrest_client_new, house_arrest_client_free, house_arrest_client_start_service, house_arrest_client_free, house_arrest_send_command, house_arrest_get_result
from libimobiledevice import plist_free
from utils import read_data_from_plist_ptr, compare_version



class House_arrest_proxy_service(Service):

    def new_client(self, device):
        """
        创建house arrest proxy client，用于调用其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: lockdown client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret =house_arrest_client_start_service(device, pointer(client), "ideviceinfo".encode("utf-8"))
        #ret = house_arrest_client_new(device, "ideviceinfo".encode("utf-8"), pointer(client))
        #print("ddd"+str(ret))
        if ret != HouseArrestErrorType.HOUSE_ARREST_E_SUCCESS:
            return None

        return client

    @staticmethod
    def free_client(client):
        """
        House_arrest_proxy_service proxy
        :param client: house arrest client(C对象）
        :return: bool 是否成功
        """
        ret = house_arrest_client_free(client)
        return ret == HouseArrestErrorType.HOUSE_ARREST_E_SUCCESS

    def open_sandbox_with_appid(self, client, docType, appid):

        #"VendContainer" "VendDocuments"
        ret = house_arrest_send_command(client,  ("VendDocuments" if docType == 1 else "VendContainer").encode("utf-8"), appid.encode("utf-8"))
        if ret != HouseArrestErrorType.HOUSE_ARREST_E_SUCCESS:
            print("send command faild "+ appid)
            return None

        plist_p = c_void_p()
        ret = house_arrest_get_result(client, plist_p)
        data = read_data_from_plist_ptr(plist_p)
        if data['Status'] != "Complete":
            print(data)
            return None

        afcClient = c_void_p()
        afc_client_new_from_house_arrest_client(client,pointer(afcClient))
        return afcClient



