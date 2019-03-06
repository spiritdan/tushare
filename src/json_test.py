# key为日期如20190227，
# work_status为状态：工作日为 0, 休息日对应结果为 1, 节假日对应的结果为 2；
# wday为星期
import time
import datetime
import json
with open("./calendar.json",'r') as load_f:
    load_dict = json.load(load_f)
    date='20191003'
    work_status=load_dict[date]['work_status']
    wday=load_dict[date]['wday']
    print(f'{date}：{wday}\n工作状态为：{work_status}')
#星期天为0 0~6
dayTime=('2019-03-03')
whatday= datetime.datetime.strptime(dayTime,'%Y-%m-%d').strftime("%w")
print(type(whatday))

if whatday !='0' and  whatday !='6':
    print(whatday)
