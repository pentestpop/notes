---
layout: default
title: "Race Conditions"
parent: "Web Application"
nav_order: 27
---

## Background

A **process** is a program in execution, consisting of executable code, memory, state, and threads.
- A **thread** is a lightweight unit of execution that shares memory and instructions with its process.
- A TCP/UDP port can only be tied to one process; a process can have many threads handling requests concurrently.

A race condition occurs when two threads collide and produce unexpected results — for example, two withdrawals on the same account where the second starts before the first updates the balance. These are **Time-of-Check to Time-of-Use (TOCTOU)** vulnerabilities.

**HTTP/2 advantage**: HTTP/2 supports single-packet multi-requests, allowing multiple requests to be stacked in the same TCP packet — eliminating network jitter and making race conditions easier to trigger reliably compared to HTTP/1.1.

---

## Basics

There are many variations of this kind of attack, including:
- Redeeming a gift card multiple times
- Rating a product multiple times
- Withdrawing or transferring cash in excess of your account balance
- Reusing a single CAPTCHA solution
- Bypassing an anti-brute-force rate limit

Limit overruns are a subtype of so-called "time-of-check to time-of-use" (TOCTOU) flaws. 


*in practice there are various uncontrollable and unpredictable external factors that affect when the server processes each request and in which order* even if you send them all at the same time

## Task 1

1. Capture the request to apply the coupon
2. Send to repeater
3. Create a new group tab
4. Duplicate tab ~20 times
5. Send request in parallel
6. Observe that the coupon has been applied multiple times

## Detecting and exploiting limit overrun race conditions with Turbo Intruder

Turbo Intruder is a BApp extension 
**Requires HTTP/2**

1. Set the `engine=Engine.BURP2` and `concurrentConnections=1` configuration options for the request engine.
2. When queueing your requests, group them by assigning them to a named gate using the `gate` argument for the `engine.queue()` method.
3. To send all of the requests in a given group, open the respective gate with the `engine.openGate()` method.

```python
def queueRequests(target, wordlists): 
	engine = RequestEngine(endpoint=target.endpoint, 
							concurrentConnections=1, 
							engine=Engine.BURP2 ) 
							
	# queue 20 requests in gate '1' 
	for i in range(20): 
		engine.queue(target.req, gate='1') 
	# send all requests in gate '1' in parallel 
	engine.openGate('1')
	
```

For more details, see the `race-single-packet-attack.py` template provided in Turbo Intruder's default examples directory.

## Task 2

`POST /login` -> **Extensions > Turbo Intruder > Send to turbo intruder**.
- make sure to highlight the password filed for that it is marked as a payload position with `%s`
- From the drop-down menu, select the `examples/race-single-packet-attack.py` template
	- Need the passwords suggested
- They give this as an example:

```python
def queueRequests(target, wordlists): 
	# as the target supports HTTP/2, use engine=Engine.BURP2 and concurrentConnections=1 for a single-packet attack 
	engine = RequestEngine(endpoint=target.endpoint, 
							concurrentConnections=1, 
							engine=Engine.BURP2 ) 
	# assign the list of candidate passwords from your clipboard 
	passwords = wordlists.clipboard 
	# queue a login request using each password from the wordlist 
	# the 'gate' argument withholds the final part of each request until engine.openGate() is invoked 
	for password in passwords: 
		engine.queue(target.req, password, gate='1') 
	# once every request has been queued 
	# invoke engine.openGate() to send all requests in the given gate simultaneously 
	engine.openGate('1') 
	
def handleResponse(req, interesting): 
	table.add(req)
```
- this takes the list of passwords from the clipboard

Run the attack, look for a **302** response
If it doesn't find one, try again with only the passwords that weren't tested because of the lockout


## Hidden multi-step sequences
A single request may initiate an entire multi-step sequence behind the scenes, we'll call those **sub-steps**

If you can identify *one or more HTTP requests that cause an interaction with **the same data***, you can potentially abuse these sub-states to expose time-sensitive variations of the kinds of logic flaws that are common in multi-step workflows. This enables race condition exploits that **go far beyond limit overruns**.
- Ex: Flawed multi-factor authentication (MFA) workflows that let you perform the first part of the login using known credentials, then navigate straight to the application via forced browsing, effectively bypassing MFA entirely.
- I think I watched Kevin and Paul do this 

![](/assets/Images/Race%20Conditions/Predict_probe_prove.png)
- Check "Smashing the state machine: The true potential of web race conditions by PortSwigger Research"

1. **Predict**
	1. Is it worth testing (valuable)
	2. Are there collisions? Two or more requests have to trigger operations on the same record
