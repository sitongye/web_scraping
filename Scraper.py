from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import random
import lxml

class Scraper:
    def __init__(self, url, agent=None):
        self.url = url
        self.site = ""
        self.proxy_pool = ["207.74.82.103:3128"]
        #["154.12.18.{}:65007".format(str(i)) for i in range(21,46)]
        print(self.proxy_pool)

        self.rotate_proxy = False
        self.driver = None
        if agent is not None:
            self.agent = agent
        else:
            self.agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Safari/537.36"}
        self.headers = requests.utils.default_headers()
        self.headers.update(self.agent)

    def _get_request(self, url="default", rotate_proxy=False):
        if self.rotate_proxy is True:
            rotate_proxy = True
        if url == "default":
            url = self.url
        if rotate_proxy is True:
            if self.proxy_pool is not None:
                random.shuffle(self.proxy_pool)
                for i in range(len(self.proxy_pool)):
                    proxy = self.proxy_pool[i]
                    print(proxy)
                    response = requests.get(url, proxies={"http": proxy, "https": proxy})
                    if response.status_code == 200:
                        print("response sucessful!")
                        return response
                    else:
                        print("this one doesnt work")
                        continue
                return "all proxies failed"
        else:
            response = requests.get(url, headers=self.headers)
            if response.status_code==200:
                print("successful request!")
                return response
            else:
                return "fail to connect"

    def _get_soup(self, request, parser="html.parser"):
        soup = BeautifulSoup(request.content, parser)
        return soup

class foot_locker(Scraper):

    def check_stock(self, soup):
        content_url = \
        soup.find("div", {"class": "fl-load-animation", "data-ajaxcontent": "fl-productDetailsSizeSelection"})[
            "data-ajaxcontent-url"]
        print(content_url)
        new_response = self._get_request(url=content_url)
        new_soup = self._get_soup(new_response)
        sizes = new_soup.find_all("button", {"class": r'\"fl-product-size--item\"'})
        for size in sizes:
            print(re.sub(r"\\n", "", size.get_text()))
        return sizes

    def add_to_cart(self, proxy=True):
        if proxy is True:
            PROXY = "165.227.173.87:40001"
            webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
                "httpProxy": PROXY,
                "ftpProxy": PROXY,
                "sslProxy": PROXY,
                "proxyType": "MANUAL",

            }
        self.driver = webdriver.Firefox(executable_path='./geckodriver')
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10)
        select_size_button = self.driver.find_elements_by_xpath(r'// *[ @ id = "fitanalytics_sizecontainer"] / section[1] / div / button[1]')[0]

        self.driver.execute_script("arguments[0].click();", select_size_button)
        WebDriverWait(self.driver, 10)
        add_to_cart_button = self.driver.find_elements_by_xpath(r'//*[@id="add-to-cart-form"]/div/div[3]/div/div[7]/button')[0]
        self.driver.execute_script("arguments[0].click();", add_to_cart_button)
def test():
    new_shoe = foot_locker("https://www.footlocker.de/en/p/nike-air-force-1-07-x-3m-men-shoes-118661?v=314108366304")
    response = new_shoe._get_request()
    print(response)
    soup = new_shoe._get_soup(response)
    content_url = soup.find("div", {"class":"fl-load-animation", "data-ajaxcontent":"fl-productDetailsSizeSelection"})["data-ajaxcontent-url"]
    print(content_url)
    new_response = new_shoe._get_request(url=content_url)
    new_soup = new_shoe._get_soup(new_response)
    sizes = new_soup.find_all("button",{"class":r'\"fl-product-size--item\"'})
    for size in sizes:
        print(re.sub(r"\\n","",size.get_text()))
    new_shoe.add_to_cart()
    WebDriverWait(new_shoe.driver, 100)
if __name__ == "__main__":
    test()
