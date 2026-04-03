---
layout: default
title: "ORM Injection"
parent: "Web Application"
nav_order: 23
---

### ORM
Object-relational mapping (ORM) is a programming technique that facilitates data conversion between incompatible systems using object-oriented programming languages. It allows developers to interact with a database using the programming language's native syntax, making data manipulation more intuitive and reducing the need for extensive SQL queries.

Commonly used ORM Frameworks:
- Doctrine (PHP)
- Hibernate (Java)
- SQLAlchemy (Python)
- Entity Framework (C#)
- Active Record (Ruby on Rails)

### SQL Injection vs ORM Injection
SQL injection and ORM injection are both techniques used to exploit vulnerabilities in database interactions, but they target different levels of the stack:

- **SQL injection**: Targets raw SQL queries, allowing attackers to manipulate SQL statements directly. This is typically achieved by injecting malicious input into query strings. The injection part in the following query, `OR '1'='1`, always evaluates to true, allowing attackers to bypass authentication:

 `SELECT * FROM users WHERE username = 'admin' OR '1'='1';`

- **ORM injection**: Targets the ORM framework, exploiting how it constructs queries from object operations. Attackers manipulate the ORM’s methods and properties to influence the resulting SQL queries.
  
 `$userRepository->findBy(['username' => "admin' OR '1'='1"]);`

![](/assets/Images/ORM%20Injection/ORMinjection1.png)


CRUD Operations set up differently based on the Framework in use. 
![](/assets/Images/ORM%20Injection/Screenshot%202024-11-26%20at%208.45.11%20PM.png)


For example, Laravel uses the `.env` file to store environment variables such as database credentials. 


### Identifying Injection
Techniques for Testing ORM Injection:
- Manual code review
- Automated scanning
- Input validation testing
- Error-based testing
- Others:
	- Checking the cookies which can use unique naming conventions. 
	- Also HTTP headers
	- URL structure. 

![](/assets/Images/ORM%20Injection/Screenshot%202024-11-26%20at%208.45.11%20PM.png)

Check with similar techniques to SQL Injection such as `'`'s. Essentially ORM is used to help abstract SQL queries, making them more secure from SQLi, so for any exploitation to work it needs to be misconfigured or under-configured. 