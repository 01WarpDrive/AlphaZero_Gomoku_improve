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

胜利后的player显示

模型棋盘大小必须匹配

引入残差结构最好，我在最后的时候用了3个残差层，但我建议15这样的大棋盘最好能用到4个以上的残差
还有就是我觉得mcts不要继续使用python来编写了，python的mcts真的很慢，这样效率不高


减小dirichlet噪声
增大simulation的数量

模型有个固定开局，用在200mcts可能会浪费时间


train self.n_playout = 400,聪明反被聪明误
self.pure_mcts_playout_num



https://github.com/opendilab/LightZero 项目中Benchmark显示，alphazero至少能更快收敛到较高胜率


* 针对200专门训练尝试
* cython优化MCTS中耗时部分

一是它的self-play和MCTS部分都是用C++实现的


explain_var_old这个数值可以用来看value function的学习情况，小于0说明预测很不准，比较理想的情况是在0～1之间逐渐增大


谢回答。explained_var_old = (1 -
np.var(np.array(winner_batch) - old_v.flatten()) /
np.var(np.array(winner_batch)))，（分布a-分布b） 的方差/分布a的方差，请问这个公式出自哪里。。
和6x6对战试了下，基本没问题了。8x8有明显的边缘失策，如同其他回复下说的一样。
个人觉得很可能是 cnn做卷积的时候对边缘的zero-padding导致的，我猜想如果将边缘位置作为输入cnn的显式特征，例如单独一张边缘特征图输入这样。。会不会好一些。
当然，增大playout次数应该是最直接的方法


@Egolas 不知道你在测试的时候n_playout是否依然设置的是400，我之前也注意到边缘落子不去堵的情况，当时我把n_playout慢慢增大，记得到3000的时候，就会堵了。其实在AlphaZero论文里虽然训练的时候n_playout设置的是800，但他们测试评估的时候其实会跑几十万次模拟，所以在单步时间允许的范围内增大n_palyout能提高效果，一定程度上解决这个问题。
如果要从算法训练的角度改进的话，我的想法是增加exploration的程度，使得自我对弈数据更多样化，比如增加开局时的噪声，或者最开始几步随机落子，然后在此基础上再自我对弈，以避免自我对弈始终从棋盘中央开始。这是我的想法，没有测试过，供参考。

测试评估我指的是人工对战的时候，就是发现AI不堵边缘时，尝试把playout设置的大一些，可能就会堵了。
现在使用的网络结构是很随意定的，考虑到实验的棋盘比较小，所以就用了一个很简单的卷积网络，卷积的层数大概就是让最上层的感受野能覆盖整个棋盘。关于你遇到的增加一个卷积层之后就完全不收敛的情况，可以减小learning rate试试。
关于网络结构我也没太多思路，一个可以尝试的就是使用AlphaGo Zero论文中采用的Res Block的结构，当然这边不需要20个block这么多，可能2～3个就差不多了。

PS: song哥的Net是conv堆积, 建议改成resnet.再考虑加深层数.

最后结论就是你想加大棋盘的话, 建议使用residual block的方式来加深 network.
当然,计算量就会大大提高,需要使用更好的GPU资源来训练 😄