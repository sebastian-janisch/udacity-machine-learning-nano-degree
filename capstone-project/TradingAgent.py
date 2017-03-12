import pandas as pd
import portfolioopt as pfopt
from Environment import Environment
from learn import QLearner
from finance import InvestmentPortfolio
import random

class TradingAgent:

    def __init__(self, data, price_item, items, alpha, random=False):
        """ Initialises the trading agent with its data and items to trade upon.

            Arguments:
            data -- a panel where items are data items (e.g. LEVERAGE_ART, or PRICE),
                    major axis are dates and minor axis are tickers
            price_item -- a string that represents the name of the stock price item
            items -- the items to form the state space over
            alpha -- the learning rate for the q learner
            random -- will trade randomly if True
        """
        self.__actions = ["BUY", "SELL"]
        self.__state_variables = items

        self.__environment = Environment(data, items)
        self.__learner = QLearner(self.__environment, self.__actions, self.__state_variables, alpha=alpha)
        self.__prices = pd.DataFrame(data.get(price_item))
        self.__returns = (self.__prices / self.__prices.shift(1) - 1)[1:]
        self.__portfolio = InvestmentPortfolio()
        self.__random = random

    def get_environment(self):
        return self.__environment

    def learn(self, periods, reward_offset, log=None):
        """ Initially trains the learner for given periods and
            realises rewards after given offset.

            Arguments:
            periods -- the number of periods to learn for without actually
                    tracking performance
            reward_offset -- the periods after which to calculate the
                    reward (e.g. if we act at time t then we calculate
                    realised asset returns between t and t + reward_offset)
            log -- a list if log messages should be added or None if not needed
        """
        actions_taken = dict()

        for i in range(periods):
            date = self.__environment.advance()

            actions = self.__learner.get_actions()
            actions_taken[date] = pd.Series(actions)

            if i <= reward_offset or i % reward_offset != 0:
                # only act every 'reward_offset' times
                continue

            date_to = self.__returns.index[i-1]
            date_from = self.__returns.index[i-1-reward_offset]
            self.__reward(date_from, date_to, actions_taken[date_from], log=log)

    def trade(self, reward_offset, log=None):
        """ Steps through time and trades available stocks in a minimum
            variance portfolio.

            Arguments:
            reward_offset -- the periods after which to calculate the
                    reward (e.g. if we act at time t then we calculate
                    realised asset returns between t and t + reward_offset)
            log -- a list if log messages should be added or None if not needed
        """

        if self.__random:
            self.learn(255, reward_offset)

        actions_taken = dict()

        i = 0
        current_date = self.__environment.advance()
        while current_date:
            state = self.__environment.sense()

            actions = pd.Series(self.__learner.get_actions())
            if self.__random:
                actions = actions.apply(lambda x: random.choice(self.__actions))

            actions_taken[current_date] = pd.Series(actions)

            if i <= reward_offset or i % reward_offset != 0:
                current_date = self.__environment.advance()
                i += 1
                continue

            buy_actions = actions.loc[actions == 'BUY'].index

            if len(buy_actions) == 0:
                self.__portfolio.rebalance(current_date, pd.Series({'CASH': 1.0}))
            else:
                current_returns = self.__returns.ix[:current_date][buy_actions]
                min_var_portfolio = pfopt.min_var_portfolio(current_returns.cov())
                self.__portfolio.rebalance(current_date, min_var_portfolio)

            date_to = self.__returns.index[255+i-1]
            date_from = self.__returns.index[255+i-1-reward_offset]

            self.__reward(date_from, date_to, actions_taken[date_from], log=log)

            current_date = self.__environment.advance()
            i += 1

    def __reward(self, date_from, date_to, actions_taken, log=None):
        returns_slice = self.__returns.ix[date_from:date_to]

        cum_returns = self.__calculate_cum_returns(returns_slice)
        std = returns_slice.std()
        sharpe = cum_returns / returns_slice.std()
        reward_date = date_from

        states = self.__environment.sense_date(reward_date)

        # if the action at the time was SELL then the reward is the inverse
        # (i.e. if we sold and the return was negative then that should be rewarded)
        sell_actions = actions_taken.loc[actions_taken == 'SELL'].index

        rewards = sharpe
        rewards.ix[sell_actions] = rewards.ix[sell_actions] * -1

        if log:
            log_cols = ["Cum. Return", "Std", "Sharpe", "Action Taken", "Reward"]
            log_cols.extend(states.index)

            log_frame = pd.DataFrame(index=rewards.index, columns=log_cols)
            log_frame["Cum. Return"] = cum_returns
            log_frame["Std"] = std
            log_frame["Sharpe"] = sharpe
            log_frame["Action Taken"] = actions_taken
            log_frame["Reward"] = rewards

            for state_variable in states.index:
                log_frame[state_variable] = states.ix[state_variable]

            log.append("Registering reward for {} for realised returns up tp {}: "\
                      .format(reward_date.date(), date_to.date()))
            log.append(log_frame.to_string())

        self.__learner.reward(states, rewards, log=log)

    def __calculate_cum_returns(self, returns):
        cum_returns = ((returns + 1).apply(lambda s: s.cumprod()) - 1).iloc[-1]
        return cum_returns

    def get_portfolio(self):
        return self.__portfolio
