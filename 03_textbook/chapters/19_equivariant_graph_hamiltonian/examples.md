# 第 19 章例题与失败样例

## 例 19-1：表示型节点特征的 shape

配置 A 的 multiplicity 为

\[
(n_{0,+},n_{1,-},n_{2,+})=(3,2,2).
\]

单个节点的三个活动数组 shape 分别为

\[
(3,1),\qquad(2,3),\qquad(2,5).
\]

总 component 数为

\[
3\cdot1+2\cdot3+2\cdot5=19.
\]

旋转只作用于每个数组最后的 \(1,3,5\) component 轴；multiplicity 轴不旋转。把所有数据展平成长度 19 后乘一个任意 \(19\times19\) 矩阵，一般会混合不同 \((\ell,p)\) 并破坏类型合同。

## 例 19-2：一条 \(1\otimes1\) 消息的输出类型

发送节点有极向量特征 \((1,-1)\)，边 filter 取 \(\ell_f=1\) 球谐，类型也是 \((1,-1)\)。CG 允许

\[
L=0,1,2,
\]

且所有输出宇称为

\[
p_{\mathrm{out}}=(-1)(-1)=+1.
\]

输出类型为

\[
(0,+1),\qquad(1,+1),\qquad(2,+1).
\]

中间通道是轴向量。若实现把 \(L=1\) 自动标成 \((1,-1)\)，正旋转可能通过，反演必失败。

## 例 19-3：固定非方 \(s+p\) 到 \(p+d\) Hamiltonian

取

\[
\widehat a=\frac{(1,2,3)^{\mathsf T}}{\sqrt{14}},
\qquad\theta=0.7,
\]

由 Rodrigues 公式得到

\[
R=
\begin{pmatrix}
0.78163917&-0.48292928&0.39473980\\
0.55011723&0.83203013&-0.07139250\\
-0.29395788&0.27295634&0.91601507
\end{pmatrix}.
\]

用第 16 章 \(B_a\) 得到 \(D^d(R)\)，并令

\[
D_i=1\oplus R\in\mathbb R^{4\times4},
\qquad
D_j=R\oplus D^d(R)\in\mathbb R^{8\times8}.
\]

合成块按 C-order 取

\[
H=\frac1{10}
\begin{pmatrix}
1&2&3&4&5&6&7&8\\
9&10&11&12&13&14&15&16\\
17&18&19&20&21&22&23&24\\
25&26&27&28&29&30&31&32
\end{pmatrix}.
\]

正确输出

\[
H'=D_iHD_j^{\mathsf T}
\]

为

\[
\begin{pmatrix}
0.10000000&0.20000000&0.30000000&0.97535236&0.28571463&0.76725285&0.18200762&0.49522844\\
0.62410472&1.18729383&0.92404573&2.02990637&0.73497184&1.45123890&0.04270819&0.82072795\\
1.24059499&2.35935876&1.82524810&3.98554501&1.44818808&2.84405571&0.07155751&1.60374698\\
1.75378060&3.32481438&2.41653652&4.93359930&1.86624781&3.44426464&-0.08761552&1.87517199
\end{pmatrix}.
\]

float64 奇异值最大变化为 \(3.55\times10^{-15}\)，与左右正交作用一致。

## 例 19-4：只左乘与错误右作用

以例 19-3 的正确 \(H'\) 为基准，归一化 Frobenius 残差为：

| 变异 | 残差 |
|---|---:|
| 只左乘 \(D_iH\) | \(0.5461588700\) |
| 只右乘 \(HD_j^{\mathsf T}\) | \(0.05995264977\) |
| 右侧误用 \(D_j\)，即 \(D_iHD_j\) | \(0.9216691727\) |

非方 shape 使 receiver/sender 交换无法靠偶然相同维数隐藏。T-E06 必须实际执行这些错误对象，而不是只列预期异常。

## 例 19-5：逆边与旋转相容

为正向边 \((i,j,n)\) 设置

\[
H_{ji,-n}=H_{ij,n}^{\mathsf T}.
\]

分别旋转两边：

\[
H_{ij,n}'=D_iH_{ij,n}D_j^{\mathsf T},
\]

\[
H_{ji,-n}'=D_jH_{ji,-n}D_i^{\mathsf T}.
\]

例 19-3 的最大逐元素差

\[
\max|H_{ji,-n}'-(H_{ij,n}')^{\mathsf T}|
=8.88\times10^{-16}.
\]

