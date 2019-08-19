# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import TaoJin
from utils.sqlbackends import session_scope
import traceback
from functools import wraps
import math
from urllib.parse import urlparse


def second_run(func):
    count = 0

    @wraps(func)
    def decorate(*args, **kwargs):
        nonlocal count
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            print(traceback.print_exc())
            while True:
                time.sleep(2)
                print("run again {} {}".format(count, args))
                count = count + 1
                if count >= 5:
                    count = 0
                    return {}
                res = decorate(*args, **kwargs)
                break
        count = 0
        return res

    return decorate


class TaoJinDi(object):

    url_home = "http://hy.taojindi.com"

    def __init__(self):
        self.session = create_session()
        self.jump = ""
        self.status = False

    def _province(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="info-list info-list2")
        mas = div.find_all("a")
        for a in mas:
            d_u = "http://hy.taojindi.com" + a.get("href")
            self._sec_cate(d_u, a.text[: -4])

    def _sec_cate(self, url, province):
        time.sleep(0.2)
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="info-list info-list5")
        mas = div.find_all("a")
        temp = []
        temp.append((url, province + "最新企业推荐"))
        for a in mas:
            d_u = "http://hy.taojindi.com" + a.get("href")
            temp.append((d_u, a.text))

    @second_run
    def _tatal_pages(self, url, category):
        print("total {}".format(url))
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="paging")
        span = div.find("span", class_="total orange ml5 mr5")
        total = int(span.text)
        if not total:
            return
        total_pages = math.ceil(total/10)
        count = 1
        while count < total_pages + 1:
            d_u = url.split(".htm")[0] + "-page-{}.html".format(count)
            if self.jump in d_u:
                self.status = True
            if not self.status:
                count = count + 1
                continue
            self._plist(d_u, category)
            count = count + 1

    @second_run
    def _plist(self, url, category):
        print("list {}".format(url))
        time.sleep(0.2)
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="company-info")
        lis = div.find_all("li")
        for li in lis:
            res = {}
            res["category"] = category
            tel = li.find("div", class_="tel")
            res["phone"] = tel.text
            a = li.find("a")
            res["enterpriseName"] = a.text
            d_u = "http://hy.taojindi.com" + a.get("href")
            res["url"] = d_u
            div = li.find("div", class_="info")
            res["about"] = div.text
            div = li.find("div", class_="address")
            temp = div.text.split()
            for item in temp:
                if "地址：" in item:
                    res["address"] = item[len("地址：" ):]
                elif "主营产品：" in item:
                    res["products"] = item[len("主营产品："):]
            print(d_u)
            # print(res)

    @second_run
    def _detail(self, url):
        time.sleep(0.2)
        print("detail {}".format(url))
        res = {}
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="company-basic clearfix")
        lis = div.find_all("li")
        temp = []
        for li in lis:
            temp.append(li.text)
        div = soup.find("div", class_="company-intro p20")
        table = div.find("table")
        trs = table.find_all("tr")
        for tr in trs:
            temp.append(" ".join(map(lambda x: x.strip(), tr.text.strip().split("\n"))))
        ss_contact = "联系人："
        ss_phone = ["移动电话：", "电话："]
        ss_enterpriseType = "公司类型："
        ss_location = "所属省市："
        ss_industry = "主营行业："
        ss_registeredFunds = "注册资金："
        ss_representative = "企业法人："
        ss_establishedTime = "成立时间："
        ss_address = "地址："
        ss_products = "主营产品："
        tem = locals()
        tem1 = ""
        for item in temp:
            for k in tem.keys():
                if "ss" in k and isinstance(tem.get(k), str) and tem.get(k) in item:
                    res[k.split("_")[-1]] = " ".join(item[item.find(tem.get(k))+len(tem.get(k)):].strip().split())
                elif "ss" in k and isinstance(tem.get(k), list):
                    for tt in tem.get(k):
                        if tt in item:
                            tem1 = tem1 + item + " "
                    res["phone"] = tem1
        return res



# TaoJinDi()._province()
# TaoJinDi()._sec_cate("http://hy.taojindi.com/region/beijing1/")
# TaoJinDi()._tatal_pages("http://hy.taojindi.com/region/beijing1/")
# TaoJinDi()._plist("http://hy.taojindi.com/region/beijing1/")
TaoJinDi()._detail("http://hy.taojindi.com/scompany441941/")