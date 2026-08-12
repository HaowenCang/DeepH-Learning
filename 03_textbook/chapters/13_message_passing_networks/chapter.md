# 第 13 章 消息传递神经网络

本章在第 12 章的属性有向多重图之上建立一至三层普通消息传递神经网络。目标是让每个中间张量、信息流方向和边级输出都可追踪，并用置换和感受野测试验证实现。这里的“普通”意味着不引入群表示或显式旋转等变通道；阶段 E 才处理轨道块在三维旋转下的协变。

D-GNN-01 提供 MPNN 的消息—更新—读出共同框架，D-GNN-02 支持集合聚合的置换结构，D-FND-02 支持梯度训练与诊断，DH-01 只用于说明普通 MPNN 与局域 Hamiltonian 学习的任务接口。来源和禁止外推见 [资料包](sources.md)。

## 13.1 普通 MPNN 的计算对象

### 13.1.1 消息、聚合、更新和读出

对有向边 \(e=(i,j,n)\)，\(i\) 为 receiver、\(j\) 为 sender。第 \(t\) 层写为

\[
m_e^{(t)}
=\phi_m^{(t)}
\left(h_i^{(t)},h_j^{(t)},f_e\right),
\]

\[
a_i^{(t)}
=\sum_{e:\operatorname{receiver}(e)=i}m_e^{(t)},
\]

\[
h_i^{(t+1)}
=\phi_u^{(t)}
\left(h_i^{(t)},a_i^{(t)}\right).
\]

这里 \(f_e\) 可包含合成的距离基、方向或类别特征。若直接使用笛卡尔位移分量，普通网络不会自动对旋转不变或等变。

### 13.1.2 参数共享与层索引

同一层的 \(\phi_m^{(t)}\) 对全部边共享，\(\phi_u^{(t)}\) 对全部节点共享。不同层可以使用不同参数；若跨层共享，必须显式声明。若参数依赖节点绝对行号或边存储行号，节点重编号等变性将失效。

层索引必须区分“输入状态”与“更新后状态”。所有第 \(t\) 层消息都由 \(h^{(t)}\) 同步计算，然后统一得到 \(h^{(t+1)}\)。在同一层循环中原地更新部分节点会引入节点遍历顺序依赖，并改变感受野。

### 13.1.3 节点级、边级和图级输出

节点输出对节点重编号等变；边输出对边实例重标等变；图级 sum/mean 读出可对节点排列不变。三种输出的评价层级不同，不能把图级不变性直接赋给边级轨道块。

阶段 D 的目标是边级合成块：

\[
\widehat y_e
=\phi_e(h_i^{(L)},h_j^{(L)},f_e).
\]

它必须与完整边键、轨道对、block shape 和 mask 同步输出。

## 13.2 一至三层前向传播

### 13.2.1 边消息张量

冻结教学层采用 row-vector 约定。设

\[
H^{(t)}\in\mathbb R^{N\times d},
\qquad
F\in\mathbb R^{E\times d_e}.
\]

对全部边并行构造

\[
Z_m^{(t)}
=
H^{(t)}_{\mathrm{receiver}}W_r^{(t)}
+H^{(t)}_{\mathrm{sender}}W_s^{(t)}
+FW_f^{(t)}
+\mathbf1(b_m^{(t)})^\mathsf T,
\]

\[
M^{(t)}=\tanh Z_m^{(t)}.
\]

其中 \(W_r^{(t)},W_s^{(t)}\in\mathbb R^{d\times d}\)，\(W_f^{(t)}\in\mathbb R^{d_e\times d}\)，\(b_m^{(t)}\in\mathbb R^d\)，所以 \(Z_m^{(t)},M^{(t)}\in\mathbb R^{E\times d}\)。

### 13.2.2 分段求和与节点更新

分段求和得到

\[
A_i^{(t)}
=\sum_{e:\operatorname{receiver}(e)=i}M_e^{(t)},
\qquad
A^{(t)}\in\mathbb R^{N\times d}.
\]

节点更新固定为

\[
Z_u^{(t)}
=H^{(t)}U_h^{(t)}
+A^{(t)}U_a^{(t)}
+\mathbf1(b_u^{(t)})^\mathsf T,
\]

\[
H^{(t+1)}=\tanh Z_u^{(t)}.
\]

空入边节点采用第 12 章 sum=0 的约定，因此仍可通过 self 项更新。padding 行在进入边 gather、分段求和和更新之前排除。

### 13.2.3 层数和图距离感受野

消息沿 sender \(\to\) receiver 流动。定义有向前驱距离

\[
\operatorname{dist}_{\to}(v,i)
\]

