
Is there a cached response or does the request need to be forwarded to the origin server?
- Determined by generating a cache key from a variety of other elements using URL path and query parameters (and headers or content type)
- Goal is to inject malicious content into the cache

## Steps

1. Identify endpoint that returns a dynamic response containing sensitive information. 
	1. Review responses in Burp - some sensitive info may not be visible on the rendered page. Focus on endpoints that support the `GET`, `HEAD`, or `OPTIONS` methods (requests that alter the origin server's state are generally not cached).
2. Identify a discrepancy in how the cache and origin server parse the URL path. This could be a discrepancy in how they:
    - Map URLs to resources.
    - Process delimiter characters.
    - Normalize paths.
3. Craft a malicious URL that uses the discrepancy to trick the cache into storing a dynamic response. 
	1. When the victim accesses the URL, their response is stored in the cache. Using Burp, you can then send a request to the same URL to fetch the cached response containing the victim's data. 
	2. Avoid doing this directly in the browser as some applications redirect users without a session or invalidate local data, which could hide a vulnerability.

While testing for discrepancies and crafting a web cache deception exploit, make sure that each request you send has a different cache key. Otherwise, you may be served cached responses, which will impact your test results.
- *Param miner* to automate this 
	- click on the top-level **Param miner > Settings** menu, then select **Add dynamic cachebuster**

`X-Cache` header: 
- Hit - cached response
- Miss - not in the cache
- Dynamic - probably not suitable for caching
- Refresh - cache was outdated

Exploiting static extension - Using discrepancies in how the cache and origin server map the URL path to resources or use delimiters, an attacker may be able to craft a request for a dynamic resource with a static extension that is ignored by the origin server but viewed by the cache.

## URL Mapping
Traditional URL mapping  - represents a direct path to a resource located on the file system. Ex: `http://example.com/path/in/filesystem/resource.html`
- `http://example.com` points to the server.
- `/path/in/filesystem/` represents the directory path in the server's file system.
- `resource.html` is the specific file being accessed.

**REST**-style URLs - abstract file paths into logical parts of the API:
`http://example.com/path/resource/param1/param2`
- `http://example.com` points to the server.
- `/path/resource/` is an endpoint representing a resource.
- `param1` and `param2` are *path parameters used by the server to process the request.*

**Example** - `http://example.com/user/123/profile/wcd.css`
- REST-style URL mapping may interpret this as a request for the `/user/123/profile` endpoint and returns the profile information for user `123`, ignoring `wcd.css` as a non-significant parameter.
- traditional URL mapping may view this as a request for a file named `wcd.css` located in the `/profile` directory under `/user/123`. It interprets the URL path as `/user/123/profile/wcd.css`

To Test: 
- Add an arbitrary path segment to the URL of your target endpoint. 
	- If the response still contains the same sensitive data as the base response, it indicates that the origin server abstracts the URL path and ignores the added segment
- modify the path to attempt to match a cache rule by adding a static extension
	- update `/api/orders/123/foo` to `/api/orders/123/foo.js`
	- If the response is cached: 
		- cache interprets the full URL path with the static extension
		- There is a cache rule to store responses for requests ending in `.js`
	- Try a range (`.css`, `.ico`, `.exe`)
		- You can then craft a URL that returns a dynamic response that is stored in the cache.

Burp Scanner automatically detects web cache deception vulns
- Web Cache Deception Scanner BApp will detect misconfigured web caches

## Lab 1
### Identify a path mapping discrepancy

1. In **Proxy > HTTP history**, right-click the `GET /my-account` request and select **Send to Repeater**.
2. Go to the **Repeater** tab. Add an arbitrary segment to the base path, for example change the path to `/my-account/abc`.
3. Send the request. *Notice that you still receive a response containing your API key*. This indicates that the origin server abstracts the URL path to `/my-account`.
4. Add a static extension to the URL path, for example `/my-account/abc.js`.
5. Send the request. *Notice that the response contains the `X-Cache: miss` and `Cache-Control: max-age=30` headers*. The `X-Cache: miss` header indicates that this response wasn't served from the cache. The `Cache-Control: max-age=30` header suggests that if the response has been cached, it should be stored for 30 seconds.
6. Resend the request within 30 seconds. *Notice that the value of the `X-Cache` header changes to `hit`*. This shows that it was served from the cache. From this, we can infer that the cache interprets the URL path as `/my-account/abc.js` and has a cache rule based on the `.js` static extension. You can use this payload for an exploit.
    

### Craft an exploit

1. In Burp's browser, click **Go to exploit server**.
2. In the **Body** section, craft an exploit that navigates the victim user `carlos` to the malicious URL that you crafted earlier. Make sure to change the arbitrary path segment you added, so the victim doesn't receive your previously cached response:
    `<script>document.location="https://YOUR-LAB-ID.web-security-academy.net/my-account/wcd.js"</script>`
3. Click **Deliver exploit to victim**. When the victim views the exploit, the response they receive is stored in the cache.
4. Go to the URL that you delivered to `carlos` in your exploit:
    `https://YOUR-LAB-ID.web-security-academy.net/my-account/wcd.js`
5. Notice that the response includes the API key for `carlos`. Copy this.
6. Click **Submit solution**, then submit the API key for `carlos` to solve the lab.

*Basically I didn't understand what was happening in this lab. The `Deliver Exploit` button is sending this link to the `carlos` user, so all we actually had to do was to create a cache page using anything.js endpoint and then visit it.*

## Using Delimiter Discrepancies

Delimiters can be used for different things in different frameworks
- `?` most commonly separates path from query
- `;` - use by Java Spring framework to add parameters known as matrix variables (so an origin server using Java Spring will treat it as a delimiter byt others don't)
- `.` - Ruby on Rails framework uses`.` as a delimiter to specify the response format:
	- `/profile` - This request is processed by the default HTML formatter, which returns the user profile information.
	- `/profile.css` - This request is recognized as a CSS extension. There isn't a CSS formatter, so the request isn't accepted and an error is returned.
	- `/profile.ico` - This request uses the `.ico` extension, which isn't recognized by Ruby on Rails. The default HTML formatter handles the request and returns the user profile information. In this situation, if the cache is configured to store responses for requests ending in `.ico`, it would cache and serve the profile information as if it were a static file.
- Encoded characters (ex: `/profile%00foo.js`): 
	- **OpenLiteSpeed** server uses the encoded null `%00` character as a delimiter. An origin server that uses OpenLiteSpeed would therefore interpret the path as `/profile`.
	- Most other frameworks respond with an error if `%00` is in the URL. However, if the cache uses Akamai or Fastly, it would interpret `%00` and everything after it as the path.
- If `/settings/users/list` to `/settings/users/listaaa` are the same, it's not going to work 
- If `/settings/users/list;aaa` gives you `settings/users/list` then `;` is a delimiter 
- **Need to find a delimiter then add a file extension**

## Lab: Exploiting Path Delimiters for Web Cache Deception

- find which delimiters work using [list provided](https://portswigger.net/web-security/web-cache-deception/wcd-lab-delimiter-list)
- add file extension and review headers
- see `miss` then `hit`
- serve `<script>document.location="https://YOUR-LAB-ID.web-security-academy.net/my-account;wcd.js"</script>` to carlos

## Delimiter Decoding Discrepancies 

Consider the example `/profile%23wcd.css`, which uses the URL-encoded `#` character:
- The **origin** server decodes `%23` to `#`. It uses `#` as a delimiter, so it interprets the path as `/profile` and returns profile information.
- The **cache** also uses the `#` character as a delimiter, but doesn't decode `%23`. It interprets the path as `/profile%23wcd.css`. If there is a cache rule for the `.css` extension it will store the response.
OR: Some cache servers may decode the URL and forward the request with decoded characters
- The **cache** server applies the cache rules based on the encoded path `/myaccount%3fwcd.css` and decides to store the response as there is a cache rule for the `.css` extension. It then decodes `%3f` to `?` and forwards the rewritten request to the origin server.
- The **origin** server receives the request `/myaccount?wcd.css`. It uses the `?` character as a delimiter, so it interprets the path as `/myaccount`.
Make sure that you also test encoded non-printable characters, particularly `%00`, `%0A` and `%09`. If these characters are decoded they can also truncate the URL path.

## Other Tips

Common practice to store static resources in specific directories which may be better to target like `static`, `/assets`, `/scripts`, or `/images`

## Normalization Discrepancies
Consider the example `/static/..%2fprofile`:
- An origin server that decodes slash characters and resolves dot-segments would normalize the path to `/profile` and return profile information.
- A cache that doesn't resolve dot-segments or decode slashes would interpret the path as `/static/..%2fprofile`. If the cache stores responses for requests with the `/static` prefix, it would cache and serve the profile information.
- *Note that the origin and cache server represent use different endpoints for the same resource here*
- Test by sending a request to a **non-cacheable** (POST request for example) resource with a *path traversal* sequence and an arbitrary directory at the start of the path (Ex: modify `/profile` to `/aaa/..%2fprofile`)
	- If the response matches the base response and returns the profile information, this indicates that the path has been interpreted as `/profile`. The origin server decodes the slash and resolves the dot-segment.
	- If the response doesn't match the base response, for example returning a `404` error message, this indicates that the path has been interpreted as `/aaa/..%2fprofile`. The origin server either doesn't decode the slash or resolve the dot-segment.

			When testing for normalization, start by encoding only the second slash in the dot-segment. This is important because some CDNs match the slash following the static directory prefix.
			
			You can also try encoding the full path traversal sequence, or encoding a dot instead of the slash. This can sometimes impact whether the parser decodes the sequence.

- You can also add a path traversal sequence after the directory prefix. For example, modify `/assets/js/stockCheck.js` to `/assets/..%2fjs/stockCheck.js`:
	- If the response is no longer cached, this indicates that the cache decodes the slash and resolves the dot-segment during normalization, interpreting the path as `/js/stockCheck.js`. It shows that there is a cache rule based on the `/assets` prefix.
	- If the response is still cached, this may indicate that the cache hasn't decoded the slash or resolved the dot-segment, interpreting the path as `/assets/..%2fjs/stockCheck.js`.

***The goal is to determine the cache rules*** meaning whether they are based on file extensions, directories, or whatever, and whether they are encoded. 

### Exploiting normalization by the cache server
If the cache server resolves encoded dot-segments but the origin server doesn't, you can attempt to exploit the discrepancy by constructing a payload according to the following structure:
`/<dynamic-path>%2f%2e%2e%2f<static-directory-prefix>` (**Double-check this, in the lab it was `%23%2f%2e%2e%2f`, but it could have been `%3f%2f%2e%2e%2f`)
- *When exploiting normalization by the cache server, encode all characters in the path traversal sequence. Using encoded characters helps avoid unexpected behavior when using delimiters, and there's no need to have an unencoded slash following the static directory prefix since the cache will handle the decoding.*
- **To exploit this discrepancy, you'll need to also identify a delimiter that is used by the origin server but not the cache.**
	- If the origin server uses a delimiter, it will truncate the URL path and return the dynamic information.
	- If the cache doesn't use the delimiter, it will resolve the path and cache the response.
- Lab: ``<script>document.location="https://YOUR-LAB-ID.web-security-academy.net/my-account%23%2f%2e%2e%2fresources?wcd"</script>``