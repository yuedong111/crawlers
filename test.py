# -*- coding: utf-8 -*-
from utils.make_sessions import create_session
import json
import re
from mtoken import MakeToken
from urllib.parse import quote_plus
from utils.make_sessions import create_meituan_session
from pyppeteer import launch
# coding=utf-8

import asyncio
import pyppeteer
from collections import namedtuple

Response = namedtuple("Response", "url html cookies headers history status")


async def get_html(url, timeout=5):
    # 默认30s
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    res = await page.goto(url, options={'timeout': int(timeout)})
    data = await page.content()
    # print(data)
    # title = await page.title()
    resp_cookies = await page.cookies()
    # print(resp_cookies)
    resp_headers = res.headers
    # print(resp_headers)
    resp_history = None
    resp_status = res.status
    response = Response(url=url,
                        html=data,
                        cookies=resp_cookies,
                        headers=resp_headers,
                        history=resp_history,
                        status=resp_status)
    return response


if __name__ == '__main__':
    url_list = ["http://www.dianping.com/chongqing/ch10/r43"]
    task = (get_html(url) for url in url_list)

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*task))
    for res in results:
        print(res)

