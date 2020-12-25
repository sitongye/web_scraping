from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

headers = requests.utils.default_headers()
headers.update({"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 13421.89.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"})
driver = webdriver.Firefox(executable_path='./geckodriver')
r = requests.get("https://www.snipes.com/c/shoes/sneaker")
try:
    snipe_soup= BeautifulSoup(r.content, "html.parser")
except:
    print("unable to parse")
#print(snipe_soup.prettify())
text = snipe_soup.find_all("div", {"class": "b-product-sort-bar l-row"})[0].find("div", {"class": "b-grid-quantity l-col-4 l-col-md-3 js-grid-quantity"}).get_text()
all_amount = re.compile(r"\d+").findall(text)[0]
print(all_amount)
driver.get("https://www.snipes.com/c/shoes/sneaker?sz="+all_amount)
try:
    showall_soup = BeautifulSoup(driver.page_source, "html.parser")
except:
    print("parsing error")

all_sneakers = showall_soup.find_all("div",{"class": "b-product-grid-tile js-tile-container"})
#    except:
#        print("fail to connect")
#        pass
def get_href(shoe_tag):
    return shoe_tag.find_all("span", {"class": "b-product-tile-link js-product-tile-link"})[0]["href"]
print(len(all_sneakers))

def get_productdetail(shoepage_soup):
    product_detail = {}
    product_detail["shoe_title"] = re.sub(r"\n", "  ", shoepage_soup.find_all("div", {"class":"js-target"})[0].get_text()).strip()
    product_detail["shoe_price"] = re.sub(r"\n", "", shoepage_soup.find("span",{"class": "b-product-tile-price-item"}).get_text()).strip()
    product_detail["shoe_image"] = shoepage_soup.find("img", {"class": "b-dynamic_image_content"})["data-src"]
    orderable_class = "js-pdp-attribute-tile b-size-value js-size-value b-swatch-circle b-swatch-value b-swatch-value--selectable b-swatch-value--orderable"
    in_store_only_class = "js-pdp-attribute-tile b-size-value js-size-value b-swatch-circle b-swatch-value b-swatch-value--selectable b-swatch-value--in-store-only"
    sold_out_class = "js-pdp-attribute-tile b-size-value js-size-value b-swatch-circle b-swatch-value b-swatch-value--selectable b-swatch-value--sold-out"
    product_detail["in_stock_sizes"] = [re.sub(r"\n","",x.get_text()) for x in shoepage_soup.find_all("span",{"class": orderable_class})]
    product_detail["in_store_only_sizes"] = [re.sub(r"\n", "", x.get_text()) for x in
                                        shoepage_soup.find_all("span", {"class": in_store_only_class})]
    product_detail["sold_out_sizes"] = [re.sub(r"\n", "", x.get_text()) for x in
                                        shoepage_soup.find_all("span", {"class": sold_out_class})]
    return product_detail



for i in range(len(all_sneakers)):
    dataframe = pd.DataFrame(columns=["product", "price", "shoe_image", "orderable_size", "sold_out_size"])
    shoe_link = "https://www.snipes.com"+get_href(all_sneakers[i])
    shoepage = BeautifulSoup(requests.get(shoe_link).content, "html.parser")
    try:
        product_dict = get_productdetail(shoepage)
        print(product_dict)
        dataframe = dataframe.append({"product": product_dict["shoe_title"],
                                  "price": product_dict["shoe_price"],
                                  "shoe_image": product_dict["shoe_image"],
                                  "orderable_size": product_dict["in_stock_sizes"],
                                  "sold_out_size": product_dict["sold_out_sizes"]}, ignore_index=True)
    except:
        print(shoe_link)
        continue
dataframe.to_csv("allshoes.csv")



#<span data-attr-value="39"
# class="js-pdp-attribute-tile b-size-value js-size-value b-swatch-circle b-swatch-value b-swatch-value--selectable b-swatch-value--in-store-only b-swatch-value--selected">39</span>






