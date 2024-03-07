from __future__ import print_function
import numpy as np
import threading
from mcts_pure import MCTSPlayer as MCTS_Pure
from collections import defaultdict, deque
from time import time


class Board(object):
    """board for the game"""

    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 9))
        self.height = int(kwargs.get('height', 9))
        # board states stored as a dict
        # key: move as location on the board
        # value: player as pieces type
        self.states = {}
        # need how many pieces in a row to win
        self.n_in_row = int(kwargs.get('n_in_row', 5))
        self.players = [1, 2]  # player1 and player2

    def init_board(self, start_player=0):
        self.current_player = self.players[start_player]  # start player
        # keep available moves in a list
        self.availables = list(range(self.width * self.height))
        self.states = {}
        self.last_move = -1

    def move_to_location(self, move):
        """
        3*3 board's moves like:
        6 7 8
        3 4 5
        0 1 2
        and move 5's location is (1,2)
        """
        h = move // self.width
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        # location: two dimensions
        # move: an int
        if len(location) != 2:
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if move not in range(self.width * self.height):
            return -1
        return move

    def current_state(self):
        """
        return the board state from the perspective of the current player.
        state shape: 4*width*height
        -[0][,]: the locations of the current player's moves
        -[1][,]: the locations of the opponent's moves
        -[2][,]: the last move location
        -[3][,]: indicate the colour to play
        """
        square_state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width,
                            move_curr % self.height] = 1.0
            square_state[1][move_oppo // self.width,
                            move_oppo % self.height] = 1.0
            # indicate the last move location
            square_state[2][self.last_move // self.width,
                            self.last_move % self.height] = 1.0
        if len(self.states) % 2 == 0:
            square_state[3][:, :] = 1.0  # indicate the colour to play
        return square_state[:, ::-1, :]

    def do_move(self, move):
        """
        put the next chess piece
        -add a new move: player pair to self.states
        -remove the move from self.availables
        -update the player and last move
        """
        self.states[move] = self.current_player
        self.availables.remove(move)
        self.current_player = (
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )
        self.last_move = move


    def has_a_winner(self):
        m = self.last_move
        if m == -1: return False, -1
        width = self.width
        height = self.height
        states = self.states
        player = states[m]
        h = m // width
        w = m % width
        n = self.n_in_row

        # from left to right
        left, right = 0, width-1
        for i in range(w):
            # current = w - i - 1
            if states.get(m-i-1, -1) != player: 
                left = w - i
                break
        for i in range(width - w - 1):
            # current = w + i + 1
            if states.get(m+i+1, -1) != player: 
                right = w + i
                break
        if right - left + 1 == n: return True, player

        # from bottom to top
        bottom, top = 0, height-1
        for i in range(h):
            # current = h - i - 1
            if states.get(m - (i+1)*width, -1) != player: 
                bottom = h - i
                break
        for i in range(height - h - 1):
            current = h + i + 1
            if states.get(m + (i+1)*width, -1) != player: 
                top = h + i
                break
        if top - bottom + 1 == n: return True, player

        # from bottom left to top right
        bottom, top = 0, height-1
        for i in range(h):
            # current = h - i - 1
            if states.get(m - (i+1)*width - (i+1), -1) != player: 
                bottom = h - i
                break
        for i in range(height - h - 1):
            current = h + i + 1
            if states.get(m + (i+1)*width + (i+1), -1) != player: 
                top = h + i
                break
        if top - bottom + 1 == n: return True, player

        # from bottom right to top left
        bottom, top = 0, height-1
        for i in range(h):
            # current = h - i - 1
            if states.get(m - (i+1)*width + (i+1), -1) != player: 
                bottom = h - i
                break
        for i in range(height - h - 1):
            current = h + i + 1
            if states.get(m + (i+1)*width - (i+1), -1) != player: 
                top = h + i
                break
        if top - bottom + 1 == n: return True, player

        return False, -1

    def game_end(self):
        """
        Check whether the game is ended or not
        """
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        elif not len(self.availables): # tie
            return True, -1
        return False, -1

    def get_current_player(self):
        return self.current_player


class Game(object):
    """game server"""

    def __init__(self, board, **kwargs):
        self.board = board
        self.pure_mcts_playout_num = 200


    def start_play(self, player1, player2, start_player=0, is_shown=1):
        """
        start a game between two players
        """
        if start_player not in (0, 1):
            raise Exception('start_player should be either 0 (player1 first) '
                            'or 1 (player2 first)')
        
        if is_shown:
            import utils.gui as gui
            lock = threading.Lock()
            gomoku_gui = gui.GomokuGUI(self.board.width, lock)
            t = threading.Thread(target=gomoku_gui.loop)
            t.start()

        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}
        
        time_sum, playout_num = 0, 0.01

        while True:
            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]
            if player_in_turn.isHuman and is_shown:
                gomoku_gui.set_is_human(True)
                lock.acquire()
                move = gomoku_gui.get_human_move()
                lock.release()
            elif player_in_turn.isAI:
                now = time()
                move= player_in_turn.get_action(self.board)
                time_sum += time() - now
                playout_num += player_in_turn.mcts._n_playout
            else: move = player_in_turn.get_action(self.board)

            self.board.do_move(move)

            if is_shown:
                color = -1 # black
                if current_player == 2 and start_player == 0 or current_player == 1 and start_player == 1: color = 1
                gomoku_gui.execute_move(color, move)

            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is", players[winner])
                    else:
                        print("Game end. Tie")

                    t.join()

                return winner, time_sum / playout_num
            
    def start_self_play(self, player, is_shown=0, temp=1e-3):
        """ 
        start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        self.board.init_board()
        p1, p2 = self.board.players
        states, mcts_probs, current_players = [], [], []
        while True:
            move, move_probs = player.get_action(self.board,
                                                 temp=temp,
                                                 return_prob=1)
            # store the data
            states.append(self.board.current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.current_player)
            # perform a move
            self.board.do_move(move)
            # if is_shown:
            #     self.graphic(self.board, p1, p2)
            end, winner = self.board.game_end()
            if end:
                # winner from the perspective of the current player of each state
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                # reset MCTS root node
                player.reset_player()
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is player:", winner)
                    else:
                        print("Game end. Tie")
                return winner, zip(states, mcts_probs, winners_z)