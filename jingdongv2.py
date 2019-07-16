# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session, create_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
from utils.sqlbackends import session_scope
from utils.models import JingDong
import time
import random
import traceback
pattern = re.compile(r'\d+')
comment_url = url = "https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv{}&productId={}&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1"
# tv_url = "https://list.jd.com/list.html?cat=737,794,798&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main"
url_map = {
    # "tv_url": "https://list.jd.com/list.html?cat=737,794,798&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main",
    "container_url": "https://list.jd.com/list.html?cat=737,794,870&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main",
    "wash_url": "https://list.jd.com/list.html?cat=737,794,880&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main",
    # "fridge": "https://list.jd.com/list.html?cat=737,794,878&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main"
}
session = create_session()


def get_products(driver, url):
    driver.get(url)
    r = driver.page_source
    soup = BeautifulSoup(r, "lxml")
    all_li = soup.find_all('li', {"class": "gl-item"})
    for item in all_li:
        try:
            name = item.find("div", {"class": "p-name"})
            name = name.text.strip()
            image = item.find("img")
            if image.get("data-lazy-img"):
                image = "https:" + image.get("data-lazy-img")
            else:
                image = "https:" + image.get("src")
            shop = item.find("div", {"class": "p-shop"})
            shop = shop.find("a")
            if shop:
                shop = shop.get("title")
                shop = shop.strip()
            else:
                shop = ""
            price = item.find("div", {"class": "p-price"})
            price = price.find("strong", {"class": "J_price"})
            price = price.text.strip()
            about = item.find("div", {"class": "p-commit p-commit-n"})
            if not about:
                about = item.find("div", {"class": "p-commit"})
            about = about.text.strip()
            detail_url = item.find("a", {"target": "_blank"})
            detail_url = "https:" + detail_url.get("href")
            res = {"id": None,
                   "productName": name,
                   "image": image,
                   "shop": shop,
                   "price": price,
                   "popular": about,
                   }
            try:
                result = get_comment(detail_url)
            except:
                continue
            res.update(result)
            jd = JingDong(**res)
            with session_scope() as session:
                session.add(jd)
        except:
            print("货品条目错误")
            print(traceback.print_exc())
            continue



def get_comment(url):
    time.sleep(random.uniform(0.4, 2))
    resu = {}
    resu["productUrl"] = url
    r = session.get(url, timeout=5)
    session.headers["Referer"] = url
    origin = r.text[r.text.find("commentVersion"): r.text.find("commentVersion") + 25]
    # print(origin)
    commentid = pattern.findall(origin)[0]
    vendorid = pattern.findall(url)[0]
    r = session.get(comment_url.format(commentid, vendorid), timeout=5)
    find_str = "fetchJSON_comment98vv{}(".format(commentid)
    print(comment_url.format(commentid, vendorid))
    print(r.status_code, r.text)
    res = r.text.replace(find_str, "")
    res = res[0: -2]
    res = json.loads(res)
    print("-"*20)
    product = res.get("productCommentSummary")
    tem = res
    if product:
        res = product
        haopinglv = res.get("goodRateShow")
        resu["rate"] = haopinglv
        resu["goodCommentCount"] = res.get("goodCountStr")
        poorcount = res.get("poorCountStr")
        resu["poorCommentCount"] = poorcount
        zhongping = res.get("generalCountStr")
        resu["generalCommentCount"] = zhongping
        zhuiping = res.get("afterCount")
        resu["afterCommentCount"] = zhuiping
        vedio = res.get("videoCount")
        resu["vedioCommentCount"] = vedio
        zongping = res.get("commentCountStr")
        resu["totalCommentCount"] = zongping
        morenhaop = res.get("defaultGoodCount")
        resu["defaultGoodCommentCount"] = morenhaop
    else:
        temp = "暂无参数"
        resu["rate"] = temp
        resu["goodCommentCount"] = temp
        resu["poorCommentCount"] = temp
        resu["generalCommentCount"] = temp
        resu["afterCommentCount"] = temp
        resu["vedioCommentCount"] = temp
        resu["totalCommentCount"] = temp
        resu["defaultGoodCommentCount"] = temp
    tags = tem.get("hotCommentTagStatistics")
    tag = ""
    if tags:
        for item in tags:
            tag = tag + "{}({})".format(item.get("name"), item.get("count")) + " "
    resu["commentTag"] = tag
    print(resu)
    return resu


def get_pages(driver, url):
    driver.get(url.format(1))
    r = driver.page_source
    # with open("test.html", "w", encoding="utf-8") as f:
    # print(r, file=f)
    soup = BeautifulSoup(r, "lxml")
    pages = soup.find("span", {"class": "p-skip"})
    pages = pattern.findall(pages.text.strip())[0]
    total = int(pages)
    count = 1
    while count <= total:
        t_url = url.format(count)
        try:
            get_products(driver, t_url)
        except Exception as e:
            print("wrong {}: {}".format(traceback.print_exc(), t_url))
        count = count + 1


def start():
    driver = create_webdriver()
    for key in url_map.keys():
        get_pages(driver, url_map.get(key))
    driver.close()
    print("爬取完毕")


# get_comment(driver, "https://item.jd.com/4609660.html")
# get_products(driver, tv_url.format(1))
if __name__ == "__main__":
    start()