为从 \(v\) 沿消息方向到 \(i\) 的最短有向路径长度，不存在路径时为 \(\infty\)。在同步局部更新且无全局特征的条件下，\(h_i^{(L)}\) 只依赖满足

\[
\operatorname{dist}_{\to}(v,i)\le L
\]

的输入节点和相应路径上的边特征。

若每个底层无向关系都成对展开为两条相反有向边，该有向距离与底层无向图距离一致。若图是非对称有向图，不能用无向距离替代。

边输出 \(\widehat y_{ij n}\) 同时读取 \(h_i^{(L)}\) 与 \(h_j^{(L)}\)，因此其节点感受野是两个端点的 \(L\) 层前驱邻域之并，而不是仅 receiver 的邻域。

## 13.3 边级回归头

### 13.3.1 端点状态、边属性和方向

定义边头输入

\[
G_e=
\left[
h_i^{(L)}
\Vert h_j^{(L)}
\Vert f_e
\right]
\in\mathbb R^{2d+d_e}.
\]

最小线性边头为

\[
\widehat y_e=G_eW_o+b_o,
\]

其中 \(W_o\in\mathbb R^{(2d+d_e)\times P_{\max}}\)，\(b_o\in\mathbb R^{P_{\max}}\)。端点拼接顺序固定为 receiver、sender、edge feature；交换端点通常改变有向边输出。

### 13.3.2 轨道块展平与掩码

损失只在第 12 章右侧连续 mask 的有效位置上计算。设有效元素总数为

\[
S=\sum_{e,a}\texttt{mask}_{ea},
\]

则逐元素 MSE 固定为

\[
L_{\mathrm{edge}}
=\frac1S
\sum_{e,a}
\texttt{mask}_{ea}
(\widehat y_{ea}-y_{ea})^2.
\]

必须要求 \(S>0\)。若采用逐结构等权损失，应先在每个结构内部按有效元素平均，再对结构平均，并明确与逐元素口径的差异。

### 13.3.3 边输出 provenance

边头输出必须原样携带：

- `structure_id`、receiver、sender、shift；
- `edge_instance_id`；
- `block_shape`；
- `mask`、局部整数下标 `orbital_i_index`、`orbital_j_index`；
- 两端节点的有序合成轨道 ID 表 `node_orbitals[structure_id][receiver]`、`node_orbitals[structure_id][sender]`，以及逐分量实际身份 `orbital_i_id`、`orbital_j_id`；
- 输出单位和 schema 版本。

这里“局部整数下标”和“实际轨道身份”是不同对象。对有效位置 (a)，若 `block_shape=(p_i,p_j)`，必须逐项断言

\[
\alpha=\left\lfloor\frac{a}{p_j}\right\rfloor,
\qquad
\beta=a\bmod p_j,
\]

\[
(\texttt{orbital\_i\_id}_{ea},
\texttt{orbital\_j\_id}_{ea})
=
(\texttt{node\_orbitals}[\texttt{structure\_id}][i][\alpha],
\texttt{node\_orbitals}[\texttt{structure\_id}][j][\beta]).
\]

阶段 D 的轨道 ID 仅为合成字符串，不表示已经选择真实元素轨道基。`orbital_i_id`、`orbital_j_id` 的逻辑形状均为 \((E,P_{\max})\)；padding 位置的局部下标为 \(-1\)，实际 ID 为空字符串，且 mask 必须为 false。若实现不重复逐分量 ID，也必须让输出以 `structure_id`、端点和冻结 schema 版本稳定引用相同的有序轨道表，并在读取时执行上述等式；不能只保存局部下标。

预测数组、完整边键、mask、局部下标、实际轨道身份、所引用的有序轨道表和 schema 版本必须采用同一边行映射。排序、拼接批处理和置换后的逆映射都应同步作用于这些对象；禁止先排序预测、后按另一规则排序键或轨道身份。轨道表缺失、端点引用错误、表内顺序漂移，或者实际 ID 与局部下标解析不一致时，即使 shape、mask 和数值仍合法也必须拒绝。

## 13.4 训练与解析反向传播

### 13.4.1 MSE 对输出头的梯度

令

\[
R=(\widehat Y-Y)\odot\texttt{mask}.
\]

则

\[
\frac{\partial L_{\mathrm{edge}}}{\partial\widehat Y}
=\frac{2}{S}R,
\]

\[
\nabla_{W_o}L=G^\mathsf T\frac{\partial L}{\partial\widehat Y},
\qquad
\nabla_{b_o}L
=\mathbf1^\mathsf T
\frac{\partial L}{\partial\widehat Y}.
\]

