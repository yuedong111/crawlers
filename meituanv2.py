# -*- coding: utf-8 -*-
from utils.make_sessions import create_meituan_session, USERAGETNS
import json
import re
from bs4 import BeautifulSoup
import time
from utils.models import MeiTuanShop
from utils.sqlbackends import session_scope
import traceback
import random
import sys
# from tuan import headers as HEADERS

url_map = {
    "life": "https://cq.meituan.com/shenghuo/pn{}/",
    "xiuxian": "https://cq.meituan.com/xiuxianyule/pn{}/",
    "meishi": "https://cq.meituan.com/meishi/pn{}/",
    "jiankangliren": "https://cq.meituan.com/jiankangliren/pn{}/",
    "jiehun": "https://cq.meituan.com/jiehun/pn{}/",
    "qinzi": "https://cq.meituan.com/qinzi/pn{}/",
    "yundong": "https://cq.meituan.com/yundongjianshen/pn{}/",
    "jiazhuang": "https://cq.meituan.com/jiazhuang/pn{}/",
    "yiliao": "https://cq.meituan.com/yiliao/pn{}/"
}

hotel_url = "https://ihotel.meituan.com/hbsearch/HotelSearch?utm_medium=pc&version_name=999.9&cateId=20&attr_28=129&uuid=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258%401562656719051&cityId=45&offset={}&limit=20&startDay=20191108&endDay=20200108&q=&sort=defaults&X-FOR-WITH=c0dGLE3siaNf6WANtDItcccQMpQvbJuHHXiSyb7dP6m2wrWAH9gtxqbHsOreGP5zCtGc3QfExeVZqpNhptxz%2F4GSYcf6XcJfaYhBt4PRoOvn4MvIuqvPMq1PsVCWsxXgDy3qFLJNM4b6nfIf6pX5og%3D%3D"
hotel_detail = "https://hotel.meituan.com/{}/"
session = create_meituan_session()
# session.headers.update(HEADERS)


def parse_shop(url):
    time.sleep(random.uniform(0.4, 2))
    result = {}
    r = session.get(url, timeout=5)
    soup = BeautifulSoup(r.text, 'lxml')
    head = soup.find("div", {"class": "seller-info-head"})
    if not head:
        resu = parse_shop2(url)
        result.update(resu)
    else:
        name = head.find("h1", {"class": "seller-name"})
        result["shop"] = name.text.strip()
        score = head.find("span", {"class": "score"})
        result["score"] = score.text.split()[0]
        div = head.find("div", {"class": "seller-info-body"})
        items = div.find_all("div", {"class": "item"})
        for item in items:
            if "地址" in item.text.strip():
                address = item.text[item.text.find("：") + 1:]
                result["address"] = address
            if "电话" in item.text:
                phone = item.text[item.text.find("：") + 1:]
                result["phone"] = phone.strip()
            if "时间" in item.text:
                time1 = item.text[item.text.find("：") + 1:]
                opentime = " ".join(time1.split())
                result["openTime"] = opentime
    if result:
        result["url"] = url
        mt = MeiTuanShop(**result)
        # print(result)
        with session_scope() as session1:
            session1.add(mt)
    else:
        count = 0
        while True:
            time.sleep(random.uniform(0.3, 2))
            session.headers["User-Agent"] = random.choices(USERAGETNS)
            r = session.get(url, timeout=5)
            soup = BeautifulSoup(r.text, 'lxml')
            head = soup.find("div", {"class": "seller-info-head"})
            if not head:
                resu = parse_shop2(url)
                result.update(resu)
            else:
                name = head.find("h1", {"class": "seller-name"})
                result["shop"] = name.text.strip()
                score = head.find("span", {"class": "score"})
                result["score"] = score.text.split()[0]
                div = head.find("div", {"class": "seller-info-body"})
                items = div.find_all("div", {"class": "item"})
                for item in items:
                    if "地址" in item.text.strip():
                        address = item.text[item.text.find("：") + 1:]
                        result["address"] = address
                    if "电话" in item.text:
                        phone = item.text[item.text.find("：") + 1:]
                        result["phone"] = phone.strip()
                    if "时间" in item.text:
                        time1 = item.text[item.text.find("：") + 1:]
                        opentime = " ".join(time1.split())
                        result["openTime"] = opentime
            if result:
                result["url"] = url
                mt = MeiTuanShop(**result)
                # print(result)
                with session_scope() as session1:
                    session1.add(mt)
            else:
                if count >= 3:
                    break
                count = count + 1
        print("获取值为空{}".format(url))


