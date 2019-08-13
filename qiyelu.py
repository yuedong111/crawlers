# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import SouLeWang
from utils.sqlbackends import session_scope
import traceback
from functools import wraps
import re
from collections import OrderedDict

class ZHQYL(object):
    url_home = "http://www.qy6.com/qyml/"

    def __init__(self):
        self.session = create_session()

    def _category(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table", {"cellspacing": "0", "cellpadding": "2", "width": "100%", "border": "0"})
        tds = table.find_all("td", {"valign": "top", "width": "50%"})
        for td in tds:
            mas = td.find_all("a")
            d_u = mas[0].get("href")
            if "fqyC32" in d_u:
                r = self.session.get(d_u)
                soup = BeautifulSoup(r.text, "lxml")
                table = soup.find("table", {"cellspacing": "0", "cellpadding": "2", "width": "100%", "border": "0"})
                tb = table.find("tbody")
                tds = tb.find_all("td", {"valign": "top", "width": "33%"})
                for td1 in tds:
                    a = td1.find("a")
                    d_u = "http://www.qy6.com/qyml/" + a.get("href")
                    detail = (d_u, a.text)
            else:
                detail = (d_u, mas[0].text)
            sa = self._total_pages(*detail)
            time.sleep(1)

    def _total_pages(self, url, category):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table", {"style": "BORDER-top: #9c9a9c 1px solid"})
        tbody = table.find("tbody")
        sts = tbody.find_all("strong")
        total_pages = int(sts[-1].text)
        temurl = url.split(".h")
        d_u = temurl[0] + "_p{}.html"
        count = 1
        while count < total_pages + 1:
            de_u = d_u.format(count)
            count = count + 1

    def _p_list(self, url, category):
        result = {}
        result["category"] = category
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table", {"width": "980", "border": "0", "cellspacing": "0", "cellpadding": "0"})
        res = OrderedDict()
        for table in tables:
            if "企业录推荐企业信息" in table.text:
                table = table.next_sibling.next_sibling
                trs = table.find_all("tr")
                for tr in trs:
                    tds = tr.find_all("td")
                    for td in tds:
                        ma = td.find_all("a", {"target": "_blank"})
                        for a in ma:
                            if not a.get("title"):
                                detail = (a.text, a.get("href"))
                            else:
                                products = a.text
                        font = td.find("font",{"color": "#666666"})
                        entype = font.text
                        res[detail] = (products, entype)
        for key, value in res.items():
            print(key, value)


ZHQYL()._p_list("http://www.qy6.com/qyml/fqyC01_p1.html", "")
