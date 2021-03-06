路径规划：分属控制与决策部分

根据对 环境信息的把握程度，路径规划被划分为 基于**先验完全信息的全局路径规划** 和 **基于传感器信息的局部路径规划。**

障碍物信息
+ 静态障碍物
+ 动态障碍物
路径规划
+ 全局路径规划，静态规划：需要掌握所有的环境信息，根据环境地图的所有信息进行路径规划。
+ 局部路径规划，动态规划：由传感器实时采集环境信息，了解地图信息，确定自身在地图中的位置，掌握局部的障碍物分布情况，选择从当前节点到目标节点的最有路径。

全局路径规划算法中，大致分为三类：
1. 传统算法
2. 智能算法
3. 传统和智能算法结合

# 1. 传统算法综述
## 1.1 迪杰斯特拉(Dijkstra)算法(单源最短路径算法)
目标：A 点到 B 点的最短路径
模式：贪心模式
## 1.2 A* 算法
启发式搜索算法：在搜索过程中建立启发式搜索规则，以此来衡量实时搜索位置和目标位置的距离关系，使搜索方向优先朝向目标点所处位置的方向，最终达到提高搜索效率的效果。

节点 $x$ 的估计函数 $f(x)$:
$$
f(x) = g(x) + h(x)
$$
起点 $s$ 到 $x$ 点的**实际度量距离**：$g(x)$
$x$ 点到终点 $e$ 的**最小估计距离**：$h(x)$

算法的基本实现过程为：从起始点 $s$ 开始，计算其子节点$\text{x.childs}$的 $f$ 值，从中选择 $f$ 值最小的子节点作为搜索的下一个节点，往复迭代，直到到达终点。
## 1.3 D* 算法
&emsp;&emsp;基于 A* 算法，Anthony Stentz 在 1994 年提出了 Dynamic A* 算法。
&emsp;&emsp;D* 是一种反向增量式搜索算法
+ **反向算法**：从终点向起点逐步搜索
+ **增量式搜索**：在搜索过程中，会计算并保存每一个节点的度量距离信息 **$H(x)$**，在**动态环境**中若出现**障碍物**，**无法继续沿预先路径搜索**时，算法会根据**历史距离信息$H(X)$**，进行路径再规划，无需从终点重新规划。

距离度量信息
$$
H(x) = H(y) + C(y, x)
$$
