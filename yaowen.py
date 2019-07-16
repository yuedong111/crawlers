# -*- coding: utf-8 -*-
from utils.make_sessions import create_yaowen_session
import json
import re
from bs4 import BeautifulSoup
import time
from utils.models import GoverNews
from utils.sqlbackends import session_scope
from utils.esbackends import es_search, EsBackends
import traceback
import random
import sys
import requests

yaowen_url = "http://spb.cq.gov.cn/pagelist.jsp?classid=3698&pageye={}&pageSize=18"
qianyan_url = "http://kjj.cq.gov.cn/Class.aspx?clsId=294&PageIndex={}"
qianyan_home = "http://kjj.cq.gov.cn"


class GovNews(object):

    def __init__(self):
        self.session = create_yaowen_session()
        self.home = "http://spb.cq.gov.cn"

    def total_pages(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        span = soup.find("span", class_="default_pgTotalPage")
        total = int(span.text)
        count = 1
        while count <= total:
            self.gov_news(yaowen_url.format(count))
            print("di {} ye".format(count))
            count = count + 1

    def gov_news(self, url):
        r = self.session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        res = {}
        ul = soup.find("ul", class_="pList01")
        lis = ul.find_all("li")
        for item in lis:
            date = item.span.text
            date = date[1:-1]
            res["publishDate"] = date
            if "http" not in item.a.get("href"):
                new_url = self.home + item.a.get("href")
            else:
                new_url = item.a.get("href")
            ess = es_search("govnews", new_url)
            if ess[0] and ess[1]:
                pass
            else:
                try:
                    resu = self.parse_detail(new_url)
                except Exception as e:
                    print(e)
                    continue
                res.update(resu)
                gw = GoverNews(**res)
                with session_scope() as sess:
                    sess.add(gw)
                EsBackends("govnews").index_data({"link": new_url, "status": 1, "date": time.time()})

    def parse_detail(self, url):
        time.sleep(random.uniform(0.5, 1))
        print(url)
        r = self.session.get(url)
        res = {}
        res["url"] = url
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.find("div", class_="news_conent_two_title")
        res["title"] = title.text
        about = soup.find("div", class_="news_conent_two_js")
        about = about.text
        if "字体" in about:
            about = about[:about.find("字体")]
        res["about"] = about
        content = soup.find("div", {"id": "news_conent_two_text"})
        res["content"] = content.encode("utf-8")
        return res

    def start(self):
        self.total_pages(yaowen_url.format(1))


sess = create_yaowen_session()


def parse_qianyann_item(url):
    sess.headers[
        "Cookie"] = "UM_distinctid=16bf50a8450476-00b7d0ed2a109b-e343166-1fa400-16bf50a8451895; _gscu_1516296093=631843228bhl3k13; _gscbrs_1516296093=1; Hm_lvt_062d51b4dcc0576135b683257033659a=1563184338; Hm_lpvt_062d51b4dcc0576135b683257033659a=1563242618; _gscs_1516296093=t6324261780strk14|pv:1"
    r = sess.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find_all("table", {"cellpadding": "0", "cellspacing": "0", "width": "98%"})
    trs = table[0].find_all("tr")
    for item in trs:
        res = {}
        tds = item.find_all("td")
        title = tds[1].a.text
        publish_date = tds[2].span.text.strip()
        res["title"] = title
        res["publishDate"] = publish_date
        de_url = qianyan_home + tds[1].a.get("href")
        res["url"] = de_url
        ess = es_search("govnews", de_url)
        if ess[0] and ess[1]:
            pass
        else:
            resu = parse_qianyan_detail(de_url)
            res.update(resu)
            gw = GoverNews(**res)
            with session_scope() as sess1:
                sess1.add(gw)
            EsBackends("govnews").index_data({"link": de_url, "status": 1, "date": time.time()})


def parse_qianyan_detail(url):
    time.sleep(random.uniform(0.2, 0.6))
    print(url)
    r = sess.get(url)
    res = {}
    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find_all("table", {"border": "0", "cellspacing": "0", "width": "96%"})
    td = table[0].find_all("td", {"align": "center", "class": "date"})
    about = " ".join(td[0].text.split())
    content = table[0].find_all("td", {"class": "v-a"})[0]
    res["about"] = about
    res["content"] = content.encode("utf-8")
    return res


def start():
    count = 1
    last_page = 4
    while count <= last_page:
        parse_qianyann_item(qianyan_url.format(count))
        print("ke ji bu di {} ye".format(count))
        count = count + 1


if __name__ == "__main__":
    GovNews().start()
    start()
