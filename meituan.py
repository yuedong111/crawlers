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
from functools import wraps


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
                    return {}
                res = decorate(*args, **kwargs)
                break
        count = 0
        return res

    return decorate


url_map = {
    # "life": "https://cq.meituan.com/shenghuo/pn{}/",
    # "xiuxian": "https://cq.meituan.com/xiuxianyule/pn{}/",
    # "meishi": "https://cq.meituan.com/meishi/pn{}/",
    # "jiankangliren": "https://cq.meituan.com/jiankangliren/pn{}/",
    # "jiehun": "https://cq.meituan.com/jiehun/pn{}/",
    # "qinzi": "https://cq.meituan.com/qinzi/pn{}/",
    # "yundong": "https://cq.meituan.com/yundongjianshen/pn{}/",
    # "jiazhuang": "https://cq.meituan.com/jiazhuang/pn{}/",
    # "yiliao": "https://cq.meituan.com/yiliao/pn{}/",
    # "jiaoyupeixun": "https://cq.meituan.com/xuexipeixun/pn{}/"
}

hotel_url = "https://ihotel.meituan.com/hbsearch/HotelSearch?utm_medium=pc&version_name=999.9&cateId=20&attr_28=129&uuid=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258%401562656719051&cityId=45&offset={}&limit=20&startDay=20190908&endDay=20190910&q=&sort=defaults&X-FOR-WITH=c0dGLE3siaNf6WANtDItcccQMpQvbJuHHXiSyb7dP6m2wrWAH9gtxqbHsOreGP5zCtGc3QfExeVZqpNhptxz%2F4GSYcf6XcJfaYhBt4PRoOvn4MvIuqvPMq1PsVCWsxXgDy3qFLJNM4b6nfIf6pX5og%3D%3D"
hotel_detail = "https://hotel.meituan.com/{}/"
session = create_meituan_session()
session.headers["Host"] = "cq.meituan.com"
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
                result = {}
                print("第{}次重试 {}".format(count + 1, url))
                time.sleep(random.uniform(1, 3))
                session.headers["User-Agent"] = random.choices(USERAGETNS)[0]
                r = session.get(url, timeout=5)
                soup = BeautifulSoup(r.text, 'lxml')
                head = soup.find("div", {"class": "seller-info-head"})
                try:
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
                except Exception as e:
                    print(count, e)
                    break
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
        try:
            for item in parse_meishi_item(session, url):
                # print("parse {}".format(item))
                parse_shop(item)
        except:
            print(traceback.print_exc())
    elif "jiehun" in url:
        print("parse jiehun {}".format(url))
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


JUMP = "http://cq.meituan.com/meishi/c233"
STATUS = False


