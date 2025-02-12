# -*- coding: utf-8 -*-
"""
An implementation of the training pipeline of AlphaZero for Gomoku
"""

from __future__ import print_function
import random
import numpy as np
from collections import defaultdict, deque
from game import Board, Game
from mcts_pure import MCTSPlayer as MCTS_Pure
from mcts_alphaZero import MCTSPlayer
from network import PolicyValueNet


train_process_path = "./model/train_process.txt"
evaluate_path = "./model/evaluate.txt"
batch_path = "./model/batch.txt"

def clear_txt():
    # clear file
    with open(train_process_path, 'w') as file:
        pass
    with open(evaluate_path, 'w') as file:
        pass
    with open(batch_path, 'w') as file:
        pass



class TrainPipeline():
    def __init__(self, board_width=9, board_height=9, n_in_row=5, init_model=None, is_gpu=None):
        # params of the board and the game
        self.board_width = board_width
        self.board_height = board_height
        self.n_in_row = n_in_row
        self.is_gpu = is_gpu
        self.board = Board(width=self.board_width,
                           height=self.board_height,
                           n_in_row=self.n_in_row)
        self.game = Game(self.board)
        # training params
        self.learn_rate = 2e-3
        self.lr_multiplier = 1.0  # adaptively adjust the learning rate based on KL
        self.kl_targ = 0.02
        self.temp = 1  # the temperature param
        self.n_playout = 600  # num of simulations for each move
        self.c_puct = 6
        self.buffer_size = 10000
        self.batch_size = 512  # mini-batch size for training
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.play_batch_size = 1 # self-play times each epoch
        self.epochs = 5  # num of train_steps for each update
        self.check_freq = 200
        self.game_batch_num = 6000 # num of train epoch
        # num of simulations used for the pure mcts, which is used as
        # the opponent to evaluate the trained policy
        self.pure_mcts_playout_num = 200
        self.best_win_ratio = 0.0
        if init_model:
            # start training from an initial policy-value net
            self.policy_value_net = PolicyValueNet(self.board_width,
                                                   self.board_height,
                                                   model_file=init_model, use_gpu=is_gpu)
            #self.best_win_ratio = self.policy_evaluate()
            #print("inil win ratio: {}".format(self.best_win_ratio))
        else:
            # start training from a new policy-value net
            self.policy_value_net = PolicyValueNet(self.board_width,
                                                   self.board_height, use_gpu=is_gpu)
        # AlphaZero player with current policy value net
        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn,
                                      c_puct=self.c_puct,
                                      n_playout=self.n_playout,
                                      is_selfplay=1)

    def get_equi_data(self, play_data):
        """
        augment the data set by rotation and flipping
        play_data: [(state, mcts_prob, winner_z), ..., ...]
        """
        extend_data = []
        for state, mcts_porb, winner in play_data:
            for i in [1, 2, 3, 4]:
                # rotate counterclockwise
                equi_state = np.array([np.rot90(s, i) for s in state])
                equi_mcts_prob = np.rot90(np.flipud(
                    mcts_porb.reshape(self.board_height, self.board_width)), i)
                extend_data.append((equi_state,
                                    np.flipud(equi_mcts_prob).flatten(),
                                    winner))
                # flip horizontally
                equi_state = np.array([np.fliplr(s) for s in equi_state])
                equi_mcts_prob = np.fliplr(equi_mcts_prob)
                extend_data.append((equi_state,
                                    np.flipud(equi_mcts_prob).flatten(),
                                    winner))
        return extend_data

    def collect_selfplay_data(self, n_games=1):
        """
        collect self-play data for training
        play n_games times
        """
        for i in range(n_games):
            # play with MCTS player
            winner, play_data = self.game.start_self_play(self.mcts_player,
                                                          temp=self.temp)
            play_data = list(play_data)[:]
            self.episode_len = len(play_data)
            # augment the data
            play_data = self.get_equi_data(play_data)
            self.data_buffer.extend(play_data)

    def policy_update(self, batch):
        """update the policy-value net"""
        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch = [data[0] for data in mini_batch]
        mcts_probs_batch = [data[1] for data in mini_batch]
        winner_batch = [data[2] for data in mini_batch]
        # save the old_probs, old_v before update
        old_probs, old_v = self.policy_value_net.policy_value(state_batch)
        for i in range(self.epochs):
            # every time tune parameters and return loss, entropy
            loss, entropy = self.policy_value_net.train_step(
                    state_batch,
                    mcts_probs_batch,
                    winner_batch,
                    self.learn_rate*self.lr_multiplier)
            # get new probability and state value form state
            new_probs, new_v = self.policy_value_net.policy_value(state_batch)
            # calculate the loss difference before and after the update
            kl = np.mean(np.sum(old_probs * (
                    np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)),
                    axis=1)
            )
            if kl > self.kl_targ * 4:  # early stopping if D_KL diverges badly
                break
        # adaptively adjust the learning rate
        if kl > self.kl_targ * 2 and self.lr_multiplier > 0.1:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_targ / 2 and self.lr_multiplier < 10:
            self.lr_multiplier *= 1.5

        explained_var_old = (1 -
                             np.var(np.array(winner_batch) - old_v.flatten()) /
                             np.var(np.array(winner_batch)))
        explained_var_new = (1 -
                             np.var(np.array(winner_batch) - new_v.flatten()) /
                             np.var(np.array(winner_batch)))
        # record the training process: loss, entropy
        out_txt = (
               "batch:{},"
               "kl:{:.5f},"
               "lr_multiplier:{:.3f},"
               "loss:{},"
               "entropy:{},"
               "explained_var_old:{:.3f},"
               "explained_var_new:{:.3f}"
               ).format(batch,
                        kl,
                        self.lr_multiplier,
                        loss,
                        entropy,
                        explained_var_old,
                        explained_var_new)
        with open(train_process_path, 'a') as wf:
            wf.write(out_txt + "\n")
        print(out_txt)
        return loss, entropy

    def policy_evaluate(self, n_games=10):
        """
        Evaluate the trained policy by playing against the pure MCTS player
        Note: this is only for monitoring the progress of training
        """
        current_mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn,
                                         c_puct=self.c_puct,
                                         n_playout=self.n_playout)
        pure_mcts_player = MCTS_Pure(c_puct=5,
                                     n_playout=self.pure_mcts_playout_num)
        win_cnt = defaultdict(int)
        for i in range(n_games):
            winner = self.game.start_play(current_mcts_player,
                                          pure_mcts_player,
                                          start_player=i % 2,
                                          is_shown=0)
            win_cnt[winner] += 1
        win_ratio = 1.0*(win_cnt[1] + 0.5*win_cnt[-1]) / n_games
        # record the evaluating result
        out_txt = "num_playouts:{}, win: {}, lose: {}, tie:{}".format(
                self.pure_mcts_playout_num,
                win_cnt[1], win_cnt[2], win_cnt[-1])
        with open(evaluate_path, 'a') as wf:
            wf.write(out_txt + "\n")
        print(out_txt)
        return win_ratio

    def run(self):
        """run the training pipeline"""
        print("Start training.")
        print("GPU is {}.".format("on" if self.is_gpu else "off"))
        try:
            # train game_batch_num times, each batch with play_batch_size
            # self-play times = game_batch_num * play_batch_size
            for i in range(self.game_batch_num):
                self.collect_selfplay_data(self.play_batch_size)
                # record the batch result
                out_txt = "batch i:{}, episode_len:{}".format(
                        i+1, self.episode_len)
                with open(batch_path, 'a') as wf:
                    wf.write(out_txt + "\n")
                print(out_txt)
                if len(self.data_buffer) > self.batch_size:
                    loss, entropy = self.policy_update(i)
                # check the performance of the current model,
                # and save the model params
                if (i+1) % self.check_freq == 0:
                    print("current self-play batch: {}".format(i+1))
                    # win_ratio = self.policy_evaluate()
                    self.policy_value_net.save_model('./model/policy_{}.model'.format(i+1))
                    # if win_ratio > self.best_win_ratio:
                    #     print("New best policy!!!!!!!!")
                    #     self.best_win_ratio = win_ratio
                    #     # update the best_policy
                    #     self.policy_value_net.save_model('./model/best_policy.model')
                    #     if (self.best_win_ratio == 1.0 and
                    #             self.pure_mcts_playout_num < 5000):
                    #         self.pure_mcts_playout_num += 1000
                    #         self.best_win_ratio = 0.0
        except KeyboardInterrupt:
            print('\n\rquit')


if __name__ == '__main__':
    clear_txt()
    training_pipeline = TrainPipeline(is_gpu=False)
    training_pipeline.run()