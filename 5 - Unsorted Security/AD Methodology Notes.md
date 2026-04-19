---
title: "AD Methodology Notes"
parent: "5 - Unsorted Security"
nav_order: 4
layout: default
---

# AD Methodology Notes

After an nmap scan on a machine with Active Directory (AD), my usual approach involves prioritizing enumeration of key services and identifying potential misconfigurations. Here's how I typically prioritize and proceed:

1. SMB (Port 445): This is often my first point of focus due to its common vulnerabilities. I look for open shares (`smbclient`, `enum4linux`, or `smbmap`), weak permissions on shared files, and potential misconfigurations like Null Sessions or anonymous access. Sometimes, you'll find sensitive information in shared folders or credentials in configuration files.
    
2. LDAP (Port 389/636): I enumerate users and groups via LDAP, especially if anonymous bind is allowed. Tools like `ldapsearch` or `enum4linux` help in gathering information about the domain, users, groups, and organizational units. A weak configuration may expose sensitive data, and if you can bind as an authenticated user, it opens more enumeration opportunities.
    
3. Kerberos (Port 88): I use tools like `kerbrute` or `GetNPUsers.py` from `Impacket` to perform username enumeration and check for accounts with no pre-authentication required (AS-REP roasting). I also enumerate service principal names (SPNs) using `GetUserSPNs.py` for Kerberoasting.
    
4. RPC (Port 135/139): I attempt to enumerate users and shares using tools like `rpcclient`. Sometimes, this provides a way to query information from the domain controller, including user accounts and group memberships.
    
5. DNS (Port 53): Check if zone transfers are allowed (`dig axfr` or `host -l`). Misconfigured DNS can leak valuable information about the domain, hosts, and network architecture.

**Tricks that often work:**

- Password Spraying: Once I have usernames from LDAP/Kerberos, I often test weak or common passwords using tools like `crackmapexec`.
    
- Privilege Escalation: If I have a low-privileged account, I focus on privilege escalation, particularly checking for misconfigurations in GPOs, weak permissions on AD objects, or vulnerable services.
    
- Group Policy Preferences: Check for GPP password vulnerabilities (stored in SYSVOL with reversible encryption).
    
- Exploiting SMB vulnerabilities: Like EternalBlue or any open SMB shares with misconfigured permissions.

**I will add just a few things to it**

- If you find a valid username via the enumeration steps that OP has mentioned then try an asrep roast.  
    
- If you are able to establish an anonymous bind then search for passwords in description field or any intel you can find. You can use ldapsearch for this  
    
- Check if you can leak NTLM creds via various methods. This is a very comprehensive article that covers this [https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/](https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/)
    
- Look for creds in smbshares and loginscripts, check if Group Policy Preferences (GPP) Passwords are in use
    
- If you manage to get a username and password/hash, repeat the enumeration steps OP mentioned to see if this account has access to information that a null session or anonymous bind doesnt
    
- Find useraccounts with the SPN set and try to kerberoast with impacket
    
- Recon using bloodhound
    
- Run winpeas and check the usual non AD escalation paths
    
- If you manage to escalate to a local admin/system account then dump cached creds with mimikatz. For a non AD machine that is domain joined this can provide you other accounts for lateral movement
