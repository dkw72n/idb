import argparse
import json
import os

from device_service import DeviceService
from installation_proxy_service import InstallationProxyService
from lockdown_service import LockdownService
from libimobiledevice import IDeviceConnectionType
from instrument_service import instrument_main, setup_parser as setup_instrument_parser


def print_devices():
    print("List of devices attached")
    device_service = DeviceService()
    device_list = device_service.get_device_list()
    for device in device_list:
        conn_type = "USB" if device['conn_type'] == IDeviceConnectionType.CONNECTION_USBMUXD else "WIFI"
        print("%s device %s" % (device['udid'], conn_type))


def get_device_info_from_configs(product_type):
    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(ROOT_DIR, "ios_deviceinfo_new.json")) as fp:
        device_info_map = json.load(fp)
        if product_type in device_info_map:
            return device_info_map[product_type]
    return None


def get_device_info(udid):
    device_service = DeviceService()
    device = device_service.new_device(udid)

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

    device_info = get_device_info_from_configs(product_type)
    device_type = device_info['deviceType']
    cpu_type = device_info['cpuInfo']['hwType']
    cpu_arch = device_info['cpuInfo']['processor']
    cpu_core_num = device_info['cpuInfo']['coreNum']
    min_cpu_freq = int(int(device_info['cpuInfo']['minCpuFreq']) / 1000)
    max_cpu_freq = int(int(device_info['cpuInfo']['maxCpuFreq']) / 1000)
    cpu_freq = "[%s, %s]" % (str(min_cpu_freq), str(max_cpu_freq))
    gpu_type = device_info['gpuInfo']
    battery_info = device_info['batteryInfo'] # TODO:

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


def print_device_info(udid):
    device_info, error = get_device_info(udid)
    if error:
        print("Error: %s" % error)
        return
    print("Device info of device(udid: %s)" % udid)
    for key, value in device_info.items():
        print("%s: %s" % (key, value))


def print_get_value(udid, key=None):
    device_service = DeviceService()
    device = device_service.new_device(udid)

    lockdown_service = LockdownService()
    lockdown_client = lockdown_service.new_client(device)

    values, error = lockdown_service.get_value(lockdown_client, key=key)
    if error:
        print("Error: %s" % error)
        return

    print("Values of device(udid: %s)" % udid)
    if type(values) == dict:
        for name, value in values.items():
            print("%s: %s" % (name, value))
    else:
        print("%s: %s" % (key, values))
    lockdown_service.free_client(lockdown_client)
    device_service.free_device(device)


def get_app_list(udid):
    device_service = DeviceService()
    device = device_service.new_device(udid)

    installation_proxy_service = InstallationProxyService()
    installation_proxy_client = installation_proxy_service.new_client(device)
    user_apps = installation_proxy_service.browse(installation_proxy_client, "User")
    system_apps = installation_proxy_service.browse(installation_proxy_client, "System")
    installation_proxy_service.free_client(installation_proxy_client)
    return user_apps, system_apps


def print_applications(udid):
    user_apps, system_apps = get_app_list(udid)
    print("List of user applications installed:")
    for app in user_apps:
        for key, value in app.items():
            print("%s: %s" % (key, value))
        print("")
    print("")
    print("List of system applications installed:")
    for app in system_apps:
        for key, value in app.items():
            print("%s: %s" % (key, value))
        print("")


def main():
    argparser = argparse.ArgumentParser()
    # argparser.add_argument("command", help="command", choices=["devices", "deviceinfo", "devicename", "instrument"])
    cmd_parser = argparser.add_subparsers(dest="command")
    cmd_parser.add_parser("devices")
    cmd_parser.add_parser("applications")
    cmd_parser.add_parser("deviceinfo")
    # getvalue
    getvalue_parser = cmd_parser.add_parser("getvalue")
    getvalue_parser.add_argument("-k", "--key")
    # instrument
    instrument_parser = cmd_parser.add_parser("instrument")
    setup_instrument_parser(instrument_parser)


    argparser.add_argument("-u", "--udid", help="udid")

    args = argparser.parse_args()
    if args.command == "devices":
        print_devices()
    elif args.command == "applications":
        print_applications(args.udid)
    elif args.command == "deviceinfo":
        print_device_info(args.udid)
    elif args.command == "getvalue":
        print_get_value(args.udid, args.key)
    elif args.command == 'instrument':
        instrument_main(args.udid, args)
    else:
        argparser.print_usage()


if __name__ == "__main__":
    main()