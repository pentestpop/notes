---
layout: default
title: "Wireshark 2"
parent: "SOC"
grand_parent: "Defensive Security"
nav_order: 17
---


Statistics:
- Resolved Address
	- Can check hostnames here
- Protocol Hierarchy
	- Number of IPv4 conversations
- Conversations
	- How many bytes were transferred
- Endpoints
	- Number of IP addresses linked with each city
	- IP addresses which are linked to AS Organization
- Protocol Details
	- Can select IPv4 vs IPv6 from the bottom of the Statistics dropdown
- DNS
- HTTP


Display filter syntax:

![](assets/Images/Wireshark%202/Screenshot%202024-12-30%20at%203.02.30%20PM.png)


Logical expressions: 

![](assets/Images/Wireshark%202/Screenshot%202024-12-30%20at%203.02.49%20PM.png)

IP Filters:

![](assets/Images/Wireshark%202/Screenshot%202024-12-30%20at%203.03.52%20PM.png)

TCP and UDP Filters:

![](assets/Images/Wireshark%202/Screenshot%202024-12-30%20at%203.06.26%20PM.png)


Application Level Protocol Filters | HTTP and DNS

![](assets/Images/Wireshark%202/Screenshot%202024-12-30%20at%203.06.36%20PM.png)

Use the  "**Analyse --> Display Filter Expression**" when you can't remember


### Advanced Operators
- **contains**
	- Ex: `http.server contains "Apache"`
- **matches** - Search a pattern of a regular expression. It is case insensitive, and complex queries have a margin of error.
	- Ex: `http.hosts matches "\.(php|html)"`
	- Lists all HTTP packets where packets' "host" fields match keywords ".php" or ".html".
- **in** - Search a value or field inside of a specific scope/range.
	- Ex: `tcp.port in {80 443 8080}`
- **upper** - Convert a string value to uppercase
	- Ex: `upper(http.server) contains "APACHE"`
- **lower** - Convert a string value to lowercase.
	- Ex: `lower(http.server) contains "apache"`
- **string** - Convert a non-string value to a string.
	- Ex: `string(frame.number) matches "[13579]$"`
	- Finds all frames with odd numbers


### Bookmarks
Right click on search bar and click save this query

### Profiles
Save queries to different profiles such as one for CTFs and one for Network Troubleshooting


## Traffic Analysis
Nmap Scans

![](assets/Images/Wireshark%202/Screenshot%202024-12-30%20at%205.02.09%20PM.png)

