import requests
# from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib
from utils.make_sessions import create_meituan_session, create_webdriver
url = 'http://waimai.meituan.com/ajax/poilist?'
def tt():
    url = "https://waimai.meituan.com/ajax/poilist?_token={}"
    url_part = "classify_type=cate_all&sort_type=0&price_type=0&support_online_pay=0&support_invoice=0&support_logistic=0&page_offset=21&page_size=20&mtsi_font_css_version=fbfd973f&uuid=sc1hcPvIyaPZBE0QsSkAhFqwX2HqN6zQxRCc74e_VCWvu6Ocy45g8S2kTudMAuwR&platform=1&partner=4&originUrl=https%3A%2F%2Fwaimai.meituan.com%2Fhome%2Fwm7c4e547jzc"
    session = create_meituan_session()
    session.headers["Cookie"] = """_ga=GA1.2.1825814531.1546998833; _lxsdk_cuid=16bd023931bc8-066f6cebecafc4-e343166-1fa400-16bd023931bc8; _hc.v=3c8a39ae-eab5-7e72-9895-1e0cefa4d0eb.1562565129; w_utmz="utm_campaign=(direct)&utm_source=(direct)&utm_medium=(none)&utm_content=(none)&utm_term=(none)"; w_uuid=sc1hcPvIyaPZBE0QsSkAhFqwX2HqN6zQxRCc74e_VCWvu6Ocy45g8S2kTudMAuwR; _ga=GA1.3.1825814531.1546998833; iuuid=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258; _lxsdk=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258; lsu=; webp=1; a2h=4; uuid=28a5322f-73aa-4105-9f73-e89a9f269c19; lat=29.379629; lng=106.508968; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _gid=GA1.3.94908691.1563514021; waddrname="%E6%B8%9D%E5%8C%97%E5%8C%BA"; w_geoid=wm7c4e547jzc; w_cid=500112; w_cpy=yubeiqu; w_cpy_cn="%E6%B8%9D%E5%8C%97%E5%8C%BA"; w_ah="29.72392799332738,106.63755979388952,%E6%B8%9D%E5%8C%97%E5%8C%BA|29.547192882746458,106.46446477621794,%E6%B2%99%E5%9D%AA%E5%9D%9D%E5%8C%BA"; wm_order_channel=default; utm_source=; au_trace_key_net=default; openh5_uuid=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258; cssVersion=e7b07c0d; w_visitid=a6e81603-aad3-4196-bbb4-1b5e142f1a3d; __mta=19355143.1562652960491.1563514446993.1563519385490.10; JSESSIONID=1fuhw9hnatu1kwuka3fzu9vpz; IJSESSIONID=15mjbuk0aqekc17d0vnnrqakfu; __utma=74597006.1825814531.1546998833.1562738511.1563519924.3; __utmc=74597006; __utmz=74597006.1563519924.3.2.utmcsr=blog.csdn.net|utmccn=(referral)|utmcmd=referral|utmcct=/xing851483876/article/details/81842329; ci3=1; rvct=30%2C1%2C45; latlng=29.607883,106.289549,1563519957917; ci=45; cityname=%E9%87%8D%E5%BA%86; i_extend=C189913015384320739764905118182476349850_b1_c0_e153957522001196166114GimthomepageallcateH__a100001__b3; __utmb=74597006.11.9.1563520047564; _gat=1; _lxsdk_s=16c08b298fb-479-720-5d5%7C%7C95"""
    # session.headers["Cookie"] = """_ga=GA1.2.1825814531.1546998833; _lxsdk_cuid=16bd023931bc8-066f6cebecafc4-e343166-1fa400-16bd023931bc8; _hc.v=3c8a39ae-eab5-7e72-9895-1e0cefa4d0eb.1562565129; w_utmz="utm_campaign=(direct)&utm_source=(direct)&utm_medium=(none)&utm_content=(none)&utm_term=(none)"; w_uuid=sc1hcPvIyaPZBE0QsSkAhFqwX2HqN6zQxRCc74e_VCWvu6Ocy45g8S2kTudMAuwR; _ga=GA1.3.1825814531.1546998833; iuuid=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258; cityname=%E9%87%8D%E5%BA%86; _lxsdk=C1EA418E59192BE72919EF4468CFA088AFC416E2D10120BB18440DA3BF854258; lsu=; webp=1; __utmz=74597006.1562738329.1.1.utmcsr=blog.csdn.net|utmccn=(referral)|utmcmd=referral|utmcct=/xing851483876/article/details/81842329; a2h=4; __utma=74597006.1825814531.1546998833.1562738329.1562738511.2; i_extend=H__a100001__b2; ci=1; rvct=1%2C45; uuid=28a5322f-73aa-4105-9f73-e89a9f269c19; lat=29.379629; lng=106.508968; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; w_visitid=a5730afa-b068-4383-8d81-63bdb54e4862; _gid=GA1.3.94908691.1563514021; __mta=19355143.1562652960491.1562724541943.1563514021916.8; waddrname="%E6%B2%99%E5%9D%AA%E5%9D%9D%E5%8C%BA"; w_geoid=wm78ndvhcgfz; w_cid=500106; w_cpy=shapingbaqu; w_cpy_cn="%E6%B2%99%E5%9D%AA%E5%9D%9D%E5%8C%BA"; w_ah="29.547192882746458,106.46446477621794,%E6%B2%99%E5%9D%AA%E5%9D%9D%E5%8C%BA"; JSESSIONID=1m1fko4dqfqffs1pf0rg7ny1s; _lxsdk_s=16c08b298fb-479-720-5d5%7C%7C8"""
    session.headers["Host"] = "waimai.meituan.com"
    session.headers["Origin"] = "https://waimai.meituan.com"
    session.headers["Referer"] = "https://waimai.meituan.com/home/wm7c4e547jzc"
    session.headers["X-FOR-WITH"] = "+lHk/N6Q9uaY3Tzpeuo9ROcfGvsgcl8Buo7Vs+MGKtxoqTqnAHsH4F+b8mv5Umzg8ft7p0LHh8p577Es5MYJ6WN1zgK0n8D4fISWvoap57EYNFDH2Iu9qtZNEpXYEZLN1ZNmecB/MNbW7PZP/r7IIg=="
    session.headers["X-Requested-With"] = "XMLHttpRequest"
    session.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
    session.headers["Accept-Language"] = "zh-CN,zh;q=0.9,ja-JP;q=0.8,ja;q=0.7,en-US;q=0.6,en;q=0.5"
    session.headers["Accept-Encoding"] = "gzip, deflate, br"
    session.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    session.headers["Content-Length"] = "330"


    test_url = "https://waimai.meituan.com/ajax/poilist?_token=eJx90ltvokAUAOD/Mq8S5wIDjEkfREuLd7BodbMPqKggAwoI6mb/+w7ttrNPS0j4cm45OeEXyJ0d6GAkHkMBVZiDDsBt1NaBAspCZKiuUoI0hFSdKmD7b4xiZmgK2OSLPuj8wAwRRWX4ZxPxREBECFIwMtFP5ctUmGjibaocUQSOZXkuOhDWQcSDqM3DqLwGaXubcXjMeAhrbmy1kGpG/NiKnf5TDsRM/tbMZIQo2CSGqP9L+kHcUJNUJYkklkTfxEzSlDQk9Q+ihpoklkTfRB/DMGtoSOqSVFKTJJL4iwZjkqYklSSSss2UbebnDmbDzza9odoc9NQcVHyD78OqOlP6zqJJll/JsfhrRGMRHVKhcHCbxEUyrR9d39u3kuh+30yes0109eyL36u7/ayOVjhRB/uT70Nc3Kbz/B5mz9f8ml6mj6s1PVuWvZy5Lda9r+1uT/fnqXugAx8f/CJSMyctnVUZtW45X4bu0jExT8JqaU17WatAhutdDovx5GXo1D5JMEkOkyDYjZbbnjkcma/87eh1jd3C86zVLC5ize0WD7Sp65WVeuHQ7w3eMc+I7dVpGuCkh7M9fF2rhvuYl6/r8Sgj94ltW+HwpfBfxLJsOB0/u60xHd49DoOjTasZZ2Uxh1V8yU/GzoMUhsl5vLzBHS/XdtHf4ysr3/uPUXWO3xewMluWM4v1amXMA7jhye1UPz2B338A6rr1bA=="

    data = {"classify_type": "cate_all",
            "sort_type": "0",
            "price_type": "0",
            "support_online_pay": "0",
            "support_invoice": "0",
            "page_offset": "21",
            "page-size": "20",
            "mtsi_font_css_version": "940b920e",
            "uuid": "sc1hcPvIyaPZBE0QsSkAhFqwX2HqN6zQxRCc74e_VCWvu6Ocy45g8S2kTudMAuwR",
            "platform": "1",
            "partner": "4",
            "originUrl": "https%3A%2F%2Fwaimai.meituan.com%2Fhome%2Fwm7c4e547jzc"}
    r = session.post(test_url, json=data, allow_redirects=False)
    print(r.text)

