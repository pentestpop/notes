---
layout: default
title: "Aircrack-ng"
parent: "Misc"
grand_parent: "Defensive Security"
nav_order: 1
---


### aircrack-ng

`aircrack-ng -a2 -b 22:C7:12:C7:E2:35 VanSpy.pcap -w /usr/share/wordlists/rockyou.txt`
- `a` is the mode with 2 referring to WPA/WPA2
- `-b` selects the target network based on the access point MAC address
	- also works: `aircrack-ng VanSpy.pcap -w /usr/share/wordlists/rockyou.txt`

https://hashcat.net/cap2hashcat/