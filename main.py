from argparse import Action
from json.tool import main
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd


def scrape_data(content: webdriver, method: str) -> None:




chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.maximize_window()
driver.get('https://www.kwestiasmaku.com/')

recipes = []
tags = []
ingredients = []
preparation = []
food_imgs = []

el_to_hover = driver.find_element(By.XPATH, "//div[@class='main-menu']//a[text()[contains(.,'Posiłki')]]")  

hover = ActionChains(driver)
hover.move_to_element(el_to_hover).click().perform()

content = driver.page_source

next_found = True

while next_found:
    for element in driver.find_elements(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']"):

        soup = BeautifulSoup(content, 'html.parser')
        name = element.find('div', attrs={'itemprop': 'name'})

        img = element.find('img', attrs={'class': 'img-responsive'})
        recipes.append(name.text.strip())
        food_imgs.append(img['src'])

        link = driver.find_element(By.XPATH, "//div[@class='views-bootstrap-grid-plugin-style']//div[@class='col col-lg-3']//img[@class='img-responsive']").click()
        hf_cont = driver.page_source
        
        rec_ing = soup.find('div', class_='group-skladniki')
        rec_ing = rec_ing.get_text()
        ingredients.append(rec_ing)
        prep = soup('div', class_='group-przepis field-group-div')
        preparation.append(prep)
        
        tag = soup.find('ul', class_='field field-name-field-przepisy field-type-taxonomy-term-reference field-label-hidden')
        tag = tag.get_text()
        tags.append(tag)
        driver.back()
        print(tags)


df = pd.DataFrame({'tags': tags, 'recipes': recipes, 'ingredients': ingredients, 'preparation': preparation, 'food_imgs': food_imgs})
df.to_csv('przepisy.csv', index=False, encoding='utf-8')
