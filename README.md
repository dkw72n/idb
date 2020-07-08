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

## Instrument

### channels

```
$ idb instrument channels
Published capabilities:
com.apple.instruments.server.services.processcontrolbydictionary 4
```

### graphics

```
$ idb instrument graphics
[GRAPHICS] 
{
    'stdTextureCreationBytes': 0,
    'XRVideoCardRunTimeStamp': 4129783,           // timestamp(us)
    'SplitSceneCount': 0,
    'Device Utilization %': 0,                    // GPU Usage - Device
    'finishGLWaitTime': 0,
    'recoveryCount': 0,
    'gartUsedBytes': 45383680,
    'gartMapInBytesPerSample': 0,
    'IOGLBundleName': 'Built-In',
    'CoreAnimationFramesPerSecond': 58,          // FPS - fps
    'freeToAllocGPUAddressWaitTime': 0,
    'TiledSceneBytes': 118784,
    'Renderer Utilization %': 0,                // GPU Usage - Render
    'Tiler Utilization %': 0,                   // GPU Usage - Tiler
    'oolTextureCreationBytes': 0,
    'gartMapOutBytesPerSample': 1998848,
    'contextGLCount': 0,
    'agpTextureCreationBytes': 0,
    'CommandBufferRenderCount': 31,
    'iosurfaceTextureCreationBytes': 0,
    'textureCount': 976,
    'hardwareWaitTime': 0,
    'agprefTextureCreationBytes': 0
}
```

### sysmontap

```
$ idb instrument sysmontap
[{
    'Processes': {
        0: [55934222336, None, 165363256, 69663420, 192643072, 1206386688, 335527936, 0, None, 2096201728],
        144: [4365975552, None, 8395, 301, 2458024, 1900544, 2310144, 144, None, 17207296],
        49: [4393910272, None, 105903, 30000, 3998160, 2375680, 3833856, 49, None, 47230976],
        3018: [4325965824, None, 113, 2, 966960, 655360, 868352, 3018, None, 966656],
        98: [4395515904, None, 211910, 55, 3293608, 4177920, 3145728, 98, None, 494104576],
        2972: [4741709824, None, 2849, 34, 23528288, 14057472, 23248896, 2972, None, 155648],
        52: [4342824960, None, 283782, 29356, 1704360, 1687552, 1556480, 52, None, 5021696],
        2494: [4361601024, None, 421, 18, 1311144, 475136, 1146880, 2494, None, 237568],
    },
    'Type': 7,
    'EndMachAbsTime': 3595494138985,
    'ProcessesAttributes': ['memVirtualSize', 'cpuUsage', 'ctxSwitch', 'intWakeups', 'physFootprint', 'memResidentSize', 'memAnon', 'pid', 'powerScore', 'diskBytesRead'],
    'StartMachAbsTime': 3595491365204
}]

[{
    'PerCPUUsage': [{
        'CPU_NiceLoad': 0.0,
        'CPU_SystemLoad': -1.0,
        'CPU_TotalLoad': 6.930693069306926,
        'CPU_UserLoad': -1.0
    }, {
        'CPU_NiceLoad': 0.0,
        'CPU_SystemLoad': -1.0,
        'CPU_TotalLoad': 0.9900990099009874,
        'CPU_UserLoad': -1.0
    }, {
        'CPU_NiceLoad': 0.0,
        'CPU_SystemLoad': -1.0,
        'CPU_TotalLoad': 0.0,
        'CPU_UserLoad': -1.0
    }, {
        'CPU_NiceLoad': 0.0,
        'CPU_SystemLoad': -1.0,
        'CPU_TotalLoad': 0.0,
        'CPU_UserLoad': -1.0
    }, {
        'CPU_NiceLoad': 0.0,
        'CPU_SystemLoad': -1.0,
        'CPU_TotalLoad': 1.0,
        'CPU_UserLoad': -1.0
    }, {
        'CPU_NiceLoad': 0.0,
        'CPU_SystemLoad': -1.0,
        'CPU_TotalLoad': 8.0,
        'CPU_UserLoad': -1.0
    }],
    'EndMachAbsTime': 3595515481450,
    'CPUCount': 6,
    'EnabledCPUs': 6,
    'SystemCPUUsage': {
        'CPU_NiceLoad': 0.0,
        'CPU_SystemLoad': -1.0,
        'CPU_TotalLoad': 16.920792079207914,         // CPU - Total Usage = SystemCPUUsage.CPU_TotalLoad / EnabledCPUs
        'CPU_UserLoad': -1.0
    },
    'Type': 33,
    'StartMachAbsTime': 3595491365204
}, {
    'Processes': {
        0: [55934222336, 0.02943223109141613, 165363748, 69663619, 192643072, 1206353920, 335495168, 0, None, 2096201728],  // 'ProcessesAttributes': ['memVirtualSize', 'cpuUsage', 'ctxSwitch', 'intWakeups', 'physFootprint', 'memResidentSize', 'memAnon', 'pid', 'powerScore', 'diskBytesRead'],
        144: [4365975552, 0.0, 8395, 301, 2458024, 1900544, 2310144, 144, 0.0, 17207296],
        49: [4393910272, 0.0, 105903, 30000, 3998160, 2375680, 3833856, 49, 0.0, 47230976],
        3018: [4325965824, 0.0, 113, 2, 966960, 655360, 868352, 3018, 0.0, 966656],
        98: [4395515904, 0.0055491588698022894, 211914, 55, 3293608, 4177920, 3145728, 98, 0.23121495260104377, 494104576],
        2972: [4741709824, 0.0, 2849, 34, 23528288, 14057472, 23248896, 2972, 0.0, 155648],
        52: [4342824960, 0.0, 283782, 29356, 1704360, 1687552, 1556480, 52, 0.0, 5021696],
        2494: [4361601024, 0.0, 421, 18, 1311144, 475136, 1146880, 2494, 0.0, 237568],
    },
    'Type': 5,
    'EndMachAbsTime': 3595520484394,
    'StartMachAbsTime': 3595494138986
}]
```


