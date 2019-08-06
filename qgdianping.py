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
import traceback

url = "http://www.dianping.com/chongqing/ch80"

item_url = {
    # "meishi": "http://www.dianping.com/chongqing/ch10",
    # "xiuxianyule": "http://www.dianping.com/chongqing/ch30",
    # "jiehun": "http://www.dianping.com/chongqing/ch55",
    # "liren": "http://www.dianping.com/chongqing/ch50",
    # "qinzi": "http://www.dianping.com/chongqing/ch70",
    # "zhoubianyou": "http://www.dianping.com/chongqing/ch35",
    # "yundongjianshen": "http://www.dianping.com/chongqing/ch45",
    "shopping": "http://www.dianping.com/chongqing/ch20",
    "jiazhuang": "http://www.dianping.com/chongqing/ch90/g90",
    "xuexipeixun": "http://www.dianping.com/chongqing/ch75",
    "shenghuofuwu": "http://www.dianping.com/chongqing/ch80",
    "yiliaojiankang": "http://www.dianping.com/chongqing/ch85",
    "aiche": "http://www.dianping.com/chongqing/ch65",
    "chongwu": "http://www.dianping.com/chongqing/ch95",
    "hotel": "http://www.dianping.com/chongqing/hotel/"
}

item_city = {
    "meishi": "http://www.dianping.com/{}/ch10",
    "xiuxianyule": "http://www.dianping.com/{}/ch30",
    "jiehun": "http://www.dianping.com/{}/ch55",
    "liren": "http://www.dianping.com/{}/ch50",
    "qinzi": "http://www.dianping.com/{}/ch70",
    "zhoubianyou": "http://www.dianping.com/{}/ch35",
    "yundongjianshen": "http://www.dianping.com/{}/ch45",
    "shopping": "http://www.dianping.com/{}/ch20",
    "jiazhuang": "http://www.dianping.com/{}/ch90/g90",
    "xuexipeixun": "http://www.dianping.com/{}/ch75",
    "shenghuofuwu": "http://www.dianping.com/{}/ch80",
    "yiliaojiankang": "http://www.dianping.com/{}/ch85",
    "aiche": "http://www.dianping.com/{}/ch65",
    "chongwu": "http://www.dianping.com/{}/ch95",
    "hotel": "http://www.dianping.com/{}/hotel/"
}

