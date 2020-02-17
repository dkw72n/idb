import argparse
import json
import os
import sys

from device_service import DeviceService
from installation_proxy_service import InstallationProxyService
from lockdown_service import LockdownService
from libimobiledevice import IDeviceConnectionType
from instrument_service import instrument_main, setup_parser as setup_instrument_parser
from spring_board_service import SpringBoardService
from image_mounter_service import ImageMounterService


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


def get_app_list(device):
    installation_proxy_service = InstallationProxyService()
    installation_proxy_client = installation_proxy_service.new_client(device)
    user_apps = None
    system_apps = None
    if installation_proxy_client:
        user_apps = installation_proxy_service.browse(installation_proxy_client, "User")
        system_apps = installation_proxy_service.browse(installation_proxy_client, "System")
        installation_proxy_service.free_client(installation_proxy_client)
    return user_apps, system_apps


def print_applications(udid):
    device_service = DeviceService()
    device = device_service.new_device(udid)
    if device is None:
        print("No device attached")
        return

    user_apps, system_apps = get_app_list(device)
    print("List of user applications installed:")
    if user_apps:
        for app in user_apps:
            for key, value in app.items():
                print("%s: %s" % (key, value))
            print("")
        print("")
    if system_apps:
        print("List of system applications installed:")
        for app in system_apps:
            for key, value in app.items():
                print("%s: %s" % (key, value))
            print("")
    device_service.free_device(device)


def print_icon(udid, bundle_id, output):
    device_service = DeviceService()
    device = device_service.new_device(udid)
    if device is None:
        print("No device attached")
        return

    spring_board_service = SpringBoardService()
    spring_board_client = spring_board_service.new_client(device)

    pngdata = spring_board_service.get_icon_pngdata(spring_board_client, bundle_id)
    if pngdata:
        with open(output, "wb") as fp:
            fp.write(pngdata)
        print("Save icon file at %s" % os.path.abspath(output))
    else:
        print("Can not get icon of app(bundleId=%s)" % bundle_id)
    spring_board_service.free_client(spring_board_client)
    device_service.free_device(device)


def print_image_lookup(udid, image_type = None):
    device_service = DeviceService()
    device = device_service.new_device(udid)
    if device is None:
        print("No device attached")
        return

    lockdown_service = LockdownService()
    lockdown_client = lockdown_service.new_client(device)

    product_version, error = lockdown_service.get_value(lockdown_client, key="ProductVersion")
    if error:
        print("Error: %s" % error)
        return
    lockdown_service.free_client(lockdown_client)

    if image_type is None:
        image_type = "Developer"

    image_mounter_service = ImageMounterService()
    image_mounter_client = image_mounter_service.new_client(device)

    image_mounted, error = image_mounter_service.lookup_image(image_mounter_client, image_type, product_version)
    if error:
        print("Error: %s" % error)
    else:
        print("Image mount status: " + ("Yes" if image_mounted else "No"))

    image_mounter_service.hangup(image_mounter_client)
    image_mounter_service.free_client(image_mounter_client)

def print_mount_image(udid, image_type, image_file, image_signature_file):
    device_service = DeviceService()
    device = device_service.new_device(udid)
    if device is None:
        print("No device attached")
        return

    lockdown_service = LockdownService()
    lockdown_client = lockdown_service.new_client(device)

    product_version, error = lockdown_service.get_value(lockdown_client, key="ProductVersion")
    if error:
        print("Error: %s" % error)
        return
    lockdown_service.free_client(lockdown_client)

    if image_type is None:
        image_type = "Developer"

    image_mounter_service = ImageMounterService()
    image_mounter_client = image_mounter_service.new_client(device)

    result = image_mounter_service.upload_image(image_mounter_client, image_type, image_file, image_signature_file)
    if not result:
        print("Error: Can not upload image")
    else:
        image_path = "/private/var/mobile/Media/PublicStaging/staging.dimage"
        result, error = image_mounter_service.mount_image(image_mounter_client, image_type, image_path, image_signature_file)
        if error:
            print("Error: %s" % error)
        else:
            print("Mount result: %s" % str(result))

    image_mounter_service.hangup(image_mounter_client)
    image_mounter_service.free_client(image_mounter_client)

def main():
    argparser = argparse.ArgumentParser()
    # argparser.add_argument("command", help="command", choices=["devices", "deviceinfo", "devicename", "instrument"])
    cmd_parser = argparser.add_subparsers(dest="command")
    cmd_parser.add_parser("devices")
    cmd_parser.add_parser("applications")
    cmd_parser.add_parser("deviceinfo")
    # imagemounter
    lookupimage_parser = cmd_parser.add_parser("lookupimage")
    lookupimage_parser.add_argument("-t", "--image_type", required=False)
    # imagemounter
    mountimage_parser = cmd_parser.add_parser("mountimage")
    mountimage_parser.add_argument("-t", "--image_type", required=False)
    mountimage_parser.add_argument("-i", "--image_file", required=False)
    mountimage_parser.add_argument("-s", "--sig_file", required=False)
    # geticon
    geticon_parser = cmd_parser.add_parser("geticon")
    geticon_parser.add_argument("--bundle_id", required=True)
    geticon_parser.add_argument("-o", "--output", required=True)
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
    elif args.command == "lookupimage":
        print_image_lookup(args.udid, args.image_type)
    elif args.command == "mountimage":
        print_mount_image(args.udid, args.image_type, args.image_file, args.sig_file)
    elif args.command == "geticon":
        print_icon(args.udid, args.bundle_id, args.output)
    elif args.command == "getvalue":
        print_get_value(args.udid, args.key)
    elif args.command == 'instrument':
        instrument_main(args.udid, args)
    else:
        argparser.print_usage()


if __name__ == "__main__":
    main()