---
title: "Access Control and Logic"
parent: "4 - Web_Application"
nav_order: 9
layout: default
has_children: true
---

# Access Control and Logic

## Information Disclosure

Check the `TRACE` method to see if there are any special headers:
Ex: `X-Custom-IP-Authorization: 127.0.0.1`

Remember when downloading a `.git` directory that you need to use a `git` or a `git` manager to actually get anything out of it

---

## Access Control

#### Lab: URL-based access control can be circumvented
Test that you are able to use the `X-Original-URL` header by adding it
- Change the URL in the request line to `/` and add the HTTP header `X-Original-URL: /invalid`
	- The fact that you get a "not found" response means that it has been processed
- Change the `X-Original-URL` value to `/admin` and see that you can access the admin page
- Change the query string to `/?username=carlos` and the `X-Original-URL` header to `/admin/delete`
	- *In practice I expect this will require some figuring out*


#### Lab: Method-based access control can be circumvented
- Login with admin credentials to check things out
- Login with `wiener` and see your session cookie
- Go back to request where you can see how to upgrade a user and substitute the `wiener` cookies
	- It won't work
- Change to `GET` request and notice that you get `"Missing parameter 'username'"` even though these exist in the `POST` request
- Change endpoint to `GET /admin-roles?username=wiener&action=upgrade` using the `wiener` cookies
- ***Basically try changing to a `GET` request and then adding the parameters you want to the endpoint you request***


#### Lab: Multi-step process with no access control on one step
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

#### Lab: Referer-based access control
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

---

## File Upload Vulnerabilities

Consider a form containing fields for uploading an image, providing a description of it, and entering your username. Submitting such a form might result in a request that looks something like this: 
```HTTP
POST /images HTTP/1.1 
Host: normal-website.com 
Content-Length: 12345 
Content-Type: multipart/form-data; boundary=---------------------------012345678901234567890123456 ---------------------------012345678901234567890123456 
Content-Disposition: form-data; name="image"; filename="example.jpg" Content-Type: image/jpeg [...binary content of example.jpg...] ---------------------------012345678901234567890123456 
Content-Disposition: form-data; name="description" This is an interesting description of my image. ---------------------------012345678901234567890123456 
Content-Disposition: form-data; name="username" wiener ---------------------------012345678901234567890123456--
```
- These individual parts may also contain their own `Content-Type` header, which tells the server the MIME type of the data that was submitted using this input.

Tip: Web servers often use the `filename` field in `multipart/form-data` requests to determine the name and location where the file should be saved.

### Apache

To execute PHP, developers might have to add the following directives to their `/etc/apache2/apache2.conf` file:

```
LoadModule php_module /usr/lib/apache2/modules/libphp.so AddType application/x-httpd-php .php
```

Apache servers load a directory-specific configuration from a file called `.htaccess` if one is present.

### IIS Server

Similarly, developers can make directory-specific configuration on IIS servers using a `web.config` file. This might include directives such as the following, which in this case allows JSON files to be served to users:

```
<staticContent> <mimeMap fileExtension=".json" mimeType="application/json" /> </staticContent>
```


### Obfuscating File Extensions
- `exploit.pHp`
- `exploit.php.jpg`
	- might be interpreted as either depending on the file system
- `exploit.php.`
	- Some components will strip or ignore trailing whitespaces, dots, and such
- `exploit%2Ephp`
	- Checks to see if the URL encoding is decoded server-side instead of input validation
- `exploit.asp;.jpg` or `exploit.asp%00.jpg`
	- Add semicolons or URL-encoded null byte characters before the file extension. If validation is written in a high-level language like PHP or Java, but the server processes the file using lower-level functions in C/C++, for example, this can cause discrepancies in what is treated as the end of the filename
