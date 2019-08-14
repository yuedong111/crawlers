from utils.models import MeiTuanShop, JingDong, EnterpriseCq, GoverNews, WaiMai, XieCheng, DZDianPingCQ, TuNiu, ShunQi, \
    WGQY, TuNiuAll, BFZY, DZDianPing, BFZYCQ, SouLeWang, QYLu, HuangYe
from utils.sqlbackends import session_scope, session_scope_remote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import time
from sqlalchemy import or_

datatable = ["MeiTuanShop", "JingDong", "EnterpriseCq", "GoverNews"]

mysql_client_remote = create_engine(
    "mysql+mysqlconnector://root:password@192.168.1.166:3306/crawls?charset=utf8",
    encoding="utf-8",
)
session_sql_remote = sessionmaker(bind=mysql_client_remote)


def table_back():
    atts = globals()
    for item1 in datatable:
        table = atts.get(item1)
        count = 0
        session_remote = session_sql_remote()
        with session_scope() as sess1:
            ms = sess1.query(table).filter().all()
            for item in ms:
                print(item.__dict__)
                temp = item.__dict__
                temp["id"] = None
                temp.pop("_sa_instance_state")
                ta = table(**temp)
                count = count + 1
                session_remote.add(ta)
                if count % 5000 == 0:
                    session_remote.commit()
            session_remote.commit()


query_map = {"MeiTuanShop": "select id from meiTuanShop where shop='{shop}' and phone='{phone}' and url='{url}'",
             "JingDong": "select id from jingDong where productName='{productName}' and productUrl='{productUrl}' and price='{price}'",
             "EnterpriseCq": "select id from enterprise where enterpriseName='{enterpriseName}' and address='{address}' and socialCreditCode='{socialCreditCode}'",
             "GoverNews": "select id from govermentnews where title='{title}' and publishDate='{publishDate}' and url='{url}'",
             "WaiMai": "select id from meituanwaimai where url='{url}'",
             "XieCheng": "select id from xiechenghotel where url = '{url}'",
             "DZDianPing": "select id from dianping where url = '{url}'",
             "TuNiu": "select id from tuniu where url = '{url}'",
             "ShunQi": "select id from shunqi where url = '{url}'",
             "WGQY": "select id from wanguoqiye where url = '{url}'",
             "TuNiuAll": "select id from tuniuquanguo where url = '{url}'",
             "BFZY": "select id from bafangziyuan where url = '{url}'",
             "BFZYCQ": "select id from bafangziyuanchongqing where url = '{url}'",
             "DZDianPingCQ": "select id from dazhongdianping where url = '{url}'",
             "SouLeWang": "select id from 51sole where url = '{url}'",
             "QYLu": "select id from qiyelu where url = '{url}'",
             "HuangYe": "select id from huangye88 where url = '{url}'",
             }


def zengliang_back():
    atts = globals()
    session_remote = session_sql_remote()
    for item1 in query_map.keys():
        # print(item1)
        table = atts.get(item1)
        ms = session_remote.query(table).order_by(table.id.desc()).first()
        with session_scope() as sess1:
            if not ms:
                dd = [0]
            else:
                res = sess1.execute(query_map.get(item1).format(**ms.__dict__))
                dd = []
                for id in res.fetchall():
                    dd.append(id[0])
                if not dd:
                    continue
            id_new = max(dd)
            if len(dd) >= 2:
                print("youchongfu {} {}".format(item1, dd))
            ms = sess1.query(table).filter(table.id > id_new).all()
            count = 0
            for item in ms:
                print(item.__dict__)
                temp = item.__dict__
                temp["id"] = None
                temp.pop("_sa_instance_state")
                if "businessScope" in temp:
                    tt = temp.get("businessScope")
                    if tt and len(tt) > 666:
                        temp["businessScope"] = tt[: 600]
                ta = table(**temp)
                count = count + 1
                session_remote.add(ta)
                if count % 1000 == 0:
                    session_remote.commit()
            session_remote.commit()
    session_remote.close()


def total_count():
    atts = globals()
    session_remote = session_sql_remote()
    total = 0
    res = {}
    for item1 in query_map.keys():
        table = atts.get(item1)
        ms = session_remote.query(table).count()
        total += ms
        res[item1] = ms
    res["total"] = total
    print(res)


def get_attr_for_check(table):
    res = []
    for item in dir(EnterpriseCq):
        if not item.startswith("__") and item != "id" and not item.startswith(
                "_") and "date" not in item.lower() and "type" not in item.lower():
            res.append(item)
    return res


def fix_funds():
    with session_scope() as sess:
        na = sess.query(BFZY).filter(BFZY.registeredFunds == None).all()
        for item1 in na:
            if item1.about:
                tem = item1.about.split("；")
                for item in tem:
                    t = item.split("：")
                    if "注册资金" == t[0]:
                        item1.registeredFunds = t[1]


def tuniutongbu():
    with session_scope() as sess:
        with session_scope_remote() as sess_remote:
            na = sess.query(TuNiuAll).filter(or_(TuNiuAll.phone != None, TuNiuAll.district != None)).all()
            for item in na:
                ture = sess_remote.query(TuNiuAll).filter(TuNiuAll.url == item.url).first()
                if not ture.phone and not ture.district:
                    ture.phone = item.phone
                    ture.district = item.district
                    sess_remote.commit()


if __name__ == "__main__":
    zengliang_back()
    # tuniutongbu()
    # total_count()
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(zengliang_back, 'interval', hours=6)
    # scheduler.start()
    # try:
    #     while True:
    #         time.sleep(10)
    # except (KeyboardInterrupt, SystemExit):
    #     scheduler.shutdown()
