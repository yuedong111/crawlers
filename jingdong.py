# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from utils.make_sessions import create_session, create_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from utils.sqlbackends import session_scope
from utils.models import JingDong

pattern = re.compile(r'\d+')
# tv_url = "https://list.jd.com/list.html?cat=737,794,798&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main"
url_map = {
    "tv_url": "https://list.jd.com/list.html?cat=737,794,798&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main",
    "container_url": "https://list.jd.com/list.html?cat=737,794,870&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main",
    "wash_url": "https://list.jd.com/list.html?cat=737,794,880&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main",
    "fridge": "https://list.jd.com/list.html?cat=737,794,878&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main"
}
# session = create_session()


def get_products(driver, url):
    driver.get(url)
    r = driver.page_source
    soup = BeautifulSoup(r, "lxml")
    all_li = soup.find_all('li', {"class": "gl-item"})
    for item in all_li:
        name = item.find("div", {"class": "p-name"})
        name = name.text.strip()
        image = item.find("img")
        if image.get("data-lazy-img"):
            image = "https:" + image.get("data-lazy-img")
        else:
            image = "https:" + image.get("src")
        # print(image)
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
        about = about.text.strip()
        detail_url = item.find("a", {"target": "_blank"})
        detail_url = "https:" + detail_url.get("href")
        comments, haoping = get_comment(driver, detail_url)
        if not comments:
            comments = "暂无评价"
        if not haoping:
            haoping = "0%"
        jd = JingDong(id=None, productName=name, image=image, shop=shop, price=price, popular=about, rate=haoping,
                      commentTag=comments)
        with session_scope() as session:
            session.add(jd)


def get_comment(driver, url):
    res = ""
    driver.get(url)
    driver.execute_script("var q=document.documentElement.scrollTop=100000")
    try:
        comment_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="detail"]/div[1]/ul/li[4]')))
    except Exception as e:
        print("没获取到")
        return None, None
    driver.execute_script("arguments[0].scrollIntoView();", comment_link)
    comment_link.click()
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="comment"]/div[2]/div[1]/div[2]/div')))
    except Exception as e:
        print("评论获取不到")
        return None, None
    r = driver.page_source
    soup = BeautifulSoup(r, "lxml")
    all_li = soup.find('div', {"class": "tag-available"})
    haopingdu = soup.find("div", {"class": "percent-con"})
    if haopingdu:
        haopingdu = haopingdu.text.strip()
    if not all_li:
        return None, None
    spans = all_li.find_all("span")
    for item in spans:
        res = res + item.text.strip() + " "
    return res, haopingdu


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
        except:
            print("wrong {}".format(t_url))
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