
from libimobiledevice import plist_to_xml, plist_to_bin, plist_free, plist_to_xml_free, plist_to_bin_free, plist_new_data
from bpylist import archiver, bplist
import plistlib
from ctypes import *


def read_buffer_from_pointer(pointer, length):
    return bytes(cast(pointer, POINTER(c_char))[:length])

def parse_plist_to_xml(bin_data:bytes):
    plist_p = plist_new_data(bin_data, len(bin_data))
    plist_xml_p = c_void_p()
    length = c_int()
    plist_to_xml(plist_p, pointer(plist_xml_p), pointer(length))
    xml = plist_xml_p.content
    plist_to_xml_free(plist_xml_p)
    plist_free(plist_p)
    return xml


def read_data_from_plist_ptr(plist_p):
    result = None

    plist_bin_p = c_void_p()
    length = c_int()
    plist_to_bin(plist_p, pointer(plist_bin_p), pointer(length))
    # print("length", length.value)

    buffer = read_buffer_from_pointer(plist_bin_p, length.value)
    # print("buffer.length", len(buffer))
    if buffer and len(buffer) > 0:
        #result = bplist.parse(buffer)
        result = plistlib.loads(buffer)
    plist_to_bin_free(plist_bin_p)
    #plist_free(plist_p)
    return result


def compare_version(v0:str, v1:str):
    tmp0 = v0.split(".")
    tmp1 = v1.split(".")
    length0 = len(tmp0)
    length1 = len(tmp1)
    i = 0
    while i < length0 and i < length1 and tmp0[i] == tmp1[i]:
        i += 1
    if i < length0 and i < length1:
        return int(tmp0[i]) - int(tmp1[i])
    else:
        return length0 - length1






