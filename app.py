import argparse

from device_service import DeviceService
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

def print_device_info(udid, key=None):
    device_service = DeviceService()
    device = device_service.new_device(udid)

    lockdown_service = LockdownService()
    lockdown_client = lockdown_service.new_client(device)

    values = lockdown_service.get_value(lockdown_client, key=key)
    print("Device Info of udid: %s" % udid)
    if type(values) == dict:
        for name, value in values.items():
            print("%s: %s" % (name, value))
    else:
        print("%s: %s" % (key, values))
    lockdown_service.free_client(lockdown_client)
    device_service.free_device(device)

def main():
    argparser = argparse.ArgumentParser()
    # argparser.add_argument("command", help="command", choices=["devices", "deviceinfo", "devicename", "instrument"])
    cmd_parser = argparser.add_subparsers(dest="command")
    cmd_parser.add_parser("devices")
    cmd_parser.add_parser("deviceinfo")
    cmd_parser.add_parser("devicename")
    instrument_parser = cmd_parser.add_parser("instrument")
    setup_instrument_parser(instrument_parser)
    
    argparser.add_argument("-u", "--udid", help="udid")

    args = argparser.parse_args()
    if args.command == "devices":
        print_devices()
    elif args.command == "deviceinfo":
        print_device_info(args.udid)
    elif args.command == "devicename":
        print_device_info(args.udid, "DeviceName")
    elif args.command == 'instrument':
        instrument_main(args.udid, args)
    else:
        argparser.print_usage()


if __name__ == "__main__":
    main()