```
enabledCPUs = data.EnabledCPUs
if enabledCPUs == 0:
    enabledCPUs = data.CPUCount
totalCPUUsage = data.SystemCPUUsage.CPU_TottatlLoad / enabledCPUs




```


### activity(IOS < 11.0)


```
$ idb instrument activity
{
   "CPUNiceLoad":0.0,
   "NetBytesIn":19742719,
   "DiskBytesWritten":134885376,
   "VMPageInBytes":789274624,
   "TotalThreads":507,
   "TotalVMSize":102345474048,
   "PhysicalMemoryActive":392609792,
   "DiskWriteOpsPerSecond":0,
   "DiskWriteOps":6297,
   "NetBytesInPerSecond":0,
   "PhysicalMemoryUsed":786100224,
   "DiskReadOpsPerSecond":0,
   "DiskBytesReadPerSecond":0,
   "NetBytesOut":18399168,
   "PhysicalMemoryFree":28282880,
   "CPUUserLoad":65.90909004211426,
   "XRActivityClientMachAbsoluteTime":14443144570,                  // absTime
   "DiskBytesWrittenPerSecond":0,
   "NetPacketsOut":4527,
   "DiskBytesRead":782565376,
   "PhysicalMemoryWired":189034496,
   "NetPacketsIn":8936,
   "TotalProcesses":0,
   "IndividualCPULoad":[
      {
         "TotalLoad":"63.636364",
         "SystemLoad":"0.000000",
         "NiceLoad":"0.000000",
         "UserLoad":"63.636364"
      },
      {
         "TotalLoad":"68.181818",
         "SystemLoad":"0.000000",
         "NiceLoad":"0.000000",
         "UserLoad":"68.181818"
      }
   ],
   "CPUTotalLoad":65.90909004211426,
   "Processes":[
      {
         "CPUUsage":0.21836340937464532,                // cpuUsage;  appCPUUsage = cpuUsage / cpuNum; totalCPUUsage = SUM(processCPUUsage)
         "UnixSyscalls":91249,
         "Private":4284416,
         "VPrivate":27578368,
         "Faults":4771,
         "TotalMicroSeconds":895321,
         "MachSyscalls":81338,
         "Ports":1106,
         "MessagesReceived":15268,
         "ContextSwitches":23485,
         "PGID":1,
         "UID":0,
         "Threads":3,
         "TotalSeconds":4,
         "ResidentSize":6176768,                        // realMemory(b)
         "PageIns":823,
         "Architecture":12,
         "PID":1,                                       // pid
         "VirtualSize":664883200,                       // virtualMemory(b)
         "Command":"launchd",
         "PPID":0,
         "MessagesSent":43868,
         "Shared":1126400
      }
   ],
   "PhysicalMemoryInactive":204455936,
   "NetPacketsOutPerSecond":0,
   "VMSwapUsed":0,
   "DiskReadOps":27249,
   "NetBytesOutPerSecond":0,
   "CPUSystemLoad":0.0,
   "NetPacketsInPerSecond":0,
   "VMPageOutBytes":139264
}
```



