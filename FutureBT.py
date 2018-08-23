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
		self.FutureAccount={}
		self.FutureAccount=collections.orderedDict()

		self.FutureAccountRecord={}
		self.FutureAccountRecord=collections.orderedDict()

		self.FundAccount={}
		self.FundAccount=collections.orderedDict()
		self.MarginAccount={}
		self.MarginAccount=collections.orderedDict()
		self.EquityAccount={}
		self.EquityAccount=collections.orderedDict()

	def LongPosition(self,futurename,num):
		self.FutureAccount[self.date][futurename]=num
		self.FutureAccountRecord[self.date][futurename]=num
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
	def ShortPosition(self,futurename,num):
		self.FutureAccount[self.date][futurename]=-num
		self.FutureAccountRecord[self.date][futurename]=-num
		self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*num
	#平全部仓位
	def ClosePositionAll(self):
		NumDate=len(self.FutureAccount.keys())
		for i in range(NumDate):
			HoldingAccount=self.FutureAccount[self.FutureAccount.keys()[i]]
			futurenames=HoldingAccount.keys()
			for futurename in futurenames:
				self.FutureAccountRecord[self.date][futurename]=0.0
				if HoldingAccount[futurename]>0:
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
				else:
					self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[futurename]
		dates=self.FutureAccount.keys()
		for date in dates:
			del self.FutureAccount[date]
	#平某一交易日的仓位
	def ClosePositionDaily(self,date):
		HoldingAccount=self.FutureAccount[date]
		futurenames=HoldingAccount.keys()
		for futurename in futurenames:
			self.FutureAccountRecord[self.date][futurename]=0.0
			if HoldingAccount[futurename]>0:
				self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
			else:
				self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[futurename]
		del self.FutureAccount[date]

	def ClosePositionPar(self,date,futurename,*args):
		#平某一期货全部仓位
		HoldingAccount=self.FutureAccount[date]
		if len(*args)==0:
			self.FutureAccountRecord[self.date][futurename]=0.0
			if HoldingAccount[futurename]>0:
				self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
			else:
				self.FundAccount[self.date]=self.FundAccount[self.date]+self.Commision*HoldingAccount[futurename]
			del self.FutureAccount[date][futurename]
		#平某一期货部分仓位
		elif len(*args)==1:
			numPosition=args[0]
			if HoldingAccount[futurename]>0:#平多头仓
				tempPosition=HoldingAccount[futurename]-numPosition
				if tempPosition>=0:
					self.FutureAccount[date][futurename]=tempPosition
					self.FutureAccountRecord[self.date][futurename]=tempPosition
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*numPosition
				else:
					self.FutureAccount[date][futurename]=0.0
					self.FutureAccountRecord[self.date][futurename]=0.0
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*HoldingAccount[futurename]
					print u'平仓量多于持仓量，只平所持头寸的仓位'
			else:#平空头仓
				tempPosition=HoldingAccount[futurename]+numPosition
				if tempPosition<=0:
					self.FutureAccount[date][futurename]=tempPosition
					self.FutureAccountRecord[self.date][futurename]=tempPosition
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*numPosition
				else:
					self.FutureAccount[date][futurename]=0.0
					self.FutureAccountRecord[self.date][futurename]=0.0
					self.FundAccount[self.date]=self.FundAccount[self.date]-self.Commision*np.abs(HoldingAccount[futurename])
					print u'平仓量多于持仓量，只平所持头寸的仓位'
		else:
			print u'参数过多，终止程序！'
			exit()


class SQSFutureBackTest(FutureBackTest):
	def __init__(self,StartDate,EndDate,InitialFundAccount,Commision,FutureType,Unit):
		FutureBackTest.__init__(self,StartDate,EndDate,InitialFundAccount)
		self.Commision=Commision
		self.FutureType=FutureType
		self.Unit=Unit
		self.Rootdir='C:/Users/fsd/OneDrive/Python/founder_future/ZSQSData/'
		self.FutureRootdir=self.Rootdir+FutureType+'_f/'
		self.FutureList=os.listdir(self.FutureRootdir)
		self.dataImport()
		self.Strategy()
		self.IndicatorCalculate()
		self.DataOutPut()
	def dataImport(self):
		pass
	def Strategy(self):
		pass
	def IndicatorCalculate(self):
		pass
	def DataOutPut(self):
		pass


