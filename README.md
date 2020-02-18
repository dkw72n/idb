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
$ idb getvalue
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


## Query for applications


```
$ idb applications
List of user applications installed:
CFBundleExecutable: JD4iPhone
CFBundleVersion: 8.4.6
CFBundleShortVersionString: 167053
CFBundleIdentifier: com.360buy.jdmobile
Path: /private/var/containers/Bundle/Application/AB511C13-DD00-4B44-AD23-253C164D9215/JD4iPhone.app
CFBundleName: 京东

List of system applications installed:
CFBundleExecutable: Contacts
CFBundleVersion: 1.0
CFBundleShortVersionString: 1.0
CFBundleIdentifier: com.apple.MobileAddressBook
Path: /private/var/containers/Bundle/Application/7FF5041A-225B-462C-9FF1-16D0A6AC571B/Contacts.app
CFBundleName: 通讯录
```

## Get Application's icon


```
$ idb geticon --bundle_id com.apple.Preferences --output icon.png
Save icon file at F:\lds\project\idb\icon.png
```


## Lookup image


```
$ idb lookupimage --image_type Developer
Image mount status: Yes
```

## Mount image

```
$ idb mountimage --image_file F:\lds\DeviceSupport\DeviceSupport\13.3\DeveloperDiskImage.dmg --sig_file F:\lds\DeviceSupport\DeviceSupport\13.3\DeveloperDiskImage.dmg.signature
Mount result: True
```


## Take screenshot

```
$ idb screenshot
Save screenshot image file at F:\lds\project\idb\screenshot_20200218_112501.png
```


## Query Running Processes

```
$ idb instrument running
runningProcesses:
isApplication	name	pid	realAppName	startDate
False	filecoordinationd	144	/usr/sbin/filecoordinationd	bpylist.timestamp datetime.datetime(2020, 2, 17, 15, 12, 42, 829858, tzinfo=datetime.timezone.utc)```
```

## Instrument channels

```
$ idb instrument channels
Published capabilities:
com.apple.instruments.server.services.processcontrolbydictionary 4
```

## System log

```
$ idb syslog
System log:
Feb 18 16:44:35 Sans-iPhone homed(HomeKitDaemon)[104] <Notice>: Remote access health monitor timer fired, checking state for all homes
Feb 18 16:44:36 Sans-iPhone symptomsd(SymptomEvaluator)[117] <Notice>: NBSM: TCP metrics iteration:691 since 30.00 secs, ret=1: allflows=5/C=0/R=0/W=1/flows=0/unacked=0/rxbytes=0/txbytes=0/rxooo=0/rxdup=0/retx=0
Feb 18 16:44:36 Sans-iPhone symptomsd(SymptomEvaluator)[117] <Notice>: NBSM: TCP progress metrics score: 20, problem ratio: 0.20 (baseline: 0.08)
Feb 18 16:44:36 Sans-iPhone CommCenter(libATCommandStudioDynamic.dylib)[81] <Notice>: QMI: Svc=0xe2(BSP) Ind MsgId=0xe021 Bin=[<private>]
Feb 18 16:44:37 Sans-iPhone wifid(WiFiPolicy)[45] <Notice>: __WiFiLQAMgrLogStats(helloworld:Stationary): Rssi: -65 {0 0} Snr: 0 Cca: 41 (S:0 O:3
```