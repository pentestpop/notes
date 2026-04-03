---
layout: default
title: "Authentication"
parent: "Web Application"
nav_order: 4
---

# Authentication Vulnerabilities

---

## Brute Force & Enumeration

### Basic Auth
Basic auth encodes credentials as `base64(username:password)` in the `Authorization` header:
```
Authorization: Basic base64(username:password)
```

**Burp Intruder approach for Basic Auth:**
1. Send request to Intruder
2. Right-click base64 section → Convert Selection → Base64 → Decode
3. Select both `user:password` and add position markers
4. Load password list
5. Add Payload Processing rule: `Add prefix` (the username + `:`)
6. Add Payload Processing rule: `Base64-encode`
7. In Payload Encoding section, remove `=` character (base64 padding causes issues)

**Hydra for Basic Auth:**
```
hydra -l user -P wordlist.txt target http-get /protected-path
```

### Bypassing Lockout
- Lockout only applies to the legitimate account — a lockout error may confirm the username is real
- If re-authenticating correctly resets a timeout, interleave the correct password in the list:
  ```
  sed 'a\correct_password' pass.txt > pass1.txt
  ```
- Set Burp Intruder Resource Pool → Maximum Concurrent Requests = 1

### MFA Bypass
1. Notice the `verify` parameter in `POST /login2` controls which user's 2FA is checked
2. Send `GET /login2` to Repeater; change `verify` to target username to generate their code
3. Log in as yourself, then send `POST /login2` to Intruder
4. Set `verify` = target username; brute-force the `mfa-code` field (typically 4-6 digits)

### Password Reset / Change
- Always test reset and password change mechanisms — they can be triggered out of order
- Password change errors may reveal if the current password was correct:
  - If entering two different new passwords only throws an error when the current password IS correct, it leaks validity

---

## JWT Authentication Attacks

JWTs are three base64url-encoded parts separated by dots: `header.payload.signature`

Decode with [jwt.io](https://jwt.io) or CyberChef.

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJhZG1pbiI6MX0.q8De2tfygNpldMvn581XHEbVzobCkoO1xXY4xRHcdJ8
```

Via API:
```
curl -H 'Content-Type: application/json' -X POST -d '{"username":"user","password":"password1"}' http://TARGET/api/v1.0/example1
```

### Attack 1: Remove Signature
- Submit the token without the last segment (signature)
- If it works, signature validation is not enforced — modify payload freely

### Attack 2: Algorithm = None
- Change the `alg` field in the header to `None` (or `none`, `NONE`)
- Use CyberChef: decode base64url → modify JSON → encode back to base64url
- Remove the signature part entirely

### Attack 3: Crack the Secret
```
hashcat -m 16500 -a 0 jwt_token.txt jwt.secrets.list
# jwt.secrets.list: https://raw.githubusercontent.com/wallarm/jwt-secrets/master/jwt.secrets.list
```
The token format for hashcat is the full base64 JWT string (`eyJ...eyJ...SIGNATURE`). Note: `nth` does not identify JWTs.

After cracking, recreate the token with the known secret in jwt.io.

### Attack 4: Algorithm Confusion (RS256 → HS256)
If the server uses RS256, you may be able to downgrade to HS256 using the public key as the HMAC secret:
1. Get the public key (starts with `ssh-rsa...`)
2. Change `alg` to `HS256` in the header
3. Sign with the public key as the HMAC secret

### Attack 5: Token Reuse Across Services
- In SSO environments, check if a token obtained for one service works on another
- Check if the token has no expiration set — persistent tokens can be reused indefinitely

### JWT Security Notes
- Sensitive data should NOT be stored in JWT claims (encoded, not encrypted)
- JWT security is only as strong as its signature/secret
- Always verify token expiration
- In SSO, the `audience` claim ensures a token is only used on the intended app

---

## Session Management

### Cookie vs Token-Based Sessions

| | Cookie-Session | Token-Based |
|---|---|---|
| Transmission | Automatically sent by browser | Must be added as header via JS |
| Protection | Cookie attributes (HttpOnly, Secure, SameSite) | No automatic protections |
| CSRF | Vulnerable (browser auto-attaches cookies) | Protected (not auto-attached) |
| Decentralized apps | Difficult (domain-locked) | Works well |

### Session Attack Vectors
- **Session fixation** — attacker sets session ID before victim logs in
- **Session hijacking** — steal session cookie via XSS, network sniffing
- **Insecure direct session references** — predictable or sequential session IDs

---

## OAuth 2.0 Attack Vectors

### Grant Type Overview

**Authorization Code Grant** (most secure, most common):
- Flow: user authenticates → authorization code → exchange for access token
- Pentesting: code leakage during redirect, CSRF on redirect_uri, PKCE bypass, open redirect

**Implicit Grant** (legacy, deprecated for SPAs):
- Token issued directly in URL fragment
- Pentesting: token in URL visible to history/logs/referrers, token theft via XSS

**Resource Owner Password Credentials (ROPC):**
- Client receives user credentials directly
- Pentesting: credential exposure, MitM, insecure storage, excessive privileges

**Client Credentials Grant:**
- Machine-to-machine, no user involved
- Pentesting: hardcoded client secrets in source code, over-permissioned scopes, reused secrets

### General OAuth Attack Vectors
1. **Token Replay** — capture and reuse access/refresh tokens
2. **Scope Mismanagement** — test if tokens grant more permissions than intended
3. **Token Lifetime** — check for overly long lifetimes or misconfigured refresh tokens
4. **Revocation** — verify tokens are invalidated after logout
5. **Open Redirect** — exploitable `redirect_uri` parameters for phishing
6. **CSRF on Authorization Endpoint** — hijack authorization codes via crafted redirect
