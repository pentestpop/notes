---
layout: default
title: "Windows Forensics"
parent: "SOC"
grand_parent: "Defensive Security"
nav_order: 13
---

# An Introduction
Tools: 
- Eric Zimmermans tools
- KAPE - Kroll Artifact Parser and Extractor 
	- automates the collection and parsing of forensic artifacts and can help create a timeline of events.
- Autopsy - an open-source forensics platform that helps analyze data from digital media like mobile devices, hard drives, and removable drives.
- Volatility - a tool that helps perform memory analysis for memory captures from both Windows and Linux Operating Systems.
- Redline - an incident response tool developed and freely distributed by FireEye. 
- Velociraptor - an advanced endpoint-monitoring, forensics, and response platform. It is open-source but very powerful.

## Process
NIST SP-800-61 Incident Handling guide steps:
1. Preparation
2. Detection and Analysis
3. Containment, Eradication, and Recovery
4. Post-incident Activity

SANS Incident Handler's handbook steps (**PICERL**):
1. Preparation
2. Identification
3. Containment
4. Eradication
5. Recovery
6. Lessons Learned

# Windows Forensics 1
The Windows Registry is a collection of databases that contains the system's configuration data. This configuration data can be about the hardware, the software, or the user's information. It also includes data about the recently used files, programs used, or devices connected to the system. You can view the registry using `regedit.exe`, a built-in Windows utility to view and edit the registry.

If you only have access to a disk image, you must know where the registry hives are located on the disk. The majority of these hives are located in the `C:\Windows\System32\Config` directory and are:

1. **DEFAULT** (mounted on `HKEY_USERS\DEFAULT`)
2. **SAM** (mounted on `HKEY_LOCAL_MACHINE\SAM`)
3. **SECURITY** (mounted on `HKEY_LOCAL_MACHINE\Security`)
4. **SOFTWARE** (mounted on `HKEY_LOCAL_MACHINE\Software`)
5. **SYSTEM** (mounted on `HKEY_LOCAL_MACHINE\System`)

For Windows 7 and above, a user’s profile directory is located in `C:\Users\<username>\` where the 9HIDDEN) hives are:

1. **NTUSER.DAT** (mounted on HKEY_CURRENT_USER when a user logs in)
	1. located in the directory `C:\Users\<username>\`.
2. **USRCLASS.DAT** (mounted on HKEY_CURRENT_USER\Software\CLASSES)
	1. located in the directory `C:\Users\<username>\AppData\Local\Microsoft\Windows`

There is another very important hive called the **AmCache hive**. This hive is located in `C:\Windows\AppCompat\Programs\Amcache.hve`. Windows creates this hive to save information on programs that were recently run on the system.

The **transaction log** for each hive is stored as a `.LOG` file in the same directory as the hive itself. 

**Registry backups** are the opposite of Transaction logs. These are the backups of the registry hives located in the `C:\Windows\System32\Config` directory. These hives are copied to the `C:\Windows\System32\Config\RegBack` directory *every ten days*.

## Data Acquisition
Tools: 
- [KAPE](https://www.kroll.com/en/services/cyber-risk/incident-response-litigation-support/kroll-artifact-parser-extractor-kape) is a live data acquisition and analysis tool which can be used to acquire registry data. It is primarily a command-line tool but also comes with a GUI.
- [Autopsy](https://www.autopsy.com/) gives you the option to acquire data from both live systems or from a disk image.
- [FTK Imager](https://www.exterro.com/ftk-imager) is similar to Autopsy

## Exploring Windows Registry
Tools:
- [AccessData's Registry Viewer](https://accessdata.com/product-download/registry-viewer-2-0-0) has a similar user interface to the Windows Registry Editor
- Eric Zimmerman's [Registry Explorer](https://ericzimmerman.github.io/#!index.md)
- [RegRipper](https://github.com/keydet89/RegRipper3.0) is a utility that takes a registry hive as input and outputs a report that extracts data from some of the forensically important keys and values in that hive.

## System Information and System Accounts
- OS Version
	- To find the OS version, we can use the following registry key:`SOFTWARE\Microsoft\Windows NT\CurrentVersion`

- The hives containing the machine’s configuration data used for controlling system startup are called *Control Sets*. Commonly, we will see two Control Sets in the `SYSTEM` hive on a machine. In most cases, ControlSet001 will point to the Control Set that the machine booted with, and ControlSet002 will be the `last known good` configuration. Their locations will be:`SYSTEM\ControlSet001` and `SYSTEM\ControlSet002`

- Computer Name: `SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName`

- Time Zone: 
`SYSTEM\CurrentControlSet\Control\TimeZoneInformation`

- Network Interfaces: `SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces`
	- The past networks a given machine was connected to can be found in the following locations:
		- `SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged`
		- `SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Managed`

- Autostart Programs - The following registry keys include information about programs or commands that run when a user logs on. 
	- `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Run`
	- `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\RunOnce`
	- `SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce`
	- `SOFTWARE\Microsoft\Windows\CurrentVersion\policies\Explorer\Run`
	- `SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
	  
