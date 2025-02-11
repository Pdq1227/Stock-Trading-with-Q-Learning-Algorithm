import warnings
import numpy as np
from sklearn.cluster import KMeans
import os

warnings.filterwarnings("ignore")
curr_path = os.path.dirname(__file__)

output_path = curr_path + '//outputs//'

class Config:
    def __init__(self, ticker):
        self.ticker = ticker
        self.epsilon = 1.0
        self.gamma = 0.618
        self.decay = 0.995
        self.epsilon_min = 0.015
        self.learning_rate = 0.03
        self.episode = 250
        self.clusters = 9
        self.kmeans = None

    def update_kmeans(self, kmeans):
        self.kmeans = kmeans

    def update_episode(self, episode):
        self.episode = episode


class Agent:
    def __init__(self, cfg):
        self.data = None
        self.epsilon = cfg.epsilon
        self.gamma = cfg.gamma
        self.epsilon_decay = cfg.decay
        self.epsilon_min = cfg.epsilon_min
        self.Q = np.matrix(np.zeros([cfg.clusters, 3]))
        self.learning_rate = cfg.learning_rate
        self.kmeans = cfg.kmeans

    def update_data(self, data):
        self.data = data

    def get_state(self, i):
        a = self.data[['O', 'H', 'L', 'C', 'RSI']].iloc[i - 1].values
        a = a.reshape(1, 5)
        b = self.kmeans.predict(a)
        return b[0]

    def get_action(self, state):
        a = [0, 1, 2]
        # 0 = Buy, 1 = Hold, 2 = Sell
        if np.random.random() <= self.epsilon:
            return np.random.randint(3)
        return np.argmax(self.Q[state,])

    def update(self, state, action, reward, next_state, next_action):
        self.Q[state, action] = self.Q[state, action] + self.learning_rate * (
                    reward + self.gamma * np.max(self.Q[next_state, next_action]) - self.Q[state, action])

