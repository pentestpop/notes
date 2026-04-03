---
layout: default
title: "Windows Local Persistence"
parent: "SOC"
grand_parent: "Defensive Security"
nav_order: 14
---

### Startup folder

Each user has a folder under `C:\Users\<your_username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
where you can put executables to be run whenever the user logs in.

### Run / RunOnce

You can also force a user to execute a program on logon via the registry. Instead of delivering your payload into a specific directory, you can use the following registry entries to specify applications to run at logon:

- HKCU\Software\Microsoft\Windows\CurrentVersion\Run
- HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce
- HKLM\Software\Microsoft\Windows\CurrentVersion\Run
- HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce
