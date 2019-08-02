# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
from utils.make_sessions import create_shunqi_session
import time
from utils.models import ShunQi
from utils.sqlbackends import session_scope
import random


class ShunQiCrawl:
    url_home = "http://chongqing.11467.com"

    def __init__(self):
        self.jump = "chengkou/pn10"
        self.status = False
        self.session = create_shunqi_session()

    def category(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="box sidesubcat t5 links")
        div = div.find("div", class_="boxcontent")
        mas = div.find_all("dl", class_="listtxt")
        for dd in mas:
            dd = dd.find_all("a")
            for a in dd:
                if a.get("href"):
                    # print(a.get("href"), dd[0].text+a.text)
                    area = dd[0].text + a.text
                    d_u = self.url_home + a.get("href")
                    self.total_pages(d_u, area)

    @staticmethod
    def str_w(ss):
        res = {}
        f_s = "产品："
        s1 = "地址："
        s2 = "时间："
        s3 = "注册资本："
        if f_s in ss:
            index = ss.find(f_s)
            res["products"] = ss[index + len(f_s):].strip()
        elif s1 in ss:
            index = ss.find(s1)
            res["address"] = ss[index + len(s1):].strip()
        elif s2 in ss:
            index = ss.find(s2)
            res["establishedTime"] = ss[index + len(s2):].strip()
        elif s3 in ss:
            index = ss.find(s3)
            res["registeredCapital"] = ss[index + len(s3):].strip()
        return res

    def total_pages(self, url, area):
        self.session.headers["Host"] = "chongqing.11467.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        page = soup.find("div", class_="pages")
        mas = page.find_all("a")
        total_pages = mas[-1].get("href").split("/")[-1][2:]
        count = 1
        while count < int(total_pages) + 1:
            d_u = url + "pn{}".format(count)
            if self.jump in d_u:
                self.status = True
            if not self.status:
                count = count + 1
                continue
            self.url_list(d_u, area)
            count = count + 1

    def url_list(self, url, area):
        print("list url {}".format(url))
        time.sleep(random.uniform(1, 3))
        self.session.headers["Host"] = "chongqing.11467.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find("ul", class_="companylist")
        lis = ul.find_all("li")
        for li in lis:
            res = {}
            res["area"] = area
            a = li.find("a")
            d_u = "http:" + a.get("href")
            name = a.get("title")
            res["enterpriseName"] = name
            res["url"] = d_u
            with session_scope() as sess:
                qxc = sess.query(ShunQi).filter(ShunQi.url == res["url"]).first()
                if not qxc:
                    resu = self.detail(d_u)
                    res.update(resu)
                    div = li.find("div", class_="f_l")
                    divs = div.find_all("div")
                    res.update(self.str_w(divs[0].text))
                    res.update(self.str_w(divs[1].text))
                    sq = ShunQi(**res)
                    sess.add(sq)
                    print(res)

    def detail(self, url):
        print("detail url {}".format(url))
        time.sleep(random.uniform(2, 3))
        res = {}
        self.session.headers["Host"] = "www.11467.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", {"id": "aboutus"})
        cdiv = div.find("div", {"id": "aboutuscontent"})
        res["about1"] = cdiv.text.strip()
        div = soup.find("div", {"id": "contact"})
        dl = div.find("dl", class_="codl")
        for index, value in enumerate(dl.children):
            if value.name == "dt":
                res[value.text] = list(dl.children)[index + 1].text.strip()
            index = index + 2
        div = soup.find("div", {"id": "gongshang"})
        table = div.find("table", class_="codl")
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            res[tds[0].text] = tds[1].text.strip()
        temp = {}
        for key in list(res.keys()):
            if "手机" in key:
                res["phone"] = res[key]
            elif "人：" in key or "厂长：" in key:
                res["representative"] = res[key]
            elif "邮政" in key:
                res["postCodes"] = res[key]
            elif "注册资本：" in key:
                res["registeredFunds"] = res[key]
            elif "固定电话" in key:
                res["fixedPhone"] = res[key]
            elif "传真" in key:
                res["fax"] = res[key]
            elif "状态" in key:
                res["operateStatus"] = res[key]
            elif key == "about1":
                res["about"] = res[key]
            elif "营业执照" in key:
                res["businessCode"] = res[key]
            elif "成立时间" in key:
                res["establishedTime"] = res[key]
            else:
                temp[key] = res[key]
            res.pop(key)
        res["others"] = json.dumps(temp)
        return res

    def start(self):
        self.category()


if __name__ == "__main__":
    while True:
        try:
            ShunQiCrawl().start()
            break
        except Exception as e:
            print(e)
            time.sleep(1200)

# ShunQi().category()
# ShunQi().url_list("http://chongqing.11467.com/liangping/huilongzhen/pn1", "sld")
# ShunQi().detail("http://www.11467.com/chongqing/co/126973.htm")
