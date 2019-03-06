import time
import requests
import bs4
import datetime
import pymysql
from support import log
from support import databaseConnect
import re


database="stock"

stock_log = log.logInit("fileoutput") #log初始化
#查询表中已存在的所有日期，返回list
#用于检查数据完整性
def check_stock_date(code,date='1990-01-01'):
    sql = f"""SELECT distinct `日期` FROM {code};"""
    with databaseConnect.mysql_operator(db=database) as cursor:
        starttime = datetime.datetime.now()
        print('正在查询历史数据，请耐心等待')
        cursor.execute(sql)

        dateTruple = cursor.fetchall()
        dateList=[]
        for date in dateTruple:
            dateList.append(date[0].strftime('%Y-%m-%d'))
        endtime = datetime.datetime.now()
        print(f'查询历史数据完成用时：{endtime - starttime}')
        #print(dateList)
        return dateList

#更新数据库
def update_stock_data(code,data_list):

    sql=f'insert into {code} values (%s,%s,%s,%s,%s,%s,%s)'
    try:
         with databaseConnect.mysql_operator(db=database) as cursor:
           cursor.executemany(sql, data_list)

    except pymysql.Error as e:
        print(e)
    except:
        print('other error')
    else:
        print('finish update stock data')



def get_details(code,date,delay_time):
    details=[]
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

        #获取某一股票某一天页数（页数不固定）
        url = 'http://market.finance.sina.com.cn/transHis.php?symbol={0}&date={1}&page={2}'.format(code, date, 1)
        print(url)
        req = requests.get(url,headers=headers).content.decode('gbk')
        #print(req)
        bscode = bs4.BeautifulSoup(req, 'html.parser')
        list_info = bscode.select('tbody>tr')
        page_bs4 = bscode.select('script[language="javascript"]')
        a = page_bs4[0].getText().split()
        get_page = [i for i, x in enumerate(a) if x.find('detailPages') != -1]
        index = int(get_page[0])
        page_num = eval(a[index].split('=')[-1].replace(';', ''))[-1][0]
        print(date)
        print(page_num)
        time.sleep(2)
        #把所有页内容爬出来放入一个列表，整个列表一起返回
        #for page in range(page_num,0,-1):
        #以下注释只跑一页测试数据库写入
        for page in range(page_num, 0, -1):
            print(page)
            url = 'http://market.finance.sina.com.cn/transHis.php?symbol={0}&date={1}&page={2}'.format(code,date,page)
            req = requests.get(url,headers=headers).content.decode('gbk')
            #print(req)
            bscode = bs4.BeautifulSoup(req, 'html.parser')
            list_info = bscode.select('tbody>tr')
            page_bs4=bscode.select('script[language="javascript"]')
            a=page_bs4[0].getText().split()
            get_page=[i for i, x in enumerate(a) if x.find('detailPages') != -1]
            index=int(get_page[0])
            page_num=eval(a[index].split('=')[-1].replace(';',''))[-1][0]
            print(date)
            #print(list_info)
            #如果列表为空跳出
            if not list_info:
                break
            for info in list_info:
                temp = []
                temp.append(date)
                temp.append(info.select('th')[0].getText())
                data=info.select('td')
                for i in range(len(data)):
                    temp.append(data[i].getText())
                temp.append(info.select('th')[1].getText())
                details.append(temp)
                print(temp)
            time.sleep(delay_time)
            #print(details)
        return details
    except Exception as e:
        stock_log.error(e)

#date起始日期,返回从起始日期到当前日期的列表当日日期列表需在下午3点以后才可以爬
def string_toDatetime(date):
    day_list=[]
    dt = datetime.datetime.strptime(date,"%Y-%m-%d")
    now = datetime.datetime.now()
    print(now)
    print(dt)

    minus_days=(now-dt)
    print(minus_days)

    for i in range(minus_days.days+1):
        new_dt = dt + datetime.timedelta(days=int('+{0}'.format(i)))
        #print(new_dt.strftime('%Y-%m-%d'))
        whatday = new_dt.strftime("%w")
        #判断是否是周末，周末则跳过
        if whatday != '0' and whatday != '6':
            day_list.append(new_dt.strftime('%Y-%m-%d'))

    return day_list

#判断某表是否存在，不存在则调用create_table创建
def table_exists(cursor,table_name):
    sql = "show tables;"
    cursor.execute(sql)
    tables = [cursor.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    if table_name in table_list:
        print(f"{table_name}已存在，继续执行")
    else:
        try:
            create_table(cursor, table_name)
            print(f"新建{table_name}成功")
        except Exception as e:
            print(e)

def create_table(cursor,table_name):
    sql_create = f"""CREATE TABLE `{table_name}` (
                      `日期` date DEFAULT NULL,
                      `时间` varchar(10) NOT NULL,
                      `成交价` varchar(10) NOT NULL,
                      `价格变动` varchar(45) NOT NULL,
                      `成交量(手)` varchar(45) DEFAULT NULL,
                      `成交额(元)` varchar(45) DEFAULT NULL,
                      `性质` varchar(45) DEFAULT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

    cursor.execute(sql_create)

def downlodad_info(code,startdate,delay_time):
    #################判断数据库是否存在，不存在则创建###################
    with databaseConnect.mysql_operator(db=database) as con:
        table_exists(con, code)
    #################从起始时间到查询数据库内存在的日期，起始日期可以不设###################
    db_date_list=check_stock_date(code,startdate)
    #################从起始时间到运行当天的日期列表（周六周日除外）###################
    all_days=string_toDatetime(startdate)
    db_date_set = set(db_date_list)
    allday_set=set(all_days)
    #A、B set取差集，得到A中存在B中不存在的值
    day_list=list(allday_set - db_date_set)
    print(f'日期列表：{day_list}')
    for day in day_list:
        details = get_details(code, day,delay_time)
        update_stock_data(code,details)
        print(details)

if __name__ == '__main__':
    code = 'sz000001'
    startdate = '2019-02-27'
    delay_time=2
    downlodad_info(code, startdate,delay_time)

