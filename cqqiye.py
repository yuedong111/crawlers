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
import traceback

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


def second_run(func):
    def decorate(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            print(e)
            while True:
                time.sleep(2)
                print("run again {}".format(args))
                res = second_run(func)(*args, **kwargs)
                break
        return res
    return decorate


class QiyeCrawl(object):
    qiye_home = "https://gongshang.mingluji.com"
    date_page = "https://gongshang.mingluji.com/chongqing/riqi?page={}"

    def __init__(self):
        self.session = create_qiye_session()
        self.jump = False
        self.jump_to = "2019"
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
        time.sleep(random.uniform(0.2, 1))
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
            sa = self.parse_date_page(url)

    @second_run
    def parse_company(self, url):
        time.sleep(random.uniform(0.5, 1))
        self.session.headers["Referer"] = url
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.title.text.strip()
        if title == "403 Forbidden":
            raise Exception("403 Forbidden")
        div = soup.find("div", {"class": "view-content"})
        if not div:
            raise NotFoundException()
        tb = div.find("tbody")
        trs = tb.find_all("tr")
        for item in trs:
            name = item.find("td", {"class": "views-field-name"})
            if name and name.a and name.a["href"]:
                url = self.qiye_home + name.a["href"]
                sa = self.parse_detail(url)

    @second_run
    def parse_detail(self, url):
        ess = es_search("qiyeminglu", url)
        if not ess[1] or not ess[0]:
            time.sleep(random.uniform(1.5, 2))
            print("parse url {}".format(url))
            r = self.session.get(url)
            soup = BeautifulSoup(r.text, "lxml")
            h1 = soup.find("h1", {"id": "page-title"})
            if "未找到" in h1.text:
                return
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
                    res["area"] = value.strip()
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
        jump_to = self.jump_to
        while True:
            item_url = item_page.format(url, count)
            if jump_to in url:
                self.jump = True
            try:
                if self.jump:
                    self.parse_company(item_url)
                else:
                    print("跳过 {}".format(url))
                    break
            except NotFoundException:
                print("{} 一共 {} 页".format(url, count))
                return
            except Exception as e:
                print(e)
                print("{} 一共 {} 页".format(url, count))
                return
            count = count + 1

    def start(self):
        self.parse_date_item()


class NotFoundException(Exception):
    pass


if __name__ == "__main__":
    while True:
        qiye = QiyeCrawl()
        with session_scope() as sess:
            ms = sess.query(EnterpriseCq).order_by(EnterpriseCq.id.desc()).first()
        qiye.jump_to = "2018-06-14"
        start_time = time.time()
        try:
            qiye.start()
            end_time = time.time()
            break
        except Exception as e:
            end_time = time.time()
            print(traceback.print_exc())
        during = end_time - start_time
        h = during / 3600
        m = (during - int(h) * 3600) / 60
        mili = during - int(h) * 3600 - int(m) * 60
        print("一共爬行了{}小时{}分{}秒  共{}秒".format(int(h), int(m), int(mili), during))
        nowt = time.asctime(time.localtime(time.time()))
        print(nowt)
        print("wait 1 minites")
        time.sleep(60*60)
