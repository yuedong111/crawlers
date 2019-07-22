import requests
# from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib
from utils.models import WaiMai
from utils.sqlbackends import session_scope
from utils.make_sessions import create_meituan_session, create_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from math import radians, cos, sin, asin, sqrt
import geohash

driver = create_webdriver()
url_home = "https://waimai.meituan.com"
waimaiurl = "https://waimai.meituan.com/home/{}"


def begin(place):
    driver.get("https://www.meituan.com/")
    driver.get("https://waimai.meituan.com/home/{}".format(place))
    count = 0
    while True:
        load = driver.find_elements_by_xpath('//*[@id="loading"]/div')
        if load:
            load = load[0]
            load.click()
        else:
            print("点击次数 {}".format(count))
            driver.get("https://waimai.meituan.com/home/{}".format(place))
            time.sleep(1)
            total = count - 1
            if total:
                for _ in range(total):
                    load = driver.find_elements_by_xpath('//*[@id="loading"]/div')
                    if load:
                        load[0].click()
                    time.sleep(2)
            r = driver.page_source
            parse_item(r, place, count)
            break
        count = count + 1
        time.sleep(3)
        if not count % 5:
            r = driver.page_source
            sta = parse_item(r, place, count)
            if sta:
                break


def parse_item(r, place, count):
    soup = BeautifulSoup(r, "lxml")
    a = soup.find_all("li", class_="fl rest-li")
    if not a:
        print("{}该区域没有店铺{}".format(place, count))
        print("https://waimai.meituan.com/home/{}".format(place))
        return True
    for item in a:
        res = {}
        res["geoArea"] = place
        div = item.div.div
        res["shop"] = div["data-title"].strip().encode(encoding="gbk", errors="ignore").decode("gbk")
        res["about"] = div["data-bulletin"].strip().encode(encoding="gbk", errors="ignore").decode("gbk")
        a = div.a
        url = url_home + a["href"]
        res["url"] = url.strip()
        span = item.find_all("span", class_="score-num fl")
        if span:
            res["score"] = span[0].text.strip()
        wm = WaiMai(**res)
        with session_scope() as sess:
            qr = sess.query(WaiMai).filter(WaiMai.url == res["url"]).first()
            if not qr:
                sess.add(wm)
                print(res)


def geodistance(nagt1, nagt2):
    lng1, lat1 = nagt1
    lng2, lat2 = nagt2
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371 * 1000
    return dis


def get_3kilo_neighor(place):
    pnum = geohash.decode(place)
    res = list()
    res.append(geohash.encode(pnum[0], pnum[1] - 0.03))
    res.append(geohash.encode(pnum[0] - 0.1, pnum[1]))
    res.append(geohash.encode(pnum[0] + 0.1, pnum[1]))
    res.append(geohash.encode(pnum[0], pnum[1] + 0.03))
    return res


quxian = {"垫江县": "wm5v5j3xgx0k",
          "shapingba": "wm78ndvhcgfz",
          "dazuqu": "wm71jcj56mgm",
          "hechuan": "wm7dd92ed9vz",
          "tongliang": "wm73vd15cd6s",
          "tongnan": "wm77b978p5w8",
          "yongchuan": "wmhh9qc58mke",
          "chengkou": "wmtmbbumbpd7",
          "fuling": "wmk35b7tjfxs",
          "changshou": "wmk1uu6z879g",
          "bishan": "wm783khyg7s7",
          "banan": "wm5z299kz8cu",
          "xiushan": "wmj9bs17p87s",
          "pengshui": "wmhyttbd15xy",
          "wanzhou": "wmmp713y3e7q",
          "nanchuan": "wmhjv7wtb36j",
          "zhongxian": "wmku6sgsur2j",
          "wushanxian": "wmw0ud01nu9j",
          "巫溪县": "wmtftmp4ejz2",
          "酉阳": "wmjk55rjfrj5",
          "丰都": "wmk9gts1cmbq",
          "武隆": "wmhwu79p7wju",
          "黔江": "wmm2533kj9u5",
          "石柱": "wmkfsq6vx9zb",
          "开县": "wmt169wng7d9",
          "江津区": "wm5wdjhhzusg",
          "rongchang": "wm5p75qfm8qg",
          "fengjie": "wmtb7pcgquvx",
          "yunyang": "wmmrcxg6vfhf"
          }


def start(start_place):
    d = set()
    c = set()
    temp = start_place
    while True:
        d.update(get_3kilo_neighor(temp))
        c.update(get_3kilo_neighor(temp))
        temp = d.pop()
        if len(c) >= 500:
            break
    for item in c:
        try:
            begin(item)
        except Exception as e:
            print(e)
            print("https://waimai.meituan.com/home/{}".format(item))


def craw():
    for item in quxian.keys():
        start(quxian.get(item))


if __name__ == "__main__":
    craw()