- Try using multibyte unicode characters, which may be converted to null bytes and dots after unicode conversion or normalization. Sequences like `xC0 x2E`, `xC4 xAE` or `xC0 xAE` may be translated to `x2E` if the filename parsed as a UTF-8 string, but then converted to ASCII characters before being used in a path.
- `exploit.p.phphp`
	- Even when `.php` is stripped, another `.php` remains

### Other
- It might try to verify the dimensions of the image and reject the file if it has not dimensions, so they may need to be spoofed
- JPEG files always begin with the bytes `FF D8 FF`.
	- This is a much more robust way of validating the file type, but even this isn't foolproof. Using special tools, such as ExifTool, it can be trivial to create a polyglot JPEG file containing malicious code within its metadata.
- XSS or SVG images from an HTML file that don't execute
	- Note that due to same-origin policy restrictions, these kinds of attacks will only work if the uploaded file is served from the same origin to which you upload it.

---

## Business Logic Vulnerabilities

#### Excessive trust in client-side controls
- Change price after capturing request

#### High-level logic vulnerabilities 
If you can get negative items in the cart, you can make the total from them just negative enough that the store credit you have is enough to buy the more expensive itme
- This lab keeps you from checking out with negative money, but doesn't keep you from have negative value in the cart, allowing you to have negative value for some items bringing down the cost of another  

