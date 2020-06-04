import sys
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
if sys.platform == 'win32':
    libplist_plus = None
    libssl = None
    libplist = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libplist.dll"))
    libimobiledevice = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libimobiledevice.dll"))
    libcrypto = libimobiledevice
    libusbmuxd = libimobiledevice
elif sys.platform.startswith('linux'):
    libplist_plus = None
    libssl = None
    libimobiledevice = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "libimobiledevice.so.6.0.0"))
    libcrypto = libimobiledevice
    libplist = libimobiledevice
    libusbmuxd = libimobiledevice
else : # mac os
    libcrypto = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "macos/libcrypto.dylib"))
    libplist_plus = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "macos/libplist++.dylib"))
    libssl = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "macos/libssl.dylib"))
    libimobiledevice = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "macos/libimobiledevice.dylib"))
    libplist = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "macos/libplist.dylib"))
    libusbmuxd = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "macos/libusbmuxd.dylib"))


# --------------------------------- plist -----------------------------------------


# plist_t plist_new_data(const char *val, uint64_t length);
plist_new_data = libplist.plist_new_data
plist_new_data.argtypes = [c_void_p, c_uint64]
plist_new_data.restype = c_void_p

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
plist_to_xml.argtypes = [c_void_p, POINTER(c_void_p), POINTER(c_int)]
plist_to_xml.restype = None

# void plist_to_bin_free(char *plist_bin);
plist_to_xml_free = libplist.plist_to_xml_free
plist_to_xml_free.argtypes = [c_void_p]
plist_to_xml_free.restype = None

# void plist_from_memory(const char *plist_bin, uint32_t length, plist_t * plist);
plist_from_memory = libplist.plist_from_memory
plist_from_memory.argtypes = [c_void_p, c_uint32, POINTER(c_void_p)]
plist_from_memory.restype = None

#plist_t plist_new_bool(uint8_t value);
plist_new_bool = libplist.plist_new_bool
plist_new_bool.argtypes = [c_uint]
plist_new_bool.restype = c_void_p


#plist_t plist_new_string(const char *val);
plist_new_string = libplist.plist_new_string
plist_new_string.argtypes = [c_char_p]
plist_new_string.restype = c_void_p

#void plist_array_append_item(plist_t node, plist_t item);
plist_array_append_item =libplist.plist_array_append_item
plist_array_append_item.argtypes = [c_void_p,c_void_p]
plist_array_append_item.restype = None

plist_new_array = libplist.plist_new_array
plist_new_array.argtypes = None
plist_new_array.restype = c_void_p

# --------------------------------- Crypto ------------------------------------------


c_ubyte_p = POINTER(c_ubyte)

EVP_CIPHER_CTX_new = libcrypto.EVP_CIPHER_CTX_new
EVP_CIPHER_CTX_new.restype = c_void_p

EVP_CIPHER_CTX_free = libcrypto.EVP_CIPHER_CTX_free
EVP_CIPHER_CTX_free.argtypes = [c_void_p]

EVP_CIPHER_CTX_reset = libcrypto.EVP_CIPHER_CTX_reset
EVP_CIPHER_CTX_reset.argtypes = [c_void_p]

EVP_EncryptInit_ex = libcrypto.EVP_EncryptInit_ex
EVP_EncryptInit_ex.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p]

EVP_EncryptUpdate = libcrypto.EVP_EncryptUpdate
EVP_EncryptUpdate.argtypes = [c_void_p, c_void_p, POINTER(c_int), c_void_p, c_int]

EVP_EncryptFinal_ex = libcrypto.EVP_EncryptFinal_ex
EVP_EncryptFinal_ex.argtypes = [c_void_p, c_void_p, POINTER(c_int)]

EVP_DecryptInit_ex = libcrypto.EVP_DecryptInit_ex
EVP_DecryptInit_ex.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p]

EVP_DecryptUpdate = libcrypto.EVP_DecryptUpdate
EVP_DecryptUpdate.argtypes = [c_void_p, c_void_p, POINTER(c_int), c_void_p, c_int]

EVP_DecryptFinal_ex = libcrypto.EVP_DecryptFinal_ex
EVP_DecryptFinal_ex.argtypes = [c_void_p, c_void_p, POINTER(c_int)]

EVP_aes_256_cbc = libcrypto.EVP_aes_256_cbc
EVP_aes_256_cbc.restype = c_void_p
# --------------------------------- IDevice -----------------------------------------


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


class IDeviceEventType(IntEnum):
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

