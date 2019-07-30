# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from utils.make_sessions import create_shunqi_session
# from utils.models import DZDianPing
# from utils.sqlbackends import session_scope


class ShunQi:

    url_home = "http://chongqing.11467.com"

    def __init__(self):
        self.jump = ""
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
                    print(a.get("href"), dd[0].text+a.text)
                    area = dd[0].text+a.text
                    d_u = self.url_home + a.get("href")

    @staticmethod
    def str_w(ss):
        res = {}
        f_s = "产品："
        s1 = "地址："
        s2 = "时间："
        s3 = "注册资本："
        if f_s in ss:
            index = ss.find(f_s)
            res["products"] = ss[index+len(f_s):]
        elif s1 in ss:
            index = ss.find(s1)
            res["address"] = ss[index + len(s1):]
        elif s2 in ss:
            index = ss.find(s2)
            res["establishedTime"] = ss[index + len(s2):]
        elif s3 in ss:
            index = ss.find(s3)
            res["registeredCapital"] = ss[index + len(s3):]
        return res

    def url_list(self, url, area):
        self.session.headers["Host"] = "chongqing.11467.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find("ul", class_="companylist")
        lis = ul.find_all("li")
        for li in lis:
            res = {}
            a = li.find("a")
            d_u = "http:" + a.get("href")
            name = a.get("title")
            res["name"] = name
            res["url"] = d_u
            print(d_u, name)
            div = li.find("div", class_="f_l")
            divs = div.find_all("div")
            res.update(self.str_w(divs[0].text))
            res.update(self.str_w(divs[1].text))
            print(res)

    def detail(self, url):
        res = {}
        self.session.headers["Host"] = "www.11467.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", {"id": "aboutus"})
        cdiv = div.find("div", {"id": "aboutuscontent"})
        res["about"] = cdiv.text.strip()
        div = soup.find("div", {"id": "contact"})
        dl = div.find("dl", class_="codl")
        for index ,value in enumerate(dl.children):
            if value.name == "dt":
                res[value.text] = list(dl.children)[index+1].text
            index = index + 2
        div = soup.find("div", {"id": "gongshang"})
        table = div.find("table", class_="codl")
        print(res)

# ShunQi().url_list("http://chongqing.11467.com/liangping/huilongzhen/pn1", "sld")
ShunQi().detail("http://www.11467.com/chongqing/co/126973.htm")