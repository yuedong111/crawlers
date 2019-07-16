from utils.make_sessions import create_meituan_session
import json
import re
from bs4 import BeautifulSoup
import time
import random
from utils.models import MeiTuanShop
from utils.esbackends import es_search, EsBackends
session = create_meituan_session()
from utils.sqlbackends import session_scope

cookies = "__mta=146208011.1562725971505.1562742466866.1562806821246.4; _lxsdk_cuid=16bd9b99c9ec8-035ab9a6954478-36664c08-1fa400-16bd9b99ca0c8; client-id=047f9384-30b4-4cce-aedb-773f7a31fd8a; mtcdn=K; uuid={}; _lx_utm=utm_source%3Dso.com%26utm_medium%3Dorganic; ci=45; rvct=45%2C114; __mta=146208011.1562725971505.1562729909942.1562742466866.3; IJSESSIONID=vguqtn4rvu70q8m6y7wyaoli; iuuid=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; cityname=%E9%87%8D%E5%BA%86; _lxsdk=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; _hc.v=10962146-cd2f-a7a9-c15a-d942a6e12989.1562744821; lat=29.551617; lng=106.460599; _lxsdk_s=16bde89f341-2f4-c1e-768%7C%7C11"


def parse_jiehun_item(session, url):
    ess = es_search("meituan", url)
    if ess[0] and ess[1]:
        pass
    else:
        time.sleep(random.uniform(1, 3))
        print("pase jiehun url {}".format(url))
        resu = {}
        jiehun_url = "https://www.meituan.com/jiehun/{}/"
        # session.headers[
        #     "Cookie"] = "__mta=146208011.1562725971505.1562821920182.1562822162903.6; _lxsdk_cuid=16bd9b99c9ec8-035ab9a6954478-36664c08-1fa400-16bd9b99ca0c8; client-id=047f9384-30b4-4cce-aedb-773f7a31fd8a; mtcdn=K; uuid=3b49df191ddb4094bc3c.1562729907.1.0.0; _lx_utm=utm_source%3Dso.com%26utm_medium%3Dorganic; ci=45; rvct=45%2C114; IJSESSIONID=vguqtn4rvu70q8m6y7wyaoli; iuuid=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; cityname=%E9%87%8D%E5%BA%86; _lxsdk=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; _hc.v=10962146-cd2f-a7a9-c15a-d942a6e12989.1562744821; __mta=146208011.1562725971505.1562742466866.1562812609604.4; lat=29.535538; lng=106.512486; _lxsdk_s=16bdf56dfcd-a48-5e0-95b%7C%7C18"
        r = session.get(url, timeout=5)
        rule = r'window.AppData = (.+?);</script>'
        slotList = re.findall(rule, r.text)
        if slotList:
            res = json.loads(slotList[0])
            # print(res)
            # if res.get("poiParam").get("uuid"):
            #     session.headers["Cookie"] = cookies.format(res.get("poiParam").get("uuid"))
            shoplist = res.get("searchResult").get("searchResult")
            for item in shoplist:
                resu["score"] = item.get("avgscore")
                resu["shop"] = item.get("title")
                resu["address"] = item.get("address")
                shop_id = item.get("id")
                target = jiehun_url.format(shop_id)
                resu["url"] = target
                res = parse_jiehun_phone(session, target)
                resu.update(res)
                mt = MeiTuanShop(**resu)
                with session_scope() as session1:
                    session1.add(mt)
                if not ess[1] and ess[0]:
                    EsBackends("meituan").update_data(id=ess[2],
                                                      body={"link": url, "status": 1, "date": time.time()})
                if not ess[0]:
                    EsBackends("meituan").index_data({"link": url, "status": 1, "date": time.time()})
        else:
            print("获取不到值 {}".format(url))
            if not ess[0]:
                EsBackends("meituan").index_data({"link": url, "status": 0, "date": time.time()})
            else:
                EsBackends("meituan").update_data(id=ess[2],
                                                  body={"link": url, "status": 0, "date": time.time()})


def parse_jiehun_phone(session, url):
    time.sleep(random.uniform(1, 2))
    res = {}
    print("parse shop {}".format(url))
    r = session.get(url, timeout=5)
    soup = BeautifulSoup(r.text, 'lxml')
    head = soup.find("div", {"id": "J_boxYouhui"})
    if not head:
        head = soup.find("div", {"id": "J_boxPromo"})
        div = head.div.find("p").find("span",{"class": "item"})
    else:
        div = head.find("div", {"class": "shop-contact"})
    if div:
        phone1 = div.text.strip().split()
        res["phone"] = " ".join(phone1)
    try:
        opent = soup.find("div", {"class": "J_showWarp"})
        trs = opent.find_all("tr")
        for item in trs:
            if "营业时间" in item.text:
                ot = item.text.strip()
                ot = " ".join(ot.split()[1:])
                res["openTime"] = ot
    except:
        res["openTime"] = ""
    return res


def parse_meishi_item(session, url):
    time.sleep(random.uniform(1, 3))
    meishi_url = "https://www.meituan.com/meishi/{}/"
    # session.headers[
    #     "Cookie"] = "__mta=146208011.1562725971505.1562742466866.1562806821246.4; _lxsdk_cuid=16bd9b99c9ec8-035ab9a6954478-36664c08-1fa400-16bd9b99ca0c8; client-id=047f9384-30b4-4cce-aedb-773f7a31fd8a; mtcdn=K; uuid=3b49df191ddb4094bc3c.1562729907.1.0.0; _lx_utm=utm_source%3Dso.com%26utm_medium%3Dorganic; ci=45; rvct=45%2C114; __mta=146208011.1562725971505.1562729909942.1562742466866.3; IJSESSIONID=vguqtn4rvu70q8m6y7wyaoli; iuuid=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; cityname=%E9%87%8D%E5%BA%86; _lxsdk=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; _hc.v=10962146-cd2f-a7a9-c15a-d942a6e12989.1562744821; lat=29.551617; lng=106.460599; _lxsdk_s=16bde89f341-2f4-c1e-768%7C%7C11"
    r = session.get(url, timeout=5)
    rule = r"window._appState = (.+?);</script>"
    slotList = re.findall(rule, r.text)
    if slotList:
        res = json.loads(slotList[0])
        if res.get("uuid"):
            session.headers["Cookie"] = cookies.format(res.get("uuid"))
        pl = res.get("poiLists")
        sl = pl.get("poiInfos")
        for item in sl:
            # score = item.get("avgScore")
            # print(item.get("title"))
            # print(item.get("address"))
            target = meishi_url.format(item.get("poiId"))
            yield target


# parse_jiehun_item(session, "https://cq.meituan.com/jiehun/pn2/")
# parse_meishi_item("https://cq.meituan.com/meishi/pn2/")
# parse_jiehun_phone(session, "https://www.meituan.com/jiehun/161830207/")
