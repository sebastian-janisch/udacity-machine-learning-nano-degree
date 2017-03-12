import pandas as pd
from scipy.stats.mstats import zscore

class Environment:
    """ The environment holds the current date and allows to sense the
        state for given date as well as advance to the next date.
    """

    def __init__(self, data, items):
        """ Initialises the environment with the underlying data panel and
            the data items to form the state space over.

            Arguments:
            data -- a panel where items are data items (e.g. LEVERAGE_ART, or PRICE),
                    major axis are dates and minor axis are tickers.
            items -- the items to form the state space over
        """
        self.__data = data
        self.__dates = list(data.get(items[0]).index)
        self.__items = items
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
        tickers = self.__data.get(self.__items[0]).columns

        environment = pd.DataFrame(index=[self.__items[0]], columns=tickers)

        # create zscores for each item
        for item in self.__items:
            try:
                item_data = self.__data.get(item).ix[date].copy()
                item_data[:] = pd.cut(zscore(item_data), bins=bins, labels=range(bins))
                environment.ix[item] = item_data
            except ValueError:
                print("Could not compute zscore for {}".format(item))
                raise


        return environment
