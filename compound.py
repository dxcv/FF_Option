#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
from WindPy import *
import os 
import re
from fengshidian import *
class Compound:
	def __init__(self):
		self.WINDStart()
		if self.errorid==0:
			self.ETFRootdir='C:/Users/fsd/OneDrive/Python/founder_future/ETFOption/'
			self.MRootdir='C:/Users/fsd/OneDrive/Python/founder_future/MOption_Data_Processed/'
			self.SRRootdir='C:/Users/fsd/OneDrive/Python/founder_future/SOption_Data_Processed/'
			
			self.ETFMinuteRootdir='C:/Users/fsd/OneDrive/Python/founder_future/AtTheMoneyOption_minute/ETFOption/'
			self.MMinuteRootdir='C:/Users/fsd/OneDrive/Python/founder_future/AtTheMoneyOption_minute/MOption/'
			self.SRMinuteRootdir='C:/Users/fsd/OneDrive/Python/founder_future/AtTheMoneyOption_minute/SROption/'
			
			self.R=pd.read_excel('C:/Users/fsd/OneDrive/Python/founder_future/shibor.xlsx')[1:]
			DateTime=[]
			for i in self.R.loc[:,u'日期']:
				DateTime.append(str(i)[:10])
			self.Rframe=pd.DataFrame(np.matrix(self.R.loc[:,u'收盘价']),columns=DateTime,index=['close']).T/100
			self.DataProcess()
		else:
			print 'Wind warning!'
	def WINDStart(self):
		self.errorid=w.start()
		self.errorid=self.errorid.ErrorCode
		if self.errorid==0:
			pass
		else:
			print self.errorid
	def OptionSort(self,frame,date,ptmtradeday,r,monthtype):
		tempdata=IndexCopy(frame)
		temp=IndexChange(tempdata,'option_name')
		#筛选call,put
		option1=temp.index[0]
		if option1[5]==u'购':
			option2=option1[:5]+u'沽'+option1[6:]
		else:
			option2=option1[:5]+u'购'+option1[6:]
		if option1[5]==u'购':
			CallCode=str(temp.loc[option1][0])+'.SH'
			PutCode=str(temp.loc[option2][0])+'.SH'
		else:
			CallCode=str(temp.loc[option2][0])+'.SH'
			PutCode=str(temp.loc[option1][0])+'.SH'
		codes=CallCode+','+PutCode+','+'510050.SH'
		#导入分钟数据
		try:
			tempframe=pd.read_excel(self.ETFMinuteRootdir+date+'_'+monthtype+'_ETF.xlsx')
		except:
			data=w.wsi(codes, "close", date+" 09:00:00", date+" 15:01:00", "BarSize=1;Fill=Previous;PriceAdj=F")
			tempIndex=data.Times
			tempframe=pd.DataFrame(data.Data[1:],columns=tempIndex,index=data.Fields[1:]).T
			writer=pd.ExcelWriter(self.ETFMinuteRootdir+date+'_'+monthtype+'_ETF.xlsx')		
			tempframe.to_excel(writer,u'平值期权分钟数据')
			writer.save()

		res=tempframe.groupby('windcode')
		for code,frame in res:
			if code==CallCode:
				Callframe=frame
			elif code==PutCode:
				Putframe=frame
			else:
				Uframe=frame
		resframe=pd.concat([Callframe,Putframe,Uframe],axis=1).iloc[:,[1,3,5]]
		resframe=pd.DataFrame(np.matrix(resframe),index=resframe.index,columns=['c','p','close'])
		tt=resframe
		tt.loc[:,'c-p+K*D']=tt.loc[:,'c']-tt.loc[:,'p']+tt.loc[:,'close']*np.exp(-r*ptmtradeday/252)
		tt.loc[:,'Premium']=(tt.loc[:,'c-p+K*D']-tt.loc[:,'close'])/tt.loc[:,'close']
		#返回c,p,close
		return tt
		
	def DataProcess(self):
		ETFList=os.listdir(self.ETFRootdir)[-20:]
		PremiumNearList=[]
		PremiumNextList=[]
		DateList=[]
		for EList in ETFList:
			Month_Sort=pd.read_excel(self.ETFRootdir+EList).groupby('ptmtradeday')
			date=str(EList[:10])
			DateList.append(date)
			self.date=date
			PtmTradeday=[]
			for i,(ptm,month_sort) in enumerate(Month_Sort):
				if i==0:
					Near_month=month_sort.sort_values(by='volume',ascending=False)
				elif i==1:
					Next_month=month_sort.sort_values(by='volume',ascending=False)
				else:
					break
				PtmTradeday.append(ptm)
			#shibor利率
			r=self.Rframe.loc[date][0]
			Near_frame=self.OptionSort(Near_month,date,PtmTradeday[0],r,'Near')
			Next_frame=self.OptionSort(Next_month,date,PtmTradeday[1],r,'Next')
			Near_Prem=Near_frame['Premium']
			Next_Prem=Next_frame['Premium']
			#收盘价，最大，最小，均值
			tmp1=[Near_Prem.iloc[-1],Near_Prem.max(),Near_Prem.min(),Near_Prem.mean()]
			tmp2=[Next_Prem.iloc[-1],Next_Prem.max(),Next_Prem.min(),Next_Prem.mean()]
			Premium_near=tmp1
			Premium_next=tmp2
			PremiumNearList.append(Premium_near)
			PremiumNextList.append(Premium_next)
		PreList1=pd.DataFrame(PremiumNearList)
		PreList2=pd.DataFrame(PremiumNextList)
		#print PreList1
		self.PremiumNearframe=pd.DataFrame(np.matrix(PreList1),index=DateList,columns=['close','max','min','mean'])
		self.PremiumNextframe=pd.DataFrame(np.matrix(PreList2),index=DateList,columns=['close','max','min','mean'])

