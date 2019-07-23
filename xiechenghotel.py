from utils.make_sessions import create_session, create_webdriver
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from utils.sqlbackends import session_scope
from utils.models import XieCheng
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def produce_data(se):
    ss = se.split("\n")
    res = {}
    for item in ss:
        tem = item.split(":")
        if len(tem) == 2:
            res[tem[0]] = tem[1].strip()
        else:
            res[tem[0]] = ""
    return res


url_home = "https://hotels.ctrip.com"
url = "https://hotels.ctrip.com/hotel/chongqing4/location"
hotel_api = "https://hotels.ctrip.com/Domestic/Tool/AjaxHotelList.aspx"

driver = create_webdriver()


def start():
    driver.get("https://www.ctrip.com/?AllianceID=1068271&sid=1955227&ouid=&app=0101F00")
    driver.get(url)
    jumppage = driver.find_element_by_xpath('//*[@id="txtpage"]')
    jumppage.clear()
    jumppage.send_keys("84")
    jump = driver.find_element_by_xpath('//*[@id="page_info"]/div[2]/input[2]')
    ActionChains(driver).click(jump).perform()
    r = driver.page_source
    count = 0
    while count < 720:
        soup = BeautifulSoup(r, "lxml")
        uls = soup.find_all("ul", class_="hotel_item")
        with session_scope() as sess:
            for item in uls:
                res = {}
                h2 = item.find("h2", class_="hotel_name")
                a = h2.a
                name = a["title"]
                res["hotelName"] = name
                href = a["href"]
                href = url_home + href
                res["url"] = href
                p = item.find("p", class_="hotel_item_htladdress")
                address = p.text.strip()
                index = address.find("地图")
                res["address"] = address[: index]
                span = item.find("span", class_="J_price_lowList")
                price = span.text
                res["price"] = price
                score = item.find_all("span", class_="hotel_value")
                if score:
                    score = score[0].text
                    res["score"] = score
                xc = XieCheng(**res)
                qxc = sess.query(XieCheng).filter(XieCheng.url == res["url"]).first()
                if not qxc:
                    sess.add(xc)
                    print(res)
        pagediv = soup.find_all("div", class_="c_page_list layoutfix")[0]
        current = None
        for item in pagediv.find_all("a"):
            if item["href"] and item["href"] == "javascript:;":
                current = int(item.text)
                print("当前到第{}页".format(item.text))
                break
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="downHerf"]')))
        time.sleep(2)
        npage = driver.find_element_by_xpath('//*[@id="downHerf"]')
        ActionChains(driver).click(npage).perform()
        r = driver.page_source


if __name__ == "__main__":
    start()
