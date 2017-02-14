import pandas as pd
import os

class FlatFileDataService:
    ''' Obtains (and allows to persist) panel data to flat files. '''

    def __init__(self, directory):
        self.__directory = directory

    def get_data(self, items, tickers):
        """
        A file represents an individual item in the resulting panel and must be a
        csv file where the relative name is the item name (e.g. 'NET_INCOME.csv').

        An error will be raised if there are missing items or tickers.

        Arguments:
        items -- the data items to obtain
        tickers -- the tickers to obain
        """

        data_items = {}
        for item in items:
            path = os.path.join(self.__directory, "{}.csv".format(item))
            data_for_item = pd.read_csv(path, index_col=0, parse_dates=True)
            data_items[item] = data_for_item[tickers]

            missing = set(data_for_item.columns) & set(tickers) - set(tickers)
            if len(missing) > 0:
                raise Exception("Missing tickers: {}".format(missing))

        return pd.Panel(data_items)

    def persist_data(self, panel):
        """
        Writes the given panel to the directory associated with this instance.

        The items of the given pandas panel will be used as file names and
        the data frame for given item will be the content of that file (that
        is for each item a file will be output).

        Arguments:
        panel -- pandas data panel to persist
        """

        for item in panel.items:
            output_path = "{}/{}.csv".format(self.__directory, item)
            panel.get(item).to_csv(output_path)