# idevice_error_t idevice_get_device_list(char ***devices, int *count);
idevice_get_device_list = libimobiledevice.idevice_get_device_list
idevice_get_device_list.argtypes = [POINTER(POINTER(c_char_p)), POINTER(c_int)]
idevice_get_device_list.restype = c_int

# idevice_error_t idevice_get_device_list_extended(idevice_info_t **devices, int *count);
idevice_get_device_list_extended = libimobiledevice.idevice_get_device_list_extended
idevice_get_device_list_extended.argtypes = [POINTER(POINTER(POINTER(IDeviceInfo))), POINTER(c_int)]
idevice_get_device_list_extended.restype = c_int

# idevice_error_t idevice_device_list_extended_free(idevice_info_t *devices);
idevice_device_list_extended_free = libimobiledevice.idevice_device_list_extended_free
idevice_device_list_extended_free.argtypes = [POINTER(POINTER(IDeviceInfo))]
idevice_device_list_extended_free.restype = c_int

# idevice_error_t idevice_event_subscribe(idevice_event_cb_t callback, void *user_data);
idevice_event_subscribe = libimobiledevice.idevice_event_subscribe
idevice_event_subscribe.argtypes = [IDeviceEventCb, c_void_p]
idevice_event_subscribe.restype = c_int

# idevice_error_t idevice_event_unsubscribe(void);
idevice_event_unsubscribe = libimobiledevice.idevice_event_unsubscribe
idevice_event_unsubscribe.argtypes = []
idevice_event_unsubscribe.restype = c_int

# idevice_error_t idevice_new(idevice_t *device, const char *udid);
idevice_new = libimobiledevice.idevice_new
idevice_new.argtypes = [POINTER(c_void_p), c_char_p]
idevice_new.restype = c_int

# idevice_error_t idevice_get_device_list_extended(idevice_info_t **devices, int *count);
idevice_new_with_options = libimobiledevice.idevice_new_with_options
idevice_new_with_options.argtypes = [POINTER(c_void_p), c_char_p, c_int]
idevice_new_with_options.restype = c_int

# idevice_error_t idevice_free(idevice_t device);
idevice_free = libimobiledevice.idevice_free
idevice_free.argtypes = [c_void_p]
idevice_free.restype = c_int


# --------------------------------- Lockdownd -----------------------------------------


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

lockdownd_client_new_with_handshake = libimobiledevice.lockdownd_client_new_with_handshake
lockdownd_client_new_with_handshake.argtypes = [c_void_p, c_void_p, c_char_p]
lockdownd_client_new_with_handshake.restype = c_int

lockdownd_client_free = libimobiledevice.lockdownd_client_free
lockdownd_client_free.argtypes = [c_void_p]
lockdownd_client_free.restype = c_int

# lockdownd_error_t lockdownd_get_value(lockdownd_client_t client, const char *domain, const char *key, plist_t *value);
lockdownd_get_value = libimobiledevice.lockdownd_get_value
lockdownd_get_value.argtypes = [c_void_p, c_char_p, c_char_p, POINTER(c_void_p)]
lockdownd_get_value.restype = c_int

# lockdownd_error_t lockdownd_set_value(lockdownd_client_t client, const char *domain, const char *key, plist_t value);
lockdownd_set_value = libimobiledevice.lockdownd_set_value
lockdownd_set_value.argtypes = [c_void_p, c_char_p, c_char_p, c_void_p]
lockdownd_set_value.restype = c_int

lockdownd_remove_value = libimobiledevice.lockdownd_remove_value
lockdownd_remove_value.argtypes = [c_void_p, c_char_p, c_char_p]
lockdownd_remove_value.restype = c_int

# --------------------------------- Mobile Image Mounter -----------------------------------------


class MobileImageMounterError(IntEnum):
    MOBILE_IMAGE_MOUNTER_E_SUCCESS = 0
    MOBILE_IMAGE_MOUNTER_E_INVALID_ARG = -1
    MOBILE_IMAGE_MOUNTER_E_PLIST_ERROR = -2
    MOBILE_IMAGE_MOUNTER_E_CONN_FAILED = -3
    MOBILE_IMAGE_MOUNTER_E_COMMAND_FAILED = -4
    MOBILE_IMAGE_MOUNTER_E_DEVICE_LOCKED = -5
    MOBILE_IMAGE_MOUNTER_E_UNKNOWN_ERROR = -256

# typedef ssize_t (*mobile_image_mounter_upload_cb_t) (void* buffer, size_t length, void *user_data);
MobileImageMounterUploadCb = CFUNCTYPE(c_ssize_t, c_void_p, c_size_t, c_void_p)

