import numpy as np
import pandas as pd

class InvestmentPortfolio:
    """Represents a portfolio of tickers with weights through time."""

    def __init__(self):
        self.__portfolio = pd.DataFrame()

    def rebalance(self, date, weights):
        """Sets the given weights for their assosiated assets at given date.

        Arguments:
        date -- the date (no time) for the rebalance
        weights -- a dictonary or series containing a mapping from ticker to weight
                   which need not be normalized.
        """
        for missing in set(weights.index) - set(self.__portfolio.columns):
            self.__portfolio[missing] = .0

        self.__portfolio.ix[date] = weights
        self.__portfolio = self.__portfolio.fillna(0)

    def calculate_portfolio_returns(self, prices):
        """ Calculates the portfolio returns given the individual asset prices.

        Arguments:
        prices -- data frame which contains prices for all assets covered by this
                  portfolio.
        """
        tickers = set(self.__portfolio.columns)

        prices = prices.ix[:,tickers]
        norm_weights = self.__portfolio.div(self.__portfolio.sum(axis=1), axis=0)
        weights_aligned = pd.DataFrame(columns=prices.columns, index=prices.index)
        weights_aligned.ix[norm_weights.index,norm_weights.columns] = norm_weights
        weights_aligned = weights_aligned.fillna(method='ffill').fillna(0)
        weights_aligned = weights_aligned.shift(1)[1:]
        asset_returns = (prices / prices.shift(1) - 1)[1:]
        asset_returns = asset_returns.ix[weights_aligned.index]

        weighted_asset_returns = asset_returns * weights_aligned
        portfolio_returns = weighted_asset_returns.dot(np.ones(len(weighted_asset_returns.columns)))
        return portfolio_returns


    def get_portfolio_weights(self):
        """ Yields the portfolio weights. """
        return self.__portfolio
