from argparse import Action
from json.tool import main
from selenium import webdriver
from selenium.webdriver.common.by import By
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
content = driver.page_source

soup = BeautifulSoup(content, 'html.parser')
recipes = []
ingredients = []
preparation = []
food_imgs = []


el_to_hover = driver.find_element(By.XPATH, "//div[@class='main-menu']//a[text()[contains(.,'Posiłki')]]")

# el_to_hover = driver.find_element(By.XPATH, "//div[@class='main-menu']//span[@class='icon icomoon icon-poradnia']")
hover = ActionChains(driver)
hover.move_to_element(el_to_hover).perform()

main_category = soup.find('a', text='Posiłki', href=True)
# //div[@class="main-menu"]//ul[@class="depth_-1 menu"]//li[@class="has-children"]


# soup.find_all(href=re.compile("elsie"), id='link1')
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>]

for element in soup.find_all('div', class_='col col-lg-3'):
    name = element.find('div', attrs={'class': 'views-field-title'})

    img = element.find('img', attrs={'class': 'img-responsive'})
    recipes.append(name.text.strip())
    food_imgs.append(img['src'])

    link = driver.find_element(By.XPATH, "//div[@class='field field-name-field-zdjecie field-type-image field-label-hidden']").click()
    hf_cont = driver.page_source
    sub_soup = BeautifulSoup(hf_cont, 'html.parser')
    rec_ing = sub_soup.find('div', class_='group-skladniki')
    ingredients.append(rec_ing)
    prep = sub_soup('div', class_='group-przepis field-group-div')
    preparation.append(prep)
    driver.back()

df = pd.DataFrame({'recipes': recipes, 'ingredients': ingredients, 'preparation': preparation, 'food_imgs': food_imgs})
df.to_csv('przepisy.csv', index=False, encoding='utf-8')
