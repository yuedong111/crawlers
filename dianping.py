# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from utils.make_sessions import create_dianping_session
import re
from fontTools import ttLib
import pickle
import os

url = "http://www.dianping.com/chongqing/ch80"

item_url = {"meishi": "http://www.dianping.com/chongqing/ch10",
            "xiuxianyule": "http://www.dianping.com/chongqing/ch30",
            "jiehun": "http://www.dianping.com/chongqing/ch55",}


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
        uni_chr = (b'uni' + chr.replace(b' ', b'').replace(b'\\n', b'').replace(b'\\t', b'').replace(b'\\u', b'')).decode()
        index = self.font.getGlyphID(uni_chr)
        return self.table[index - 2]

    def _convert(self, chr):
        if chr.isascii():
            return chr
        if self._is_normal_char(chr):
            return chr
        try:
            chr_b = chr.encode('unicode_escape', errors='ignore').replace(b' ', b'').replace(b'\\n', b'').replace(b'\\t', b'').replace(b'\\xa0', b', ')
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

    def page_item(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", {"id": "shop-all-list"})
        if not div:
            return "no content"
        lis = div.find_all("li")
        for item in lis:
            a = item.find("a", {"data-hippo-type": "shop"})
            print(a["title"])
            detail_url = a["href"]
            d = item.find("div", class_="operate J_operate Hide")
            if d:
                manya = d.find_all("a")
                for a in manya:
                    if a["class"] == ["o-map", "J_o-map"]:
                        print(a["data-address"])
                        break
            comm = item.find("div", class_="comment")
            print(comm.span["title"])
            phone = self.parse_phone(detail_url)

    def parse_phone(self, url):
        print(url)
        r1 = self.session.get(url)
        if "ETag" in r1.headers:
            self.session.headers["If-None-Match"] = r1.headers["ETag"]
        self.session.headers["Referer"] = url
        self.session.headers["Host"] = "s3plus.meituan.net"
        css = self.css_pattern.search(r1.text)
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
        soup = BeautifulSoup(r1.text, "lxml")
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
        else:
            phone = phone.text
        rosetta = Rosetta(local_filename)
        res = rosetta.convert(res)
        index = res.find("电话：")
        phone = res[index+len("电话："):]
        os.remove(local_filename)
        return phone

    def parse_cate(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find("div", {"id": "J_nt_items"})
        manya = div.find_all("a")
        for a in manya:
            if a.get("href"):
                print(a["href"])

    def parse_jiehun(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find('div', {"id": "J_boxList"})
        ul = div.find("ul", class_="shop-list")
        lis = ul.find_all("li")
        for item in lis:
            a = item.a
            if a.get("title"):
                print(a.get("title"))
            if a.get("href"):
                jiehun_url = self.url_home + a.get("href")
            p = item.find_all("p", class_="area-list")
            if p:
                p = p[0]
                print(p.text.strip())
            score = item.find("span", class_="item-rank-rst irr-star40")
            if score:
                print(score.get("title"))
            r2 = self.session.get(jiehun_url)
            soup = BeautifulSoup(r2.text, "lxml")
            div = soup.find("div", class_="offers-box")




# DianPing().parse_cate("http://www.dianping.com/chongqing/ch0")
DianPing().parse_jiehun("http://www.dianping.com/chongqing/ch55/p1")