- SAM Hive and User Information: `SAM\Domains\Account\Users`

- Recently open files: `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs`

- Microsoft Office Specific Recently Opened Documents:
`NTUSER.DAT\Software\Microsoft\Office\VERSION`

- ShellBags - When any user opens a folder, it opens in a specific layout. Users can change this layout according to their preferences. These layouts can be different for different folders. We can find this info here:
	- `USRCLASS.DAT\Local Settings\Software\Microsoft\Windows\Shell\Bags`
	- `USRCLASS.DAT\Local Settings\Software\Microsoft\Windows\Shell\BagMRU`
	- `NTUSER.DAT\Software\Microsoft\Windows\Shell\BagMRU`
	- `NTUSER.DAT\Software\Microsoft\Windows\Shell\Bags`

- Open/Save and LastVisited Dialog MRUs - When we open or save a file, a dialog box appears asking us where to save or open that file from. It might be noticed that once we open/save a file at a specific location, Windows remembers that location. This implies that we can find out recently used files if we get our hands on this information. We can do so by examining the following registry keys:
	- `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePIDlMRU`
	- `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU`

- Windows Explorer Address/Search Bars:
	- `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths`
	- `NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery`

- UserAssist - Windows keeps track of applications launched by the user using Windows Explorer for statistical purposes in the User Assist registry keys.
	- `NTUSER.DAT\Software\Microsoft\Windows\Currentversion\Explorer\UserAssist\{GUID}\Count`

- Shimcache - ShimCache is a mechanism used to keep track of application compatibility with the OS and tracks all applications launched on the machine.
	- It is also called Application Compatibility Cache (AppCompatCache).
	- `SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache`
	- We can use the following command to run the AppCompatCache Parser Utility: `AppCompatCacheParser.exe --csv <path to save output> -f <path to SYSTEM hive for data parsing> -c <control set to parse>`

- AmCache - The AmCache hive is an artifact related to ShimCache. This performs a similar function to ShimCache, and stores additional data related to program executions.
	- `C:\Windows\appcompat\Programs\Amcache.hve`
	- Information about the last executed programs can be found at the following location in the hive: `Amcache.hve\Root\File\{Volume GUID}\`

- BAM/DAM - Background Activity Monitor or BAM keeps a tab on the activity of background applications. Similar Desktop Activity Moderator or DAM is a part of Microsoft Windows that optimizes the power consumption of the device. Both of these are a part of the Modern Standby system in Microsoft Windows.
	- `SYSTEM\CurrentControlSet\Services\bam\UserSettings\{SID}`
	- `SYSTEM\CurrentControlSet\Services\dam\UserSettings\{SID}`

- Device Identification - The following locations keep track of USB keys plugged into a system: 
	- `SYSTEM\CurrentControlSet\Enum\USBSTOR`
	- `SYSTEM\CurrentControlSet\Enum\USB`
	- The following registry checks the last times they were connected/removed:
		- `SYSTEM\CurrentControlSet\Enum\USBSTOR\Ven_Prod_Version\USBSerial#\Properties\{83da6326-97a6-4088-9453-a19231573b29}\####`
			- Where ####: 
				- 0064 for first connection time
				- 0066 for last connection time
				- 0067 for last removal time
- USB Device Volume Name: 
	- `SOFTWARE\Microsoft\Windows Portable Devices\Devices`


# Windows Forensics 2
## FAT file systems
FAT - File Allocation Table
- was the default filesystem for Microsoft (**NTFS** now)
- The **exFAT** file system is now the default for SD cards larger than 32GB
- Supports these data structures: 
	- A **cluster** is a basic storage unit of the FAT file system. Each file stored on a storage device can be considered a group of clusters containing bits of information.
	- A **directory** contains information about file identification, like file name, starting cluster, and filename length.
	- The **File Allocation Table** is a linked list of all the clusters. It contains the status of the cluster and the pointer to the next cluster in the chain.

| **Attribute**                  | **FAT12**  | **FAT16**  | **FAT32**   | **exFAT**   |
| ------------------------------ | ---------- | ---------- | ----------- | ----------- |
| **Addressable bits**           | 12         | 16         | 28          |             |
| **Max number of clusters**     | 4,096      | 65,536     | 268,435,456 |             |
| **Supported size of clusters** | 512B - 8KB | 2KB - 32KB | 4KB - 32KB  | 4KB to 32MB |
| **Maximum Volume size**        | 32MB       | 2GB        | 2TB         | 128PB       |
`*`The maximum volume size for FAT32 is 2TB, but Windows limits formatting to only 32GB. However, volume sizes formatted on other OS with larger volume sizes are supported by Windows.

