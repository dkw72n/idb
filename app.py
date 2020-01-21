import argparse

from device_service import DeviceService
from libimobiledevice import IDeviceConnectionType

def print_devices():
    print("List of devices attached")
    device_service = DeviceService()
    device_list = device_service.get_device_list()
    for device in device_list:
        conn_type = "USB" if device['conn_type'] == IDeviceConnectionType.CONNECTION_USBMUXD else "WIFI"
        print("%s device %s" % (device['udid'], conn_type))

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("command", help="command")

    args = argparser.parse_args()
    if args.command == "devices":
        print_devices()


if __name__ == "__main__":
    main()