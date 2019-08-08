# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import BFZY
from utils.sqlbackends import session_scope
import re
import json
from requests.exceptions import ConnectionError


def reconnect(fn):
    def decorete(*args, **kwargs):
        while True:
            try:
                res = fn(*args, **kwargs)
                break
            except ConnectionError:
                print("重连 {}".format(kwargs.get("url")))
                time.sleep(2)
        return res

    return decorete


class BaFZY:
    url = "https://www.b2b168.com/chongqingqiye/"
    url_home = "https://www.b2b168.com/page-company.html"
    fpa = re.compile(r"\d+")

    def __init__(self):
        self.session = create_session()
        self.jump = "beijingqiye/dongchengqu/andingmenjiedao/l-23.html"
        self.status = False

    def get_cate(self, url, locate):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        sdiv = soup.find("div", class_="subNav")
        # area = sdiv.text.split()[-1]
        # area = area.strip()[:-2]
        div = soup.find("div", class_="mach_list clearfix")
        dls = div.find_all("dl")
        for item in dls:
            mas = item.find_all("a")
            cate = mas[0].get("title")
            area = cate[:-2]
            for a in mas[1:]:
                c_u = "https://www.b2b168.com" + a.get("href")
                sa = self.total_pages(c_u, area, locate)
                # print(c_u)

    def total_pages(self, url, area, locate):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="pages")
        res = self.fpa.findall(div.text)
        try:
            total_pages = int(res[0])
        except:
            total_pages = 0
            return
        count = 1
        while count < total_pages + 1:
            lurl = url + "l-{}.html"
            d_u = lurl.format(count)
            if self.jump in d_u:
                self.status = True
            if not self.status:
                count = count + 1
                continue
            self.p_list(d_u, area, locate)
            count += 1

    @reconnect
    def p_list(self, url, area, locate):
        print("page url {}".format(url))
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find("ul", class_="list")
        mas = ul.find_all("a")
        for a in mas:
            res = {}
            res["locate"] = locate
            res["area"] = area
            name = a.get("title")
            res["enterpriseName"] = name
            if not a.get("href").startswith("http"):
                d_u = "https:" + a.get("href")
            else:
                d_u = a.get("href")
            res["url"] = d_u
            try:
                temp = a.next_sibling.next_sibling
                font = temp.find("font")
            except:
                font = None
                print("error {}".format(url))
            if font:
                res["updateTime"] = font.text
            with session_scope() as sess:
                wgs = sess.query(BFZY).filter(BFZY.url == d_u).first()
                if not wgs:
                    resu = self.detail(d_u)
                    res.update(resu)
                    wg = BFZY(**res)
                    sess.add(wg)
                    print(res)

    def detail(self, url):
        print(url)
        time.sleep(0.7)
        res = {}
        res["url"] = url
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="Cneirong")
        if div:
            about = div.find("ul", class_="Cgsjj")
            if hasattr(about.next_sibling, "text"):
                res["about"] = about.next_sibling.text
            else:
                res["about"] = about.text
            temp = div.find("dl", class_="codl")
            dds = temp.find_all("dd")
            people = dds[2].text
            res["address"] = dds[0].text
            res["representative"] = "".join(people.split())
            phone = dds[3].text
            res["phone"] = phone
            home_url = dds[-1].text
            res["homePage"] = home_url
            primarys = div.find_all("ul", class_="cgsxx")
            for primary in primarys:
                trs = primary.find_all("tr")
                deal = []
                for item in trs:
                    for item1 in item:
                        if hasattr(item1, "text"):
                            deal.append(item1.text)
                for item in range(0, len(deal), 2):
                    item1 = deal[item]
                    res[item1] = deal[item + 1]
            res = dict([(k, v) for k, v in res.items() if v])
        else:
            li = soup.find("li", class_="CHOME")
            if li:
                about = li.text.strip()
                res["about"] = about
            uls = soup.find_all("ul", class_="box-rightsidebar3")
            temp = []
            for ul in uls:
                tds = ul.find_all("td")
                for item in tds:
                    temp.append(item.text)
            for item in range(0, len(temp), 2):
                item1 = temp[item]
                res[item1] = temp[item + 1]
            res = {k: v for k, v in res.items() if v}
            lis = soup.find_all("li", class_="x4")
            for li in lis:
                if hasattr(li, "text"):
                    if "所在地区" in li.text:
                        dd = ""
                        mas = li.find_all("a")
                        for a in mas:
                            dd = dd + a.text + " "
                        res["address"] = dd
        res["others"] = {}
        for key in list(res.keys()):
            if "法人代表或负责" in key:
                res["representative"] = "".join(res[key].split())
                res.pop(key)
            elif "成立时间" in key:
                res["establishedTime"] = res[key].strip()
                res.pop(key)
            elif "注册资金" in key:
                res["registeredFunds"] = res[key]
                res.pop(key)
            elif key not in ["others", "url", "about", "representative", "establishedTime", "address", "phone"]:
                res["others"].update({key: res[key]})
                res.pop(key)
        res["others"] = json.dumps(res["others"])
        if "about" in res:
            tem = res["about"].split("；")
            for item in tem:
                t = item.split("：")
                if "注册资金" == t[0]:
                    res["registeredFunds"] = t[1]
        return res

    def parse_provice(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        divs = soup.find_all("div", class_="map")
        for div in divs:
            ul = div.find("ul", class_="unit-tit")
            if hasattr(ul, "text") and ul.text == "所有地区":
                mas = div.find_all("a")
                for a in mas:
                    if "chongqing" not in a.get("href"):
                        d_url = "https://www.b2b168.com" + a.get("href")
                        locate = a.text[:-2]
                        self.get_cate(d_url, locate)


if __name__ == "__main__":
    BaFZY().parse_provice()
