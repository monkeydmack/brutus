# Brutus
BRUTUS is a brute force tool that is used to brute force most websites
# Update V 1.3.3
<be>
main-stable working without rockyou2021.txt
  <br>
  main.py working with rockyou2021.txt
<br>
  Added pw logging and progress indicator
<br>
  Working on status with ctrl+p to pause and resume

# Update V 1.3.2
<br>
  Added usage of pw directory and sorted .txt usage the larger the pwlist go first

# Update! v.1.3.1
added arg support **yay**
<br>
  -h, --help            show this help message and exit<br>
  -u USERNAME, --username=USERNAME Choose the username<br>
  --usernamesel=USERNAMESEL Choose the username selector<br>
  --passsel=PASSSEL     Choose the password selector<br>
  --loginsel=LOGINSEL   Choose the login button selector<br>
  --passlist=PASSLIST   Enter the password list directory<br>
  --website=WEBSITE     choose a website<br>
dont worry if you load up the tool without any args youll go to the default wizard!
Also i removed the apt xvfb and pip2 pyvirtualdisplay
## Installation Instructions
```
git clone https://github.com/monkeydmack/brutus.git
python main.py
```

## Requirements
```
pip install selenium
pip install requests
pip install keyboard

```
Chrome and chromedriver are required

(current 'chromedriver' in zip)

You can download chromedriver here: http://chromedriver.chromium.org/downloads
for this fork, create a folder in your C drive called 'webdrivers' and place the executable file inside. If you want to use a different directory, simply change the CHROME_DVR_DIR variable inside the python file.


rockyou2021 pw list torrent in zip
<br>
## How to use (text)
1). Find a website with a login page<br>
2). Inspect element to find the Selector of the username form<br>
3). Do the same for the password field<br>
4). The the login form <br>
5). When Asked put in the username to brute force<br>
6). Watch it go!


