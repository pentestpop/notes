---
title: "Authentication Vulnerabilties"
parent: "Authentication and Session"
grand_parent: "4 - Web_Application"
nav_order: 1
layout: default
---

# Authentication Vulnerabilties

Sometimes if you log back in correctly, you can reset a timeout
- Create a list with the correct creds every x times
- Set `Resouce Pool` in Intruder with **Maximum concurrent requests** set to `1`. 
- `sed 'a\correct_password' pass.txt > pass1.txt`
- `sed 'a\peter' pass.txt > pass1.txt` to copy user list over and over

It may be that lockout only happens to legit account, so a lockout error may be evidence that an account is real

Basic auth: `Authorization: Basic base64(username:password)`

### MFA
Ex: 
1. Notice that in the `POST /login2` request, the `verify` parameter is used to determine which user's account is being accessed.
2. Send the `GET /login2` request to Repeater. Change the value of the `verify` parameter to `carlos` and send the request. This ensures that a temporary 2FA code is generated for Carlos.
3. Go to the login page and enter your username and password. Then, submit an invalid 2FA code.
4. Send the `POST /login2` request to Intruder.
5. In Burp Intruder, set the `verify` parameter to `carlos` and add a payload position to the `mfa-code` parameter. Brute-force the verification code.

### Other
Always look at reset password and password change mechanisms, it's possible that they can be done out of order or that the error codes will tell you something
- Current password and then two new passwords where entering two different new passwords only throws a code if the current password is correct
