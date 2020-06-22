import argparse
from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at
from threading import Thread, Event
import time
import traceback
from service import Service
import socket
import uuid
import threading
from zeroconf import ServiceBrowser, Zeroconf
from utils import aes_256_cbc_decrypt, aes_256_cbc_encrypt

from device_service import DeviceService
from libimobiledevice import            \
    instrument_client_start_service,    \
    instrument_client_free,             \
    instrument_receive,                 \
    instrument_receive_with_timeout,    \
    instrument_send_command,            \
    InstrumentError

from dtxlib import DTXMessage, DTXMessageHeader,    \
    auxiliary_to_pyobject, pyobject_to_auxiliary,   \
    pyobject_to_selector, selector_to_pyobject
from bpylist import archiver, bplist
from utils import parse_plist_to_xml
import struct

try:
    import pykp
except:
    pykp = None
    pass

allowed = '_qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890+-_=()*&^%$#@![]{}\\|;\':"<>?,./`~'

def hexdump(buf):
  def form1(b):
    return ' '.join(map(lambda x:'%02x' % x, b))
  def form2(b):
    return ''.join(map(lambda c: c if c in allowed else '.', b.decode('ascii', "replace")))
  LINE_BYTES = 32
  lines = [buf[i: i + LINE_BYTES] for i in range(0, len(buf), LINE_BYTES)]
  for l in lines:
    print(form1(l), form2(l))

def load_byte_from_hexdump(hd):
  return bytes(map(lambda a:int(a, 16), filter(None, hd.split())))

sample_setconf = load_byte_from_hexdump("""
79 5B 3D 1F 20 00 00 00 00 00 01 00 C7 05 00 00 70 00 00 00 00 00 00 00 19 00 00 00 01 00 00 00
02 00 00 00 23 05 00 00 B7 05 00 00 00 00 00 00 F0 05 00 00 00 00 00 00 13 05 00 00 00 00 00 00
0A 00 00 00 02 00 00 00 07 05 00 00 62 70 6C 69 73 74 30 30 D4 01 02 03 04 05 79 7A 7B 58 24 6F
62 6A 65 63 74 73 58 24 76 65 72 73 69 6F 6E 59 24 61 72 63 68 69 76 65 72 54 24 74 6F 70 AF 10
40 06 07 18 19 1A 1B 1C 1D 1E 1F 2A 1B 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D
3E 3F 40 41 42 43 44 45 46 47 48 49 4A 4B 51 52 53 67 68 69 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75
76 55 24 6E 75 6C 6C D3 08 09 0A 0B 0C 12 56 24 63 6C 61 73 73 57 4E 53 2E 6B 65 79 73 5A 4E 53
2E 6F 62 6A 65 63 74 73 80 3F A5 0D 0E 0F 10 11 80 02 80 03 80 04 80 05 80 07 A5 13 14 15 16 17
80 08 80 09 80 2D 80 2E 80 3E 52 75 72 59 70 72 6F 63 41 74 74 72 73 52 62 6D 58 63 70 75 55 73
61 67 65 58 73 79 73 41 74 74 72 73 5E 73 61 6D 70 6C 65 49 6E 74 65 72 76 61 6C 11 03 E8 D2 08
0A 20 21 80 2C A8 22 23 24 25 26 27 28 29 80 0A 80 0B 80 11 80 13 80 16 80 19 80 24 80 2A 5E 6D
65 6D 56 69 72 74 75 61 6C 53 69 7A 65 5A 70 72 6F 63 53 74 61 74 75 73 58 61 70 70 53 6C 65 65
70 53 75 69 64 59 76 6D 50 61 67 65 49 6E 73 58 6D 65 6D 52 53 68 72 64 59 63 74 78 53 77 69 74
63 68 5D 6D 65 6D 43 6F 6D 70 72 65 73 73 65 64 5A 69 6E 74 57 61 6B 65 75 70 73 5E 63 70 75 54
6F 74 61 6C 53 79 73 74 65 6D 5E 72 65 73 70 6F 6E 73 69 62 6C 65 50 49 44 5D 70 68 79 73 46 6F
6F 74 70 72 69 6E 74 5C 63 70 75 54 6F 74 61 6C 55 73 65 72 5C 73 79 73 43 61 6C 6C 73 55 6E 69
78 5F 10 0F 6D 65 6D 52 65 73 69 64 65 6E 74 53 69 7A 65 5C 73 79 73 43 61 6C 6C 73 4D 61 63 68
5C 6D 65 6D 50 75 72 67 65 61 62 6C 65 5D 64 69 73 6B 42 79 74 65 73 52 65 61 64 5D 6D 61 63 68
50 6F 72 74 43 6F 75 6E 74 5C 5F 5F 73 75 64 64 65 6E 54 65 72 6D 56 5F 5F 61 72 63 68 58 6D 65
6D 52 50 72 76 74 57 6D 73 67 53 65 6E 74 54 70 70 69 64 5B 74 68 72 65 61 64 43 6F 75 6E 74 57
6D 65 6D 41 6E 6F 6E 5F 10 10 64 69 73 6B 42 79 74 65 73 57 72 69 74 74 65 6E 54 70 67 69 64 56
66 61 75 6C 74 73 57 6D 73 67 52 65 63 76 5C 5F 5F 72 65 73 74 72 69 63 74 65 64 53 70 69 64 59
5F 5F 73 61 6E 64 62 6F 78 D2 4C 4D 4E 4F 5A 24 63 6C 61 73 73 6E 61 6D 65 58 24 63 6C 61 73 73
65 73 57 4E 53 41 72 72 61 79 A2 4E 50 58 4E 53 4F 62 6A 65 63 74 10 00 09 D2 08 0A 54 55 80 2C
AF 10 11 56 57 58 59 5A 5B 5C 5D 5E 5F 60 61 62 63 64 65 66 80 30 80 1C 80 25 80 23 80 31 80 32
80 33 80 34 80 35 80 36 80 37 80 38 80 39 80 3A 80 3B 80 3C 80 3D 5C 64 69 73 6B 57 72 69 74 65
4F 70 73 5F 10 15 76 6D 43 6F 6D 70 72 65 73 73 6F 72 50 61 67 65 43 6F 75 6E 74 5E 76 6D 45 78
74 50 61 67 65 43 6F 75 6E 74 5B 76 6D 46 72 65 65 43 6F 75 6E 74 5E 76 6D 49 6E 74 50 61 67 65
43 6F 75 6E 74 5F 10 10 76 6D 50 75 72 67 65 61 62 6C 65 43 6F 75 6E 74 5C 6E 65 74 50 61 63 6B
65 74 73 49 6E 5B 76 6D 57 69 72 65 43 6F 75 6E 74 5A 6E 65 74 42 79 74 65 73 49 6E 5D 6E 65 74
50 61 63 6B 65 74 73 4F 75 74 5B 64 69 73 6B 52 65 61 64 4F 70 73 5B 76 6D 55 73 65 64 43 6F 75
6E 74 5D 5F 5F 76 6D 53 77 61 70 55 73 61 67 65 5B 6E 65 74 42 79 74 65 73 4F 75 74 12 3B 9A CA
00 D2 4C 4D 77 78 5C 4E 53 44 69 63 74 69 6F 6E 61 72 79 A2 77 50 12 00 01 86 A0 5F 10 0F 4E 53
4B 65 79 65 64 41 72 63 68 69 76 65 72 D1 7C 7D 54 72 6F 6F 74 80 01 00 08 00 11 00 1A 00 23 00
2D 00 32 00 75 00 7B 00 82 00 89 00 91 00 9C 00 9E 00 A4 00 A6 00 A8 00 AA 00 AC 00 AE 00 B4 00
B6 00 B8 00 BA 00 BC 00 BE 00 C1 00 CB 00 CE 00 D7 00 E0 00 EF 00 F2 00 F7 00 F9 01 02 01 04 01
06 01 08 01 0A 01 0C 01 0E 01 10 01 12 01 21 01 2C 01 35 01 39 01 43 01 4C 01 56 01 64 01 6F 01
7E 01 8D 01 9B 01 A8 01 B5 01 C7 01 D4 01 E1 01 EF 01 FD 02 0A 02 11 02 1A 02 22 02 27 02 33 02
3B 02 4E 02 53 02 5A 02 62 02 6F 02 73 02 7D 02 82 02 8D 02 96 02 9E 02 A1 02 AA 02 AC 02 AD 02
B2 02 B4 02 C8 02 CA 02 CC 02 CE 02 D0 02 D2 02 D4 02 D6 02 D8 02 DA 02 DC 02 DE 02 E0 02 E2 02
E4 02 E6 02 E8 02 EA 02 F7 03 0F 03 1E 03 2A 03 39 03 4C 03 59 03 65 03 70 03 7E 03 8A 03 96 03
A4 03 B0 03 B5 03 BA 03 C7 03 CA 03 CF 03 E1 03 E4 03 E9 00 00 00 00 00 00 02 01 00 00 00 00 00
00 00 7E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 EB 62 70 6C 69 73 74 30 30 D4 01 02 03 04
05 06 07 0A 58 24 76 65 72 73 69 6F 6E 59 24 61 72 63 68 69 76 65 72 54 24 74 6F 70 58 24 6F 62
6A 65 63 74 73 12 00 01 86 A0 5F 10 0F 4E 53 4B 65 79 65 64 41 72 63 68 69 76 65 72 D1 08 09 54
72 6F 6F 74 80 01 A2 0B 0C 55 24 6E 75 6C 6C 5A 73 65 74 43 6F 6E 66 69 67 3A 08 11 1A 24 29 32
37 49 4C 51 53 56 5C 00 00 00 00 00 00 01 01 00 00 00 00 00 00 00 0D 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 67
""")

