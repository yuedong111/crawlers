# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from utils.make_sessions import create_dianping_session, create_webdriver
from utils.models import DZDianPing
from utils.sqlbackends import session_scope
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from fontTools import ttLib
import pickle
import os
import time

url = "http://www.dianping.com/chongqing/ch80"

item_url = {
    "meishi": "http://www.dianping.com/chongqing/ch10",
    "xiuxianyule": "http://www.dianping.com/chongqing/ch30",
    "jiehun": "http://www.dianping.com/chongqing/ch55",
    "liren": "http://www.dianping.com/chongqing/ch50",
    "qinzi": "http://www.dianping.com/chongqing/ch70",
    "zhoubianyou": "http://www.dianping.com/chongqing/ch35",
    "yundongjianshen": "http://www.dianping.com/chongqing/ch45",
    "shopping": "http://www.dianping.com/chongqing/ch20",
    "jiazhuang": "http://www.dianping.com/chongqing/ch90",
    "xuexipeixun": "http://www.dianping.com/chongqing/ch75",
    "shenghuofuwu": "http://www.dianping.com/chongqing/ch80",
    "yiliaojiankang": "http://www.dianping.com/chongqing/ch85",
    "aiche": "http://www.dianping.com/chongqing/ch65",
    "chongwu": "http://www.dianping.com/chongqing/ch95",
    "hotel": "http://www.dianping.com/chongqing/hotel/"
}


class Rosetta(object):
    """source from https://github.com/loricheung/anti-DPAntiSpider.git"""

    def __init__(self, font_file):
        MAPPING_FILE = './character'
        self.font = ttLib.TTFont(font_file)
        self.table = pickle.load(open(MAPPING_FILE, 'rb'))

    def _is_normal_char(self, char):
        if len(char) <= 1:
            if ord(char) < 0x9FEF:
                return True
            else:
                char = char.encode('unicode_escape')
                if hex(int(char.replace(b'\\u', b'').decode(), 16)) < '0xe000':
                    return True
        else:
            if any([ord(c) < 0x9FEF for c in char]):
                return True

    def _get_chinese_char(self, chr):
        uni_chr = (b'uni' + chr.replace(b' ', b'').replace(b'\\n', b'').replace(b'\\t', b'').replace(b'\\u',
                                                                                                     b'')).decode()
        index = self.font.getGlyphID(uni_chr)
        return self.table[index - 2]

    def _convert(self, chr):
        if chr.isascii():
            return chr
        if self._is_normal_char(chr):
            return chr
        try:
            chr_b = chr.encode('unicode_escape', errors='ignore').replace(b' ', b'').replace(b'\\n', b'').replace(
                b'\\t', b'').replace(b'\\xa0', b', ')
            return self._get_chinese_char(chr_b)
        except Exception:
            return chr

    def convert(self, chr_list):
        # chr_list = filter(lambda x: len(x.strip()) != 0, chr_list)
        chr_list = list(map(self._convert, [c for c in chr_list]))
        return ''.join([str(c) for c in chr_list])


