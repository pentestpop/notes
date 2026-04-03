---
layout: default
title: "Business Logic"
parent: "Web Application"
nav_order: 5
---

### Excessive trust in client-side controls
- Change price after capturing request

### High-level logic vulnerabilities 
If you can get negative items in the cart, you can make the total from them just negative enough that the store credit you have is enough to buy the more expensive itme
- This lab keeps you from checking out with negative money, but doesn't keep you from have negative value in the cart, allowing you to have negative value for some items bringing down the cost of another  

### Flawed enforcement of business rules
- In this lab you alternate between coupon codes since it only blocks the most recent one (I didn't see the one at the bottom)


### Low-level logic flaw
- Add so many l33t jackets that the *total sale in the cart becomes negative and try to raise it just to the level of your gift card* with other items
- Requires noticing that a max of 99 can be added at a time, and requires doing that over 100 times to reach a negative number


### Lab: Inconsistent handling of exceptional input
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

### Lab: Weak isolation on dual-use endpoint

```HTTP
POST /my-account/change-password HTTP/2
Host: 0a0c00310345474982ac018900f3002e.web-security-academy.net
Cookie: session=LiI4QKuTTVXZM9IOogYo0KMZW6VulL2X

...

csrf=b3MLWQqvcNqvpdW6aaSDF1UQKVlYejoN&username=wiener&current-password=peter&new-password-1=peter1&new-password-2=peter1
```
- This is the request showing a change of password for the `wiener` user, but you can change the user to `administrator` and simply remove the `current-password` parameter before changing it
- **Remove the current-password parameter**


### Lab: Insufficient workflow validation
This lab makes flawed assumptions about the sequence of events in the purchasing workflow, use them to buy a "Lightweight l33t leather jacket"
- Walk through the purchasing workflow with a cheaper item, and see a confirmation request coming after the initial `POST` request. 
```http
GET /cart/order-confirmation?order-confirmed=true HTTP/2
Host: 0ab900810409374684b99f6e0032001f.web-security-academy.net
Cookie: session=ngsesHrLEhAqh7XqzJU2GCjanpviqaQ4
...
```
No parameters needed, just a confirmation. Fill the cart back up with the jacket and then send a `GET` request to this endpoint. 


### Lab: Authentication bypass via flawed state machine
*This lab makes flawed assumptions about the sequence of events in the login process. To solve the lab, exploit this flaw to bypass the lab's authentication, access the admin interface, and delete the user `carlos`.*

- The key thing here is that there is a `/role-selector` page after the initial `POST` request to the `/login` page. *If you simply drop this request, the role defaults to administrator*. Note that you must **drop the request**. It doesn't work to simply browse away before selecting. 

### Lab: Infinite money logic flaw
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

### Lab: Authentication bypass via encryption oracle
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

































