import json
import os

from device_service import DeviceService
from libimobiledevice import IDeviceEventType
from lockdown_service import LockdownService

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class Device(object):

    def __init__(self, serial, device_name, model, device_info, connected):
        self.serial = serial
        self.device_name = device_name
        self.model = model
        self.device_info = device_info
        self.connected = connected

    def __str__(self):
        return "[Device] udid=%s, device_name=%s, model=%s" % (self.serial, self.device_name, self.model)

class DeviceManager(object):

    def __init__(self):
        self._device_service = DeviceService()
        self._device_service.subscribe(self._on_device_changed)
        self._device_map = {}
        self._listeners = []

        self._refresh_device_map()

    def __del__(self):
        pass

    def _refresh_device_map(self):
        devices = self._device_service.get_device_list()
        for device in devices:
            udid = device['udid']
            if udid not in self._device_map:
                device_info, error = self.get_device_info(udid)
                device_name = "unknown"
                product_type = "unknown"
                if device_info:
                    device_name = device_info['device_name']
                    product_type = device_info['product_type']
                device = Device(udid, device_name, product_type, device_info, connected=True)
                self._device_map[udid] = device

    def _on_device_changed(self, event):
        print("on_device_changed", event)
        self._refresh_device_map()
        device = self._device_map[event['udid']]
        if event['type'] == IDeviceEventType.IDEVICE_DEVICE_ADD:
            device.connected = True
            for l in self._listeners:
                l.on_device_connect(device)
        elif event['type'] == IDeviceEventType.IDEVICE_DEVICE_REMOVE:
            device.connected = False
            for l in self._listeners:
                l.on_device_disconnect(device)

    def register_device_change_listener(self, listener):
        self._listeners.append(listener)

    def unregister_device_change_listener(self, listener):
        self._listeners.remove(listener)

    def get_device_info(self, udid):
        device = self._device_service.new_device(udid)
        if not device:
            return None, "No device connected with udid(%s)" % udid

        lockdown_service = LockdownService()
        lockdown_client = lockdown_service.new_client(device)

        values, error = lockdown_service.get_value(lockdown_client, key=None)
        if error:
            return None, error

        device_name = values['DeviceName']
        product_version = values['ProductVersion']
        build_version = values['BuildVersion']
        product_type = values['ProductType']
        unique_device_id = values['UniqueDeviceID']
        os = "%s(%s)" % (product_version, build_version)

        device_info = self._get_device_info_from_configs(product_type)
        device_type = device_info['deviceType']
        cpu_type = device_info['cpuInfo']['hwType']
        cpu_arch = device_info['cpuInfo']['processor']
        cpu_core_num = device_info['cpuInfo']['coreNum']
        min_cpu_freq = int(int(device_info['cpuInfo']['minCpuFreq']) / 1000)
        max_cpu_freq = int(int(device_info['cpuInfo']['maxCpuFreq']) / 1000)
        cpu_freq = "[%s, %s]" % (str(min_cpu_freq), str(max_cpu_freq))
        gpu_type = device_info['gpuInfo']
        battery_info = device_info['batteryInfo']  # TODO:

        lockdown_service.free_client(lockdown_client)
        self._device_service.free_device(device)

        return {
               "os_type": "iOS",
               "device_name": device_name,
               "device_type": device_type,
               "product_type": product_type,
               "os": os,
               "cpu_type": cpu_type,
               "cpu_arch": cpu_arch,
               "cpu_core_num": cpu_core_num,
               "cpu_freq": cpu_freq,
               "gpu_type": gpu_type,
        }, None

    def _get_device_info_from_configs(self, product_type):
        with open(os.path.join(ROOT_DIR, "ios_deviceinfo_new.json")) as fp: # TODO:
            device_info_map = json.load(fp)
            if product_type in device_info_map:
                return device_info_map[product_type]
        return None

    def get_connected_devices(self):
        return list(self._device_map.values())