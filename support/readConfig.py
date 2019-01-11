import subprocess
import time
import sched
import datetime
import random
import configparser
import os

config = configparser.ConfigParser(allow_no_value=False)
config.read("config.cfg", encoding='utf-8')
class conf():

    # 初始化，设置adb目录
    def __init__(self):
        self.db = config.get("mysql","database")


if __name__ == '__main__':
    conf=conf()
    print(conf.db)