def yanzhengma_warning(fn):

    def decorete(*args, **kwargs):
        while True:
            try:
                res = fn(*args, **kwargs)
                break
            except Exception as e:
                print("输入验证码 {}{}".format(kwargs.get("url"), traceback.print_exc()))
                time.sleep(2)
        return res
    return decorete


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
        self.jump = "anshan/ch10"
        self.status = False
        # self.browser = create_webdriver()

    @staticmethod
    def parse_city():
        with open("static/citylist.html", "r", encoding="utf-8") as f:
            r = f.read()
            soup = BeautifulSoup(r, "lxml")
            mas = soup.find_all("a", class_="link onecity")
            for a in mas:
                t = a.get("href").split("/")[-2]
                yield (t, a.text)

    @yanzhengma_warning
    def page_item(self, url, area, locate):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        if "ch70" in url:
            div = soup.find("div", {"id": "J_boxList"})
            lis = div.find_all("li")
            for li in lis:
                res = {}
                res["locate"] = locate
                res["area"] = area.strip()
                name = li.find("a", class_="shopname")
                if name:
                    res["shop"] = name.get("title")
                else:
                    break
                d_u = "http:" + li.a.get("href")
                res["url"] = d_u
                p = li.find("p", class_="baby-info-scraps")
                span = p.find("span", class_="key-list")
                if span:
                    res["address"] = span.text.strip()
                mk = li.find("p", class_="remark")
                res["score"] = mk.span.get("title")
                dz = DZDianPing(**res)
                with session_scope() as sess:
                    qxc = sess.query(DZDianPing).filter(DZDianPing.url == res["url"]).first()
                    if not qxc:
                        sess.add(dz)
                        print(res)
        elif "ch90" in url:
            divs = soup.find_all("div", class_="shop-info")
            for item in divs:
                res= {}
                res["locate"] = locate
                res["area"] = area
                div = item.find("div", class_="shop-title")
                h3 = div.h3
                a = h3.a
                if a:
                    d_u = "http:" + a.get("href")
                    res["url"] = d_u
                    res["shop"] = a.text
                div = item.find("div", class_="row shop-info-text-i")
                span = div.span
                if span:
                    res["score"] = span.text
                span = div.find("span", class_="shop-location")
                res ["address"] = " ".join(span.text.split())
                dz = DZDianPing(**res)
                with session_scope() as sess:
                    qxc = sess.query(DZDianPing).filter(DZDianPing.url == res["url"]).first()
                    if not qxc:
                        sess.add(dz)
                        print(res)
        else:
            div = soup.find("div", {"id": "shop-all-list"})
            if not div:
                return "no content"
            lis = div.find_all("li")
            for item in lis:
                res = {}
                res["locate"] = locate
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

    @yanzhengma_warning
    def parse_cate(self, url, locate):
        print(url)
        if self.jump in url:
            self.status = True
        if not self.status:
            return
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        if "ch55" in url:
            li = soup.find("li", class_="t-item-box t-district J_li")
            if not li:
                j_u = url+"/p{}"
                count = 1
                while count < 51:
                    jiehun_url = j_u.format(count)
                    print(jiehun_url)
                    self.parse_jiehun(jiehun_url, locate, locate)
                    time.sleep(0.5)
                    count = count + 1
            else:
                div = li.find("div", class_="t-list")
                lis = div.find_all("li")
                for item in lis:
                    a = item.find("a")
                    if a.get("href"):
                        url = self.url_home + a["href"] + "p{}"
                        count = 1
                        while count < 51:
                            jiehun_url = url.format(count)
                            print(jiehun_url)
                            if hasattr(a, "text"):
                                self.parse_jiehun(jiehun_url, a.text, locate)
                            else:
                                self.parse_jiehun(jiehun_url, "未知", locate)
                            time.sleep(0.5)
                            count = count + 1
        elif "hotel" in url:
            self.session.headers["Cookie"] = """navCtgScroll=0; _hc.v="\"85fd17cf-fdb1-490d-9e4e-2b7090d0ae6c.1562822672\""; _lxsdk_cuid=16c22ac17a87c-0b6f1684f738ee-36664c08-1fa400-16c22ac17a9c8; _lxsdk=16c22ac17a87c-0b6f1684f738ee-36664c08-1fa400-16c22ac17a9c8; s_ViewType=10; aburl=1; Hm_lvt_4c4fc10949f0d691f3a2cc4ca5065397=1564034271; cy=57; cye=alashan; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1563950118,1564112965,1564448583,1565075956; wed_user_path=1040|0; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1565076978; cityInfo=%7B%22cityId%22%3A57%2C%22cityName%22%3A%22%E9%98%BF%E6%8B%89%E5%96%84%22%2C%22provinceId%22%3A0%2C%22parentCityId%22%3A0%2C%22cityOrderId%22%3A0%2C%22isActiveCity%22%3Afalse%2C%22cityEnName%22%3A%22alashan%22%2C%22cityPyName%22%3Anull%2C%22cityAreaCode%22%3Anull%2C%22cityAbbrCode%22%3Anull%2C%22isOverseasCity%22%3Afalse%2C%22isScenery%22%3Afalse%2C%22TuanGouFlag%22%3A0%2C%22cityLevel%22%3A0%2C%22appHotLevel%22%3A0%2C%22gLat%22%3A0%2C%22gLng%22%3A0%2C%22directURL%22%3Anull%2C%22standardEnName%22%3Anull%7D; lastVisitUrl=%2Falashan%2Fhotel%2Fr103579; selectLevel=%7B%7D; _lxsdk_s=16c65c0d922-e1a-bd4-95%7C%7C1890"""
            r = self.session.get(url)
            soup = BeautifulSoup(r.text, "lxml")
            div = soup.find("div", class_="type area")
            if not div:
                div = soup.find("div", class_="nav")
            div = div.find("div", class_="sub-filter-region-wrapper")
            ma = div.find_all("a")
            for a in ma:
                if a.get("href"):
                    count = 1
                    while count < 51:
                        url = self.url_home + a["href"] + "p{}".format(count)
                        print(url)
                        self.parse_hotel(url, a.get("title"), locate)
                        count = count + 1
                        time.sleep(0.5)
        elif "ch70" in url:
            li = soup.find("li", class_="t-item-box t-district J_li")
            if not li:
                j_u = url+"/p{}"
                count = 1
                while count < 51:
                    jiehun_url = j_u.format(count)
                    self.parse_jiehun(jiehun_url, locate, locate)
                    time.sleep(0.5)
                    count = count + 1
            else:
                div = li.find("div", class_="t-list")
                mli = li.find_all("a")
                for a in mli:
                    if a.get("href") and a.get("href").startswith("/"):
                        if a.get("href") == "/chongqing/ch70":
                            qdurl = "http://www.dianping.com" + a.get("href") + "/p{}"
                        else:
                            qdurl = "http://www.dianping.com" + a.get("href") + "p{}"
                        count = 1
                        while count < 51:
                            url1 = qdurl.format(count)
                            time.sleep(0.5)
                            try:
                                print(url1)
                                self.page_item(url1, a.text, locate)
                                count = count + 1
                            except Exception as e:
                                print(e)
                                break
        elif "ch90" in url:
            div = soup.find("div", {"id": "J_shopsearch"})
            div = div.find_all("div", class_="row")[1]
            lis = div.find_all("li")
            for item in lis:
                a = item.a
                if a:
                    d_u = "http:" + a.get("href") + "p{}"
                    count = 1
                    while count < 51:
                        time.sleep(0.5)
                        try:
                            print(d_u.format(count))
                            self.page_item(d_u.format(count), a.text, locate)
                            count = count + 1
                        except Exception as e:
                            print(e)
                            break
        else:
            div = soup.find("div", {"id": "J_nt_items"})
            manya = div.find_all("a")
            for a in manya:
                if a.get("href"):
                    count = 1
                    while count < 51:
                        url = a["href"] + "p{}".format(count)
                        time.sleep(0.5)
                        try:
                            print(url)
                            self.page_item(url, a.get("data-click-title"), locate)
                            count = count + 1
                        except Exception as e:
                            print(e)
                            break

    def parse_jiehun(self, url, area, locate):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find('div', {"id": "J_boxList"})
        ul = div.find("ul", class_="shop-list")
        lis = ul.find_all("li")
        for item in lis:
            res = {}
            res["locate"] = locate
            res["area"] = area.strip()
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
            score = item.find("p", class_="remark")
            if score:
                res["score"] = score.span.get("title")
            # r2 = self.session.get(jiehun_url)
            # print(jiehun_url)
            # soup = BeautifulSoup(r2.text, "lxml")
            # div = soup.find("div", class_="offers-box")
            # if not div:
            #     div = soup.find("div", class_="shop-wrap")
            #     if not div:
            #         div = soup.find_all("div", {"id": "J_boxYouhui", "class": "textshow"})[0]
            #         span = div.find_all("span", class_="fl")[0]
            #         if span.get("title"):
            #             res["address"] = span.get("title")
            #         sp = div.find_all("span", class_="icon-phone")[0]
            #         res["phone"] = sp.text
            #     else:
            #         h1 = div.find("h1", class_="shop-title")
            #         span = div.find("span", class_="fl road-addr")
            #         address = span.text.strip()
            #         res["address"] = address
            #         phone = div.find("span", class_="icon-phone")
            #         res["phone"] = " ".join(phone.text.split()).strip()
            # else:
            #     span = div.find("span", class_="info-name")
            #     address = span["title"]
            #     res["address"] = address.strip()
            #     p = div.find("p", class_="expand-info tel")
            #     sp = p.find("span", class_="item")
            #     res["phone"] = " ".join(sp.text.split()).strip()
            dz = DZDianPing(**res)
            with session_scope() as sess:
                qxc = sess.query(DZDianPing).filter(DZDianPing.url == res["url"]).first()
                if not qxc:
                    sess.add(dz)
                    print(res)

    def parse_hotel(self, url, area, locate):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find("ul", class_="hotelshop-list")
        lis = ul.find_all("li", class_="hotel-block")
        for li in lis:
            res = {}
            res["locate"] = locate
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
                    try:
                        score = float(int(span["class"][-1][-2:]) / 10)
                    except:
                        score = 0
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
        for city in self.parse_city():
            if city[0] != "chongqing":
                for item in item_city:
                    ss = self.parse_cate(item_city[item].format(city[0]), city[1])

    def __del__(self):
        # self.browser.quit()
        self.session.close()


if __name__ == "__main__":
    try:
        DianPing().start()
    except Exception as e:
        print(traceback.print_exc())
    # while True:
    #     try:
    #         DianPing().start()
            # time.sleep(600)
        # except Exception as e:
        #     print(traceback.print_exc())
            # time.sleep(1800)




# DianPing().parse_cate("http://www.dianping.com/chongqing/hotel")
# DianPing().page_item("http://www.dianping.com/chongqing/ch10/r1608")
# DianPing().parse_jiehun("http://www.dianping.com/chongqing/ch55/p1")
# DianPing().parse_phone("http://www.dianping.com/shop/92726787", "lsd")
# DianPing().parse_hotel("http://www.dianping.com/chongqing/hotel/r102291")
# DianPing().parse_hotel_detail("http://www.dianping.com/shop/79272817")
#     DianPing().parse_jiehun("http://www.dianping.com/chongqing/ch55/r42p1", "渝中区")
#     DianPing().parse_cate("http://www.dianping.com/chongqing/ch70")