# mobile_image_mounter_error_t mobile_image_mounter_start_service(idevice_t device, mobile_image_mounter_client_t* client, const char* label);
mobile_image_mounter_start_service = libimobiledevice.mobile_image_mounter_start_service
mobile_image_mounter_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
mobile_image_mounter_start_service.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_free(mobile_image_mounter_client_t client);
mobile_image_mounter_free = libimobiledevice.mobile_image_mounter_free
mobile_image_mounter_free.argtypes = [c_void_p]
mobile_image_mounter_free.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_lookup_image(mobile_image_mounter_client_t client, const char *image_type, plist_t *result);
mobile_image_mounter_lookup_image = libimobiledevice.mobile_image_mounter_lookup_image
mobile_image_mounter_lookup_image.argtypes = [c_void_p, c_char_p, POINTER(c_void_p)]
mobile_image_mounter_lookup_image.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_upload_image(mobile_image_mounter_client_t client, const char *image_type, size_t image_size, const char *signature, uint16_t signature_size, mobile_image_mounter_upload_cb_t upload_cb, void* userdata);
mobile_image_mounter_upload_image = libimobiledevice.mobile_image_mounter_upload_image
mobile_image_mounter_upload_image.argtypes = [c_void_p, c_char_p, c_size_t, c_char_p, c_uint16, MobileImageMounterUploadCb, c_void_p]
mobile_image_mounter_upload_image.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_upload_image_file(mobile_image_mounter_client_t client, const char *image_type, const char* image_file_path, const char *signature_file_path);
mobile_image_mounter_upload_image_file = libimobiledevice.mobile_image_mounter_upload_image_file
mobile_image_mounter_upload_image_file.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
mobile_image_mounter_upload_image_file.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_mount_image(mobile_image_mounter_client_t client, const char *image_path, const char *signature, uint16_t signature_size, const char *image_type, plist_t *result);
mobile_image_mounter_mount_image = libimobiledevice.mobile_image_mounter_mount_image
mobile_image_mounter_mount_image.argtypes = [c_void_p, c_char_p, c_char_p, c_uint16, c_char, POINTER(c_void_p)]
mobile_image_mounter_mount_image.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_mount_image_file(mobile_image_mounter_client_t client, const char *image_path, const char *signature_file, const char *image_type, plist_t *result);
mobile_image_mounter_mount_image_file = libimobiledevice.mobile_image_mounter_mount_image_file
mobile_image_mounter_mount_image_file.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, POINTER(c_void_p)]
mobile_image_mounter_mount_image_file.restype = c_int

# mobile_image_mounter_error_t mobile_image_mounter_hangup(mobile_image_mounter_client_t client);
mobile_image_mounter_hangup = libimobiledevice.mobile_image_mounter_hangup
mobile_image_mounter_hangup.argtypes = [c_void_p]
mobile_image_mounter_hangup.restype = c_int


# --------------------------------- Screenshotr -----------------------------------------


class ScreenshotrError(IntEnum):
    SCREENSHOTR_E_SUCCESS = 0,
    SCREENSHOTR_E_INVALID_ARG = -1
    SCREENSHOTR_E_PLIST_ERROR = -2
    SCREENSHOTR_E_MUX_ERROR = -3
    SCREENSHOTR_E_SSL_ERROR = -4
    SCREENSHOTR_E_RECEIVE_TIMEOUT = -5
    SCREENSHOTR_E_BAD_VERSION = -6
    SCREENSHOTR_E_UNKNOWN_ERROR = -256

# screenshotr_error_t screenshotr_client_start_service(idevice_t device, screenshotr_client_t* client, const char* label);
screenshotr_client_start_service = libimobiledevice.screenshotr_client_start_service
screenshotr_client_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
screenshotr_client_start_service.restype = c_int

# screenshotr_error_t screenshotr_client_free(screenshotr_client_t client);
screenshotr_client_free = libimobiledevice.screenshotr_client_free
screenshotr_client_free.argtypes = [c_void_p]
screenshotr_client_free.restype = c_int

# screenshotr_error_t screenshotr_take_screenshot(screenshotr_client_t client, char **imgdata, uint64_t *imgsize);
screenshotr_take_screenshot = libimobiledevice.screenshotr_take_screenshot
screenshotr_take_screenshot.argtypes = [c_void_p, POINTER(c_void_p), POINTER(c_uint64)]
screenshotr_take_screenshot.restype = c_int


# --------------------------------- Syslog Relay -----------------------------------------


