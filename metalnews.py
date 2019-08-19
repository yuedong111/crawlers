# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import MetalInc
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


class MetalNews(object):
    url_home = "http://www.metalnews.cn/company/"

    def __init__(self):
        self.session = create_session()
        self.session.headers["Upgrade-Insecure-Requests"] = "1"
        self.session.headers[
            "Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        self.session.headers["Accept-Encoding"] = "gzip, deflate"
        self.session.headers["Accept-Language"] = "zh-CN,zh;q=0.9"
        self.session.headers["Cache-Control"] = "max-age=0"
        self.session.headers["Connection"] = "keep-alive"
        self.session.headers["Host"] = "www.metalnews.cn"
        self.jump = "search-htm-areaid-33-page-14.html"
        self.status = False

    def _province(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="category")
        mas = div.find_all("a")
        for a in mas:
            self._total_page(a.get("href"))

    def _total_page(self, url):
        time.sleep(0.2)
        print("total {}".format(url))
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="pages")
        if not div:
            total_pages = 1
        else:
            cite = div.find("cite")
            temp = cite.text
            temp = temp.split("/")[-1]
            total_pages = int(temp[:-1])
        count = 1
        while count < total_pages + 1:
            d_u = url.split(".htm")[0] + "-page-{}.html".format(count)
            if self.jump in d_u:
                self.status = True
            if not self.status:
                count = count + 1
                continue
            self._plist(d_u)
            count = count + 1

    @second_run
    def _plist(self, url):
        time.sleep(0.2)
        print("list {}".format(url))
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        divt = soup.find("div", class_="left_box")
        divs = divt.find_all("div", class_="list")
        for div in divs:
            res = {}
            lis = div.find_all("li")
            for li in lis:
                a = li.find("a")
                if a:
                    res["url"] = a.get("href")
                    tem = li.text.split()
                    if not tem:
                        continue
                    res["enterpriseName"] = tem[0]
                else:
                    if "主营：" in li.text:
                        res["products"] = li.text[li.text.find("主营：") + 3:]
                    else:
                        res["businessModel"] = li.text.strip()
            td = div.find("td", {"class": "f_orange", "width": "100"})
            if td:
                res["location"] = td.text
            with session_scope() as sess:
                cns = sess.query(MetalInc).filter(MetalInc.url == res["url"]).first()
                if not cns:
                    resu = self._detail(res["url"])
                    res.update(resu)
                    cn = MetalInc(**res)
                    sess.add(cn)

    @second_run
    def _detail(self, url):
        res = {}
        time.sleep(0.2)
        intro = url + "introduce/"
        print("detail {}".format(url))
        r = self.session.get(intro)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="lh18 px13")
        if not div:
            r = self.session.get(url)
            soup = BeautifulSoup(r.text, "lxml")
            div = soup.find("div", {"id": "content"})
            res["about"] = div.text.strip()
            div = soup.find("div", class_="contact_body")
            lis = div.find_all("li")
            temp = []
            for li in lis:
                temp.append(li.text)
            dd_contact = "联系人"
            dd_phone = "电话"
            dd_enterpriseType = "公司类型"
            dd_businessModel = "经营模式"
            dd_products = "销售产品"
            dd_location = "所在地"
            dd_address = "地址"
            dd_industry = "主营行业"
            dd_registerDate = "注册年份"
            dd_registeredFunds = "注册资本"
            dd_companyScale = "公司规模"
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
        else:
            res["about"] = div.text.strip()
            div = soup.find("div", class_="px13 lh18")
            trs = div.find_all("tr")
            temp = []
            for tr in trs:
                temp.append(tr.text)
            temp1 = []
            for item in temp:
                if item.count("\n") == 5:
                    tem = [i for i, v in enumerate(item) if v == "\n"]
                    index = tem[2]
                    temp1.append(item[: index].strip())
                    temp1.append(item[index:].strip())
                else:
                    temp1.append(item.strip())

            divs = soup.find_all("div", class_="side_body")
            temp = []
            for item in divs:
                if item.previous_sibling and "联系方式" in item.previous_sibling.previous_sibling.div.text:
                    lis = item.find_all("li")
                    for li in lis:
                        temp.append(li.text)
            temp.extend(temp1)
            dd_contact = "联系人："
            dd_phone = ["手机：", "电话：", "传真："]
            dd_enterpriseType = "公司类型："
            dd_businessScope = "经营范围："
            dd_location = "所 在 地："
            dd_address = "地址："
            dd_industry = "主营行业："
            dd_registerDate = "注册年份："
            dd_registeredFunds = "注册资本："
            dd_companyScale = "公司规模："
            tem = locals()
            tem1 = ""
            for item in temp:
                for k in tem.keys():
                    if "dd" in k and isinstance(tem.get(k), str) and tem.get(k) in item:
                        if k.split("_")[-1] not in res:
                            res[k.split("_")[-1]] = " ".join(
                                item[item.find(tem.get(k)) + len(tem.get(k)):].strip().split())
                    if "dd" in k and isinstance(tem.get(k), list):
                        for tt in tem.get(k):
                            if tt in item:
                                tem1 = tem1 + item + " "
                        if "phone" not in res or not res["phone"]:
                            res["phone"] = tem1
        return res


if __name__ == "__main__":
    MetalNews()._province()

# MetalNews()._province()
# MetalNews()._plist("http://www.metalnews.cn/company/search-htm-areaid-1.html")
# MetalNews()._detail("http://www.metalnews.cn/com/shby1171/")
