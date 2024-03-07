# AlphaZero_Gomoku_improve

This project is based on [junxiaosong/AlphaZero_Gomoku: An implementation of the AlphaZero algorithm for Gomoku (also called Gobang or Five in a Row) (github.com)](https://github.com/junxiaosong/AlphaZero_Gomoku).

Some new features:

* tune the model (for 9_9_5 gomoku game)
* multithread for accelerating
* visualization for training(loss/entropy/learning rate) and playing(board)

# operating environment

* To play with the trained AI models, only need:
  * Platform: Windows
  * Python: A newer version is fine
  * Numpy: A newer version is fine

* To train a new AI model:
  * PyTorch: A newer version is fine.\\(tested on 2.1.0+cu118)

* To visualize the training process:
  * matplotlib: A newer version is fine

> This project develops/tests on VS code throughout

# file

* game.py               

  >  game server for Gomoku

* human.py

  > human player interface

* mcts_pure.py

  > pure MCTS player

* mcts_alphaZero.py

  > alphaZero agent

* network.py

  > policy network for alphaZero

* train.py

  > trains the policy network

* visualize.py

  > visualize the data recorded during training

* model/

  * policy_2400.model

    > trained model

  * batch.txt

    > records the batch result

  * train_process.txt

    > records the training process

* utils/

  * gui.py

    > implement the graphics interface for Gomoku

  * background.png

    > the background image of the chessboard

  * tools.py

    > other tool functions

* visualize/

  * entropy_plot.png

    > Visualization of information entropy during training

  * loss_plot.png

    > Visualization of loss during training

  * lr_plot.png

    > Visualization of Learning rate factor during training

* play_with_alphaZero.py

  > play Gomoku yourself with AlphaZero

* test_alphaZero.py

  > test the win_ratio of AlphaZero agent against pure MCTS  and the average simulation time

# Tutorials

## AlphaZero Vs Pure MCTS(200)

* Run `test_alphaZero.py` directly

* The default is not to display the board, you can display the board by:

  ```python
  policy_evaluate(game, model_file, n_games=10, is_shown=0)
  =>
  policy_evaluate(game, model_file, n_games=10, is_shown=1)
  ```

  **When the board is displayed, when the game is over, you must manually close the visual interface to proceed to the next game.**

## play Gomoku yourself with AlphaZero

* Run `play_with_alphaZero.py` directly
* When the game ends, the terminal will output a win or loss result

## train a model yourself 

* Run `train.py` directly, disable gpu by default

* Enable gpu acceleration:

  ```Python
  training_pipeline = TrainPipeline(is_gpu=False)
  =>
  training_pipeline = TrainPipeline(is_gpu=True)
  ```

* Retrain the existing model:

  ```python
  training_pipeline = TrainPipeline(is_gpu=True)
  =>
  training_pipeline = TrainPipeline(init_model=<model path>, is_gpu=True)
  ```