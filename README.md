# AlphaZero_Gomoku_improve
> an impletation of Gomoku AI based on AlphaZero



# 改进

## 对原先代码逻辑改进

1. game.py
   * current_state
   * self.players
   * self.states
   * get_current_player



e:\a_work\github\AlphaZero_Gomoku_improve\policy_value_net_pytorch.py:84: UserWarning: Creating a tensor from a list of numpy.ndarrays is extremely slow. Please consider converting the list to a single numpy.ndarray with numpy.array() before converting to a tensor. (Triggered internally at C:\actions-runner\_work\pytorch\pytorch\builder\windows\pytorch\torch\csrc\utils\tensor_new.cpp:264.)
  state_batch = Variable(torch.FloatTensor(state_batch).cuda())
kl:0.01344,lr_multiplier:1.000,loss:5.383143901824951,entropy:4.3856635093688965,explained_var_old:-0.000,explained_var_new:0.019