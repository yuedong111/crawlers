# -*- coding: utf-8 -*-
from utils.make_sessions import create_meituan_session, USERAGETNS, COOKIES, create_webdriver
import json
import re
from bs4 import BeautifulSoup
import time
from utils.models import MeiTuanShop
from utils.sqlbackends import session_scope
from utils.esbackends import es_search, EsBackends
import traceback
import random
import sys
from jiehun_meishi import parse_jiehun_item, parse_meishi_item
from meituanpeixun import parse_peixun

url_map = {
    "life": "https://cq.meituan.com/shenghuo/pn{}/",
    "xiuxian": "https://cq.meituan.com/xiuxianyule/pn{}/",
    "meishi": "https://cq.meituan.com/meishi/pn{}/",
    "jiankangliren": "https://cq.meituan.com/jiankangliren/pn{}/",
    "jiehun": "https://cq.meituan.com/jiehun/pn{}/",
    "qinzi": "https://cq.meituan.com/qinzi/pn{}/",
    "yundong": "https://cq.meituan.com/yundongjianshen/pn{}/",
    "jiazhuang": "https://cq.meituan.com/jiazhuang/pn{}/",
    "yiliao": "https://cq.meituan.com/yiliao/pn{}/",
    "jiaoyupeixun": "https://cq.meituan.com/xuexipeixun/pn{}/"
}

hotel_url = "https://ihotel.meituan.com/hbsearch/HotelSearch?utm_medium=pc&version_name=999.9&cateId=20&attr_28=129&uuid=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258%401562656719051&cityId=45&offset={}&limit=20&startDay=20191108&endDay=20200108&q=&sort=defaults&X-FOR-WITH=c0dGLE3siaNf6WANtDItcccQMpQvbJuHHXiSyb7dP6m2wrWAH9gtxqbHsOreGP5zCtGc3QfExeVZqpNhptxz%2F4GSYcf6XcJfaYhBt4PRoOvn4MvIuqvPMq1PsVCWsxXgDy3qFLJNM4b6nfIf6pX5og%3D%3D"
hotel_detail = "https://hotel.meituan.com/{}/"
session = create_meituan_session()
driver = create_webdriver()


def parse_shop(url):
    ess = es_search("meituan", url)
    if ess[0] and ess[1]:
        pass
    else:
        print("parse shop url {}".format(url))
        time.sleep(random.uniform(1, 3))
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
                    result["phone"] = phone
                if "时间" in item.text:
                    time1 = item.text[item.text.find("：") + 1:]
                    opentime = " ".join(time1.split())
                    result["openTime"] = opentime
        if result:
            result["url"] = url
            mt = MeiTuanShop(**result)
            with session_scope() as session1:
                session1.add(mt)
            if not ess[1] and ess[0]:
                EsBackends("meituan").update_data(id=ess[2], body={"link": url, "status": 1, "date": time.time()})
            if not ess[0]:
                EsBackends("meituan").index_data({"link": url, "status": 1, "date": time.time()})
        else:
            count = 0
            while True:
                print("第{}次重试 {}".format(count + 1, url))
                time.sleep(random.uniform(1, 3))
                session.headers["User-Agent"] = random.choices(USERAGETNS)[0]
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
                            result["phone"] = phone
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
                    if not ess[1] and ess[0]:
                        EsBackends("meituan").update_data(id=ess[2],
                                                          body={"link": url, "status": 1, "date": time.time()})
                    if not ess[0]:
                        EsBackends("meituan").index_data({"link": url, "status": 1, "date": time.time()})
                else:
                    if count >= 3:
                        break
                    count = count + 1
            if not ess[0]:
                EsBackends("meituan").index_data({"link": url, "status": 0, "date": time.time()})
            else:
                EsBackends("meituan").update_data(id=ess[2],
                                                  body={"link": url, "status": 0, "date": time.time()})
            print("获取值为空{}".format(url))


