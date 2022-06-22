from requests import Session
from threading import Thread
from queue import Queue
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from models import Recipe
from psql_connection import get_engine_from_settings, get_meta_data, get_session
from models import Recipe, recreate_database


def scrap_recipy_name(driver: webdriver, content: str, x_path: str) -> str:
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='group-przepis field-group-div']")))
        soup = BeautifulSoup(content, 'html.parser')
        rec_name = soup.find('div', attrs={'itemprop': 'name'})
        rec_name = rec_name.get_text()
        return rec_name
    except (TimeoutException, NoSuchElementException):
        return "Error"

def scrap_recipy_ingredients(driver: webdriver, content: str, x_path: str) -> str:
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, x_path)))
        soup = BeautifulSoup(content, 'html.parser')
        rec_ing = soup.find('div', class_='group-skladniki field-group-div')
        rec_ing = rec_ing.get_text()
        return rec_ing
    except (TimeoutException, NoSuchElementException):
        return "Error"

def scrap_recipy_preparation(driver: webdriver, content: str, x_path: str) -> str:
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, x_path)))
        soup = BeautifulSoup(content, 'html.parser')
        rec_prep = soup.find('div', class_='group-przepis field-group-div')
        rec_prep = rec_prep.get_text()
        return rec_prep
    except (TimeoutException, NoSuchElementException):
        return "Error"

def scrap_recipy_tags(driver: webdriver, content: str, x_path: str) -> str:
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, x_path)))
        soup = BeautifulSoup(content, 'html.parser')
        rec_tags = soup.find('div', class_='group-kategorie field-group-div')
        rec_tags = rec_tags.get_text()
        return rec_tags
    except (TimeoutException, NoSuchElementException):
        return "Error"

def threaded_scrap_recipy_name(driver: webdriver,  entry_queue: Queue, exit_queue: Queue) -> str:
    while True: 
        try:
            content, xpath = entry_queue.get()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            soup = BeautifulSoup(content, 'html.parser')
            rec_name = soup.find('div', attrs={'itemprop': 'name'})
            rec_name = rec_name.get_text()
            exit_queue.put(rec_name)
        except (TimeoutException, NoSuchElementException):
            exit_queue.put('Error')

def threaded_scrap_recipy_ingredients(driver: webdriver, entry_queue: Queue, exit_queue: Queue) -> str:
    while True:
        try:
            content, xpath = entry_queue.get()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            soup = BeautifulSoup(content, 'html.parser')
            rec_ing = soup.find('div', class_='group-skladniki field-group-div')
            rec_ing = rec_ing.get_text()
            exit_queue.put(rec_ing)
        except (TimeoutException, NoSuchElementException):
            exit_queue.put('Error')

def threaded_scrap_recipy_preparation(driver: webdriver,entry_queue: Queue, exit_queue: Queue) -> str:
    while True:
        try:
            content, xpath = entry_queue.get()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            soup = BeautifulSoup(content, 'html.parser')
            rec_prep = soup.find('div', class_='group-przepis field-group-div')
            rec_prep = rec_prep.get_text()
            exit_queue.put(rec_prep)
        except (TimeoutException, NoSuchElementException):
            exit_queue.put('Error')

def threaded_scrap_recipy_tags(driver: webdriver,entry_queue: Queue, exit_queue: Queue) -> str:
    while True:
        try:
            content, xpath = entry_queue.get()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            soup = BeautifulSoup(content, 'html.parser')
            rec_tags = soup.find('div', class_='group-kategorie field-group-div')
            rec_tags = rec_tags.get_text()
            exit_queue.put(rec_tags)
        except (TimeoutException, NoSuchElementException):
            exit_queue.put('Error')

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()
driver.get('https://www.kwestiasmaku.com/przepisy/posilki')

recipes = []
tags = []   
ingredients = []
preparation = []

next_found = True
elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")

k = 0

db = get_engine_from_settings()
Session = get_session()
session = Session()
recreate_database(db)

send_queues = [Queue() for i in range(4)]
receive_queues = [Queue() for i in range(4)]

threads = [
    Thread(target=threaded_scrap_recipy_name, args=(driver, send_queues[0], receive_queues[0]), daemon=True),
    Thread(target=threaded_scrap_recipy_ingredients, args=(driver, send_queues[1], receive_queues[1]), daemon=True),
    Thread(target=threaded_scrap_recipy_preparation, args=(driver, send_queues[2], receive_queues[2]), daemon=True),
    Thread(target=threaded_scrap_recipy_tags, args=(driver, send_queues[3], receive_queues[3]), daemon=True),
]

for thread in threads:
    thread.start()

while next_found:
    for i in range(0, len(elements)):
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(elements[i])).click()
        except (TimeoutException, NoSuchElementException):
            print('Element could not be found')
            break
        except StaleElementReferenceException:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(elements[i])).click()
        try:        
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='group-przepis field-group-div']")))
        except StaleElementReferenceException:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='group-przepis field-group-div']")))
        except (TimeoutException, NoSuchElementException):
            print('Element could not be found')
            break
            
        content = driver.page_source

        for queue, x_path in zip( send_queues, [
            "//div[@class='group-przepis field-group-div']",
            "//div[@class='group-przepis field-group-div']",
            "//div[@class='group-przepis field-group-div']",
            "//div[@class='group-kategorie field-group-div']"
        ]) : 
            queue.put((content, x_path))

        results = [queue.get() for queue in receive_queues]
        
        # rec_name = scrap_recipy_name(driver, content, "//div[@class='group-przepis field-group-div']")
        # rec_ing = scrap_recipy_ingredients(driver, content, "//div[@class='group-przepis field-group-div']")
        # prep = scrap_recipy_preparation(driver, content, "//div[@class='group-przepis field-group-div']")
        # tag = scrap_recipy_tags(driver, content, "//div[@class='group-kategorie field-group-div']")

        recipy = Recipe(
            name=results[0],
            ingredients=results[1],
            preparation=results[2],
            tags=results[3]
        )

        session.add(recipy)
        session.commit()

        driver.back()
        
        elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")
        
        print(f"Beep {k}")
        k = k + 1

    try:
        driver.find_element(By.XPATH, '//li[@class="next last"]').click()
        elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")
    except (NoSuchElementException, TimeoutException):
        next_found = False
