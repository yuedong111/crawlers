from bs4 import BeautifulSoup
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.sqlbackends import session_scope
from utils.models import MeiTuanShop
from utils.esbackends import es_search, EsBackends
from selenium.common.exceptions import TimeoutException


def parse_peixun(driver, url):
    ess = es_search("meituan", url)
    if ess[0] and ess[1]:
        pass
    else:
        time.sleep(random.uniform(2, 4))
        res = {}
        res["url"] = url
        driver.get(url)
        try:
            comment_link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="lego-widget-mtpc-shop-head-001-000"]/div/div[1]/div[3]/p[2]/span')))
        except TimeoutException:
            driver.get(url)
            comment_link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="lego-widget-mtpc-shop-head-001-000"]/div/div[1]/div[3]/p[2]/span')))
        comment_link.click()
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        div = soup.find("div", {"class": "mb-flex-1"})
        name = div.find("h1", {"class": "shop-name-title"})
        rank = div.find("div", {"class": "shop-review"})
        ap = div.find("div", class_="shop-address")
        opentime = soup.find_all("div", class_="merchant-intro-item clear-both")
        for item in opentime:
            ti = item.find("div", class_="merchant-intro-title")
            valu = item.find('div', class_="merchant-intro-content")
            if "营业时间" in ti.text:
                opentime = " ".join(valu.text.strip().split())
                res["openTime"] = opentime
        temp = ap.text.split()
        address = temp[0][temp[0].find("：") + 1:]
        phone = temp[1][temp[1].find("：") + 1:]
        res["address"] = address.strip()
        res["phone"] = phone.strip()
        res["score"] = rank.text.strip()
        res["shop"] = name.text.strip()
        ms = MeiTuanShop(**res)
        print(res)
        with session_scope() as sess:
            sess.add(ms)
        if not ess[1] and ess[0]:
            EsBackends("meituan").update_data(id=ess[2], body={"link": url, "status": 1, "date": time.time()})
        if not ess[0]:
            EsBackends("meituan").index_data({"link": url, "status": 1, "date": time.time()})


