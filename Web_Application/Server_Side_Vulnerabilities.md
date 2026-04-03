---
layout: default
title: "Server Side Vulnerabilities"
parent: "Web Application"
nav_order: 31
---

### Path traversal

### Access Control
- `/admin` panel you can browse to even when not logged in
- `administrator-panel9898` you can view in a JS file
- Some applications determine the user's access rights or role at login, and then store this information in a user-controllable location. This could be:
	- A hidden field.
	- A cookie.
	- A preset query string parameter


### SSRF
*allows an attacker to cause the server-side application to make requests to an unintended location*
```HTTP
POST /product/stock HTTP/1.0 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 118 
stockApi=http://stock.weliketoshop.net:8080/product/stock/check%3FproductId%3D6%26storeId%3D1
```
becomes
```HTTP
POST /product/stock HTTP/1.0 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 118 
stockApi=http://localhost/admin
```

### OS command injection
try `|` instead of `&`

