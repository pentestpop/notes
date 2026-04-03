---
layout: default
title: "Linux Forensics"
parent: "SOC"
grand_parent: "Defensive Security"
nav_order: 5
---

# Linux Forensics

## OS and Account Information
**OS release information:** `cat /etc/os-release`

**User accounts:** `cat /etc/password | column -t -s :`

**Group Information:** `cat /etc/group`

**Sudoers list:** `sudo cat /etc/sudoers`

**Login information:** In the /var/log directory, we can find log files of all kinds including `wtmp` and `btmp`. The `btmp` file saves information about failed logins, while the `wtmp` keeps historical data of logins. These files are not regular text files that can be read using `cat`, `less` or `vim`; instead, they are binary files, which have to be read using the `last` utility. You can learn more about the `last` utility by reading its man page.
- `sudo last -f /var/log/wtmp`

**Authentication logs:** `cat /var/log/auth.log |tail`

## System Configuration
**Hostname:** `cat /etc/hostname`

**Timezone:** `cat /etc/timezone`

**Network Configuration:** `cat /etc/network/interfaces`
- `ip address show`

**Active network connections:** `netstat -natp`

**Running processes:** `ps aux`

**DNS information:** `cat /etc/hosts`
- The information about DNS servers that a Linux host talks to for DNS resolution is stored in the resolv.conf file. Its location is `/etc/resolv.conf`.
- `cat /etc/resolv.conf`


## Persistence mechanisms
**Cron jobs** - Cron jobs are commands that run periodically after a set amount of time. A Linux host maintains a list of Cron jobs in a file located at `/etc/crontab`.
 - `cat /etc/crontab`

**Service startup** - Like Windows, services can be set up in Linux that will start and run in the background after every system boot. A list of services can be found in the `/etc/init.d` directory.
- `ls /etc/init.d`

**.Bashrc** - When a bash shell is spawned, it runs the commands stored in the `.bashrc` file. This file can be considered as a startup list of actions to be performed. Hence it can prove to be a good place to look for persistence.
- `cat ~/.bashrc`

## Evidence of execution
**Sudo execution history** - All the commands that are run on a Linux host using `sudo` are stored in the auth log.
- `cat /var/log/auth.log* |grep -i $COMMAND|tail`

**Bash history** - Any commands other than the ones run using `sudo` are stored in the bash history.
- `cat ~/.bash_history`

**Files accessed using vim** - The `Vim` text editor stores logs for opened files in `Vim` in the file named `.viminfo` in the home directory.
- `cat ~/.viminfo`

## Log files
**Syslog** - The Syslog contains messages that are recorded by the host about system activity. The detail which is recorded in these messages is configurable through the logging level. We can use the `cat` utility to view the Syslog, which can be found in the file `/var/log/syslog`. Since the Syslog is a huge file, it is easier to use `tail`, `head`, `more` or `less` utilities to help make it more readable.
- `cat /var/log/syslog* | head`

**Auth logs** - The auth logs contain information about users and authentication-related logs.
- `cat /var/log/auth.log* | head`

**Third-party logs** - Similar to the syslog and authentication logs, the `/var/log/` directory contains logs for third-party applications such as webserver, database, or file share server logs.
- `ls /var/log` then `cat /var/log/$example/$example.log`

