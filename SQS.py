#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from urllib import urlopen
import json
from fengshidian import *
from datetime import datetime
import numpy as np
import pandas as pd
import re
from datetime import timedelta


rootdir='C:/Users/fsd/OneDrive/Python/founder_future/ZSQSData/'
temprootdir='C:/Users/fsd/OneDrive/Python/founder_future/ZSQSData/cu_f/'
list_temp=os.listdir(rootdir)
try:
    listdownload=os.listdir(temprootdir)
except:
    pass
if len(list_temp)==0:
    start='2015-01-01'
else:
    latestUpdateTime=listdownload[-1][:8]
    start=latestUpdateTime[:4]+'-'+latestUpdateTime[4:6]+'-'+latestUpdateTime[6:8]
#下午16点之前只更新到前一天的数据，16点以后才更新今日数据。
if datetime.now().hour>=16:
    end=datetime.now().strftime('%Y-%m-%d')
else:
    end=(datetime.now()-timedelta(1)).strftime('%Y-%m-%d')

datestart=datetime.strptime(start,'%Y-%m-%d')
dateend=datetime.strptime(end,'%Y-%m-%d')

#dateend='2017-04-30'
#dateend=datetime.strptime(dateend,'%Y-%m-%d')
dayIndex=[]
while datestart!=dateend:
    datestart=datestart+timedelta(1)
    dayIndex.append(datestart.strftime('%Y-%m-%d'))

for number,daytime in enumerate(dayIndex):
    date=daytime[:4]+daytime[5:7]+daytime[8:10]
    print date
    html=urlopen('http://www.shfe.com.cn/data/dailydata/kx/kx'+date+'.dat')
    ED_html=urlopen('http://www.shfe.com.cn/data/instrument/ContractBaseInfo'+date+'.dat')
    html=html.read().decode("utf8").encode("utf8")
    ED_html=ED_html.read().decode("utf8").encode("utf8")
    try:
        my_html = json.loads(html)
        my_ED_html=json.loads(ED_html)
    except:
        continue

        #print u'网页解析'
    rows=len(my_html['o_curinstrument'])
        #print rows
    frame=pd.DataFrame()
    for i in range(rows):
        temp=pd.DataFrame.from_dict(my_html['o_curinstrument'][i], orient='index').T.iloc[:,1:]
        frame=pd.concat([frame,temp])
        #print frame

    rows=len(my_ED_html['ContractBaseInfo'])
    frame_E=pd.DataFrame()
    for i in range(rows):
        temp_E=pd.DataFrame.from_dict(my_ED_html['ContractBaseInfo'][i],orient='index').T
        frame_E=pd.concat([frame_E,temp_E])

    columns_name=['PRODUCTID','PRODUCTNAME','DELIVERYMONTH','PRESETTLEMENTPRICE','OPENPRICE','HIGHESTPRICE','LOWESTPRICE','CLOSEPRICE','SETTLEMENTPRICE','ZD1_CHG','ZD2_CHG','VOLUME','OPENINTEREST','OPENINTERESTCHG']
    columns_cname=['PRODUCTID',u'品种名称',u'交割月份',u'前结算价',u'开盘价',u'最高价',u'最低价',u'收盘价',u'结算参考价',u'涨跌1',u'涨跌2',u'成交量',u'持仓量',u'持仓变化量']

    frame=pd.DataFrame(frame,columns=columns_name)
    frame_E=IndexChange(frame_E[['INSTRUMENTID','EXPIREDATE']],'INSTRUMENTID',2,6)
        #print frame_E
    resframe_temp=pd.DataFrame(np.matrix(frame),index=range(len(frame)),columns=columns_cname)
    resframe_temp=resframe_temp[:-1]
    resframe_temp=IndexChange(resframe_temp,u'交割月份')
    resframe_temp=resframe_temp.drop(u'小计')
    try:
        resframe=pd.concat([resframe_temp,frame_E],axis=1)
    except:
        res_row=len(frame_E)
        print res_row
        resframe_temp=resframe_temp[:res_row]
        resframe=pd.concat([resframe_temp,frame_E],axis=1)
        print u'期转现'
        #print resframe
        #print resframe
    for productename,temp_frame in resframe.groupby(u'PRODUCTID'):
        print productename
        productename=productename.replace(" ","")
        res=temp_frame.iloc[:,2:]
            
            #print rootdir+productename,date
        if os.path.exists(rootdir+productename):#存在路径
                #print 1
            writer=pd.ExcelWriter(rootdir+productename+'/'+date+'_'+temp_frame.iloc[0,0].replace(" ","")+ '_Daily.xlsx')
            res.to_excel(writer,temp_frame.iloc[0,1].replace(" ","")+u'日行情数据')
            writer.save()
        else:
            os.mkdir(rootdir+temp_frame.iloc[0,0].replace(" ",""))
            writer=pd.ExcelWriter(rootdir+productename+'/'+date+'_'+temp_frame.iloc[0,0].replace(" ","")+ '_Daily.xlsx')
            res.to_excel(writer,temp_frame.iloc[0,1].replace(" ","")+u'日行情数据')
            writer.save()
