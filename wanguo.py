# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session
import time
from utils.models import WGQY
from utils.sqlbackends import session_scope


class WG:

    url = "https://www.trustexporter.com/chongqing/pn{}.htm"

    def __init__(self):
        self.session = create_session()

    def parse_page(self):
        count = 123
        while count < 251:
            print(self.url.format(count))
            r = self.session.get(self.url.format(count), verify=False)
            soup = BeautifulSoup(r.text, "lxml")
            div = soup.find("div", class_="left_box")
            uls = div.find_all("ul")
            for item in uls:
                res = {}
                a = item.find("a")
                res["enterpriseName"] = a.get("title")
                res["url"] = a.get("href")
                lis = item.find_all("li")
                mb = lis[1].text
                res["primaryBusiness"] = mb.strip()
                if len(lis) > 2:
                    phone = lis[2].text.strip()
                    res["phone"] = phone
                # result = self.parse_detail(res["url"])
                # res.update(result)
                # print(res)
                with session_scope() as sess:
                    wgs = sess.query(WGQY).filter(WGQY.url == res["url"]).first()
                    if not wgs:
                        result = self.parse_detail(res["url"])
                        res.update(result)
                        wg = WGQY(**res)
                        sess.add(wg)
            count = count + 1

    def parse_detail(self, url):
        time.sleep(0.5)
        print("detail {}".format(url))
        res = {}
        r = self.session.get(url, verify=False)
        soup = BeautifulSoup(r.text, "lxml")
        cname = soup.find("div", {"id": "logoi"}).text.strip()
        index = cname.find("http")
        cname = cname[:index].strip()
        tda = soup.find("td", {"id": "side"})
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
        divs = soup.find_all("div", class_="mainkcontent")
        content = divs[0].find("div", class_="content")
        if content:
            res["about"] = content.text
        div = divs[-1]
        tds = div.find_all("td")
        temp = {}
        for index, value in enumerate(tds):
            if len(tds) > index + 1:
                temp[value.text.strip()] = tds[index+1].text.strip()
            index = index + 2
        for key in temp.keys():
            if "成立时间：" in key:
                res["establishedTime"] = temp[key]
            elif "注册资金：" in key:
                res["registeredFunds"] = temp[key]
            elif "所属行业：" in key:
                res["category"] = temp[key]
            elif "所 在 地：" in key:
                res["location"] = temp[key]
        return res

    def start(self):
        self.parse_page()


if __name__ == "__main__":
    WG().start()