padding 位置的输出梯度严格为零。

### 13.4.2 消息层的链式法则

边头对 \(h_i^{(L)}\) 与 \(h_j^{(L)}\) 的梯度需要按端点 scatter-add 回节点。分段求和的伴随操作则是 gather：若 \(A_i=\sum_{e:r(e)=i}M_e\)，那么

\[
\frac{\partial L}{\partial M_e}
=
\frac{\partial L}{\partial A_{\operatorname{receiver}(e)}}.
\]

因此前向的 gather—message—scatter-sum 在反向中按相反顺序传播。receiver/sender 混淆会同时破坏前向和梯度，但形状仍可能全部合法。

对任意局部激活 \(Y=\tanh Z\)，

\[
\frac{\partial L}{\partial Z}
=
\frac{\partial L}{\partial Y}
\odot(1-Y\odot Y).
\]

完整实现应缓存各层 \(H,Z_m,M,A,Z_u\) 或在反向中可重建它们；激活内存估计必须说明采用缓存还是重计算。

### 13.4.3 有限差分和梯度失败样例

T-D02 的有限差分口径继续适用。阶段 D 代码至少对一个消息权重、一个更新权重、边头权重和偏置执行中心差分，并强制注入：

- 漏掉 \(1/S\)；
- receiver scatter 改成 sender scatter；
- tanh 导数写成 \(1-H\)；
- padding 梯度未置零。

任一错误未被梯度检查或定向断言发现，代码门控失败。

## 13.5 置换一致性

### 13.5.1 共享消息函数

节点置换后，旧边 \((i,j,n)\) 变为 \((p(i),p(j),n)\)。共享消息函数和同步边特征保证对应边消息相同。若用绝对节点编号嵌入而不把它作为同步置换的输入，结论失效。

### 13.5.2 求和聚合

对应节点的入边多重集合一一映射，sum 与边行顺序无关，因此聚合后节点状态随 \(P\) 重排。D-D03 已给出逐层证明。

### 13.5.3 节点状态与边输出的等变证明

由 D-D03 的归纳，

\[
H'^{(L)}=PH^{(L)}.
\]

共享边头再给出

\[
\widehat y'_{p(e)}=\widehat y_e.
\]

T-D04 必须在非对称图、不同端点特征和随机边行重排下同时检查节点状态、边输出和 provenance。若只比较图级 sum，许多端点重标错误会被掩盖。

## 13.6 表达能力、优化和诊断边界

### 13.6.1 聚合碰撞与有限感受野

普通 MPNN 可能无法区分某些局部结构或聚合碰撞。增加层数扩大图距离感受野，却可能带来过平滑、优化困难和更高成本；它不保证解决所有图同构或长程物理问题。

### 13.6.2 训练下降、泛化和语义验证

训练损失下降不能验证：

- 分组划分无泄漏；
- 周期邻居表完备；
- 节点重编号一致；
- 边块索引正确；
- 旋转协变或下游物理正确。

这些性质分别由第 11、12、14 章、阶段 E 和后续实践门控验证。

### 13.6.3 普通 MPNN 不自动具有旋转等变性

若边特征只含距离，标量输出可以具有旋转不变输入接口，但这不自动产生轨道块协变输出。若边特征含笛卡尔位移并送入普通 MLP，旋转后数值通常改变且没有受控表示律。阶段 E 将引入表示矩阵和随机旋转残差。

## 13.7 本章可验证结论

### 13.7.1 张量形状追踪

对每层必须记录：

| 张量 | 形状 |
|---|---|
| \(H^{(t)}\) | \((N,d)\) |
| \(Z_m^{(t)},M^{(t)}\) | \((E,d)\) |
| \(A^{(t)},Z_u^{(t)},H^{(t+1)}\) | \((N,d)\) |
| \(G\) | \((E,2d+d_e)\) |
| \(\widehat Y\) | \((E,P_{\max})\) |

批处理还必须满足第 12 章的 graph ID、mask 和 padding 契约。

### 13.7.2 置换、感受野和梯度测试

一个可接受实现至少同时通过：

- 节点置换与边行重排；
- 1、2、3 层有向前驱感受野；
- 多镜像边不折叠；
- 输出 provenance 与 mask；
- 解析梯度与有限差分；
- 训练/验证/测试分组和确定性。

### 13.7.3 M8/M9 授权边界

本章网络只使用合成图和合成边标签，不安装 DeepH、不获取正式数据、不生成 DFT 标签，也不冻结正式材料或软件对象。M7 与 M7-I 通过后才进入 M8；M9 外部动作仍需用户明确授权。