![](/assets/Images/Race%20Conditions/same_record.png)
2. **Probe**
	1. Benchmark how the application works under normal conditions
		1. Group requests and `Send group in sequence (separate connection)`
		2. Then send same group of requests at once using the **single-packet attack** (`Send group in parallel`) or Turbo Intruder
	2. Anything can be a clue, look for deviations or even changes in behavior afterward or different email contents
	3. On ***Professional***, you can use the **Trigger race conditions** custom action. This sends parallel requests with a single click, removing the need to manually create and group tabs in Repeater. 

3. **Prove**
	1. Understand and clean (trim superfluous requests, tune the timing)
	2. Explore impact - think of it as structural weakness, look for chains and variations, don't stop at the first exploit
		1. You might run into weird or unfamiliar behavior, the highest impact might be hard to find


## Multi-endpoint race conditions
Sending requests to multiple endpoints at the same time.
- Classic logic flaw in online stores where you add an item to your basket or cart, pay for it, then add more items to the cart before force-browsing to the order confirmation page
- you can potentially **add more items** to your basket during the race window **between when the payment is validated and when the order is confirmed**.

**Issues**: trying to line up windows for each request
- Delays introduced by network architecture
	- Like when front-end server establishes connection to back end
- Delays introduced by endpoint-specific processing
	- Depending on what operations are triggered on different endpoints

**Workarounds**:
- *Differentiate between back-end delays and endpoint-specific*
	- Back-end don't always interfere with race conditions bc they delay requests equally
	- **Warm with inconsequential requests** to smooth out processing times
		- Ex: add a get request to the beginning of the group before processing everything as a single request in parallel
	- If this doesn't work, it's a **back-end** delay

## Task 3 
Essentially this required me to:
1. Have a gift card
2. buy a gift card - send the checkout request to repeater in a Group1
3. Add a jacket to the cart - send that request to repeater in a Group1
4. Send Group1 together *in parallel*

I needed to have the gift card in the cart before checking out so that it didn't say the cart was empty before adding the jacket. Also it took a few tries. 

## Abusing Rate or Resource Limits
![](/assets/Images/Race%20Conditions/rate_or_resource_limits.png)


## Single-endpoint race conditions
Parallel request with different values to the same endpoint can create issues
- Ex: Sending password reset requests for a hacker user and victim user at the same time can provide the hacker with the victim's reset token 
- *This does need to happen in exactly the right order which requires luck or multiple attempts*
- Email address confirmations or any email-based operations are generally a good target for this 


## Task 4
You are trying to change your email to carlos@ginandjuice.shop
- Create an email change request to your email
- Create an email change request to the carlos email
- Send them both in parallel
- Click the link in the email
- Refresh and go to the admin panel

## Session-based locking mechanisms
If you notice that all of your requests are being processed sequentially, try sending each of them using a different session token.
- This is to get around the session locking, which is pretty good at masking trivial vulnerabilities

## Partial construction race conditions
Many applications create objects in multiple steps, which may introduce a temporary middle state in which the object is exploitable.
- Ex: New user registration might create user and set their API key in two separate SQL statements, leaving a tiny window where the user exists but their API key is not initialized
- Might be able to use the API key as `null` in that time
	- For passwords instead, the hashed is used so it needs to match the `null` value
- Ruby on Rails lets you pass in arrays and non-string data structures using non-standard syntax:

```
GET /api/user/info?user=victim&api-key[]= HTTP/2 
Host: vulnerable-website.com
```


## Time-sensitive attacks

Maybe not a race condition, but a situation where precise timing makes a difference
Ex: Timestamps used instead of cryptographically secure randoms strings to generate security tokens
- Password reset token randomized using a timestamp, so it might be possible to trigger two resets for two different users which use the same token. Requires you to time the requests so they generate the same timestamp.

## Task 5
Basically what's happening here is that the password reset function has some kind of limitation where requests are processed one at a time based on the Cookie (and the csrf token which seems based on the cookie), but you can send two requests in parallel if they have different cookies and csrf tokens. The key is to send a request to the `GET /forgot-password` endpoint, but remove the Cookie so you get assigned a new one. So the steps are:
1. Capture a `POST forgot-password` request for the `wiener` user
	1. This will have its own Cookie and CSRF token
2. Capture a `GET /forgot-password` request and remove the Cookie before sending
	1. This generates a new cookie which *must be copied*
3. Then send a `POST /forgot-password` request as carlos, **capturing first and replacing the cookie** and capture it
4. Send both in Repeater as parallel which will send you an email
5. This email link includes the wiener user in the URL, but that's ok
6. Submit a new password and capture the POST request
7. Change the user in the paramters from wiener to carlos, but don't worry about changing it in the URL
8. Then login as carlos with this password



































