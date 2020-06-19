import argparse
import json
import os
import io
import sys
import time
import datetime

from afc_service import AfcService
from device_service import DeviceService
from installation_proxy_service import InstallationProxyService
from lockdown_service import LockdownService
from libimobiledevice import IDeviceConnectionType, SbservicesInterfaceOrientation
from instrument_service import instrument_main, setup_parser as setup_instrument_parser
from screenshotr_service import ScreenshotrService
from spring_board_service import SpringBoardService
from image_mounter_service import ImageMounterService
from syslog_relay_service import SyslogRelayService
from lockdown_service import LockdownService

try:
    from PIL import Image
except:
    Image = None

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

device_service = DeviceService()


def _get_device_or_die(udid = None):
    device = None
    if udid is not None:
        device = device_service.new_device(udid)
    else:
        device_list = device_service.get_device_list()
        if len(device_list) > 0:
            device = device_service.new_device(device_list[0]['udid'])
    if device is None:
        print("No device attached")
        exit(-1)
    else:
        return device


def print_devices():
    print("List of devices attached")
    device_list = device_service.get_device_list()
    for device in device_list:
        conn_type = "USB" if device['conn_type'] == IDeviceConnectionType.CONNECTION_USBMUXD else "WIFI"
        print("%s device %s" % (device['udid'], conn_type))


def get_device_info_from_configs(product_type):
    with open(os.path.join(ROOT_DIR, "ios_deviceinfo_new.json")) as fp:
        device_info_map = json.load(fp)
        if product_type in device_info_map:
            return device_info_map[product_type]
    return None


def get_device_info(udid):
    device = _get_device_or_die(udid)

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

    lockdown_service.free_client(lockdown_client)
    device_service.free_device(device)

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
    device = _get_device_or_die(udid)

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
    device = _get_device_or_die(udid)

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
    device = _get_device_or_die(udid)

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


def enable_Wireless(udid,enable = 1):
    device = _get_device_or_die(udid)
    lockdown_service = LockdownService()
    client = lockdown_service.new_client(device)
    lockdown_service.enable_wireless(client,int(enable),"","")
    lockdown_service.free_client(client)

def orientation_to_str(orientation):
    if orientation == SbservicesInterfaceOrientation.SBSERVICES_INTERFACE_ORIENTATION_PORTRAIT_UPSIDE_DOWN:
        return "PORTRAIT_UPSIDE_DOWN"
    elif orientation == SbservicesInterfaceOrientation.SBSERVICES_INTERFACE_ORIENTATION_LANDSCAPE_LEFT:
        return "LANDSCAPE_LEFT"
    elif orientation == SbservicesInterfaceOrientation.SBSERVICES_INTERFACE_ORIENTATION_LANDSCAPE_RIGHT:
        return "LANDSCAPE_RIGHT"
    elif orientation == SbservicesInterfaceOrientation.SBSERVICES_INTERFACE_ORIENTATION_PORTRAIT:
        return "PORTRAIT"
    else:
        return "UNKNOWN"

def rotate_image(data, orientation):
    if Image is None:
        print("[WARNING] PIL is not installed, can not auto rotate image, orientation=%s!" % orientation_to_str(orientation))
        return data

    bytes_io = io.BytesIO(data)
    image = Image.open(bytes_io)
    #print("image size=%s orientation=%s" % (str(image.size), str(orientation)))

    if orientation == SbservicesInterfaceOrientation.SBSERVICES_INTERFACE_ORIENTATION_PORTRAIT_UPSIDE_DOWN:
        image = image.transpose(Image.ROTATE_180)
    elif orientation == SbservicesInterfaceOrientation.SBSERVICES_INTERFACE_ORIENTATION_LANDSCAPE_LEFT:
        image = image.transpose(Image.ROTATE_270)
    elif orientation == SbservicesInterfaceOrientation.SBSERVICES_INTERFACE_ORIENTATION_LANDSCAPE_RIGHT:
        image = image.transpose(Image.ROTATE_90)
    else:
        image = image # portrait, do nothing
    bytes_io = io.BytesIO()
    image.save(bytes_io, format="PNG")
    return bytes_io.getvalue()

