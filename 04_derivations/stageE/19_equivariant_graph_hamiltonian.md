# D-E05—D-E07：等变消息、Hamiltonian 块与局部架

## 1. 目标与对象边界

本文件完成：

- D-E05：\(s,p,d\) Hamiltonian 块、多壳层、Hermiticity 与双侧协变；
- D-E06：径向偶标量、球谐、CG、聚合、同型混合和门控组成的最小消息层；
- D-E07：局部坐标预测、全局回拉、精确退化合同和比较边界；
- D-E09：上述对象的局部 shape/成本与正式 T-E10 边界。

所有计算只针对固定合成图和合成矩阵。DeepH-E3/e3nn 软件、数据、材料和 DFT 设置不在本推导范围。

## 2. 周期图和表示 schema

边

\[
e=(i,j,n)
\]

以 \(i\) 为 receiver、\(j\) 为 sender，位移行向量为

\[
d_e=(f_j+n-f_i)A.
\]

全局主动旋转采用行晶格

\[
A'=AR^{\mathsf T},
\]

故

\[
d_e'=d_eR^{\mathsf T}.
\]

列方向满足 \(\widehat d_{\mathrm{col}}'=R\widehat d_{\mathrm{col}}\)。离散 \((i,j,n)\) 不变。

节点特征按类型拆分：

\[
x^{(\ell,p)}
\in\mathbb F^{N\times n_{\ell,p}\times(2\ell+1)}.
\]

component mask 对一个 irrep shell 只能全真或全假。边级消息另有前导 \(E\) 轴；batch 只在 node/edge/graph 轴扩展，不能混入 component。

### 2.1 D-E05—D-E07 统一符号、维度与身份表

下表中的 \(N,E\) 分别是节点和有向边数，\(P_i,P_j\) 是 receiver/sender 实际轨道数，\(n_{\ell,p}\) 是 irrep multiplicity，\(q\) 是局部架对象数。除非另行声明，complex 路线使用 `complex128`/`complex64`，等价实路线使用 `float64`/`float32`；同一次残差比较不得混用 dtype。

| D-E | 符号 | rank 与 shape | dtype、基与身份 |
|---|---|---|---|
| D-E05 | \(H_{e}\) | rank 3；packed 为 \((E,P_i,P_j)\)，逐边活动块为 \((P_i(e),P_j(e))\) | 实笛卡尔或 DLMF-CS 复 coefficient 基；edge row、完整 edge key/ID、左右 shell span、实际轨道 ID、mask、basis family、K/hash |
| D-E05 | \(D_i,D_j\) | rank 2；\((P_i,P_i)\)、\((P_j,P_j)\) | 与各端 shell 顺序和 basis family 完全一致；不带 edge 置换 |
| D-E06 | \(x^{(\ell,p)}\) | rank 3；\((N,n_{\ell,p},2\ell+1)\) | coefficient 表示；node、multiplicity、\(m\) 升序身份 |
| D-E06 | \(y^{\mathrm{pv}}_{e,\ell}\) | rank 2；\((E,2\ell+1)\) | complex 球谐点值，按 \(D^*\) 变换；edge row、方向、\(m\) 升序 |
| D-E06 | \(z^{\mathrm{cf}}_{e,\ell}=\overline{y^{\mathrm{pv}}_{e,\ell}}\) | rank 2；\((E,2\ell+1)\) | complex coefficient filter，按 \(D\) 变换；`stageE-edge-filter-v1`、basis/hash、edge provenance |
| D-E06 | \(w_{e,\alpha}\) | rank 2；\((E,n_{\mathrm{path}})\) | 实偶标量；distance/radial-path 身份 |
| D-E06 | \(C^{LM}_{\ell m,\ell_fm_f}\) | rank 3；\((2L+1,2\ell+1,2\ell_f+1)\) | 冻结 DLMF-CS coefficient CG；输出 \(M\) 与两个输入快轴、CG hash |
| D-E06 | \(m,a,h\) | rank 3；\(m:(E,n_{\mathrm{path}},2L+1)\)，\(a:(N,n_{\mathrm{path}},2L+1)\)，\(h:(N,n_{L,p},2L+1)\) | coefficient 表示；分别保留 edge/path、receiver/path、node/multiplicity 身份；component 不与这些轴混合 |
| D-E07 | \(u_q,v_q\) | rank 2；\((q,3)\)；单对象为 \((3,)\) | 实笛卡尔列向量；local-object ID、端点/来源、尺度 \(s_q\) |
| D-E07 | \(F_q=[e_1,e_2,e_3]\) | rank 3；\((q,3,3)\)；单对象为 \((3,3)\) | `float64`/`float32`，列为唯一右手局部轴；\(F\in SO(3)\) |
| D-E07 | \(U_i,U_j\) | rank 2；\((P_i,P_i)\)、\((P_j,P_j)\) | 由 \(F_i,F_j\) 在完整 shell 顺序上的直和表示；携带轨道/basis/hash |
| D-E07 | \(\overline H=U_i^\dagger HU_j\) | rank 2；\((P_i,P_j)\) | 局部块与原块共享 edge、shell、轨道和 mask 身份；回拉不得转置左右身份 |

统一行合同是：每条边的 \(y^{\mathrm{pv}}\)、\(z^{\mathrm{cf}}\)、\(w\)、\(m\)、Hamiltonian 块、mask、edge key/ID 和 provenance 在同一 edge row；共轭、CG 收缩、局部化和回拉均不得独立排序。

## 3. D-E06 最小消息层

**输入、输出与成立条件。** 输入是已通过图/schema/方向零长度门控的 \(x^{(\ell,p)}\)、有限径向偶权重 \(w\)、按完整 edge row 生成的复点值 \(y^{\mathrm{pv}}\)，以及冻结的 CG 表。必须先构造 \(z^{\mathrm{cf}}=\overline{y^{\mathrm{pv}}}\)，使两个 CG 输入都按 coefficient \(D\) 表示变换；还要求合法三角范围、宇称乘法、同一 dtype/basis/component 顺序、完整 path/edge provenance、完整 irrep mask 和偶标量门控。输出为 \(h^{(L,p)}\in\mathbb F^{N\times n_{L,p}\times(2L+1)}\)。最终不变量是逐路径、聚合后与端到端的旋转/反演/置换残差；入口为 T-E08，schema 与故障拒绝同时进入 T-E12。

### 3.1 路径公式

对路径

\[
(\ell_{\mathrm{in}},p_{\mathrm{in}},\mu)
\otimes
(\ell_f,p_f)
\to
(L,p_{\mathrm{out}},\alpha),
\]

要求

\[
p_{\mathrm{out}}=p_{\mathrm{in}}p_f,
\qquad
|\ell_{\mathrm{in}}-\ell_f|\le L\le\ell_{\mathrm{in}}+\ell_f.
\]

消息为

\[
m_{e,\alpha M}
=
w_\alpha(r_e)
\sum_{m,m_f}
C^{LM}_{\ell_{\mathrm{in}}m,\ell_fm_f}
x_{j,\mu m}
z^{\mathrm{cf}}_{e,\ell_fm_f}.
\]

这里

\[
y^{\mathrm{pv}}_{e,\ell_f}(R\widehat d_e)
=D_{\ell_f}(R)^*y^{\mathrm{pv}}_{e,\ell_f}(\widehat d_e),
\qquad
z^{\mathrm{cf}}_{e,\ell_f}:=\overline{y^{\mathrm{pv}}_{e,\ell_f}},
\]

故 \(z^{\mathrm{cf}}(R\widehat d)=D_{\ell_f}(R)z^{\mathrm{cf}}(\widehat d)\)。\(w_\alpha(r):(0,+1)\)。球谐 direction 必须先通过

\[
\zeta_d=\lVert d\rVert/s>\tau_0
\]

的单向量合同；float64/32 的 \(\tau_0\) 为 \(10^{-12}/10^{-5}\)，等号拒绝。

### 3.2 路径等变证明

设输入 \(x\) 和 coefficient filter \(z^{\mathrm{cf}}\) 分别按 \(D_{\mathrm{in}},D_f\) 变换。CG intertwiner 给出

\[
C(D_{\mathrm{in}}\otimes D_f)=D_LC.
\]

径向权重不变，故

\[
m_e(RX)=D_L(R)m_e(X).
\]

该证明依赖本节显式共轭接口、第 17 章点值/系数映射和第 18 章 CG 快轴。若把 \(y^{\mathrm{pv}}\) 直接送入 coefficient CG，第二输入实际按 \(D_f^*\) 变换，以上等式一般不成立；只验证实基或 z 轴选择定则也不足以推出上式。

### 3.3 聚合与同型混合

\[
a_{i,\alpha M}
=
\sum_{e:\operatorname{receiver}(e)=i}m_{e,\alpha M}.
\]

线性性给

\[
a_i(RX)=D_La_i(X).
\]

同型权重

\[
h_{i,\nu M}
=
\sum_\alpha W_{\nu\alpha}^{(L,p)}a_{i,\alpha M}
\]

只作用 multiplicity 轴，与 component 表示对易。空 sum 为零。

### 3.4 门控和失败非线性

偶标量门控

\[
\widetilde h=g_+h,\qquad g_+:(0,+1)
\]

保持 \((L,p)\)。一般 \(g:(0,p_g)\) 给 \((L,p_gp)\)；伪标量 \(1+s_-\) 无确定宇称必须拒绝。逐 component 平方、ReLU 或不同 \(M\) 使用不同任意权重一般不与 \(D_L\) 对易。

### 3.5 节点置换

对节点置换 \(\pi\)，边端点同步变为 \((\pi(i),\pi(j),n)\)，节点 tensor 和输出按 \(\pi\) 重排。共享路径函数和 receiver sum 保证

\[
\Phi(P_\pi X)=P_\pi\Phi(X).
\]

整数 shift 不随节点编号变换；完整 edge-row 映射必须保留。

### 3.6 D-E06 可独立复算正反例

**两边实消息正例。** 一个 receiver 有两条入边，取

\[
\widehat d_1=(1,0,0)^{\mathsf T},
\quad
\widehat d_2=(0,1,0)^{\mathsf T},
\quad
(s_1,s_2)=(2,3),
\quad
(w_1,w_2)=(1,1/2).
\]

在 \(0\otimes1\to1\) 的等价实笛卡尔路线中，逐边消息和 receiver sum 为

\[
m_1=(2,0,0)^{\mathsf T},
\qquad
m_2=(0,3/2,0)^{\mathsf T},
\qquad
a_i=(2,3/2,0)^{\mathsf T}.
\]

主动 \(R_z(\pi/2)\) 后，逐层残差

\[
\rho(m'_1,Rm_1)=0,
\quad
\rho(m'_2,Rm_2)=0,
\quad
\rho(a'_i,Ra_i)=0,
\]

且 \(a'_i=(-3/2,2,0)^{\mathsf T}\)。这同时固定 edge direction、逐边输出和 receiver sum，不能只比较最终 shape。

**一般轴复 coefficient 正例。** 取

\[
\widehat d=(1,2,3)^{\mathsf T}/\sqrt{14},
\qquad
\widehat a=(2,-1,1)^{\mathsf T}/\sqrt6,
\qquad
\theta=0.73.
\]

使用 DLMF-CS \(\ell=1\) 点值、\(m=(-1,0,1)\) 与 `complex128`，有

\[
y^{\mathrm{pv}}_1(\widehat d)
=
\begin{pmatrix}
0.09233720-0.18467439i\\
0.39175354\\
-0.09233720-0.18467439i
\end{pmatrix},
\]

\[
z^{\mathrm{cf}}_1(R\widehat d)
=
\begin{pmatrix}
-0.03335607+0.00015643i\\
0.48631997\\
0.03335607+0.00015643i
\end{pmatrix}.
\]

独立按全精度计算得到

\[
\rho\!\left(z^{\mathrm{cf}}_1(R\widehat d),
D^{(1)}(R)z^{\mathrm{cf}}_1(\widehat d)\right)
=6.62\times10^{-17}.
\]

若错误地把点值 \(y^{\mathrm{pv}}\) 当作 coefficient 输出，则定向故障为

\[
\rho\!\left(y^{\mathrm{pv}}_1(R\widehat d),
D^{(1)}(R)y^{\mathrm{pv}}_1(\widehat d)\right)
=0.5219896443,
\]

远高于 float64 门限。该故障必须进入 T-E08；若改变 edge row、\(m\) 顺序、filter version/hash 或 provenance，应由 T-E12 拒绝。

## 4. D-E05 Hamiltonian 双侧协变

**输入、输出与成立条件。** 输入是逐边块 \(H_e:\mathcal V_j\to\mathcal V_i\)、与左右完整 shell 顺序一致的幺正/正交表示 \(D_i,D_j\)，以及可双向恢复的 edge、shell、actual-orbital、mask 和 basis provenance。要求 dtype/基一致、左右作用方向正确、逆边完整且 batch/padding 先切除 inactive 区。输出与输入块 shape 相同。最终不变量是 \(H'_e=D_iH_eD_j^\dagger\)、逆边共轭相容、实—复路线一致和奇异值保持；入口为 T-E06，行/schema 拒绝同时进入 T-E12。

### 4.1 从轨道基变换推出块公式

令轨道基列在主动旋转下由 \(D_i,D_j\) 表示。矩阵块映射

\[
H_{ij}:\mathcal V_j\to\mathcal V_i
\]

必须满足交换图

\[
D_iH_{ij}=H_{ij}'D_j.
\]

右乘 \(D_j^\dagger=D_j^{-1}\) 得

\[
\boxed{H_{ij}'=D_iH_{ij}D_j^\dagger}.
\]

这也说明左右方向由映射的陪域/定义域决定，不是可交换的装饰。

### 4.2 shape 表

设 \(n_s=1,n_p=3,n_d=5\)。单壳层 \(H_{\ell_i\ell_j}\) 的 shape 为

\[
(2\ell_i+1)\times(2\ell_j+1).
\]

所以 \(s-p\) 是 \(1\times3\)，\(p-d\) 是 \(3\times5\)，\(d-p\) 是 \(5\times3\)。非方块特别适合定向故障，因为错误交换通常直接 shape 失败。

### 4.3 多壳层

对 shell 集 \(\mathcal S_i\)，

\[
D_i=\bigoplus_{\alpha\in\mathcal S_i}D^{(\ell_\alpha)}.
\]

Hamiltonian 按 shell-pair 网格分块。每个 shell 的 multiplicity、实际轨道 ID、basis family、component 顺序和 mask 必须保留；相同 \(\ell\) 的两个 shell 不得合并。

### 4.4 实/复基相容

令

\[
H_{\mathrm c}=K_iH_{\mathrm r}K_j^\dagger,
\qquad
D_{\mathrm c}=K D_{\mathrm r}K^\dagger.
\]

则

\[
\begin{aligned}
H_{\mathrm c}'
&=D_{i,\mathrm c}H_{\mathrm c}D_{j,\mathrm c}^\dagger\\
&=K_iD_{i,\mathrm r}H_{\mathrm r}D_{j,\mathrm r}^{\mathsf T}K_j^\dagger\\
&=K_iH_{\mathrm r}'K_j^\dagger.
\end{aligned}
\]

因此实/复两路线严格相容。复基右侧若误用普通转置，上述等式一般失败。

## 5. Hermiticity、逆边与周期身份

### 5.1 逆边

正向 \((i,j,n)\) 的逆边为 \((j,i,-n)\)。Hermiticity 给

\[
H_{ji,-n}=H_{ij,n}^\dagger.
\]

旋转后

\[
\begin{aligned}
H_{ji,-n}'
&=D_jH_{ij,n}^\dagger D_i^\dagger\\
&=(D_iH_{ij,n}D_j^\dagger)^\dagger.
\end{aligned}
\]

所以双侧协变不破坏共轭配对。

### 5.2 完整边身份

边 payload 为

\[
[\text{stageD-edge-v1},
\text{structure ID},i,j,n_x,n_y,n_z].
\]

旋转前后 payload、edge ID、row order 和 inverse mapping 不变。换胞时 shift 需按阶段 D 先回拉规范代表再配对；旋转测试不得把换胞规则混入。

### 5.3 统一行映射

prediction、target、mask、block shape、shell pair、actual orbital identity、edge key/ID、位移和 provenance 必须共享长度 \(E\) 的行轴。所有边级数组严格为 \(E\) 行；多/少一行或独立滚动必须拒绝。

## 6. 固定 \(4\times8\) 合成块

取

\[
H_{ab}=0.1(8a+b+1),
\qquad
a=0,\ldots,3,\quad b=0,\ldots,7.
\]

receiver 顺序为 \(s,p_x,p_y,p_z\)，sender 顺序为 \(p_x,p_y,p_z,d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2}\)。取

\[
\widehat a=(1,2,3)^{\mathsf T}/\sqrt{14},
\qquad\theta=0.7,
\]

\[
D_i=1\oplus R,\qquad D_j=R\oplus D^d(R).
\]

直接复算的错误相对正确 \(D_iHD_j^{\mathsf T}\) 的归一化残差为：

\[
\rho(D_iH,H')=0.5461588700,
\]

\[
\rho(HD_j^{\mathsf T},H')=0.05995264977,
\]

\[
\rho(D_iHD_j,H')=0.9216691727.
\]

逆边旋转与正确块转置最大差为 \(8.88\times10^{-16}\)。这些是 T-E06 的解析/数值锚点，不是正式材料统计。

## 7. batch、mask 与 padding

### 7.1 concat

concat 节点 tensor 的第一轴是

\[
N_{\mathrm{tot}}=\sum_gN_g,
\]

边轴是 \(E_{\mathrm{tot}}\)。graph ID、count 和 offset 必须一致，边端点落在所属图节点区间。重复 structure ID 允许，但 graph slot 不得混淆。

### 7.2 padded

按类型存储

\[
x^{(\ell,p)}
\in
\mathbb F^{B\times N_{\max}\times n_{\ell,p}^{\max}\times(2\ell+1)}.
\]

active node/multiplicity mask 应为 prefix；component shell 全真或全假。inactive 值可为 NaN/极大哨兵，但必须先用 mask 索引切出，再进入任何数值 kernel。禁止先乘再乘零 mask，因为 \(0\cdot\mathrm{NaN}\) 仍是 NaN。

### 7.3 Hamiltonian blocks

非方 shell-pair块可用 packed 行或 padded

\[
(B,E_{\max},P_i^{\max},P_j^{\max})
\]

存储；两条轨道轴的 mask、实际轨道身份和 shell span 必须可反解。prediction 的两维宽度必须与左右 component mask 一致。

## 8. D-E07 局部架与回拉

**输入、输出与成立条件。** 输入是有限列向量 \(u_q,v_q\in\mathbb R^3\)、有限正尺度 \(s_q\)、与端点 shell 顺序相同的局部表示 \(U_i,U_j\)，以及全局块 \(H_e\) 的完整身份。仅在两向量均通过无量纲零长度门控、归一化叉积严格位于近共线阈值接受侧、唯一 Gram-Schmidt 右手架满足 \(F^{\mathsf T}F=I\)、\(\det F=+1\)，且不存在任意后备轴时成立。输出是局部不变块 \(\overline H\) 和回拉全局块；最终不变量是 \(F(RX)=RF(X)\)、\(\overline H(RX)=\overline H(X)\)、回拉得到 \(D_iH D_j^\dagger\)。入口为 T-E09，轨道/edge/schema 一致性同时进入 T-E12。

### 8.1 局部不变量

令 \(F_i,F_j\in SO(3)\) 且

\[
F_i(RX)=RF_i(X).
\]

表示矩阵满足

\[
U_i(RX)=D_i(R)U_i(X).
\]

局部块

\[
\overline H=U_i^\dagger HU_j
\]

在全局旋转下：

\[
\begin{aligned}
\overline H'
&=U_i'^\dagger H'U_j'\\
&=U_i^\dagger D_i^\dagger
(D_iHD_j^\dagger)
D_jU_j\\
&=\overline H.
\end{aligned}
\]

回拉

\[
H=U_i\overline HU_j^\dagger
\]

因此给出正确双侧协变。

### 8.2 唯一右手架

输入为有限 \(u,v\) 和有限正 \(s\)。先验证

\[
\zeta_u=\lVert u\rVert/s,\quad
\zeta_v=\lVert v\rVert/s.
\]

若 \(\zeta\le\tau_0\) 拒绝，float64/32 的 \(\tau_0=10^{-12}/10^{-5}\)。归一化后

\[
\eta=\lVert\widehat u\times\widehat v\rVert.
\]

若 \(\eta\le\tau_{\mathrm{frame}}\) 拒绝，float64/32 的 \(\tau_{\mathrm{frame}}=10^{-8}/10^{-4}\)。等号均拒绝。

接受时唯一构造

\[
e_1=\widehat u,
\]

\[
e_2=
\frac{\widehat v-(e_1^{\mathsf T}\widehat v)e_1}
{\lVert\widehat v-(e_1^{\mathsf T}\widehat v)e_1\rVert},
\qquad
e_3=e_1\times e_2.
\]

### 8.3 失败域

必须拒绝：

- \(s\le0\) 或非有限；
- \(u,v\) rank/shape 错误或含非有限值；
- \(\zeta\) 位于阈值拒绝侧；
- \(\eta\) 位于阈值拒绝侧；
- 任意后备轴；
- \(F^{\mathsf T}F\) 或 \(\det F=+1\) 失败；
- 回拉左右作用、转置/共轭或 shell 顺序错误。

### 8.4 比较边界

局部路线和显式等变路线必须在相同输入图、目标、dtype、预算和评价脚本下比较。局部架拒绝样例应报告覆盖率/拒绝率，但不能静默填补；显式等变路线也需单独验证方向零长度和 CG/身份故障。

### 8.5 D-E07 非退化 \(4\times8\) 局部化—回拉正例

取 receiver 架输入

\[
u_i=(1,0,0)^{\mathsf T},
\qquad
v_i=(1,1,0)^{\mathsf T}/\sqrt2,
\]

sender 架输入

\[
u_j=(0,1,0)^{\mathsf T},
\qquad
v_j=(0,1,1)^{\mathsf T}/\sqrt2,
\]

并令两个尺度均为 1。唯一构造给出

\[
F_i=I,
\qquad
F_j=
\begin{pmatrix}
0&0&1\\
1&0&0\\
0&1&0
\end{pmatrix}.
\]

对第 6 节的 \(4\times8\) 块，取

\[
U_i=1\oplus F_i,
\qquad
U_j=F_j\oplus D^d(F_j).
\]

局部块为

\[
\overline H=U_i^{\mathsf T}HU_j
=
\begin{pmatrix}
0.2&0.3&0.1&0.5&0.6&0.4&-1.04282032&0.20621778\\
1.0&1.1&0.9&1.3&1.4&1.2&-2.13564065&0.49903811\\
1.8&1.9&1.7&2.1&2.2&2.0&-3.22846097&0.79185843\\
2.6&2.7&2.5&2.9&3.0&2.8&-4.32128129&1.08467875
\end{pmatrix}.
\]

再取轴 \((1,2,-1)^{\mathsf T}/\sqrt6\)、角 \(0.61\) 的一般主动旋转。以全精度 `float64` 复算，局部不变残差、原架局部化—回拉残差、旋转后全局回拉残差分别为

\[
3.34\times10^{-16},
\qquad
2.73\times10^{-16},
\qquad
2.07\times10^{-16}.
\]

这些残差分别检查局部预测、\(4\times8\) 左右轨道作用和最终全局协变，任何一个都不能由另一个替代。

### 8.6 阈值、后备轴和正负近共线定量失败

float64 取 \(u=(1,0,0)^{\mathsf T}\) 与

\[
v_\varepsilon=(1,\varepsilon,0)^{\mathsf T}/\sqrt{1+\varepsilon^2}.
\]

令 \(\tau=10^{-8}\)。按实际 \(\eta=\lVert\widehat u\times\widehat v\rVert\)，\(\eta=\tau\) 必须拒绝，不能因舍入前参数名为 \(\tau\) 就接受；\(\eta>\tau\) 才进入构架。若在退化侧使用固定全局 \(e_y\) 后备轴，对 \(R_x(\pi/2)\) 有

\[
\lVert e_y-R_x(\pi/2)e_y\rVert_2
=\sqrt2,
\]

而协变后备轴应是 \(R_x(\pi/2)e_y\)，故失败是有限量而非浮点噪声。

即使 \(|\varepsilon|>\tau\) 且两侧均被接受，\(\varepsilon\to0^+\) 与 \(\varepsilon\to0^-\) 分别给

\[
F_+=I,
\qquad
F_-=\operatorname{diag}(1,-1,-1),
\]

从而

\[
\lVert F_+-F_-\rVert_F=2\sqrt2=2.8284271247.
\]

所以近共线域存在有限跳变；阈值只能明确拒绝域，不能把该路线宣称为全空间连续。T-E09 必须同时执行阈值等号、正负两侧、固定后备轴和错误回拉故障。

## 9. 误差和成本分层

### 9.1 残差

统一

\[
\rho(A,B)=
\frac{\lVert A-B\rVert_F}
{\max(1,\lVert A\rVert_F,\lVert B\rVert_F)}.
\]

float64/32 接受阈值为 \(5\times10^{-12}/5\times10^{-6}\)。报告逐层、端到端、Hamiltonian 块、inverse-pair 和 local pullback 残差。

### 9.2 模型误差

合成 target 误差例如

\[
\mathrm{MAE},
\quad
\mathrm{MSE},
\quad
\frac{\lVert\widehat H-H\rVert_F}{\max(1,\lVert H\rVert_F)}
\]

与等变残差分列。等变只约束变换关系，不保证接近 target。

### 9.3 D-E09 成本

消息路径、同型混合、receiver 聚合、Hamiltonian 双侧乘法和局部架是不同操作图。每项从实际 shape 计算 MAC/FLOP；complex 操作须展开。数组按名称、shape、dtype、nbytes 报告，区分 total/reference peak。T-E10 的 144 点 reference kernel 口径不能被本章局部计数替代。

## 10. T-E 映射与故障矩阵

| 推导 | 入口 | 正确证据 | 强制失败 |
|---|---|---|---|
| D-E05 双侧块 | T-E06 | 多 shape、实/复、逆边、完整 provenance | 只左乘、漏 \(\dagger\)、左右交换、轨道错位 |
| D-E06 消息层 | T-E08 | 逐层/端到端旋转、反演、置换 | 错 CG、方向错位、高阶逐分量非线性、伪标量坏门控 |
| D-E07 局部架 | T-E09 | 非退化架、局部不变、全局回拉 | 零/共线/阈值等号、后备轴、错误回拉 |
| D-E09 成本 | T-E10 | 144 点、MAC/FLOP/聚合/bytes 分层 | scan/config 混用、漏数组、wall-time 入 hash |
| schema/身份 | T-E12 | 完整 edge/shell/mask/row | padding 穿透、多余行、独立滚动、非法 dtype/shape |

## 11. 分项最终不变量、残差对象与定义域

| 推导 | 可独立复算最终不变量 | 残差对象 | 成立定义域与退出门控 |
|---|---|---|---|
| D-E05 | \(H'_e=D_iH_eD_j^\dagger\)；\(H'_{ji,-n}=(H'_{ij,n})^\dagger\)；实—复路线相容 | 非方块旋转、inverse pair、basis-route、奇异值及三种定向故障残差 | 完整 shell/轨道/basis/edge provenance、合法 mask/dtype；T-E06/T-E12 |
| D-E06 | \(z^{\mathrm{cf}}(R\widehat d)=Dz^{\mathrm{cf}}(\widehat d)\)；\(m'=D_Lm\)；\(a'=D_La\)；节点置换/反演相容 | filter、逐边消息、聚合、端到端、直接输入 \(D^*\) 点值、错误 CG/非线性/门控残差 | 非零方向、冻结点值—coefficient 接口、合法 CG/宇称/完整 edge row；T-E08/T-E12 |
| D-E07 | \(F'=RF\)；\(\overline H'=\overline H\)；\(H'=U_i'\overline H U_j'^\dagger=D_iHD_j^\dagger\) | frame、局部块、\(4\times8\) 回拉、阈值等号、后备轴、正负近共线跳变残差 | 有限正尺度、两向量非零、\(\eta>\tau_{\mathrm{frame}}\)、唯一右手架；T-E09/T-E12 |

因此，等变消息只在复点值先显式转换为 coefficient filter 后，才能由 CG intertwiner 和对易操作复合得到。Hamiltonian 块作为 sender 到 receiver 的线性映射必然双侧变换，并与周期逆边、Hermiticity 和轨道 provenance 共享身份。局部架路线只在唯一协变架的非退化定义域内通过不变预测和回拉实现同一公式；拒绝域和有限跳变必须作为结果报告，而不能用后备轴隐藏。