class SyslogRelayError(IntEnum):
    SYSLOG_RELAY_E_SUCCESS = 0
    SYSLOG_RELAY_E_INVALID_ARG = -1
    SYSLOG_RELAY_E_MUX_ERROR = -2
    SYSLOG_RELAY_E_SSL_ERROR = -3
    SYSLOG_RELAY_E_NOT_ENOUGH_DATA = -4
    SYSLOG_RELAY_E_TIMEOUT = -5
    SYSLOG_RELAY_E_UNKNOWN_ERROR = -256

# typedef void (*syslog_relay_receive_cb_t)(char c, void *user_data);
SyslogRelayReceiveCb = CFUNCTYPE(None, c_char, c_void_p)

# syslog_relay_error_t syslog_relay_client_start_service(idevice_t device, syslog_relay_client_t * client, const char* label);
syslog_relay_client_start_service = libimobiledevice.syslog_relay_client_start_service
syslog_relay_client_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
syslog_relay_client_start_service.restype = c_int

# syslog_relay_error_t syslog_relay_client_free(syslog_relay_client_t client);
syslog_relay_client_free = libimobiledevice.syslog_relay_client_free
syslog_relay_client_free.argtypes = [c_void_p]
syslog_relay_client_free.restype = c_int

# syslog_relay_error_t syslog_relay_start_capture(syslog_relay_client_t client, syslog_relay_receive_cb_t callback, void* user_data);
syslog_relay_start_capture = libimobiledevice.syslog_relay_start_capture
syslog_relay_start_capture.argtypes = [c_void_p, SyslogRelayReceiveCb, c_void_p]
syslog_relay_start_capture.restype = c_int

# syslog_relay_error_t syslog_relay_stop_capture(syslog_relay_client_t client);
syslog_relay_stop_capture = libimobiledevice.syslog_relay_stop_capture
syslog_relay_stop_capture.argtypes = [c_void_p]
syslog_relay_stop_capture.restype = c_int


# --------------------------------- Installation Proxy -----------------------------------------


class InstProxyError(IntEnum):
    # /* custom */
    INSTPROXY_E_SUCCESS = 0,
    INSTPROXY_E_INVALID_ARG = -1,
    INSTPROXY_E_PLIST_ERROR = -2,
    INSTPROXY_E_CONN_FAILED = -3,
    INSTPROXY_E_OP_IN_PROGRESS = -4,
    INSTPROXY_E_OP_FAILED = -5,
    INSTPROXY_E_RECEIVE_TIMEOUT = -6,
    # /* native */
    INSTPROXY_E_ALREADY_ARCHIVED = -7,
    INSTPROXY_E_API_INTERNAL_ERROR = -8,
    INSTPROXY_E_APPLICATION_ALREADY_INSTALLED = -9,
    INSTPROXY_E_APPLICATION_MOVE_FAILED = -10,
    INSTPROXY_E_APPLICATION_SINF_CAPTURE_FAILED = -11,
    INSTPROXY_E_APPLICATION_SANDBOX_FAILED = -12,
    INSTPROXY_E_APPLICATION_VERIFICATION_FAILED = -13,
    INSTPROXY_E_ARCHIVE_DESTRUCTION_FAILED = -14,
    INSTPROXY_E_BUNDLE_VERIFICATION_FAILED = -15,
    INSTPROXY_E_CARRIER_BUNDLE_COPY_FAILED = -16,
    INSTPROXY_E_CARRIER_BUNDLE_DIRECTORY_CREATION_FAILED = -17,
    INSTPROXY_E_CARRIER_BUNDLE_MISSING_SUPPORTED_SIMS = -18,
    INSTPROXY_E_COMM_CENTER_NOTIFICATION_FAILED = -19,
    INSTPROXY_E_CONTAINER_CREATION_FAILED = -20,
    INSTPROXY_E_CONTAINER_P0WN_FAILED = -21,
    INSTPROXY_E_CONTAINER_REMOVAL_FAILED = -22,
    INSTPROXY_E_EMBEDDED_PROFILE_INSTALL_FAILED = -23,
    INSTPROXY_E_EXECUTABLE_TWIDDLE_FAILED = -24,
    INSTPROXY_E_EXISTENCE_CHECK_FAILED = -25,
    INSTPROXY_E_INSTALL_MAP_UPDATE_FAILED = -26,
    INSTPROXY_E_MANIFEST_CAPTURE_FAILED = -27,
    INSTPROXY_E_MAP_GENERATION_FAILED = -28,
    INSTPROXY_E_MISSING_BUNDLE_EXECUTABLE = -29,
    INSTPROXY_E_MISSING_BUNDLE_IDENTIFIER = -30,
    INSTPROXY_E_MISSING_BUNDLE_PATH = -31,
    INSTPROXY_E_MISSING_CONTAINER = -32,
    INSTPROXY_E_NOTIFICATION_FAILED = -33,
    INSTPROXY_E_PACKAGE_EXTRACTION_FAILED = -34,
    INSTPROXY_E_PACKAGE_INSPECTION_FAILED = -35,
    INSTPROXY_E_PACKAGE_MOVE_FAILED = -36,
    INSTPROXY_E_PATH_CONVERSION_FAILED = -37,
    INSTPROXY_E_RESTORE_CONTAINER_FAILED = -38,
    INSTPROXY_E_SEATBELT_PROFILE_REMOVAL_FAILED = -39,
    INSTPROXY_E_STAGE_CREATION_FAILED = -40,
    INSTPROXY_E_SYMLINK_FAILED = -41,
    INSTPROXY_E_UNKNOWN_COMMAND = -42,
    INSTPROXY_E_ITUNES_ARTWORK_CAPTURE_FAILED = -43,
    INSTPROXY_E_ITUNES_METADATA_CAPTURE_FAILED = -44,
    INSTPROXY_E_DEVICE_OS_VERSION_TOO_LOW = -45,
    INSTPROXY_E_DEVICE_FAMILY_NOT_SUPPORTED = -46,
    INSTPROXY_E_PACKAGE_PATCH_FAILED = -47,
    INSTPROXY_E_INCORRECT_ARCHITECTURE = -48,
    INSTPROXY_E_PLUGIN_COPY_FAILED = -49,
    INSTPROXY_E_BREADCRUMB_FAILED = -50,
    INSTPROXY_E_BREADCRUMB_UNLOCK_FAILED = -51,
    INSTPROXY_E_GEOJSON_CAPTURE_FAILED = -52,
    INSTPROXY_E_NEWSSTAND_ARTWORK_CAPTURE_FAILED = -53,
    INSTPROXY_E_MISSING_COMMAND = -54,
    INSTPROXY_E_NOT_ENTITLED = -55,
    INSTPROXY_E_MISSING_PACKAGE_PATH = -56,
    INSTPROXY_E_MISSING_CONTAINER_PATH = -57,
    INSTPROXY_E_MISSING_APPLICATION_IDENTIFIER = -58,
    INSTPROXY_E_MISSING_ATTRIBUTE_VALUE = -59,
    INSTPROXY_E_LOOKUP_FAILED = -60,
    INSTPROXY_E_DICT_CREATION_FAILED = -61,
    INSTPROXY_E_INSTALL_PROHIBITED = -62,
    INSTPROXY_E_UNINSTALL_PROHIBITED = -63,
    INSTPROXY_E_MISSING_BUNDLE_VERSION = -64,
    INSTPROXY_E_UNKNOWN_ERROR = -256

