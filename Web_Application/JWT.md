---
layout: default
title: "JWT"
parent: "Web Application"
nav_order: 18
---


JSON web tokens (**JWTs**) are a *standardized format for sending cryptographically signed JSON data between systems*.

A JWT consists of 3 parts: **a header, a payload, and a signature**. These are each separated by a dot, as shown in the following example:

```JSON
eyJraWQiOiI5MTM2ZGRiMy1jYjBhLTRhMTktYTA3ZS1lYWRmNWE0NGM4YjUiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTY0ODAzNzE2NCwibmFtZSI6IkNhcmxvcyBNb250b3lhIiwic3ViIjoiY2FybG9zIiwicm9sZSI6ImJsb2dfYXV0aG9yIiwiZW1haWwiOiJjYXJsb3NAY2FybG9zLW1vbnRveWEubmV0IiwiaWF0IjoxNTE2MjM5MDIyfQ.SYZBPIBg2CRjXAJ8vCER0LA_ENjII1JakvNQoP-Hw6GG1zfl4JyngsZReIfqRvIAEi5L4HV0q7_9qGhQZvy9ZdxEJbwTxRs_6Lb-fZTDpW6lKYNdMyjw45_alSCZ1fypsMWz_2mTpQzil0lOtps5Ei_z7mM7M8gCwe_AGpI53JxduQOaB5HkT5gVrv9cKu9CsW5MS6ZbqYXpGyOG5ehoxqm8DL5tFYaW3lB50ELxi0KsuTKEbD0t5BCl0aCR2MBJWAbN-xeLwEenaqBiwPVvKixYleeDQiBEIylFdNNIMviKRgXiYuAvMziVPbwSgkZVHeEdF5MQP1Oe2Spac-6IfA
```

The **header and payload** parts of a JWT are just *base64url-encoded JSON objects*. The header contains metadata about the token itself, while the payload contains the actual "claims" about the user. For example, you can decode the payload from the token above to reveal the following claims:

```JSON
{ 
	"iss": "portswigger", 
	"exp": 1648037164, 
	"name": "Carlos Montoya", 
	"sub": "carlos", 
	"role": "blog_author", 
	"email": "carlos@carlos-montoya.net", 
	"iat": 1516239022 
}
```

The signature is the important part of the security 

[jwt.io](jwt.io) Is a helpful debugger. 

JWTs aren't really used as a standalone entity. The JWT spec is extended by both the **JSON Web Signature (JWS)** and **JSON Web Encryption (JWE)** specifications, which define concrete ways of actually implementing JWTs.
- a JWT is usually either a JWS or JWE token

## JWT header parameters
- `jwk` (JSON Web Key) - provides an embedded JSON object representing the key
- `jku` (KSON Web Key Set URL) - Provides a URL from which servers can fetch a set of keys containing the correct key
- `kid` (Key ID) - Provides an ID that servers can use to identify the correct key in cases where there are multiple keys (such as for different kinds of data)
	- Arbitrary string of developer choosing, may even be the name of a file
	- *This can make it prone to directory traversal*, perhaps not to be read, but to be  `/dev/null` -> especially dangerous if it's **symmetric** because we know we can sign will `NULL`, but the contents of another file would work as well
- `cty` (Content Type) - can be used to declare a media type, *usually omitted*, but underlying library **may support it anyway**. 
	- Point would be to change to `text/xml` or `application/x-java-serialized-object`, enabling new vectors for XXE or deserialization attacks
- `x5c` (X.509) - sometimes used to pass the X.509 public key cert of the key used to sign the JWT, can be used to inject self-signed certs, similar to the `jwk` header injection. Parsing these certs can introduce new vulns. 



## JWT Attacks
*JWT attacks involve a user sending modified JWTs to the server in order to achieve a malicious goal*

### Lab1
You can decode the payload of the JWT in base64 and simply change the username to `administrator`

## No Signature
```JSON
{ 
	"alg": "HS256", 
	"typ": "JWT"
}
``` 

`typ` can be set to none
**In the actual solution, it was change the `alg` to `none`**
This removed the last section of the JWT, though it did still end in a `.`

