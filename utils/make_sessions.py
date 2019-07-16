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
        # "Cookie": "shshshfpa=6df8fdaa-e06d-7dc1-2d9a-34565b9b29b1-1540522217; shshshfpb=12377aea9c06e4a55b38e8af29c2ca6630103a320e274ca1c5bd280ea9; areaId=4; PCSYCityID=4; ipLoc-djd=4-50953-50979-0; user-key=5ef807ad-037f-4f77-b3dc-3db51b4c445c; cn=1; __jdu=1540522216092634850635; unpl=V2_ZzNtbUZTRUVyAUdRLB5cB2IEGltLXkpFdQkTUn1JWQNjB0BaclRCFX0UR1JnGFQUZgoZWUJcRhdFCEdkexhdBGYBGlhLVXNILGYAUydcWl5XWEdtQVdzFEUIQlF6HV8GZAMVXEpURBdwAUJVfBtYNVcDGllyZx5NKlIfBCNcDFtXBRZYQVdGFH0IdlVLGGxOCQJfXUZSQhF2C0VUfBhUBmABF1RGVkQXcThHZHg%3d; __jdc=122270672; __jdv=122270672|www.linkhaitao.com|t_1000039483_lh_w6mt7j|tuiguang|557a6804f6134697888a10d77a4755c6|1562633501957; _gcl_au=1.1.1057568808.1562634415; shshshfp=f1f433d12a9a2da86d006c406afb4e99; 3AB9D23F7A4B3C9B=WJ6IQM255ZG6RDIXPNYYWDBUXXKFSEXTM5SEIXCJHCAKRBG7T4SRDCWMWCKZO6ADG73VDIEO6WDHNOSP2G2RLEGIDU; __jda=122270672.1540522216092634850635.1540522216.1562633502.1562639202.13; JSESSIONID=70E7F0502327256D53109F354BD10F47.s1; shshshsID=00abbc85aad2ce14682c8f1d9ec557f2_4_1562639533322; __jdb=122270672.4.1540522216092634850635|13.1562639202"
    }
    return s


def create_webdriver() -> webdriver.Chrome:
    opt = webdriver.ChromeOptions()
    opt.add_argument('headless')
    opt.add_argument('--disable-gpu')
    opt.add_argument('window-size=1280,720')
    opt.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36")
    opt.add_experimental_option('excludeSwitches', ['enable-automation'])
    d = webdriver.Chrome(chrome_options=opt)
    return d


def create_meituan_session():
    s = requests.Session()
    s.headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2,"
                           "ja;q=0.2,ru;q=0.2,gl;q=0.2,ko;q=0.2",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
        # "Referer": "http://cq.meituan.com/meishi/",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Cookie": "_lxsdk_cuid=16bd9b99c9ec8-035ab9a6954478-36664c08-1fa400-16bd9b99ca0c8; __mta=20889095.1562725959175.1562725959175.1562725959175.1; mtcdn=K; ci=45; rvct=45%2C114; iuuid=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; cityname=%E9%87%8D%E5%BA%86; _lxsdk=8369B0074906E31235D094B1D10CB5398B04DC92AAFDBADB7477CB96EEFF986E; _hc.v=10962146-cd2f-a7a9-c15a-d942a6e12989.1562744821; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1562914412; uuid=dd98538429474553a0f0.1563160693.1.0.0; client-id=7fcaa6d4-5179-4c89-bc4d-555478116e0d; lat=29.553193; lng=106.575508; _lxsdk_s=16bf47aac77-e93-952-171%7C%7C33"
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
        "Cookie": "__utmz=152261551.1562899049.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); has_js=1; __utmc=152261551; Hm_lvt_f733651f7f7c9cfc0c1c62ebc1f6388e=1562899049,1562983216,1563152848,1563179374; __utma=152261551.328900377.1562899049.1563179374.1563237230.7; __utmt=1; __utmb=152261551.2.10.1563237230; Hm_lpvt_f733651f7f7c9cfc0c1c62ebc1f6388e=1563237264"
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


USERAGETNS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "User-Agent,Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "User-Agent,Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
    "User-Agent,Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "User-Agent,Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36"
]
COOKIES = "__mta=151828102.1562565124818.1562824670554.1562824729202.6; _ga=GA1.2.1825814531.1546998833; _lxsdk_cuid=16bd023931bc8-066f6cebecafc4-e343166-1fa400-16bd023931bc8; _hc.v=3c8a39ae-eab5-7e72-9895-1e0cefa4d0eb.1562565129; uuid=bdc40862df5c4c0bbe55.1562652623.1.0.0; IJSESSIONID=pldhhf1x477h2s7ivnhqaz0g; iuuid=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258; cityname=%E9%87%8D%E5%BA%86; _lxsdk=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258; ci=45; rvct=45%2C1; mtcdn=K; userTicket=XQasjWTqmGsUMgtOCcZINxYWlPFPQdghHWrDJFSz; lsu=; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; webp=1; __utmc=74597006; __utmz=74597006.1562738329.1.1.utmcsr=blog.csdn.net|utmccn=(referral)|utmcmd=referral|utmcct=/xing851483876/article/details/81842329; ci3=1; a2h=4; __utma=74597006.1825814531.1546998833.1562738329.1562738511.2; i_extend=H__a100001__b2; latlng=29.5904,106.509888,1562747757451; client-id=07550f00-06b7-4bde-9d07-d78624821eb4; lat=29.599689; lng=106.549822; __mta=151828102.1562565124818.1562810227184.1562824667042.8; _lxsdk_s=16bdf9be952-e87-81-ce%7C%7C8"


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