class MCompound(Compound):
	def __init__(self):
		Compound.__init__(self)
		#self.MFutureRootdir='C:/Users/fsd/OneDrive/Python/founder_future/MFuture_Data_Processed/'
	def OptionSort(self,frame,date,ptmtradeday,r,monthtype):
		temp=IndexCopy(frame)
		#筛选call,put
		option1=temp.index[0]
		if option1[6]=='C':
			option2=option1[:6]+'P'+option1[7:]
		else:
			option2=option1[:6]+'C'+option1[7:]
		if option1[6]=='P':
			CallCode=str(temp.loc[option1][0])+'.DCE'
			PutCode=str(temp.loc[option2][0])+'.DCE'
		else:
			CallCode=str(temp.loc[option2][0])+'.DCE'
			PutCode=str(temp.loc[option1][0])+'.DCE'
		codes=CallCode+','+PutCode+','+CallCode[:5]+'.DCE'
		#导入分钟数据
		try:
			tempframe=pd.read_excel(self.MMinuteRootdir+date+'_'+monthtype+'_M.xlsx')
		except:
			data=w.wsi(codes, "close", date+" 09:00:00", date+" 15:01:00", "BarSize=1;Fill=Previous;PriceAdj=F")
			tempIndex=data.Times
			tempframe=pd.DataFrame(data.Data[1:],columns=tempIndex,index=data.Fields[1:]).T
			writer=pd.ExcelWriter(self.MMinuteRootdir+date+'_'+monthtype+'_M.xlsx')		
			tempframe.to_excel(writer,u'平值期权分钟数据')
			writer.save()
		#print codes
		#print tempframe
		res=tempframe.groupby('windcode')
		for code,frame in res:
			code='m'+code[1:]
			#print code,frame
			if code==CallCode:
				#print 1
				Callframe=frame
			elif code==PutCode:
				Putframe=frame
				#print 2
			else:
				Uframe=frame
				#print 3
		resframe=pd.concat([Callframe,Putframe,Uframe],axis=1).iloc[:,[1,3,5]]
		resframe=pd.DataFrame(np.matrix(resframe),index=resframe.index,columns=['c','p','close'])
		tt=resframe
		#print tt
		tt.loc[:,'c-p+K*D']=tt.loc[:,'c']-tt.loc[:,'p']+tt.loc[:,'close']*np.exp(-r*ptmtradeday/252)
		tt.loc[:,'Premium']=(tt.loc[:,'c-p+K*D']-tt.loc[:,'close'])/tt.loc[:,'close']
		#返回c,p,close
		return tt
	def DataProcess(self):
		MOptionList=os.listdir(self.MRootdir)[-20:]
		PremiumNearList=[]
		PremiumNextList=[]
		DateList=[]
		for MList in MOptionList:
			Month_Sort=pd.read_excel(self.MRootdir+MList).groupby('ptmtradeday')
			date=str(MList[:8])
			date=date[:4]+'-'+date[4:6]+'-'+date[6:8]
			DateList.append(date)
			self.date=date
			PtmTradeday=[]
			for i,(ptm,month_sort) in enumerate(Month_Sort):
				if i==0:
					Near_month=month_sort.sort_values(by=u'成交量',ascending=False)
					Vol_near=Near_month.sum().loc[u'成交量']
					PtmTradeday.append(ptm)
				elif i==1:
					Next_month=month_sort.sort_values(by=u'成交量',ascending=False)
					Vol_next=Next_month.sum().loc[u'成交量']
					PtmTradeday.append(ptm)
				else:
					Vol_Temp=month_sort.sum().loc[u'成交量']
					if Vol_Temp<min(Vol_near,Vol_next):
						pass
					else:
						if Vol_near>Vol_next:
							Next_month=month_sort.sort_values(by=u'成交量',ascending=False)
							Vol_next=Vol_Temp
							PtmTradeday[1]=ptm
						else:
							Near_month=Next_month
							Next_month=month_sort.sort_values(by=u'成交量',ascending=False)
							Vol_near=Vol_next
							Vol_next=Vol_Temp
							PtmTradeday[0]=PtmTradeday[1]
							PtmTradeday[1]=ptm
						
			#shibor利率
			r=self.Rframe.loc[date][0]
			Near_frame=self.OptionSort(Near_month,date,PtmTradeday[0],r,'Near')
			Next_frame=self.OptionSort(Next_month,date,PtmTradeday[1],r,'Next')
			Near_Prem=Near_frame['Premium']
			Next_Prem=Next_frame['Premium']
			#收盘价，最大，最小，均值
			tmp1=[Near_Prem.iloc[-1],Near_Prem.max(),Near_Prem.min(),Near_Prem.mean()]
			tmp2=[Next_Prem.iloc[-1],Next_Prem.max(),Next_Prem.min(),Next_Prem.mean()]
			Premium_near=tmp1
			Premium_next=tmp2
			PremiumNearList.append(Premium_near)
			PremiumNextList.append(Premium_next)
		PreList1=pd.DataFrame(PremiumNearList)
		PreList2=pd.DataFrame(PremiumNextList)
		#print PreList1
		self.PremiumNearframe=pd.DataFrame(np.matrix(PreList1),index=DateList,columns=['close','max','min','mean'])
		self.PremiumNextframe=pd.DataFrame(np.matrix(PreList2),index=DateList,columns=['close','max','min','mean'])

