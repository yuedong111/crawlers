# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import WGQY
from utils.sqlbackends import session_scope
import traceback
from functools import wraps


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
                if count >= 3:
                    count = 0
                    return "too many retrys"
                res = decorate(*args, **kwargs)
                break
        return res

    return decorate


class WG:
    url_home = "https://www.trustexporter.com"
    url = "https://www.trustexporter.com/chongqing/pn{}.htm"

    def __init__(self):
        self.session = create_session()
        self.jump = "weifang/pn25.htm"
        self.status = False

    def parse_page(self, url, area):
        d_url = url + "pn{}.htm"
        try:
            count = 1
            r = self.session.get(d_url.format(count))
            soup = BeautifulSoup(r.text, "lxml")
            divp = soup.find("div", class_="pages")
            if not divp:
                total_page = 1
            else:
                cite = divp.find("cite").text
                temp = cite.split("/")[-1]
                total_page = int(temp[:-1])
            print("{} gong {} ye ".format(url, total_page))
            while count < total_page + 1:
                print(d_url.format(count))
                if not self.status:
                    if self.jump in d_url.format(count):
                        self.status = True
                    count = count + 1
                    continue
                sa = self.final_parse(d_url, count, area)
                count = count + 1
        except Exception as e:
            print(e)

    @second_run
    def final_parse(self, url, count, area):
        r = self.session.get(url.format(count))
        print("kaishi jiexi ")
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="left_box")
        uls = div.find_all("ul")
        with session_scope() as sess:
            for item in uls:
                res = {}
                res["location"] = area
                a = item.find("a")
                res["enterpriseName"] = a.get("title")
                res["url"] = a.get("href")
                lis = item.find_all("li")
                mb = lis[1].text
                res["primaryBusiness"] = mb.strip()
                if len(lis) > 2:
                    phone = lis[2].text.strip()
                    res["phone"] = phone
                wgs = sess.query(WGQY).filter(WGQY.url == res["url"]).first()
                if not wgs:
                    result = self.parse_detail(res["url"])
                    res.update(result)
                    wg = WGQY(**res)
                    sess.add(wg)
            print("wanbi")

    def parse_detail(self, url):
        time.sleep(0.5)
        print("detail {}".format(url))
        res = {}
        self.session.headers[
            "Cookie"] = "Hm_lvt_908376e0e856e8b64f7af6081984a5d1=1564651662,1564966733; Hm_lpvt_908376e0e856e8b64f7af6081984a5d1=1564968718"
        try:
            r = self.session.get(url)
        except:
            r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        cname = soup.find("div", {"id": "logoi"}).text.strip()
        index = cname.find("http")
        cname = cname[:index].strip()
        tda = soup.find("td", {"id": "side"})
        try:
            sc = tda.find_all("div", class_="sidekcontent")
            for ds in sc:
                if ds.previous_sibling and ds.previous_sibling.previous_sibling.div.text.strip() == cname:
                    divsc = ds
                    lis = divsc.find_all("li")
                    tem = ''
                    for item in lis:
                        if "地址" in item.text:
                            res["address"] = item.text
                        else:
                            tem = tem + item.text + " "
                    res["phone"] = tem
        except Exception as e:
            print(e)
        divs = soup.find_all("div", class_="mainkcontent")
        content = divs[0].find("div", class_="content")
        if content:
            res["about"] = content.text.encode("gbk", errors="ignore").decode("gbk")
        div = divs[-1]
        tds = div.find_all("td")
        temp = {}
        for index, value in enumerate(tds):
            if len(tds) > index + 1:
                temp[value.text.strip()] = tds[index + 1].text.strip()
            index = index + 2
        for key in temp.keys():
            if "成立时间：" in key:
                res["establishedTime"] = temp[key]
            elif "注册资金" in key:
                res["registeredFunds"] = temp[key]
            elif "所属行业：" in key:
                res["category"] = temp[key]
            elif "所 在 地：" in key:
                res["location"] = temp[key]
        return res

    def province(self):
        r = self.session.get(self.url_home)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", class_="neirong www")
        mas = div.find_all("a")
        for a in mas:
            self.parse_page(a.get("href"), a.text)

    def start(self):
        self.province()


if __name__ == "__main__":
    while True:
        try:
            WG().start()
            break
        except Exception as e:
            print(traceback.print_exc())
            time.sleep(300)
