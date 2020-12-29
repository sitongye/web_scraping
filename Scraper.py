from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import Proxy
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import random
import lxml
import asyncio
from proxybroker import Broker
from fake_useragent import UserAgent

ua = UserAgent()
ua.update()

class Scraper:
    def __init__(self, url, rotate_proxy=False, agent=ua.random):
        print(agent)
        self.url = url
        self.site = ""
        if rotate_proxy is True:
            self.proxy_pool = self._populate_proxy(7)
        else:
            self.proxy_pool = []
        # ["154.12.18.{}:65007".format(str(i)) for i in range(21,46)]
        print(self.proxy_pool)
        self.rotate_proxy = rotate_proxy
        self.driver = None
        self.agent = {"User-Agent": agent}
        self.headers = requests.utils.default_headers()
        self.headers.update(self.agent)

    def _populate_proxy(self, num=5):
        proxy_pool = []

        async def show(proxies):
            while True:
                proxy = await proxies.get()
                if proxy is None: break
                proxy_pool.append(proxy)
                print('Found proxy: %s' % proxy)

        proxies = asyncio.Queue()
        broker = Broker(proxies)
        tasks = asyncio.gather(
            broker.find(types=["HTTPS"], limit=10),
            show(proxies))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)
        return [str(t.host) + ":" + str(t.port) for t in proxy_pool]

    def _get_request(self, url="default", rotate_proxy=False):
        if self.rotate_proxy is True:
            rotate_proxy = True
        if url == "default":
            url = self.url
        if rotate_proxy is True:
            loop = 0
            while loop < 6:
                if len(self.proxy_pool) != 0:
                    proxy = self.proxy_pool.pop()
                    print(proxy)
                    try:
                        response = requests.get(url, proxies={"http": proxy, "https": proxy})
                        if response.status_code == 200:
                            print("response sucessful!")
                            return response
                    except:
                        continue
                else:
                    self.proxy_pool = self._populate_proxy(6)
                    loop += 1
                    print("last batch doesnt work")
            return "all failed"
        else:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
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
        sizes = new_soup.find_all("button", {"class": r'\"fl-product-size--item\"',"type":re.compile(r".+EU.+")})
        for size in sizes:
            print(re.sub(r"\\n", "", size.get_text()))
        return sizes


    def open_browser(self, with_proxy=False):
        profile = webdriver.FirefoxProfile()
        if with_proxy is True:
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.socks", "127.0.0.1")
            profile.set_preference("network.proxy.socks_port", 9050)

            profile.update_preferences()

        self.driver = webdriver.Firefox(profile, executable_path='./geckodriver')
        self.driver.get(self.url)
        WebDriverWait(self.driver, 20)

    def add_to_cart(self):
        select_size_button = self.driver.find_elements_by_xpath(r'//*[@id="fitanalytics_sizecontainer"]/section[1]/div/button[10]')[0]
        self.driver.execute_script("arguments[0].click();", select_size_button)
        wait = WebDriverWait(self.driver, 10)
        element = wait.until()
        add_to_cart_button = self.driver.find_elements_by_xpath(r'//*[@id="add-to-cart-form"]/div/div[3]/div/div[7]/button')[0]
        self.driver.execute_script("arguments[0].click();", add_to_cart_button)
        WebDriverWait(self.driver, 30)

    def check_out(self):
        #WebDriverWait(self.driver, 30)
        cart_amount =self.driver.find_element_by_class_name("fl-header--mini-cart--items-count").text
        print(cart_amount)
        if int(cart_amount) == 1:
            upright_cart = self.driver.find_elements_by_xpath(r'//*[@id="flcomponentheaderfull"]/div/div[1]/span[1]/div/div[1]')[0]
            self.driver.execute_script("arguments[0].click();", upright_cart)
            jetzt_kaufen = self.driver.find_elements_by_xpath(r'//*[@id="flcomponentheaderfull"]/div/div[1]/span[1]/div/div[2]/div/div[2]/div[7]/div[1]/a')[0]
            if jetzt_kaufen.is_displayed() is True:
                self.driver.execute_script("arguments[0].click();", jetzt_kaufen)
                EC.presence_of_element_located((By.ID, "myDynamicElement"))
            FORTFAHREN = self.driver.find_elements_by_xpath(r'/html/body/main/div/div[2]/div[1]/div[2]/div/div/div/a')[0]
            #FORTFAHREN = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, r'/html/body/main/div/div[2]/div[1]/div[2]/div/div/div/a')))
            if FORTFAHREN.is_displayed() is True:
                self.driver.execute_script("arguments[0].click();", FORTFAHREN)
            element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, r"/html/body/main/div/div[2]/div/ol/li[1]"))
            )
            # fill in billing info
            Vorname = self.driver.find_element_by_id("billing_FirstNamecheckout-billing-address-form")
            Vorname.send_keys('Sitong')
            Nachname = self.driver.find_element_by_id("billing_LastName")
            Nachname.send_keys('Ye')
            Adresse = self.driver.find_element_by_id("predict_checkout-billing-address-form")
            Adresse.send_keys('Kastellstr. 6, 53227, Bonn')
            Tel = self.driver.find_element_by_id("billing_PhoneHomecheckout-billing-address-form")
            Tel.send_keys('015174211571')
            Day = self.driver.find_element_by_id("Day")
            Day.send_keys('04')
            Month = self.driver.find_element_by_id("Month")
            Month.send_keys('11')
            Year = self.driver.find_element_by_id("Year")
            Year.send_keys('1994')
            email = self.driver.find_element_by_id("fl-login-input-email-billing")
            email.send_keys('sitongye94@outlook.com')
            passwort = self.driver.find_element_by_id("fl-input-password-checkout-address-panel")
            passwort.send_keys("Nike941104!")
            WebDriverWait(self.driver, 20)
            self.browser.find_element_by_class("fl-checkbox--label fl-checkbox--label__top-aligned").click()
            WebDriverWait(self.driver, 3)
            self.browser.find_element_by_class("fl-checkbox--label").click()

            JETZTKAUFEN = self.driver.find_element_by_xpath("/html/body/main/div/div[2]/form/div/div[5]/button[2]")
            JETZTKAUFEN.click()
        else:
            return False
            WebDriverWait(self.driver, 5)



def test(check_stock_test=True,
         populate_proxy_test=True,
         add_to_cart_test=False
         ):
    new_shoe = foot_locker("https://www.footlocker.de/de/p/nike-air-force-1-07-x-3m-men-shoes-118661?v=314108366304",
                           rotate_proxy=False,
                           agent="Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.14; rv:85.0) Gecko/20100101 Firefox/85.0")
    response = new_shoe._get_request()
    print(response)
    soup = new_shoe._get_soup(response)
    if check_stock_test is True:
        new_shoe.check_stock(soup)
        new_shoe.open_browser()
        new_shoe.add_to_cart()
        if input("continue?")=="y":
            new_shoe.check_out()
        else:
            new_shoe.add_to_cart()
    WebDriverWait(new_shoe.driver, 100)


if __name__ == "__main__":
    test()


