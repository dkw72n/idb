
import plistlib
from ctypes import *

from bpylist import archiver, bplist
from libimobiledevice import (EVP_aes_256_cbc, EVP_CIPHER_CTX_free,
                              EVP_CIPHER_CTX_new, EVP_CIPHER_CTX_reset,
                              EVP_DecryptFinal_ex, EVP_DecryptInit_ex,
                              EVP_DecryptUpdate, EVP_EncryptFinal_ex,
                              EVP_EncryptInit_ex, EVP_EncryptUpdate,
                              plist_free, plist_from_memory, plist_new_data,
                              plist_to_bin, plist_to_bin_free, plist_to_xml,
                              plist_to_xml_free)


def read_buffer_from_pointer(pointer, length):
    return bytes(cast(pointer, POINTER(c_char))[:length])

def parse_plist_to_xml(bin_data:bytes):
    plist = c_void_p()
    plist_from_memory(bin_data, len(bin_data), pointer(plist))
    plist_xml_p = c_void_p()
    length = c_int()
    plist_to_xml(plist, pointer(plist_xml_p), pointer(length))
    xml = read_buffer_from_pointer(plist_xml_p, length.value)
    plist_to_xml_free(plist_xml_p)
    plist_free(plist)
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

def aes_256_cbc_encrypt(buf, key, iv=None):
    out_bytes = c_int()
    out = create_string_buffer(8192)
    ret = b''
    ctx = EVP_CIPHER_CTX_new()
    EVP_CIPHER_CTX_reset(ctx)
    if iv is None: iv = b'\x00' * 16
    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), None, key, iv)
    cur = 0
    try:
        while cur < len(buf):
            step = min(len(buf) - cur, 4096)
            if not EVP_EncryptUpdate(ctx, out, pointer(out_bytes), buf[cur:cur + step], step):
                return None
            ret += out[:out_bytes.value]
            cur += step
        if not EVP_EncryptFinal_ex(ctx, out, pointer(out_bytes)):
            return None
        ret += out[:out_bytes.value]
    finally:
        EVP_CIPHER_CTX_reset(ctx)
        EVP_CIPHER_CTX_free(ctx)
    return ret

def aes_256_cbc_decrypt(buf, key, iv=None):
    out_bytes = c_int()
    out = create_string_buffer(8192)
    ret = b''
    ctx = EVP_CIPHER_CTX_new()
    EVP_CIPHER_CTX_reset(ctx)
    if iv is None: iv = b'\x00' * 16
    EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), None, key, iv)
    try:
        cur = 0
        while cur < len(buf):
            step = min(len(buf) - cur, 4096)
            if not EVP_DecryptUpdate(ctx, out, pointer(out_bytes), buf[cur:cur + step], step):
                return None
            ret += out[:out_bytes.value]
            cur += step
        if not EVP_DecryptFinal_ex(ctx, out, pointer(out_bytes)):
            return None
        ret += out[:out_bytes.value]
    finally:
        EVP_CIPHER_CTX_reset(ctx)
        EVP_CIPHER_CTX_free(ctx)
    return ret