def print_screenshot(udid, output = None):
    device = _get_device_or_die(udid)

    # get orientation of device
    spring_board_service = SpringBoardService()
    spring_board_client = spring_board_service.new_client(device)
    orientation = spring_board_service.get_interface_orientation(spring_board_client)
    spring_board_service.free_client(spring_board_client)

    # take screenshot
    screenshotr_service = ScreenshotrService()
    screenshotr_client = screenshotr_service.new_client(device)
    imgdata, file_ext = screenshotr_service.take_screenshot(screenshotr_client)
    if imgdata:
        if output is None:
            output = os.path.join(ROOT_DIR, "screenshot_%s%s" % (datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), file_ext))
        imgdata = rotate_image(imgdata, orientation)
        with open(output, "wb") as fp:
            fp.write(imgdata)
        print("Save screenshot image file at %s(orientation: %s)" % (os.path.abspath(output), orientation_to_str(orientation)))
    else:
        print("Error: Can not take screenshot")
    screenshotr_service.free_client(screenshotr_client)

    device_service.free_device(device)

def print_image_lookup(udid, image_type = None):
    device = _get_device_or_die(udid)

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
    device = _get_device_or_die(udid)

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
    device_service.free_device(device)


line = ""
def print_syslog(udid = None):
    device = _get_device_or_die(udid)

    syslog_relay_service = SyslogRelayService()
    syslog_relay_client = syslog_relay_service.new_client(device)
    def callback(char_data, user_data):
        global line
        if char_data == b"\n":
            print(line)
            line = ""
        else:
            line += char_data.decode("utf-8")

    result = syslog_relay_service.start_capture(syslog_relay_client, callback)
    if result:
        print("System log:(pressing Ctrl+C to exit)")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass

    syslog_relay_service.free_client(syslog_relay_client)
    device_service.free_device(device)


def print_list(udid, device_directory = "."):
    device = _get_device_or_die(udid)

    afc_service = AfcService()
    afc_client = afc_service.new_client(device)
    file_list = afc_service.read_directory(afc_client, device_directory)
    print("List of directory %s:" % device_directory)
    if file_list:
        for file in file_list:
            print(file['filename'], end=" ")

    afc_service.free_client(afc_client)
    device_service.free_device(device)


def pull_file(udid, remote_file): # TODO: pull directory
    device = _get_device_or_die(udid)

    afc_service = AfcService()
    afc_client = afc_service.new_client(device)

    afc_file = afc_service.open_file(afc_client, remote_file, "r")
    output_file = os.path.join(ROOT_DIR, os.path.basename(remote_file))
    output = open(output_file, "wb")
    while True:
        buffer = afc_file.read(1024)
        output.write(buffer)
        if not buffer:
            break
    output.close()
    afc_file.close()
    afc_service.free_client(afc_client)
    device_service.free_device(device)
    print("pull file %s" % output_file)


def push_file(udid, local_file, device_directory):
    if not os.path.exists(local_file):
        print("Error: %s is not exists" % local_file)
        return

    device = _get_device_or_die(udid)

    afc_service = AfcService()
    afc_client = afc_service.new_client(device)

    success = afc_service.make_directory(afc_client, device_directory) # TODO: check
    remote_file = device_directory + "/" + os.path.basename(local_file)
    afc_file = afc_service.open_file(afc_client, remote_file, "w")
    input_file = open(local_file, "rb")
    while True:
        buffer = input_file.read(1024)
        if not buffer:
            break
        afc_file.write(buffer)
    input_file.close()
    afc_file.close()
    afc_service.free_client(afc_client)
    device_service.free_device(device)
    print("push file %s to %s" % (local_file, remote_file))


def make_directory(udid, device_directory):
    device = _get_device_or_die(udid)

    afc_service = AfcService()
    afc_client = afc_service.new_client(device)

    result = afc_service.make_directory(afc_client, device_directory)
    print("Make directory %s %s" % (device_directory, "Success" if result else "Fail"))

    afc_service.free_client(afc_client)
    device_service.free_device(device)


def remove_path(udid, device_path):
    device = _get_device_or_die(udid)

    afc_service = AfcService()
    afc_client = afc_service.new_client(device)

    result = False
    error = None
    try:
        result = afc_service.remove_path(afc_client, device_path)
    except IOError as e:
        error = e

    if result:
        print("%s Deleted." % device_path)
    else:
        print("Error: %s" % error)

    afc_service.free_client(afc_client)
    device_service.free_device(device)

