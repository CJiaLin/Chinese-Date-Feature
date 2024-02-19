import datetime
import pandas as pd
import chinese_calendar as calendar

start_time = datetime.date(year=2021, month=1, day=1)
end_time = datetime.date(year=2025, month=1, day=1)
datetime_list = [start_time + datetime.timedelta(days=i) for i in range((end_time - start_time).days)]

on_holidays = [] # 是否节假日
holiday_names = [] # 法定假日名称
date_type = [] # 日期类别：0-工作日，1-周末，2-短假日，3-长假日
tiao_xius = [] # 是否调休工作日
long_count = 0 
long_nth = [] # 法定假日第几天
long_holidays = []

for i in range(len(datetime_list)):
    date = datetime_list[i]
    on_holiday, holiday_name = calendar.get_holiday_detail(date)
    on_holidays.append(on_holiday)
    holiday_names.append(holiday_name)

    # 日期类别
    if on_holiday is True and holiday_name in ['Spring Festival', 'Labour Day', 'National Day']:  # 春节、五一、国庆为长假日
        date_type.append(3)
    elif on_holiday is True and holiday_name is not None:  # 短假日
        date_type.append(2)
    elif on_holiday:  # 周末
        date_type.append(1) 
    else: # 工作日
        date_type.append(0)

    # 除周末外的法定假日，第几天节假日
    if on_holiday is True and holiday_name is not None:  
        long_count += 1
        long_nth.append(long_count)
        long_holidays.append(1)
    elif long_count != 0:
        long_count = 0
        long_nth.append(0)
        long_holidays.append(0)
    else:
        long_nth.append(0)
        long_holidays.append(0)
    
    # 调休上班日
    if on_holiday is False and holiday_name is not None:  
        tiao_xius.append(True)
    else:
        tiao_xius.append(False)

    # # 节假日前7天标记
    # if on_holiday is False:
        
data = pd.DataFrame({'datetime': pd.to_datetime(datetime_list), 
                     'on_holiday': on_holidays, 
                     'holiday_name': holiday_names,
                     'date_type':  date_type,
                     'tiao_xiu': tiao_xius,
                     'long_nth': long_nth,
                     'long_holiday': long_holidays})

holiday_before = []
for i in range(len(long_holidays) - 7):
    if long_holidays[i] == 1:
        holiday_before.append(0)
        continue
    
    count = 0
    if 1 not in long_holidays[i + 1: i + 8]:
        holiday_before.append(0)
        continue

    for j in range(1, 8):
        if long_holidays[i + j] == 1:
            holiday_before.append(count + 1)
            break
        else:
            count += 1
    if count == 7:
        holiday_before.append(0)

holiday_before.extend([7, 6, 5, 4, 3, 2, 1])

holiday_after = []
after_count = 0
holi_flg = False
for i in range(len(long_holidays)):
    if long_holidays[i] == 1:
        after_count = 0
        holiday_after.append(0)
        holi_flg = True
        continue

    if holi_flg == True:
        after_count += 1
    
    if after_count > 7:
        holiday_after.append(0)
    else:
        holiday_after.append(after_count)

data['holiday_before'] = holiday_before
data['holiday_after'] = holiday_after

solar_data = pd.DataFrame(calendar.get_solar_terms(datetime_list[0], datetime_list[-1]), columns=['datetime', 'solar_terms'])
solar_data.datetime = pd.to_datetime(solar_data.datetime)

data_merge = data.merge(solar_data, on='datetime', how='left').fillna(False)

data_merge.to_csv('chinese_calendar.csv', index=None)