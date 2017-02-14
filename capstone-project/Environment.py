import pandas as pd
from scipy.stats.mstats import zscore

class Environment:

    def __init__(self, data):
        self.__data = data
        self.__dates = list(data.get("LEVERAGE").index)
        self.__current_date_index = -1

    def advance(self):
        """ Advances one step through time.

            Yields the next date in time or None if we are at the
            end of the time series.
        """

        if self.__current_date_index + 1 == len(self.__dates):
            return None

        self.__current_date_index += 1
        return self.__dates[self.__current_date_index]

    def sense(self):
        """ Creates the environment space for current date. """

        date = self.__dates[self.__current_date_index]
        environment = self.sense_date(date)

        return environment

    def sense_date(self, date):
        bins = 3
        tickers = self.__data.get("LEVERAGE").columns

        environment = pd.DataFrame(index=["LEVERAGE"], columns=tickers)

        # Leverage ratio
        leverage = self.__data.get("LEVERAGE").ix[date].copy()
        leverage[:] = pd.cut(zscore(leverage), bins=bins, labels=range(bins))
        environment.ix["LEVERAGE"] = leverage

        # Profit margin
        profit_margin = self.__data.get("NET_PROFIT_MARGIN").ix[date].copy()
        profit_margin[:] = pd.cut(zscore(profit_margin), bins=bins, labels=range(bins))
        environment.ix["NET_PROFIT_MARGIN"] = profit_margin

        return environment