# instproxy_error_t instproxy_client_start_service(idevice_t device, instproxy_client_t * client, const char* label);
instproxy_client_start_service = libimobiledevice.instproxy_client_start_service
instproxy_client_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
instproxy_client_start_service.restype = c_int

# instproxy_error_t instproxy_client_free(instproxy_client_t client);
instproxy_client_free = libimobiledevice.instproxy_client_free
instproxy_client_free.argtypes = [c_void_p]
instproxy_client_free.restype = c_int

# instproxy_error_t instproxy_browse(instproxy_client_t client, plist_t client_options, plist_t *result);
instproxy_browse = libimobiledevice.instproxy_browse
instproxy_browse.argtypes = [c_void_p, c_void_p, POINTER(c_void_p)]
instproxy_browse.restype = c_int

# LIBIMOBILEDEVICE_API plist_t instproxy_client_options_new(void)
instproxy_client_options_new = libimobiledevice.instproxy_client_options_new
instproxy_client_options_new.argtypes = []
instproxy_client_options_new.restype = c_void_p

# LIBIMOBILEDEVICE_API void instproxy_client_options_free(plist_t client_options)
instproxy_client_options_free = libimobiledevice.instproxy_client_options_free
instproxy_client_options_free.argtypes = [c_void_p]
instproxy_client_options_free.restype = None

# LIBIMOBILEDEVICE_API void instproxy_client_options_add(plist_t client_options, ...)
instproxy_client_options_add = libimobiledevice.instproxy_client_options_add
instproxy_client_options_add.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p]
instproxy_client_options_add.restype = None

# LIBIMOBILEDEVICE_API void instproxy_client_options_set_return_attributes(plist_t client_options, ...)
instproxy_client_options_set_return_attributes = libimobiledevice.instproxy_client_options_set_return_attributes
instproxy_client_options_set_return_attributes.argtypes = [c_void_p, c_char_p, c_char_p, c_char_p, c_char_p]
instproxy_client_options_set_return_attributes.restype = None


