---
layout: default
title: "Redline"
parent: "SOC"
grand_parent: "Defensive Security"
nav_order: 7
---

Redline will essentially give an analyst a 30,000-foot view (10 kilometers high view) of a Windows, Linux, or macOS endpoint. Using Redline, you can analyze a potentially compromised endpoint through the memory dump, including various file structures.
- Collect registry data (Windows hosts only)
- Collect running processes
- Collect memory images (before Windows 10)
- Collect Browser History
- Look for suspicious strings

## Data Collection
Steps: 
1. Pick a method (Standard, Comprehensive or IOC Search)
2. Pick an OS
3. Edit your script including Memory, Disk, System, Network, and Other
	1. Memory
		1. You can configure the script to collect memory data such as process listings, drivers enumeration (Windows hosts only), and hook detection (versions before Windows 10).
	2. Disk: 
		1. This is where you can collect the data on Disks partitions and Volumes along with File Enumeration.
	3. System
		1. The system will provide you with machine information:
			- Machine and operating system (OS) information
			- Analyze system restore points (Windows versions before 10 only)
			- Enumerate the registry hives (Windows only)
			- Obtain user accounts (Windows and OS X only)
			- Obtain groups (OS X only)
			- Obtain the prefetch cache (Windows only)
	4. Network:
		1. Network Options supports Windows, OS X, and Linux platforms. You can configure the script to collect network information and browser history, which is essential when investigating the browser activities, including malicious file downloads and inbound/outbound connections.
	5. Other: 

*Note that for "Save Your Collector TO" the folder must be empty. Then to rn the audit (`.bat` file), you must run as Administrator.*

## Redline Interface
A *handle* is a connection from a process to an object or resource in a Windows operating system. Operating systems use handles for referencing internal objects like files, registry keys, resources, etc.

Some of the important sections you need to pay attention to are:
- Strings
- Ports
- File System (**not included in this analysis session**)
- Registry
- Windows Services
- Tasks (Threat actors like to create scheduled tasks for persistence)
- Event Logs (this another great place to look for the suspicious Windows PowerShell events as well as the Logon/Logoff, user creation events, and others)
- ARP and Route Entries (**not included in this analysis session**)
- Browser URL History (**not included in this analysis session**)
- File Download History