coreprofile_cfg = load_byte_from_hexdump("""
0a 00 00 00 02 00 00 00 08 04 00 00 62 70 6c 69 73 74 30 30 d4 01 02 03 04 05 70 71 72 58 24 6f
62 6a 65 63 74 73 58 24 76 65 72 73 69 6f 6e 59 24 61 72 63 68 69 76 65 72 54 24 74 6f 70 af 10
2a 06 07 14 15 16 17 18 19 1a 1e 28 29 2a 2b 2c 2d 2e 34 35 36 37 38 39 3a 3b 3c 43 44 48 4c 4d
53 57 5a 19 5e 62 63 66 69 6d 6e 55 24 6e 75 6c 6c d3 08 09 0a 0b 0c 10 56 24 63 6c 61 73 73 57
4e 53 2e 6b 65 79 73 5a 4e 53 2e 6f 62 6a 65 63 74 73 80 29 a3 0d 0e 0f 80 02 80 04 80 05 a3 11
12 13 80 06 80 08 80 28 52 75 72 52 62 6d 52 74 63 52 72 70 11 01 f4 10 00 d2 08 0a 1b 1c 80 20
a1 1d 80 09 d3 08 09 0a 1f 20 24 80 27 a3 21 22 23 80 0a 80 0d 80 0f a3 25 26 27 80 10 80 1d 80
26 54 6b 64 66 32 53 63 73 64 53 6b 64 66 52 74 6b 52 74 61 54 75 75 69 64 d2 08 0a 2f 30 80 19
a3 31 32 33 80 11 80 14 80 18 12 25 99 00 00 12 85 02 00 00 12 31 ca 00 00 12 31 b0 00 00 12 85
01 00 00 12 85 c0 00 00 12 85 20 00 00 12 31 80 01 08 d2 3d 3e 3f 40 5a 24 63 6c 61 73 73 6e 61
6d 65 58 24 63 6c 61 73 73 65 73 5c 4e 53 4d 75 74 61 62 6c 65 53 65 74 a3 3f 41 42 55 4e 53 53
65 74 58 4e 53 4f 62 6a 65 63 74 10 80 d2 08 45 46 47 59 4e 53 2e 73 74 72 69 6e 67 80 1c 5f 10
82 3c 65 76 65 6e 74 73 3e 3c 65 76 65 6e 74 20 74 79 70 65 3d 22 4b 44 65 62 75 67 22 20 63 6c
61 73 73 3d 22 34 39 22 20 73 75 62 63 6c 61 73 73 3d 22 31 37 36 22 20 63 6f 64 65 3d 22 2a 22
2f 3e 3c 65 76 65 6e 74 20 74 79 70 65 3d 22 4b 44 65 62 75 67 22 20 63 6c 61 73 73 3d 22 34 39
22 20 73 75 62 63 6c 61 73 73 3d 22 31 32 38 22 20 63 6f 64 65 3d 22 22 2f 3e 3c 2f 65 76 65 6e
74 73 3e d2 3d 3e 49 4a 5f 10 0f 4e 53 4d 75 74 61 62 6c 65 53 74 72 69 6e 67 a3 49 4b 42 58 4e
53 53 74 72 69 6e 67 10 03 d2 08 0a 4e 4f 80 25 a3 50 51 52 80 1f 80 21 80 23 d2 08 0a 54 55 80
20 a1 56 80 1d d2 3d 3e 58 59 57 4e 53 41 72 72 61 79 a2 58 42 d2 08 0a 5b 5c 80 20 a1 5d 80 22
d2 08 0a 5f 60 80 20 a1 61 80 24 10 02 d2 3d 3e 64 65 5e 4e 53 4d 75 74 61 62 6c 65 41 72 72 61
79 a3 64 58 42 d2 08 45 67 68 80 1c 5f 10 24 32 43 34 36 42 36 31 41 2d 43 44 41 39 2d 34 44 35
39 2d 42 39 30 31 2d 32 32 45 32 38 42 30 38 43 32 36 30 d2 3d 3e 6a 6b 5f 10 13 4e 53 4d 75 74
61 62 6c 65 44 69 63 74 69 6f 6e 61 72 79 a3 6a 6c 42 5c 4e 53 44 69 63 74 69 6f 6e 61 72 79 10
0a d2 3d 3e 6c 6f a2 6c 42 12 00 01 86 a0 5f 10 0f 4e 53 4b 65 79 65 64 41 72 63 68 69 76 65 72
d1 73 74 54 72 6f 6f 74 80 01 00 08 00 11 00 1a 00 23 00 2d 00 32 00 5f 00 65 00 6c 00 73 00 7b
00 86 00 88 00 8c 00 8e 00 90 00 92 00 96 00 98 00 9a 00 9c 00 9f 00 a2 00 a5 00 a8 00 ab 00 ad
00 b2 00 b4 00 b6 00 b8 00 bf 00 c1 00 c5 00 c7 00 c9 00 cb 00 cf 00 d1 00 d3 00 d5 00 da 00 de
00 e2 00 e5 00 e8 00 ed 00 f2 00 f4 00 f8 00 fa 00 fc 00 fe 01 03 01 08 01 0d 01 12 01 17 01 1c
01 21 01 26 01 2b 01 36 01 3f 01 4c 01 50 01 56 01 5f 01 61 01 66 01 70 01 72 01 f7 01 fc 02 0e
02 12 02 1b 02 1d 02 22 02 24 02 28 02 2a 02 2c 02 2e 02 33 02 35 02 37 02 39 02 3e 02 46 02 49
02 4e 02 50 02 52 02 54 02 59 02 5b 02 5d 02 5f 02 61 02 66 02 75 02 79 02 7e 02 80 02 a7 02 ac
02 c2 02 c6 02 d3 02 d5 02 da 02 dd 02 e2 02 f4 02 f7 02 fc 00 00 00 00 00 00 02 01 00 00 00 00
00 00 00 75 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 fe
""")
def setup_parser(parser):
    parser.add_argument("--wireless", default=False, action='store_true')
    instrument_cmd_parsers = parser.add_subparsers(dest="instrument_cmd")
    instrument_cmd_parsers.required = True
    instrument_cmd_parsers.add_parser("channels")
    instrument_cmd_parsers.add_parser("sysmontap")
    instrument_cmd_parsers.add_parser("graphics")
    instrument_cmd_parsers.add_parser("running")
    instrument_cmd_parsers.add_parser("codec")
    instrument_cmd_parsers.add_parser("timeinfo")
    p = instrument_cmd_parsers.add_parser("execname")
    p.add_argument("pid", type=float)
    p = instrument_cmd_parsers.add_parser("activity")
    p.add_argument("pid", type=float)
    instrument_cmd_parsers.add_parser("networking")
    p = instrument_cmd_parsers.add_parser("energy")
    p.add_argument("pid", type=float)
    p = instrument_cmd_parsers.add_parser("netstat")
    p.add_argument("pid", type=float)
    p = instrument_cmd_parsers.add_parser("kill")
    p.add_argument("pid", type=float)
    p = instrument_cmd_parsers.add_parser("launch")
    p.add_argument("bundleid")
    p = instrument_cmd_parsers.add_parser("monitor")
    p.add_argument("pid", type=float)
    p.add_argument("--network", default=True, action='store_true')
    instrument_cmd_parsers.add_parser("coreprofile")
    instrument_cmd_parsers.add_parser("power")
    instrument_cmd_parsers.add_parser("wireless")

    instrument_cmd_parsers.add_parser("test")

