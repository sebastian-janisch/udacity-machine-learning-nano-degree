import pandas as pd
import quandl
import pandas_datareader.data as web

class QuandlYahooDataService:
    ''' Obtains fundamental data from Quandl and market data from yahoo.'''
    quandl.ApiConfig.api_key = ''

    __fundamental_items = {
        'REVENUE': 'SF1/{}_REVENUEUSD_ART',
        'NET_INCOME': 'SF1/{}_NETINC_ART',
        'AVERAGE_ASSETS': 'SF1/{}_ASSETSAVG_ART',
        'AVERAGE_EQUITY': 'SF1/{}_EQUITYAVG_ART',
        'INTEREST_EXPENSE': 'SF1/{}_INTEXP_ART',
        'EBIT': 'SF1/{}_EBIT_ART',
        'EBT': 'SF1/{}_EBT_ART',
        'DIVIDEND_YIELD': 'SF1/{}_DIVYIELD',
        'NET_PROFIT_MARGIN': 'SF1/{}_NETMARGIN_ART',
    }

    def __init__(self):
        pass

    def get_data(self, items, tickers):
        """ Returns a panel which's items are the given items and has dates
            on the major axis and tickers on the minor axis.

            Keyword arguments:
            tickers -- can contain either valid stock tickers or stock indices.
            items -- a list of data items to obtain. See 'get_available_items'.
        """
        fundamental_data = {}

        items = set(items)
        if "PRICE" in items:
            prices = self.__load_yahoo__(tickers)
            fundamental_data["PRICE"] = prices
            items = items - {"PRICE"}


        for item in items:
            item_keys = [self.__fundamental_items[item].format(ticker) for ticker in tickers]
            data_for_item = quandl.get(item_keys)
            data_for_item.columns = tickers

            fundamental_data[item] = data_for_item

        return pd.Panel(fundamental_data)

    def __load_yahoo__(self, tickers):
        url = "http://ichart.finance.yahoo.com/table.csv?s={}"
        result = pd.DataFrame()
        for ticker in tickers:
            data = pd.read_csv(url.format(ticker), index_col=0, parse_dates=True)["Adj Close"]
            frame = data.to_frame(ticker)
            result = result.join(data.to_frame(ticker), how='outer')

        result = result.fillna(method='ffill')
        return result
