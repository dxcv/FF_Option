#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
import scipy.stats as st 

class EuropeanOption:
	def __init__(self,S,K,T,r,sigma,optiontype):
		self.S=S
		self.K=K
		self.T=T
		self.r=r
		self.sigma=sigma
		self.d1=(np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
		self.d2=self.d1-sigma*np.sqrt(T)
		self.D=np.exp(-r*T)
		self.optiontype=optiontype
		self.run()
	def run(self):
		self.TheoryValue()
		self.Delta()
		self.Gamma()
		self.Theta()
		self.Speed()
		self.Vega()
		self.Rho()
	def N(x):
		return st.norm.cdf(x,loc = 0,scale = 1) 
	def N_(x):
		return st.norm.pdf(x,loc = 0,scale = 1) 
	def TheoryValue(self):
		S=self.S
		K=self.K
		T=self.T
		r=self.r
		d1=self.d1
		d2=self.d2
		sigma=self.sigma
		D=self.D
		if self.optiontype=='Call':
			self.theoryvalue=S*self.N(d1)-K*D*self.N(d2)
		elif self.optiontype=='Put':
			self.theoryvalue=-S*self.N(-d1)+K*D*self.N(-d2)
		elif self.optiontype=='BinaryCall':
			self.theoryvalue=D*self.N(d2)
		elif self.optiontype=='BinaryPut':
			self.theoryvalue=D*(1-self.N(d2))
		else:
			print 'optiontype is wrong'
	def Delta(self):
		S=self.S
		K=self.K
		T=self.T
		r=self.r
		d1=self.d1
		d2=self.d2
		sigma=self.sigma
		D=self.D
		if self.optiontype=='Call':
			self.delta=self.N(d1)
		elif self.optiontype=='Put':
			self.delta=self.N(d1)-1
		elif self.optiontype=='BinaryCall':
			self.delta=D*self.N_(d2)/(sigma*S*np.sqrt(T))
		elif self.optiontype=='BinaryPut':
			self.delta=-D*self.N_(d2)/(sigma*S*np.sqrt(T))
		else:
			print 'optiontype is wrong'
	def Gamma(self):
		S=self.S
		K=self.K
		T=self.T
		r=self.r
		d1=self.d1
		d2=self.d2
		sigma=self.sigma
		D=self.D
		if self.optiontype=='Call':
			self.gamma=self.N_(d1)/(sigma*S*np.sqrt(T))
		elif self.optiontype=='Put':
			self.gamma=self.N_(d1)/(sigma*S*np.sqrt(T))
		elif self.optiontype=='BinaryCall':
			self.gamma=-D*d1*self.N_(d2)/(sigma*sigma*S*S*T)
		elif self.optiontype=='BinaryPut':
			self.gamma=D*d1*self.N_(d2)/(sigma*sigma*S*S*T)
		else:
			print 'optiontype is wrong'
	def Theta(self):
		S=self.S
		K=self.K
		T=self.T
		r=self.r
		d1=self.d1
		d2=self.d2
		sigma=self.sigma
		D=self.D
		if self.optiontype=='Call':
			self.theta=-sigma*S*self.N_(d1)/(2*np.sqrt(T))-r*K*D*self.N(d2)
		elif self.optiontype=='Put':
			self.theta=-sigma*S*self.N_(-d1)/(2*np.sqrt(T))+r*K*D*self.N(-d2)
		elif self.optiontype=='BinaryCall':
			self.theta=r*D*self.N(d2)+D*self.N_(d2)*(d1/(2*T)-r/(sigma*np.sqrt(T)))
		elif self.optiontype=='BinaryPut':
			self.theta=r*D*(1-self.N(d2))-D*self.N_(d2)*(d1/(2*T)-r/(sigma*np.sqrt(T)))
		else:
			print 'optiontype is wrong'
	def Speed(self):
		S=self.S
		K=self.K
		T=self.T
		r=self.r
		d1=self.d1
		d2=self.d2
		sigma=self.sigma
		D=self.D
		if self.optiontype=='Call':
			self.speed=-self.N_(d1)/(sigma*sigma*S*S*T)*(d1+sigma*np.sqrt(T))
		elif self.optiontype=='Put':
			self.speed=-self.N_(d1)/(sigma*sigma*S*S*T)*(d1+sigma*np.sqrt(T))
		elif self.optiontype=='BinaryCall':
			self.speed=-D*self.N_(d2)/(sigma*sigma*S*S*S*T)*(-2*d1+(1-d1*d2)/(sigm*np.sqrt(T)))
		elif self.optiontype=='BinaryPut':
			self.speed=D*self.N_(d2)/(sigma*sigma*S*S*S*T)*(-2*d1+(1-d1*d2)/(sigm*np.sqrt(T)))
		else:
			print 'optiontype is wrong'
	def Vega(self):
		S=self.S
		K=self.K
		T=self.T
		r=self.r
		d1=self.d1
		d2=self.d2
		sigma=self.sigma
		D=self.D
		if self.optiontype=='Call':
			self.vega=self.N_(d1)*S*np.sqrt(T)
		elif self.optiontype=='Put':
			self.vega=self.N_(d1)*S*np.sqrt(T)
		elif self.optiontype=='BinaryCall':
			self.vega=-D*self.N_(d2)*(np.sqrt(T)+d2/sigma)
		elif self.optiontype=='BinaryPut':
			self.vega=D*self.N_(d2)*(np.sqrt(T)+d2/sigma)
		else:
			print 'optiontype is wrong'
	def Rho(self):
		S=self.S
		K=self.K
		T=self.T
		r=self.r
		d1=self.d1
		d2=self.d2
		sigma=self.sigma
		D=self.D
		if self.optiontype=='Call':
			self.rho=K*T*D*self.N(d2)
		elif self.optiontype=='Put':
			self.rho=-K*T*D*self.N(-d2)
		elif self.optiontype=='BinaryCall':
			self.rho=-T*D*self.N(d2)+np.sqrt(T)/sigma*D*self.N_(d2)
		elif self.optiontype=='BinaryPut':
			self.rho=-T*D*(1-self.N(d2))-np.sqrt(T)/sigma*D*self.N_(d2)
		else:
			print 'optiontype is wrong'