## NTFS File System
New Technology File System (NTFS) developed by Microsoft to add a little more in terms of security, reliability, and recovery capabilities. 
- Journaling - keeps a log of changes to the metadata in the volume.
- Access Controls
- Volume Shadow Copy - keeps track of changes made to a file, a user can restore previous file versions for recovery or system restore.
- Alternate Data Streams - a feature in NTFS that allows files to have multiple streams of data stored in a single file

### Master File Table
Like the File Allocation Table, there is a Master File Table in NTFS. However, the Master File Table, or MFT, is much more extensive than the File Allocation Table. It is a structured database that tracks the objects stored in a volume. Therefore, we can say that the NTFS file system data is organized in the Master File Table. From a forensics point of view, the following are some of the critical files in the MFT:
- $MFT - the first record in the volume, this file contains a directory of all the files present on the volume.
- $LOGFILE - stores the transactional logging of the file system. It helps maintain the integrity of the file system in the event of a crash
- $UsnJrnl - Update Sequence Number (USN) Journal, It contains information about all the files that were changed in the file system and the reason for the change. It is also called the change journal.

### MFT Explorer 
Eric Zimmerman tool 

## Recovering Deleted Files
A **disk image** file is a file that contains a bit-by-bit copy of a disk drive. A bit-by-bit copy saves all the data in a disk image file, including the metadata, in a single file.

### Autopsy
New Case is the first step

## Evidence of Execution

**Windows Prefetch Files:** When a program is run in Windows, it stores its information for future use. This stored information is used to load the program quickly in case of frequent use. This information is stored in prefetch files which are located in the `C:\Windows\Prefetch` directory, have a `.pf` extension, and contain:
- the last run times of the application, 
- the number of times the application was run, 
- and any files and device handles used by the file

Syntax on file and directory: 
- `PECmd.exe -f <path-to-Prefetch-files> --csv <path-to-save-csv>`
- `PECmd.exe -d <path-to-Prefetch-directory> --csv <path-to-save-csv>`

**Windows 10 Timeline:** Windows 10 stores recently used applications and files in an SQLite database called the Windows 10 Timeline found here: `C:\Users\<username>\AppData\Local\ConnectedDevicesPlatform\{randomfolder}\ActivitiesCache.db`

- `WxTCmd.exe -f <path-to-timeline-file> --csv <path-to-save-csv>`

**Windows Jump Lists:** Windows introduced jump lists to help users go directly to their recently used files from the taskbar. We can view jumplists by right-clicking an application's icon in the taskbar, and it will show us the recently opened files in that application. This data is stored in the following directory:
`C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations`

- `JLECmd.exe -f <path-to-Jumplist-file> --csv <path-to-save-csv>`

**Shortcut Files:**
Windows creates a shortcut file for each file opened either locally or remotely. The shortcut files contain information about the first and last opened times of the file and the path of the opened file, along with some other data. Shortcut files can be found in the following locations:

`C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Recent\`
`C:\Users\<username>\AppData\Roaming\Microsoft\Office\Recent\`
- `LECmd.exe -f <path-to-shortcut-files> --csv <path-to-save-csv>`

**IE/Edge history:**
An interesting thing about the IE/Edge browsing history is that it includes files opened in the system as well, whether those files were opened using the browser or not. Hence, a valuable source of information on opened files in a system is the IE/Edge history. We can access the history in the following location:

`C:\Users\<username>\AppData\Local\Microsoft\Windows\WebCache\WebCacheV*.dat`

- The files/folders accessed appear with a `file:///*` prefix in the IE/Edge history. Though several tools can be used to analyze Web cache data, you can use **Autopsy** to do so in the attached VM. For doing that, select Logical Files as a data source.
- In the Window where Autopsy asks about ingest modules to process data, check the box in front of 'Recent Activity' and uncheck everything else.

**Jump Lists:** As we already learned in the last task, Jump Lists create a list of the last opened files. This information can be used to identify both the last executed programs and the last opened files in a system. Remembering from the last task, Jump Lists are present at the following location:

`C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations`

**External Devices:**
USB - When any new device is attached to a system, information related to the setup of that device is stored in the `setupapi.dev.log`. This log contains the device serial number and the first/last times when the device was connected.This log is present at the following location:

`C:\Windows\inf\setupapi.dev.log`

**Shortcut Files:** As we learned in the previous task, shortcut files are created automatically by Windows for files opened locally or remotely. These shortcut files can sometimes provide us with information about connected USB devices. It can provide us with information about the volume name, type, and serial number. Recalling from the previous task, this information can be found at:

`C:\Users\<username>\AppData\Roaming\Microsoft\Windows\Recent\`

`C:\Users\<username>\AppData\Roaming\Microsoft\Office\Recent\`