def parse_shop2(url):
    time.sleep(random.uniform(0.4, 2))
    resu = {}
    r = session.get(url, timeout=5)
    rule = r'appState = (.+?);</script>'
    slotList = re.findall(rule, r.text)
    if slotList:
        res = json.loads(slotList[0])
        temp = res.get("detailInfo")
        resu["shop"] = temp.get("name")
        resu["phone"] = temp.get("phone").strip()
        resu["address"] = temp.get("address")
        resu["score"] = temp.get("avgScore")
        resu["openTime"] = temp.get("openTime")
    return resu


def parse_pages(url):
    r = session.get(url, timeout=5)
    soup = BeautifulSoup(r.text, 'lxml')
    div = soup.find("div", {"class": "common-list-main"})
    print("pages page url {}".format(url))
    if div:
        for item in div:
            a = item.find("a", {"class": "abstract-pic grey"})
            if a.get("href"):
                shop_url = "https:" + a.get("href")
                parse_shop(shop_url)


def total_pages(url):
    r = session.get(url.format(1))
    soup = BeautifulSoup(r.text, 'lxml')
    nav = soup.find("nav", {"class": "mt-pagination"})
    ul = nav.find("ul", {"class": "clearfix"})
    lis = ul.find_all("li", {"class": "num-item"})
    pages = lis[-1].text
    last_page = int(pages)
    count = 1
    while count <= last_page:
        page_url = url.format(count)
        try:
            time.sleep(random.uniform(0.4, 1))
            parse_pages(page_url)
        except KeyboardInterrupt:
            exit(0)
        except:
            print("error problem url {}:{}".format(traceback.print_exc(), page_url))
        count = count + 1


def get_hotelids(url):
    session = create_meituan_session()
    session.headers["Accept"] = "application/json, text/plain, */*"
    session.headers["Origin"] = "https://hotel.meituan.com"
    session.headers["Referer"] = "https://hotel.meituan.com/chongqing/"
    temp = 0
    count = 0
    while True:
        time.sleep(random.uniform(0.4, 2))
        r = session.get(url.format(temp))
        items = r.json().get("ct_pois")
        temp = temp + 20
        if not items:
            count = count + 1
            if count >= 3:
                print("酒店爬取完毕 {}".format(temp))
                break
            continue
        else:
            count = 0
        for item in items:
            url1 = hotel_detail.format(item.get("poiid"))
            try:
                get_hotel_detail(url1)
            except:
                print("error hotel url wrong {}:{}".format(traceback.print_exc(), url1))


def get_hotel_detail(url):
    result = {}
    time.sleep(random.uniform(0.4, 2))
    r = session.get(url)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, 'lxml')
    naspan = soup.find("div", {"class": "breadcrumb-nav"})
    result["shop"] = naspan.text.strip()
    result["openTime"] = "全天"
    div = soup.find("div", {"class": "mb10"})
    span = div.find("span")
    result["address"] = span.text.strip()
    li = soup.find("li", {"class": "fs14"})
    divs = li.find_all("div", {"class": "mb10"})
    item = divs[-1]
    if "电话" in item.text:
        phone = item.text[item.text.find("：") + 1:]
        result["phone"] = phone
    score = soup.find("div", {"class": "other-detail-line1-score"})
    result["score"] = score.text.strip()
    mt = MeiTuanShop(**result)
    if result:
        result["url"] = url
        with session_scope() as session1:
            session1.add(mt)
    else:
        print("获取值为空 {}".format(url))


def start():
    for item in url_map:
        try:
            total_pages(url_map[item])
        except:
            print("error {}: {}".format(traceback.print_exc(), url_map[item]))

    get_hotelids(hotel_url)
    print("done!")


if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        sys.exit()