def cmd_channels(rpc):
    done = Event()
    def _notifyOfPublishedCapabilities(res):
        done.set()
        print("Published capabilities:")
        for k, v in auxiliary_to_pyobject(res.raw._auxiliaries[0]).items():
            print(k, v)
    rpc.register_callback("_notifyOfPublishedCapabilities:", _notifyOfPublishedCapabilities)
    rpc.start()
    if not done.wait(5):
        print("[WARN] timeout waiting capabilities")
    rpc.stop()

def cmd_sysmontap(rpc):
    done = Event()
    def _notifyOfPublishedCapabilities(res):
        done.set()
    def dropped_message(res):
        print("[DROP]", res.parsed, res.raw.channel_code)
    def on_sysmontap_message(res):
        print("[SYSMONTAP]", res.parsed)
    rpc.register_callback("_notifyOfPublishedCapabilities:", _notifyOfPublishedCapabilities)
    rpc.register_unhandled_callback(dropped_message)
    rpc.start()
    if not done.wait(5):
        print("[WARN] timeout waiting capabilities")
    # print("set", rpc.call("com.apple.instruments.server.services.sysmontap", "setSamplingRate:", 40.0).parsed) # 没反应
    rpc.call("com.apple.instruments.server.services.sysmontap", "setConfig:", {
        'ur': 1000, 
        'procAttrs': ['memVirtualSize', 'cpuUsage', 'ctxSwitch', 'intWakeups', 'physFootprint', 'memResidentSize', 'memAnon', 'pid', 'powerScore', 'diskBytesRead'], 
        'bm': 0, 
        'cpuUsage': True, 
        'sampleInterval': 1000000000}) # 改这个也没反应
    rpc.register_channel_callback("com.apple.instruments.server.services.sysmontap", on_sysmontap_message)
    print("start", rpc.call("com.apple.instruments.server.services.sysmontap", "start").parsed)
    try:
        while 1: time.sleep(10)
    except:
        pass
    print("stop", rpc.call("com.apple.instruments.server.services.sysmontap", "stop").parsed)
    rpc.stop()

