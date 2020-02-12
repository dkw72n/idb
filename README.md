# iOS Debug Bridge 

iOS Debug Bridge (idb) is a versatile command-line tool that lets you communicate with a device.



## Query for devices

```
$ idb devices
List of devices attached
97006ebdc8bc5daed2e354f4addae4fd2a81c52d device USB
```


## Get device info

```
$ idb --udid 97006ebdc8bc5daed2e354f4addae4fd2a81c52d deviceinfo
Device info of device(udid: 97006ebdc8bc5daed2e354f4addae4fd2a81c52d)
os_type: iOS
device_name: San's iPhone
device_type: iPhone X
product_type: iPhone10,3
os: 13.3.1(17D50)
cpu_type: Apple A11 Bionic
cpu_arch: Apple A11 Bionic 64-bit
cpu_core_num: 6
cpu_freq: [0, 2390]
gpu_type: Apple A10X Fusion (12-core graphics)
```


## Get Value

```
$ idb --udid 97006ebdc8bc5daed2e354f4addae4fd2a81c52d getvalue
Values of device(udid: 97006ebdc8bc5daed2e354f4addae4fd2a81c52d)
BasebandCertId: 2315222105
BasebandKeyHashInformation: {'AKeyStatus': 2, 'SKeyHash': b'\xbb\xef\xedp,/i\x0f\xb5c\xdbx\xd0\x8e2z\x00\x84\x98\x1d\xbc\x98\x02\xe5i\x13\xa1h\x85F\x05j', 'SKeyStatus': 0}
BasebandSerialNumber: b"'C\xde\x01"
BasebandVersion: 5.30.01
BoardId: 6
BuildVersion: 17D50
CPUArchitecture: arm64
ChipID: 32789
DeviceClass: iPhone
DeviceColor: 1
DeviceName: San's iPhone
DieID: 7157468793159726
HardwareModel: D22AP
HasSiDP: True
PartitionType: GUID_partition_scheme
ProductName: iPhone OS
ProductType: iPhone10,3
ProductVersion: 13.3.1
ProductionSOC: True
ProtocolVersion: 2
SupportedDeviceFamilies: [1]
TelephonyCapability: True
UniqueChipID: 7157468793159726
UniqueDeviceID: 97006ebdc8bc5daed2e354f4addae4fd2a81c52d
WiFiAddress: e4:9a:dc:b4:ba:94
```