class DianPing:
    css_pattern = re.compile(r'\/\/s3plus\.meituan\.net/v1/(.*?)\/svgtextcss/(.*?)\.css')
    woff_pattern = re.compile(r'\/\/s3plus\.meituan\.net/v1/mss_\w+\/font\/\w+\.woff')

    def __init__(self):
        self.session = create_dianping_session()
        self.url_home = "http://www.dianping.com"
        self.jump = "/ch10/r1632"
        self.status = False
        # self.browser = create_webdriver()

    def page_item(self, url, area):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", {"id": "shop-all-list"})
        if not div:
            return "no content"
        lis = div.find_all("li")
        for item in lis:
            res = {}
            res["area"] = area
            a = item.find("a", {"data-hippo-type": "shop"})
            res["shop"] = a["title"]
            detail_url = a["href"]
            res["url"] = detail_url
            d = item.find("div", class_="operate J_operate Hide")
            if d:
                manya = d.find_all("a")
                for a in manya:
                    if a["class"] == ["o-map", "J_o-map"]:
                        res["address"] = a["data-address"]
                        break
            comm = item.find("div", class_="comment")
            res["score"] = comm.span["title"]
            dz = DZDianPing(**res)
            with session_scope() as sess:
                qxc = sess.query(DZDianPing).filter(DZDianPing.url == res["url"]).first()
                if not qxc:
                    sess.add(dz)
                    print(res)
            # phone = self.parse_phone(detail_url, "xx")

    def parse_phone(self, url, url2):

        """这部分弃用"""

        r1 = self.session.get(url)
        r1 = r1.text
        # self.browser.get(url2)
        # self.browser.get(url)
        # WebDriverWait(self.browser, 10).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, '//*[@id="basic-info"]')))
        # r1 = self.browser.page_source
        # if "ETag" in r1.headers:
        # self.session.headers["If-None-Match"] = r1.headers["ETag"]
        self.session.headers["Referer"] = url
        self.session.headers["Host"] = "s3plus.meituan.net"
        css = self.css_pattern.search(r1)
        if css:
            css_url = css.group(0)
            css_content = self.session.get('http:' + css_url, stream=True)
            woff = self.woff_pattern.search(css_content.text)
            if woff:
                woff_url = woff.group()
                local_filename = woff_url.split('/')[-1]
                print(local_filename)
                with self.session.get("http:" + woff_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
        soup = BeautifulSoup(r1, "lxml")
        div = soup.find("div", id="not-found-tip")
        if div or not r1.strip():
            return "not-found-tip"
        div = soup.find("div", {"id": "basic-info"})
        p = div.find("p", class_="expand-info tel")
        phone = p.find("span", class_="item")
        res = []
        if not phone:
            ds = p.children
            enph = p.text
            for d in ds:
                if hasattr(d, "text"):
                    if d.text:
                        res.append(d.text)
                elif "\xa0 1" in d:
                    res.append(" ")
                    res.append("1")
                elif d.strip():
                    res.append(d)
            rosetta = Rosetta(local_filename)
            res = rosetta.convert(res)
            index = res.find("电话：")
            phone = res[index + len("电话："):]
        else:
            phone = phone.text
        print(phone)
        p = div.find("p", class_="info info-indent")
        otime = p.find("span", class_="item")
        res = []
        if not otime:
            ds = p.children
            enph = p.text
            for d in ds:
                if hasattr(d, "text"):
                    if d.text:
                        res.append(d.text)
                elif " 11:" in d:
                    res.append(" ")
                    # res.append("1")
                elif d.strip():
                    res.append(d)
            rosetta = Rosetta(local_filename)
            res = rosetta.convert(res)
            otime = res
            # index = res.find("电话：")
            # phone = res[index + len("电话："):]
        else:
            otime = otime.text
        print(otime)
        os.remove(local_filename)
        return phone

    def parse_cate(self, url):
        print(url)
        r = self.session.get(url)
        # with open("test.html", 'w', encoding="utf-8") as f:
        # f.write(r.text)
        soup = BeautifulSoup(r.text, "lxml")
        if "ch55" in url:
            li = soup.find("li", class_="t-item-box t-district J_li")
            div = li.find("div", class_="t-list")
            lis = div.find_all("li")
            for item in lis:
                a = item.find("a")
                if a.get("href"):
                    url = self.url_home + a["href"]
                    count = 1
                    while count < 51:
                        url = url + "p{}".format(count)
                        print(url)
                        if hasattr(a, "text"):
                            self.parse_jiehun(url, a.text)
                        else:
                            self.parse_jiehun(url, "未知")
                        time.sleep(0.5)
                        count = count + 1
        elif "hotel" in url:
            div = soup.find("div", class_="type area")
            div = div.find("div", class_="sub-filter-region-wrapper")
            ma = div.find_all("a")
            for a in ma:
                if a.get("href"):
                    count = 1
                    while count < 51:
                        url = self.url_home + a["href"] + "p{}".format(count)
                        print(url)
                        self.parse_hotel(url, a.get("title"))
                        count = count + 1
                        time.sleep(0.5)
        else:
            div = soup.find("div", {"id": "J_nt_items"})
            manya = div.find_all("a")
            for a in manya:
                if a.get("href"):
                    # if self.jump in a.get("href"):
                    #     self.status = True
                    # if not self.status:
                    #     continue
                    count = 1
                    while count < 51:
                        url = a["href"] + "p{}".format(count)
                        time.sleep(0.5)
                        try:
                            print(url)
                            self.page_item(url, a.get("data-click-title"))
                            count = count + 1
                        except Exception as e:
                            print(e)
                            break

    def parse_jiehun(self, url, area):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find('div', {"id": "J_boxList"})
        ul = div.find("ul", class_="shop-list")
        lis = ul.find_all("li")
        for item in lis:
            res = {}
            res["area"] = area
            a = item.a
            if a.get("title"):
                res["shop"] = a.get("title")
            if a.get("href"):
                jiehun_url = self.url_home + a.get("href")
                index = jiehun_url.find("?")
                res["url"] = jiehun_url[:index]
            p = item.find_all("p", class_="area-list")
            if p:
                p = p[0]
                res["address"] = p.text.strip()
            score = item.find("span", class_="item-rank-rst irr-star40")
            if score:
                res["score"] = score.get("title")
            r2 = self.session.get(jiehun_url)
            soup = BeautifulSoup(r2.text, "lxml")
            div = soup.find("div", class_="offers-box")
            if not div:
                div = soup.find("div", class_="shop-wrap")
                h1 = div.find("h1", class_="shop-title")
                span = div.find("span", class_="fl road-addr")
                address = span.text.strip()
                res["address"] = address
                phone = div.find("span", class_="icon-phone")
                res["phone"] = " ".join(phone.text.split()).strip()
            else:
                span = div.find("span", class_="info-name")
                address = span["title"]
                res["address"] = address.strip()
                p = div.find("p", class_="expand-info tel")
                sp = p.find("span", class_="item")
                res["phone"] = " ".join(sp.text.split()).strip()
            dz = DZDianPing(**res)
            with session_scope() as sess:
                qxc = sess.query(DZDianPing).filter(DZDianPing.url == res["url"]).first()
                if not qxc:
                    sess.add(dz)
                    print(res)

    def parse_hotel(self, url, area):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find("ul", class_="hotelshop-list")
        lis = ul.find_all("li", class_="hotel-block")
        for li in lis:
            res = {}
            res["area"] = area
            h2 = li.find("h2", class_="hotel-name")
            a = h2.find("a", class_="hotel-name-link")
            name = a.text
            res["shop"] = name
            place = li.find("p", class_="place")
            a = place.find("a")
            place = a.text
            res["address"] = place
            div = li.find("div", class_="remark")
            if div:
                span = div.find("span")
                if span.get("class"):
                    score = float(int(span["class"][-1][-2:]) / 10)
                    res["score"] = score
            data_poi = li.get("data-poi")
            hotel_url = "http://www.dianping.com/shop/" + data_poi
            res["url"] = hotel_url
            try:
                address = self.parse_hotel_detail(hotel_url)
                res["address"] = address
            except Exception as e:
                print("error when parse hotel address {}".format(e))
            dz = DZDianPing(**res)
            with session_scope() as sess:
                qxc = sess.query(DZDianPing).filter(DZDianPing.url == res["url"]).first()
                if not qxc:
                    sess.add(dz)
                    print(res)

    def parse_hotel_detail(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        span = soup.find_all("span", class_="hotel-address")[0]
        return span.text

    def start(self):
        for item in item_url:
            self.parse_cate(item_url[item])

    def __del__(self):
        # self.browser.quit()
        self.session.close()


if __name__ == "__main__":
    DianPing().start()

# DianPing().parse_cate("http://www.dianping.com/chongqing/hotel")
# DianPing().page_item("http://www.dianping.com/chongqing/ch10/r1608")
# DianPing().parse_jiehun("http://www.dianping.com/chongqing/ch55/p1")
# DianPing().parse_phone("http://www.dianping.com/shop/92726787", "lsd")
# DianPing().parse_hotel("http://www.dianping.com/chongqing/hotel/r102291")
# DianPing().parse_hotel_detail("http://www.dianping.com/shop/79272817")
