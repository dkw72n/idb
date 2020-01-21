from ctypes import *
from bpylist import archiver, bplist
import os
import struct
import traceback
from pprint import pprint
import string
from enum import Enum, IntEnum, IntFlag

# md = cdll.LoadLibrary( "libimobiledevice.dll")
# md = CDLL(os.path.join(os.path.dirname(__file__), "libimobiledevice.dll"))

libplist = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libplist.dll"))
libplist_plus = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libplist++.dll"))
libcrypto = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libcrypto-1_1-x64"))
libssl = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libssl-1_1-x64.dll"))
libusbmuxd = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libusbmuxd.dll"))
libimobiledevice = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libimobiledevice.dll"))


class IDeviceInfo(Structure):
    """
    struct idevice_info {
        char *udid;
        enum idevice_connection_type conn_type;
        void* conn_data;
    };
    """
    _fields_ = [
        ('udid', c_char_p),
        ('conn_type', c_int),
        ('conn_data', c_char_p)
    ]


class IDeviceEventType(Enum):
    IDEVICE_DEVICE_ADD = 1
    IDEVICE_DEVICE_REMOVE = 2
    IDEVICE_DEVICE_PAIRED = 3


class IDeviceConnectionType(IntEnum):
    CONNECTION_USBMUXD = 1
    CONNECTION_NETWORK = 2


class IDeviceOptions(IntFlag):
    IDEVICE_LOOKUP_USBMUX = 1 << 1  # include USBMUX devices during lookup
    IDEVICE_LOOKUP_NETWORK = 1 << 2,  # include network devices during lookup
    IDEVICE_LOOKUP_PREFER_NETWORK = 1 << 3  # prefer network connection if device is available via USBMUX *and* network


class IDeviceError(IntEnum):
    IDEVICE_E_SUCCESS = 0
    IDEVICE_E_INVALID_ARG = -1
    IDEVICE_E_UNKNOWN_ERROR = -2
    IDEVICE_E_NO_DEVICE = -3
    IDEVICE_E_NOT_ENOUGH_DATA = -4
    IDEVICE_E_SSL_ERROR = -6
    IDEVICE_E_TIMEOUT = -7


class IDeviceEvent(Structure):
    """
    typedef struct {
        enum idevice_event_type event; /**< The event type. */
        const char *udid; /**< The device unique id. */
        enum idevice_connection_type conn_type; /**< The connection type. */
    } idevice_event_t
    """
    _fields_ = [
        ('event', c_int),
        ('udid', c_char_p),
        ('conn_type', c_int)
    ]


IDeviceEventCb = CFUNCTYPE(None, POINTER(IDeviceEvent), c_void_p)

# include\libimobiledevice\libimobiledevice.h
idevice_get_device_list = libimobiledevice.idevice_get_device_list
idevice_get_device_list.argtypes = [POINTER(POINTER(c_char_p)), POINTER(c_int)]
idevice_get_device_list.restype = c_int

idevice_get_device_list_extended = libimobiledevice.idevice_get_device_list_extended
idevice_get_device_list_extended.argtypes = [POINTER(POINTER(POINTER(IDeviceInfo))), POINTER(c_int)]
idevice_get_device_list_extended.restype = c_int

idevice_device_list_extended_free = libimobiledevice.idevice_device_list_extended_free
idevice_device_list_extended_free.argtypes = [POINTER(POINTER(IDeviceInfo))]
idevice_device_list_extended_free.restype = c_int

idevice_event_subscribe = libimobiledevice.idevice_event_subscribe
idevice_event_subscribe.argtypes = [IDeviceEventCb, c_void_p]
idevice_event_subscribe.restype = c_int

idevice_event_unsubscribe = libimobiledevice.idevice_event_unsubscribe
idevice_event_unsubscribe.argtypes = []
idevice_event_unsubscribe.restype = c_int

idevice_new_with_options = libimobiledevice.idevice_new_with_options
idevice_new_with_options.argtypes = [POINTER(c_void_p), c_char_p, c_int]
idevice_new_with_options.restype = c_int

idevice_free = libimobiledevice.idevice_free
idevice_free.argtypes = [c_void_p]
idevice_free.restype = c_int


# LOCKDOWN


