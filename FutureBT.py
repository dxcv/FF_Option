#!/usr/bin/python
# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd
import collections
import re 
import os
from fengshidian import *
from datetime import datetime

class FutureBackTest:
	def __init__(self,StartDate,EndDate,InitialFundAccount):
		self.StartDate=StartDate
		self.EndDate=EndDate
		self.InitialFundAccount=InitialFundAccount
		self.AccountCreate()
	def AccountCreate(self):
		self.FutureAccount={}#期货账户
		self.FutureAccount=collections.OrderedDict()
		self.OffSetAccount={}#平仓盈亏账户
		self.OffSetAccount=collections.OrderedDict()

		self.FutureAccountRecord={}#记录期货交易账户
		self.FutureAccountRecord=collections.OrderedDict()

		self.FundAccount={}#可用资金账户
		self.FundAccount=collections.OrderedDict()
		self.MarginAccount={}#保证金账户
		self.MarginAccount=collections.OrderedDict()
		self.EquityAccount={}#权益账户
		self.EquityAccount=collections.OrderedDict()

		self.TotalPosition={}#持有头寸账户
		self.TotalPosition=collections.OrderedDict()
	#开多头仓
	def LongPosition(self,futurename,num):
		self.FutureAccount[self.date][futurename]=num
		self.FutureAccountRecord[self.date][futurename]=num
		
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
	#开空头仓
	def ShortPosition(self,futurename,num):
		self.FutureAccount[self.date][futurename]=-num
		self.FutureAccountRecord[self.date][futurename]=-num
		
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
	#平全部仓位，并计算平仓盈亏
	def ClosePositionAll(self):
		NumDate=len(self.FutureAccount.keys())
		OffSet_total=0.0
		for i in range(NumDate):
			HoldingAccount=self.FutureAccount[self.FutureAccount.keys()[i]]
			futurenames=HoldingAccount.keys()
			for futurename in futurenames:
				self.FutureAccountRecord[self.date][futurename]=0.0
				diff=self.data.loc[futurename,u'收盘价']-self.data.loc[futurename,u'前结算价']
				OffSet_total=OffSet_total+diff*HoldingAccount[futurename]*self.Unit
				if HoldingAccount[futurename]>0:#平多头仓
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
				else:#平空头仓
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[futurename]

		self.OffSetAccount[self.date]=OffSet_total

		dates=self.FutureAccount.keys()
		for date in dates:
			del self.FutureAccount[date]
			
	#平某一交易日的仓位，并计算平仓盈亏
	def ClosePositionDaily(self,date):
		print self.date,'close_daily'
		try:
			self.OffSetAccount[self.date]=self.OffSetAccount[self.date]
		except:
			self.OffSetAccount[self.date]=0.0
		HoldingAccount=self.FutureAccount[date]
		futurenames=HoldingAccount.keys()
		OffSet_total=0.0
		for futurename in futurenames:
			self.FutureAccountRecord[self.date][futurename]=0.0
			diff=self.data.loc[futurename,u'收盘价']-self.data.loc[futurename,u'前结算价']
			OffSet_total=OffSet_total+diff*HoldingAccount[futurename]*self.Unit
			if HoldingAccount[futurename]>0:
				self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
			else:
				self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[futurename]

		self.OffSetAccount[self.date]=self.OffSetAccount[self.date]+OffSet_total
		del self.FutureAccount[date]
		
	#平部分仓位
	def ClosePositionPar(self,date,futurename,*args):
		print self.date,'closePar'
		
		try:
			self.OffSetAccount[self.date]=self.OffSetAccount[self.date]
		except:
			self.OffSetAccount[self.date]=0.0
		HoldingAccount=self.FutureAccount[date]
		OffSet_total=0.0
		diff=self.data.loc[futurename,u'收盘价']-self.data.loc[futurename,u'前结算价']
		#平某一期货全部仓位
		if len(args)==0:
			self.FutureAccountRecord[self.date][futurename]=0.0
			OffSet_total=OffSet_total+diff*HoldingAccount[futurename]*self.Unit#平仓盈亏
			#self.OffSetAccount[self.date]=self.OffSetAccount[self.date]+OffSet_total

			if HoldingAccount[futurename]>0:
				self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
			else:
				self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[futurename]
			del self.FutureAccount[date][futurename]
			#若平仓后，该交易日无期货，则剔除
			if self.FutureAccount[date]:
				pass
			else:
				del self.FutureAccount[date]
		#平某一期货部分仓位
		elif len(args)==1:
			numPosition=args[0]
			if HoldingAccount[futurename]>0:#平多头仓
				tempPosition=HoldingAccount[futurename]-numPosition
				if tempPosition>=0:
					self.FutureAccount[date][futurename]=tempPosition
					self.FutureAccountRecord[self.date][futurename]=tempPosition
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*numPosition

					OffSet_total=OffSet_total+diff*numPosition*self.Unit#平仓盈亏
				else:
					self.FutureAccount[date][futurename]=0.0
					self.FutureAccountRecord[self.date][futurename]=0.0
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
					OffSet_total=OffSet_total+diff*HoldingAccount[futurename]*self.Unit#平仓盈亏
					print u'平仓量多于持仓量，只平所持头寸的仓位'
					#
					del self.FutureAccount[date][futurename]
					
					if self.FutureAccount[date]:
						pass
					else:
						del self.FutureAccount[date]
						

			else:#平空头仓
				tempPosition=HoldingAccount[futurename]+numPosition
				if tempPosition<=0:
					self.FutureAccount[date][futurename]=tempPosition
					self.FutureAccountRecord[self.date][futurename]=tempPosition
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*numPosition
					OffSet_total=OffSet_total+diff*numPosition*self.Unit#平仓盈亏
				else:
					self.FutureAccount[date][futurename]=0.0
					self.FutureAccountRecord[self.date][futurename]=0.0
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*np.abs(HoldingAccount[futurename])
					OffSet_total=OffSet_total+diff*HoldingAccount[futurename]*self.Unit#平仓盈亏
					print u'平仓量多于持仓量，只平所持头寸的仓位'
					del self.FutureAccount[date][futurename]
					
					if self.FutureAccount[date]:
						pass
					else:
						del self.FutureAccount[date]
			
		else:		
			print u'参数过多，终止程序！'
			exit(1)

		self.OffSetAccount[self.date]=self.OffSetAccount[self.date]+OffSet_total
	#计算持有头寸
	def TotalPositionCal(self):
		self.TotalPosition[self.date]={}
		#print self.TotalPosition[self.date]
		self.TotalPosition[self.date]=collections.OrderedDict()
		#总持仓格式为{date：{某交易日1：[],某交易日2：[],....,某交易日n:[]}},其中[]中依次为多头(+)，空头(-)，总持仓数(多头加空头绝对值)
		
		PositionDates=self.FutureAccount.keys()
		#print PositionDates
		#print self.FutureAccount[PositionDates[0]]
		if self.FutureAccount[PositionDates[0]]:
			for i in range(len(PositionDates)):
				self.TotalPosition[self.date][PositionDates[i]]=[]
				total_long=0
				total_short=0

				HoldingAccount=self.FutureAccount[PositionDates[i]]
				if HoldingAccount:
					for futurename in HoldingAccount.keys():
						if HoldingAccount[futurename]>0:
							total_long=total_long+HoldingAccount[futurename]
						else:
							total_short=total_short+HoldingAccount[futurename]
					self.TotalPosition[self.date][PositionDates[i]].append(total_long)
					self.TotalPosition[self.date][PositionDates[i]].append(total_short)
					self.TotalPosition[self.date][PositionDates[i]].append(total_long+np.abs(total_short))
					#print self.TotalPosition[self.date]
		else:
			pass
	#计算某只期货保证金
	def MarginCal(self,futurename):
		return self.data.loc[futurename,u'结算参考价']*self.MarRatio
	#保证金汇总
	def MarginSumCal(self):
		TempMargin=0.0
		PositionDates=self.FutureAccount.keys()
		for i in range(len(PositionDates)):
			HoldingAccount=self.FutureAccount[PositionDates[i]]
			if HoldingAccount:
				for futurename in HoldingAccount.keys():
					TempMargin=TempMargin+self.MarginCal(futurename)*HoldingAccount[futurename]

		self.MarginAccount[self.date]=TempMargin
	#计算盈亏
	def SettlementDaily(self):
		#持仓盈亏
		PositionGL_total=0.0
		PositionDates=self.FutureAccount.keys()
		for i in range(len(PositionDates)):
			HoldingAccount=self.FutureAccount[PositionDates[i]]
			if HoldingAccount:
				for futurename in HoldingAccount.keys():
					if PositionDates[i]==self.date:#当日持仓
						diff=self.data.loc[futurename,u'结算参考价']-self.data.loc[futurename,u'收盘价']
						PositionGL_total=PositionGL_total+diff*HoldingAccount[futurename]*self.Unit
					else:
						diff=self.data.loc[futurename,u'结算参考价']-self.data.loc[futurename,u'前结算价']
						PositionGL_total=PositionGL_total+diff*HoldingAccount[futurename]*self.Unit
		#print self.FundAccount,self.OffSetAccount
		self.FundAccount[self.date]=self.FundAccount[self.date]+self.OffSetAccount[self.date]+PositionGL_total
		self.EquityAccount[self.date]=self.FundAccount[self.date]
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.MarginAccount[self.date]



