#!/usr/bin/python
# -*- coding: UTF-8 -*-
from fengshidian import *
import numpy as np
import pandas as pd
import collections
import re
import os

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

class SROptionBackTest(OptionBackTest):
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision):
		OptionBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.OptionRootdir='C:/Users/fsd/OneDrive/Python/founder_future/SOption_Data_Processed/'
		self.SRFutureRootdir='C:/Users/fsd/OneDrive/Python/founder_future/SRFuture_Data_Processed/'
		self.IndicatorRootdir='C:/Users/fsd/Desktop/SROption.xlsm'
		self.OptionList=os.listdir(self.OptionRootdir)
		self.Unit=10.0
		self.Commision=Commision
		self.dataImport()
		self.VIXStr()
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
	#开多头仓
	def LongPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=num
		self.OptionAccountRecord[self.date][optionname]=num
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.data.loc[optionname,u'今收盘']*num*self.Unit
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		#print self.date,self.OptionAccount[self.date]

	#开空头仓
	def ShortPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=-num
		self.OptionAccountRecord[self.date][optionname]=-num
		self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'今收盘']*num*self.Unit
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		#print self.date,self.OptionAccount[self.date]

	def ClosePositionAll(self):
		HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
		optionnames=HoldingAccount.keys()
		for optionname in optionnames:
			self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'今收盘']*HoldingAccount[optionname]*self.Unit
			self.OptionAccountRecord[self.date][optionname]=0.0
			if HoldingAccount[optionname]>0:
				self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[optionname]
			else:
				self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[optionname]
		del self.OptionAccount[self.OptionAccount.keys()[0]]
		#print self.date,self.OptionAccount[self.date]

	def ClosePositionPar(self,optionname):
		num=self.OptionAccount[self.OptionAccount.keys()[0]][optionname]
		self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'今收盘']*num*self.Unit
		if num>0:
			self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		else:
			self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*num

		for opname in self.OptionAccount[self.OptionAccount.keys()[0]].keys():
			if opname==optionname:
				self.OptionAccountRecord[self.date][opname]=0.0
			else:
				self.OptionAccountRecord[self.date][opname]=self.OptionAccount[self.OptionAccount.keys()[0]][opname]

		del self.OptionAcccount[self.OptionAccount.keys()[0]][optionname]
		#print self.date,self.OptionAccount[self.date]
		if self.OptionAccount[self.OptionAccount.keys()[0]]:
			pass
		else:
			del self.OptionAccount[self.OptionAccount.keys()[0]]

	def SRMarginCal(self,optionname):
		futurename=optionname[:5]
		OptionType=optionname[5]
		StrikePrice=float(optionname[6:10])
		FutureSettlePrice=float(self.FutureData.loc[futurename,u'今结算'])
		OptionSettlePrice=float(self.data.loc[optionname,u'今结算'])
		if OptionType=='C':
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(StrikePrice-FutureSettlePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		else:
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(FutureSettlePrice-StrikePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		Margin=max(tmp1,tmp2)
		return Margin

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
						TempMargin=TempMargin+self.SRMarginCal(optionname)*np.abs(num)
		self.MarginAccount[self.date]=TempMargin
		self.FundAccount[self.date]=self.FundAccount[self.date]-TempMargin
	def EquityCal(self):
		temp=self.FundAccount[self.date]+self.MarginAccount[self.date]
		if self.OptionAccount:
			HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
			optionnames=HoldingAccount.keys()
			for optionname in optionnames:
				temp=temp+self.data.loc[optionname,u'今收盘']*HoldingAccount[optionname]*self.Unit
		else:#
			#print 'No Options'
			pass
		self.EquityAccount[self.date]=temp
	def VIXStr(self):
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
				else:
					self.FundAccount[self.date]=self.FundAccount[self.FundAccount.keys()[-1]]
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.MarginAccount[self.MarginAccount.keys()[-1]]

				self.daynum=self.daynum+1
				#盘中操作，导入数据
				#开仓用self.dataOpen数据，平仓用self.data数据
				self.data=pd.read_excel(self.OptionRootdir+option).sort_values(by=u'成交量(手)',ascending=False)[[u'今结算',u'今收盘',u'成交量(手)','ptmtradeday']]
				self.dataOpen=self.data[self.data.loc[:,'ptmtradeday']>7]
				self.FutureData=pd.read_excel(self.SRFutureRootdir+self.tempdate+'_SR_Future.xls')

				#导入VIX指标
				dayIndicator=self.Indicator.loc[date]
				#print dayIndicator
				Vix=dayIndicator.loc['VIX']
				MA=dayIndicator.loc['MA']
				MA_minus=dayIndicator.loc['MA-n*std']
				MA_plus=dayIndicator.loc['MA+n*std']

				#先对到期合约进行平仓，再判断持有多头，空头还是空仓
				HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						if self.data.loc[optionname,'ptmtradeday']==1:
							self.ClosePositionPar(optionname)
				#判断是否持有多头，空头还是空仓
				total_volume=0.0
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						total_volume=total_volume+HoldingAccount[optionname]

				if total_volume>0:
					if Vix>=MA:
						self.ClosePositionAll()
					if Vix>MA_plus:
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.SRMarginCal(optionname)
							num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.ShortPosition(optionname,num)
								self.ShortPosition(optionname,1)
								if optionname[5]=='C':
									optionname2=optionname[:5]+'P'+optionname[6:]
								else:
									optionname2=optionname[:5]+'C'+optionname[6:]
								self.ShortPosition(optionname2,1)
				elif total_volume<0:#有空头仓
					if Vix<=MA:#平仓
						self.ClosePositionAll()
					if Vix<MA_minus:#Vix过小，开多头仓
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.data.loc[optionname,u'今收盘']*self.Unit
							num=min(max(int(TradeCapital*1.0/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.LongPosition(optionname,num)
								self.LongPosition(optionname,1)
								if optionname[5]=="C":
									optionname2=optionname[:5]+"P"+optionname[6:]
								else:
									optionname2=optionname[:5]+"C"+optionname[6:]
								self.LongPosition(optionname2,1)
				else:
					if Vix>MA_plus:#开空头仓,合约到期时间要大于7个交易日
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.SRMarginCal(optionname)#卖一手期权所需缴纳的保证金
							num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.ShortPosition(optionname,num)
								self.ShortPosition(optionname,1)
								if optionname[5]=="C":
									optionname2=optionname[:5]+"P"+optionname[6:]
								else:
									optionname2=optionname[:5]+"C"+optionname[6:]
								self.ShortPosition(optionname2,1)
					elif Vix<MA_minus:
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.data.loc[optionname,u'今收盘']*self.Unit
							num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.LongPosition(optionname,num)
								self.LongPosition(optionname,1)
								if optionname[5]=="C":
									optionname2=optionname[:5]+"P"+optionname[6:]
								else:
									optionname2=optionname[:5]+"C"+optionname[6:]
								self.LongPosition(optionname2,1)
					else:
						pass

				if self.OptionAccount[self.date]:
					pass
				else:
					del self.OptionAccount[self.date]

				self.MarginSumCal()
				self.EquityCal()
			else:
				pass
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
		self.Max_Retracement= (data[index_j] - data[index_i])/data[index_i]  # 最大回撤
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
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision):
		OptionBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.OptionRootdir='C:/Users/fsd/OneDrive/Python/founder_future/MOption_Data_Processed/'
		self.MFutureRootdir='C:/Users/fsd/OneDrive/Python/founder_future/MFuture_Data_Processed/'#期货数据还未下
		self.IndicatorRootdir='C:/Users/fsd/Desktop/MOption.xlsm'
		self.OptionList=os.listdir(self.OptionRootdir)
		self.Unit=10.0
		self.Commision=Commision
		self.dataImport()
		self.VIXStr()
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
	#开多头仓
	def LongPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=num
		self.OptionAccountRecord[self.date][optionname]=num
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.data.loc[optionname,u'收盘价']*num*self.Unit
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num


	#开空头仓
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

		del self.OptionAcccount[self.OptionAccount.keys()[0]][optionname]
		if self.OptionAccount[self.OptionAccount.keys()[0]]:
			pass
		else:
			del self.OptionAccount[self.OptionAccount.keys()[0]]
	#豆粕保证金需重新编辑下
	def MMarginCal(self,optionname):
		futurename=optionname[:5]
		OptionType=optionname[6]
		StrikePrice=float(optionname[8:])
		FutureSettlePrice=float(self.FutureData.loc[futurename,u'结算价'])
		OptionSettlePrice=float(self.data.loc[optionname,u'结算价'])
		if OptionType=='C':
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(StrikePrice-FutureSettlePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		else:
			tmp1=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit-max(FutureSettlePrice-StrikePrice,0.0)*self.Unit
			tmp2=OptionSettlePrice*self.Unit+FutureSettlePrice*0.06*self.Unit*0.5
		Margin=max(tmp1,tmp2)
		return Margin

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
						TempMargin=TempMargin+self.MMarginCal(optionname)*np.abs(num)
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
	def VIXStr(self):
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
				else:
					self.FundAccount[self.date]=self.FundAccount[self.FundAccount.keys()[-1]]
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.MarginAccount[self.MarginAccount.keys()[-1]]

				self.daynum=self.daynum+1
				#盘中操作，导入数据
				#开仓用self.dataOpen数据，平仓用self.data数据
				self.data=pd.read_excel(self.OptionRootdir+option).sort_values(by=u'成交量',ascending=False)[[u'结算价',u'收盘价',u'成交量','ptmtradeday']]
				self.dataOpen=self.data[self.data.loc[:,'ptmtradeday']>7]
				#期货数据还未下载处理
				self.FutureData=pd.read_excel(self.MFutureRootdir+self.tempdate+'_M_Future.xls')

				#导入VIX指标
				dayIndicator=self.Indicator.loc[date]
				#print dayIndicator
				Vix=dayIndicator.loc['VIX']
				MA=dayIndicator.loc['MA']
				MA_minus=dayIndicator.loc['MA-n*std']
				MA_plus=dayIndicator.loc['MA+n*std']

				#先对到期合约进行平仓，再判断持有多头，空头还是空仓
				HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						if self.data.loc[optionname,'ptmtradeday']==1:
							self.ClosePositionPar(optionname)
				#判断是否持有多头，空头还是空仓
				total_volume=0.0
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						total_volume=total_volume+HoldingAccount[optionname]

				if total_volume>0:
					if Vix>=MA:
						self.ClosePositionAll()
					if Vix>MA_plus:
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.MMarginCal(optionname)
							num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.ShortPosition(optionname,num)
								self.ShortPosition(optionname,1)
								if optionname[6]=='C':
									optionname2=optionname[:6]+'P'+optionname[7:]
								else:
									optionname2=optionname[:6]+'C'+optionname[7:]
								self.ShortPosition(optionname2,1)
				elif total_volume<0:#有空头仓
					if Vix<=MA:#平仓
						self.ClosePositionAll()
					if Vix<MA_minus:#Vix过小，开多头仓
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.data.loc[optionname,u'收盘价']*self.Unit
							num=min(max(int(TradeCapital*1.0/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.LongPosition(optionname,num)
								self.LongPosition(optionname,1)
								if optionname[6]=="C":
									optionname2=optionname[:6]+"P"+optionname[7:]
								else:
									optionname2=optionname[:6]+"C"+optionname[7:]
								self.LongPosition(optionname2,1)
				else:
					if Vix>MA_plus:#开空头仓,合约到期时间要大于7个交易日
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.MMarginCal(optionname)#卖一手期权所需缴纳的保证金
							num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.ShortPosition(optionname,num)
								self.ShortPosition(optionname,1)
								if optionname[6]=="C":
									optionname2=optionname[:6]+"P"+optionname[7:]
								else:
									optionname2=optionname[:6]+"C"+optionname[7:]
								self.ShortPosition(optionname2,1)
					elif Vix<MA_minus:
						TradeCapital=self.FundAccount[self.date]*0.3
						options=self.dataOpen.index[:1]
						for optionname in options:
							TradeCapitalUnit=self.data.loc[optionname,u'收盘价']*self.Unit
							num=min(max(int(TradeCapital*0.99/len(options)/TradeCapitalUnit),0),50)
							if num>0:
								#self.LongPosition(optionname,num)
								self.LongPosition(optionname,1)
								if optionname[6]=="C":
									optionname2=optionname[:6]+"P"+optionname[7:]
								else:
									optionname2=optionname[:6]+"C"+optionname[7:]
								self.LongPosition(optionname2,1)
					else:
						pass

				if self.OptionAccount[self.date]:
					pass
				else:
					del self.OptionAccount[self.date]

				self.MarginSumCal()
				self.EquityCal()
			else:
				pass
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
		self.Max_Retracement= (data[index_j] - data[index_i])/data[index_i]  # 最大回撤
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
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision):
		OptionBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.OptionRootdir='C:/Users/fsd/OneDrive/Python/founder_future/ETFOption/'

		self.IndicatorRootdir='C:/Users/fsd/Desktop/ETFOption.xlsm'
		self.OptionList=os.listdir(self.OptionRootdir)
		#self.Unit(optionname)=10000.0
		self.Commision=Commision
		self.dataImport()
		self.VIXStr()
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
		print'long', self.date,self.OptionAccount[self.date]


	#开空头仓
	def ShortPosition(self,optionname,num):
		self.OptionAccount[self.date][optionname]=-num
		self.OptionAccountRecord[self.date][optionname]=-num

		self.FundAccount[self.date]=self.FundAccount[self.date]+self.data.loc[optionname,u'close']*num*self.Unit(optionname)
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
		print 'short',self.date,self.OptionAccount[self.date]
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
		print 'all',self.date,self.OptionAccount[self.date]
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
		print 'par',self.date,self.OptionAccount[self.date]
	def Unit(self,optionname):
		#2016.11.28
		optionname=str(optionname)
		obj=re.search(r'(月)([\d,\.]*)',optionname)
		temp=obj.group(2)
		if temp[-1]=='A' and self.date>='2016-11-28':
			return 10220.0
		else:
			return 10000.0
	#豆粕保证金需重新编辑下
	def OpenETFMarginCal(self,optionname):
		PreSettle=self.data.loc[optionname,'pre_settle']
		row=len(self.obj.loc[:self.date])
		ETFPreClose=self.obj.iloc[row-2,0]
		
		OptionType=optionname[5]
		optionname=str(optionname)
		obj=re.search(r'(月)([\d,\.]*)',optionname)
		temp=obj.group(2)
		if temp[-1]=='A':
			StrikePrice=float(temp[:-1])
		else:
			StrikePrice=float(temp)

		if OptionType=='C':
			call_out_option=max(StrikePrice-ETFPreClose,0.0)
			OpenMargin=(PreSettle+Max(0.12*ETFPreClose-call_out_option,0.07*ETFPreClose))*self.Unit(optionname)
		else:
			put_out_option=max(ETFPreClose-StrikePrice,0.0)
			OpenMargin=min(PreSettle+max(0.12*ETFPreClose-put_out_option,0.07*StrikePrice),StrikePrice)*self.Unit(optionname)
		return OpenMargin

	def MaintainETFMarginCal(self,optionname):
		Settle=self.data.loc[optionname,'settlement_price']
		ETFClose=self.obj.loc[self.date,'close']
		#刚发行的期权前一交易日，没有前结算价，需从当天数据里导入
		PreSettle=self.data.loc[optionname,'pre_settle']
		row=len(self.obj.loc[:self.date])
		ETFPreClose=self.obj.iloc[row-2,0]

		OptionType=optionname[5]
		optionname=str(optionname)
		obj=re.search(r'(月)([\d,\.]*)',optionname)
		temp=obj.group(2)
		if temp[-1]=='A':
			StrikePrice=float(temp[:-1])
		else:
			StrikePrice=float(temp)

		if OptionType=='C':
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
	def VIXStr(self):
		OptionList=self.OptionList
		Indicator=self.Indicator
		self.daynum=0
		for numlist,option in enumerate(OptionList):
			tempdate=option[:10]
			date=str(tempdate)
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
				else:
					self.FundAccount[self.date]=self.FundAccount[self.FundAccount.keys()[-1]]
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.MarginAccount[self.MarginAccount.keys()[-1]]

				self.daynum=self.daynum+1
				#盘中操作，导入数据
				#开仓用self.dataOpen数据，平仓用self.data数据
				self.data=pd.read_excel(self.OptionRootdir+option).sort_values(by=u'volume',ascending=False)[['option_name','pre_settle','settlement_price','close','volume','ptmtradeday']]
				self.dataOpen=self.data[self.data.loc[:,'ptmtradeday']>7]
				self.data=IndexChange(self.data,'option_name')
				self.dataOpen=IndexChange(self.dataOpen,'option_name')
				#前一交易日数据
				

				#导入VIX指标
				dayIndicator=self.Indicator.loc[date]
				#print dayIndicator
				Vix=dayIndicator.loc['VIX']
				MA=dayIndicator.loc['MA']
				MA_minus=dayIndicator.loc['MA-n*std']
				MA_plus=dayIndicator.loc['MA+n*std']

				#先对到期合约进行平仓，再判断持有多头，空头还是空仓
				HoldingAccount=self.OptionAccount[self.OptionAccount.keys()[0]]
				#print self.OptionAccount.keys(),HoldingAccount
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						if self.data.loc[optionname,'ptmtradeday']==1:
							self.ClosePositionPar(optionname)
				#判断是否持有多头，空头还是空仓
				total_volume=0.0
				if HoldingAccount:
					for optionname in HoldingAccount.keys():
						total_volume=total_volume+HoldingAccount[optionname]
				#print self.date,total_volume

				if total_volume>0.0:
					if Vix>=MA:
						self.ClosePositionAll()
					if Vix>MA_plus:
						TradeCapital=self.FundAccount[self.date]*0.3
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
				elif total_volume<0.0:#有空头仓
					if Vix<=MA:#平仓
						self.ClosePositionAll()
					if Vix<MA_minus:#Vix过小，开多头仓
						TradeCapital=self.FundAccount[self.date]*0.3
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
						TradeCapital=self.FundAccount[self.date]*0.3
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
						TradeCapital=self.FundAccount[self.date]*0.3
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

#StartDate,EndDate,InitialFundAccount,Commision
StartDate='2017-03-31'
EndDate='2018-07-23'
InitialFundAccount=1000000.0
Commision=6.0
MOptionBackTest(StartDate,EndDate,InitialFundAccount,Commision)