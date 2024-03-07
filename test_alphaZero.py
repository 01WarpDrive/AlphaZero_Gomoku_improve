from __future__ import print_function
from game import Board, Game
from mcts_pure import MCTSPlayer as MCTS_Pure
from mcts_alphaZero import MCTSPlayer
from network import PolicyValueNet
from collections import defaultdict

def policy_evaluate(game, model_file, n_games=10, is_shown=0):
    """
    Evaluate the trained policy by playing against the pure MCTS player
    """
    best_policy = PolicyValueNet(game.board.width, game.board.height, model_file)
    mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=200)
    pure_mcts_player = MCTS_Pure(c_puct=5, n_playout=game.pure_mcts_playout_num)
    
    time_sum = 0
    win_cnt = defaultdict(int)
    for i in range(n_games):
        winner, simulation_time = game.start_play(mcts_player, pure_mcts_player, start_player=i % 2, is_shown=is_shown)
        time_sum += simulation_time
        win_cnt[winner] += 1
    win_ratio = 1.0*(win_cnt[1] + 0.5*win_cnt[-1]) / n_games
    simulation_time = time_sum / n_games
    print("\nnum_playouts:{}, win: {}, lose: {}, tie:{}".format(
            game.pure_mcts_playout_num,
            win_cnt[1], win_cnt[2], win_cnt[-1]))
    print("The average simulation time is {}\n".format(simulation_time))
    return win_ratio, simulation_time

if __name__ == '__main__':
    board_width = 9
    board_height = 9
    pure_playout_num = 200

    board = Board(width=board_width,
                       height=board_height,
                       n_in_row=5)
    model_file = './final_model/policy_2400.model'

    game = Game(board)
    game.pure_mcts_playout_num = pure_playout_num

    policy_evaluate(game, model_file, n_games=10, is_shown=0)