class SQSFutureBackTest(FutureBackTest):
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision,FutureType,Unit,MarRatio):
		FutureBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.Commision=Commision
		self.FutureType=FutureType
		self.Unit=Unit
		self.MarRatio=MarRatio
		self.Rootdir='C:/Users/fsd/OneDrive/Python/founder_future/ZSQSData/'
		self.FutureRootdir=self.Rootdir+FutureType+'_f/'
		self.FutureList=os.listdir(self.FutureRootdir)
		self.dataImport()
		self.Strategy()
		self.IndicatorCalculate()
		self.DataOutPut()
	#导入指标，或自行计算指标
	def dataImport(self):
		close=[]
		DATE=[]
		close_week=[]
		DATE_week=[]
		for future in self.FutureList:
			date=future[:8]
			DATE.append(date)
			data=pd.read_excel(self.FutureRootdir+future).sort_values(by=u'成交量',ascending=False)
			close.append(data.iloc[0].loc[u'收盘价'])
			weekday=datetime.strptime(date,"%Y%m%d").weekday()+1
			if weekday==5:
				DATE_week.append(date)
				close_week.append(data.iloc[0].loc[u'收盘价'])
		self.close_frame=pd.DataFrame(close,index=DATE,columns=['close_day'])
		self.close_week_frame=pd.DataFrame(close_week,index=DATE_week,columns=['close_week'])
		#print self.close_week_frame
		self.close_MA_5=self.close_frame.rolling(window=5).mean()
		self.close_week_MA_5=self.close_week_frame.rolling(window=5).mean()
		#print self.close_week_MA_5
	#导入每天的交易数据
	def DataImportDaily(self,future,date):
		self.data=pd.read_excel(self.FutureRootdir+future).sort_values(by=u'成交量',ascending=False)
		date1=str(self.data.loc[:,"EXPIREDATE"].iloc[0])
		date2=str(date)
		date1=datetime.strptime(date1,"%Y%m%d")
		date2=datetime.strptime(date2,"%Y%m%d")
		diff_day=(date1-date2).days
		if diff_day<=7:
			self.dataOpen=self.data.iloc[1:,:]
		else:
			self.dataOpen=self.data
	#期货若剩3个自然日到期，自动平仓
	def MaturityClose(self):
		PositionDates=self.FutureAccount.keys()
		for i in range(len(PositionDates)):
			HoldingAccount=self.FutureAccount[PositionDates[i]]
			if HoldingAccount:
				for futurename in HoldingAccount.keys():
					date1=str(self.data.loc[futurename,"EXPIREDATE"])
					date2=self.date
					date1=datetime.strptime(date1,"%Y%m%d")
					date2=datetime.strptime(date2,"%Y-%m-%d")
					diff_day=(date1-date2).days
					#print diff_day
					if diff_day<=3:
						print 'MaturityClose'
						self.ClosePositionPar(PositionDates[i],futurename)
	#回测
	def Strategy(self):
		FutureList=self.FutureList
		self.daynum=0
		for future in FutureList:
			tempdate=future[:8]
			self.tempdate=tempdate
			date=tempdate[:4]+'-'+tempdate[4:6]+'-'+tempdate[6:8]
			date=str(date)
			self.date=date
			
			if date>=self.StartDate and date<=self.EndDate:
				print date
				#每日开盘前操作
				self.FutureAccount[self.date]={}
				self.FutureAccount[self.date]=collections.OrderedDict()
				self.FutureAccountRecord[self.date]={}
				self.FutureAccountRecord[self.date]=collections.OrderedDict()
				self.OffSetAccount[self.date]=0.0

				if self.daynum==0:
					self.FundAccount[self.date]=self.InitialFundAccount
					self.daynum=self.daynum+1
				else:
					self.FundAccount[self.date]=self.FundAccount[self.FundAccount.keys()[-1]]
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.MarginAccount[self.MarginAccount.keys()[-1]]

				#导入每日交易数据
				self.DataImportDaily(future,self.tempdate)
				#对即将到期的合约进行平仓
				self.MaturityClose()
				#计算持有多头，空头，总持仓情况
				self.TotalPositionCal()
				#策略
				self.StrategyDaily(date)
				#每日保证金计算
				self.MarginSumCal()
				#每日盈亏结算
				self.SettlementDaily()
	#策略
	def StrategyDaily(self,date):
		tempdate=date[:4]+date[5:7]+date[8:10]#tempdate形式为'20160101' date形式为'2016-01-01'
		Date=datetime.strptime(date,"%Y-%m-%d").weekday()+1
		#print self.TotalPosition[self.date]
		#print self.FutureAccount.keys()
		if self.TotalPosition[self.date]:
			
			long_position=self.TotalPosition[self.date][self.FutureAccount.keys()[0]][0]
			short_position=self.TotalPosition[self.date][self.FutureAccount.keys()[0]][1]
			total_position=self.TotalPosition[self.date][self.FutureAccount.keys()[0]][2]
			#print long_position
		else:
			long_position=0.0
			short_position=0.0
			total_position=0.0
		
		if total_position==0:#空仓
			if Date==5:
				
				self.Max_Retracement_data=[]
				self.Max_Retracement_data.append(self.dataOpen.iloc[0].loc[u'收盘价'])
				TradeCapital=self.FundAccount[date]*0.1
				#print self.close_MA_5
				MA_tmp1=self.close_MA_5.loc[tempdate,'close_day']
				#print self.close_week_MA_5
				MA_tmp2=self.close_week_MA_5.loc[tempdate,'close_week']
				tmp1=self.close_frame.loc[tempdate,'close_day']
				tmp2=self.close_week_frame.loc[tempdate,'close_week']
				if tmp1>MA_tmp1 and tmp2>MA_tmp2:
					TradeCapitalUnit=self.MarginCal(self.dataOpen.index[0])
					num=min(max(int(TradeCapital/TradeCapitalUnit),0),20)
					futurename=self.dataOpen.index[0]
					self.LongPosition(futurename,num)
					print u'开仓'
		elif total_position>0 and long_position>0:#多头仓

			self.Max_Retracement_data.append(self.dataOpen.iloc[0].loc[u'收盘价'])
			data=self.Max_Retracement_data
			#print 'data',data
			try:
				index_j = np.argmax(np.maximum.accumulate(data) - data)  # 结束位置
				index_i = np.argmax(data[:index_j])  # 开始位置
				Max_Retracement= float(data[index_j] - data[index_i])/data[index_i]  # 最大回撤
			except:
				Max_Retracement=0
			#print Max_Retracement
			if Max_Retracement<-0.05:
				self.ClosePositionAll()
				print u'平仓'

				del self.Max_Retracement_data
		else:
			pass
		#平仓
		try:
			if self.FutureAccount[self.date]:
				pass
			else:
				del self.FutureAccount[self.date]
		except:
			pass

	#指标计算
	def IndicatorCalculate(self):
		self.EquityAccountframe=pd.DataFrame.from_dict(self.EquityAccount, orient='index')
		self.FundAccountframe=pd.DataFrame.from_dict(self.FundAccount, orient='index')
		self.MarginAccountframe=pd.DataFrame.from_dict(self.MarginAccount, orient='index')
		#self.OptionAccountRecordframe=pd.DataFrame.from_dict(self.OptionAccountRecord,orient='index')
		for i in self.FutureAccountRecord.keys():
			print i,self.FutureAccountRecord[i]
		#收益率计算
		#print self.EquityAccountframe
		TempYield=(self.EquityAccountframe-self.InitialFundAccount)/self.InitialFundAccount
		#print TempYield
		self.Yield=pd.DataFrame(np.matrix(TempYield),index=TempYield.index,columns=['Yield'])
		#最大回撤计算retracement
		data=self.Yield.loc[:,'Yield'].values
		index_j = np.argmax(np.maximum.accumulate(data) - data)  # 结束位置
		index_i = np.argmax(data[:index_j])  # 开始位置
		print data
		self.Max_Retracement= (data[index_j] - data[index_i])/data[index_i]  # 最大回撤
	#数据导出
	def DataOutPut(self):
		writer=pd.ExcelWriter('test.xlsx')
		self.Yield.to_excel(writer,self.FutureType+'_test_data')
		writer.save()
#1、报价单位：铜、铝、锌、铅、镍、锡、螺纹钢、线材、热轧卷板、天然橡胶、燃料油、石油沥青为元/吨；黄金为元/克；白银为元/千克。
#2、交易单位：铜、铝、锌、铅为5吨/手；镍、锡为1吨/手；螺纹钢、线材、热轧卷板、石油沥青、天然橡胶为10吨/手；燃料油为10吨/手；黄金为1000克/手；白银为15千克/手。
#商品代码：铜(cu),铝(al),锌(zn),铅(pb),镍(ni),锡(sn),银(ag),黄金(au),螺纹钢(rb),线材(wr)(数据均为0),热轧卷板(hc),燃料油(fu),石油沥青(bu),天然橡胶(ru)
#保证金均取10%
StartDate='2015-04-03'
EndDate='2018-08-15'
InitialFundAccount=1000000
Commision=0.0
FutureType='ru'
Unit=10.0
MarRatio=0.1
SQSFutureBackTest(StartDate,EndDate,InitialFundAccount,Commision,FutureType,Unit,MarRatio)