#### Flawed enforcement of business rules
- In this lab you alternate between coupon codes since it only blocks the most recent one (I didn't see the one at the bottom)


#### Low-level logic flaw
- Add so many l33t jackets that the *total sale in the cart becomes negative and try to raise it just to the level of your gift card* with other items
- Requires noticing that a max of 99 can be added at a time, and requires doing that over 100 times to reach a negative number


#### Lab: Inconsistent handling of exceptional input
*exploit a logic flaw in its account registration process to gain access to administrative functionality*
- Lab requires getting admin access by registering with a `dontwannacry.com` email when you don't have access to that inbox
- You have to try and notice that the email field when registering an account is limited to 255 characters, so if you register a normal account, but the address' 255th character ends with `dontwannacry.com`, you can register with a different email, but it will validate as a `dontwannacry.com` email. 
- Ex:
```HTTP
POST /register HTTP/2
Host: 0ac6006b03ca782082a0a1ec00360007.web-security-academy.net
Cookie: session=WlNWxqLZvSRXOKTwPg2DRPRrA3QHPgl4
Content-Length: 159

...

csrf=GPsp2gI1Sj0cEHCbYcDgSQq68EXQEgZm&username=pop8&email=123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234pop8@dontwannacry.com.exploit-0a8b00100348785e82baa026016f00ce.exploit-server.net&password=password
```

#### Lab: Weak isolation on dual-use endpoint

```HTTP
POST /my-account/change-password HTTP/2
Host: 0a0c00310345474982ac018900f3002e.web-security-academy.net
Cookie: session=LiI4QKuTTVXZM9IOogYo0KMZW6VulL2X

...

csrf=b3MLWQqvcNqvpdW6aaSDF1UQKVlYejoN&username=wiener&current-password=peter&new-password-1=peter1&new-password-2=peter1
```
- This is the request showing a change of password for the `wiener` user, but you can change the user to `administrator` and simply remove the `current-password` parameter before changing it
- **Remove the current-password parameter**


#### Lab: Insufficient workflow validation
This lab makes flawed assumptions about the sequence of events in the purchasing workflow, use them to buy a "Lightweight l33t leather jacket"
- Walk through the purchasing workflow with a cheaper item, and see a confirmation request coming after the initial `POST` request. 
```http
GET /cart/order-confirmation?order-confirmed=true HTTP/2
Host: 0ab900810409374684b99f6e0032001f.web-security-academy.net
Cookie: session=ngsesHrLEhAqh7XqzJU2GCjanpviqaQ4
...
```
No parameters needed, just a confirmation. Fill the cart back up with the jacket and then send a `GET` request to this endpoint. 


#### Lab: Authentication bypass via flawed state machine
*This lab makes flawed assumptions about the sequence of events in the login process. To solve the lab, exploit this flaw to bypass the lab's authentication, access the admin interface, and delete the user `carlos`.*

- The key thing here is that there is a `/role-selector` page after the initial `POST` request to the `/login` page. *If you simply drop this request, the role defaults to administrator*. Note that you must **drop the request**. It doesn't work to simply browse away before selecting. 

#### Lab: Infinite money logic flaw
This one allowed unlimited gift card purchases with 30% off, but they were only worth 10$ at a time, so the trick was to use a [macro to automate](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money). Steps below:
- Study the proxy history and notice that you redeem your gift card by supplying the code in the `gift-card` parameter of the `POST /gift-card` request.
- Click **Settings** in the top toolbar. The **Settings** dialog opens.
- Click **Sessions**. In the **Session handling rules** panel, click **Add**. The **Session handling rule editor** dialog opens.
- In the dialog, go to the **Scope** tab. Under **URL scope**, select **Include all URLs**.
- Go back to the **Details** tab. Under **Rule actions**, click **Add** > **Run a macro**. Under **Select macro**, click **Add** again to open the **Macro Recorder**.
- Select the following sequence of requests:
```
POST /cart
POST /cart/coupon 
POST /cart/checkout 
GET /cart/order-confirmation?order-confirmed=true 
POST /gift-card
````
- Then, click **OK**. The **Macro Editor** opens.
- In the list of requests, select `GET /cart/order-confirmation?order-confirmed=true`. Click **Configure item**. In the dialog that opens, click **Add** to create a custom parameter. Name the parameter `gift-card` and highlight the gift card code at the bottom of the response. Click **OK** twice to go back to the **Macro Editor**.
- Select the `POST /gift-card` request and click **Configure item** again. In the **Parameter handling** section, use the drop-down menus to specify that the `gift-card` parameter should be derived from the prior response (response 4). Click **OK**.
- In the **Macro Editor**, click **Test macro**. Look at the response to `GET /cart/order-confirmation?order-confirmation=true` and note the gift card code that was generated. Look at the `POST /gift-card` request. Make sure that the `gift-card` parameter matches and confirm that it received a `302` response. Keep clicking **OK** until you get back to the main Burp window.
- Send the `GET /my-account` request to Burp Intruder. Make sure that **Sniper attack** is selected.
- In the **Payloads** side panel, under **Payload configuration**, select the payload type **Null payloads**. Choose to generate `412` payloads.
- Click on **Resource pool** to open the **Resource pool** side panel. Add the attack to a resource pool with the **Maximum concurrent requests** set to `1`. Start the attack.
- When the attack finishes, you will have enough store credit to buy the jacket and solve the lab.

#### Lab: Authentication bypass via encryption oracle
This one was pretty complicated, it involved realizing that a notification cookie in a response to the `/post/comment` endpoint was being set, along with a "Invalid email address:" string to the `/post?postId=<x>` endpoint. So the goal was to: 
- Decrypting a `stay-logged-in` cookie by including a `GET /post?postId=<x>` request
- Noticing the format is `<username>:<timestamp>`
- Changing the format to `administrator:<timestamp>`
- Checking that this works by encrypting it in a  `POST /post/comment` request
	- and decrypting it in a `GET /post?postId=<x>` request
- Recognizing that we can't use that on its own because it is also including the "Invalid email address:" string (23 bytes)
- Sending the `notification` cookie to decoder, removing the 23 bytes
- Realizing it must be a multiple of 16
- Changing the cookie to `xxxxxxxxxadministrator:<timestamp>` then re-encrypting it (9 x's)
- Sending that to decoder and removing 32 bytes (23 + 9 `x`'s)
- Using that as the `stay-logged-in` cookie to request `/admin` page
- **Note the the decoder process involves URL-decoding, then base64 decoding and vice-versa**

Full steps [here](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-encryption-oracle), but it may be specific to this lab tbh

---
