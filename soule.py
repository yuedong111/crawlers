# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_soule_session as create_session
import time
from utils.models import SouLeWang
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
            print(traceback.print_exc())
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
            self._category(d_u, a.text)

    def _category(self, url, location):
        r = self.session.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="hy_include")
        mas = div.find_all("a")
        for a in mas:
            d_u = "http://www.51sole.com" + a.get("href")
            category = a.text
            self._pages(d_u, category, location)

    @second_run
    def _pages(self, url, category, location):
        print("total {}".format(url))
        r = self.session.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="list-page")
        span = div.find("span")
        res = self.fpa.findall(span.text)
        try:
            total_pages = int(res[0])
        except Exception as e:
            print("zong ye shu {}".format(e))
            total_pages = 1
        count = 1
        while count < total_pages + 1:
            d_u = url + "p{}/".format(count)
            if self.jump in d_u:
                self.status = True
            if not self.status:
                count = count + 1
                continue
            self._list_item(d_u, category, location)
            count = count + 1

    @staticmethod
    def index_page(url):
        s = url.split("/")
        index = s[-2][1:]
        return int(index)

    @second_run
    def _list_item(self, url, category, location):
        time.sleep(0.6)
        print("list url {}".format(url))
        self.session.headers["Referer"] = url[:url.find("/p")] + "/p{}/".format(self.index_page(url)-1)
        r = self.session.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="hy_lbox fl mt2")
        div = div.find("div", class_="hy_companylist")
        lis = div.find_all("li")
        for li in lis:
            res = {}
            a = li.find("a")
            if a.get("href").startswith("http"):
                d_u = a.get("href")
            else:
                d_u = "http:"+a.get("href")
            res["url"] = d_u
            res["category"] = category
            res["location"] = location
            res["enterpriseName"] = a.text
            span = li.find("span", class_="tel")
            if hasattr(span, "text"):
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
            with session_scope() as sess:
                soule = sess.query(SouLeWang).filter(SouLeWang.url == d_u).first()
                if not soule:
                    resu = self._detail(d_u)
                    res.update(resu)
                    sou = SouLeWang(**res)
                    sess.add(sou)

    @second_run
    def _detail(self, url):
        print("detail {}".format(url))
        time.sleep(0.5)
        res = {}
        r = self.session.get(url)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="contact-info")
        if div:
            lis = div.find_all("li")
            temp = []
            for li in lis:
                temp.append(li.text)
            ss1 = "联\xa0\xa0系\xa0\xa0人："
            ss2 = "邮\xa0\xa0\xa0\xa0\xa0\xa0\xa0编："
            ss3 = "地\xa0\xa0\xa0\xa0\xa0\xa0\xa0址："
            ss4 = "商铺网址："
            for item in temp:
                if ss1 in item:
                    res["contact"] = " ".join(item[len(ss1):].strip().split())
                elif ss2 in item:
                    res["postCodes"] = item[len(ss2):]
                elif ss4 in item:
                    res["siteUrl"] = item[len(ss4):]
                elif ss3 in item:
                    res["address"] = item[len(ss3):]
            div = soup.find("div", class_="company-info")
            trs = div.find_all("tr")
            temp = []
            for item in trs:
                temp.append(" ".join(item.text.split()))
            ssd_enterpriseType = "企业类型"
            ssd_businessModel = "经营模式"
            ssd_location = "所在地区"
            ssd_industry = "所属行业"
            ssd_registerDate = "注册时间"
            ssd_registeredFunds = "注册资本"
            ssd_companyScale = "公司规模"
            ssd_annualTurnover = "年营业额"
            ssd_products = "主营产品"
            ssd_representative = "法定代表人"
            tem = locals()
            for item in temp:
                for k in tem.keys():
                    if "ssd" in k and tem.get(k) in item:
                        res[k.split("_")[-1]] = item[len(tem.get(k)):].strip()
        else:
            div = soup.find("div", {"id": "navcontact"})
            lis = div.find_all("li")
            temp = []
            for item in lis:
                temp.append(item.text.strip())
            dd_contact = "联系人："
            dd_phone = ["手机：", "QQ：", "电话："]
            tem = locals()
            tem1 = ""
            for item in temp:
                for k in tem.keys():
                    if "dd" in k and isinstance(tem.get(k), str) and tem.get(k) in item:
                        res[k.split("_")[-1]] = " ".join(item[len(tem.get(k)):].strip().split())
                    elif "dd" in k and isinstance(tem.get(k), list):
                        for tt in tem.get(k):
                            if tt in item:
                                tem1 = tem1 + item + " "
                        res["phone"] = tem1
            div = div.find("div", class_="more")
            a = div.find("a")
            if a.get("href").startswith("http"):
                d_u = a.get("href")
            else:
                d_u = "http:" + a.get("href")
            r = self.session.get(d_u)
            soup = BeautifulSoup(r.text, "lxml")
            div = soup.find("div", {"id": "companyinfo"})
            lis = div.find_all("li")
            temp = []
            for li in lis:
                temp.append(" ".join(li.text.strip().split()))
            ssd_enterpriseType = "企业类型："
            ssd_businessModel = "经营模式："
            ssd_location = "所在地区："
            ssd_industry = "所属行业："
            ssd_registerDate = "注册时间："
            ssd_registeredFunds = "注册资本："
            ssd_companyScale = "公司规模："
            ssd_annualTurnover = "年营业额："
            ssd_products = "主营产品："
            ssd_representative = "法定代表人："
            ssd_siteUrl = "公司网站："
            tem = locals()
            for item in temp:
                for k in tem.keys():
                    if "ssd" in k and tem.get(k) in item:
                        res[k.split("_")[-1]] = item[len(tem.get(k)):].strip()
        return res

    def start(self):
        self._provice()


if __name__ == "__main__":
    SouLe().start()

