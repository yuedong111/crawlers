# -*- coding: utf-8 -*-
import requests
from selenium import webdriver
from bs4 import BeautifulSoup


def create_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        ),
        # "Referer": "https://item.jd.com/4609660.html",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                  "image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2,"
                           "ja;q=0.2,ru;q=0.2,gl;q=0.2,ko;q=0.2",
        "Pragma": "no-cache",
    }
    return s


def create_webdriver() -> webdriver.Chrome:
    opt = webdriver.ChromeOptions()
    # opt.add_argument('headless')
    opt.add_argument('--disable-gpu')
    opt.add_argument('window-size=1280,720')
    # opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36")
    opt.add_experimental_option('excludeSwitches', ['enable-automation'])
    opt.add_argument('log-level=3')
    d = webdriver.Chrome(chrome_options=opt)
    return d


def create_meituan_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
        # "Referer": "http://cq.meituan.com/meishi/",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Host": "cq.meituan.com",
        "Cookie": "__mta=20889095.1562725959175.1562725959175.1564211556336.2; _lxsdk_cuid=16bd9b99c9ec8-035ab9a6954478-36664c08-1fa400-16bd9b99ca0c8; __mta=20889095.1562725959175.1562725959175.1562725959175.1; iuuid=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; cityname=%E9%87%8D%E5%BA%86; _lxsdk=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; _hc.v=10962146-cd2f-a7a9-c15a-d942a6e12989.1562744821; ci=45; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1562914412,1563263956; rvct=45%2C1%2C114; _ga=GA1.2.1247011406.1563181057; uuid=8277f3ea41b7463db851.1564104218.1.0.0; client-id=1f96d392-0947-4a40-b9b0-36d8d749ea88; lat=29.0371; lng=106.6734; _lxsdk_s=16c323f1d11-01d-109-894%7C%7C9"
    }
    return s


def create_qiye_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Host": "gongshang.mingluji.com",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": "__utmz=152261551.1562899049.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); has_js=1; Hm_lvt_f733651f7f7c9cfc0c1c62ebc1f6388e=1563152848,1563179374,1563868785,1564360505; __utmc=152261551; __utma=152261551.328900377.1562899049.1564369508.1564384398.28; __utmt=1; __utmb=152261551.5.10.1564384398; Hm_lpvt_f733651f7f7c9cfc0c1c62ebc1f6388e=1564385360",
    }
    return s


def create_yaowen_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Host": "spb.cq.gov.cn",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": "yjtc_client_visit_cookie=yjtc_c48f3a770ed74ab1929a811f866ec49a; _gscu_291166401=63184235agmjiw91; _gscbrs_291166401=1; UM_distinctid=16bf50a8450476-00b7d0ed2a109b-e343166-1fa400-16bf50a8451895; JSESSIONID=2B85A3568487B56E6D9754F216336FF4; CNZZDATA1277379281=1108448340-1563182331-https%253A%252F%252Fwww.baidu.com%252F%7C1563234537; _gscs_291166401=t63237516wf6aax47|pv:2"
    }
    return s


