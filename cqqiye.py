# -*- coding: utf-8 -*-
from utils.make_sessions import create_qiye_session, USERAGETNS, COOKIES, create_session, collect_ip
import json
import re
from bs4 import BeautifulSoup
import time
from utils.models import EnterpriseCq
from utils.sqlbackends import session_scope
from utils.esbackends import EsBackends, es_search
import random
from requests.exceptions import ProxyError

patern = re.compile(r"[1-9A-GY]{1}[1239]{1}[1-5]{1}[0-9]{5}[0-9A-Z]{10}")

# ds = get_proxy("https", 500)
# dt = collect_ip()
Proxies = {
    # "http": "http://{}:{}".format(dt[0].get("ip"), dt[0].get("port")),
    "http": "http://{}:{}".format("121.63.198.229", "9999"),
}


def check_proxy(func):
    def decorate(*args, **kwargs):
        while True:
            try:
                res = func(*args, **kwargs)
                break
            except ProxyError:
                pass
        return res

    return decorate


class QiyeCrawl(object):
    qiye_home = "https://gongshang.mingluji.com"
    date_page = "https://gongshang.mingluji.com/chongqing/riqi?page={}"

    def __init__(self):
        self.session = create_qiye_session()
        # self.session.proxies = Proxies

    def parse_date_item(self):
        count = 0
        while True:
            url = self.date_page.format(count)
            try:
                self.parse_page(url)
            except NotFoundException:
                print("日期一共{}页".format(count))
                raise NotFoundException("some item not found!")
                # break
            count = count + 1

    def parse_page(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        t = soup.find("tbody")
        if not t:
            raise NotFoundException()
        tds = t.find_all("td")
        for item in tds:
            date_time = item.text.strip()
            a = item.find("a")
            url = self.qiye_home + a["href"]
            self.parse_date_page(url)

    def parse_company(self, url):
        time.sleep(random.uniform(0.2, 1))
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", {"class": "view-content"})
        if not div:
            raise NotFoundException()
        tb = div.find("tbody")
        trs = tb.find_all("tr")
        for item in trs:
            name = item.find("td", {"class": "views-field-name"})
            # print("gongsi url {}".format(url))
            # print(name.a.text)
            if name and name.a and name.a["href"]:
                url = self.qiye_home + name.a["href"]
                self.parse_detail(url)

    def parse_detail(self, url):
        ess = es_search("qiyeminglu", url)
        if not ess[1] or not ess[0]:
            time.sleep(random.uniform(0.5, 2))
            print("parse url {}".format(url))
            r = self.session.get(url)
            soup = BeautifulSoup(r.text, "lxml")
            fs = soup.find("fieldset", {"class": "ad_biger"})
            lis = fs.div.find_all("li")
            res = {}
            for li in lis:
                name = li.find("span", {"class": "field-label"}).text.strip()
                value = li.find("span", {"class": "field-item"}).text.strip()
                if "点击" in value:
                    index = value.find("点击")
                    value = value[:index - 1]
                if "统一社会信用" in name:
                    value = re.findall(patern, value)[0]
                    res["socialCreditCode"] = value
                if "名称" in name:
                    res["enterpriseName"] = value
                if "地址" in name:
                    res["address"] = value
                if "地区" in name:
                    res["area"] = value
                if "日期" in name:
                    res["registerDate"] = value
                if "范围" in name:
                    res["businessScope"] = value
                if "代表人" in name:
                    res["legalRepresentative"] = value
                if "资金" in name:
                    res["registeredFunds"] = value
                if "类型" in name:
                    if value:
                        res["enterpriseType"] = value
                    else:
                        value = lis[-1].find("span", {"class": "field-item"}).span
                        if value:
                            res["enterpriseType"] = value.text.strip()
                            print(value.text)
            ecq = EnterpriseCq(**res)
            with session_scope() as session1:
                session1.add(ecq)
            if not ess[0]:
                EsBackends("qiyeminglu").index_data({"link": url, "status": 1, "date": time.time()})
            else:
                EsBackends("qiyeminglu").update_data({"link": url, "status": 1, "date": time.time()})

    def parse_date_page(self, url):
        item_page = "{}?page={}"
        count = 0
        jumpto = "2019-05-04"
        while True:
            item_url = item_page.format(url, count)
            try:
                while True:
                    if jumpto in url:
                        break
                    else:
                        print("跳过")
                        continue
                self.parse_company(item_url)
            except NotFoundException:
                print("{} 一共 {} 页".format(url, count))
                break
            count = count + 1

    def start(self):
        self.parse_date_item()


class NotFoundException(Exception):
    pass


if __name__ == "__main__":
    while True:
        start_time = time.time()
        try:
            QiyeCrawl().start()
            end_time = time.time()
            break
        except Exception as e:
            end_time = time.time()
            print(e)
        during = end_time - start_time
        h = during / 3600
        m = (during - int(h)* 3600) / 60
        mili = during - int(h)* 3600 - int(m) * 60
        print("一共爬行了{}小时{}分{}秒  共{}秒".format(int(h), int(m), int(mili), during))
        print("wait 0.5 hours")
        time.sleep(1800)

