# A Model-Free Reinforcement Learning Trading Agent
# Udacity Machine Learning Nano Degree Capstone Project

Sebastian Janisch

This README outlines how to use the code for the capstone project.

1. This project utilises the below external libraries:

	- Numpy
	- Pandas 
	- portfolioopt (https://github.com/czielinski/portfolioopt)
	- Matplotlib
	
2. The code is structured as python classes and made up of the below main artefacts:

	- QuandlYahooDataService: data service to retrieve corporate fundamental data from 
	  Quandl (corporate data) and Yahoo (price data)

	- FlatFileDataService: data service that reads input data from flat-files.
	  This class can be used in conjunction with the data provided with this submission.

	- FinancialDataService: sets on top of either of the two above services and performs 
	  data cleansing/enrichment operations.
	  
	- QLearner: general q-learning implementation
	
	- Environment: class to form the state space (the environment variables)
	
	- InvestmentPortfolio: tracks portfolio weights of an investment portfolio through 
	  time and offers ability to compute portfolio returns
	  
	- TradingAgent: the agent that utilises the QLearner, Environment and InvestmentPortfolio 
	  classes to drive the system.
	  
3. There is no main method for this code. Rather, the code is utilised and explained/charted 
   using an IPython Notebook which is attached to this submission.