def parse_shop2(url):
    time.sleep(random.uniform(1, 2))
    resu = {}
    r = session.get(url)
    rule = r'appState = (.+?);</script>'
    slotList = re.findall(rule, r.text)
    if slotList:
        res = json.loads(slotList[0])
        temp = res.get("detailInfo")
        resu["shop"] = temp.get("name")
        resu["phone"] = temp.get("phone")
        resu["address"] = temp.get("address")
        resu["score"] = temp.get("avgScore")
        resu["openTime"] = temp.get("openTime")
    return resu


Found = False


def parse_pages(url):
    session.headers["Referer"] = url
    if "meishi" in url:
        print("parse meishi url {}".format(url))
        for item in parse_meishi_item(session, url):
            parse_shop(item)
    elif "jiehun" in url:
        parse_jiehun_item(session, url)
    else:
        r = session.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        div = soup.find("div", {"class": "common-list-main"})
        print("pages url {}".format(url))
        # print(div)
        if div:
            for item in div:
                a = item.find("a", {"class": "abstract-pic grey"})
                if a.get("href"):
                    shop_url = "https:" + a.get("href")
                    if "xuexipeixun" in shop_url:
                        print("peixun url {}".format(shop_url))
                        try:
                            parse_peixun(driver, shop_url)
                        except Exception as e:
                            print(e)
                        # global Found
                        # if shop_url == "https://www.meituan.com/xuexipeixun/189039722/":
                        #     Found = True
                        # if Found:
                        #     parse_peixun(driver, shop_url)
                        # else:
                        #    print("跳过")
                    else:
                        parse_shop(shop_url)


def total_pages(url):
    session.headers["Referer"] = url
    session.headers["Cookie"] = COOKIES
    r = session.get(url.format(1))
    soup = BeautifulSoup(r.text, 'lxml')
    count = None
    if "meishi" in url:
        count = 1
        last_page = 67
    elif "jiehun" in url:
        last_page = 11
    elif "yiliao" in url:
        last_page = 5
    elif "shenghuo" in url:
        last_page = 19
    elif "xiuxianyule" in url:
        last_page = 32
    elif "jiankangliren" in url:
        last_page = 30
    elif "qinzi" in url:
        last_page = 20
    elif "yundongjianshen" in url:
        last_page = 12
    elif "jiazhuang" in url:
        last_page = 4
    elif "xuexipeixun" in url:
        last_page = 12
    else:
        nav = soup.find("nav", {"class": "mt-pagination"})
        ul = nav.find("ul", {"class": "clearfix"})
        lis = ul.find_all("li", {"class": "num-item"})
        pages = lis[-1].text
        last_page = int(pages)
    if not count:
        count = 1
    while count <= last_page:
        page_url = url.format(count)
        try:
            time.sleep(random.uniform(0.5, 1))
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
        time.sleep(random.uniform(0.5, 2))
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
    ess = es_search("meituan", url)
    if ess[0] and ess[1]:
        pass
    else:
        result = {}
        time.sleep(random.uniform(1, 3))
        r = session.get(url)
        print("parse hotel {}".format(url))
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, 'lxml')
        naspan = soup.find("div", {"class": "breadcrumb-nav"})
        result["shop"] = naspan.text.strip()
        result["url"] = url
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
            if not ess[1] and ess[0]:
                EsBackends("meituan").update_data(id=ess[2],
                                                  body={"link": url, "status": 1, "date": time.time()})
            if not ess[0]:
                EsBackends("meituan").index_data({"link": url, "status": 1, "date": time.time()})
        else:
            if not ess[0]:
                EsBackends("meituan").index_data({"link": url, "status": 0, "date": time.time()})
            else:
                EsBackends("meituan").update_data(id=ess[2],
                                                  body={"link": url, "status": 0, "date": time.time()})
            print("获取值为空 {}".format(url))


def start():
    for item in url_map:
        try:
            total_pages(url_map[item])
            driver.quit()
        except:
            driver.quit()
            print("error {}: {}".format(traceback.print_exc(), url_map[item]))

    get_hotelids(hotel_url)
    print("done!")


if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        sys.exit()
