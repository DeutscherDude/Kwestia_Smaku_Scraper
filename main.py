from argparse import Action
from json.tool import main
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd


chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()
driver.get('https://www.kwestiasmaku.com/')

recipes = []
tags = []
ingredients = []
preparation = []

el_to_hover = driver.find_element(By.XPATH, "//div[@class='main-menu']//a[text()[contains(.,'Posiłki')]]")  

hover = ActionChains(driver)
hover.move_to_element(el_to_hover).click().perform()

next_found = True
elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")

while next_found:
    for i in range(0, len(elements)):

        elements[i].click()
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        name = soup.find('div', attrs={'itemprop': 'name'})

        driver.implicitly_wait(2.5)
        rec_ing = soup.find('div', class_='group-skladniki field-group-div')
        rec_ing = rec_ing.get_text()
        ingredients.append(rec_ing)
        prep = soup('div', class_='group-przepis field-group-div')
        preparation.append(prep)
        
        tag = soup.find('ul', class_='field field-name-field-przepisy field-type-taxonomy-term-reference field-label-hidden')
        tag = tag.get_text()
        tags.append(tag)

        driver.back()
        driver.implicitly_wait(3)
        
        elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")
    try:
        driver.find_element(By.XPATH, '//li[@class="next last"]').click()
        driver.implicitly_wait(1.5)
        elements = driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']")
    except NoSuchElementException:
        print('End of list')
        next_found = False


df = pd.DataFrame({'tags': tags, 'recipes': recipes, 'ingredients': ingredients, 'preparation': preparation})
df.to_csv('przepisy.csv', index=False, encoding='utf-8')