### networking(Wifi mode)

```
$ idb instrument networking
connection-detected {'LocalAddress': '192.168.31.195:63993', 'RemoteAddress': '17.57.145.102:5223', 'InterfaceIndex': 8, 'Pid': -2, 'RecvBufferSize': 131072, 'RecvBufferUsed': 0, 'SerialNumber': 2, 'Kind': 1}
connection-detected {'LocalAddress': '172.31.57.105:63992', 'RemoteAddress': '17.252.204.141:5223', 'InterfaceIndex': 3, 'Pid': -2, 'RecvBufferSize': 131072, 'RecvBufferUsed': 0, 'SerialNumber': 3, 'Kind': 1}
connection-detected {'LocalAddress': '192.168.31.195:56950', 'RemoteAddress': '17.56.8.133:993', 'InterfaceIndex': 8, 'Pid': -2, 'RecvBufferSize': 131072, 'RecvBufferUsed': 0, 'SerialNumber': 12, 'Kind': 1}
connection-detected {'LocalAddress': '0.0.0.0:59998', 'RemoteAddress': '0.0.0.0:0', 'InterfaceIndex': 8, 'Pid': -2, 'RecvBufferSize': 0, 'RecvBufferUsed': 0, 'SerialNumber': 13, 'Kind': 2}
connection-detected {'LocalAddress': '[::]:59814', 'RemoteAddress': '[::]:0', 'InterfaceIndex': 8, 'Pid': -2, 'RecvBufferSize': 0, 'RecvBufferUsed': 0, 'SerialNumber': 38, 'Kind': 2}
connection-detected {'LocalAddress': '[::]:5353', 'RemoteAddress': '[::]:0', 'InterfaceIndex': 8, 'Pid': -2, 'RecvBufferSize': 196724, 'RecvBufferUsed': 0, 'SerialNumber': 52, 'Kind': 2}
connection-detected {'LocalAddress': '0.0.0.0:5353', 'RemoteAddress': '0.0.0.0:0', 'InterfaceIndex': 8, 'Pid': -2, 'RecvBufferSize': 196724, 'RecvBufferUsed': 0, 'SerialNumber': 53, 'Kind': 2}
interface-detection {'InterfaceIndex': 8, 'Name': 'en0'}
interface-detection {'InterfaceIndex': 3, 'Name': 'pdp_ip0'}
connection-update {
    'RxPackets': 20448,
    'RxBytes': 4242060,             // download
    'TxPackets': 15446,
    'TxBytes': 3144553,             // upload
    'RxDups': None,
    'RxOOO': None,
    'TxRetx': None,
    'MinRTT': None,
    'AvgRTT': None,
    'ConnectionSerial': 53
}
```


### netstat(USB mode)

```
idb instrument netstat 2468
start {2468.0}
{
    2468.0: {
        'net.packets.delta': 0,
        'time': 1582189905.198155,
        'net.tx.bytes': 56636,      // upload
        'net.bytes.delta': 0,
        'net.rx.packets.delta': 0,
        'net.tx.packets': 303,
        'net.rx.bytes': 293823,     // download
        'net.bytes': 350459,
        'net.tx.bytes.delta': 0,
        'net.rx.bytes.delta': 0,
        'net.rx.packets': 416,
        'pid': 2468.0,
        'net.tx.packets.delta': 0,
        'net.packets': 719
    }
}
```


### energy

```
$ idb instrument energy 2468
{
    2230.0: {
        'energy.overhead': 490.0,                    // Energy - overheadEnergy
        'kIDEGaugeSecondsSinceInitialQueryKey': 11,
        'energy.version': 1,
        'energy.gpu.cost': 0,                       // Energy - gpuEnergy
        'energy.cpu.cost': 35.94272039376739,       // Energy - cpuEnergy
        'energy.networkning.overhead': 500,
        'energy.appstate.cost': 8,
        'energy.location.overhead': 0,
        'energy.thermalstate.cost': 0,
        'energy.networking.cost': 0,                // Energy - networkEnergy
        'energy.cost': 25.942720393767388,
        'energy.cpu.overhead': 0,
        'energy.location.cost': 0,                  // Energy - locationEnergy
        'energy.gpu.overhead': 0,
        'energy.appstate.overhead': 0,
        'energy.inducedthermalstate.cost': -1
    }
}
```

