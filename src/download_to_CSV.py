import time
import requests
import bs4
import datetime
import csv


def get_details(code,date,delay_time):
    details=[]
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

        #获取某一股票某一天页数（页数不固定）
        url = 'http://market.finance.sina.com.cn/transHis.php?symbol={0}&date={1}&page={2}'.format(code, date, 1)
        print(f'获取页数')
        req = requests.get(url,headers=headers).content.decode('gbk')

        bscode = bs4.BeautifulSoup(req, 'html.parser')
        list_info = bscode.select('tbody>tr')
        page_bs4 = bscode.select('script[language="javascript"]')
        a = page_bs4[0].getText().split()
        get_page = [i for i, x in enumerate(a) if x.find('detailPages') != -1]
        index = int(get_page[0])
        page_num = eval(a[index].split('=')[-1].replace(';', ''))[-1][0]
        print(f"页数{page_num}")
        time.sleep(2)
        #把所有页内容爬出来放入一个列表，整个列表一起返回
        #for page in range(page_num,0,-1):
        #以下注释只跑一页测试数据库写入
        for page in range(page_num, 0, -1):

            url = 'http://market.finance.sina.com.cn/transHis.php?symbol={0}&date={1}&page={2}'.format(code,date,page)
            req = requests.get(url,headers=headers).content.decode('gbk')
            #print(req)
            print(f'爬取地址：{url}')
            bscode = bs4.BeautifulSoup(req, 'html.parser')
            list_info = bscode.select('tbody>tr')
            page_bs4=bscode.select('script[language="javascript"]')
            a=page_bs4[0].getText().split()
            get_page=[i for i, x in enumerate(a) if x.find('detailPages') != -1]

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
        print(e)

#date起始日期,返回从起始日期到当前日期的列表当日日期列表需在下午3点以后才可以爬
def string_toDatetime(date):
    day_list=[]
    dt = datetime.datetime.strptime(date,"%Y-%m-%d")
    now = datetime.datetime.now()
    minus_days=(now-dt)

    for i in range(minus_days.days+1):
        new_dt = dt + datetime.timedelta(days=int('+{0}'.format(i)))
        #print(new_dt.strftime('%Y-%m-%d'))
        whatday = new_dt.strftime("%w")
        #判断是否是周末，周末则跳过
        if whatday != '0' and whatday != '6':
            day_list.append(new_dt.strftime('%Y-%m-%d'))

    return day_list
def write_csv(code,date,history_list):
    csv_file = open(f'{code}_{date}.csv', 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(['日期','时间','成交价','价格变动','成交量(手)','成交额(元)','性质'])
    for history in history_list:
        writer.writerow(history)
    csv_file.close()

def downlodad_info(code,startdate,delay_time):
    day_list = string_toDatetime(startdate)
    for day in day_list:
        details = get_details(code, day,delay_time)
        print(details)
        if details==None:
            print(f"{code}暂时无法爬取{day}的数据，原因可能是被反爬或暂无数据")
            continue
        print(f'{code}文件写入')

        write_csv(code, day, details)

if __name__ == '__main__':
    #股票代码
    code = 'sz000001'
    #起始日期，会生成从起始日期到当天的列表，多个日期会按日期放不同文件。3点前爬当天的数据可能会有问题
    startdate = '2019-02-28'
    #爬取间隔，如果被封就把时间调大
    delay_time=3
    downlodad_info(code, startdate,delay_time)

