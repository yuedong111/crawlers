# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import HuangYe
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
                    return "too many retrys"
                res = decorate(*args, **kwargs)
                break
        return res

    return decorate


class QYHuangYe(object):
    url_home = "http://b2b.huangye88.com/region/"

    def __init__(self):
        self.session = create_session()
        self.jump = "chongqing/LEDteshuzhaomingdeng12773/"
        self.status = False
        self.session.headers["Upgrade-Insecure-Requests"] = "1"

    def _provice(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="topprovince")
        mas = div.find_all("a")
        temp = []
        temp.append(("http://b2b.huangye88.com/chongqing/", "重庆"))
        temp.append(("http://b2b.huangye88.com/beijing/", "北京"))
        temp.append(("http://b2b.huangye88.com/shanghai/", "上海"))
        temp.append(("http://b2b.huangye88.com/tianjin/", "天津"))
        for a in mas:
            if a.get("href"):
                temp.append((a.get("href"), a.text))
        for item in temp:
            self._cate(item[0])

    def _cate(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        divs = soup.find_all("div", class_="tag_tx")
        for div in divs:
            mas = div.find_all("a")
            for a in mas:
                self.seconde_cate(a.get("href"), a.text)

    def seconde_cate(self, url, category):
        time.sleep(0.3)
        self.session.headers["Host"] = "b2b.huangye88.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="box")
        mas = div.find_all("a")
        temp = []
        temp.append((url, category))
        for a in mas:
            temp.append((a.get("href"), a.text))
        for item in temp:
            if self.jump in item[0]:
                self.status = True
            if not self.status:
                continue
            self._total_pages(*item)

    @second_run
    def _total_pages(self, url, category):
        time.sleep(0.3)
        self.session.headers["Host"] = "b2b.huangye88.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        span = soup.find("span", {"style": "float:right;padding-right:10px"})
        em = span.find("em")
        if int(em.text) > 1000:
            total_pages = 50
        else:
            total_pages = math.ceil(int(em.text) / 20)
        count = 1
        while count < total_pages + 1:
            d_u = url + "pn{}/".format(count)
            sa = self._p_list(d_u, category)
            count = count + 1

    @second_run
    def _p_list(self, url, category):
        time.sleep(0.3)
        if "pn1/" in url:
            url = url[:url.find("pn1/")]
        print("list url {}".format(url))
        self.session.headers["Host"] = "b2b.huangye88.com"
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        form = soup.find("form", {"id": "jubao"})
        mas = form.find_all("dl")
        for dl in mas:
            res = {}
            res["category"] = category
            a1 = dl.find("a", {"rel": "nofollow"})
            if a1:
                res["phone"] = a1.text
            dds = dl.find_all("dd")
            for dd in dds:
                if not dd.has_attr("class"):
                    res["products"] = dd.text[:-4]
            a = dl.find("a", {"itemprop": "name"})
            if a:
                d_u = a.get("href") + "company_detail.html"
                res["enterpriseName"] = a.text
                res["url"] = d_u
                with session_scope() as sess:
                    hy = sess.query(HuangYe).filter(HuangYe.url == d_u).first()
                    if not hy:
                        result = self._detail(d_u)
                        res.update(result)
                        HY = HuangYe(**res)
                        sess.add(HY)

    @second_run
    def _detail(self, url):
        time.sleep(0.3)
        print("detail {}".format(url))
        res = {}
        d = urlparse(url)
        self.session.headers["Host"] = d.netloc
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find('ul', class_="l-txt none")
        if not ul:
            res["about"] = "该企业不存在"
            return res
        temp = ul.text.split()
        ss_contact = "联系人："
        ss_phone = "手机："
        tem = locals()
        for item in temp:
            for k in tem.keys():
                if "ss" in k and isinstance(tem.get(k), str) and tem.get(k) in item:
                    res[k.split("_")[-1]] = " ".join(item[len(tem.get(k)):].strip().split())
        if "phone" in res and ss_phone in res["phone"]:
            res["phone"] = res["phone"][res["phone"].find(ss_phone) + len(ss_phone):]
        ul1 = soup.find("ul", class_="con-txt")
        lis = ul1.find_all("li")
        temp = []
        for li in lis:
            temp.append(li.text)
        ssd_enterpriseType = "企业类型："
        ssd_location = "所在地："
        ssd_industry = "主营行业："
        ssd_registeredFunds = "注册资金："
        ssd_representative = "企业法人："
        ssd_establishedTime = "成立时间："
        ssd_products = "主营产品："
        tem = locals()
        for item in temp:
            for k in tem.keys():
                if "ssd" in k and tem.get(k) in item:
                    res[k.split("_")[-1]] = item[len(tem.get(k)):].strip()
        div = soup.find_all("div", class_="r-content")[-1]
        p = div.find("p", class_="txt")
        res["about"] = p.text.strip()
        table = div.find("table", {"border": "0", "cellspacing": "1"})
        trs = table.find_all("tr")
        for tr in trs:
            span = tr.find("span")
            key = span.text
            value = tr.text
            value = value[value.find(key) + len(key):]
            if "经营模式" in key:
                res["businessModel"] = value
            elif "企业状态" in key:
                res["status"] = value
            elif "主要客户群" in key:
                if len(value) > 66:
                    value = value[:66]
                res["customers"] = value
            elif "经营范围" in key:
                if len(value) > 600:
                    value = value[:600]
                res["businessScope"] = value
            elif "公司邮编" in key:
                res["postCodes"] = value
            elif "行政区域" in key:
                res["location"] = value
            elif "公司地址" in key:
                res["address"] = value
        return res

    def start(self):
        self._provice()


if __name__ == "__main__":
    QYHuangYe().start()

# HuangYe()._provice()
# HuangYe()._cate("http://b2b.huangye88.com/guangdong/", "")
# HuangYe().seconde_cate("http://b2b.huangye88.com/guangdong/jixie/", "jixie")
# HuangYe()._total_pages("http://b2b.huangye88.com/guangdong/jixie/")
# HuangYe()._p_list("http://b2b.huangye88.com/guangdong/jixie/")
# HuangYe()._detail("http://jingyan2019.b2b.huangye88.com/company_detail.html")
