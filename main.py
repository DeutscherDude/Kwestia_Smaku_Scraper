from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from psql_connection import get_session
from sqlalchemy import insert
import pandas as pd


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

session = get_session()

while next_found:
    for i in range(0, len(elements)):
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(elements[i])).click()
            # elements[i].click()
        except TimeoutException:
            print('Element could not be found')
            break
        try:        
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='group-przepis field-group-div']")))
        except TimeoutException:
            print('Element could not be found')
            break    
            
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        name = soup.find('div', attrs={'itemprop': 'name'})

        driver.implicitly_wait(2)
        rec_ing = soup.find('div', class_='group-skladniki field-group-div')
        rec_ing = rec_ing.get_text()
        
        prep = soup.find('div', class_='group-przepis field-group-div')
        prep = prep.get_text()
        
        tag = soup.find('ul', class_='field field-name-field-przepisy field-type-taxonomy-term-reference field-label-hidden')
        tag = tag.get_text()

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
    except NoSuchElementException:
        next_found = False


df = pd.DataFrame({'tags': tags, 'recipes': recipes, 'ingredients': ingredients, 'preparation': preparation})
df.to_csv('przepisy.csv', index=False, encoding='utf-8')