productVersion >= 11.0:
* energy.cpu.cost: cpuEnergy
* energy.gpu.cost: gpuEnergy
* energy.networking.cost: networkEnergy
* energy.location.cost: locationEnergy
* energy.display.cost: displayEnergy
* energy.overhead: overheadEnergy

productVersion < 11.0:
* energy.CPU: cpuEnergy
* energy.GPU: gpuEnergy
* energy.networking: networkEnergy
* energy.location: locationEnergy
* energy.overhead: overheadEnergy


## System log

```
$ idb syslog
System log:(pressing Ctrl+C to exit)
Feb 18 16:44:35 Sans-iPhone homed(HomeKitDaemon)[104] <Notice>: Remote access health monitor timer fired, checking state for all homes
Feb 18 16:44:36 Sans-iPhone symptomsd(SymptomEvaluator)[117] <Notice>: NBSM: TCP metrics iteration:691 since 30.00 secs, ret=1: allflows=5/C=0/R=0/W=1/flows=0/unacked=0/rxbytes=0/txbytes=0/rxooo=0/rxdup=0/retx=0
Feb 18 16:44:36 Sans-iPhone symptomsd(SymptomEvaluator)[117] <Notice>: NBSM: TCP progress metrics score: 20, problem ratio: 0.20 (baseline: 0.08)
Feb 18 16:44:36 Sans-iPhone CommCenter(libATCommandStudioDynamic.dylib)[81] <Notice>: QMI: Svc=0xe2(BSP) Ind MsgId=0xe021 Bin=[<private>]
Feb 18 16:44:37 Sans-iPhone wifid(WiFiPolicy)[45] <Notice>: __WiFiLQAMgrLogStats(helloworld:Stationary): Rssi: -65 {0 0} Snr: 0 Cca: 41 (S:0 O:3
```


## List directory

```
$ idb ls /
Downloads Books Photos Recordings DCIM iTunesRestore iTunes_Control MediaAnalysis PhotoData PublicStaging Purchases 

$ idb ls /  --bundle="com.seasun.tmgp.jx3m" (optional )-d = 1
List of directory /Documents//:
whalesdk-cs debug3.json .DS_Store MSDKINFO.sqlite ss_tmp xgserialization.b 

```

## Make directory

```
$ idb mkdir /Temp
Make directory /Temp Success

$ idb mkdir /Temp --bundle="com.seasun.tmgp.jx3m" -d = 1
Make directory /Temp Success

```

## Delete file or directory 

```
$ idb rm /Temp
/Temp Deleted.

$ idb rm /Temp --bundle="com.seasun.tmgp.jx3m" -d = 1
/Temp Deleted.

```

## Push file into device

```
$ idb push test.txt /Temp
push file test.txt to /Temp

$ idb push test.txt /Temp  --bundle="com.seasun.tmgp.jx3m" -d = 1
push file test.txt to /Temp

```


## Pull file from device

```
$ idb pull /Temp/test.txt
pull file F:\lds\project\idb\test.txt

$ idb pull /Temp/test.txt  --bundle="com.seasun.tmgp.jx3m" -d = 1
pull file F:\lds\project\idb\test.txt

```

## Install ipa into device

```
$ idb install ~/tmp.ipa

```

## Uninstall ipa into device

```
$ idb uninstall com.seasun.jxpocket.tako

```

## launch app with bundle id
```
$ idb instrument launch com.ksg.tako
``` 

## wireless mode

```
$ idb -u 97006ebdc8bc5daed2e354f4addae4fd2a81c52d:10.11.255.115 heartbeat
``` 

```
$ idb -u 97006ebdc8bc5daed2e354f4addae4fd2a81c52d:10.11.255.115 deviceinfo
``` 


## diagnostics

iOS >= 13.0 
```
$ idb diagnostics AppleSmartBattery
```

iOS < 13.0 
```
$ idb diagnostics AppleARMPMUCharger
```