# --------------------------------- Spring board -----------------------------------------


class SbservicesError(IntEnum):
    SBSERVICES_E_SUCCESS = 0
    SBSERVICES_E_INVALID_ARG = -1
    SBSERVICES_E_PLIST_ERROR = -2
    SBSERVICES_E_CONN_FAILED = -3
    SBSERVICES_E_UNKNOWN_ERROR = -256

class SbservicesInterfaceOrientation(IntEnum):
    SBSERVICES_INTERFACE_ORIENTATION_UNKNOWN = 0,
    SBSERVICES_INTERFACE_ORIENTATION_PORTRAIT = 1
    SBSERVICES_INTERFACE_ORIENTATION_PORTRAIT_UPSIDE_DOWN = 2
    SBSERVICES_INTERFACE_ORIENTATION_LANDSCAPE_RIGHT = 3
    SBSERVICES_INTERFACE_ORIENTATION_LANDSCAPE_LEFT = 4

# sbservices_error_t sbservices_client_start_service(idevice_t device, sbservices_client_t* client, const char* label);
sbservices_client_start_service = libimobiledevice.sbservices_client_start_service
sbservices_client_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
sbservices_client_start_service.restype = c_int

# sbservices_error_t sbservices_client_free(sbservices_client_t client);
sbservices_client_free = libimobiledevice.sbservices_client_free
sbservices_client_free.argtypes = [c_void_p]
sbservices_client_free.restype = c_int

# sbservices_error_t sbservices_get_icon_pngdata(sbservices_client_t client, const char *bundleId, char **pngdata, uint64_t *pngsize);
sbservices_get_icon_pngdata = libimobiledevice.sbservices_get_icon_pngdata
sbservices_get_icon_pngdata.argtypes = [c_void_p, c_char_p, POINTER(c_void_p), POINTER(c_uint64)]
sbservices_get_icon_pngdata.restype = c_int

# sbservices_error_t sbservices_get_interface_orientation(sbservices_client_t client, sbservices_interface_orientation_t* interface_orientation);
sbservices_get_interface_orientation = libimobiledevice.sbservices_get_interface_orientation
sbservices_get_interface_orientation.argtypes = [c_void_p, POINTER(c_uint)]
sbservices_get_interface_orientation.restype = c_int

# void free(void*)
libimobiledevice_free = libimobiledevice.libimobiledevice_free
libimobiledevice_free.argtypes = [c_void_p]
libimobiledevice_free.restype = None


# --------------------------------- Instrument -----------------------------------------


class InstrumentError(IntEnum):
    INSTRUMENT_E_SUCCESS         =  0,
    INSTRUMENT_E_INVALID_ARG     = -1,
    INSTRUMENT_E_PLIST_ERROR     = -2,
    INSTRUMENT_E_MUX_ERROR       = -3,
    INSTRUMENT_E_SSL_ERROR       = -4,
    INSTRUMENT_E_RECEIVE_TIMEOUT = -5,
    INSTRUMENT_E_BAD_VERSION     = -6,
    INSTRUMENT_E_CONN_FAILED     = -7,
    INSTRUMENT_E_UNKNOWN_ERROR   = -256

# instrument_error_t instrument_client_start_service(idevice_t device, instrument_client_t* client, const char* label);
instrument_client_start_service = libimobiledevice.instrument_client_start_service
instrument_client_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
instrument_client_start_service.restype = c_int

# instrument_error_t instrument_client_free(instrument_client_t client);
instrument_client_free = libimobiledevice.instrument_client_free
instrument_client_free.argtypes = [c_void_p]
instrument_client_free.restype = c_int

# instrument_error_t instrument_send_command(instrument_client_t client, const char *data, uint32_t size, uint32_t *sent);
instrument_send_command = libimobiledevice.instrument_send_command
instrument_send_command.argtypes = [c_void_p, c_void_p, c_uint32, POINTER(c_uint32)]
instrument_send_command.restype = c_int

# instrument_error_t instrument_receive(instrument_client_t client, char *data, uint32_t size, uint32_t *received);
instrument_receive = libimobiledevice.instrument_receive
instrument_receive.argtypes = [c_void_p, c_void_p, c_uint32, POINTER(c_uint32)]
instrument_receive.restype = c_int

# instrument_error_t instrument_receive_with_timeout(instrument_client_t client, char *data, uint32_t size, uint32_t *received, unsigned int timeout);
instrument_receive_with_timeout = libimobiledevice.instrument_receive_with_timeout
instrument_receive_with_timeout.argtypes = [c_void_p, c_void_p, c_uint32, POINTER(c_uint32), c_uint]
instrument_receive_with_timeout.restype = c_int


