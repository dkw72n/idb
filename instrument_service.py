import argparse
from ctypes import cdll, c_int, c_char, POINTER, c_char_p, c_byte, pointer, cast, c_void_p, c_uint, create_string_buffer, Structure, c_uint32, c_int32, c_uint16, c_uint64, c_int64, sizeof, create_string_buffer, string_at
from threading import Thread, Event
import time
import traceback
from service import Service
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

def setup_parser(parser):
    instrument_cmd_parsers = parser.add_subparsers(dest="instrument_cmd")
    instrument_cmd_parsers.required = True
    instrument_cmd_parsers.add_parser("channels")
    instrument_cmd_parsers.add_parser("sysmontap")
    instrument_cmd_parsers.add_parser("graphics")
    instrument_cmd_parsers.add_parser("running")
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
    done.wait()
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
    done.wait()
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
    done.wait()
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

def test(rpc):

    done = Event()
    def _notifyOfPublishedCapabilities(res):
        done.set()
    def dropped_message(res):
        print("[DROP]", res.parsed, res.raw.channel_code)
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
    #print("runningProcesses", rpc.call("com.apple.instruments.server.services.deviceinfo", "runningProcesses").parsed)
    channel = "com.apple.xcode.debug-gauge-data-providers.Energy"
    print("query", rpc.call(channel, "supportedAttributes").parsed)
    print("start", rpc.call(channel, "startSamplingForPIDs:", {5141}).parsed)
    #print("start", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:", 0).parsed)
    #print("opengl", rpc.call("com.apple.instruments.server.services.graphics.opengl", "startSamplingAtTimeInterval:processIdentifier:", 0, 5013.0).parsed)
    #time.sleep(10)
    #print("stop", rpc.call("com.apple.instruments.server.services.graphics.opengl", "stopSampling").parsed)
    #print("cleanup", rpc.call("com.apple.instruments.server.services.graphics.opengl", "cleanup").parsed)
    #time.sleep(3)
    try:
        while 1: time.sleep(10)
    except:
        pass
    rpc.stop()

def instrument_main(_, opts):
    device_service = DeviceService()
    device = device_service.new_device(opts.udid)
    if not device:
        print("failed to new device")
        return
    rpc = InstrumentRPC()
    if not rpc.init(device):
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
        else:
            # print("unknown cmd:", opts.instrument_cmd)
            test(rpc)
    except:
        traceback.print_exc()
    rpc.deinit()
    device_service.free_device(device)
    return

class DTXClientMixin:

    def send_dtx(self, client, dtx):
        buffer = dtx.to_bytes()
        return self.send_all(client, buffer)

    def recv_dtx(self, client, timeout=-1):
        header_buffer = self.recv_all(client, sizeof(DTXMessageHeader), timeout=timeout)
        if not header_buffer:
            return None
        header = DTXMessageHeader.from_buffer_copy(header_buffer)
        body_buffer = self.recv_all(client, header.length, timeout=timeout)
        if not body_buffer:
            return None
        return DTXMessage.from_bytes(header_buffer + body_buffer)

class InstrumentService(Service, DTXClientMixin):
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

class InstrumentRPCParseError:
    pass

InstrumentServiceConnectionLost = DTXMessage().set_selector(pyobject_to_selector("[PerfCat] Connection Lost!"))

class InstrumentRPCResult:
    def __init__(self, dtx):
        self.raw = dtx
        if self.raw is None:
            self.parsed = None
            self.plist = None
            return
        sel = dtx.get_selector()
        if not sel:
            self.plist = ""
            self.parsed = None
            return
        self.plist = bplist.parse(sel)
        try:
            self.parsed = archiver.unarchive(sel)
        except:
            self.parsed = InstrumentRPCParseError()
        
class InstrumentRPC:

    def __init__(self):
        self._cli = None
        self._is = InstrumentService()
        self._recv_thread = None
        self._running = False
        self._callbacks = {}
        self._sync_waits = {}
        self._next_identifier = 1
        self._channels = {}
        self._receiver_exiting = False
        self._unhanled_callback = None
        self._channel_callbacks = {}

    def init(self, device):
        """
        初始化 instrument rpc 服务:
        成功后必须调用 deinit 反初始化
        :param device: 由DeviceService创建的device对象（C对象）
        :return: bool 是否成功
        """
        self._cli = self._is.new_client(device)
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
        self._running = True
        self._recv_thread = Thread(target=self._receiver, name="InstrumentRecevier")
        self._recv_thread.start()
        return True

    def stop(self):
        """
        停止 instrument rpc 服务
        :return: 无返回值
        """
        self._running = False
        self._recv_thread.join()
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
        for aux in auxiliaries:
            dtx.add_auxiliary(pyobject_to_auxiliary(aux))
        if sync:
            dtx.expects_reply = True
            param = {"result": None, "event": Event()}
            self._sync_waits[dtx.identifier] = param
        #print("perfcat => ios")
        #hexdump(dtx.to_bytes())
        self._is.send_dtx(self._cli, dtx)
        if sync:
            param['event'].wait()
            ret = param['result']
            #print("ios => perfcat")
            #hexdump(ret.to_bytes())
            self._sync_waits.pop(dtx.identifier)
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
            if dtx.identifier in self._sync_waits:
                param = self._sync_waits[dtx.identifier]
                param['result'] = dtx
                param['event'].set()
            elif 2**32 - dtx.channel_code in self._channel_callbacks:
                #print("subscription!!")
                try:
                    self._channel_callbacks[2**32 - dtx.channel_code](InstrumentRPCResult(dtx))
                except:
                    traceback.print_exc()
            else:
                selector = selector_to_pyobject(dtx.get_selector())
                if selector and type(selector) is str and selector in self._callbacks:
                    try:
                        self._callbacks[selector](InstrumentRPCResult(dtx))
                    except:
                        traceback.print_exc()
                else:
                    if self._unhanled_callback:
                        try:
                            self._unhanled_callback(InstrumentRPCResult(dtx))
                        except:
                            traceback.print_exc
                    #print("dropped", selector, dtx, dtx.identifier, dtx.channel_code)
        self._receiver_exiting = True # to block incoming calls
        for identifier in self._sync_waits:
            self._sync_waits[identifier]['result'] = InstrumentServiceConnectionLost
            self._sync_waits[identifier]['event'].set()
        
                        
                

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
    print(opts)
    instrument_main(None, opts)


if __name__ == '__main__':
    #d = DTXMessage.from_bytes(sample_setconf)
    #print(archiver.unarchive(d.get_selector()))
    #for i in d._auxiliaries:
    #    print(auxiliary_to_pyobject(i))
    main()