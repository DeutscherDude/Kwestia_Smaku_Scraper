from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd


chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get('https://www.kwestiasmaku.com/')
content = driver.page_source

soup = BeautifulSoup(content, 'html.parser')
recipes = []
ingredients = []
preparation = []
food_imgs = []

for element in soup.find_all('div', class_='col col-lg-3'):
    name = element.find('div', attrs={'class': 'views-field-title'})
    if name.text.strip() == '':
        break

    img = element.find('img', attrs={'class': 'img-responsive'})
    recipes.append(name.text.strip())
    food_imgs.append(img['src'])

    print(f"{name} \n-----------------------------------------------------")

    link = driver.find_element(By.XPATH, "//a[contains(text(),'" + name.text.strip() +"')]").click()
    hf_cont = driver.page_source
    sub_soup = BeautifulSoup(hf_cont, 'html.parser')
    rec_ing = sub_soup.find('div', class_='group-skladniki')
    ingredients.append(rec_ing)
    prep = sub_soup('div', class_='group-przepis field-group-div')
    preparation.append(prep)
    driver.back()

print(len(recipes))
print(len(ingredients))

df = pd.DataFrame({'recipes': recipes, 'ingredients': ingredients, 'preparation': preparation, 'food_imgs': food_imgs})
df.to_csv('przepisy.csv', index=False, encoding='utf-8')

    # link = waiter.until(Expected) driver.find_element(By.XPATH, "//a[contains(text(),'" + name.text.strip() +"')]").click()