from __future__ import print_function
from game import Board, Game
from mcts_pure import MCTSPlayer as MCTS_Pure
from mcts_alphaZero import MCTSPlayer
from network import PolicyValueNet
from human import Human


def play(width, height, model_path, start_player = 0, is_shown = 0):
    n = 5
    board = Board(width=width, height=height, n_in_row=n)
    game = Game(board)

    best_policy = PolicyValueNet(width, height, model_file = model_path)
    mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=200)

    human = Human()
    pure_mcts_player = MCTS_Pure(c_puct=5, n_playout=200)

    # return game.start_play(pure_mcts_player, mcts_player, start_player=start_player, is_shown=is_shown)
    # set start_player=0 for human first
    return game.start_play(human, mcts_player, start_player=start_player, is_shown=is_shown)        

if __name__ == '__main__':

    n_game = 1

    width, height = 9, 9
    model_file = './final_model/policy_2400.model'

    for i in range(n_game):
        winner, _= play(width, height, model_file, start_player=0, is_shown=1)