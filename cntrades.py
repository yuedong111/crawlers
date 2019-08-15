# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import CnTrade
from utils.sqlbackends import session_scope
import traceback
from functools import wraps
import re
from collections import OrderedDict
import time
from urllib.parse import urlparse

def second_run(func):
    count = 0

    @wraps(func)
    def decorate(*args, **kwargs):
        nonlocal count
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            if str(e) == "404":
                time.sleep(3)
            print(traceback.print_exc())
            while True:
                time.sleep(2)
                print("run again {} {}".format(count, args))
                count = count + 1
                if 2 < count < 5:
                    time.sleep(5)
                if count >= 5:
                    return {}
                res = decorate(*args, **kwargs)
                break
        count = 0
        return res
    return decorate


class Trades(object):

    url_home = "http://www.cntrades.com/company/"

    def __init__(self):
        self.session = create_session()
        self.session.headers["Upgrade-Insecure-Requests"] = "1"
        self.session.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        self.session.headers["Accept-Encoding"] = "gzip, deflate"
        self.session.headers["Accept-Language"] = "zh-CN,zh;q=0.9"
        self.session.headers["Cache-Control"] = "max-age=0"
        self.session.headers["Connection"] = "keep-alive"
        self.cookies = "DOT_mysqlrw=2; Hm_lvt_abb44720aa6580c1c49b6ffff8216dab=1565771047,1565832018; DOT_last_search={}; Hm_lpvt_abb44720aa6580c1c49b6ffff8216dab={}"
        self.session.headers["Cookie"] = self.cookies.format(int(time.time())-1, int(time.time())-2)
        self.jump = ""
        self.status = False

    def _cate(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="com_ct5")
        dls = div.find_all("dl")
        for dl in dls:
            imi = dl.find_all("i")
            for i in imi:
                a = i.find("a")
                if a:
                    self._seconde_cate(a.get("href"), a.text)

    @second_run
    def _seconde_cate(self, url, category):
        time.sleep(1)
        self.session.headers["Cookie"] = self.cookies.format(int(time.time())-1, int(time.time())-2)
        self.session.headers["Host"] = "www.cntrades.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find("ul", class_="class-name-item")
        mas = ul.find_all("a")
        temp = []
        temp.append((url, category))
        for a in mas:
            tem = (a.get("href"), a.text)
            if tem not in temp:
                temp.append(tem)
        for item in temp:
            if item:
                if self.jump in item[0]:
                    self.status = True
                if not self.status:
                    continue
                self._total_pages(*item)

    @second_run
    def _total_pages(self, url, category):
        time.sleep(0.7)
        print("total {}".format(url))
        self.session.headers["Cookie"] = self.cookies.format(int(time.time())-1, int(time.time())-2)
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        cite = soup.find("cite")
        total_pages = cite.text.split("/")[-1][:-1]
        total_pages = int(total_pages)
        count = 1
        du = url.split(".html")[0]
        while count < total_pages + 1:
            d_u = du + "-{}.html".format(count)
            if self.jump in du:
                self.status = True
            if not self.status:
                count = count + 1
                continue
            sa = self._p_list(d_u, category)
            count = count + 1

    @second_run
    def _p_list(self, url, category):
        time.sleep(1)
        print("list {}".format(url))
        res = {}
        res["category"] = category
        self.session.headers["Host"] = "www.cntrades.com"
        self.session.headers["Cookie"] = self.cookies.format(int(time.time())-1, int(time.time())-2)
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        divv = soup.find("div", class_="left_box")
        if not divv:
            if "404 Not Found" in r.text:
                raise Exception("404")
        divs = divv.find_all("div", class_="list")
        for div in divs:
            lis = div.find_all("li")
            for li in lis:
                a = li.find("a")
                if a:
                    res["url"] = a.get("href")
                    tem = li.text.split()
                    res["enterpriseName"] = tem[0]
                    res["businessModel"] = tem[-1]
                else:
                    if "主营：" in li.text:
                        res["products"] = li.text[li.text.find("主营：")+3:]
                    else:
                        res["address"] = li.text
            td = div.find("td", {"class": "f_orange", "width": "100"})
            if td:
                res["location"] = td.text
            with session_scope() as sess:
                cns = sess.query(CnTrade).filter(CnTrade.url == res["url"]).first()
                if not cns:
                    resu = self._detail(res["url"])
                    res.update(resu)
                    cn = CnTrade(**res)
                    sess.add(cn)

    @second_run
    def _detail(self, url):
        time.sleep(1)
        d = urlparse(url)
        print("detail {}".format(url))
        res = {}
        intro = url + "/introduce/"
        self.session.headers["Cookie"] = self.cookies.format(int(time.time())-1, int(time.time()))
        self.session.headers["Host"] = d.netloc
        r = self.session.get(intro)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", {"id": "content"})
        if not div:
            div = soup.find("div", class_="lh18 px13 pd10")
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
                temp1.append(item[index: ].strip())
            else:
                temp1.append(item.strip())
        ssd_enterpriseType = "公司类型："
        ssd_businessModel = "经营模式："
        ssd_location = "所 在 地："
        ssd_industry = "主营行业："
        ssd_registerDate = "注册年份："
        ssd_registeredFunds = "注册资本："
        ssd_companyScale = "公司规模："
        ssd_products = "销售的产品："
        ssd_businessScope = "经营范围："
        tem = locals()
        for item in temp1:
            for k in tem.keys():
                if "ssd" in k and tem.get(k) in item:
                    res[k.split("_")[-1]] = item[len(tem.get(k)):].strip()
        time.sleep(1)
        conurl = url + "/contact/"
        r = self.session.get(conurl)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="px13 lh18")
        trs = div.find_all("tr")
        ctemp = []
        for tr in trs:
            ctemp.append(tr.text.strip())
        ssc_address = "公司地址："
        ssc_postCodes = "邮政编码："
        ssc_siteUrl = "公司网址："
        ssc_contact = "联 系 人："
        tem = locals()
        for item in ctemp:
            for k in tem.keys():
                if "ssc" in k and tem.get(k) in item:
                    res[k.split("_")[-1]] = item[len(tem.get(k)):].strip()
        res["siteUrl"] = " http".join(res["siteUrl"].split("http"))
        imgs = div.find_all("img", {"align": "absmddle"})
        imgt = ""
        for img in imgs:
            imgt = imgt + img.get("src") + " "
        res["phoneimg"] = imgt
        return res

    def start(self):
        self._cate()


if __name__ == "__main__":
    Trades().start()




# Trades()._cate()
# Trades()._seconde_cate("http://www.cntrades.com/company/list-2597.html")
# Trades()._total_pages("http://www.cntrades.com/company/list-2597.html", "")
# Trades()._p_list("http://www.cntrades.com/company/list-2741-2.html", "运动鞋")
# Trades()._detail("http://xk12345.cntrades.com")