若只生成正向边后在输出末尾无 provenance 地转置，无法证明所配对的是同一 structure、反向端点和 \(-n\)。

## 例 19-6：复基中转置不能替代共轭转置

取

\[
D_i=\operatorname{diag}(e^{i\alpha},e^{-i\alpha}),
\qquad
D_j=\operatorname{diag}(1,e^{i\beta}),
\]

以及一般复块 \(H\in\mathbb C^{2\times2}\)。正确式为

\[
H'=D_iHD_j^\dagger.
\]

若使用 \(D_j^{\mathsf T}=D_j\)，第二列获得 \(e^{+i\beta}\) 而不是 \(e^{-i\beta}\)。当 \(\beta\notin\pi\mathbb Z\) 且第二列非零时，两者不同。该故障不会由 shape 检查发现。

## 例 19-7：完整边键不随旋转改变

取

\[
e=(\text{stageD-edge-v1},\text{stageE-synth},2,0,-1,0,1).
\]

旋转后笛卡尔位移变为 \(Rd\)，但 edge payload 和 SHA-256 edge ID 必须逐字节不变。错误做法包括：

- 用旋转后浮点位移重建离散 shift；
- 按距离重排后不带逆置换；
- 把不同镜像但同距离的边折叠。

T-E06/T-E08 必须在同一完整键行上比较旋转前后输出。

## 例 19-8：concat/padded 表示轴

设两图节点数 \(N_1=2,N_2=3\)，都有一个 \(p\) shell。concat shape 为

\[
(5,1,3),
\]

并用 graph ID 区分前 2 行与后 3 行。padded shape 为

\[
(2,3,1,3),
\]

第一个图最后一个节点 inactive。若 inactive 区写入 NaN，正确实现应在任何旋转、CG 或 loss 前切除，使有效输出与填零/极大值探针逐元素相同。把 component 轴 3 与节点 padding 轴混淆会产生合法广播但错误语义。

## 例 19-9：非退化局部架

取

\[
u=(1,0,0)^{\mathsf T},
\qquad
v=\frac{(1,1,0)^{\mathsf T}}{\sqrt2},
\qquad s=1.
\]

则

\[
e_1=(1,0,0)^{\mathsf T},
\quad
e_2=(0,1,0)^{\mathsf T},
\quad
e_3=(0,0,1)^{\mathsf T},
\]