class SRCompound(Compound):
	def __init__(self):
		Compound.__init__(self)
	def OptionSort(self,frame,date,ptmtradeday,r,monthtype):
		temp=IndexCopy(frame)
		#筛选call,put
		option1=temp.index[0]
		if option1[5]=='C':
			option2=option1[:5]+'P'+option1[6:]
		else:
			option2=option1[:5]+'C'+option1[6:]
		if option1[5]=='P':
			CallCode=str(temp.loc[option1][0])+'.CZC'
			PutCode=str(temp.loc[option2][0])+'.CZC'
		else:
			CallCode=str(temp.loc[option2][0])+'.CZC'
			PutCode=str(temp.loc[option1][0])+'.CZC'
		codes=CallCode+','+PutCode+','+CallCode[:5]+'.CZC'
		#print codes
		#导入分钟数据
		try:
			tempframe=pd.read_excel(self.SRMinuteRootdir+date+'_'+monthtype+'_SR.xlsx')
		except:
			data=w.wsi(codes, "close", date+" 09:00:00", date+" 15:01:00", "BarSize=1;Fill=Previous;PriceAdj=F")
			tempIndex=data.Times
			tempframe=pd.DataFrame(data.Data[1:],columns=tempIndex,index=data.Fields[1:]).T
			writer=pd.ExcelWriter(self.SRMinuteRootdir+date+'_'+monthtype+'_SR.xlsx')		
			tempframe.to_excel(writer,u'平值期权分钟数据')
			writer.save()
		res=tempframe.groupby('windcode')
		for code,frame in res:
			#print code,frame
			if code==CallCode:
				#print 1
				Callframe=frame
			elif code==PutCode:
				Putframe=frame
				#print 2
			else:
				Uframe=frame
				#print 3
		resframe=pd.concat([Callframe,Putframe,Uframe],axis=1).iloc[:,[1,3,5]]
		resframe=pd.DataFrame(np.matrix(resframe),index=resframe.index,columns=['c','p','close'])
		tt=resframe
		tt.loc[:,'c-p+K*D']=tt.loc[:,'c']-tt.loc[:,'p']+tt.loc[:,'close']*np.exp(-r*ptmtradeday/252)
		tt.loc[:,'Premium']=(tt.loc[:,'c-p+K*D']-tt.loc[:,'close'])/tt.loc[:,'close']	
		#返回c,p,close
		return tt
	def DataProcess(self):
		SROptionList=os.listdir(self.SRRootdir)[-20:]
		PremiumNearList=[]
		PremiumNextList=[]
		DateList=[]
		for SRList in SROptionList:
			Month_Sort=pd.read_excel(self.SRRootdir+SRList).groupby('ptmtradeday')
			date=str(SRList[:8])
			date=date[:4]+'-'+date[4:6]+'-'+date[6:8]
			self.date=date
			DateList.append(date)
			PtmTradeday=[]
			for i,(ptm,month_sort) in enumerate(Month_Sort):
				if i==0:
					Near_month=month_sort.sort_values(by=u'成交量(手)',ascending=False)
					Vol_near=Near_month.sum().loc[u'成交量(手)']
					PtmTradeday.append(ptm)
				elif i==1:
					Next_month=month_sort.sort_values(by=u'成交量(手)',ascending=False)
					Vol_next=Next_month.sum().loc[u'成交量(手)']
					PtmTradeday.append(ptm)
				else:
					Vol_Temp=month_sort.sum().loc[u'成交量(手)']
					if Vol_Temp<min(Vol_near,Vol_next):
						pass
					else:
						if Vol_near>Vol_next:
							Next_month=month_sort.sort_values(by=u'成交量(手)',ascending=False)
							Vol_next=Vol_Temp
							PtmTradeday[1]=ptm
						else:
							Near_month=Next_month
							Next_month=month_sort.sort_values(by=u'成交量(手)',ascending=False)
							Vol_near=Vol_next
							Vol_next=Vol_Temp
							PtmTradeday[0]=PtmTradeday[1]
							PtmTradeday[1]=ptm
			#shibor利率
			r=self.Rframe.loc[date][0]
			Near_frame=self.OptionSort(Near_month,date,PtmTradeday[0],r,'Near')
			Next_frame=self.OptionSort(Next_month,date,PtmTradeday[1],r,'Next')
			Near_Prem=Near_frame['Premium']
			Next_Prem=Next_frame['Premium']
			#收盘价，最大，最小，均值
			tmp1=[Near_Prem.iloc[-1],Near_Prem.max(),Near_Prem.min(),Near_Prem.mean()]
			tmp2=[Next_Prem.iloc[-1],Next_Prem.max(),Next_Prem.min(),Next_Prem.mean()]
			Premium_near=tmp1
			Premium_next=tmp2
			PremiumNearList.append(Premium_near)
			PremiumNextList.append(Premium_next)
		PreList1=pd.DataFrame(PremiumNearList)
		PreList2=pd.DataFrame(PremiumNextList)
		#print PreList1
		self.PremiumNearframe=pd.DataFrame(np.matrix(PreList1),index=DateList,columns=['close','max','min','mean'])
		self.PremiumNextframe=pd.DataFrame(np.matrix(PreList2),index=DateList,columns=['close','max','min','mean'])

