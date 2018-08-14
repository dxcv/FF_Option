#!/usr/bin/python
# -*- coding: UTF-8 -*-
from WindPy import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fengshidian import *
import requests
from bs4 import BeautifulSoup
import os
from datetime import timedelta, datetime
from time import sleep

class DataDownLoadProcess:
	def __init__(self):
		self.WINDStart()
		if self.errorid==0:
			self.MOptionDownLoad()
			self.SROptionDownLoad()
			self.SRFutureDownLoad()
			self.MFutureDownload()
			self.MFutureDataProcess()
			self.MOptionDataProcess()
			self.SRFutureDataProcess()
			self.SROptionDataProcess()
			self.ETFDownLoad()
		else:
			print 'Wind warning!'
	def WINDStart(self):
		self.errorid=w.start()
		if self.errorid==0:
			pass
		else:
			print self.errorid
	def strsub(self,num):
		num=int(num)-1
		return str(num)
	def MOptionDownLoad(self):
		rootdirdownload='C:/Users/fsd/OneDrive/Python/founder_future/MOption/'
		listdownload=os.listdir(rootdirdownload)
		if len(listdownload)==0:
			start='2017-03-30'
		else:
			latestUpdateTime=listdownload[-1][:8]
			start=latestUpdateTime[:4]+'-'+latestUpdateTime[4:6]+'-'+latestUpdateTime[6:8]

		end=datetime.now().strftime('%Y-%m-%d')
		datestart=datetime.strptime(start,'%Y-%m-%d')
		dateend=datetime.strptime(end,'%Y-%m-%d')
		dayIndex=[]
		while datestart!=dateend:
			datestart=datestart+timedelta(1)
			dayIndex.append(datestart.strftime('%Y-%m-%d'))

		M_url='http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html'
		MCheck_url='http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
		for number,daytime in enumerate(dayIndex):
			year=daytime[:4]
			month=self.strsub(daytime[5:7])
			day=daytime[8:10]
			tempdate=daytime[:4]+daytime[5:7]+daytime[8:10]
			data={
				'dayQuotes.variety': 'all',
				'dayQuotes.trade_type': '1',
				'year': year,
				'month': month,
				'day': day,
				'exportFlag': 'excel',
				}
			MCheck_url='http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
			tp=requests.post(MCheck_url,data=data)
			html_soup=BeautifulSoup(tp.content,'lxml')
			ftp=html_soup.find_all('div',class_='tradeResult02')
			if ftp[0].text[-5:-1]==u'暂无数据':
				pass
			else:
				tq=requests.post(M_url,data=data)
				with open(rootdirdownload+tempdate+"_Daily.xls",'wb') as f:
					f.write(tq.content)
	def MFutureDownLoad(self):
		rootdirdownload='C:/Users/fsd/OneDrive/Python/founder_future/MFuture/'
		listdownload=os.listdir(rootdirdownload)
		if len(listdownload)==0:
			start='2017-03-30'
		else:
			latestUpdateTime=listdownload[-1][:8]
			start=latestUpdateTime[:4]+'-'+latestUpdateTime[4:6]+'-'+latestUpdateTime[6:8]

		end=datetime.now().strftime('%Y-%m-%d')
		datestart=datetime.strptime(start,'%Y-%m-%d')
		dateend=datetime.strptime(end,'%Y-%m-%d')
		#dateend='2017-04-30'
		#dateend=datetime.strptime(dateend,'%Y-%m-%d')
		dayIndex=[]
		while datestart!=dateend:
			datestart=datestart+timedelta(1)
			dayIndex.append(datestart.strftime('%Y-%m-%d'))
		#dayIndex=dayIndex 

		M_url='http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html'
		MCheck_url='http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
		strr=''
		while strr=='':
			for number,daytime in enumerate(dayIndex):
				year=daytime[:4]
				month=self.strsub(daytime[5:7])
				day=daytime[8:10]
				tempdate=daytime[:4]+daytime[5:7]+daytime[8:10]
				data={
						'dayQuotes.variety': 'm',
						'dayQuotes.trade_type': '0',
						'year': year,
						'month': month,
						'day': day,
						'exportFlag': 'excel',
						}
				MCheck_url='http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
					#headers = {'Connection': 'close',}
					#tp=requests.post(MCheck_url,data=data,headers=headers)
				tp=requests.post(MCheck_url,data=data)
				html_soup=BeautifulSoup(tp.content,'lxml')
				ftp=html_soup.find_all('div',class_='tradeResult02')
					#print ftp
				if ftp[0].text[-5:-1]==u'暂无数据':
					pass
				else:
					tq=requests.post(M_url,data=data)
					with open(rootdirdownload+tempdate+"_Future_Daily.xls",'wb') as f:
						f.write(tq.content)
	def SROptionDownLoad(self):
		rootdirdownload='C:/Users/fsd/OneDrive/Python/founder_future/SOption/'
		listdownload=os.listdir(rootdirdownload)
		if len(listdownload)==0:
			start='2017-04-18'
		else:
			latestUpdateTime=listdownload[-1][:8]
			start=latestUpdateTime[:4]+'-'+latestUpdateTime[4:6]+'-'+latestUpdateTime[6:8]
			
		end=datetime.now().strftime('%Y-%m-%d')
		datestart=datetime.strptime(start,'%Y-%m-%d')
		dateend=datetime.strptime(end,'%Y-%m-%d')
		dayIndex=[]
		while datestart!=dateend:
			datestart=datestart+timedelta(1)
			dayIndex.append(datestart.strftime('%Y-%m-%d'))
		dayIndex=dayIndex   
		for number,daytime in enumerate(dayIndex):
			year=daytime[:4]
			month=self.strsub(daytime[5:7])
			day=daytime[8:10]
			tempdate=daytime[:4]+daytime[5:7]+daytime[8:10]
			SR_url_check='http://www.czce.com.cn/portal/DFSStaticFiles/Option/'+year+'/'+tempdate+'/OptionDataDaily.htm'
			SR_url='http://www.czce.com.cn/portal/DFSStaticFiles/Option/'+year+'/'+tempdate+'/OptionDataDaily.xls'
			tp=requests.get(SR_url_check)
			html_soup=BeautifulSoup(tp.content,'lxml')
			ftp=html_soup.find_all('title')
			if ftp[0].text==u'错误页面':
				pass
			else:
				tq=requests.get(SR_url)
				with open(rootdirdownload+tempdate+"_OptionDataDaily.xls",'wb') as f:
					f.write(tq.content)
	def SRFutureDownLoad(self):
		rootdirdownload='C:/Users/fsd/OneDrive/Python/founder_future/SRFuture/'
		listdownload=os.listdir(rootdirdownload)
		if len(listdownload)==0:
			start='2017-04-18'
		else:
			latestUpdateTime=listdownload[-1][:8]
			start=latestUpdateTime[:4]+'-'+latestUpdateTime[4:6]+'-'+latestUpdateTime[6:8]
			
		end=datetime.now().strftime('%Y-%m-%d')
		datestart=datetime.strptime(start,'%Y-%m-%d')
		dateend=datetime.strptime(end,'%Y-%m-%d')
		dayIndex=[]
		while datestart!=dateend:
			datestart=datestart+timedelta(1)
			dayIndex.append(datestart.strftime('%Y-%m-%d'))
		dayIndex=dayIndex   
		for number,daytime in enumerate(dayIndex):
			year=daytime[:4]
			month=self.strsub(daytime[5:7])
			day=daytime[8:10]
			tempdate=daytime[:4]+daytime[5:7]+daytime[8:10]
			SR_url_check='http://www.czce.com.cn/portal/DFSStaticFiles/Future/'+year+'/'+tempdate+'/FutureDataDailySR.htm'
			SR_url='http://www.czce.com.cn/portal/DFSStaticFiles/Future/'+year+'/'+tempdate+'/FutureDataDailySR.xls'
			tp=requests.get(SR_url_check)
			html_soup=BeautifulSoup(tp.content,'lxml')
			ftp=html_soup.find_all('title')
			if ftp[0].text==u'错误页面':
				pass
			else:
				tq=requests.get(SR_url)
				with open(rootdirdownload+tempdate+"_FutureDataDaily.xls",'wb') as f:
					f.write(tq.content)
	def MFutureDataProcess(self):
		rootdir='C:/Users/fsd/OneDrive/Python/founder_future/MFuture/'
		rootdir2='C:/Users/fsd/OneDrive/Python/founder_future/MFuture_Data_Processed/'
		Mlist=os.listdir(rootdir)
		for i in Mlist:
			date=i[:8]
			temp=pd.read_excel(rootdir+i)
			temp=IndexChange(temp,u'商品名称')
			temp=temp.loc[:u'豆粕小计'].iloc[:-1]
			tempindex=[]
			for i in temp.iloc[:,0]:
				tempindex.append('m'+str(int(i)))
			data=pd.DataFrame(np.matrix(temp.iloc[:,1:]),index=tempindex,columns=temp.columns[1:])
			
			for num in data.columns:
				data[num]=data[num].str.replace(',','')
			data=pd.DataFrame(data,dtype=float)
			writer = pd.ExcelWriter(rootdir2+date+'_M_Future.xls')
			data.to_excel(writer,u'豆粕期货日行情数据')
			writer.save()
	def MOptionDataProcess(self):
		rootdir = 'C:/Users/fsd/OneDrive/Python/founder_future/MOption'
		rootdir2='C:/Users/fsd/OneDrive/Python/founder_future/MOption_Data_Processed/'
		list1 = os.listdir(rootdir) #列出文件夹下所有的目录与文件
		list2=os.listdir(rootdir2)
		templists=list1[-(len(list1)-len(list2)):]
		if len(list1)==len(list2):
			print 'update completed'
			pass
		else:
			for templist in templists:
				tempdate=templist[:8]
				date=tempdate[:4]+'-'+tempdate[4:6]+'-'+tempdate[6:8]
				
					
				data=pd.read_excel(rootdir+templist)	  
				for col in data.columns:
					if data[col].dtype==float:
						pass
					else:
						data[col]=data[col].str.replace(',','')
				temp_index=data[u'商品名称']
				data_tmp1=pd.DataFrame(np.matrix(data.iloc[:,1:]),index=temp_index,columns=data.columns[1:]).loc[:u'豆粕小计'].iloc[:-1]
				temp_index=data_tmp1[u'合约名称']
				data_tmp2=pd.DataFrame(np.matrix(data_tmp1.iloc[:,1:]),index=temp_index,columns=data_tmp1.columns[1:])
				data_tmp2=pd.DataFrame(np.matrix(data_tmp2),index=data_tmp2.index,columns=data_tmp2.columns,dtype=float)
				del data_tmp2.index.name
					
				strr=''
				for i in data_tmp2.index:
					i=i+'.DCE'
					strr=strr+i+','
				strr=strr[:-1]
				dataptm=w.wsd(strr, "ptmtradeday", date, date, "")
				print dataptm
				
				dataptmtemp=pd.DataFrame(dataptm.Data,columns=dataptm.Codes,index=dataptm.Fields).T
			   
				dataptmtemp=pd.DataFrame(np.matrix(dataptmtemp),index=data_tmp2.index,columns=['ptmtradeday'])
				data_tmp2=pd.concat([data_tmp2,dataptmtemp],axis=1)
				writer = pd.ExcelWriter(rootdir2+tempdate+'_Daily_Processed.xls')
				data_tmp2.to_excel(writer,u'豆粕日行情数据')
				writer.save()
	def SRFutureDataProcess(self):
		rootdir = 'C:/Users/fsd/OneDrive/Python/founder_future/SRFuture/'
		rootdir2='C:/Users/fsd/OneDrive/Python/founder_future/SRFuture_Data_Processed/'
		list1 = os.listdir(rootdir) #列出文件夹下所有的目录与文件
		list2=os.listdir(rootdir2)
		listTemp=list1[-len(list1)+len(list2):]
		if len(list1)==len(list2):
			print 'update completed'
			pass
		else:
			for i in range(0,len(list1)-len(list2)):
				date=listTemp[i][:8]
				temp=pd.read_excel(rootdir+listTemp[i])
				cols=temp.loc[0].values[1:]
				indexs=temp.iloc[:,0][1:]
				data=pd.DataFrame(np.matrix(temp.iloc[1:,1:]),index=indexs,columns=cols)
				del data.index.name
				data=data.drop(u'小计')
				data=data.drop(u'总计')
				for num in data.columns:
					data[num]=data[num].str.replace(',','')
				data=pd.DataFrame(data,dtype=float)
				writer=pd.ExcelWriter(rootdir2+date+'_SR_Future.xls')
				data.to_excel(writer,u'白糖期货日行情数据')
				writer.save()
	def SROptionDataProcess(self):
		rootdir = 'C:/Users/fsd/OneDrive/Python/founder_future/SOption/'
		rootdir2='C:/Users/fsd/OneDrive/Python/founder_future/SOption_Data_Processed/'
		list1 = os.listdir(rootdir) #列出文件夹下所有的目录与文件
		list2=os.listdir(rootdir2)
		templists=list1[-(len(list1)-len(list2)):]
		if len(list1)==len(list2):
			print 'update completed'
			pass
		else:
			for templist in templists:
				date=templist[:8]
				#date=date[:4]+'-'+date[4:6]+'-'+date[6:8]
				temp=pd.read_excel(rootdir+templist)
				cols=temp.iloc[0].values
				tempdate=temp.columns[0][-11:-1]
				temp_index=temp.iloc[:,0][1:]
				data=pd.DataFrame(np.matrix(temp.iloc[1:,1:]),index=temp_index,columns=cols[1:])
				del data.index.name
				data=data.drop(u'小计')
				data=data.drop(u'SR合计')
				data=data.drop(u'总计')
				for i in data.columns:
					data[i]=data[i].str.replace(',','')
				data=pd.DataFrame(data,index=data.index,columns=data.columns,dtype=float)
						#writer = pd.ExcelWriter('C:/Users/fsd/OneDrive/Python/founder_future/SOption_Data_Processed/'+date+'_SR_Processed.xlsx')
						#data.to_excel(writer,u'白糖日行情数据')
						#writer.save()	 
				data_tmp2=data
				strr=''
				for i in data_tmp2.index:
					i=i+'.CZC'
					strr=strr+i+','
				strr=strr[:-1]
				dataptm=w.wsd(strr, "ptmtradeday", date, date, "")
				dataptmtemp=pd.DataFrame(dataptm.Data,columns=dataptm.Codes,index=dataptm.Fields).T
				dataptmtemp=pd.DataFrame(np.matrix(dataptmtemp),index=data_tmp2.index,columns=['ptmtradeday'])
				data_tmp2=pd.concat([data_tmp2,dataptmtemp],axis=1)
				writer = pd.ExcelWriter(rootdir2+date+'_SR_Processed.xls')
				data_tmp2.to_excel(writer,u'白糖日行情数据')
				writer.save()
	def ETFDownLoad(self):
		rootdir='C:/Users/fsd/OneDrive/Python/founder_future/ETFOption/'
		listdir=os.listdir(rootdir)
		date=listdir[-1][:10]
		DateIndex=w.wsd("510050.SH", "close", date,"" , "")
		TimeIndex=pd.DataFrame(DateIndex.Data,columns=DateIndex.Times,index=['close']).T.index
		TimeIndex=TimeIndex[1:]
		try:
			for date in TimeIndex:
				date=str(date)
				data=w.wset("optiondailyquotationstastics","startdate="+date+";enddate="+date+";exchange=sse;windcode=510050.SH")
				tempdataframe=pd.DataFrame(data.Data[2:],columns=data.Data[1],index=data.Fields[2:]).T
				strr=''
				for i in tempdataframe.index:
					i=i+".SH"
					strr=strr+i+','
				strr=strr[:-1]
				dataptm=w.wsd(strr, "ptmtradeday", date, date, "")
				tempptmframe=pd.DataFrame(dataptm.Data[0],index=tempdataframe.index,columns=['ptmtradeday'])
				result=pd.concat([tempdataframe,tempptmframe],axis=1)
				writer=pd.ExcelWriter(rootdir+date+'_Daily_Processed.xls')
				result.to_excel(writer,u'50ETF日行情数据')
				writer.save()
		except:
			print '50ETF data updated!'

DataDownLoadProcess()