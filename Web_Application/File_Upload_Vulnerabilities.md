---
layout: default
title: "File Upload Vulnerabilities"
parent: "Web Application"
nav_order: 12
---


Consider a form containing fields for uploading an image, providing a description of it, and entering your username. Submitting such a form might result in a request that looks something like this: 
```HTTP
POST /images HTTP/1.1 
Host: normal-website.com 
Content-Length: 12345 
Content-Type: multipart/form-data; boundary=---------------------------012345678901234567890123456 ---------------------------012345678901234567890123456 
Content-Disposition: form-data; name="image"; filename="example.jpg" Content-Type: image/jpeg [...binary content of example.jpg...] ---------------------------012345678901234567890123456 
Content-Disposition: form-data; name="description" This is an interesting description of my image. ---------------------------012345678901234567890123456 
Content-Disposition: form-data; name="username" wiener ---------------------------012345678901234567890123456--
```
- These individual parts may also contain their own `Content-Type` header, which tells the server the MIME type of the data that was submitted using this input.

Tip: Web servers often use the `filename` field in `multipart/form-data` requests to determine the name and location where the file should be saved.

## Apache

To execute PHP, developers might have to add the following directives to their `/etc/apache2/apache2.conf` file:

```
LoadModule php_module /usr/lib/apache2/modules/libphp.so AddType application/x-httpd-php .php
```

Apache servers load a directory-specific configuration from a file called `.htaccess` if one is present.

## IIS Server

Similarly, developers can make directory-specific configuration on IIS servers using a `web.config` file. This might include directives such as the following, which in this case allows JSON files to be served to users:

```
<staticContent> <mimeMap fileExtension=".json" mimeType="application/json" /> </staticContent>
```


## Obfuscating File Extensions
- `exploit.pHp`
- `exploit.php.jpg`
	- might be interpreted as either depending on the file system
- `exploit.php.`
	- Some components will strip or ignore trailing whitespaces, dots, and such
- `exploit%2Ephp`
	- Checks to see if the URL encoding is decoded server-side instead of input validation
- `exploit.asp;.jpg` or `exploit.asp%00.jpg`
	- Add semicolons or URL-encoded null byte characters before the file extension. If validation is written in a high-level language like PHP or Java, but the server processes the file using lower-level functions in C/C++, for example, this can cause discrepancies in what is treated as the end of the filename
- Try using multibyte unicode characters, which may be converted to null bytes and dots after unicode conversion or normalization. Sequences like `xC0 x2E`, `xC4 xAE` or `xC0 xAE` may be translated to `x2E` if the filename parsed as a UTF-8 string, but then converted to ASCII characters before being used in a path.
- `exploit.p.phphp`
	- Even when `.php` is stripped, another `.php` remains

## Other
- It might try to verify the dimensions of the image and reject the file if it has not dimensions, so they may need to be spoofed
- JPEG files always begin with the bytes `FF D8 FF`.
	- This is a much more robust way of validating the file type, but even this isn't foolproof. Using special tools, such as ExifTool, it can be trivial to create a polyglot JPEG file containing malicious code within its metadata.
- XSS or SVG images from an HTML file that don't execute
	- Note that due to same-origin policy restrictions, these kinds of attacks will only work if the uploaded file is served from the same origin to which you upload it.