所以 \(F=I\)。对任意合法旋转 \(R\)，输入变为 \(Ru,Rv\)，同一算法给 \(F'=R\)。因此

\[
\overline H=U_i^\dagger HU_j
\]

保持不变，回拉给出正确全局协变块。

## 例 19-10：局部架阈值与任意后备轴失败

固定

\[
u=(1,0,0),
\qquad
v_\varepsilon=\frac{(1,\varepsilon,0)}{\sqrt{1+\varepsilon^2}}.
\]

float64 使用 \(\tau_{\mathrm{frame}}=10^{-8}\)。当

\[
\varepsilon\in\{0,\tau/4,\tau/2,\tau\}
\]

时，实际 \(\eta\le\tau\) 必须拒绝；在 \(2\tau,4\tau,10^{-2}\) 处按实际 \(\eta>\tau\) 接受。等号拒绝。退化时若任意选择全局 \(y\) 轴作为后备，旋转输入后后备轴不随 \(R\) 旋转，一般有 \(F(RX)\ne RF(X)\)。

## 例 19-11：数学残差与拟合误差不同

设正确协变预测为 \(\widehat H=H_{\mathrm{target}}+\Delta\)，且 \(\Delta\) 自身按相同双侧表示变换。则等变残差可为机器精度，但预测误差

\[
\lVert\Delta\rVert_F
\]

仍可很大。反之，一个在单个样例上恰好接近 target 的非等变函数可有小拟合误差，但随机旋转残差很大。因此 T-E06/T-E08 必须分列 equivariance residual 与 target error。

## 例 19-12：成本对象不能混写

对固定同型逐边线性 reference kernel，MAC 来自实际

\[
(E,n_{\mathrm{out}},n_{\mathrm{in}},2\ell+1)
\]

contraction，receiver 聚合加法另计。球谐生成、CG 路径、局部架和 Hamiltonian 双侧乘法若实际执行，必须以各自操作图另报，不能塞进 reference kernel 的 MAC。数组 bytes 同样按名称给 total/reference peak；可选 wall-time 不进入确定性 hash。

## 例 19-13：两条边的端到端向量消息

取一个 receiver \(i\) 的两条入边，receiver→sender 单位方向为

\[
\widehat d_1=(1,0,0)^{\mathsf T},
\qquad
\widehat d_2=(0,1,0)^{\mathsf T}.
\]

发送节点偶标量分别为 \(s_1=2,s_2=3\)，径向偶权重为 \(w_1=1,w_2=1/2\)。使用 \(0\otimes1\to1\) 路径，在等价实笛卡尔基中

\[
m_e=w_es_e\widehat d_e.
\]

receiver sum 为

\[
a_i=2(1,0,0)^{\mathsf T}
+\frac32(0,1,0)^{\mathsf T}
=(2,3/2,0)^{\mathsf T}.
\]

在主动 \(R_z(\pi/2)\) 下，

\[
\widehat d_1'=(0,1,0)^{\mathsf T},
\qquad
\widehat d_2'=(-1,0,0)^{\mathsf T},
\]

所以

\[
a_i'=(-3/2,2,0)^{\mathsf T}
=R_z(\pi/2)a_i.
\]

该例同时验证径向偶标量、方向表示、sum 聚合和端到端输出。若把位移方向改成 sender→receiver 的负向，等变性仍可能通过，但消息语义与冻结 edge direction/target 不一致；因此还需方向、edge key 和合成 target 检查，不能只看旋转残差。

## 例 19-14：一般轴复点值必须先变为 coefficient filter

取

\[
\widehat d=(1,2,3)^{\mathsf T}/\sqrt{14},
\qquad
\widehat a=(2,-1,1)^{\mathsf T}/\sqrt6,
\qquad
\theta=0.73,
\]

并令 \(R\) 为绕 \(\widehat a\) 的主动旋转。DLMF-CS \(\ell=1\)、\(m=(-1,0,1)\) 的函数点值为

\[
y^{\mathrm{pv}}_1(\widehat d)
=
\begin{pmatrix}
0.09233720-0.18467439i\\
0.39175354\\
-0.09233720-0.18467439i
\end{pmatrix}.
\]

它按 \(D^{(1)}(R)^*\) 变换。进入规范 coefficient CG 前取

\[
z^{\mathrm{cf}}_1=\overline{y^{\mathrm{pv}}_1}.
\]

旋转方向的 filter 为

\[
z^{\mathrm{cf}}_1(R\widehat d)
=
\begin{pmatrix}
-0.03335607+0.00015643i\\
0.48631997\\
0.03335607+0.00015643i
\end{pmatrix},
\]

全精度 `complex128` 残差为

\[
\rho\!\left(z^{\mathrm{cf}}_1(R\widehat d),
D^{(1)}(R)z^{\mathrm{cf}}_1(\widehat d)\right)
=6.62\times10^{-17}.
\]

若直接把 \(y^{\mathrm{pv}}\) 当 coefficient，则

\[
\rho\!\left(y^{\mathrm{pv}}_1(R\widehat d),
D^{(1)}(R)y^{\mathrm{pv}}_1(\widehat d)\right)
=0.5219896443.
\]

这个反例在实笛卡尔基中会被 \(D^*=D\) 隐藏。因此 T-E08 必须包含一般轴复数正例和该定向失败；T-E12 还必须拒绝 filter hash、\(m\) 顺序或 edge-row provenance 与路径声明不一致的对象。
