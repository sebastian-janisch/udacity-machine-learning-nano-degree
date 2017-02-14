class QLearner:

    def __init__(self, environment, actions, state_variables, alpha=0.5):
        """
            Arguments:
            environment -- the environment that allows to sense the current state
            actions -- possible actions for all states
            state_variables -- a list of available state varialbes
        """
        self.__environment = environment
        self.__actions = actions
        self.__state_variables = state_variables
        self.__Q = dict()
        self.__alpha= alpha

    def reward(self, states, rewards, log=None):
        """ Realises rewards for given states.

            Arguments:
            states -- data frame with actionable (e.g. asset) on x
                      and state variables on y
            rewards -- series with rewards for actionables (e.g. asset)
            log -- list to append log messages on or None if not needed
        """

        actions = self.get_actions_for_states(states, log)

        for actionable in actions.keys():
            state = self.__build_state(states[actionable])
            self.__updateQ(state)

            action = actions[actionable]
            reward = rewards[actionable]
            old_q = self.__Q[state][action]
            new_q = old_q + self.__alpha * (reward - old_q)

            self.__Q[state][action] = new_q

            if log:
                log.append("Updating Q for action {} in state {} from {} to {}"\
                             .format(action, state, old_q, new_q))

    def get_actions(self, log=None):
        """ Senses the environment and determines the best actions for each
            of the possible actionable.

            Arguments:
            log -- list of log should be appended or None if not needed
        """

        states = self.__environment.sense()
        actions = self.get_actions_for_states(states, log=log)

        return actions

    def get_actions_for_states(self, states, log=None):
        """
            Gets actions to choose for given state data frame.

            Arguments:
            states -- data frame with actionable (e.g. asset) on x
                      and state variables on y
            log -- list to append log messages on or None if not needed

        """
        result = {}

        for actionable in states.columns:
            state = self.__build_state(states[actionable])

            self.__updateQ(state)

            # find best Q
            best_Q = None
            for action in self.__Q[state].keys():
                q_value = self.__Q[state][action]
                if best_Q == None or best_Q[0] < q_value:
                    best_Q = (q_value, action)

            if log:
                log.append("Choosing {} for {} based on best Q {} for state {} ({})"\
                         .format(best_Q[1], actionable, best_Q[0], state, self.__Q[state]))
            result[actionable] = best_Q[1]

        return result

    def __build_state(self, raw_state):
        state = []
        for state_variable in self.__state_variables:
            state.append(raw_state[state_variable])

        return tuple(state)

    def __updateQ(self, state):
        # add state to Q table
        if state not in self.__Q:
            self.__Q[state] = {}
            for action in self.__actions:
                self.__Q[state][action] = 0.0
