import pytesseract
from PIL import Image
from utils.make_sessions import create_webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = create_webdriver()


def cut_imge(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="basic-info"]')))
    # yanzheng = driver.find_element_by_class_name("")
    file_name = url.split("/")[-1]
    if "https://verify.meituan.com/v2/" in driver.current_url:
        time.sleep(2)
        print("输入验证码")
    driver.find_element_by_xpath('//*[@id="basic-info"]/a').click()
    tel = driver.find_element_by_xpath('//*[@id="basic-info"]/p')
    ot = driver.find_element_by_xpath('//*[@id="basic-info"]/div[4]/p[1]')
    tel.screenshot('E:\\images\\{}.png'.format(file_name+"phone"))
    ot.screenshot('E:\\images\\{}.png'.format(file_name+"opentime"))


def recog_image(image_str):
    im = Image.open(image_str)
    dd = pytesseract.image_to_string(im,lang="eng")
    print(dd)
    dd = dd.split(" ")
    temp = 0
    for index, value in enumerate(dd):
        if value.strip()[0].isdigit():
            temp = index
            break
    print(dd)
    print(" ".join(dd[index:]))


# recog_image("E:/images/131460957.png")

cut_imge("http://www.dianping.com/shop/131460957")