import pytesseract
from PIL import Image
from utils.make_sessions import create_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.models import DZDianPing
from utils.sqlbackends import session_scope
import os
import re

fpa = re.compile(r"\d+")

driver = create_webdriver()


def cut_imge(url):
    driver.get(url)
    while "https://verify.meituan.com/v2/" in driver.current_url:
        print("输入验证码")
        time.sleep(10)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="basic-info"]')))
    file_name = url.split("/")[-1]
    try:
        ot = driver.find_element_by_xpath('//*[@id="basic-info"]/a')
        if ot:
            ot.click()
        tel = driver.find_element_by_xpath('//*[@id="basic-info"]/p')
        ot = driver.find_element_by_xpath('//*[@id="basic-info"]/div[4]/p[1]')
        if tel:
            phone_file = 'E:\\images\\{}.png'.format(file_name+"phone")
            if not os.path.exists(phone_file):
                tel.screenshot(phone_file)
        if ot:
            otfile = 'E:\\images\\{}.png'.format(file_name+"opentime")
            if not os.path.exists(otfile):
                ot.screenshot(otfile)
    except Exception as e:
        print(url)
        print(e)
        return


def recog_image(image_str):
    timep = re.compile(r"(\d+:\d+-).*")
    phonep = re.compile(r"((0\d{2,3}-\d{7,8})|(1[3584]\d{9}))")
    im = Image.open(image_str)
    dd = pytesseract.image_to_string(im, lang="eng")
    dd = dd.split(" ")
    temp = ""
    for index, value in enumerate(dd):
        res = timep.match(value.strip())
        pres = phonep.match(value)
        if pres:
            temp = temp + pres.group(0) + " "
        if res:
            temp = temp + res.group(0) + " "
    return temp
        # if value.strip()[0].isdigit():
        #     temp = index
        #     break
    # print(dd)
    # print(" ".join(dd[temp:]))


def jietu():
    with session_scope() as sess:
        dz = sess.query(DZDianPing).filter(DZDianPing.phone == None).all()
        for item in dz:
            url = item.url
            file_name = url.split("/")[-1]
            phone_file = 'E:\\images\\{}.png'.format(file_name + "phone")
            if not os.path.exists(phone_file):
                sa = cut_imge(item.url)
                time.sleep(2)


def regnize():
    path = 'E:\images'
    url = "http://www.dianping.com/shop/{}"
    for filename in os.listdir(path):
        index = filename.find(".")
        res = fpa.findall(filename)
        hotel_id = res[0]
        cate = filename[len(res[0]): index]
        print(hotel_id)
        fp = os.path.join(path, filename)
        with session_scope() as session:
            dz = session.query(DZDianPing).filter(DZDianPing.url == url.format(hotel_id)).first()
            if dz:
                if cate == "opentime" and not dz.openTime:
                    result = recog_image(fp)
                    dz.openTime = result
                if cate == "phone" and not dz.phone:
                    result = recog_image(fp)
                    dz.phone = result
        time.sleep(2)



# regnize()
jietu()
# recog_image("E:/images/131460957.png")


# cut_imge("http://www.dianping.com/shop/131460957")