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
from selenium.webdriver.common.action_chains import ActionChains
from sqlalchemy import and_


# driver = create_webdriver()
url_home = "https://waimai.meituan.com"
waimaiurl = "https://waimai.meituan.com/home/{}"


def begin(place):
    driver.get("https://waimai.meituan.com/")
    driver.get("https://waimai.meituan.com/home/{}".format(place))
    count = 0
    while True:
        time.sleep(3)
        load = driver.find_elements_by_xpath('//*[@id="loading"]/div')
        if load:
            load = load[0]
            try:
                load.click()
            except Exception as e:
                print("shouci jiazai {}".format(e))
        else:
            print("点击次数 {}".format(count))
            driver.get("https://waimai.meituan.com/home/{}".format(place))
            time.sleep(1)
            total = count - 1
            if total:
                for _ in range(total):
                    load = driver.find_elements_by_xpath('//*[@id="loading"]/div')
                    if load:
                        try:
                            load[0].click()
                        except Exception as e:
                            print(e)
                    time.sleep(2)
            r = driver.page_source
            sta = parse_item(driver, r, place, count)
            break
        count = count + 1
        if not count % 5:
            r = driver.page_source
            sta = parse_item(driver, r, place, count)
            if sta:
                break


def parse_item(driver, r, place, count):
    soup = BeautifulSoup(r, "lxml")
    a = soup.find_all("li", class_="fl rest-li")
    try:
        title = soup.title.text.strip()
    except Exception as e:
        print(e)
        title = ""
    if title == "403 Forbidden":
        raise ForbiddenException("403 forbidden")
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
        span = item.find_all("span", class_="score-num fl")
        if span:
            res["score"] = span[0].text.strip()
        res["url"] = url.strip()
        with session_scope() as sess:
            qr = sess.query(WaiMai).filter(and_(WaiMai.shop == res["shop"], WaiMai.about == res["about"])).first()
            if not qr:
                driver.get(url)
                shop = driver.find_elements_by_xpath("/html/body/div[3]/div[2]/div/div[2]/div[2]")
                if not shop:
                    driver.get(url)
                time.sleep(1)
                try:
                    ActionChains(driver).move_to_element(shop[0]).perform()
                except Exception as e:
                    print("{} {}".format(url, e))
                r1 = driver.page_source
                soup1 = BeautifulSoup(r1, "lxml")
                try:
                    div = soup1.find("div", class_="rest-info-down-wrap")
                    timep = div.find("div", class_="clearfix sale-time")
                    if timep:
                        timep = timep.text.split()[-1]
                        res["openTime"] = timep.strip()
                except Exception as e:
                    print("opentime{}".format(e))
                try:
                    address = div.find("div", class_="rest-info-thirdpart poi-address")
                    if address:
                        address = address.text.split()[-1]
                        res["address"] = address.strip()
                except Exception as e:
                    print("address {}".format(e))
                time.sleep(1)
                res["url"] = url.strip()
                wm = WaiMai(**res)
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
    res.append(geohash.encode(pnum[0], pnum[1] - 0.01))
    res.append(geohash.encode(pnum[0] - 0.02, pnum[1]))
    res.append(geohash.encode(pnum[0] + 0.02, pnum[1]))
    res.append(geohash.encode(pnum[0], pnum[1] + 0.01))
    return res


quxian = {
    # "垫江县": "wm5v5j3xgx0k",
    # "shapingba": "wm78ndvhcgfz",
    # "dazuqu": "wm71jcj56mgm",
    # "hechuan": "wm7dd92ed9vz",
    # "tongliang": "wm73vd15cd6s",
    # "tongnan": "wm77b978p5w8",
    # "yongchuan": "wmhh9qc58mke",
    # "chengkou": "wmtmbbumbpd7",
    # "fuling": "wmk35b7tjfxs",
    # "changshou": "wmk1uu6z879g",
    # "bishan": "wm783khyg7s7",
    # "banan": "wm5z299kz8cu",
    # "xiushan": "wmj9bs17p87s",
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
    "yunyang": "wmmrcxg6vfhf",
    "nanping": "wm5zcpupnw6q",
    "大渡口": "wm5xz0w86d7u"
}


def start(start_place):
    d = set()
    c = set()
    temp = start_place
    while True:
        d.update(get_3kilo_neighor(temp))
        c.update(get_3kilo_neighor(temp))
        temp = d.pop()
        if len(c) >= 800:
            break
    for item in c:
        try:
            begin(item)
            time.sleep(1)
        except ForbiddenException as e:
            raise e
        except Exception as e:
            print(e)
            print("https://waimai.meituan.com/home/{}".format(item))


def craw():
    for item in quxian.keys():
        print("in {}".format(item))
        start(quxian.get(item))


class ForbiddenException(Exception):
    pass


if __name__ == "__main__":
    while True:
        driver = create_webdriver()
        try:
            start_time = time.time()
            craw()
            end_time = time.time()
            break
        except ForbiddenException as e:
            end_time = time.time()
            print(e)
        finally:
            driver.quit()
        during = end_time - start_time
        h = during / 3600
        m = (during - int(h) * 3600) / 60
        mili = during - int(h) * 3600 - int(m) * 60
        print("一共爬行了{}小时{}分{}秒  共{}秒".format(int(h), int(m), int(mili), during))
        nowt = time.asctime(time.localtime(time.time()))
        print(nowt)
        print("wait two hours")
        time.sleep(2 * 3600)
