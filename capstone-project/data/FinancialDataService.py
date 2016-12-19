import pandas as pd
import quandl
import pandas_datareader.data as web
import datetime

class FinancialDataService:
	'''Exposes an API to retrieve quantitative data for different financial tickers.'''

	quandl.ApiConfig.api_key = ''

	fundamental_items = {
		'REVENUE': 'SF1/{}_REVENUEUSD_MRQ',
    	'NET_INCOME': 'SF1/{}_NETINC_MRQ',
		'AVERAGE_ASSETS': 'SF1/{}_ASSETSAVG_MRT',
		'AVERAGE_EQUITY': 'SF1/{}_EQUITYAVG_MRT',
		'INTEREST_EXPENSE': 'SF1/{}_INTEXP_MRQ',
		'EBIT': 'SF1/{}_EBIT_MRQ',
		'EBT': 'SF1/{}_EBT_MRQ',
		'DIVIDEND_YIELD': 'SF1/{}_DIVYIELD',
		'NET_PROFIT_MARGIN': 'SF1/{}_NETMARGIN',
		'ADJUSTED_CLOSE': 'SF1/{}_PRICE'
	}

	derived_items = {
		'LEVERAGE': (["AVERAGE_ASSETS", "AVERAGE_EQUITY"], lambda df: df["AVERAGE_ASSETS"] / df["AVERAGE_EQUITY"]),
		'INTEREST_BURDEN': (["EBT", "EBIT"], lambda df: df["EBT"] / df["EBIT"]),
		'INTEREST_COVERAGE': (["NET_INCOME", "INTEREST_EXPENSE"], lambda df: df["NET_INCOME"] / df["INTEREST_EXPENSE"])
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
				| set(FinancialDataService.derived_items.keys())

	def get_data(self, tickers = [], \
					   items = [], \
					   expand_composites = False, \
					   trim = True):
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

		direct_items = set(FinancialDataService.fundamental_items.keys()) & set(items)
		derived_items = set(FinancialDataService.derived_items.keys()) & set(items)

		# direct items required by derived items
		required_direct_items = set([item for derived_item in derived_items \
									 	  for item in FinancialDataService.derived_items[derived_item][0]])

		# less the direct items that are required anyway
		required_additional_items = required_direct_items - direct_items

		quandl_items = set(direct_items | required_additional_items)

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

		result = pd.Panel(fundamental_data).fillna(method='ffill')

		# mapping from derived item to computation lambda
		compute_items = dict((key, FinancialDataService.derived_items[key][1]) for key in derived_items)
		derived_data = self.__compute_derived_items__(result, compute_items)

		result = result.join(derived_data)

		if trim:
			result = result.dropna(axis=1)

		return result.loc[list(existing),:,:]

	def __compute_derived_items__(self, data, computations):
	    """Applies the given computations over each ticker data frame of the
	       given panel and returns a panel for which each ticker data frame contains
	       the given computation results where the column names are the keys of
	       the computations dictionary. If 'data' is a data frame then this is treated
	       as a panel with one ticker.

	       Keyword arguments:
	       data -- a panel or data frame
	       computations -- a dictionary where a key maps to a function that takes
	                       a data frame and outputs a series with result metrics
	    """

	    try:
	        keys = data.minor_axis
	        metrics = {}
	        for key in keys:
	            df = data.loc[:,:,key]
	            metrics[key] = self.__compute__(df, computations)
	        return pd.Panel(metrics).swapaxes(0, 2)
	    except AttributeError:
	        return __compute__(data, computations)

	def __compute__(self, df, computations):
	    columns = {}

	    for key in computations.keys():
	        computation = computations[key]
	        computation_result = computation(df)
	        columns[key] = computation_result

	    return pd.DataFrame(columns)
