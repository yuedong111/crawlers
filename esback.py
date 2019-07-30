from utils.esbackends import EsBackends
from utils.sqlbackends import session_scope
from utils.models import MeiTuanShop, JingDong, EnterpriseCq
from utils.make_sessions import create_qiye_session
import time
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from sqlalchemy import and_


def sql_to_es():
    with session_scope() as sess:
        ms = sess.query(JingDong).all()
        es = EsBackends("jingdong")
        for item in ms:
            res = {}
            res["link"] = item.productUrl
            res["status"] = 1
            res["date"] = time.time()
            es.index_data(res)


def es_search(index, url):
    es = EsBackends(index)
    body = {
        "query": {

            "multi_match": {

                "query": url,

                "type": "phrase",

                "slop": 0,

                "fields": [

                    "link"

                ],

                # "analyzer": "charSplit",

                "max_expansions": 1

            }

        }

    }
    res = es.search_data(body)
    # fl = url[url.find("/name") + len("/name"):]
    print(res)
    if res.get("hits").get("hits"):
        for item in res.get("hits").get("hits"):
            # fu = item.get("_source").get("link")
            # fd = fu[fu.find("/name") + len("/name"):]
            # print(fd)
            if url.strip() == item.get("_source").get("link"):
                status = item.get("_source").get("status")
                return True, status, item.get("_id")
    return False, 0, None


def add_cate():
    cate = ["电视", "洗衣机", "冰箱", "空调"]
    with session_scope() as sescope:
        ms = sescope.query(JingDong).all()
        for item in ms:
            for ca in cate:
                if ca in item.productName:
                    item.category = ca
                elif "高清" in item.productName:
                    item.category = "电视"
                elif "多门" in item.productName or "柜" in item.productName or "升" in item.productName:
                    item.category = "冰箱"
                elif "挂机" in item.productName or "匹" in item.productName:
                    item.category = "空调"
                elif "衣" in item.productName or "桶" in item.productName or "洗" in item.productName:
                    item.category = "洗衣机"


def fulfil_cate():
    session = create_qiye_session()
    url = "https://gongshang.mingluji.com/chongqing/name/{}"
    from urllib.parse import quote_plus
    with session_scope() as sess:
        ms = sess.query(EnterpriseCq).filter(EnterpriseCq.enterpriseType == None).all()
        for item in ms:
            name = item.enterpriseName.strip()
            name = quote_plus(name)
            t_url = url.format(name)
            time.sleep(1)
            r = session.get(t_url)
            soup = BeautifulSoup(r.text, "lxml")
            fs = soup.find("fieldset", {"class": "ad_biger"})
            lis = fs.div.find_all("li")
            for li in lis:
                name = li.find("span", {"class": "field-label"}).text.strip()
                value = li.find("span", {"class": "field-item"}).text.strip()
                if "类型" in name:
                    if value:
                        item.enterpriseType = value
                    else:
                        value = lis[-1].find("span", {"class": "field-item"}).span
                        if value:
                            item.enterpriseType = value.text.strip()


def quchong(table):
    with session_scope() as sescope:
        ms = sescope.query(table).all()
        res = []
        for item in ms:
            ids = sescope.query(table).filter(table.url.strip() == item.url.strip()).all()
            if len(ids) > 1:
                for iditem in ids:
                    if iditem.id != item.id:
                        res.append(iditem.id)
                        sescope.delete(iditem)
        print(len(res))


def peixunquchong():
    with session_scope() as sescope:
        ms = sescope.query(MeiTuanShop).all()
        es = EsBackends("meituan")
        for item in ms:
            res = {}
            res["link"] = item.url
            res["status"] = 1
            res["date"] = time.time()
            es.index_data(res)

def newest_data():
    with session_scope() as sess:
        ms = sess.query(EnterpriseCq).order_by(EnterpriseCq.id.desc()).first()
        print(ms.registerDate.strip())


# quchong(MeiTuanShop)
# d = "支持开发票，划重点考试要考的👇🏻👇🏻👇🏻浪漫情💐鲜花店3452345"
# print(d.encode(encoding="gbk", errors="ignore").decode("gbk"))
# newest_data()
# qiyequchong()
# peixunquchong()
# if res[0] and res[1]:
#     print("sousuodao")

# body = {"doc": {'link': 'https://www.meituan.com/xiuxianyule/50803702/', 'status': 1, 'date': '2323232233'}}
# es=Elasticsearch(hosts=["127.0.0.1:9200"])
# resu = es.indices.delete(index="govnews")
# print(resu)
# res = es_search("meituan", "https://www.meituan.com/xiuxianyule/50803702/")
# print(res)
# if res[0] and res[1]:
#     print("sousuodao")
