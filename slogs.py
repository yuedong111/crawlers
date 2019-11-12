# -*- coding: utf-8 -*-
from __future__ import print_function
from subprocess import Popen, PIPE
import os
import re
import time
rese = re.compile("\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2},\d+")

class slog:

    def __init__(self):
        self.path = ["/zctt/iaap/service/log", "/zctt/iaap/service"]

    def search(self, content):
        p = Popen("""grep "{}" *.*""".format(content), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        temp = stdout.split("\n")
        for line in temp:
            yield line

    def d_search(self, content, *args):
        res = []
        for path in self.path:
            os.chdir(path)
            for line in self.search(content):
                if args:
                    for content2 in args:
                        if content2 not in line:
                            break
                    else:
                        res.append(self.deal_time(line))
                else:
                    res.append(self.deal_time(line))
        res.sort(key=lambda item: list(item.values())[0])
        for item in res:
            print(item)

    def deal_time(self, item):
        res1 = rese.search(item)
        if res1:
            time1 = res1.group(0)
            time2 = time1[time1.find(",") + 1:]
            d = time.strptime(time1, "%Y-%m-%d %H:%M:%S,%f")
            dint = int(time.mktime(d))
            timeint = float("{}.{}".format(dint, time2))
            temp = {item: timeint}
        else:
            temp = {item: 10000.00}
        return temp


if __name__ == "__main__":
    slog().d_search("999d9612-be09-4481-bbd1-9c5d7ce377f7", "2019-10-09 15:08:39,725")
