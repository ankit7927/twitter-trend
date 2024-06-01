from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pymongo, uuid, socket, json, random
from datetime import datetime

def scrapper(username_inp, password_inp):
    trending_topics = []

    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument('--proxy-server=213.19.123.178:229')
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

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

    trending_section = wait.until(EC.presence_of_element_located((By.XPATH, "//section[@aria-labelledby='accessible-list-1']")))

    trending_items = trending_section.find_elements(By.XPATH, ".//div[@data-testid='trend']")[:5]

    for item in trending_items:
        topic = item.text.split('\n')[1]
        trending_topics.append(topic.replace("#", ""))

    driver.quit()
    return trending_topics

def insert_into_db(trending_topics:list):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
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
    credentials = []
    with open("credentials.json","r") as file:
        credentials = json.loads(s=file.read())

    cred = random.choice(credentials)
    username= cred["username"]
    password= cred["password"]
    trending_topics = scrapper(username_inp=str(username), password_inp=str(password))

    insert_into_db(trending_topics=trending_topics)