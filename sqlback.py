from utils.models import MeiTuanShop, JingDong, EnterpriseCq, GoverNews, WaiMai, XieCheng, DZDianPing, TuNiu
from utils.sqlbackends import session_scope, session_scope_remote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
import time

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
             "DZDianPing": "select id from dazhongdianping where url = '{url}'",
             "TuNiu": "select id from tuniu where url = '{url}'",
             }


def zengliang_back():
    atts = globals()
    for item1 in query_map.keys():
        table = atts.get(item1)
        session_remote = session_sql_remote()
        ms = session_remote.query(table).order_by(table.id.desc()).first()
        with session_scope() as sess1:
            if not ms:
                dd = [0]
            else:
                res = sess1.execute(query_map.get(item1).format(**ms.__dict__))
                dd = []
                for id in res.fetchall():
                    dd.append(id[0])
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
                ta = table(**temp)
                count = count + 1
                session_remote.add(ta)
                if count % 1000 == 0:
                    session_remote.commit()
            session_remote.commit()


def get_attr_for_check(table):
    res = []
    for item in dir(EnterpriseCq):
        if not item.startswith("__") and item != "id" and not item.startswith(
                "_") and "date" not in item.lower() and "type" not in item.lower():
            res.append(item)
    return res


if __name__ == "__main__":
    zengliang_back()
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(zengliang_back, 'interval', hours=6)
    # scheduler.start()
    # try:
    #     while True:
    #         time.sleep(10)
    # except (KeyboardInterrupt, SystemExit):
    #     scheduler.shutdown()
