---
title: "SSH"
parent: "1 - Enumeration"
nav_order: 8
layout: default
---

# SSH

`ssh -i $key $user@$target`

alternate port `ssh -p $port $user@$target`

You can connect to the ssh service via netcat to grab the banner and search the version for OS info.
- `nc -nv $IP 22`

## Brute forcing:
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

## creating ssh key
- ssh-keygen
- `ssh -p 2222(unless 22) -i $created_key(no pub) $user@$host`
- Using a id_sa (private key) from /home/user/.ssh/id_sa

## Password Protected SSH key
1. may need to chmod 600 id_rsa (too many permissions won't work)
2. ssh2john id_rsa > ssh.hash
3. remove "id_rsa:" from ssh.hash
4. hashcat -h | grep -i "ssh" (22921 for example)
5. hashcat -m 22921 ssh.hash ssh.passwords -r ssh.rule --force
