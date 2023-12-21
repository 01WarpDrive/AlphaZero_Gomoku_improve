# -*- coding: utf-8 -*-
"""
choose two of AI__player, mcts_player, human to play a game
Input your move in the format: 2,3
"""

from __future__ import print_function
from game import Board, Game
from mcts_pure import MCTSPlayer as MCTS_Pure
from mcts_alphaZero import MCTSPlayer
from policy_value_net_pytorch import PolicyValueNet


class Human(object):
    """
    human player
    """

    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board):
        try:
            location = input("Your move: ")
            if isinstance(location, str):  # for python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)
        except Exception as e:
            move = -1
        if move == -1 or move not in board.availables:
            print("invalid move")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)


def run(model_file, width=9, height=9, n=5, player1=0, player2=1):
    try:
        # load policy
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)
        best_policy = PolicyValueNet(width, height, model_file = model_file)

        # load player
        ai_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=200)
        mcts_player = MCTS_Pure(c_puct=5, n_playout=200)
        human = Human() # human player, input your move in the format: 2,3
        players = [ai_player, mcts_player, human]

        game.start_play(players[player1], players[player2], start_player=0, is_shown=1)
    except KeyboardInterrupt:
        print('\n\rquit')


if __name__ == '__main__':
    # 0-ai_player, 1-mcts_player, 2-human
    run('./model/best_policy.model', 9, 9, player1=0, player2=2)
