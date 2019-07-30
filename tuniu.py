from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from utils.sqlbackends import session_scope
import json
from utils.make_sessions import create_webdriver, create_tuniu_session
from utils.models import XieCheng
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from utils.models import TuNiu


class TuNiuApi:
    # session = create_tuniu_session()

    def __init__(self):
        self.session = create_tuniu_session()

    def driver_get(self):
        url = "http://hotel.tuniu.com/list/300p0s0b0/"
        driver = create_webdriver()
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]/div[2]/div[1]')))
        r = driver.page_source
        soup = BeautifulSoup(r, "lxml")
        h_l = soup.find("div", class_="hotel-list")
        for item in h_l:
            div = item.find("div", class_="nameAndIcon")
            a = div.find("a")
            if a:
                name = a.text
                d_url = "http://hotel.tuniu.com" + a.get("href")
                print(name, d_url)

            a_d = item.find("div", class_="addressInfo")
            if a_d:
                address = a_d.get("title")
                print(address)
            s_d = item.find("div", class_="hotel-brief fl")
            span = s_d.find("span", class_="highlight")
            if span:
                score = span.text
                print(score)
            ps = s_d.find("span", class_="digit")
            if ps:
                price = ps.text
                print(price)

    def get_data(self):
        page = 2
        url = "http://hotel.tuniu.com/ajax/list?search%5BcityCode%5D=300&search%5BcheckInDate%5D=2019-7-30&search%5BcheckOutDate%5D=2019-7-31&search%5Bkeyword%5D=&suggest=&sort%5Bfirst%5D%5Bid%5D=recommend&sort%5Bfirst%5D%5Btype%5D=&sort%5Bsecond%5D=&sort%5Bthird%5D=cash-back-after&page={}&returnFilter=0"
        while True:
            print("the page is {}".format(page))
            r = self.session.get(url.format(page))
            r.encoding = "utf-8"
            # res = json.loads(r.text)
            # print(r.json())
            if not r.json():
                print("now page is {}".format(page))
                break
            data_list = r.json().get("data").get("list")
            for item in data_list:
                res = {}
                res["address"] = item.get("address")
                # print(item.get("name"))
                d_url = "http://hotel.tuniu.com" + item.get("url")
                res["url"] = d_url
                res["shop"] = item.get("name")
                res["score"] = item.get("remarkScore")
                res["price"] = item.get("startPrice")
                res["decorateYear"] = item.get("decorateYear")
                area = json.dumps(item.get("pos"))
                res["area"] = area
                tn = TuNiu(**res)
                with session_scope() as sess:
                    qxc = sess.query(TuNiu).filter(TuNiu.url == res["url"]).first()
                    if not qxc:
                        sess.add(tn)
                        print(res)
            page = page + 1
            time.sleep(0.5)

    def get_phone(self):
        url = "http://hotel.tuniu.com/ajax/getHotelStaticInfo?id={}&checkindate=2019-07-31&checkoutdate=2019-08-01"
        # count = 1
        with session_scope() as sess1:
            tn = sess1.query(TuNiu).filter(TuNiu.phone == None).all()
            for item in tn:
                hotel_id = item.url.split("/")[-1].strip()
                r = self.session.get(url.format(hotel_id))
                # count = count + 1
                temp = r.json()
                item.phone = temp.get("data").get("hotel").get("tel")
                item.district = temp.get("data").get("hotel").get("districtName")
                sess1.commit()
                print(temp.get("data").get("hotel").get("tel"))
                time.sleep(0.5)


if __name__ == "__main__":
    # TuNiuApi().get_data()
    while True:
        try:
            TuNiuApi().get_phone()
            break
        except Exception as e:
            print("输验证码 {}".format(e))
            time.sleep(3)
