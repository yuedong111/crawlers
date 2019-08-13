# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import QYLu
from utils.sqlbackends import session_scope
import traceback
from functools import wraps
import re
from collections import OrderedDict


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
            sa = self._p_list(de_u, category)
            count = count + 1

    @second_run
    def _p_list(self, url, category):
        time.sleep(0.2)
        print("list url {}".format(url))
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
                        font = td.find("font", {"color": "#666666"})
                        entype = font.text
                        res[detail[1]] = (detail[0], products, entype)
        for key, value in res.items():
            result["enterpriseName"] = value[0]
            result["products"] = value[1]
            result["businessModel"] = value[2]
            result["url"] = key
            with session_scope() as sess:
                qy = sess.query(QYLu).filter(QYLu.url == key).first()
                if not qy:
                    resu = self._detail(key)
                    result.update(resu)
                    sou = QYLu(**result)
                    sess.add(sou)

    @second_run
    def _detail(self, url):
        time.sleep(0.3)
        print("detail {}".format(url))
        res = {}
        ssd_enterpriseType = "企业经济性质："
        ssd_businessModel = "经营模式："
        ssd_location = "公司注册地："
        ssd_industry = "所属行业："
        ssd_establishedTime = "成立时间："
        ssd_registeredFunds = "注册资金："
        ssd_companyScale = "员工人数："
        ssd_products = "主营产品或服务："
        ssd_representative = "法人代表/负责人："
        ssd_markets = "主营市场："
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        td = soup.find("td", {"width": "210", "align": "center", "valign": "top", "style": "PADDING-TOP: 7px"})
        if not td:
            td = soup.find("td", {"style": "word-break:break-all"})
            if not td:
                return {"others": "信息不存在"}
            res["about"] = td.text.strip()
            table = soup.find("table", {"border": "0", "cellpadding": "2", "cellspacing": "2", "width": "100%"})
            tds = table.find_all("td")
            temp = []
            for td in tds:
                temp.append(td.text)
            tem = locals()
            ot = ""
            for item in temp:
                for k in tem.keys():
                    if "ssd" in k and tem.get(k) in item:
                        res[k.split("_")[-1]] = item[len(tem.get(k)):].strip()
                        break
                else:
                    ot = ot + item + " "
            res["others"] = " ".join(ot.strip().split("\n"))
            table = soup.find("table", {"align": "center", "border": "0", "cellpadding": "0", "cellspacing": "0",
                                        "width": "90%"})
            trs = table.find_all("tr")
            temp = []
            for tr in trs:
                temp.append(tr.text.strip())
            res["contact"] = " ".join(temp[0].split())
            ss_address = "公司地址："
            ss_phone = ["传\u3000\u3000真：", "电\u3000\u3000话：", "移动电话：", "邮\u3000\u3000编："]
            tem = locals()
            tem1 = ""
            for item in temp:
                for k in tem.keys():
                    if "ss" in k and isinstance(tem.get(k), str) and tem.get(k) in item:
                        res[k.split("_")[-1]] = " ".join(item[len(tem.get(k)):].strip().split())
                    elif "ss" in k and isinstance(tem.get(k), list):
                        for tt in tem.get(k):
                            if tt in item:
                                tem1 = tem1 + item + " "
                        res["phone"] = tem1
        else:
            table = td.find("table", {"width": "80%", "border": "0", "cellspacing": "0", "cellpadding": "0"})
            trs = table.find_all("tr")
            temp = []
            for tr in trs:
                td = tr.find("td")
                temp.append(" ".join(td.text.strip().split()))
                if "联系人" in td.text:
                    durl = td.a.get("href")
                    r = self.session.get(durl)
                    soup1 = BeautifulSoup(r.text, "lxml")
                    tds = soup1.find_all("td", {"height": "25"})
                    for td in tds:
                        if hasattr(td, "text") and "详细地址" in td.text:
                            res["address"] = td.text
            ss_contact = "联系人："
            ss_phone = ["手 机：", "电 话："]
            tem = locals()
            tem1 = ""
            for item in temp:
                for k in tem.keys():
                    if "ss" in k and isinstance(tem.get(k), str) and tem.get(k) in item:
                        res[k.split("_")[-1]] = " ".join(item[len(tem.get(k)):].strip().split())
                    elif "ss" in k and isinstance(tem.get(k), list):
                        for tt in tem.get(k):
                            if tt in item:
                                tem1 = tem1 + item + " "
                        res["phone"] = tem1
            mas = soup.find_all("a")
            for a in mas:
                if "about" in a.get("href") and "详细" in a.text:
                    d_u = "http://www.qy6.com" + a.get("href")
                    r = self.session.get(d_u)
                    soup = BeautifulSoup(r.text, "lxml")
                    table = soup.find("table", {"width": "760", "border": "0", "cellspacing": "0", "cellpadding": "0"})
                    td = table.find("td", class_="bady")
                    res["about"] = td.text.strip()
                    tds = table.find_all("td")
                    temp = []
                    for item in tds:
                        temp.append(item.text)
                    tem = locals()
                    ot = ""
                    for item in temp:
                        for k in tem.keys():
                            if "ssd" in k and tem.get(k) in item:
                                res[k.split("_")[-1]] = item[len(tem.get(k)):].strip()
                                break
                        else:
                            ot = ot + item + " "
                    res["others"] = " ".join(ot.strip().split("\n"))
        return res

    def start(self):
        self._category()


if __name__ == "__main__":
    ZHQYL().start()

# ZHQYL()._p_list("http://www.qy6.com/qyml/fqyC01_p1.html", "")
# ZHQYL()._detail("http://www.qy6.com/qyml/compchengyi88.html")
# ZHQYL()._detail("http://www.qy6.com/qyml/compxingyuejiguang.html")
# ZHQYL()._detail("http://www.qy6.com/qyml/compjxzbgs.html")