# --------------------------------- AFC -----------------------------------------


class AfcError(IntEnum):
    AFC_E_SUCCESS = 0
    AFC_E_UNKNOWN_ERROR = 1
    AFC_E_OP_HEADER_INVALID = 2
    AFC_E_NO_RESOURCES = 3
    AFC_E_READ_ERROR = 4
    AFC_E_WRITE_ERROR = 5
    AFC_E_UNKNOWN_PACKET_TYPE = 6
    AFC_E_INVALID_ARG = 7
    AFC_E_OBJECT_NOT_FOUND = 8
    AFC_E_OBJECT_IS_DIR = 9
    AFC_E_PERM_DENIED = 10
    AFC_E_SERVICE_NOT_CONNECTED = 11
    AFC_E_OP_TIMEOUT = 12
    AFC_E_TOO_MUCH_DATA = 13
    AFC_E_END_OF_DATA = 14
    AFC_E_OP_NOT_SUPPORTED = 15
    AFC_E_OBJECT_EXISTS = 16
    AFC_E_OBJECT_BUSY = 17
    AFC_E_NO_SPACE_LEFT = 18
    AFC_E_OP_WOULD_BLOCK = 19
    AFC_E_IO_ERROR = 20
    AFC_E_OP_INTERRUPTED = 21
    AFC_E_OP_IN_PROGRESS = 22
    AFC_E_INTERNAL_ERROR = 23
    AFC_E_MUX_ERROR = 30
    AFC_E_NO_MEM = 31
    AFC_E_NOT_ENOUGH_DATA = 32
    AFC_E_DIR_NOT_EMPTY = 33
    AFC_E_FORCE_SIGNED_TYPE = -1


class AfcFileMode(IntEnum):
    AFC_FOPEN_RDONLY = 0x00000001   # / ** < r O_RDONLY * /
    AFC_FOPEN_RW = 0x00000002       # / ** < r+ O_RDWR | O_CREAT * /
    AFC_FOPEN_WRONLY = 0x00000003   # / ** < w O_WRONLY | O_CREAT | O_TRUNC * /
    AFC_FOPEN_WR = 0x00000004       # / ** < w+ O_RDWR | O_CREAT | O_TRUNC * /
    AFC_FOPEN_APPEND = 0x00000005   # / ** < a O_WRONLY | O_APPEND | O_CREAT * /
    AFC_FOPEN_RDAPPEND = 0x00000006 # / ** < a+ O_RDWR | O_APPEND | O_CREAT * /


class AfcLinkType(IntEnum):
    AFC_HARDLINK = 1,
    AFC_SYMLINK = 2


class AfcLockOp(IntEnum):
    AFC_LOCK_SH = 1 | 4 # / ** < shared lock * /
    AFC_LOCK_EX = 2 | 4 # / ** < exclusive lock * /
    AFC_LOCK_UN = 8 | 4 # / ** < unlock * /

# afc_error_t afc_client_start_service(idevice_t device, afc_client_t* client, const char* label);
afc_client_start_service = libimobiledevice.afc_client_start_service
afc_client_start_service.argtypes = [c_void_p, POINTER(c_void_p), c_char_p]
afc_client_start_service.restype = c_int

# afc_error_t afc_client_free(afc_client_t client);
afc_client_free = libimobiledevice.afc_client_free
afc_client_free.argtypes = [c_void_p]
afc_client_free.restype = c_int

# afc_error_t afc_get_device_info(afc_client_t client, char ***device_information);
afc_get_device_info = libimobiledevice.afc_get_device_info
afc_get_device_info.argtypes = [c_void_p, POINTER(POINTER(c_char_p))]
afc_get_device_info.restype = c_int

# afc_error_t afc_read_directory(afc_client_t client, const char *path, char ***directory_information);
afc_read_directory = libimobiledevice.afc_read_directory
afc_read_directory.argtypes = [c_void_p, c_char_p, POINTER(POINTER(c_char_p))]
afc_read_directory.restype = c_int

# afc_error_t afc_get_file_info(afc_client_t client, const char *filename, char ***file_information);
afc_get_file_info = libimobiledevice.afc_get_file_info
afc_get_file_info.argtypes = [c_void_p, c_char_p, POINTER(POINTER(c_char_p))]
afc_get_file_info.restype = c_int

# afc_error_t afc_file_open(afc_client_t client, const char *filename, afc_file_mode_t file_mode, uint64_t *handle);
afc_file_open = libimobiledevice.afc_file_open
afc_file_open.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_uint64)]
afc_file_open.restype = c_int

