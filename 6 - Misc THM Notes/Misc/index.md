---
title: "Misc"
parent: "6 - Misc THM Notes"
nav_order: 4
layout: default
has_children: true
---

# Misc

## Aircrack-ng

#### aircrack-ng

`aircrack-ng -a2 -b 22:C7:12:C7:E2:35 VanSpy.pcap -w /usr/share/wordlists/rockyou.txt`
- `a` is the mode with 2 referring to WPA/WPA2
- `-b` selects the target network based on the access point MAC address
	- also works: `aircrack-ng VanSpy.pcap -w /usr/share/wordlists/rockyou.txt`

https://hashcat.net/cap2hashcat/

---

## RSA Encrytion

1. Bob chooses two prime numbers: p = 157 and q = 199. He calculates n = p × q = 31243.
2. With ϕ(n) = n − p − q + 1 = 31243 − 157 − 199 + 1 = 30888, Bob selects e = 163 such that e is relatively prime to ϕ(n); moreover, he selects d = 379, where e × d = 1 mod ϕ(n), i.e., e × d = 163 × 379 = 61777 and 61777 mod 30888 = 1. The public key is (n,e), i.e., (31243,163) and the private key is $(n,d), i.e., (31243,379).
3. Let’s say that the value they want to encrypt is x = 13, then Alice would calculate and send y = xe mod n = 13163 mod 31243 = 16341.
4. Bob will decrypt the received value by calculating x = yd mod n = 16341379 mod 31243 = 13. This way, Bob recovers the value that Alice sent.

You need to know the main variables for RSA in CTFs: p, q, m, n, e, d, and c. As per our numerical example:

- p and q are large prime numbers
- n is the product of p and q
- The public key is n and e
- The private key is n and d
- m is used to represent the original message, i.e., plaintext
- c represents the encrypted text, i.e., ciphertext

---

## Reverse Engineering

### Volatility

```bash
for plugin in windows.malfind.Malfind windows.psscan.PsScan windows.pstree.PsTree windows.pslist.PsList windows.cmdline.CmdLine windows.filescan.FileScan windows.dlllist.DllList; do vol3 -q -f $memoryImage.mem $plugin > wcry.$plugin.txt; done
```

This runs volatility using these plugins:
- windows.pstree.PsTree
- windows.pslist.PsList
- windows.cmdline.CmdLine
- windows.filescan.FileScan
- windows.dlllist.DllList
- windows.malfind.Malfind
- windows.psscan.PsScan

You can also prepocess the memory image with `strings`:
- `strings $memoryImage.mem > image.strings.ascii.txt`
- `strings $memoryImage.mem -e l > image.strings.unicode_little_endian.txt`
- `strings $memoryImage.mem -e b > image.strings.unicode_big_endian.txt`

### FlareVM:

Below are the tools grouped by their category. 

#### Reverse Engineering & Debugging

Reverse engineering is like solving a puzzle backward: you take a finished product apart to understand how it works. Debugging is identifying errors, understanding why they happen, and correcting the code to prevent them.

- **Ghidra** - NSA-developed open-source reverse engineering suite.  
    
- **x64dbg** - Open-source debugger for binaries in x64 and x32 formats.  
    
- **OllyDbg** - Debugger for reverse engineering at the assembly level.  
    
- **Radare2** - A sophisticated open-source platform for reverse engineering.
- **Binary Ninja** - A tool for disassembling and decompiling binaries.  
    
- **PEiD** - Packer, cryptor, and compiler detection tool.

#### Disassemblers & Decompilers

Disassemblers and Decompilers are crucial tools in malware analysis. They help analysts understand malicious software’s behaviour, logic, and control flow by breaking it into a more understandable format. The tools mentioned below are commonly used in this category.

- **CFF Explorer** - A PE editor designed to analyze and edit Portable Executable (PE) files.
- **Hopper Disassembler** - A Debugger, disassembler, and decompiler.
- **RetDec** - Open-source decompiler for machine code.

#### Static & Dynamic Analysis

Static and dynamic analysis are two crucial methods in cyber security for examining malware. Static analysis involves inspecting the code without executing it, while dynamic analysis involves observing its behaviour as it runs. The tools mentioned below are commonly used in this category.

- **Process Hacker** - Sophisticated memory editor and process watcher.
- **PEview** - A portable executable (PE) file viewer for analysis.
- **Dependency Walker** - A tool for displaying an executable’s DLL dependencies.
- **DIE (Detect It Easy)** - A packer, compiler, and cryptor detection tool.

#### Forensics & Incident Response

Digital Forensics involves the collection, analysis, and preservation of digital evidence from various sources like computers, networks, and storage devices. At the same time, Incident Response focuses on the detection, containment, eradication, and recovery from cyberattacks. The tools mentioned below are commonly used in this category.

- **Volatility** - RAM dump analysis framework for memory forensics.
- **Rekall** - Framework for memory forensics in incident response.
- **FTK Imager** - Disc image acquisition and analysis tools for forensic use.

#### Network Analysis

Network Analysis includes different methods and techniques for studying and analysing networks to uncover patterns, optimize performance, and understand the underlying structure and behaviour of the network.

- **Wireshark** - Network protocol analyzer for traffic recording and examination.  
    
- **Nmap** - A vulnerability detection and network mapping tool.  
    
- **Netcat** - Read and write data across network connections with this helpful tool.

#### File Analysis

File Analysis is a technique used to examine files for potential security threats and ensure proper file permissions.

- **FileInsight** - A program for looking through and editing binary files.
- **Hex Fiend** - Hex editor that is light and quick.
- **HxD** - Binary file viewing and editing with a hex editor.

#### Scripting & Automation

