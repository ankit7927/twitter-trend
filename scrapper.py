from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pymongo, uuid, socket
from datetime import datetime
import os

def scrapper(username_inp, password_inp, proxy):
    trending_topics = []

    proxy_set = {
        "httpProxy": proxy,
        "ftpProxy": proxy,
        "sslProxy": proxy,
        "noProxy": None,
        "proxyType": "manual"
    }

    chrome_options = Options()
    chrome_options.set_capability("proxy", proxy_set)

    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")

    # for linux server
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # linux chrome service
    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get('https://twitter.com/i/flow/login')

    wait = WebDriverWait(driver, 10)

    username = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete=username]')))

    username.send_keys(username_inp)

    next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[role=button].r-13qz1uu')))

    next_button.click()

    password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[type=password]')))

    password.send_keys(password_inp)

    login_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*=Login_Button]')))

    login_button.click()

    wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Home']")))

    trending_section = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[@aria-label='Timeline: Trending now']")))

    trending_items = trending_section.find_elements(By.XPATH, ".//div[@class='css-175oi2r r-1adg3ll r-1ny4l3l']")

    for item in trending_items[-6:-1]:
        topic = item.text.split('\n')[1]
        trending_topics.append(topic.replace("#", ""))

    driver.quit()
    return trending_topics

def insert_into_db(trending_topics:list, db_string):
    client = pymongo.MongoClient(db_string)
    db = client["x_trends"]
    collection = db["trends"]

    data = {
        "_id": str(uuid.uuid4()),
        "trend1": trending_topics[0] if len(trending_topics) > 0 else None,
        "trend2": trending_topics[1] if len(trending_topics) > 1 else None,
        "trend3": trending_topics[2] if len(trending_topics) > 2 else None,
        "trend4": trending_topics[3] if len(trending_topics) > 3 else None,
        "trend5": trending_topics[4] if len(trending_topics) > 4 else None,
        "datetime": datetime.now(),
        "ip_address": socket.gethostbyname(socket.gethostname())
    }
    print(data)
    collection.insert_one(data)

if __name__ == "__main__":
    DB_URL = os.getenv("DB_URL")
    PROXY_URL = os.getenv("PROXY_URL")
    X_UNAME = os.getenv("X_UNAME")
    X_PWORD = os.getenv("X_PWORD")

    if DB_URL == "" or PROXY_URL == "" or X_PWORD == "" or X_UNAME == "":
        raise Exception("data not provided")

    trending_topics = scrapper(username_inp=X_UNAME, password_inp=X_PWORD, proxy=PROXY_URL)
    insert_into_db(trending_topics=trending_topics, db_string=DB_URL)