driver = create_webdriver()
driver.get("https://meituan.com/")
driver.get("https://waimai.meituan.com/home/wm7c4e547jzc")

change_tag = """
var haha = document.getElementsByClassName('bottom')[0].getElementsByTagName("span");
haha[1].innerText = {};
"""
cookies = driver.get_cookies()
data = {"classify_type": "cate_all",
            "sort_type": "0",
            "price_type": "0",
            "support_online_pay": "0",
            "support_invoice": "0",
            "support_logistic": "0",
            "page_offset": "21",
            "page-size": "20",
            "mtsi_font_css_version": "940b920e",
            "uuid": "sc1hcPvIyaPZBE0QsSkAhFqwX2HqN6zQxRCc74e_VCWvu6Ocy45g8S2kTudMAuwR",
            "platform": "1",
            "partner": "4",
            "originUrl": "https%3A%2F%2Fwaimai.meituan.com%2Fhome%2Fwm7c4e547jzc"}
for item in cookies:
    if item.get("name") =="w_uuid":
        data["uuid"] = item.get("value")
dtoken = urllib.parse.urlencode(data)
script = "Rohr_Opt.reload('{}')".format(url + dtoken)
driver.execute_script(change_tag.format(script))
cookies = driver.get_cookies()
for item in cookies:
    if item.get("name") =="w_uuid":
        data["uuid"] = item.get("value")
print(cookies)

# driver.get_log('browser')
# print(r)
# print(dir(driver))
# print(driver.result)
