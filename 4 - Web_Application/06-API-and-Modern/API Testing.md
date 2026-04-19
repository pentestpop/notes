Find out: 
- The input data the API processes, including both compulsory and optional parameters.
- The types of requests the API accepts, including supported HTTP methods and media formats.
- Rate limits and authentication mechanisms.

`/api/books and /api/books/mystery` are separate endpoints
- Check the base path so if you find `/api/books/mystery/ghost` check `/api/books/mystery`

Burp Scanner to crawl the API

Test all potential methods: 
- `GET` - Retrieves data from a resource.
- `PATCH` - Applies partial changes to a resource.
- `OPTIONS` - Retrieves information on the types of request methods that can be used on a resource.
- Ex:
	- `GET /api/tasks` - Retrieves a list of tasks.
	- `POST /api/tasks` - Creates a new task.
	- `DELETE /api/tasks/1` - Deletes a task.

Change `Content-Type` header to see if that does anything - can disclose info, bypass, flawed defenses, take advantage of differences in processing logic (secure with JSON but susceptible to injection attacks when dealing with JSON)

### Mass Assignment 
Mass assignment (also known as *auto-binding*) can inadvertently create hidden parameters. It occurs when software frameworks automatically bind request parameters to fields on an internal object. Mass assignment may therefore result in the application supporting parameters that were never intended to be processed by the developer.
- Ex: Send PATCH request with found parameter - one valid and one invalid, if it behaves differently, this may suggest that the invalid value impacts the query logic, but the valid value doesn't (and can maybe be updated by the user). 

### Server-side parameter pollution
Involves internal APIs that aren't accessible from the internet, but a website embeds user input into an internal API without adequate encoding for the purposes of: 
- Overriding existing parameters
- Modifying application behavior
- Accessing unauthorized data
- To test for server-side parameter pollution in the query string, place query syntax characters like `#`, `&`, and `=` in your input and observe how the application responds.
	- Ex: 
		- Consider a vulnerable application that enables you to search for other users based on their username. When you search for a user, your browser makes the following request:
			- `GET /userSearch?name=peter&back=/home`
		- To retrieve user information, the server queries an internal API with the following request:
			- `GET /users/search?name=peter&publicProfile=true`
	- You can use a URL-encoded `#` character to attempt to truncate the server-side request. To help you interpret the response, you could also add a string after the `#` character.
		- For example, you could modify the query string to the following:
			- `GET /userSearch?name=peter%23foo&back=/home`
		- The front-end will try to access the following URL:
			- `GET /users/search?name=peter#foo&publicProfile=true`
			- If it returns peter, the query may have been truncated, but if it returns an error, then it may not have been
			- If you can truncate it, then the maybe `publicProfile` doesn't need to be set to true, and you can find non-public profiles
	- Try adding a URL-encoded `&` (`%26`), to add another parameter, you can fuzz for these
	- You can also add a second (`GET /userSearch?name=peter%26name=carlos&back=/home`)
		- PHP parses last parameter only
		- ASP.NET combines both ("peter,carlos')
		- Node.js / express parses the first parameter only

In [this](https://portswigger.net/web-security/learning-paths/api-testing/api-testing-testing-for-server-side-parameter-pollution-in-the-query-string/api-testing/server-side-parameter-pollution/lab-exploiting-server-side-parameter-pollution-in-query-string#) example:
- Check HTTP history and note that the forgot-password endpoint and the `/static/js/forgotPassword.js` script are related
- Note that you can add a second parameter using & (`%26`) which gives a different error than terminating query with # (`%23`)
- `username=administrator%26field=x%23` gives "Invalid field" so you can fuzz in Intruder for `x` and find email
- **But** - `/static/js/forgotPassword.js` also shows a `/forgot-password?reset_token=${resetToken}`
	- So we need to get the reset token
- `username=administrator%26field=reset_token%23`
- That gets you the reset token and then you can go to `/forgot-password?reset_token=${resetToken}`

#### Structured Data Formats
- When you edit your name, your browser makes the following request:
	- `POST /myaccount name=peter`
- This results in the following server-side request:
	- `PATCH /users/7312/update {"name":"peter"}`
- You can attempt to add the `access_level` parameter to the request as follows:
	- `POST /myaccount name=peter","access_level":"administrator`
- If the user input is added to the server-side JSON data without adequate validation or sanitization, this results in the following server-side request:
	- `PATCH /users/7312/update {name="peter","access_level":"administrator"}`
	- This may result in the user `peter` being given administrator access.
- If client-side input is encoded: 
	- `POST /myaccount {"name": "peter\",\"access_level\":\"administrator"}`
	- Becomes: `PATCH /users/7312/update {"name":"peter","access_level":"administrator"}`


*To prevent server-side parameter pollution, use an allowlist to define characters that don't need encoding, and make sure all other user input is encoded before it's included in a server-side request. You should also make sure that all input adheres to the expected format and structure.*