class LockdowndError(IntEnum):
    # /* custom */
    LOCKDOWN_E_SUCCESS = 0,
    LOCKDOWN_E_INVALID_ARG = -1,
    LOCKDOWN_E_INVALID_CONF = -2,
    LOCKDOWN_E_PLIST_ERROR = -3,
    LOCKDOWN_E_PAIRING_FAILED = -4,
    LOCKDOWN_E_SSL_ERROR = -5,
    LOCKDOWN_E_DICT_ERROR = -6,
    LOCKDOWN_E_RECEIVE_TIMEOUT = -7,
    LOCKDOWN_E_MUX_ERROR = -8,
    LOCKDOWN_E_NO_RUNNING_SESSION = -9,
    # /* native */
    LOCKDOWN_E_INVALID_RESPONSE = -10,
    LOCKDOWN_E_MISSING_KEY = -11,
    LOCKDOWN_E_MISSING_VALUE = -12,
    LOCKDOWN_E_GET_PROHIBITED = -13,
    LOCKDOWN_E_SET_PROHIBITED = -14,
    LOCKDOWN_E_REMOVE_PROHIBITED = -15,
    LOCKDOWN_E_IMMUTABLE_VALUE = -16,
    LOCKDOWN_E_PASSWORD_PROTECTED = -17,
    LOCKDOWN_E_USER_DENIED_PAIRING = -18,
    LOCKDOWN_E_PAIRING_DIALOG_RESPONSE_PENDING = -19,
    LOCKDOWN_E_MISSING_HOST_ID = -20,
    LOCKDOWN_E_INVALID_HOST_ID = -21,
    LOCKDOWN_E_SESSION_ACTIVE = -22,
    LOCKDOWN_E_SESSION_INACTIVE = -23,
    LOCKDOWN_E_MISSING_SESSION_ID = -24,
    LOCKDOWN_E_INVALID_SESSION_ID = -25,
    LOCKDOWN_E_MISSING_SERVICE = -26,
    LOCKDOWN_E_INVALID_SERVICE = -27,
    LOCKDOWN_E_SERVICE_LIMIT = -28,
    LOCKDOWN_E_MISSING_PAIR_RECORD = -29,
    LOCKDOWN_E_SAVE_PAIR_RECORD_FAILED = -30,
    LOCKDOWN_E_INVALID_PAIR_RECORD = -31,
    LOCKDOWN_E_INVALID_ACTIVATION_RECORD = -32,
    LOCKDOWN_E_MISSING_ACTIVATION_RECORD = -33,
    LOCKDOWN_E_SERVICE_PROHIBITED = -34,
    LOCKDOWN_E_ESCROW_LOCKED = -35,
    LOCKDOWN_E_PAIRING_PROHIBITED_OVER_THIS_CONNECTION = -36,
    LOCKDOWN_E_FMIP_PROTECTED = -37,
    LOCKDOWN_E_MC_PROTECTED = -38,
    LOCKDOWN_E_MC_CHALLENGE_REQUIRED = -39,
    LOCKDOWN_E_UNKNOWN_ERROR = -256


lockdownd_client_new = libimobiledevice.lockdownd_client_new
lockdownd_client_new.argtypes = [c_void_p, c_void_p, c_char_p]
lockdownd_client_new.restype = c_int

lockdownd_client_free = libimobiledevice.lockdownd_client_free
lockdownd_client_free.argtypes = [c_void_p]
lockdownd_client_free.restype = c_int

# lockdownd_error_t lockdownd_get_value(lockdownd_client_t client, const char *domain, const char *key, plist_t *value);
lockdownd_get_value = libimobiledevice.lockdownd_get_value
lockdownd_get_value.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(c_void_p)]
lockdownd_get_value.restype = c_int

# PLIST

# void plist_free(plist_t plist);
plist_free = libplist.plist_free
plist_free.argtypes = [c_void_p]
plist_free.restype = None

# void plist_to_bin(plist_t plist, char **plist_bin, uint32_t * length);
plist_to_bin = libplist.plist_to_bin
plist_to_bin.argtypes = [c_void_p, POINTER(c_void_p), POINTER(c_int)]
plist_to_bin.restype = None

