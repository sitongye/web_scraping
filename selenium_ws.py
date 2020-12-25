from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


driver = webdriver.Firefox(executable_path='./geckodriver')
#driver.get('https://www.snipes.com/')

driver.get('https://www.snipes.com/')
WebDriverWait(driver,timeout=1000).until(lambda a: a.find_elements_by_class_name('slide'))
slide = driver.find_elements_by_class_name('slide')[0]
brands = slide.find_elements_by_tag_name("a")
print(len(brands))
for brand in brands:
    brand_html = brand.get_attribute("href")
    #print(brand_html)
    brand_soup = BeautifulSoup(brand_html, parser="html.parser")
    print(brand_soup.prettify())
