import time
import requests
import bs4
import datetime
import pymysql
from support import log
from support import databaseConnect



def update_stock_data(data_list):
    try:
         with databaseConnect.mysql_operator(db='stock') as cursor:
           cursor.executemany("""insert into stock.sz000002 values (%s,%s,%s,%s,%s,%s,%s)""", data_list)

    except pymysql.Error as e:
        print(e)
    except:
        print('other error')
    else:
        print('finish update stock data')



def get_details(code,date,page):
    details=[]
    for page in range(page,0,-1):

        url = 'http://market.finance.sina.com.cn/transHis.php?symbol={0}&date={1}&page={2}'.format(code,date,page)
        req = requests.get(url).content.decode('gbk')
        bscode = bs4.BeautifulSoup(req, 'html.parser')
        list_info = bscode.select('tbody>tr')
        #print(date)
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
        time.sleep(5)
        #print(details)
    return details

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
    #details=get_details('sz000002','2018-12-14',70)
    #print(details)

    day_list=string_toDatetime('1991-01-01')
    for day in day_list:
        details = get_details('sz000002', day, 70)
        update_stock_data(details)
        print(details)