Scripting and Automation involve using scripts such as PowerShell and Python to automate repetitive tasks and processes, making them more efficient and less prone to human error.

- **Python** - Mainly automation-focused on Python modules and tools.
- **PowerShell Empire** - Framework for PowerShell post-exploitation.

#### Sysinternals Suite

The Sysinternals Suite is a collection of advanced system utilities designed to help IT professionals and developers manage, troubleshoot, and diagnose Windows systems.

- **Autoruns** - Shows what executables are configured to run during system boot-up.
- **Process Explorer** - Provides information about running processes.
- **Process Monitor** -Monitors and logs real-time process/thread activity.

---

## Security Engineer

**VLANs** (**V**irtual **LAN**) are used to segment portions of a network at layer two and differentiate devices. 
VLANs are configured on a switch by adding a "tag" to a frame. The **802.1q** or **dot1q** tag will designate the VLAN that the traffic originated from.
The **Native VLAN** is used for any traffic that is not tagged and passes through a switch. To configure a native VLAN, we must determine what interface and tag to assign them, then set the interface as the default native VLAN. Below is an example of adding a native VLAN in Open vSwitch.

---

## File Analysis

`Oledump.py` is a Python tool that analyzes **OLE2** files, commonly called Structured Storage or Compound File Binary Format. **OLE** stands for **Object Linking and Embedding,** a proprietary technology developed by Microsoft. OLE2 files are typically used to store multiple data types, such as documents, spreadsheets, and presentations, within a single file. This tool is handy for extracting and examining the contents of OLE2 files, making it a valuable resource for forensic analysis and malware detection.
- `oledump.py $file`
- then `oledump.py $file -s $treamNumber`
- then `oledump.py $file -s $treamNumber --vbadecompress`

---

## Defend Against Phishing

- Email Security (SPF, DKIM, DMARC)
- SPAM Filters (flags or blocks incoming emails based on reputation)
- Email Labels (alert users that an incoming email is from an outside source)
- Email Address/Domain/URL Blocking (based on reputation or explicit denylist)
- Attachment Blocking (based on the extension of the attachment)
- Attachment Sandboxing (detonating email attachments in a sandbox environment to detect malicious activity)
- Security Awareness Training (internal phishing campaigns)

#### SPF
Sender Policy Framework (SPF) is used to authenticate the sender of an email. With an SPF record in place, Internet Service Providers can verify that a mail server is authorized to send email for a specific domain. An SPF record is a DNS TXT record containing a list of the IP addresses that are allowed to send email on behalf of your domain.

How does a basic SPF record look like?

`v=spf1 ip4:127.0.0.1 include:_spf.google.com -all`
- `v=spf1` -> This is the start of the SPF record
- `ip4:127.0.0.1` -> This specifies which IP (in this case version IP4 & not IP6) can send mail
- `include:_spf.google.com` -> This specifies which domain can send mail
- `-all` -> non-authorized emails will be rejected

Let's look at Twitter's SPF record using dmarcian's SPF Surveyor [tool](https://dmarcian.com/spf-survey/).

#### DKIM
DKIM stands for **DomainKeys Identified Mail** and is used for the authentication of an email that’s being sent. Like SPF, DKIM is an open standard for email authentication that is used for DMARC alignment. A DKIM record exists in the DNS, but it is a bit more complicated than SPF. *DKIM’s advantage is that it can survive forwarding*, which makes it superior to SPF and a foundation for securing your email.

DKIM Record looks like:
`v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxTQIC7vZAHHZ7WVv/5x/qH1RAgMQI+y6Xtsn73rWOgeBQjHKbmIEIlgrebyWWFCXjmzIP0NYJrGehenmPWK5bF/TRDstbM8uVQCUWpoRAHzuhIxPSYW6k/w2+HdCECF2gnGmmw1cT6nHjfCyKGsM0On0HDvxP8I5YQIIlzNigP32n1hVnQP+UuInj0wLIdOBIWkHdnFewzGK2+qjF2wmEjx+vqHDnxdUTay5DfTGaqgA9AKjgXNjLEbKlEWvy0tj7UzQRHd24a5+2x/R4Pc7PF/y6OxAwYBZnEPO0sJwio4uqL9CYZcvaHGCLOIMwQmNTPMKGC9nt3PSjujfHUBX3wIDAQA`
- `v=DKIM1`-> This is the version of the DKIM record. This is optional. 
- `k=rsa` -> This is the key type. The default value is RSA. RSA is an encryption algorithm (cryptosystem).
- `p=` -> This is the public key that will be matched to the private key, which was created during the DKIM setup process.

#### DMARC
DMARC, (**Domain-based  Message Authentication Reporting, & Conformance**) an open source standard, uses a concept called alignment to tie the result of two other open source standards, SPF (a published list of servers that are authorized to send email on behalf of a domain) and DKIM (a tamper-evident domain seal associated with a piece of email), to the content of an email. If not already deployed, putting a DMARC record into place for your domain will give you feedback that will allow you to troubleshoot your SPF and DKIM configurations if needed.

DMARC Record: `v=DMARC1; p=quarantine; rua=mailto:postmaster@website.com`
- `v=DMARC1` -> Must be in all caps, and it's not optional
- `p=quarantine` -> If a check fails, then an email will be sent to the spam folder (DMARC Policy)
- `rua=mailto:postmaster@website.com` -> Aggregate reports will be sent to this email address

DMARC checker: https://dmarcian.com/domain-checker/

#### S/MIME
S/MIME (**Secure/Multipurpose internet Mail Extensions**) is a widely accepted protocol for sending digitally signed and encrypted messages. 2 main ingredients for S/MIME are: 1. **Digital Signatures** and 2. **Encryption**

---
