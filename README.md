# AlphaZero_Gomoku_improve
> an impletation of Gomoku AI based on AlphaZero



# 改进

## 对原先代码逻辑改进

1. game.py
   * current_state
   * self.players
   * self.states
   * get_current_player


### 数据结构改良
e:\a_work\github\AlphaZero_Gomoku_improve\policy_value_net_pytorch.py:84: UserWarning: Creating a tensor from a list of numpy.ndarrays is extremely slow. Please consider converting the list to a single numpy.ndarray with numpy.array() before converting to a tensor. (Triggered internally at C:\actions-runner\_work\pytorch\pytorch\builder\windows\pytorch\torch\csrc\utils\tensor_new.cpp:264.)
  state_batch = Variable(torch.FloatTensor(state_batch).cuda())
kl:0.01344,lr_multiplier:1.000,loss:5.383143901824951,entropy:4.3856635093688965,explained_var_old:-0.000,explained_var_new:0.019

### GPU加速
hello， 大神， 请问下你训练机器配置是什么样的， 用了gpu没呢。 我发现有个小问题， 如果用了gpu， mctsaphaZero.py文件里， self.policy(state)这里， 返回值leafvalue其实在gpu里， 类型为tensor（我用的pytorch版本）， 这里只需要把leaf_value = leaf_value.cpu().numpy()， 挪到cpu里， 整体会快5倍左右。 我用的RTX 2080, 不到10个小时就可以把8*8, 5的训练出来



@782832949 ，突然想到棋盘扩大之后dirichlet噪声的参数可能需要调整。根据AlphaZero论文里的描述， 这个参数一般按照反比于每一步的可行move数量设置，所以棋盘扩大之后这个参数可能需要减小。
具体是mcts_alphaZero.py中的197行
p=0.75 * probs + 0.25 * np.random.dirichlet(0.3 * np.ones(len(probs)))
其中的0.3可能减小一些（比如到0.1），会有帮助。不过我也没有实际跑大棋盘的经验，仅供参考。