def cmd_graphics(rpc):
    done = Event()
    def _notifyOfPublishedCapabilities(res):
        done.set()
    def dropped_message(res):
        print("[DROP]", res.parsed, res.raw.channel_code)
    def on_graphics_message(res):
        print("[GRAPHICS]", res.parsed)
    rpc.register_callback("_notifyOfPublishedCapabilities:", _notifyOfPublishedCapabilities)
    rpc.register_unhandled_callback(dropped_message)
    rpc.start()
    if not done.wait(5):
        print("[WARN] timeout waiting capabilities")
    rpc.register_channel_callback("com.apple.instruments.server.services.graphics.opengl", on_graphics_message)
    print("set", rpc.call("com.apple.instruments.server.services.graphics.opengl", "setSamplingRate:", 5.0).parsed) # 5 -> 0.5秒一条消息
    print("start", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:", 0.0).parsed)
    #print("start", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:processIdentifier:", 0, 0.0).parsed)
    try:
        while 1: time.sleep(10)
    except:
        pass
    print("stop", rpc.call("com.apple.instruments.server.services.graphics.opengl", "stopSampling").parsed)
    rpc.stop()

def cmd_monitor(rpc, pid, network_stat = True):
    done = Event()
    def _notifyOfPublishedCapabilities(res):
        done.set()
    def dropped_message(res):
        print("[DROP]", res.parsed, res.raw.channel_code)
    def on_graphics_message(res):
        print("[GRAPHICS]", res.parsed)
    decoder = None
    print(pykp)
    if pykp:
        decoder = pykp.KPDecoder()
    def on_channel_message(res):
        #print(res.parsed)
        #print(res.plist)
        if type(res.plist) is InstrumentRPCParseError:
            #print("load_byte_from_hexdump(\"\"\"")
            #hexdump(res.raw.get_selector())
            #print("\"\"\"),")
            if decoder:
                for code, time, arg1, arg2, arg3 in decoder.decode(res.raw.get_selector()):
                    if code & 0xff000000 == 0x31000000:
                        print(f"[COREPROFILE][{time}] code={code:08x} ({arg1}, {arg2}, {arg3})")
    rpc.register_callback("_notifyOfPublishedCapabilities:", _notifyOfPublishedCapabilities)
    rpc.register_unhandled_callback(dropped_message)
    rpc.start()
    if not done.wait(5):
        print("[WARN] timeout waiting capabilities")
    rpc.register_channel_callback("com.apple.instruments.server.services.graphics.opengl", on_graphics_message)
    print("set", rpc.call("com.apple.instruments.server.services.graphics.opengl", "setSamplingRate:", 5.0).parsed) # 5 -> 0.5秒一条消息
    print("start", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:", 0.0).parsed)
    #print("start", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:processIdentifier:", 0, 0.0).parsed)

    ch_cp = "com.apple.instruments.server.services.coreprofilesessiontap"
    rpc.register_channel_callback(ch_cp, on_channel_message)
    rpc.call(ch_cp, "setConfig:", InstrumentRPCRawArg(coreprofile_cfg))
    rpc.call(ch_cp, "start")
    if network_stat:
        print("start", rpc.call("com.apple.xcode.debug-gauge-data-providers.NetworkStatistics", "startSamplingForPIDs:", {pid}).parsed)
    try:
        while 1:
            if network_stat:
                attr = {}
                ret = rpc.call("com.apple.xcode.debug-gauge-data-providers.NetworkStatistics", "sampleAttributes:forPIDs:", attr, {pid})
                print("[NETSTAT]", ret.parsed)
            time.sleep(1)
    except:
        pass
    print("stop", rpc.call("com.apple.instruments.server.services.graphics.opengl", "stopSampling").parsed)
    print("stop", rpc.call(ch_cp, "stop").parsed)
    rpc.stop()
    time.sleep(1)

def cmd_running(rpc):
    rpc.start()
    running = rpc.call("com.apple.instruments.server.services.deviceinfo", "runningProcesses").parsed
    print("runningProcesses:")
    headers = '\t'.join(sorted(running[0].keys()))
    print(headers)
    for item in running:
        sorted_item = sorted(item.items())
        print('\t'.join(map(str, [v for _, v in sorted_item])))
    rpc.stop()

def cmd_codec(rpc):
    selector = "traceCodesFile"
    rpc.start()
    codecs = rpc.call("com.apple.instruments.server.services.deviceinfo", selector).parsed
    print(codecs)
    rpc.stop()

def cmd_timeinfo(rpc):
    rpc.start()
    machTimeInfo = rpc.call("com.apple.instruments.server.services.deviceinfo", "machTimeInfo").parsed
    print("machTimeInfo:", {
        "mach_absolute_time": machTimeInfo[0],
        "mach_timebase_info": {
            "number": machTimeInfo[1],
            "denom": machTimeInfo[2]
        }
    })
    rpc.stop()

def cmd_execname(rpc, pid):
    rpc.start()
    execname = rpc.call("com.apple.instruments.server.services.deviceinfo", "execnameForPid:", pid).parsed
    print(execname)
    rpc.stop()

def pre_call(rpc):
    done = Event()
    def _notifyOfPublishedCapabilities(res):
        done.set()
    def dropped_message(res):
        print("[DROP]", res.parsed, res.raw.channel_code)
    
    rpc.register_callback("_notifyOfPublishedCapabilities:", _notifyOfPublishedCapabilities)
    rpc.register_unhandled_callback(dropped_message)
    rpc.start()
    if not done.wait(5):
        print("[WARN] timeout waiting capabilities")



def cmd_networking(rpc):
    headers = {
        0: ['InterfaceIndex', "Name"],
        1: ['LocalAddress', 'RemoteAddress', 'InterfaceIndex', 'Pid', 'RecvBufferSize', 'RecvBufferUsed', 'SerialNumber', 'Kind'],
        2: ['RxPackets', 'RxBytes', 'TxPackets', 'TxBytes', 'RxDups', 'RxOOO', 'TxRetx', 'MinRTT', 'AvgRTT', 'ConnectionSerial']
    }
    msg_type = {
        0: "interface-detection",
        1: "connection-detected",
        2: "connection-update",
    }
    def on_callback_message(res):
        from socket import inet_ntoa, htons, inet_ntop, AF_INET6
        class SockAddr4(Structure):
            _fields_ = [
                ('len', c_byte),
                ('family', c_byte),
                ('port', c_uint16),
                ('addr', c_byte * 4),
                ('zero', c_byte * 8)
            ]
            def __str__(self):
                return f"{inet_ntoa(self.addr)}:{htons(self.port)}"

        class SockAddr6(Structure):
            _fields_ = [
                ('len', c_byte),
                ('family', c_byte),
                ('port', c_uint16),
                ('flowinfo', c_uint32),
                ('addr', c_byte * 16),
                ('scopeid', c_uint32)
            ]
            def __str__(self):
                return f"[{inet_ntop(AF_INET6, self.addr)}]:{htons(self.port)}"

        data = res.parsed
        if data[0] == 1:
            if len(data[1][0]) == 16:
                data[1][0] = str(SockAddr4.from_buffer_copy(data[1][0]))
                data[1][1] = str(SockAddr4.from_buffer_copy(data[1][1]))
            elif len(data[1][0]) == 28:
                data[1][0] = str(SockAddr6.from_buffer_copy(data[1][0]))
                data[1][1] = str(SockAddr6.from_buffer_copy(data[1][1]))
        print(msg_type[data[0]], dict(zip(headers[data[0]], data[1])))
        # print("[data]", res.parsed)
    pre_call(rpc)
    rpc.register_channel_callback("com.apple.instruments.server.services.networking", on_callback_message)
    print("replay", rpc.call("com.apple.instruments.server.services.networking", "replayLastRecordedSession").parsed)
    print("start", rpc.call("com.apple.instruments.server.services.networking", "startMonitoring").parsed)
    
    try:
        while 1: time.sleep(10)
    except:
        pass
    print("stopMonitoring", rpc.call("com.apple.instruments.server.services.networking", "stopMonitoring").parsed)
    rpc.stop()


def cmd_activity(rpc, pid):
    def on_callback_message(res):
        print("[ACTIVITY]", res.parsed)

    pre_call(rpc)
    rpc.register_channel_callback("com.apple.instruments.server.services.activity", on_callback_message)
    
    print("start", rpc.call("com.apple.instruments.server.services.activity", "startSamplingWithPid:", pid).parsed)
    
    try:
        while 1: time.sleep(10)
    except:
        pass
    print("stop", rpc.call("com.apple.instruments.server.services.activity", "stopSampling").parsed)
    rpc.stop()

def cmd_energy(rpc, pid):
    rpc.start()
    channel = "com.apple.xcode.debug-gauge-data-providers.Energy"
    attr = {}
    print("start", rpc.call(channel, "startSamplingForPIDs:", {pid}).parsed)
    try:
        while 1:
            ret = rpc.call(channel, "sampleAttributes:forPIDs:", attr, {pid})
            print(ret.parsed)
            time.sleep(1)
    except:
        pass
    rpc.stop()

def cmd_netstat(rpc, pid):
    rpc.start()
    channel = "com.apple.xcode.debug-gauge-data-providers.NetworkStatistics"
    attr = {}
    print("start", rpc.call(channel, "startSamplingForPIDs:", {pid}).parsed)
    try:
        while 1:
            ret = rpc.call(channel, "sampleAttributes:forPIDs:", attr, {pid})
            print(ret.parsed)
            time.sleep(1)
    except:
        pass
    rpc.stop()

def cmd_kill(rpc, pid):
    rpc.start()
    channel = "com.apple.instruments.server.services.processcontrol"
    print(rpc.call(channel, "killPid:", pid).parsed)
    rpc.stop()

def cmd_coreprofile(rpc):
    decoder = None
    print(pykp)
    if pykp:
        decoder = pykp.KPDecoder()
    def on_channel_message(res):
        #print(res.parsed)
        #print(res.plist)
        if type(res.plist) is InstrumentRPCParseError:
            #print("load_byte_from_hexdump(\"\"\"")
            #hexdump(res.raw.get_selector())
            #print("\"\"\"),")
            if decoder:
                for code, time, arg1, arg2, arg3 in decoder.decode(res.raw.get_selector()):
                    print(f"[{time}] code={code:08x} ({arg1}, {arg2}, {arg3})")
    
    rpc.start()
    channel = "com.apple.instruments.server.services.coreprofilesessiontap"
    rpc.register_channel_callback(channel, on_channel_message)
    rpc.call(channel, "setConfig:", InstrumentRPCRawArg(coreprofile_cfg))
    rpc.call(channel, "start")
    try:
        while 1: time.sleep(10)
    except:
        pass
    rpc.call(channel, "stop")
    rpc.stop()

def cmd_power(rpc):
    headers = ['startingTime', 'duration', 'level'] # DTPower
    ctx = {
        'remained': b''
    }
    def on_channel_message(res):
        print(res.parsed)
        ctx['remained'] += res.parsed['data']
        cur = 0
        while cur + 3 * 8 <= len(ctx['remained']):
            print("[level.dat]", dict(zip(headers, struct.unpack('>ddd', ctx['remained'][cur: cur + 3 * 8]))))
            cur += 3 * 8
            pass
        ctx['remained'] = ctx['remained'][cur:]
        #print(res.plist)
        #print(res.raw.get_selector())
    rpc.start()
    channel = "com.apple.instruments.server.services.power"
    rpc.register_channel_callback(channel, on_channel_message)
    stream_num = rpc.call(channel, "openStreamForPath:", "live/level.dat").parsed
    print("open", stream_num)
    print("start", rpc.call(channel, "startStreamTransfer:", float(stream_num)).parsed)
    print("[!] wait a few seconds, be patient...")
    try:
        while 1: time.sleep(10)
    except:
        pass
    print("stop", rpc.call(channel, "endStreamTransfer:", float(stream_num)).parsed)
    rpc.stop()


def cmd_wireless(rpc):
    def dropped_message(res):
        print("[DROP]", res.plist, res.raw.channel_code)
        pass
    def channel_canceled(res):
        print("not supported:", res.plist)
        rpc.stop()
    rpc.register_unhandled_callback(dropped_message)
    rpc.register_callback("_channelCanceled:", channel_canceled)
    rpc.start()
    channel = "com.apple.instruments.server.services.wireless"
    enabled = rpc.call(channel, "isServiceEnabled").parsed
    print("enabled", enabled)
    if enabled:
        print("remove", rpc.call(channel, "removeDaemonFromService").parsed)
    print("start", rpc.call(channel, "startServerDaemonWithName:type:passphrase:", "perfcat", float(77498864), "U" * 32).parsed)
    enabled = rpc.call(channel, "isServiceEnabled").parsed
    print("enabled", enabled)
    if enabled:
        try:
            while 1: time.sleep(1)
        except:
            pass
        print("remove", rpc.call(channel, "removeDaemonFromService").parsed)
    rpc.stop()

## sample:  launch com.ksg.tako
def cmd_launch(rpc, bundleid):
    def on_channel_message(res):
        print(res)
    rpc.start()
    channel = "com.apple.instruments.server.services.processcontrol"
    rpc.register_channel_callback(channel, on_channel_message)
    print("start", rpc.call(channel, "launchSuspendedProcessWithDevicePath:bundleIdentifier:environment:arguments:options:", "", bundleid, {}, [], {"StartSuspendedKey":0,"KillExisting":1}).parsed)
    rpc.stop()

def test(rpc):

    done = Event()
    def _notifyOfPublishedCapabilities(res):
        done.set()
    def dropped_message(res):
        #print("[DROP]", res.plist, res.raw.channel_code)
        pass
    def on_sysmontap_message(res):
        print("[Subs]", res.parsed)

    #rpc.register_callback("_notifyOfPublishedCapabilities:", _notifyOfPublishedCapabilities)
    rpc.register_unhandled_callback(dropped_message)
    rpc.start()
    #done.wait()
    #print("runningProcesses", rpc.call("com.apple.instruments.server.services.deviceinfo", "runningProcesses").parsed)
    # print("cleanup", rpc.call("com.apple.instruments.server.services.graphics.opengl", "cleanup").plist)
    # print("setConfig:", rpc.call("com.apple.instruments.server.services.sysmontap", "setConfig:", {'ur': 1000, 'procAttrs': ['memVirtualSize', 'cpuUsage', 'ctxSwitch', 'intWakeups', 'physFootprint', 'memResidentSize', 'memAnon', 'pid'], 'bm': 0, 'cpuUsage': True, 'sampleInterval': 2000000000}).parsed)
    #rpc.register_channel_callback("com.apple.instruments.server.services.sysmontap", on_sysmontap_message)
    #print("start", rpc.call("com.apple.instruments.server.services.sysmontap", "start").plist)
    #time.sleep(10)
    #print("stop", rpc.call("com.apple.instruments.server.services.sysmontap", "stop").plist)
    print("runningProcesses", rpc.call("com.apple.instruments.server.services.deviceinfo", "runningProcesses").parsed)
    #channel = "com.apple.instruments.server.services.power"
    #stream_num = rpc.call(channel, "openStreamForPath:", "live/level.dat").parsed
    #print("open", stream_num)
    #print("start", rpc.call(channel, "startStreamTransfer:", float(stream_num)).parsed)
    #channel = "com.apple.instruments.server.services.coreprofilesessiontap"
    #print("config", rpc.call(channel, "setConfig:", InstrumentRPCRawArg(coreprofile_cfg)).plist)
    #print("start", rpc.call(channel, "start").parsed)
    #print("start", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:", 0).parsed)
    #print("opengl", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:processIdentifier:", 0, 5013.0).parsed)
    #time.sleep(10)
    #print("stop", rpc.call("com.apple.instruments.server.services.graphics.opengl", "stopSampling").parsed)
    #print("cleanup", rpc.call("com.apple.instruments.server.services.graphics.opengl", "cleanup").parsed)
    #time.sleep(3)
    try:
        while 0: time.sleep(10)
    except:
        pass
    #print("stop", rpc.call(channel, "endStreamTransfer:", float(stream_num)).parsed)
    #print("stop", rpc.call(channel, "stop").parsed)
    rpc.stop()

"""

           +
           v
    +------+-------+
    |start wireless+-------failed-----+
    +------+-------+                  |
           |                          |
           |successful                |
           |                          |
+----------v------------+             |
|start zeroconf listener+--timeout--->+
+----------+------------+             |
           |                          |
           |found                     |
           |                          |
       +---v---+                      |
       |connect+-----------failed---->+
       +---+---+                      |
           |                          |
           |successful                |
           |                          |
        +--v---+               +------v----+
        |return|               |exit failed|
        +------+               +-----------+

"""

def prepare_rpc(rpc):
    def dropped_message(res):
        print("[DROP]", res.plist, res.raw.channel_code)
        pass
    def channel_canceled(res):
        print("not supported:", res.plist)
        rpc.stop()
    rpc.register_unhandled_callback(dropped_message)
    rpc.register_callback("_channelCanceled:", channel_canceled)
    rpc.start()

def start_wireless_mode(device): # returns (ret, name, preshared_key)
    rpc = InstrumentRPC()
    if not rpc.init(DTXUSBTransport, device):
        print("failed to init rpc")
        return
    prepare_rpc(rpc)
    try:

        channel = "com.apple.instruments.server.services.wireless"
        while 1:
            enabled = rpc.call(channel, "isServiceEnabled").parsed
            if not enabled: break
            print("remove", rpc.call(channel, "removeDaemonFromService").parsed)
            time.sleep(1)
        psk = uuid.uuid4().hex
        name = uuid.uuid4().hex[:4]
        print("start", rpc.call(channel, "startServerDaemonWithName:type:passphrase:", "perfcat_" + name, float(19900724), psk).parsed)
        enabled = rpc.call(channel, "isServiceEnabled").parsed
        # print("enabled", enabled)

        return bool(enabled), name, psk
    finally:
        rpc.stop()


def wait_for_wireless_device(name, timeout=None): # return (addresses, port)
    expecting_name = f"perfcat_{name}._19900724._tcp.local."
    print(f"[WIRELESS] expecting {expecting_name}")
    found = threading.Event()
    ctx = {}

    class MyListener:

        def remove_service(self, zeroconf, type, name):
            print("[Service] `%s` removed" % (name,))
            
        def add_service(self, zeroconf, type, name):
            info = zeroconf.get_service_info(type, name)
            print(f"[Service] `{name}` added, service info: `{info}`")
            if name == expecting_name:
                ctx['addresses'] = list(map(socket.inet_ntoa, info.addresses))
                ctx['port'] = info.port
                print(f"[Service] `{name}` found, `{ctx}`")
                found.set()

    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_19900724._tcp.local.", listener)
    
    if not found.wait(timeout):
        # timeout ?
        ctx['addresses'] = []
        ctx['port'] = 0
    browser.cancel()
    zeroconf.close()

    return ctx['addresses'], ctx['port']

def init_wireless_rpc(addresses, port, psk):
    for addr in addresses:
        rpc = InstrumentRPC()
        inited = rpc.init(DTXSockTransport, (addr, int(port), psk))
        if inited:
            return rpc
    return None


def get_usb_rpc(device):
    rpc = InstrumentRPC()
    if not rpc.init(DTXUSBTransport, device):
        return None
    return rpc

def get_wireless_rpc(device, timeout = 30):
    ret, name, psk = start_wireless_mode(device)
    #print(f"ret = {ret}, psk = {psk}")
    addresses, port = wait_for_wireless_device(name, timeout)
    #print(f"addrs = {addresses}, port = {port}")
    rpc = init_wireless_rpc(addresses, port, psk)
    #print(f"rpc = {rpc}")
    return rpc


class DTXFragment:

    def __init__(self, buf):
        self._header = DTXMessageHeader.from_buffer_copy(buf[:sizeof(DTXMessageHeader)])
        self._bufs = [buf]
        self.current_fragment_id = 0 if self._header.fragmentId == 0 else -1

    def append(self, buf):
        assert self.current_fragment_id >= 0, "attempt to append to an broken fragment"
        assert len(buf) >= sizeof(DTXMessageHeader)
        subheader = DTXMessageHeader.from_buffer_copy(buf[:sizeof(DTXMessageHeader)])
        assert subheader.fragmentCount == self._header.fragmentCount
        assert subheader.fragmentId == self.current_fragment_id + 1
        self.current_fragment_id = self.current_fragment_id + 1
        self._bufs.append(buf)

    @property
    def message(self):
        assert self.completed, "should only be called when completed"
        return DTXMessage.from_bytes(b''.join(self._bufs))

    @property
    def completed(self):
        return self.current_fragment_id + 1 == self._header.fragmentCount
    
    @property
    def key(self):
        return (self._header.channelCode, self._header.identifier)

    @property
    def header(self):
        return self._header.fragmentId == 0

class DTXClientMixin:

    def send_dtx(self, client, dtx):
        buffer = dtx.to_bytes()
        return self.send_all(client, buffer)

    def recv_dtx_fragment(self, client, timeout=-1):
        header_buffer = self.recv_all(client, sizeof(DTXMessageHeader), timeout=timeout)
        if not header_buffer:
            return None
        header = DTXMessageHeader.from_buffer_copy(header_buffer)
        if header.fragmentCount > 1 and header.fragmentId == 0:
            return header_buffer
        body_buffer = self.recv_all(client, header.length, timeout=timeout)
        if not body_buffer:
            return None
        return header_buffer + body_buffer

    def recv_dtx(self, client, timeout=-1):
        self._setup_manager()
        while 1:
            buf = self.recv_dtx_fragment(client, timeout)
            if not buf:
                return None
            fragment = DTXFragment(buf)
            if fragment.completed:
                return fragment.message
            value = getattr(client, 'value', id(client))
            key = (value, fragment.key)
            if fragment.header:
                self._dtx_demux_manager[key] = fragment
            else:
                assert key in self._dtx_demux_manager
                self._dtx_demux_manager[key].append(buf)
                if self._dtx_demux_manager[key].completed:
                    ret = self._dtx_demux_manager[key].message
                    self._dtx_demux_manager.pop(key)
                    return ret

    def _setup_manager(self):
        if hasattr(self, "_dtx_demux_manager"):
            return
        self._dtx_demux_manager = {}


class DTXSockTransport:

    def new_client(self, addr):
        """
        创建instrument client，用于调用instrument服务的其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: instrument client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = socket.create_connection((addr[0], addr[1]), timeout=3)
        print("[WIRELESS] connection made")
        self._psk = addr[2]
        self._done = threading.Event()
        return client

    def free_client(self, client):
        """
        释放 instrument client
        :param client: instrument client(C对象）
        :return: bool 是否成功
        """
        client.close()
        return True

    def send_all(self, client, buffer:bytes) -> bool:
        """
        向 instrument client 发送整块buffer
        成功时表示整块数据都被发出
        :param client: instrument client(C对象）
        :param buffer: 数据
        :return: bool 是否成功
        """
        while buffer:
            sent = client.send(buffer)
            buffer = buffer[sent:]
        return True

    def recv_all(self, client, length, timeout=-1) -> bytes:
        """
        从 instrument client 接收长度为 length 的 buffer
        成功时表示整块数据都被接收
        :param client: instrument client(C对象）
        :param length: 数据长度
        :return: 长度为 length 的 buffer, 失败时返回 None
        """
        received = 0
        ret = b''
        rb = None
        while len(ret) < length:
            err = 0
            l = length - len(ret)
            if l > 8192: l = 8192
            
            try:
                if timeout > 0:
                    client.settimeout(timeout/1000) # 毫秒, 需要转成秒
                    rb = client.recv(l)
                    client.settimeout(None)
                else:
                    rb = client.recv(l)
            except socket.timeout:
                pass

            if not rb:
                return None
            ret += rb
        return ret
        pass
    
    def pre_start(self, rpc):
        def challenge(res):
            #print("challenge:")
            bb = auxiliary_to_pyobject(res.raw.get_auxiliary_at(0))
            #hexdump(bb)
            key = self._psk.encode('utf-8')
            bb = bytes(bb)
            d = aes_256_cbc_decrypt(bb, key)
            #print(d)
            out = aes_256_cbc_encrypt(d[:-1] + b'ack\x00', key)
            #hexdump(out)
            self._done.set()
            return out
        rpc.register_callback("challenge:", challenge)
        print("[WIRELESS] challange callback registered")

    def post_start(self, rpc):
        self._done.wait()
        pass

class DTXUSBTransport:
    """
    Instruments 服务，用于监控设备状态, 采集性能数据
    """

    def new_client(self, device):
        """
        创建instrument client，用于调用instrument服务的其他接口
        :param device: 由DeviceService创建的device对象（C对象）
        :return: instrument client(C对象), 在使用完毕后请务必调用free_client来释放该对象内存
        """
        client = c_void_p()
        ret = instrument_client_start_service(device, pointer(client), b"PerfCat")
        if ret != InstrumentError.INSTRUMENT_E_SUCCESS:
            return None
        return client

    def free_client(self, client):
        """
        释放 instrument client
        :param client: instrument client(C对象）
        :return: bool 是否成功
        """
        ret = instrument_client_free(client)
        return  ret == InstrumentError.INSTRUMENT_E_SUCCESS

    def send_all(self, client:c_void_p, buffer:bytes) -> bool:
        """
        向 instrument client 发送整块buffer
        成功时表示整块数据都被发出
        :param client: instrument client(C对象）
        :param buffer: 数据
        :return: bool 是否成功
        """
        sent = c_uint()
        while buffer:
            if instrument_send_command(client, buffer, len(buffer), pointer(sent)) != InstrumentError.INSTRUMENT_E_SUCCESS:
                return False
            buffer = buffer[sent.value:]
        return True

    def recv_all(self, client:c_void_p, length, timeout=-1) -> bytes:
        """
        从 instrument client 接收长度为 length 的 buffer
        成功时表示整块数据都被接收
        :param client: instrument client(C对象）
        :param length: 数据长度
        :return: 长度为 length 的 buffer, 失败时返回 None
        """
        received = c_uint()
        ret = b''
        rb = create_string_buffer(8192)
        while len(ret) < length:
            err = 0
            l = length - len(ret)
            if l > 8192: l = 8192
            if timeout > 0:
                err = instrument_receive_with_timeout(client, rb, l, pointer(received), timeout)
            else:
                err = instrument_receive(client, rb, l, pointer(received))
            if err != InstrumentError.INSTRUMENT_E_SUCCESS:
                # print(f"service_receive error: {err}")
                return None
            ret += rb[:received.value]
        return ret
        pass
    
    def pre_start(self, rpc):
        pass

    def post_start(self, rpc):
        pass

class InstrumentRPCParseError:
    pass

InstrumentServiceConnectionLost = DTXMessage().set_selector(pyobject_to_selector("[PerfCat] Connection Lost!"))

class InstrumentRPCRawArg:
    def __init__(self, data:bytes):
        self.data = data

class InstrumentRPCResult:
    def __init__(self, dtx):
        self.raw = dtx
        if self.raw is None:
            self.xml = None
            self.parsed = None
            self.plist = None
            return
        sel = dtx.get_selector()
        if not sel:
            self.xml = ""
            self.plist = ""
            self.parsed = None
            return
        try:
            self.xml = parse_plist_to_xml(sel).decode('utf-8')
            #print(self.xml)
        except:
            #traceback.print_exc()
            self.xml = InstrumentRPCParseError()
        try:
            self.plist = bplist.parse(sel)
        except:
            self.plist = InstrumentRPCParseError()
            #print("--------", sel)
        try:
            self.parsed = archiver.unarchive(sel)
        except:
            self.parsed = InstrumentRPCParseError()
        
class InstrumentRPC:

    def __init__(self):
        self._cli = None
        self._is = None
        self._recv_thread = None
        self._running = False
        self._callbacks = {}
        self._sync_waits = {}
        self._next_identifier = 1
        self._channels = {}
        self._receiver_exiting = False
        self._unhanled_callback = None
        self._channel_callbacks = {}

    def init(self, transport, arg):
        """
        初始化 instrument rpc 服务:
        成功后必须调用 deinit 反初始化
        :param device: 由DeviceService创建的device对象（C对象）
        :return: bool 是否成功
        """
        class T(transport, DTXClientMixin):
            pass
        self._is = T()
        self._cli = self._is.new_client(arg)
        if self._cli is None:
            return False
        return True

    def deinit(self):
        """
        反初始化 instrument rpc 服务
        :return: 无返回值
        """
        if self._cli:
           self._is.free_client(self._cli)
           self._cli = None

    def start(self):
        """
        启动 instrument rpc 服务
        :return: bool 是否成功
        """
        if self._running:
            return True
        self._running = True
        self._recv_thread = Thread(target=self._receiver, name="InstrumentRecevier")
        self._is.pre_start(self)
        self._recv_thread.start()
        self._is.post_start(self)
        return True

    def stop(self):
        """
        停止 instrument rpc 服务
        :return: 无返回值
        """
        self._running = False
        if self._recv_thread:
            self._recv_thread.join()
            self._recv_thread = None
        pass
    
    def register_callback(self, selector, callback):
        """
        注册回调, 接受 instrument server 到 client 的远程调用
        :parma selector: 字符串, selector 名称
        :param callback: 回调函数, 接受一个参数, 类型是 InstrumentRPCResult 对象实例
        :return: 无返回值
        """
        self._callbacks[selector] = callback

    def register_channel_callback(self, channel, callback):
        """
        注册回调, 接受 instrument server 到 client 的远程调用
        :parma channel: 字符串, channel 名称
        :param callback: 回调函数, 接受一个参数, 类型是 InstrumentRPCResult 对象实例
        :return: 无返回值
        """
        channel_id = self._make_channel(channel)
        self._channel_callbacks[channel_id] = callback

    def register_unhandled_callback(self, callback):
        """
        注册回调, 接受 instrument server 到 client 的远程调用, 处理所以未被处理的消息
        :param callback: 回调函数, 接受一个参数, 类型是 InstrumentRPCResult 对象实例
        :return: 无返回值
        """
        self._unhanled_callback = callback

    def _make_channel(self, channel:str):
        if channel is None:
            return 0
        if channel in self._channels:
            return self._channels[channel]

        channel_id = len(self._channels) + 1
        dtx = self._call(True, 0, "_requestChannelWithCode:identifier:", channel_id, channel)
        if dtx.get_selector():
            print("Make Channel Error:", dtx.get_selector())
            raise RuntimeError("failed to make channel")
        self._channels[channel] = channel_id
        return channel_id

    def call(self, channel:str, selector:str, *auxiliaries):
        channel_id = self._make_channel(channel)
        ret = self._call(True, channel_id, selector, *auxiliaries)
        return InstrumentRPCResult(ret)

    def call_noret(self, channel:str, selector:str, *auxiliaries):
        channel_id = self._make_channel(channel)
        self._call(False, channel_id, selector, *auxiliaries)

    def _call(self, sync:bool, channel_id:int, selector:str, *auxiliaries):
        if self._receiver_exiting:
            raise RuntimeWarning("rpc service died")
        dtx = DTXMessage()
        dtx.identifier = self._next_identifier
        self._next_identifier += 1
        dtx.channel_code = channel_id
        dtx.set_selector(pyobject_to_selector(selector))
        wait_key = (dtx.channel_code, dtx.identifier)
        for aux in auxiliaries:
            if type(aux) is InstrumentRPCRawArg:
                dtx.add_auxiliary(aux.data)
            else:
                dtx.add_auxiliary(pyobject_to_auxiliary(aux))
        if sync:
            dtx.expects_reply = True
            param = {"result": None, "event": Event()}
            self._sync_waits[wait_key] = param
        #print("perfcat => ios")
        #hexdump(dtx.to_bytes())
        self._is.send_dtx(self._cli, dtx) # TODO: protect this line with mutex
        if sync:
            param['event'].wait()
            ret = param['result']
            #print("ios => perfcat")
            #hexdump(ret.to_bytes())
            self._sync_waits.pop(wait_key)
            return ret
    
    def _receiver(self):
        last_none = 0
        while self._running:
            dtx = self._is.recv_dtx(self._cli, 1000) # ms
            if dtx is None:
                cur = time.time()
                if cur - last_none < 0.1:
                    # print("fail too soon")
                    break
                last_none = cur
                continue
            # print("recv:", dtx)
            self._next_identifier = max(self._next_identifier, dtx.identifier + 1)
            wait_key = (dtx.channel_code, dtx.identifier)
            if wait_key in self._sync_waits:
                param = self._sync_waits[wait_key]
                param['result'] = dtx
                param['event'].set()
            elif 2**32 - dtx.channel_code in self._channel_callbacks:
                #print("subscription!!")
                try:
                    self._channel_callbacks[2**32 - dtx.channel_code](InstrumentRPCResult(dtx))
                except:
                    traceback.print_exc()
            else:
                try:
                    selector = selector_to_pyobject(dtx.get_selector())
                except:
                    selector = None

                if selector and type(selector) is str and selector in self._callbacks:
                    try:
                        ret = self._callbacks[selector](InstrumentRPCResult(dtx))
                        if dtx.expects_reply:
                            reply = dtx.new_reply()
                            reply.set_selector(pyobject_to_selector(ret))
                            reply._payload_header.flags = 0x3
                            self._is.send_dtx(self._cli, reply)
                    except:
                        traceback.print_exc()
                else:
                    if self._unhanled_callback:
                        try:
                            self._unhanled_callback(InstrumentRPCResult(dtx))
                        except:
                            traceback.print_exc()
                    #print("dropped", selector, dtx, dtx.identifier, dtx.channel_code)
        self._receiver_exiting = True # to block incoming calls
        for wait_key in self._sync_waits:
            self._sync_waits[wait_key]['result'] = InstrumentServiceConnectionLost
            self._sync_waits[wait_key]['event'].set()
        
                        
def instrument_main(device, opts):
    device_service = DeviceService()
    if opts.wireless:
        rpc = get_wireless_rpc(device)
    else:
        rpc = get_usb_rpc(device)
    if not rpc:
        print("failed to init rpc")
        device_service.free_device(device)
        return
    try:
        if opts.instrument_cmd == 'channels':
            cmd_channels(rpc)
        elif opts.instrument_cmd == 'sysmontap':
            cmd_sysmontap(rpc)
        elif opts.instrument_cmd == 'graphics':
            cmd_graphics(rpc)
        elif opts.instrument_cmd == 'running':
            cmd_running(rpc)
        elif opts.instrument_cmd == 'codec':
            cmd_codec(rpc)
        elif opts.instrument_cmd == 'timeinfo':
            cmd_timeinfo(rpc)
        elif opts.instrument_cmd == 'execname':
            cmd_execname(rpc, opts.pid)
        elif opts.instrument_cmd == 'monitor':
            cmd_monitor(rpc, opts.pid, opts.network)
        elif opts.instrument_cmd == 'activity':
            cmd_activity(rpc, opts.pid)
        elif opts.instrument_cmd == 'networking':
            cmd_networking(rpc)
        elif opts.instrument_cmd == 'energy':
            cmd_energy(rpc, opts.pid)
        elif opts.instrument_cmd == 'netstat':
            cmd_netstat(rpc, opts.pid)
        elif opts.instrument_cmd == 'kill':
            cmd_kill(rpc, opts.pid)
        elif opts.instrument_cmd == 'coreprofile':
            cmd_coreprofile(rpc)
        elif opts.instrument_cmd == 'power':
            cmd_power(rpc)
        elif opts.instrument_cmd == 'wireless':
            cmd_wireless(rpc)
        elif opts.instrument_cmd == 'launch':
            cmd_launch(rpc, opts.bundleid)
        else:
            # print("unknown cmd:", opts.instrument_cmd)
            test(rpc)
    except:
        traceback.print_exc()
    rpc.deinit()
    device_service.free_device(device)
    return                

def main():
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    opts = parser.parse_args()
    ds = DeviceService()
    devices = ds.get_device_list()
    if not devices:
        print("No devices attached!")
        return
    opts.udid = devices[0]['udid']
    device = ds.new_device(opts.udid)
    print(opts)
    instrument_main(device, opts)
    ds.free_device(device)

if __name__ == '__main__':
    #d = DTXMessage.from_bytes(open("core2.bin", "rb").read())
    #print(archiver.unarchive(d.get_selector()))
    #for i in d._auxiliaries:
    #    #print(auxiliary_to_pyobject(i))
    #    hexdump(i)
    main()