tmp1=Compound()
WeekRootdir='C:/Users/fsd/OneDrive/Python/founder_future/CommodityOption/compound/ETFOption/'
writer=pd.ExcelWriter(WeekRootdir+tmp1.date+'_ETF.xlsx')		
tmp1.PremiumNearframe.to_excel(writer,u'近月合成标的')
tmp1.PremiumNextframe.to_excel(writer,u'次近月合成标的')
writer.save()

tmp2=MCompound()
WeekRootdir='C:/Users/fsd/OneDrive/Python/founder_future/CommodityOption/compound/MOption/'
writer=pd.ExcelWriter(WeekRootdir+tmp2.date+'_M.xlsx')		
tmp2.PremiumNearframe.to_excel(writer,u'主力合成标的')
tmp2.PremiumNextframe.to_excel(writer,u'次主力合成标的')
writer.save()

tmp3=SRCompound()
WeekRootdir='C:/Users/fsd/OneDrive/Python/founder_future/CommodityOption/compound/SROption/'
writer=pd.ExcelWriter(WeekRootdir+tmp3.date+'_SR.xlsx')		
tmp3.PremiumNearframe.to_excel(writer,u'主力合成标的')
tmp3.PremiumNextframe.to_excel(writer,u'次主力合成标的')
writer.save()