def create_dianping_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        ),
        "Referer": "www.dianping.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.dianping.com",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": """navCtgScroll=0; showNav=javascript:; showNav=javascript:; navCtgScroll=0; _hc.v="\"85fd17cf-fdb1-490d-9e4e-2b7090d0ae6c.1562822672\""; _lxsdk_cuid=16c22ac17a87c-0b6f1684f738ee-36664c08-1fa400-16c22ac17a9c8; _lxsdk=16c22ac17a87c-0b6f1684f738ee-36664c08-1fa400-16c22ac17a9c8; cy=9; cye=chongqing; s_ViewType=10; aburl=1; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1563950118; cy=9; cityid=9; cye=chongqing; wedchatguest=g110114642626128510; cityInfo=%7B%22cityId%22%3A9%2C%22cityName%22%3A%22%E9%87%8D%E5%BA%86%22%2C%22provinceId%22%3A0%2C%22parentCityId%22%3A0%2C%22cityOrderId%22%3A0%2C%22isActiveCity%22%3Afalse%2C%22cityEnName%22%3A%22chongqing%22%2C%22cityPyName%22%3Anull%2C%22cityAreaCode%22%3Anull%2C%22cityAbbrCode%22%3Anull%2C%22isOverseasCity%22%3Afalse%2C%22isScenery%22%3Afalse%2C%22TuanGouFlag%22%3A0%2C%22cityLevel%22%3A0%2C%22appHotLevel%22%3A0%2C%22gLat%22%3A0%2C%22gLng%22%3A0%2C%22directURL%22%3Anull%2C%22standardEnName%22%3Anull%7D; Hm_lvt_4c4fc10949f0d691f3a2cc4ca5065397=1564034271; Hm_lpvt_4c4fc10949f0d691f3a2cc4ca5065397=1564034271; wed_user_path=1040|0; _lx_utm=utm_source%3Dlbdt; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1564046168; lastVisitUrl=%2Fchongqing%2Fhotel; selectLevel=%7B%22level1%22%3A%222%22%2C%22level2%22%3A%221%22%7D; _lxsdk_s=16c27f8f515-43-5aa-8cb%7C%7C2565""",
    }
    return s


def create_tuniu_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        ),
        "Referer": "http://hotel.tuniu.com/list/300p0s0b0/?city=300&poi=0&stars=0&brands=0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "hotel.tuniu.com",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": "tuniuuser_citycode=MzAw; p_phone_400=4007-999-999; p_phone_level=0; p_global_phone=%2B0086-25-8685-9999; _tacau=MCwwOWIxYWRkZi05ZDgxLTI4MzgtZTRkZi0yNjFiOWUwMjI3ZWMs; _tact=MWU4ZWU5MzUtYWEzNC1iZTZkLTQ0OGYtNTdlNWE4NGJkMzRm; _tacc=1; _ga=GA1.2.350844114.1564131863; OLBSESSID=cpgp411o03nm6ae7s5iekmiqi1; MOBILE_APP_SETTING_STATE-126=CLOSE; hotel_view_history_new_guid=974C1855-9D94-3C70-F0D7-18A4AF4F7DFB; UM_distinctid=16c2d86d4fc71b-0d1aa791e3325a-36664c08-1fa400-16c2d86d4fd5a4; __xsptplus352=352.4.1564216598.1564216598.1%234%7C%7C%7C%7C%7C%23%234vRGfgDQNnXazGokMMmVKTpiK30rD0XB%23; tuniu_partner=MTc2NTgsMCwsN2Q1YjI4Y2Y1NDViOGZjYjllNjBkMTZkMTNhNTYyOTU%3D; _tacz2=taccsr%3Dwww.so%7Ctacccn%3D%28organic%29%7Ctaccmd%3D%28none%29%7Ctaccct%3D%2525E9%252580%252594%2525E7%252589%25259B%2525E6%252597%252585%2525E8%2525A1%25258C%2525E7%2525BD%252591%7Ctaccrt%3D%28none%29; _taca=1564131857258.1564216598446.1564369575147.5; _tacb=NzA1OTE1M2UtOWNmZC1kZTU3LWRjODgtYzhmNDcwYjJmMDE0; PageSwitch=1%2C213612736; _gid=GA1.2.376646834.1564369575; MOBILE_APP_SETTING_OPEN-126=1; tuniuuser_ip_citycode=MzAw; isHaveShowPriceTips=1; Hm_lvt_51d49a7cda10d5dd86537755f081cc02=1564369589; Hm_lpvt_51d49a7cda10d5dd86537755f081cc02=1564369589; hotel_index_search_history=eyJfMzAwIjp7ImNoZWNraW5kYXRlIjoiMjAxOS03LTMwIiwiY2hlY2tvdXRkYXRlIjoiMjAxOS03LTMxIiwiY2l0eV9pZCI6IjMwMCIsImNpdHlfbmFtZSI6IumHjeW6hiJ9fQ==; hotel_checkindate=2019-7-30; hotel_checkoutdate=2019-7-31; hotel_order_begin_date=2019-7-30; hotel_order_end_date=2019-7-31; CNZZDATA5726564=cnzz_eid%3D550169148-1564129206-http%253A%252F%252Fhotel.tuniu.com%252F%26ntime%3D1564367298; _pzfxuvpc=1564131862548%7C3416526400151055857%7C22%7C1564369613459%7C5%7C2167611298499104658%7C1087456991132054631; _pzfxsvpc=1087456991132054631%7C1564369575216%7C4%7Chttps%3A%2F%2Fwww.so.com%2Fs%3Fq%3D%25E9%2580%2594%25E7%2589%259B%25E6%2597%2585%25E8%25A1%258C%25E7%25BD%2591%26src%3Dsrp_suggst_brand_ci_7%26fr%3Dlm%26ls%3Dsm2338310%26lm_extend%3Dctype%253A31%26psid%3Da138216431274d24ab452da02a0607c2%26eci%3D%26nlpv%3Dbrand_ci_7; rg_entrance=010000%2F003001%2F000013%2F000000"
    }
    return s


def create_shunqi_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": "Hm_lvt_819e30d55b0d1cf6f2c4563aa3c36208=1564452370,1564452440; Hm_lpvt_819e30d55b0d1cf6f2c4563aa3c36208=1564452881"
    }
    return s


USERAGETNS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "User-Agent,Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "User-Agent,Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
    "User-Agent,Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "User-Agent,Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
]
COOKIES = "__mta=20889095.1562725959175.1562725959175.1564211556336.2; _lxsdk_cuid=16bd9b99c9ec8-035ab9a6954478-36664c08-1fa400-16bd9b99ca0c8; __mta=20889095.1562725959175.1562725959175.1562725959175.1; iuuid=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; cityname=%E9%87%8D%E5%BA%86; _lxsdk=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; _hc.v=10962146-cd2f-a7a9-c15a-d942a6e12989.1562744821; ci=45; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1562914412,1563263956; rvct=45%2C1%2C114; _ga=GA1.2.1247011406.1563181057; uuid=8277f3ea41b7463db851.1564104218.1.0.0; client-id=1f96d392-0947-4a40-b9b0-36d8d749ea88; lat=29.0371; lng=106.6734; _lxsdk_s=16c323f1d11-01d-109-894%7C%7C9"

def get_proxy(cate, count):
    ps_map = {"http": "wn", "https": "wt"}
    url = "https://www.xicidaili.com/{}/{}".format(ps_map.get(cate), count)
    sess = create_session()
    tempsess = create_session()
    sess.headers["Cookie"] = "_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTkyMGE1Njc3OGJhMTBhMzM2NDc5Yjg3MzQ1ZjI5YWJlBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMVg0MGhVS2ZQSkZPKzJ6ODdHMXFuTm5wcU1JaU9QdmZyVFJxaUxKMUltZnc9BjsARg%3D%3D--329dbe3773b6716dd5a7af1a839dd6d3dbcd0cbe; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1562986629; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1562986629"
    # sess.headers["If-None-Match"] = 'W/"274d5059b4169aae70610422d50be14b"'
    sess.headers["Upgrade-Insecure-Requests"] = "1"
    sess.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"
    sess.headers["Accept-Encoding"] = "gzip, deflate, br"
    sess.headers["Accept-Language"] = "zh-CN,zh;q=0.9"
    sess.headers["Host"] = "www.xicidaili.com"
    sess.headers["Connection"] = "keep-alive"
    sess.headers["Cache-Control"] = "max-age=0"
    # sess.headers["Referer"] = "https://www.xicidaili.com/wt/"
    sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
    r = sess.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    iplist = soup.find("table", {"id": "ip_list"})
    # print(iplist)
    trs = iplist.find_all("tr")
    result = []
    for item in trs[1:]:
        tds = item.find_all("td")
        for td in tds:
            if td.div:
                if td.div.div and "fast" in td.div.div.get("class"):
                    temp = {"ip": tds[1].text, "port": tds[2].text}
                    check = "{}://{}:{}".format(cate, tds[1].text, tds[2].text)
                    try:
                        tempsess.proxies = {cate: check}
                        r = tempsess.get("http://icanhazip.com/", timeout=0.5)
                        print(r.text, r.status_code)
                        if r.text.strip() == temp.get("ip"):
                            print(temp)
                            result.append(temp)
                    except Exception as e:
                        # print(e)
                        break
    return result


def collect_ip():
    count = 555
    while count < 2000:
        print(count)
        d= get_proxy("http", str(count))
        if d:
            return d
        count = count + 1


# collect_ip()