def install_ipa(udid, ipa_path):

    device = _get_device_or_die(udid)
    installation_proxy_service = InstallationProxyService()
    client = installation_proxy_service.new_client(device)
    print("start install")
    apps = installation_proxy_service.install(device, client, ipa_path)
    print("finsih install")
    installation_proxy_service.free_client(client)
        
def uninstall_ipa(udid, bundle_id):
    device = _get_device_or_die(udid)
    installation_proxy_service = InstallationProxyService()
    client = installation_proxy_service.new_client(device)
    print("start install")
    apps = installation_proxy_service.uninstall(device, client, bundle_id)
    print("finsih install")
    installation_proxy_service.free_client(client)

def start_heartbeat(udid):
    DeviceService.start_heartbeat(udid)

def main():
    argparser = argparse.ArgumentParser()
    # argparser.add_argument("command", help="command", choices=["devices", "deviceinfo", "devicename", "instrument"])
    cmd_parser = argparser.add_subparsers(dest="command")
    cmd_parser.add_parser("devices")
    cmd_parser.add_parser("applications")
    cmd_parser.add_parser("deviceinfo")
    cmd_parser.add_parser("syslog")


    # list
    list_parser = cmd_parser.add_parser("ls")
    list_parser.add_argument("device_directory")
    # mkdir
    list_parser = cmd_parser.add_parser("mkdir")
    list_parser.add_argument("device_directory")
    # rm
    list_parser = cmd_parser.add_parser("rm")
    list_parser.add_argument("device_path")
    # pull file
    pull_parser = cmd_parser.add_parser("pull")
    pull_parser.add_argument("remote_file")
    # push file
    push_parser = cmd_parser.add_parser("push")
    push_parser.add_argument("local_file")
    push_parser.add_argument("device_directory")
    # imagemounter
    lookupimage_parser = cmd_parser.add_parser("lookupimage")
    lookupimage_parser.add_argument("-t", "--image_type", required=False)
    # imagemounter
    mountimage_parser = cmd_parser.add_parser("mountimage")
    mountimage_parser.add_argument("-t", "--image_type", required=False)
    mountimage_parser.add_argument("-i", "--image_file", required=False)
    mountimage_parser.add_argument("-s", "--sig_file", required=False)
    # screenshot
    screenshot_parser = cmd_parser.add_parser("screenshot")
    screenshot_parser.add_argument("-o", "--output", required=False)
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

    cmd_wireless = cmd_parser.add_parser("enableWireless")
    cmd_wireless.add_argument("-e", "--enable", required=False)

    cmd_parser.add_parser("heartbeat")

    argparser.add_argument("-u", "--udid", help="udid")

    ## install
    install_parser = cmd_parser.add_parser("install")
    install_parser.add_argument("ipa_path")

    ## uninstall
    uninstall_parser = cmd_parser.add_parser("uninstall")
    uninstall_parser.add_argument("bundle_id")

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
    elif args.command == "syslog":
        print_syslog(args.udid)
    elif args.command == "screenshot":
        print_screenshot(args.udid, args.output)
    elif args.command == "getvalue":
        print_get_value(args.udid, args.key)
    elif args.command == 'instrument':
        instrument_main(_get_device_or_die(args.udid), args)
    elif args.command == 'ls':
        print_list(args.udid, args.device_directory)
    elif args.command == 'mkdir':
        make_directory(args.udid, args.device_directory)
    elif args.command == 'rm':
        remove_path(args.udid, args.device_path)
    elif args.command == 'pull':
        pull_file(args.udid, args.remote_file)
    elif args.command == 'push':
        push_file(args.udid, args.local_file, args.device_directory)
    elif args.command == 'enableWireless':
        enable_Wireless(args.udid, args.enable)
    elif args.command == 'install':
        install_ipa(args.udid, args.ipa_path)
    elif args.command == 'uninstall':
        uninstall_ipa(args.udid, args.bundle_id)
    elif args.command == 'heartbeat':
        start_heartbeat(args.udid)
    else:
        argparser.print_usage()


if __name__ == "__main__":
    main()