class Model:
    def __init__(self, cfg):
        self.cfg = cfg
        self.agent = None
        self.train_rois = None
        self.test_rois = None
        self.dir_path = output_path + self.cfg.ticker
        os.makedirs(self.dir_path + '//charts')
        os.makedirs(self.dir_path + '//csv//Train')
        os.makedirs(self.dir_path + '//csv//Test')
        os.makedirs(self.dir_path + '//qtables')

    def train(self, train_data):
        kmeans = KMeans(n_clusters=self.cfg.clusters, random_state=0).fit(train_data[['O', 'H', 'L', 'C', 'RSI']].values)
        self.cfg.update_kmeans(kmeans)
        self.agent = Agent(self.cfg)
        self.agent.update_data(train_data)
        train_rois = []
        for i in range(self.cfg.episode):
            state = self.agent.get_state(0)
            action = self.agent.get_action(state)
            active_action = None
            active_price = 0
            active_quantity = 0
            capital = 10000000
            margin = capital
            total_profit = 0
            df_train = self.agent.data
            for r in range(len(df_train)):
                reward = 0
                df_train['Action1'][r] = action
                df_train['ActiveAction'][r] = active_action
                if active_action == 'sell':
                    profit = (active_price - df_train['Close'][r]) * active_quantity
                    profit_p = (active_price - df_train['Close'][r]) / active_price * 100
                    if profit_p < -10.0 or profit_p > 15.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_train['Cash'][r] = margin
                        action = 0
                        active_action = None
                        if profit_p < -10.0:
                            df_train['Action'][r] = 'Cutloss Short'
                        else:
                            df_train['Action'][r] = 'TP 15% Short'
                        reward = max(np.log(active_price) - np.log(df_train['Close'][r]), 0)
                        df_train['Reward'][r] = reward
                        if r != len(df_train) - 1:
                            next_state = self.agent.get_state(r + 1)
                            next_action = self.agent.get_action(next_state)
                            self.agent.update(state, action, reward, next_state, next_action)
                            action = next_action
                            state = next_state
                        continue

                elif active_action == 'buy':
                    profit = (df_train['Close'][r] - active_price) * active_quantity
                    profit_p = (df_train['Close'][r] - active_price) / active_price * 100
                    if profit_p < -10.0 or profit_p > 15.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_train['Cash'][r] = margin
                        action = 2
                        active_action = None
                        if profit_p < -10.0:
                            df_train['Action'][r] = 'Cutloss Long'
                        else:
                            df_train['Action'][r] = 'TP 15% Long'
                        reward = max(np.log(df_train['Close'][r]) - np.log(active_price), 0)
                        df_train['Reward'][r] = reward
                        if r != len(df_train) - 1:
                            next_state = self.agent.get_state(r+1)
                            next_action = self.agent.get_action(next_state)
                            self.agent.update(state, action, reward, next_state, next_action)
                            action = next_action
                            state = next_state
                        continue

                if action == 0 and active_action == None:
                    df_train['Cash'][r] = margin
                    df_train['Action'][r] = 'Open Long'
                    active_quantity = margin // df_train['Close'][r]
                    margin %= df_train['Close'][r]
                    active_price = df_train['Close'][r]
                    active_action = 'buy'
                elif action == 0 and active_action == 'sell':
                    profit = (active_price - df_train['Close'][r]) * active_quantity
                    profit_p = (active_price - df_train['Close'][r]) / active_price * 100
                    if profit_p > 7.0 or profit_p < -7.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_train['Cash'][r] = margin
                        active_action = None
                        if profit_p > 7.0:
                            df_train['Action'][r] = 'TP Short'
                        if profit_p < -7.0:
                            df_train['Action'][r] = 'Close Loss Short'
                        reward = max(np.log(active_price) - np.log(df_train['Close'][r]), 0)
                        df_train['Reward'][r] = reward
                    else:
                        action = 0
                        df_train['Action'][r] = 'Hold Short'
                        df_train['Cash'][r] = margin + active_quantity * (2 * active_price - df_train['Close'][r])
                        reward = max(np.log(active_price) - np.log(df_train['Close'][r]), 0)
                        df_train['Reward'][r] = reward
                elif action == 0 and active_action == 'buy':
                    action = 0
                    df_train['Action'][r] = 'Hold Long'
                    df_train['Cash'][r] = margin + (active_quantity * df_train['Close'][r])
                    reward = max(np.log(df_train['Close'][r]) - np.log(active_price), 0)
                    df_train['Reward'][r] = reward

                if action == 2 and active_action == None and margin > df_train['Close'][r]:
                    df_train['Cash'][r] = margin
                    df_train['Action'][r] = 'Open Short'
                    active_quantity = margin // df_train['Close'][r]
                    margin %= df_train['Close'][r]
                    active_price = df_train['Close'][r]
                    active_action = 'sell'
                elif action == 2 and active_action == 'buy':
                    profit = (df_train['Close'][r] - active_price) * active_quantity
                    profit_p = (df_train['Close'][r] - active_price) / active_price * 100
                    if profit_p > 7.0 or profit_p < -7.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_train['Cash'][r] = margin
                        active_action = None
                        if profit_p > 7.0:
                            df_train['Action'][r] = 'TP Long'
                        if profit_p < -7.0:
                            df_train['Action'][r] = 'Close Loss Long'
                        reward = max(np.log(df_train['Close'][r]) - np.log(active_price), 0)
                        df_train['Reward'][r] = reward
                    else:
                        action = 0
                        df_train['Action'][r] = 'Hold Long'
                        df_train['Cash'][r] = margin + (active_quantity * df_train['Close'][r])
                        reward = max(np.log(df_train['Close'][r]) - np.log(active_price), 0)
                        df_train['Reward'][r] = reward
                elif action == 2 and active_action == 'sell':
                    action = 0
                    df_train['Action'][r] = 'Hold Short'
                    df_train['Cash'][r] = margin + active_quantity * (2 * active_price - df_train['Close'][r])
                    reward = max(np.log(active_price) - np.log(df_train['Close'][r]), 0)
                    df_train['Reward'][r] = reward

                if action == 1:
                    if active_action == None:
                        df_train['Cash'][r] = margin
                        df_train['Action'][r] = 'Nothing'
                    elif active_action == 'buy':
                        df_train['Cash'][r] = margin + active_quantity * df_train['Close'][r]
                        df_train['Action'][r] = 'Hold Long'
                        reward = max(np.log(df_train['Close'][r]) - np.log(active_price), 0)
                        df_train['Reward'][r] = reward
                    elif active_action == 'sell':
                        df_train['Cash'][r] = margin + active_quantity * (2 * active_price - df_train['Close'][r])
                        df_train['Action'][r] = 'Hold Short'
                        reward = max(np.log(active_price) - np.log(df_train['Close'][r]), 0)
                        df_train['Reward'][r] = reward

                if r == len(df_train) - 1:
                    if active_action == 'sell':
                        profit = (active_price - df_train['Close'][r]) * active_quantity
                        total_profit += profit
                        margin += active_quantity * active_price + profit
                        df_train['Cash'][r] = margin
                        active_action = None
                        df_train['Action'][r] = 'Close End Short'
                    if active_action == 'buy':
                        profit = (df_train['Close'][r] - active_price) * active_quantity
                        total_profit += profit
                        margin += active_quantity * active_price + profit
                        df_train['Cash'][r] = margin
                        active_action = None
                        df_train['Action'][r] = 'Close End Long'
                else:
                    next_state = self.agent.get_state(r + 1)
                    next_action = self.agent.get_action(next_state)
                    self.agent.update(state, action, reward, next_state, next_action)
                    action = next_action
                    state = next_state
            roi = (margin - capital) / capital * 100
            train_rois.append(roi)
            if self.agent.epsilon > self.agent.epsilon_min and i > 1:
                self.agent.epsilon *= self.agent.epsilon_decay
            np.save(self.dir_path+'//qtables//qtable'+str(i+1)+'.npy',self.agent.Q)
            df_train.to_csv(self.dir_path+'//csv//Train//Train'+str(i+1)+'.csv')
        self.train_rois = train_rois

    def test(self, data_test):
        self.agent.update_data(data_test)
        self.cfg.update_episode(30)
        test_rois = []
        best_test = 0
        best_df = data_test
        for i in range(self.cfg.episode):
            state = self.agent.get_state(0)
            action = self.agent.get_action(state)
            active_action = None
            active_price = 0
            active_quantity = 0
            capital = 10000000
            margin = capital
            total_profit = 0
            df_test = self.agent.data
            for r in range(len(df_test)):
                reward = 0
                df_test['Action1'][r] = action
                df_test['ActiveAction'][r] = active_action

                if active_action == 'sell':
                    profit = (active_price - df_test['Close'][r]) * active_quantity
                    profit_p = (active_price - df_test['Close'][r]) / active_price * 100
                    if profit_p < -10.0 or profit_p > 15.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_test['Cash'][r] = margin
                        action = 0
                        active_action = None
                        if profit_p < -10.0:
                            df_test['Action'][r] = 'Cutloss Short'
                        else:
                            df_test['Action'][r] = 'TP 15% Short'
                        reward = np.log(active_price) - np.log(df_test['Close'][r])
                        if r != len(df_test) - 1:
                            next_state = self.agent.get_state(r + 1)
                            next_action = self.agent.get_action(next_state)
                            # next_action = np.argmax(agent.Q[next_state,])
                            action = next_action
                            state = next_state
                        continue
                elif active_action == 'buy':
                    profit = (df_test['Close'][r] - active_price) * active_quantity
                    profit_p = (df_test['Close'][r] - active_price) / active_price * 100
                    if profit_p < -10.0 or profit_p > 15.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_test['Cash'][r] = margin
                        action = 2
                        active_action = None
                        if profit_p < -10.0:
                            df_test['Action'][r] = 'Cutloss Long'
                        else:
                            df_test['Action'][r] = 'TP 15% Long'
                        reward = np.log(df_test['Close'][r]) - np.log(active_price)
                        if r != len(df_test) - 1:
                            next_state = self.agent.get_state(r + 1)
                            next_action = self.agent.get_action(next_state)
                            # next_action = np.argmax(agent.Q[next_state,])
                            action = next_action
                            state = next_state
                        continue

                if action == 0 and active_action == None:
                    df_test['Cash'][r] = margin
                    df_test['Action'][r] = 'Open Long'
                    active_quantity = margin // df_test['Close'][r]
                    margin %= df_test['Close'][r]
                    active_price = df_test['Close'][r]
                    active_action = 'buy'
                elif action == 0 and active_action == 'sell':
                    profit = (active_price - df_test['Close'][r]) * active_quantity
                    profit_p = (active_price - df_test['Close'][r]) / active_price * 100
                    if profit_p > 7.0 or profit_p < -7.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_test['Cash'][r] = margin
                        active_action = None
                        if profit_p > 7.0:
                            df_test['Action'][r] = 'TP Short'
                        if profit_p < -7.0:
                            df_test['Action'][r] = 'Close Loss Short'
                        reward = np.log(active_price) - np.log(df_test['Close'][r])
                    else:
                        action = 1
                        df_test['Action'][r] = 'Hold Short'
                        df_test['Cash'][r] = margin + active_quantity * (2 * active_price - df_test['Close'][r])
                elif action == 0 and active_action == 'buy':
                    action = 1
                    df_test['Action'][r] = 'Hold Long'
                    df_test['Cash'][r] = margin + (active_quantity * df_test['Close'][r])

                if action == 2 and active_action == None and margin > df_test['Close'][r]:
                    df_test['Cash'][r] = margin
                    df_test['Action'][r] = 'Open Short'
                    active_quantity = margin // df_test['Close'][r]
                    margin %= df_test['Close'][r]
                    active_price = df_test['Close'][r]
                    active_action = 'sell'
                elif action == 2 and active_action == 'buy':
                    profit = (df_test['Close'][r] - active_price) * active_quantity
                    profit_p = (df_test['Close'][r] - active_price) / active_price * 100
                    if profit_p > 7.0 or profit_p < -7.0:
                        total_profit += profit
                        margin += (active_price * active_quantity) + profit
                        df_test['Cash'][r] = margin
                        active_action = None
                        if profit_p > 5.0:
                            df_test['Action'][r] = 'TP Long'
                        if profit_p < -5.0:
                            df_test['Action'][r] = 'Close Loss Long'
                        reward = np.log(df_test['Close'][r]) - np.log(active_price)
                    else:
                        action = 1
                        df_test['Action'][r] = 'Hold Long'
                        df_test['Cash'][r] = margin + (active_quantity * df_test['Close'][r])
                elif action == 2 and active_action == 'sell':
                    action = 1
                    df_test['Action'][r] = 'Hold Short'
                    df_test['Cash'][r] = margin + active_quantity * (2 * active_price - df_test['Close'][r])

                if action == 1:
                    if active_action == None:
                        df_test['Cash'][r] = margin
                        df_test['Action'][r] = 'Nothing'
                    elif active_action == 'buy':
                        df_test['Cash'][r] = margin + active_quantity * df_test['Close'][r]
                        df_test['Action'][r] = 'Hold Long'
                    elif active_action == 'sell':
                        df_test['Cash'][r] = margin + active_quantity * (2 * active_price - df_test['Close'][r])
                        df_test['Action'][r] = 'Hold Short'

                if r == len(df_test) - 1:
                    if active_action == 'sell':
                        profit = (active_price - df_test['Close'][r]) * active_quantity
                        total_profit += profit
                        margin += active_quantity * active_price + profit
                        df_test['Cash'][r] = margin
                        active_action = None
                        df_test['Action'][r] = 'Close End Short'
                    if active_action == 'buy':
                        profit = (df_test['Close'][r] - active_price) * active_quantity
                        total_profit += profit
                        margin += active_quantity * active_price + profit
                        df_test['Cash'][r] = margin
                        active_action = None
                        df_test['Action'][r] = 'Close End Long'
                else:
                    next_state = self.agent.get_state(r + 1)
                    next_action = self.agent.get_action(next_state)
                    # next_action = np.argmax(agent.Q[next_state,])
                    action = next_action
                    state = next_state
            df_test['Price_Change'] = (df_test['Close'] - df_test['Close'][0]) / df_test['Close'][0] * 100
            df_test['Capital_Change'] = (df_test['Cash'] - df_test['Cash'][0]) / df_test['Cash'][0] * 100
            roi = (df_test['Cash'][len(df_test) - 1] - df_test['Cash'][0]) / df_test['Cash'][0] * 100
            if roi > best_test:
                best_df = df_test
                best_test = roi
            #test_rois.append(roi)

        best_df.to_csv(self.dir_path + '//csv//Test//Test' + '.csv')
        self.test_rois = test_rois
        np.save(self.dir_path+'//train_rois.npy',self.train_rois)
        np.save(self.dir_path+'//test_rois.npy',self.test_rois)