# afc_error_t afc_file_close(afc_client_t client, uint64_t handle);
afc_file_close = libimobiledevice.afc_file_close
afc_file_close.argtypes = [c_void_p, c_uint64]
afc_file_close.restype = c_int

# afc_error_t afc_file_lock(afc_client_t client, uint64_t handle, afc_lock_op_t operation);
afc_file_lock = libimobiledevice.afc_file_lock
afc_file_lock.argtypes = [c_void_p, c_uint64, c_int]
afc_file_lock.restype = c_int

# afc_error_t afc_file_read(afc_client_t client, uint64_t handle, char *data, uint32_t length, uint32_t *bytes_read);
afc_file_read = libimobiledevice.afc_file_read
afc_file_read.argtypes = [c_void_p, c_uint64, c_void_p, c_uint32, POINTER(c_uint32)]
afc_file_read.restype = c_int

# afc_error_t afc_file_write(afc_client_t client, uint64_t handle, const char *data, uint32_t length, uint32_t *bytes_written);
afc_file_write = libimobiledevice.afc_file_write
afc_file_write.argtypes = [c_void_p, c_uint64, c_void_p, c_uint32, POINTER(c_uint32)]
afc_file_write.restype = c_int

# afc_error_t afc_file_seek(afc_client_t client, uint64_t handle, int64_t offset, int whence);
afc_file_seek = libimobiledevice.afc_file_seek
afc_file_seek.argtypes = [c_void_p, c_uint64, c_int64, c_int]
afc_file_seek.restype = c_int

# afc_error_t afc_file_tell(afc_client_t client, uint64_t handle, uint64_t *position);
afc_file_tell = libimobiledevice.afc_file_tell
afc_file_tell.argtypes = [c_void_p, c_uint64, POINTER(c_uint64)]
afc_file_tell.restype = c_int

# afc_error_t afc_file_truncate(afc_client_t client, uint64_t handle, uint64_t newsize);
afc_file_truncate = libimobiledevice.afc_file_truncate
afc_file_truncate.argtypes = [c_void_p, c_uint64, c_uint64]
afc_file_truncate.restype = c_int

# afc_error_t afc_remove_path(afc_client_t client, const char *path);
afc_remove_path = libimobiledevice.afc_remove_path
afc_remove_path.argtypes = [c_void_p, c_char_p]
afc_remove_path.restype = c_int

# afc_error_t afc_rename_path(afc_client_t client, const char *from, const char *to);
afc_rename_path = libimobiledevice.afc_rename_path
afc_rename_path.argtypes = [c_void_p, c_char_p, c_char_p]
afc_rename_path.restype = c_int

# afc_error_t afc_make_directory(afc_client_t client, const char *path);
afc_make_directory = libimobiledevice.afc_make_directory
afc_make_directory.argtypes = [c_void_p, c_char_p]
afc_make_directory.restype = c_int

# afc_error_t afc_truncate(afc_client_t client, const char *path, uint64_t newsize);
afc_truncate = libimobiledevice.afc_truncate
afc_truncate.argtypes = [c_void_p, c_char_p, c_uint64]
afc_truncate.restype = c_int

# afc_error_t afc_make_link(afc_client_t client, afc_link_type_t linktype, const char *target, const char *linkname);
afc_make_link = libimobiledevice.afc_make_link
afc_make_link.argtypes = [c_void_p, c_int, c_char_p, c_char_p]
afc_make_link.restype = c_int

# afc_error_t afc_set_file_time(afc_client_t client, const char *path, uint64_t mtime);
afc_set_file_time = libimobiledevice.afc_set_file_time
afc_set_file_time.argtypes = [c_void_p, c_char_p, c_uint64]
afc_set_file_time.restype = c_int

# afc_error_t afc_remove_path_and_contents(afc_client_t client, const char *path);
afc_remove_path_and_contents = libimobiledevice.afc_remove_path_and_contents
afc_remove_path_and_contents.argtypes = [c_void_p, c_char_p]
afc_remove_path_and_contents.restype = c_int

# afc_error_t afc_get_device_info_key(afc_client_t client, const char *key, char **value);
afc_get_device_info_key = libimobiledevice.afc_get_device_info_key
afc_get_device_info_key.argtypes = [c_void_p, c_char_p, c_char_p]
afc_get_device_info_key.restype = c_int

# afc_error_t afc_dictionary_free(char **dictionary);
afc_dictionary_free = libimobiledevice.afc_dictionary_free
afc_dictionary_free.argtypes = [POINTER(c_char_p)]
afc_dictionary_free.restype = c_int