# void plist_to_bin_free(char *plist_bin);
plist_to_bin_free = libplist.plist_to_bin_free
plist_to_bin_free.argtypes = [c_void_p]
plist_to_bin_free.restype = None

# void plist_to_xml(plist_t plist, char **plist_xml, uint32_t * length);
plist_to_xml = libplist.plist_to_xml
plist_to_xml.argtypes = [c_void_p, POINTER(c_char_p), POINTER(c_int)]
plist_to_xml.restype = None

# void plist_to_bin_free(char *plist_bin);
plist_to_xml_free = libplist.plist_to_xml_free
plist_to_xml_free.argtypes = [c_char_p]
plist_to_xml_free.restype = None


# Mobile Image Mounter

class MobileImageMounterError(IntEnum):
    MOBILE_IMAGE_MOUNTER_E_SUCCESS = 0,
    MOBILE_IMAGE_MOUNTER_E_INVALID_ARG = -1,
    MOBILE_IMAGE_MOUNTER_E_PLIST_ERROR = -2,
    MOBILE_IMAGE_MOUNTER_E_CONN_FAILED = -3,
    MOBILE_IMAGE_MOUNTER_E_COMMAND_FAILED = -4,
    MOBILE_IMAGE_MOUNTER_E_DEVICE_LOCKED = -5,
    MOBILE_IMAGE_MOUNTER_E_UNKNOWN_ERROR = -256

MobileImageMounterUploadCb = CFUNCTYPE(c_ssize_t, c_void_p, c_size_t, c_void_p)

class LockdowndServiceDescriptor(Structure):
    """
    struct lockdownd_service_descriptor {
        uint16_t port;
        uint8_t ssl_enabled;
    };
    """
    _fields_ = [
        ('port', c_int16),
        ('ssl_enabled', c_int8),
    ]

# mobile_image_mounter_error_t mobile_image_mounter_new(idevice_t device, lockdownd_service_descriptor_t service, mobile_image_mounter_client_t *client);
mobile_image_mounter_new = libimobiledevice.mobile_image_mounter_new
mobile_image_mounter_new.argtypes = [c_void_p, POINTER(LockdowndServiceDescriptor), POINTER(c_void_p)]
mobile_image_mounter_new.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_start_service(idevice_t device, mobile_image_mounter_client_t* client, const char* label);
mobile_image_mounter_start_service = libimobiledevice.mobile_image_mounter_start_service
mobile_image_mounter_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
mobile_image_mounter_new.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_free(mobile_image_mounter_client_t client);
mobile_image_mounter_free = libimobiledevice.mobile_image_mounter_free
mobile_image_mounter_free.argtypes = [c_void_p]
mobile_image_mounter_free.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_lookup_image(mobile_image_mounter_client_t client, const char *image_type, plist_t *result);
mobile_image_mounter_lookup_image = libimobiledevice.mobile_image_mounter_lookup_image
mobile_image_mounter_lookup_image.argtypes = [c_void_p, c_char_p, c_void_p]
mobile_image_mounter_lookup_image.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_upload_image(mobile_image_mounter_client_t client, const char *image_type, size_t image_size, const char *signature, uint16_t signature_size, mobile_image_mounter_upload_cb_t upload_cb, void* userdata);
mobile_image_mounter_upload_image = libimobiledevice.mobile_image_mounter_upload_image
mobile_image_mounter_upload_image.argtypes = [c_void_p, c_char_p, c_size_t, c_char_p, c_uint16, MobileImageMounterUploadCb, c_void_p]
mobile_image_mounter_upload_image.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_mount_image(mobile_image_mounter_client_t client, const char *image_path, const char *signature, uint16_t signature_size, const char *image_type, plist_t *result);
mobile_image_mounter_mount_image = libimobiledevice.mobile_image_mounter_mount_image
mobile_image_mounter_mount_image.argtypes = [c_void_p, c_char_p, c_char_p, c_uint16, c_char_p, c_void_p]
mobile_image_mounter_mount_image.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_hangup(mobile_image_mounter_client_t client);
mobile_image_mounter_hangup = libimobiledevice.mobile_image_mounter_hangup
mobile_image_mounter_hangup.argtypes = [c_void_p]
mobile_image_mounter_hangup.restype = c_int
