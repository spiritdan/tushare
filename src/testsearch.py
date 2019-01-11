#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=no-member
#上面一行解决vscode 中ts.pro_api()无此成员BUG pylint 的 *E1101* 错误
import pymysql
import time
import datetime

from support import log
from support import databaseConnect

import tushare as ts

stock_log = log.logInit("fileoutput")  # log初始化


def update_stock_data(api, stock_code):
    try:
        start_dt = '20190109'
        time_temp = datetime.datetime.now() - datetime.timedelta(days=1)
        end_dt = time_temp.strftime('%Y%m%d')
        df = ts.pro_bar(pro_api=api, ts_code=stock_code, adj='qfq', start_date=start_dt, end_date=end_dt,freq='60min')  # 获取数据
        stock_data = df.where(df.notnull(), None)  # 将Nan转换为None

        # df = ts.pro_bar(pro_api=api, ts_code=stock_code, adj='qfq')  # 获取数据
        # stock_data = df.where(df.notnull(), None)  # 将Nan转换为None

        data_list = []

        for row in stock_data.itertuples(index=False, name=None):  # 将dataframe转换为list
            data_list.append(row)
            print(row)


    except pymysql.Error as e:
        stock_log.error(e)
    except:
        stock_log.error('other error')
    else:
        stock_log.info('finish update stock data')


if __name__ == '__main__':
        #旧c34877586f962f39f0c69de2a027c30fba8eb05bda5a1f9ae525449b
#新c8c44b9ef173fa35b3a09aadb7cf4c2f0513c232f8a4c6ca608b81f1
    pro = ts.pro_api('06645505054699358268a42f4a21f23eb95c0ce218bd2c2980242e19')
    update_stock_data(pro, '000001.SZ')
