```http
GET /web-security HTTP/1.1 
Host: portswigger.net
```
- This used to not exist bc each IP would host one domain 
	- Now we have virtual hosts
	- Also CDN or load balancer

## Attack
*Attacks that involve injecting a payload directly into the Host header*

Off-the-shelf web applications typically don't know what domain they are deployed on unless it is manually specified in a configuration file during setup
- Sometimes they just pull from the host header:
- `<a href="https://_SERVER['HOST']/support">Contact support</a>`

The Host header is a potential vector for exploiting a range of other vulnerabilities, most notably:
- Web cache poisoning
- Business logic flaws in specific functionality
- Routing-based SSRF
- Classic server-side vulnerabilities, such as SQL injection

## How to test for and identify

1. Supply an arbitrary Host header
- Sometimes this won't work at all if the target IP is being derived from the Host header
- Sometimes it *will* work if there's a fallback option configured 

2. Check for flawed validation
- try to understand how the website parses the Host header to uncover loopholes
	- maybe they ignore the port
```http
GET /example HTTP/1.1 
Host: vulnerable-website.com:bad-stuff-here
```
- sometimes they use matching logic to apply arbitrary subdomains
	- Maybe you can bypass validation by registering an arbitrary domain name that ends with the same characters
		- `notvulnerable-website.com` vs `vulnerablewebsite.com`
	- Or subdomain you've already compromised: `hacked-subdomain.vulnerable-website.com`

3. Send ambiguous requests
- Duplicate headers
	- One could have precedence over the other
```HTTP
GET /example HTTP/1.1 
Host: vulnerable-website.com 
Host: bad-stuff-here
```
- Supply absolute URL
```HTTP
GET https://vulnerable-website.com/ HTTP/1.1 
Host: bad-stuff-here
```
- Add line wrapping
	- This could be a good idea if the front-end server ignores the indented one, but the back-end server doesn't
```HTTP
GET /example HTTP/1.1 
	Host: bad-stuff-here 
Host: vulnerable-website.com
```
	


4.  Inject host override headers
This is similar, but instead of being ambiguous which they will pick, it's intentionally trying to bypass
```HTTP
GET /example HTTP/1.1 
Host: vulnerable-website.com 
X-Forwarded-Host: bad-stuff-here
```
`X-Forwarded-Host` is the **standard**, but there are others:
- `X-Host`
- `X-Forwarded-Server`
- `X-HTTP-Host-Override`
- `Forwarded`


## Lab: Host header authentication bypass
`/admin` says: "Admin interface only available to **local** users"
Change header `Host: localhost`
- *Have to do this for each request*

## Lab: Basic password reset poisoning (**I don't get this one**)

1. Test the "Forgot your password?" functionality. 
2. Reset password email contains the query parameter `temp-forgot-password-token`..
3. In Burp, notice that the `POST /forgot-password` request is used to trigger the password reset email, and it contains the username as a body parameter. Send this request to Burp Repeater.
4. In Burp Repeater, observe that you can change the Host header to an arbitrary value and still successfully trigger a password reset. Notice that the URL in the email contains your arbitrary Host header instead of the usual domain name.
5. Back in Burp Repeater, change the Host header to your exploit server's domain name (`YOUR-EXPLOIT-SERVER-ID.exploit-server.net`) and change the `username` parameter to `carlos`. Send the request.
6. Go to your exploit server and open the access log. You will see a request for `GET /forgot-password` with the `temp-forgot-password-token` parameter containing Carlos's password reset token. Make a note of this token.
7. Go to your email client and copy the genuine password reset URL from your first email. Visit this URL in the browser, but replace your reset token with the one you obtained from the access log.
8. Change Carlos's password to whatever you want, then log in as `carlos` to solve the lab.

~~*I kind of don't understand how the emails get delivered when you change the Host address*.~~
==Ok, so basically the change the host header because that's what generates the password reset link==


## Lab: Web cache poisoning via ambiguous requests
Refer to [Web Cache Poisoning](obsidian://open?vault=Security&file=Burp%20Suite%20Academy%2FWeb%20Cache%20Poisoning)

You basically do a simple web cache poisoning using the `HTTP Host` header

![](/assets/images/HTTP%20Host%20header%20attacks/host_header_cache_poisoing.png)
- See the `/resources/js/tracking.js`
- **Solution** - add a second `Host` header and see that it is the source for the `tracking.js` file
- Rename the exploit `/resources/js/tracking.js`
- Poison the cache with the exploit server as the second `Host` header

## Lab: Routing-based SSRF
**Solution** - this is as simple as knowing there is an admin panel at `/admin` on an internal host and using Intruder to fuzz for different `Host` headers with `Host: 192.168.0.x` until you get to 154. 

```HTTP
POST /admin/delete HTTP/2
Host: 192.168.0.154

...

csrf=yDkWspviRNjw5a97lQouTBEYEMiTOFAA&username=carlos
```

## Lab: SSRF via flawed request parsing
"This lab is vulnerable to routing-based SSRF due to its flawed parsing of the request's intended host. You can exploit this to access an insecure intranet admin panel located at an internal IP address."

**Solution:** This is a matter of fuzzing for the internal host as above, but in this case, you most also supply the full endpoint in the request to get to the admin page. Ex:

First:
```HTTP
GET https://0a1c00ca034d533284872054000c0024.web-security-academy.net/admin HTTP/2
Host: 192.168.0.143
...
```
Then:
```HTTP
POST /admin/delete HTTP/2
Host: 0a1c00ca034d533284872054000c0024.web-security-academy.net

...

csrf=tsvY2E7q7o6I6tfzpYhxG8PjtaTNrLtH&username=carlos
```
- *Note that the Host header changed back at this point, and it still worked, probably because of the csrf token. If this had not worked, I could have used the full endpoint and internal host in the `POST` request.*


# Connection State Attacks

For performance reasons, many websites reuse connections for multiple request/response cycles with the same client. Poorly implemented HTTP servers sometimes work on the dangerous assumption that certain properties, such as the Host header, are identical for all HTTP/1.1 requests sent over the same connection. This may be realistically true of requests sent by a browser but not for a sequence of requests sent from Burp Repeater. This can lead to a number of potential issues.

For example, you may occasionally encounter servers that only perform thorough validation on the first request they receive over a new connection. In this case, you c*an potentially bypass this validation by sending an innocent-looking initial request then following up with your malicious one down the same connection*.

## Lab: Host validation bypass via connection state attack

**Solution:** Capture a request, add it to a group, duplicate it, send it in parallel with a `GET /admin/delete?csrf=<>&username=carlos`
- You have to grab the CSRF token from one request and use it in the next attempt
- *Most likely there is a way to script this such that the response from one becomes the paramenter in the next*
- I suspect it's actually supposed to be a `POST` request with the parameters in the body, but it works with the parameters in the request as well

# SSRF via a malformed request line

Custom proxies sometimes fail to validate the request line properly, which can allow you to supply unusual, malformed input with unfortunate results.

For example, a reverse proxy might take the path from the request line, prefix it with `http://backend-server`, and route the request to that upstream URL. This works fine if the path starts with a `/` character, but what if starts with an `@` character instead?

`GET @private-intranet/example HTTP/1.1`

The resulting upstream URL will be `http://backend-server@private-intranet/example`, which most HTTP libraries interpret as a request to access `private-intranet` with the username `backend-server`.