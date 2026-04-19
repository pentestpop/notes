Nmap Scans:

![](/assets/images/Wireshark%202/Screenshot%202024-12-31%20at%202.19.39%20PM.png)

## Types of Scans
There are a few. 

### TCP Connect Scans:
- Relies on the three-way handshake (needs to finish the handshake process).
- Usually conducted with `nmap -sT` command.
- Used by non-privileged users (only option for a non-root user).
- Usually has a windows size larger than 1024 bytes as the request expects some data due to the nature of the protocol.

The given filter shows the TCP Connect scan patterns in a capture file:
`tcp.flags.syn==1 and tcp.flags.ack==0 and tcp.window_size > 1024`

### SYN Scans:
- Doesn't rely on the three-way handshake (no need to finish the handshake process).
- Usually conducted with `nmap -sS` command.
- Used by privileged users.
- Usually have a size less than or equal to 1024 bytes as the request is not finished and it doesn't expect to receive data.

The given filter shows the TCP SYN scan patterns in a capture file:
`tcp.flags.syn==1 and tcp.flags.ack==0 and tcp.window_size <= 1024

### UDP Scans
- Doesn't require a handshake process
- No prompt for open ports
- ICMP error message for close ports
- Usually conducted with `nmap -sU` command.

The given filter shows the UDP scan patterns in a capture file:
`icmp.type==3 and icmp.code==3`


## ARP Poisoning and Man in the Middle
**ARP analysis in a nutshell:**
- Works on the local network
- Enables the communication between MAC addresses
- Not a secure protocol
- Not a routable protocol
- It doesn't have an authentication function
- Common patterns are request & response, announcement and gratuitous packets.

![](/assets/images/Wireshark%202/Screenshot%202024-12-31%20at%203.11.37%20PM.png)

Analysis
![](/assets/images/Wireshark%202/Screenshot%202024-12-31%20at%203.13.15%20PM.png)



## DHCP Analysis

![](/assets/images/Wireshark%202/Screenshot%202024-12-31%20at%204.28.58%20PM.png)

## NetBIOS (NBNS) Analysis
![](/assets/images/Wireshark%202/Screenshot%202024-12-31%20at%204.32.38%20PM.png)


## Kerberos
![](/assets/images/Wireshark%202/Screenshot%202024-12-31%20at%204.33.27%20PM.png)

## FTP
![](/assets/images/Wireshark%202/Screenshot%202025-01-02%20at%203.19.59%20PM.png)


## HTTP
![](/assets/images/Wireshark%202/Screenshot%202025-01-02%20at%203.51.05%20PM.png)

### User Agent
![](/assets/images/Wireshark%202/Screenshot%202025-01-02%20at%203.51.22%20PM.png)

## HTTPS
Decrypting HTTPS Traffic

![](/assets/images/Wireshark%202/Screenshot%202025-01-02%20at%203.51.40%20PM.png)