# 1. 背景
&emsp;&emsp;网络加深遇到瓶颈，出现梯度消失和爆炸的问题。
&emsp;&emsp;受 LSTM 的控制门的思想启发，2015 年何凯明提出了 ResNet 网络，
$$
\begin{aligned}
y   &= H(x, w_h) \cdot T(x, w_t) + x \cdot (1 - T(x, w_t)) \\
    &=  \alpha \cdot H(x, w_h) + (1 - \alpha) \cdot x
\end{aligned}
$$
当 $\alpha = 0$ 时 $y = x$，当 $\alpha = 1$ 时，$y = H(x, w_h)$。
# 2 ResNet Block
传统网络：$y = f(x)$，ResNet Block ：$y = f(x) + x$，称之为 `skip connect`。
# 3 原因
&emsp;&emsp;[Skip connections eliminate singularities](https://arxiv.org/abs/1701.09175) (跳过连接消除奇点)指出：**神经网络的退化，才是难以训练深层网络根本原因所在，而不是梯度消散**
&emsp;&emsp;虽然梯度范数大，但是如果网络的可用自由度对这些范数的贡献非常不均衡，也就是每个层只有少量的隐藏单元，对不同的输入改变它们的激活值，而大部分隐藏单元对不同的输入都是相同的反应，此时**整个权重矩阵的秩不高**，随着网络的加深，连乘后使得整个秩变得更低。
&emsp;&emsp;这也是我们常说的网络退化问题，虽然是一个很高维的矩阵，但大部分维度却没有信息，表达能力没有看起来那么强大。
&emsp;&emsp;残差连接正是强制打破了网络的对称性。
&emsp;&emsp;[Understanding and Improving Convolutional Neural Networks via Concatenated Rectified Linear Units](https://arxiv.org/abs/1603.05201)：打破了网络的对称性，消除了网络退化的问题，提升了网络的表征能力。


# [附](https://www.zhihu.com/question/61265076/answer/186347780)
&emsp;&emsp;从信号处理的方式说，要保证系统稳定。类似线性系统极点要在单位圆里，非线性直接价格激活卡住。
简而言之：ReLu 不行，越界了；sigmoid 差一半平面；只有 tanh 刚刚好。tanh 还有个好处是零点梯度为 1，这个性质比 sigmoid 好，relu 在右半平面也是 1， 但是越界不稳定。


# 10. Relu(Rectified Linear Units 修正线性单元)
## 10.1 表达式
$$
\text{ReLU}(x) = \max(0, x)
$$
## 10.2 优缺点
1. 和 sigmoid 、tanh 神经元昂贵的操作相比，ReLU 可以通过简单的 **零阈值** 矩阵进行激活，并且 **不受饱和的影响**
2. sigmoid 、 tanh 函数相比，ReLU 可以 **加快随机梯度下降算法的收敛**，普遍认为原因在于其具有 **线性、非饱和** 的形式。
3. ReLU 在训练时非常脆弱，并且可能会 **死掉**。当流经 LeLU 神经元的一个大梯度可能导致权重更新后该神经元接受到任何数据点都不会再激活。如果发生这种情况，之后通过该单位点的梯度永远是零。也就是说，ReLU 可能会在训练过程中 **不可逆死亡**，**破坏数据流形**。例如，如果学习率太高，40%的网络会**死**，而设置一个适当的学习率，可以在一定程度避免这个问题。
