---
title: "Checklist to Run Every Time"
parent: "5 - Unsorted Security"
nav_order: 8
layout: default
---

# Checklist to Run Every Time

Note that CMD+L is the key to create and check boxes

- [ ] unchecked
- [x] 

### Enumeration
- [ ] `nmap $IP`
- [ ] then `nmap -p- $IP -T4`
- [ ] then `nmap -$ports -sC -A -T4 $IP -oN nmap`
- [ ] then `nmap -sU -T4 $IP`
- [ ] `smbclient -L \\\\$IP\\ -N`
- [ ] `ftp anonymous@$IP`
- [ ] `nxc smb -u '' -p '' $IP`
	- This should be able to help you get the domain name
- [ ] Add name of box to `users.txt` and `passwords.txt`


### Linux Foothold
- [ ] `./vbenum.sh`
- [ ] `./linpeas.sh`
- [ ] `./lse.sh -l1`
- [ ] `ps aux | grep -i 'root' --color=auto`
- [ ] `./pspy64`
- [ ] `ls /opt`
- [ ] `ls /var/html/www` or `tree`
	- or whatever the web directory is
- [ ] `tree /home`
- [ ] `find / -perm -u=s -type f 2>/dev/null`
- [ ] `find / -writable -type d 2>/dev/null`
- [ ] `find / -type f -name *.conf 2>/dev/null`
	- [ ] `/find / -type f -name *pass* 2>/dev/null`
- [ ] `sudo -l`
- [ ] `cat /etc/passwd`
- [ ] `cat /etc/shadow`


### Windows Foothold
- [ ] Is there anything unusual in `C:\`
- [ ] Is there anything unusual in `C:\Program Files`
- [ ] `systeminfo`
- [ ] `powershell Get-History`
- [ ] `whoami /priv`
- [ ] `whoami /groups`
- [ ] `Get-Content "$HOME\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"`
- [ ] `.\winpeas.exe`
- [ ] `tree /a /f C:\Users` for anything that sticks out
- [ ] `Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue`
	- `Get-ChildItem -Path C:\xampp -Include *.txt,*.ini -File -Recurse -ErrorAction SilentlyContinue` - sub out xampp for other server
	- `Get-ChildItem -Path C:\Users\ -Include *.txt,*.pdf,*.xls,*.xlsx,*.doc,*.docx -File -Recurse -ErrorAction SilentlyContinue`


### AD Post Privesc
- [ ] `.\mimikatz.exe "privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "lsadump::sam" "lsadump::secrets" "exit"`
- [ ] `.\Rubeus.exe kerberoast /format:hashcat /nowrap /outfile:hashes.kerberoast`
- [ ] `.\Rubeus.exe asreproast /format:hashcat /nowrap /outfile:hashes.asreproast`
- [ ] `Import-Module .\adPEAS.ps1` and `Invoke-adPEAS`
- [ ] `bloodhound-python -u $user -p '$password' -ns $ip -d domain.offsec -c all`
- [ ] `.\adPEAS-Light.ps1`
- [ ] Did you get all users of a domain with something like `sudo nxc smb $IP -u $user -p $password --users`
