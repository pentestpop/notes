---
layout: default
title: "Snort Cheat Sheet"
parent: "SOC"
grand_parent: "Defensive Security"
nav_order: 8
---

1. Write a **single** rule to detect "**all TCP port 80 traffic**" packets in the given pcap file.
	1. `alert tcp any any <> any 80 (msg: "TCP Port 80  Activity Detected"; sid: 100001; rev:1;)`
2. Write a **single** rule to detect "**all TCP port 21**"  traffic in the given pcap.
	1. `alert tcp any any <> any 21 (msg: "FTP Port 21 Activity Detected"; sid: 1000001;)`
3. Write a rule to detect failed FTP login attempts in the given pcap.
	1. `alert tcp any any <> any 21 (msg: "Failed FTP login attempt";content:"530";sid:1000001;)`
4. Write a rule to detect FTP login attempts with the "Administrator" username but no password entered yet.
	1. `alert tcp any any <> 21 (msg: "Failed FTP Administrator login";content:"Administrator";content:"331";sid:1000001;)`
5. Write a rule to detect the PNG file in the given pcap.
	1. `alert tcp any any <> any any (msg:"PNG File Detected"; content:"|89 50 4E 47 0D 0A 1A 0A|"; depth:8;sid:1000001;)`
6. Write a rule to detect the GIF file in the given pcap.
	1. `alert tcp any any -> any any (msg:"GIF File Detected"; content:"GIF";sid:1000001;)`