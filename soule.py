# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_soule_session as create_session
import time
from utils.models import WGQY
from utils.sqlbackends import session_scope
import traceback
from functools import wraps
import re

def second_run(func):
    count = 0

    @wraps(func)
    def decorate(*args, **kwargs):
        nonlocal count
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            print(e)
            while True:
                time.sleep(2)
                print("run again {} {}".format(count, args))
                count = count + 1
                if count >= 5:
                    count = 0
                    return "too many retrys"
                res = decorate(*args, **kwargs)
                break
        return res

    return decorate


class SouLe(object):

    url_home = "http://www.51sole.com/company/"
    fpa = re.compile(r"\d+")

    def __init__(self):
        self.session = create_session()
        self.jump = ""
        self.status = False

    def _provice(self):
        r = self.session.get(self.url_home)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="enterprise-info")
        mas = div.find_all("a")
        for a in mas:
            d_u = "http:" + a.get("href")
            print(d_u, a.text)

    def _category(self, url):
        self.session.headers["Referer"] = "http://www.51sole.com/company/"
        self.session.headers["Host"] = "www.51sole.com"
        r = self.session.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="hy_include")
        mas = div.find_all("a")
        for a in mas:
            d_u = "http://www.51sole.com" + a.get("href")
            print(d_u)

    def _pages(self, url):
        r = self.session.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="list-page")
        span = div.find("span")
        res = self.fpa.findall(span.text)
        try:
            total_pages = int(res[0])
        except:
            total_pages = 1
        print(total_pages)
        count = 1
        while count < total_pages + 1:
            d_u = url + "p{}/".format(count)

    def _list_item(self, url):
        r = self.session.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="hy_lbox fl mt2")
        div = div.find("div", class_="hy_companylist")
        lis = div.find_all("li")
        for li in lis:
            res = {}
            a = li.find("a")
            d_u = "http:"+a.get("href")
            res["url"] = d_u
            res["enterpriseName"] = a.text
            span = li.find("span", class_="tel")
            res["phone"] = span.text
            dds = li.find_all("dd")
            temp = []
            for dd in dds:
                temp.append(dd.text)
            ss = "地址："
            ss1 = "主营产品："
            for item in temp:
                if ss in item:
                    res["address"] = item[len(ss):]
                elif ss1 in item:
                    res["products"] = item[len(ss1):]
            print(res)




# SouLe()._category("http://www.51sole.com/anshan/")
# SouLe()._pages("http://www.51sole.com/anshan-anfang/p2/")
SouLe()._list_item("http://www.51sole.com/anshan-anfang/p1/")