## Weak Key
`hashcat -a 0 -m 16500 eyJraWQiOiIxZjA0ZTY4Yi1iNTMzLTQ2ZDYtOGI1Zi02Y2UyMGExZWVlOWYiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc2NDE5Mjk2NSwic3ViIjoid2llbmVyIn0.phYMSXkl0cq_o_uD-u-6Amve7mduEFl8lDZUOIFB3iY jwt.secrets `

## Labs
### Lab: JWT authentication bypass via jwk header injection
From instructions: *lab uses a JWT-based mechanism for handling sessions. The server supports the `jwk` parameter in the JWT header. This is sometimes used to embed the correct verification key directly in the token. However, it fails to check whether the provided key came from a trusted source.*
- This means we can use the JWT editor extensions to fiddle with it and change to the `administrator` user

![](/assets/Images/JWT%20-%20JSON%20Web%20Tokens/jwk_header_injection.png)

- I generated a key from the JWT Editor Extension page then use that to `Sign` from this repeater tab, then copied and pasted it into the request. These were the steps that needed to be followed:
1. Go to the **JWT Editor Keys** tab in Burp's main tab bar.
2. Click **New RSA Key**.
3. In the dialog, click **Generate** to automatically generate a new key pair, then click **OK** to save the key. Note that you don't need to select a key size as this will automatically be updated later.
4.  `GET /admin` and change the value of the `sub` claim to `administrator`.
5. At the bottom of the **JSON Web Token** tab, click **Attack**, then select **Embedded JWK**. When prompted, select your newly generated RSA key and click **OK**.
6. In the header of the JWT, observe that a `jwk` parameter has been added containing your public key.

Apparently I did not need to worry about the key id or the key size. Also I did need to click **Attack** rather than Sign or Encrypt. 

### Lab: JWT authentication bypass via jku header injection
[info](https://www.vaadata.com/blog/jwt-json-web-token-vulnerabilities-common-attacks-and-security-best-practices/)

This lab requires two steps:
1. Generating the key and hosting on the epxloit server
2. Fiddling with the JWT in the JWT Editor tab

To generate the token and host it
1. Click **New RSA Key**.
2. In the dialog, click **Generate** to automatically generate a new key pair, then click **OK** to save the key. Note that you don't need to select a key size as this will automatically be updated later.
3. In the browser, go to the exploit server and replace the contents of the **Body** section with an empty JWK Set as follows:
```JSON
{ 
	"keys": [ 
	] 
}
```
4.  Back on the JWT Editor Keys tab, right-click on the entry for the key that you just generated, then select **Copy Public Key as JWK**.
5. Paste the JWK into the `keys` array on the exploit server, then store the exploit. The result should look something like this:
```JSON
{ 
	"keys": [ 
		{ 
			"kty": "RSA", 
			"e": "AQAB", 
			"kid": "893d8f0b-061f-42c2-a4aa-5056e12b8ae7", 
			"n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw" 
		} 
	]
}
```
- (I most got here, but I just copied and pasted the whole key rather than public key as JWK)

To fix the JWT:
1. Go back to the `GET /admin` request in Burp Repeater and switch to the extension-generated JSON Web Token message editor tab.
2. **Replace the current value of the `kid` parameter** with the `kid` of the JWK that you uploaded to the exploit server.
3. **Add a new `jku` parameter to the header of the JWT**. Set its value to the URL of your JWK Set on the exploit server.
4. Change the value of the `sub` claim to `administrator`.
5. At the bottom of the tab, click **Sign**, then select the RSA key that you generated in the previous section.
6. Make sure that the **Don't modify header** option is selected, then click OK. The modified token is now signed with the correct signature.
7. Use this cookie to get to `/admin` and delete carlos

(I correctly added the jku, but I failed to change the `kid`, and I never clicked `Sign`)

### Lab: JWT authentication bypass via kid header path traversal
1. Go to the JWT Editor tab and generate **New Symmetric Key**
2. Replace the generated value for the k property with a Base64-encoded null byte (**AA\==**). Note that this is just a workaround because the JWT Editor extension won't allow you to sign tokens using an empty string.
3. Back in Repeater, change the value of the `kid` parameter to a path traversal sequence pointing to the `/dev/null` file such as `../../../../../../../dev/null`. 
	1. Don't forget to change the value of the `sub` claim to `administrator`. 
4. **Sign** (Don't modify header) -> *The modified token is now signed using a null byte as the secret key.* 
5. Use that Cookie, go to admin panel, delete carlos, done. 
