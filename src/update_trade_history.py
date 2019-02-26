import time
import requests
import bs4
import datetime
import pymysql
from support import log
from support import databaseConnect
database="stock"

stock_log = log.logInit("fileoutput") #log初始化
def check_stock_date():
    with databaseConnect.mysql_operator(db=database) as cursor:
        cursor.execute("""SELECT distinct `日期` FROM stock.sz000001;""")
        dateTruple = cursor.fetchall()
        dateList=[]
        for date in dateTruple:
            dateList.append(date[0].strftime('%Y-%m-%d'))
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



def get_details(code,date):
    details=[]
    try:
        #获取某一股票某一天页数（页数不固定）
        url = 'http://market.finance.sina.com.cn/transHis.php?symbol={0}&date={1}&page={2}'.format(code, date, 1)
        print(url)
        req = requests.get(url).content.decode('gbk')
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

        #把所有页内容爬出来放入一个列表，整个列表一起返回
        #for page in range(page_num,0,-1):
        #以下注释只跑一页测试数据库写入
        for page in range(1, 0, -1):
            print(page)
            url = 'http://market.finance.sina.com.cn/transHis.php?symbol={0}&date={1}&page={2}'.format(code,date,page)
            req = requests.get(url).content.decode('gbk')
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
            time.sleep(2)
            #print(details)
        return details
    except Exception as e:
        stock_log.error(e)

#date起始日期,返回从起始日期到当前日期的列表
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
        day_list.append(new_dt.strftime('%Y-%m-%d'))
    return day_list


if __name__ == '__main__':
   # details=get_details('sz000002','2004-10-08')
    #print(details)
    db_date_list=check_stock_date()
    days=string_toDatetime('2019-1-1')

    db_date_set = set(db_date_list)
    day_set=set(days)
    #A、B set取差集，得到A中存在B中不存在的值
    day_list=list(day_set - db_date_set)
    print(day_list)
    # code='sz000001'
    # for day in day_list:
    #     details = get_details(code, day)
    #     update_stock_data(code,details)
    #     print(details)