def total_pages(url):
    session.headers["Referer"] = url
    session.headers["Cookie"] = COOKIES
    # r = session.get(url.format(1))
    try:
        print(url.format(1))
        driver.get(url.format(1))
    except:
        print(url[:-5])
        driver.get(url[:-5])
    while "verify.meituan.com/v2" in driver.current_url:
        print("输入验证码")
        time.sleep(10)
    time.sleep(1)
    r = driver.page_source
    # with open("test.html", "w", encoding="utf-8") as f:
    #     f.write(r)
    soup = BeautifulSoup(r, 'lxml')
    nav = soup.find("div", {"class": "mt-pagination"})
    try:
        temp = []
        if not nav:
            nav = soup.find("nav", class_="mt-pagination")
            mas = nav.find_all("a")
            for item in mas:
                if hasattr(item, "text"):
                    if item.text.strip() and len(item.text.strip()) < 4:
                        temp.append(item.text)
        else:
            lis = nav.find_all("span")
            for item in lis:
                if hasattr(item, "text"):
                    if item.text.strip() and len(item.text.strip()) < 4:
                        temp.append(item.text)
        last_page = int(temp[-1])
    except Exception as e:
        # print(traceback.print_exc())
        last_page = 1
    print(last_page)
    count = 1
    while count <= last_page:
        page_url = url.format(count)
        try:
            time.sleep(random.uniform(1, 2))
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
    session.headers["Host"] = "ihotel.meituan.com"
    # session.headers["Cookie"] = "_lxsdk_cuid=16bd9b99c9ec8-035ab9a6954478-36664c08-1fa400-16bd9b99ca0c8; iuuid=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; cityname=%E9%87%8D%E5%BA%86; _lxsdk=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; _hc.v=10962146-cd2f-a7a9-c15a-d942a6e12989.1562744821; ci=45; rvct=45%2C1%2C114; _ga=GA1.2.1247011406.1563181057; _lx_utm=utm_source%3Dso.com%26utm_medium%3Dorganic; uuid=36ead8f00d76403086f7.1566196693.1.0.0; IJSESSIONID=jaox69mj94cq1rkw4jpfsxtuw; _lxsdk_s=16ca898f3b0-645-dd2-166%7C%7C39"
    temp = 0
    count = 0
    while True:
        time.sleep(random.uniform(1, 2))
        r = session.get(url.format(temp))
        # print(url.format(temp))
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
        # session = create_meituan_session()
        session.headers["Host"] = "hotel.meituan.com"
        r = session.get(url)
        print("parse hotel {}".format(url))
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, 'lxml')
        naspan = soup.find("div", {"class": "breadcrumb-nav"})
        if not naspan:
            naspan = soup.find_all("span", class_="fs26 fc3 pull-left bold")
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


# @second_run
def start():
    for item in url_map:
        try:
            r = session.get(url_map[item].format(1))
            soup = BeautifulSoup(r.text, "lxml")
            if "shenghuo" in url_map[item]:
                div = soup.find("div", class_="filter-component")
                mas = div.find_all("a")
                for a in mas:
                    if a.get("href") and a.get("href").startswith("//"):
                        url = "https:" + a.get("href") + "pn{}/"
                        try:
                            sa = total_pages(url)
                        except Exception as e:
                            print(traceback.print_exc())
            elif "meishi" in url_map[item]:
                div = soup.find("div", {"class": "filter", "data-reactid": "15"})
                mas = div.find_all("a")
                # global JUMP, STATUS
                for a in mas:
                    if a.get("href") and "?" not in a.get("href"):
                        url = a.get("href") + "pn{}/"
                        try:
                            # if JUMP in url:
                            #     STATUS = True
                            # if not STATUS:
                            #     continue
                            sa = total_pages(url)
                        except Exception as e:
                            print(traceback.print_exc())
            else:
                div = soup.find("div", {"class": "filter-box"})
                if not div:
                    # print(r.text.find("龙湖新壹街店"))
                    try:
                        div = soup.find_all("div", class_="filter-component")
                        if not div:
                            if "没有符合条件的商家" in r.text:
                                continue
                            else:
                                raise Exception("没有找到 {}".format(url_map[item].format(1)))
                        div = div[-1]
                        div = div.find_all("div", class_="tag-group tag-group-expend")
                        if not div:
                            raise Exception("没有找到 {}".format(url_map[item].format(1)))
                        div = div[0]
                        ds = div.find_all("div")
                        for item in ds:
                            a = item.a
                            if a:
                                if a.get("href") and a.get("href").startswith("//"):
                                    d_u = "https:" + a.get("href") + "pn{}/"
                                    # ares = a.text.strip()
                                    try:
                                        sa = total_pages(d_u)
                                    except Exception as e:
                                        print(e)
                    except Exception as e:
                        print(traceback.print_exc())
                else:
                    mas = div.find_all("a")
                    for ite in mas:
                        if ite.get("href") and ite.get("href").startswith("//"):
                            url = "https:" + ite.get("href") + "pn{}/"
                            try:
                                sa = total_pages(url)
                            except Exception as e:
                                print(e)
        except:
            print("error {}: {}".format(traceback.print_exc(), url_map[item].format(1)))

    get_hotelids(hotel_url)
    print("done!")


if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        # driver.quit()
        sys.exit()
    finally:
        driver.quit()
