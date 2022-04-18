from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from psql_connection import get_engine_from_settings, get_meta_data, get_session
from sqlalchemy import insert
import pandas as pd


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

k = 1

db = get_engine_from_settings()
meta_data = get_meta_data(db)
recipes_table = meta_data.tables

print(recipes_table)

# session = get_session()


while next_found:
    for i in range(0, len(elements)):
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(elements[i])).click()
        except (TimeoutException, NoSuchElementException):
            print('Element could not be found')
            break
        try:        
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='group-przepis field-group-div']")))
        except (TimeoutException, NoSuchElementException):
            print('Element could not be found')
            break    
            
        content = driver.page_source
        
        rec_name = scrap_recipy_name(driver, content, "//div[@class='group-przepis field-group-div']")
        rec_ing = scrap_recipy_ingredients(driver, content, "//div[@class='group-przepis field-group-div']")
        prep = scrap_recipy_preparation(driver, content, "//div[@class='group-przepis field-group-div']")
        tag = scrap_recipy_tags(driver, content, "//div[@class='group-kategorie field-group-div']")

        recipes.append(rec_name)
        ingredients.append(rec_ing)
        preparation.append(prep)
        tags.append(tag)
        # Add name, rec_ing, prep and tag as a new row to the database

        driver.implicitly_wait(1)
        driver.back()
        
        elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")
        
        k = k + 1
        print(f"Beep {k}")

    try:
        driver.find_element(By.XPATH, '//li[@class="next last"]').click()
        driver.implicitly_wait(1.5)
        elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")
    except (NoSuchElementException, TimeoutException):
        next_found = False


df = pd.DataFrame({'tags': tags, 'recipes': recipes, 'ingredients': ingredients, 'preparation': preparation})
df.to_csv('przepisy.csv', index=False, encoding='utf-8')
