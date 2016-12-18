import pandas as pd
import quandl
import pandas_datareader.data as web
import datetime

class FinancialDataService:
	'''Exposes an API to retrieve quantitative data for different financial tickers.'''

	quandl.ApiConfig.api_key = 'Fjsaq61Lf4HshV9S2fsG'

	fundamental_items = {
		'REVENUE': 'SF1/{}_REVENUE_ARQ',
    	'NET_INCOME': 'SF1/{}_NETINC_ARQ'
	}

	stock_items = {
		'ADJUSTED_CLOSE': 'Adj Close'
	}

	# TODO possibly move into own class and push in as dependency
	indices = {
		'DJIA': ['AAPL', 'AXP', 'BA', 'CAT', 'CSCO', 'CVX', 'KO', 'DD', 'XOM', \
			     'GE', 'GS', 'HD', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MMM',  \
				 'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'TRV', 'UNH', 'UTX', 'V', \
				 'VZ', 'WMT', 'DIS']
	}

	def __init___(self, ):
		pass

	def get_available_items(self):
		return set(FinancialDataService.fundamental_items.keys()) \
				| set(FinancialDataService.stock_items.keys())

	def get_data(self, tickers = [], \
					   items = [], \
					   expand_composites = False, \
					   trim = [True]):
		""" Returns a panel which's items are the given items and has dates
			on the major axis and tickers on the minor axis.

			Items that do not exist as per 'get_available_items' are ignored.

			NaN items are fill forwarded.

			Keyword arguments:
			tickers -- can contain either valid stock tickers or stock indices.
			items -- a list of data items to obtain. See 'get_available_items'.
			expand_composites -- if True then any ticker that can be resolved
								 as a composite (e.g. DJIA) will be resolved
								 to its composite tickers.
			trim -- if True then the head of the resulting panel will be trimmed
					to the first date for which all items are non NaN.
		"""

		existing = self.get_available_items() & set(items)

		quandl_items = list(existing & set(FinancialDataService.fundamental_items.keys()))
		yahoo_items = list(existing & set(FinancialDataService.stock_items.keys()))

		if expand_composites:
			tickers = [ticker if ticker not in FinancialDataService.indices.keys() \
						  	  else FinancialDataService.indices[ticker] \
						  	  for ticker in tickers]
			tickers = [item for sublist in tickers for item in sublist]

		fundamental_data = {}

		for item in quandl_items:
			item_keys = [FinancialDataService.fundamental_items[item].format(ticker) for ticker in tickers]
			data_for_item = quandl.get(item_keys)
			data_for_item.columns = tickers

			fundamental_data[item] = data_for_item

		stock_data = pd.Panel()
		if len(yahoo_items) > 0:
			start = datetime.datetime(1900, 1, 1)
			end = datetime.datetime.today()
			item_keys = [FinancialDataService.stock_items[key] for key in yahoo_items]
			stock_data = web.DataReader(tickers, 'yahoo', start=start, end=end).loc[item_keys]
			stock_data.items = yahoo_items

		result = pd.Panel(fundamental_data).join(stock_data, how='outer')
		result = result.fillna(method='ffill')

		if trim:
			result = result.dropna(axis=1)

		return result
