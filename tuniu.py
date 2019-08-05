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
from utils.models import TuNiu, TuNiuAll
from concurrent import futures
import traceback
import datetime


class TuNiuApi:
    # session = create_tuniu_session()
    url = "https://hotel.tuniu.com/ajax/list?search%5Bcity%5D={cid}&search%5BcheckInDate%5D={tomorrow}&search%5BcheckOutDate%5D={aftert}&search%5BcityCode%5D={cid}&page={page}"
    url_home = "https://hotel.tuniu.com"

    def __init__(self):
        self.session = create_tuniu_session()
        self.city = {}
        self.status = False
        self.start_time = time.time()
        with open("config.json", "r", encoding="utf-8") as f:
            lj = json.load(f)
            self.current_city = lj.get("current_city")
            self.current_page = lj.get("current_page")

    def parse_city(self):
        with open("tuniucity.html", "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "lxml")
        div = soup.find("div", {"id": "popCity_box"})
        lis = div.find_all("a")
        for item in lis:
            self.city[item.get("code")] = item.get("title")

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

    def get_all_data(self, cid, city):
        page = 1
        today = datetime.date.today()
        if city != self.current_city:
            return
        while True:
            if city == self.current_city and page == self.current_page:
                self.status = True
            if not self.status:
                page = page + 1
                print("tiaoguo {} {}".format(city, page))
                continue
            print("the page is {}".format(page))
            r = self.session.get(self.url.format(cid=cid, page=page, tomorrow=today + datetime.timedelta(days=1),
                                                 aftert=today + datetime.timedelta(days=2)))
            r.encoding = "utf-8"
            temp = r.json().get("data")
            try:
                total = temp.get("total")
            except Exception as e:
                end_time = time.time()
                if end_time - self.start_time > 100:
                    with open("config.json", "r+", encoding="utf-8") as f:
                        lj = json.load(f)
                    with open("config.json", "w", encoding="utf-8") as f:
                        lj["current_page"] = page
                        lj["current_city"] = city
                        json.dump(lj, f)
                raise e
            if not total:
                print("now page is {}".format(page))
                break
            data_list = temp.get("list")
            for item in data_list:
                res = {}
                res["city"] = city
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
                tn = TuNiuAll(**res)
                with session_scope() as sess:
                    qxc = sess.query(TuNiuAll).filter(TuNiuAll.url == res["url"]).first()
                    if not qxc:
                        sess.add(tn)
                        print(res)
            page = page + 1
            time.sleep(0.5)

    def get_data(self):
        page = 5
        url = "http://hotel.tuniu.com/ajax/list?search%5BcityCode%5D=300&search%5BcheckInDate%5D=2019-8-6&search%5BcheckOutDate%5D=2019-8-7&search%5Bkeyword%5D=&suggest=&sort%5Bfirst%5D%5Bid%5D=recommend&sort%5Bfirst%5D%5Btype%5D=&sort%5Bsecond%5D=&sort%5Bthird%5D=cash-back-after&page={}&returnFilter=0"
        while True:
            print("the page is {}".format(page))
            r = self.session.get(url.format(page))
            r.encoding = "utf-8"
            print(r.json())
            temp = r.json().get("data")
            try:
                total = temp.get("total")
            except Exception as e:
                print(e, temp)
                raise e
            if not total:
                print("now page is {}".format(page))
                break
            data_list = temp.get("list")
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
        url = "http://hotel.tuniu.com/ajax/getHotelStaticInfo?id={}&checkindate=2019-08-1&checkoutdate=2019-08-02"
        count = 1
        # res = []
        with session_scope() as sess2:
            tn = sess2.query(TuNiu).filter(TuNiu.phone == None).all()
            for item in tn:
                hotel_id = item.url.split("/")[-1].strip()
                count = count + 1
                # if count < 39:
                #     continue
                # res.append(hotel_id)
                # try:
                #     with futures.ProcessPoolExecutor(max_workers=10) as executor:
                #         for item in executor.map(self.sub_get_phone, res):
                #             print(item)
                # except KeyboardInterrupt:
                #     exit(0)
                r = self.session.get(url.format(hotel_id))
                # count = count + 1
                try:
                    temp = r.json()
                    item.phone = temp.get("data").get("hotel").get("tel")
                    item.district = temp.get("data").get("hotel").get("districtName")
                    sess2.commit()
                except AttributeError as e:
                    print(hotel_id, e)
                    if "list" in str(e):
                        continue
                    else:
                        raise e
                print(temp.get("data").get("hotel").get("tel"))
                # time.sleep(3)

    def sub_get_phone(self, hotel_id):
        url = "http://hotel.tuniu.com/ajax/getHotelStaticInfo?id={}&checkindate=2019-08-1&checkoutdate=2019-08-02"
        with session_scope() as sess2:
            tn = sess2.query(TuNiu).filter(TuNiu.phone == None).all()
            for item in tn:
                hotel_id1 = item.url.split("/")[-1].strip()
                if hotel_id1 == hotel_id:
                    r = self.session.get(url.format(hotel_id), timeout=3)
                    try:
                        temp = r.json()
                        item.phone = temp.get("data").get("hotel").get("tel")
                        item.district = temp.get("data").get("hotel").get("districtName")
                        print("cha ru titiao {}".format(temp.get("data").get("hotel").get("tel")))
                        sess2.commit()
                        break
                    except Exception as e:
                        print("{}has error {}".format(hotel_id, e))
                        break
                    finally:
                        sess2.commit()

    def start(self):
        self.parse_city()
        for key in self.city.keys():
            if key != 300:
                sa = self.get_all_data(key, self.city[key])


if __name__ == "__main__":
    while True:
        try:
            TuNiuApi().start()
            break
        except Exception as e:
            print("输验证码 {}".format(e))
            time.sleep(2 * 3600)
