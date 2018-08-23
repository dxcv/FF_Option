#!/usr/bin/python
# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd
import collections
import re 
import os
from fengshidian import *
from datetime import datetime
class OptionBackTest:
	def __init__(self,StartDate,EndDate,InitialFundAccount):
		self.StartDate=StartDate
		self.EndDate=EndDate
		self.InitialFundAccount=InitialFundAccount
		self.AccountCreate()
	def AccountCreate(self):
		self.OptionAccount={}
		self.OptionAccount=collections.OrderedDict()

		self.OptionAccountRecord={}
		self.OptionAccountRecord=collections.OrderedDict()

		self.FundAccount={}
		self.FundAccount=collections.OrderedDict()
		self.MarginAccount={}
		self.MarginAccount=collections.OrderedDict()
		self.EquityAccount={}
		self.EquityAccount=collections.OrderedDict()
		#标的主连及无风险利率
		self.RCVRootdir='C:/Users/fsd/OneDrive/Python/founder_future/shibor.xlsx'
	def LongPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=num
		self.OptionAccountRecord[self.date][optionname]=num
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.data.loc[optionname,u'收盘价']*num*self.Unit
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
	def ShortPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=-num
		self.OptionAccountRecord[self.date][optionname]=-num
		self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'收盘价']*num*self.Unit
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
	def ClosePositionAll(self):
		HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
		optionnames=HoldingAccount.keys()
		for optionname in optionnames:
			self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'收盘价']*HoldingAccount[optionname]*self.Unit
			self.OptionAccountRecord[self.date][optionname]=0.0
			if HoldingAccount[optionname]>0:
				self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[optionname]
			else:
				self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[optionname]
		del self.OptionAccount[self.OptionAccount.keys()[0]]
	def ClosePositionPar(self,optionname):
		num=self.OptionAccount[self.OptionAccount.keys()[0]][optionname]
		self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'收盘价']*num*self.Unit
		if num>0:
			self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		else:
			self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*num

		for opname in self.OptionAccount[self.OptionAccount.keys()[0]].keys():
			if opname==optionname:
				self.OptionAccountRecord[self.date][opname]=0.0
			else:
				self.OptionAccountRecord[self.date][opname]=self.OptionAccount[self.OptionAccount.keys()[0]][opname]

		del self.OptionAccount[self.OptionAccount.keys()[0]][optionname]
		#print self.date,self.OptionAccount[self.date]
		if self.OptionAccount[self.OptionAccount.keys()[0]]:
			pass
		else:
			del self.OptionAccount[self.OptionAccount.keys()[0]]

	#每个期权品种重写
	def MarginSumCal(self):
		TempMargin=0.0
		if self.OptionAccount:
			HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
			if HoldingAccount:
				for optionname in HoldingAccount.keys():
					num=HoldingAccount[optionname]
					if num>0:
						pass
					else:
						TempMargin=TempMargin+self.MarginCal(optionname)*np.abs(num)
		self.MarginAccount[self.date]=TempMargin
		self.FundAccount[self.date]=self.FundAccount[self.date]-TempMargin
	def EquityCal(self):
		temp=self.FundAccount[self.date]+self.MarginAccount[self.date]
		if self.OptionAccount:
			HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
			optionnames=HoldingAccount.keys()
			for optionname in optionnames:
				temp=temp+self.data.loc[optionname,u'收盘价']*HoldingAccount[optionname]*self.Unit
		else:#
			#print 'No Options'
			pass
		self.EquityAccount[self.date]=temp
	def IndicatorCalculate(self):
		self.EquityAccountframe=pd.DataFrame.from_dict(self.EquityAccount, orient='index')
		self.FundAccountframe=pd.DataFrame.from_dict(self.FundAccount, orient='index')
		self.MarginAccountframe=pd.DataFrame.from_dict(self.MarginAccount, orient='index')
		for i in self.OptionAccountRecord.keys():
			print i,self.OptionAccountRecord[i]
		#收益率计算
		#print self.EquityAccountframe
		TempYield=(self.EquityAccountframe-self.InitialFundAccount)/self.InitialFundAccount
		#print TempYield
		self.Yield=pd.DataFrame(np.matrix(TempYield),index=TempYield.index,columns=['Yield'])
		#最大回撤计算retracement
		data=self.Yield.loc[:,'Yield'].values
		index_j = np.argmax(np.maximum.accumulate(data) - data)  # 结束位置
		index_i = np.argmax(data[:index_j])  # 开始位置
		self.Max_Retracement= (data[index_j] - data[index_i])/data[index_i]
	def BullCallDaily(self,date,U_Strike,delta_Strike,LongShortType):
		#print self.OptionAccount
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		if self.OptionType=='M':
			OTP=6
		elif self.OptionType=='SR':
			OTP=5
		else:
			print 'option type waring '
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			Strike=float(optionname[-4:])
			if U_Strike>Strike:
				for i in range(10):
					if U_Strike<Strike+delta_Strike*(i+1):
						Strike_1=Strike+delta_Strike*i
						Strike_2=Strike+delta_Strike*(i+1)
						break
					else:
						pass
			else:
				for i in range(10):
					if U_Strike>Strike-delta_Strike*(i+1):
						Strike_2=Strike-delta_Strike*i
						Strike_1=Strike-delta_Strike*(i+1)
						break
					else:
						pass
			Option_1=(optionname[:OTP]+'C'+optionname[OTP+1:])[:-4]+str(int(Strike_1))
			Option_2=(optionname[:OTP]+'C'+optionname[OTP+1:])[:-4]+str(int(Strike_2))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.ShortPosition(Option_2,1)
			else:
				self.ShortPosition(Option_1,1)
				self.LongPosition(Option_2,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def BullPutDaily(self,date,U_Strike,delta_Strike,LongShortType):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		if self.OptionType=='M':
			OTP=6
		elif self.OptionType=='SR':
			OTP=5
		else:
			print 'option type waring '
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			Strike=float(optionname[-4:])
			if U_Strike>Strike:
				for i in range(10):
					if U_Strike<Strike+delta_Strike*(i+1):
						Strike_1=Strike+delta_Strike*i
						Strike_2=Strike+delta_Strike*(i+1)
						break
					else:
						pass
			else:
				for i in range(10):
					if U_Strike>Strike-delta_Strike*(i+1):
						Strike_2=Strike-delta_Strike*i
						Strike_1=Strike-delta_Strike*(i+1)
						break
					else:
						pass
			Option_1=(optionname[:OTP]+'P'+optionname[OTP+1:])[:-4]+str(int(Strike_1))
			Option_2=(optionname[:OTP]+'P'+optionname[OTP+1:])[:-4]+str(int(Strike_2))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.ShortPosition(Option_2,1)
			else:
				self.ShortPosition(Option_1,1)
				self.LongPosition(Option_2,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def Straddle(self,date,LongShortType):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		if self.OptionType=='M':
			OTP=6
		elif self.OptionType=='SR':
			OTP=5
		else:
			print 'option type waring '
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			Strike=float(optionname[-4:])
			
			Option_1=(optionname[:OTP]+'C'+optionname[OTP+1:])[:-4]+str(int(Strike))
			Option_2=(optionname[:OTP]+'P'+optionname[OTP+1:])[:-4]+str(int(Strike))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.LongPosition(Option_2,1)
			else:
				self.ShortPosition(Option_1,1)
				self.ShortPosition(Option_2,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def Strangle(self,date,U_Strike,delta_Strike,LongShortType):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		if self.OptionType=='M':
			OTP=6
		elif self.OptionType=='SR':
			OTP=5
		else:
			print 'option type waring '
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			Strike=float(optionname[-4:])
			if U_Strike>Strike:
				for i in range(10):
					if U_Strike<Strike+delta_Strike*(i+1):
						Strike_1=Strike+delta_Strike*i
						Strike_2=Strike+delta_Strike*(i+1)
						break
					else:
						pass
			else:
				for i in range(10):
					if U_Strike>Strike-delta_Strike*(i+1):
						Strike_2=Strike-delta_Strike*i
						Strike_1=Strike-delta_Strike*(i+1)
						break
					else:
						pass
			Option_1=(optionname[:OTP]+'P'+optionname[OTP+1:])[:-4]+str(int(Strike_1))
			Option_2=(optionname[:OTP]+'C'+optionname[OTP+1:])[:-4]+str(int(Strike_2))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.LongPosition(Option_2,1)
			else:
				self.ShortPosition(Option_1,1)
				self.ShortPosition(Option_2,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def ButterflyCall(self,date,U_Strike,delta_Strike,LongShortType):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		if self.OptionType=='M':
			OTP=6
		elif self.OptionType=='SR':
			OTP=5
		else:
			print 'option type waring '
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			Strike=float(optionname[-4:])
			Strike_1=Strike-delta_Strike
			Strike_2=Strike
			Strike_3=Strike+delta_Strike

			Option_1=(optionname[:OTP]+'C'+optionname[OTP+1:])[:-4]+str(int(Strike_1))
			Option_2=(optionname[:OTP]+'C'+optionname[OTP+1:])[:-4]+str(int(Strike_2))
			Option_3=(optionname[:OTP]+'C'+optionname[OTP+1:])[:-4]+str(int(Strike_3))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.ShortPosition(Option_2,2)
				self.LongPosition(Option_3,1)
			else:
				self.ShortPosition(Option_1,1)
				self.LongPosition(Option_2,2)
				self.ShortPosition(Option_3,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def ButterflyPut(self,date,U_Strike,delta_Strike,LongShortType):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		if self.OptionType=='M':
			OTP=6
		elif self.OptionType=='SR':
			OTP=5
		else:
			print 'option type waring '
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			Strike=float(optionname[-4:])
			Strike_1=Strike-delta_Strike
			Strike_2=Strike
			Strike_3=Strike+delta_Strike

			Option_1=(optionname[:OTP]+'P'+optionname[OTP+1:])[:-4]+str(int(Strike_1))
			Option_2=(optionname[:OTP]+'P'+optionname[OTP+1:])[:-4]+str(int(Strike_2))
			Option_3=(optionname[:OTP]+'P'+optionname[OTP+1:])[:-4]+str(int(Strike_3))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.ShortPosition(Option_2,2)
				self.LongPosition(Option_3,1)
			else:
				self.ShortPosition(Option_1,1)
				self.LongPosition(Option_2,2)
				self.ShortPosition(Option_3,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass

	def VIXDailyTrade(self,dayIndicator,date):
		Vix=dayIndicator.loc['VIX']
		MA=dayIndicator.loc['MA']
		MA_minus=dayIndicator.loc['MA-n*std']
		MA_plus=dayIndicator.loc['MA+n*std']
		if self.OptionType=='M':
			OTP=6
		elif self.OptionType=='SR':
			OTP=5
		
		if self.total_volume>0:
			if Vix>=MA:
				self.ClosePositionAll()
			if Vix>MA_plus:
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.MarginCal(optionname)
					num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
					if num>0:
						#self.ShortPosition(optionname,num)
						self.ShortPosition(optionname,1)
						if optionname[OTP]=='C':
							optionname2=optionname[:OTP]+'P'+optionname[OTP+1:]
						else:
							optionname2=optionname[:OTP]+'C'+optionname[OTP+1:]
						self.ShortPosition(optionname2,1)
		elif self.total_volume<0:#有空头仓
			if Vix<=MA:#平仓
				self.ClosePositionAll()
			if Vix<MA_minus:#Vix过小，开多头仓
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.data.loc[optionname,u'收盘价']*self.Unit
					num=min(max(int(TradeCapital*1.0/len(options)/TradeCapitalUnit),0),50)
					if num>0:
						#self.LongPosition(optionname,num)
						self.LongPosition(optionname,1)
						if optionname[OTP]=="C":
							optionname2=optionname[:OTP]+"P"+optionname[OTP+1:]
						else:
							optionname2=optionname[:OTP]+"C"+optionname[OTP+1:]
						self.LongPosition(optionname2,1)
		else:
			if Vix>MA_plus:#开空头仓,合约到期时间要大于7个交易日
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.MarginCal(optionname)#卖一手期权所需缴纳的保证金
					num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
					if num>0:
						#self.ShortPosition(optionname,num)
						self.ShortPosition(optionname,1)
						if optionname[OTP]=="C":
							optionname2=optionname[:OTP]+"P"+optionname[OTP+1:]
						else:
							optionname2=optionname[:OTP]+"C"+optionname[OTP+1:]
						self.ShortPosition(optionname2,1)
			elif Vix<MA_minus:
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.data.loc[optionname,u'收盘价']*self.Unit
					num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
					if num>0:
						#self.LongPosition(optionname,num)
						self.LongPosition(optionname,1)
						if optionname[OTP]=="C":
							optionname2=optionname[:OTP]+"P"+optionname[OTP+1:]
						else:
							optionname2=optionname[:OTP]+"C"+optionname[OTP+1:]
						self.LongPosition(optionname2,1)
			else:
				pass

class SROptionBackTest(OptionBackTest):
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision,OptionType):
		OptionBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.OptionRootdir='C:/Users/fsd/OneDrive/Python/founder_future/SOption_Data_Processed/'
		self.SRFutureRootdir='C:/Users/fsd/OneDrive/Python/founder_future/SRFuture_Data_Processed/'
		self.IndicatorRootdir='C:/Users/fsd/Desktop/SROption.xlsm'
		self.OptionType=OptionType
		self.OptionList=os.listdir(self.OptionRootdir)
		self.Unit=10.0
		self.Commision=Commision
		self.dataImport()
		
		self.Strategy()
		
		self.IndicatorCalculate()
		self.DataOutput()
		
	def dataImport(self):
		#VIX指标导入
		temp=pd.read_excel(self.IndicatorRootdir,sheetname='VIX_oppor')[2:]
		#print temp
		tempindex=temp.iloc[:,0].values[1:]
		tempcols=temp.iloc[0,:][1:].values
		self.Indicator=pd.DataFrame(np.matrix(temp.iloc[1:,1:]),index=tempindex,columns=tempcols)
		#导入标的主连收盘成交量，无风险利率
		tmp=pd.read_excel(self.RCVRootdir,sheetname='SR')[3:]
		indextemp=[]
		for i in tmp.index:
			date=str(i)[:10]
			indextemp.append(date)
		self.obj=pd.DataFrame(np.matrix(tmp),index=indextemp,columns=['close','volume']).loc[self.StartDate:self.EndDate]
		
	def DataImportDaily(self,option,date):
		#开仓用self.dataOpen数据，平仓用self.data数据
		self.data=pd.read_excel(self.OptionRootdir+option).sort_values(by=u'成交量(手)',ascending=False)[[u'今结算',u'今收盘',u'成交量(手)','ptmtradeday']]
		self.FutureData=pd.read_excel(self.SRFutureRootdir+date+'_SR_Future.xls')[[u'今结算']]
		self.data=self.data[[u'今收盘',u'今结算',u'成交量(手)','ptmtradeday']]
		self.data=pd.DataFrame(np.matrix(self.data),index=self.data.index,columns=[u'收盘价',u'结算价',u'成交量','ptmtradeday'])
		self.dataOpen=self.data[self.data.loc[:,'ptmtradeday']>7]
		#if self.date=='2017-07-24':
			#print self.dataOpen
		self.FutureData=pd.DataFrame(np.matrix(self.FutureData),index=self.FutureData.index,columns=[[u'结算价']])
	def MarginCal(self,optionname):
		futurename=optionname[:5]
		StrikePrice=float(optionname[6:10])
		FutureSettlePrice=float(self.FutureData.loc[futurename,u'结算价'])
		OptionSettlePrice=float(self.data.loc[optionname,u'结算价'])
		if optionname[5]=='C':
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(StrikePrice-FutureSettlePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		else:
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(FutureSettlePrice-StrikePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		Margin=max(tmp1,tmp2)
		return Margin

	def Strategy(self):
		OptionList=self.OptionList
		Indicator=self.Indicator
		self.daynum=0
		for option in OptionList:
			tempdate=option[:8]
			self.tempdate=tempdate
			date=tempdate[:4]+'-'+tempdate[4:6]+'-'+tempdate[6:8]
			date=str(date)
			self.date=date
			#print date
			if date>=self.StartDate and date<=self.EndDate:
				#每日开盘前结算
				self.OptionAccount[self.date]={}
				self.OptionAccount[self.date]=collections.OrderedDict()
				self.OptionAccountRecord[self.date]={}
				self.OptionAccountRecord[self.date]=collections.OrderedDict()

				if self.daynum==0:
					self.FundAccount[self.date]=self.InitialFundAccount
					self.daynum=self.daynum+1
				else:
					self.FundAccount[self.date]=self.FundAccount[self.FundAccount.keys()[-1]]
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.MarginAccount[self.MarginAccount.keys()[-1]]

				#盘中操作，导入每天数据
				self.DataImportDaily(option,self.tempdate)
				
				#导入VIX指标
				#dayIndicator=self.Indicator.loc[date]
				#先对到期合约进行平仓，再判断持有多头，空头还是空仓
				HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						if self.data.loc[optionname,'ptmtradeday']==1:
							self.ClosePositionPar(optionname)
				#判断是否持有多头，空头还是空仓
				self.total_volume=0.0
				self.total_volume_abs=0.0
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						self.total_volume=self.total_volume+HoldingAccount[optionname]
						self.total_volume_abs=self.total_volume_abs+np.abs(HoldingAccount[optionname])
				#每一天操作
				#self.VIXDailyTrade(dayIndicator,date)#波动率策略
				U_Strike=float(self.obj.loc[date,'close'])
				#self.BullCallDaily(date,U_Strike,100.0,'short')#牛市看涨策略,熊市看涨
				#self.BullPutDaily(date,U_Strike,100.0,'short')#牛市看跌策略，熊市看跌
				#self.Straddle(date,'short')#跨式突破，跨式盘整
				#self.Strangle(date,U_Strike,100.0,'short')
				#self.ButterflyCall(date,U_Strike,100.0,'short')#碟式价差，看涨
				self.ButterflyPut(date,U_Strike,100.0,'short')#碟式价差，看跌
				#判断每日“新开”的期权操作账户是否为空，若为空，删去。
				if self.OptionAccount[self.date]:
					pass
				else:
					del self.OptionAccount[self.date]

				self.MarginSumCal()
				self.EquityCal()
			else:
				pass
	def DataOutput(self):
		tp1=self.EquityAccountframe
		NetValue=tp1-self.InitialFundAccount
		NetValue=pd.DataFrame(np.matrix(NetValue),index=NetValue.index,columns=['NetValue'])
		tp2=self.FundAccountframe
		tp3=self.MarginAccountframe
		tp4=self.obj.loc[:,'close']
		tp5=self.obj.loc[:,'volume']
		temp=pd.concat([tp1,tp2,tp3,tp4],axis=1)
		res=pd.DataFrame(np.matrix(temp),index=temp.index,columns=['equity','fund','Margin','underlying'])
		#res.to_csv('test.csv')
		pd.concat([NetValue,tp4],axis=1).to_csv('SRtestN10n1.csv')


class MOptionBackTest(OptionBackTest):
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision,OptionType):
		OptionBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.OptionRootdir='C:/Users/fsd/OneDrive/Python/founder_future/MOption_Data_Processed/'
		self.MFutureRootdir='C:/Users/fsd/OneDrive/Python/founder_future/MFuture_Data_Processed/'#期货数据还未下
		self.IndicatorRootdir='C:/Users/fsd/Desktop/MOption.xlsm'
		self.OptionType=OptionType
		self.OptionList=os.listdir(self.OptionRootdir)
		self.Unit=10.0
		self.Commision=Commision
		self.dataImport()
		self.Strategy()
		self.IndicatorCalculate()
		self.DataOutput()
	def dataImport(self):
		#VIX指标导入
		temp=pd.read_excel(self.IndicatorRootdir,sheetname='VIX_oppor')[2:]
		#print temp
		tempindex=temp.iloc[:,0].values[1:]
		tempcols=temp.iloc[0,:][1:].values
		self.Indicator=pd.DataFrame(np.matrix(temp.iloc[1:,1:]),index=tempindex,columns=tempcols)
		#print self.Indicator
		#导入标的主连收盘成交量，无风险利率
		tmp=pd.read_excel(self.RCVRootdir,sheetname='M')[3:]
		indextemp=[]
		for i in tmp.index:
			date=str(i)[:10]
			indextemp.append(date)
		self.obj=pd.DataFrame(np.matrix(tmp),index=indextemp,columns=['close','volume']).loc[self.StartDate:self.EndDate]
	def DataImportDaily(self,option,date):
		#开仓用self.dataOpen数据，平仓用self.data数据
		self.data=pd.read_excel(self.OptionRootdir+option).sort_values(by=u'成交量',ascending=False)[[u'结算价',u'收盘价',u'成交量','ptmtradeday']]
		self.dataOpen=self.data[self.data.loc[:,'ptmtradeday']>7]
		#期货数据还未下载处理
		self.FutureData=pd.read_excel(self.MFutureRootdir+self.tempdate+'_M_Future.xls')
	def MarginCal(self,optionname):
		futurename=optionname[:5]
		StrikePrice=float(optionname[8:])
		FutureSettlePrice=float(self.FutureData.loc[futurename,u'结算价'])
		OptionSettlePrice=float(self.data.loc[optionname,u'结算价'])
		if optionname[6]=='C':
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(StrikePrice-FutureSettlePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		else:
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(FutureSettlePrice-StrikePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		Margin=max(tmp1,tmp2)
		return Margin

	def Strategy(self):
		OptionList=self.OptionList
		Indicator=self.Indicator
		self.daynum=0
		for option in OptionList:
			tempdate=option[:8]
			self.tempdate=tempdate
			date=tempdate[:4]+'-'+tempdate[4:6]+'-'+tempdate[6:8]
			date=str(date)
			self.date=date

			if date>=self.StartDate and date<=self.EndDate:
				#每日开盘前结算
				self.OptionAccount[self.date]={}
				self.OptionAccount[self.date]=collections.OrderedDict()
				self.OptionAccountRecord[self.date]={}
				self.OptionAccountRecord[self.date]=collections.OrderedDict()

				if self.daynum==0:
					self.FundAccount[self.date]=self.InitialFundAccount
					self.daynum=self.daynum+1
				else:
					self.FundAccount[self.date]=self.FundAccount[self.FundAccount.keys()[-1]]
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.MarginAccount[self.MarginAccount.keys()[-1]]
				#盘中操作，导入数据
				self.DataImportDaily(option,self.tempdate)

				#导入VIX指标
				dayIndicator=self.Indicator.loc[date]
				#先对到期合约进行平仓，再判断持有多头，空头还是空仓
				HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						if self.data.loc[optionname,'ptmtradeday']==1:
							self.ClosePositionPar(optionname)
				#判断是否持有多头，空头还是空仓
				self.total_volume=0.0
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						self.total_volume=self.total_volume+HoldingAccount[optionname]

				self.VIXDailyTrade(dayIndicator,date)

				if self.OptionAccount[self.date]:
					pass
				else:
					del self.OptionAccount[self.date]
				self.MarginSumCal()
				self.EquityCal()
			else:
				pass
	def DataOutput(self):
		tp1=self.EquityAccountframe
		NetValue=tp1-self.InitialFundAccount
		tp2=self.FundAccountframe
		tp3=self.MarginAccountframe
		tp4=self.obj.loc[:,'close']
		tp5=self.obj.loc[:,'volume']
		temp=pd.concat([tp1,tp2,tp3,tp4],axis=1)
		res=pd.DataFrame(np.matrix(temp),index=temp.index,columns=['equity','fund','Margin','underlying'])
		#res.to_csv('test.csv')
		pd.concat([self.Yield,tp4],axis=1).to_csv('Mtest.csv')


class ETFOptionBackTest(OptionBackTest):
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision,OptionType):
		OptionBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.OptionRootdir='C:/Users/fsd/OneDrive/Python/founder_future/ETFOption/'
		self.IndicatorRootdir='C:/Users/fsd/Desktop/ETFOption.xlsm'
		self.OptionType=OptionType
		self.OptionList=os.listdir(self.OptionRootdir)
		#self.Unit(optionname)=10000.0
		self.Commision=Commision
		self.dataImport()
		self.Strategy()
		self.IndicatorCalculate()
		self.DataOutput()
	def dataImport(self):
		#VIX指标导入
		temp=pd.read_excel(self.IndicatorRootdir,sheetname='VIX_oppor')[2:]
		#print temp
		tempindex=temp.iloc[:,0].values[1:]
		tempcols=temp.iloc[0,:][1:].values
		self.Indicator=pd.DataFrame(np.matrix(temp.iloc[1:,1:]),index=tempindex,columns=tempcols)
		#导入标的主连收盘成交量，无风险利率
		tmp=pd.read_excel(self.RCVRootdir,sheetname='50ETF')[3:]
		indextemp=[]
		for i in tmp.index:
			date=str(i)[:10]
			indextemp.append(date)
		temp=pd.DataFrame(np.matrix(tmp),index=indextemp,columns=['close','volume'])
		row1=len(temp.loc[:self.StartDate])
		row2=len(temp.loc[:self.EndDate])
		self.obj=temp.iloc[row1-2:row2]
	#开多头仓
	def LongPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=num
		self.OptionAccountRecord[self.date][optionname]=num

		self.FundAccount[self.date]=self.FundAccount[self.date]-self.data.loc[optionname,u'close']*num*self.Unit(optionname)
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		#print'long', self.date,self.OptionAccount[self.date]


	#开空头仓
	def ShortPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=-num
		self.OptionAccountRecord[self.date][optionname]=-num

		self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'close']*num*self.Unit(optionname)
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		#print 'short',self.date,self.OptionAccount[self.date]
	def ClosePositionAll(self):
		HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
		optionnames=HoldingAccount.keys()
		for optionname in optionnames:
			self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'close']*HoldingAccount[optionname]*self.Unit(optionname)
			#记录期权成交情况
			self.OptionAccountRecord[self.date][optionname]=0.0
			if HoldingAccount[optionname]>0:
				self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[optionname]
			else:
				self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[optionname]
		#print self.OptionAccount.keys()
		del self.OptionAccount[self.OptionAccount.keys()[0]]
		#print 'all',self.date,self.OptionAccount[self.date]
	def ClosePositionPar(self,optionname):
		num=self.OptionAccount[self.OptionAccount.keys()[0]][optionname]
		self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,'close']*num*self.Unit(optionname)
		if num>0:
			self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		else:
			self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*num
		#记录期权成交情况
		for opname in self.OptionAccount[self.OptionAccount.keys()[0]].keys():
			if opname==optionname:
				self.OptionAccountRecord[self.date][opname]=0.0
			else:
				self.OptionAccountRecord[self.date][opname]=self.OptionAccount[self.OptionAccount.keys()[0]][opname]

		del self.OptionAccount[self.OptionAccount.keys()[0]][optionname]

		if self.OptionAccount[self.OptionAccount.keys()[0]]:
			pass
		else:
			del self.OptionAccount[self.OptionAccount.keys()[0]]
		#print 'par',self.date,self.OptionAccount[self.date]
	def Unit(self,optionname):
		#2016.11.28
		optionname=str(optionname)
		obj=re.search(r'(月)([\d,\.,A]*)',optionname)
		temp=obj.group(2)
		if temp[-1]=='A' and self.date>='2016-11-28':
			return 10220.0
		else:
			return 10000.0
	#开仓保证金
	def OpenETFMarginCal(self,optionname):
		PreSettle=self.data.loc[optionname,'pre_settle']
		row=len(self.obj.loc[:self.date])
		ETFPreClose=self.obj.iloc[row-2,0]

		optionname=str(optionname)
		obj=re.search(r'(月)([\d,\.,A]*)',optionname)
		temp=obj.group(2)
		if temp[-1]=='A':
			StrikePrice=float(temp[:-1])
		else:
			StrikePrice=float(temp)

		if optionname[5]=='C':
			call_out_option=max(StrikePrice-ETFPreClose,0.0)
			OpenMargin=(PreSettle+Max(0.12*ETFPreClose-call_out_option,0.07*ETFPreClose))*self.Unit(optionname)
		else:
			put_out_option=max(ETFPreClose-StrikePrice,0.0)
			OpenMargin=min(PreSettle+max(0.12*ETFPreClose-put_out_option,0.07*StrikePrice),StrikePrice)*self.Unit(optionname)
		return OpenMargin
	#维持保证金
	def MaintainETFMarginCal(self,optionname):
		Settle=self.data.loc[optionname,'settlement_price']
		ETFClose=self.obj.loc[self.date,'close']
		#刚发行的期权前一交易日，没有前结算价，需从当天数据里导入
		PreSettle=self.data.loc[optionname,'pre_settle']
		row=len(self.obj.loc[:self.date])
		ETFPreClose=self.obj.iloc[row-2,0]

		optionname=str(optionname)
		obj=re.search(r'(月)([\d,\.,A]*)',optionname)
		temp=obj.group(2)
		if temp[-1]=='A':
			StrikePrice=float(temp[:-1])
		else:
			StrikePrice=float(temp)

		if optionname[5]=='C':
			call_out_option=max(StrikePrice-ETFPreClose,0.0)
			MainMargin=(Settle+Max(0.12*ETFClose-call_out_option,0.07*ETFPreClose))*self.Unit(optionname)
		else:
			put_out_option=max(ETFPreClose-StrikePrice,0.0)
			MainMargin=min(Settle+max(0.12*ETFClose-put_out_option,0.07*StrikePrice),StrikePrice)*self.Unit(optionname)
		return MainMargin
		
	def MarginSumCal(self):
		TempMargin=0.0
		if self.OptionAccount:
			HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
			if HoldingAccount:
				for optionname in HoldingAccount.keys():
					num=HoldingAccount[optionname]
					if num>0:
						pass
					else:
						TempMargin=TempMargin+self.MaintainETFMarginCal(optionname)*np.abs(num)
		self.MarginAccount[self.date]=TempMargin
		self.FundAccount[self.date]=self.FundAccount[self.date]-TempMargin
	def EquityCal(self):
		temp=self.FundAccount[self.date]+self.MarginAccount[self.date]
		if self.OptionAccount:
			HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
			optionnames=HoldingAccount.keys()
			for optionname in optionnames:
				temp=temp+self.data.loc[optionname,u'close']*HoldingAccount[optionname]*self.Unit(optionname)
		else:#
			#print 'No Options'
			pass
		self.EquityAccount[self.date]=temp
	def VIXDailyTrade(self,dayIndicator,date):
		Vix=dayIndicator.loc['VIX']
		MA=dayIndicator.loc['MA']
		MA_minus=dayIndicator.loc['MA-n*std']
		MA_plus=dayIndicator.loc['MA+n*std']
		if self.total_volume>0.0:
			if Vix>=MA:
				self.ClosePositionAll()
			if Vix>MA_plus:
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.MaintainETFMarginCal(optionname)
					num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
					if num>0:
						#self.ShortPosition(optionname,num)
						self.ShortPosition(optionname,1)
						if optionname[5]==u'购':
							optionname2=optionname[:5]+u'沽'+optionname[6:]
						else:
							optionname2=optionname[:5]+u'购'+optionname[6:]
							self.ShortPosition(optionname2,1)
		elif self.total_volume<0.0:#有空头仓
			if Vix<=MA:#平仓
				self.ClosePositionAll()
			if Vix<MA_minus:#Vix过小，开多头仓
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.data.loc[optionname,'close']*self.Unit(optionname)
					num=min(max(int(TradeCapital*1.0/len(options)/TradeCapitalUnit),0),50)
					if num>0.0:
						#self.LongPosition(optionname,num)
						self.LongPosition(optionname,1)
						if optionname[5]==u"购":
							optionname2=optionname[:5]+u"沽"+optionname[6:]
						else:
							optionname2=optionname[:5]+u"购"+optionname[6:]
						self.LongPosition(optionname2,1)
		else:
			if Vix>MA_plus:#开空头仓,合约到期时间要大于7个交易日
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.MaintainETFMarginCal(optionname)#卖一手期权所需缴纳的保证金
					num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
					if num>0.0:
						#self.ShortPosition(optionname,num)
						self.ShortPosition(optionname,1)
						if optionname[5]==u"购":
							optionname2=optionname[:5]+u"沽"+optionname[6:]
						else:
							optionname2=optionname[:5]+u"购"+optionname[6:]
						self.ShortPosition(optionname2,1)
			elif Vix<MA_minus:
				TradeCapital=self.FundAccount[date]*0.3
				options=self.dataOpen.index[:1]
				for optionname in options:
					TradeCapitalUnit=self.data.loc[optionname,'close']*self.Unit(optionname)
					num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
					if num>0.0:
						#self.LongPosition(optionname,num)
						self.LongPosition(optionname,1)
						if optionname[5]==u"购":
							optionname2=optionname[:5]+u"沽"+optionname[6:]
						else:
							optionname2=optionname[:5]+u"购"+optionname[6:]
						self.LongPosition(optionname2,1)
			else:
				pass
	#牛市价差策略
	def BullDaily(self,date,LongShortType,Call_Put):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			optionname=str(optionname)
			obj=re.search(r'(.*月)([\d,\.,A]*)',optionname)
			temp=obj.group(2)
			DeliverDay=unicode(obj.group(1))[6:]
			#print temp
			diff_Strike_list=[]
			if temp[-1]=='A':
				Strike=float(temp[:-1])
				for op in self.dataOpen.index[1:10]:
					if op[-1]=='A':
						op=str(op)
						obj_temp=re.search(r'(.*月)([\d,\.]*)',op)
						if DeliverDay==unicode(obj_temp.group(1))[6:]:
							if float(obj_temp.group(2))!=Strike:
								diff_Strike_list.append(float(obj_temp.group(2))-Strike)
					else:
						pass
				num=np.argmin(np.abs(diff_Strike_list))#选取与成交量最大的期权之间执行间距最小的期权
				Strike_temp=diff_Strike_list[num]+Strike
			else:
				Strike=float(temp)
				#print Strike
				for op in self.dataOpen.index[1:10]:
					#print op
					if op[-1]!='A':
						op=str(op)
						obj_temp=re.search(r'(.*月)([\d,\.]*)',op)
						if DeliverDay==unicode(obj_temp.group(1))[6:]:
							if float(obj_temp.group(2))!=Strike:
								print '1'
								diff_Strike_list.append(float(obj_temp.group(2))-Strike)
					else:
						pass
				num=np.argmin(np.abs(diff_Strike_list))
				Strike_temp=diff_Strike_list[num]+Strike

			if Strike<Strike_temp:
				Strike_1=Strike
				Strike_2=Strike_temp
			else:
				Strike_1=Strike_temp
				Strike_2=Strike
			if temp[-1]=='A':
				Option_1=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.3f'%round(Strike_1,3)))+'A'
				Option_2=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.3f'%round(Strike_2,3)))+'A'
			else:
				Option_1=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.2f'%round(Strike_1,2)))
				Option_2=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.2f'%round(Strike_2,2)))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.ShortPosition(Option_2,1)
			else:
				self.ShortPosition(Option_1,1)
				self.LongPosition(Option_2,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def Straddle(self,date,LongShortType):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			optionname=str(optionname)
			obj=re.search(r'(.*月)([\d,\.,A]*)',optionname)
			#temp=obj.group(2)
			#DeliverDay=unicode(obj.group(1))[6:]
			#print temp

			Option_1=unicode(obj.group(1))[:5]+u'购'+unicode(obj.group(1))[6:]+unicode(obj.group(2))
			Option_2=unicode(obj.group(1))[:5]+u'沽'+unicode(obj.group(1))[6:]+unicode(obj.group(2))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.LongPosition(Option_2,1)
			else:
				self.ShortPosition(Option_1,1)
				self.ShortPosition(Option_2,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def Strangle(self,date,LongShortType):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			optionname=str(optionname)
			obj=re.search(r'(.*月)([\d,\.,A]*)',optionname)
			temp=obj.group(2)
			DeliverDay=unicode(obj.group(1))[6:]
			#print temp
			diff_Strike_list=[]
			if temp[-1]=='A':
				Strike=float(temp[:-1])
				for op in self.dataOpen.index[1:10]:
					if op[-1]=='A':
						op=str(op)
						obj_temp=re.search(r'(.*月)([\d,\.]*)',op)
						if DeliverDay==unicode(obj_temp.group(1))[6:]:
							if float(obj_temp.group(2))!=Strike:
								diff_Strike_list.append(float(obj_temp.group(2))-Strike)
					else:
						pass
				num=np.argmin(np.abs(diff_Strike_list))#选取与成交量最大的期权之间执行间距最小的期权
				Strike_temp=diff_Strike_list[num]+Strike
			else:
				Strike=float(temp)
				#print Strike
				for op in self.dataOpen.index[1:10]:
					#print op
					if op[-1]!='A':
						op=str(op)
						obj_temp=re.search(r'(.*月)([\d,\.]*)',op)
						if DeliverDay==unicode(obj_temp.group(1))[6:]:
							if float(obj_temp.group(2))!=Strike:
								print '1'
								diff_Strike_list.append(float(obj_temp.group(2))-Strike)
					else:
						pass
				num=np.argmin(np.abs(diff_Strike_list))
				Strike_temp=diff_Strike_list[num]+Strike

			if Strike<Strike_temp:
				Strike_1=Strike
				Strike_2=Strike_temp
			else:
				Strike_1=Strike_temp
				Strike_2=Strike
			if temp[-1]=='A':
				Option_1=unicode(obj.group(1))[:5]+u'沽'+unicode(obj.group(1))[6:]+unicode(str('%.3f'%round(Strike_1,3)))+'A'
				Option_2=unicode(obj.group(1))[:5]+u'购'+unicode(obj.group(1))[6:]+unicode(str('%.3f'%round(Strike_2,3)))+'A'
			else:
				Option_1=unicode(obj.group(1))[:5]+u'沽'+unicode(obj.group(1))[6:]+unicode(str('%.2f'%round(Strike_1,2)))
				Option_2=unicode(obj.group(1))[:5]+u'购'+unicode(obj.group(1))[6:]+unicode(str('%.2f'%round(Strike_2,2)))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.LongPosition(Option_2,1)
			else:
				self.ShortPosition(Option_1,1)
				self.ShortPosition(Option_2,1)
			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass
	def Butterfly(self,date,LongShortType,Call_Put):
		WeekDay=datetime.strptime(date,'%Y-%m-%d').weekday()+1
		print self.total_volume_abs
		if self.total_volume_abs==0 and WeekDay==1:
			optionname=self.dataOpen.index[:1][0]
			optionname=str(optionname)
			obj=re.search(r'(.*月)([\d,\.,A]*)',optionname)
			temp=obj.group(2)
			DeliverDay=unicode(obj.group(1))[6:]
			#print temp
			diff_Strike_list=[]
			if temp[-1]=='A':
				Strike=float(temp[:-1])
				for op in self.dataOpen.index[1:10]:
					if op[-1]=='A':
						op=str(op)
						obj_temp=re.search(r'(.*月)([\d,\.]*)',op)
						if DeliverDay==unicode(obj_temp.group(1))[6:]:
							if float(obj_temp.group(2))!=Strike:
								diff_Strike_list.append(float(obj_temp.group(2))-Strike)
					else:
						pass
			else:
				Strike=float(temp)
				#print Strike
				for op in self.dataOpen.index[1:10]:
					#print op
					if op[-1]!='A':
						op=str(op)
						obj_temp=re.search(r'(.*月)([\d,\.]*)',op)
						if DeliverDay==unicode(obj_temp.group(1))[6:]:
							if float(obj_temp.group(2))!=Strike:
								print '1'
								diff_Strike_list.append(float(obj_temp.group(2))-Strike)
					else:
						pass
			diff_Strike_list.sort()
			
			plus=[i for i in diff_Strike_list if i>0]
			minus=[i for i in diff_Strike_list if i<0]
			try:
				Strike_1=minus[-1]+Strike
				Strike_2=Strike
				Strike_3=plus[0]+Strike
			except:
				try:
					Strike_1=Strike
					Strike_2=plus[0]+Strike
					Strike_3=plus[1]+Strike
				except:
					Strike_1=minus[-2]+Strike
					Strike_2=minus[-1]+Strike
					Strike_3=Strike

			if temp[-1]=='A':
				Option_1=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.3f'%round(Strike_1,3)))+'A'
				Option_2=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.3f'%round(Strike_2,3)))+'A'
				Option_3=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.3f'%round(Strike_3,3)))+'A'
			else:
				Option_1=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.2f'%round(Strike_1,2)))
				Option_2=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.2f'%round(Strike_2,2)))
				Option_3=unicode(obj.group(1))[:5]+Call_Put+unicode(obj.group(1))[6:]+unicode(str('%.2f'%round(Strike_3,2)))
			if LongShortType=='long':
				self.LongPosition(Option_1,1)
				self.ShortPosition(Option_2,2)
				self.LongPosition(Option_3,1)
			else:
				self.ShortPosition(Option_1,1)
				self.LongPosition(Option_2,2)
				self.ShortPosition(Option_3,1)

			print self.date,u'开仓',self.OptionAccount
		elif self.total_volume_abs>0 and WeekDay==5:
			print u'平仓'
			self.ClosePositionAll()
		else:
			pass

	def Strategy(self):
		OptionList=self.OptionList
		Indicator=self.Indicator
		self.daynum=0
		for numlist,option in enumerate(OptionList):
			tempdate=option[:10]
			date=str(tempdate)
			self.date=date
			#print date
			print date,self.OptionAccount
			if date>=self.StartDate and date<=self.EndDate:
				#每日开盘前结算
				self.OptionAccount[self.date]={}
				self.OptionAccount[self.date]=collections.OrderedDict()
				self.OptionAccountRecord[self.date]={}
				self.OptionAccountRecord[self.date]=collections.OrderedDict()

				if self.daynum==0:
					self.FundAccount[self.date]=self.InitialFundAccount
					self.daynum=self.daynum+1
				else:
					self.FundAccount[self.date]=self.FundAccount[self.FundAccount.keys()[-1]]
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.MarginAccount[self.MarginAccount.keys()[-1]]

				#盘中操作，导入数据
				#开仓用self.dataOpen数据，平仓用self.data数据
				self.data=pd.read_excel(self.OptionRootdir+option).sort_values(by=u'volume',ascending=False)[['option_name','pre_settle','settlement_price','close','volume','ptmtradeday']]
				self.dataOpen=self.data[self.data.loc[:,'ptmtradeday']>7]
				self.data=IndexChange(self.data,'option_name')
				self.dataOpen=IndexChange(self.dataOpen,'option_name')
				#前一交易日数据

				#导入VIX指标
				#dayIndicator=self.Indicator.loc[date]
				#print dayIndicator

				#先对到期合约进行平仓，再判断持有多头，空头还是空仓
				HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
				#print self.OptionAccount.keys(),HoldingAccount
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						if self.data.loc[optionname,'ptmtradeday']==1:
							self.ClosePositionPar(optionname)
				#判断是否持有多头，空头还是空仓
				self.total_volume=0.0
				self.total_volume_abs=0.0
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						self.total_volume=self.total_volume+HoldingAccount[optionname]
						self.total_volume_abs=self.total_volume_abs+np.abs(HoldingAccount[optionname])
				#print self.date,total_volume
				#U_Strike=float(self.obj.loc[date,'close'])
				#self.VIXDailyTrade(dayIndicator,date)
				#self.BullDaily(date,'long',u'沽')#牛熊市价差策略,购为牛市差价，沽为熊市差价，long(short)表示买入(卖出)该策略，即看涨(看跌)策略。
				#self.Straddle(date,'short')#long 跨市突破 short 跨式盘整
				#self.Strangle(date,'short')#long 宽跨式突破，short宽跨式盘整
				self.Butterfly(date,'long',u'沽')#蝶式牛熊价差，购蝶式看涨，沽为蝶式看跌，long(short)表示买入(卖出)该策略，即看涨(看跌)策略。
				
				if self.OptionAccount[self.date]:
					pass
				else:
					del self.OptionAccount[self.date]
				#print self.OptionAccount
				self.MarginSumCal()
				self.EquityCal()
			else:
				pass
	def IndicatorCalculate(self):
		self.EquityAccountframe=pd.DataFrame.from_dict(self.EquityAccount, orient='index')
		self.FundAccountframe=pd.DataFrame.from_dict(self.FundAccount, orient='index')
		self.MarginAccountframe=pd.DataFrame.from_dict(self.MarginAccount, orient='index')
		#self.OptionAccountRecordframe=pd.DataFrame.from_dict(self.OptionAccountRecord,orient='index')
		for i in self.OptionAccountRecord.keys():
			print i,self.OptionAccountRecord[i]
		#收益率计算
		#print self.EquityAccountframe
		TempYield=(self.EquityAccountframe-self.InitialFundAccount)/self.InitialFundAccount
		#print TempYield
		self.Yield=pd.DataFrame(np.matrix(TempYield),index=TempYield.index,columns=['Yield'])
		#最大回撤计算retracement
		data=self.Yield.loc[:,'Yield'].values
		index_j = np.argmax(np.maximum.accumulate(data) - data)  # 结束位置
		index_i = np.argmax(data[:index_j])  # 开始位置
		self.Max_Retracement= (data[index_j] - data[index_i])/data[index_i]  # 最大回撤
	def DataOutput(self):
		tp1=self.EquityAccountframe
		NetValue=tp1-self.InitialFundAccount
		NetValue=pd.DataFrame(np.matrix(NetValue),index=tp1.index,columns=['NetValue'])
		tp2=self.FundAccountframe
		tp3=self.MarginAccountframe
		tp4=self.obj.loc[:,'close']
		tp5=self.obj.loc[:,'volume']
		temp=pd.concat([tp1,tp2,tp3,tp4],axis=1)
		res=pd.DataFrame(np.matrix(temp),index=temp.index,columns=['equity','fund','Margin','underlying'])
		#res.to_csv('test.csv')
		pd.concat([NetValue,tp4],axis=1).to_csv('ETFtest.csv')

#商品期权
StartDate='2015-02-10'
EndDate='2018-08-17'
InitialFundAccount=1000000.0
Commision=0.0
ETFOptionBackTest(StartDate,EndDate,InitialFundAccount,Commision,'ETF')