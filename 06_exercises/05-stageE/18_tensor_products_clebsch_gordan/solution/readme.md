# 第 18 章参考解答

## A18-01 张量积维数与索引

\(\ell_1=2,\ell_2=1\) 时

\[
n_{\mathrm{prod}}=(2\cdot2+1)(2\cdot1+1)=5\cdot3=15.
\]

三角条件给出

\[
L=1,2,3.
\]

输出维数为

\[
(2\cdot1+1)+(2\cdot2+1)+(2\cdot3+1)
=3+5+7=15.
\]

因为 \(m_2\) 是快轴，

\[
a(m_1,m_2)
=(m_1+2)3+(m_2+1).
\]

所以

\[
a(-2,-1)=0,
\]

\[
a(0,1)=2\cdot3+2=8,
\]

\[
a(2,0)=4\cdot3+1=13.
\]

两种 Kronecker 顺序都有相同 shape \(15\)，并且都能容纳相同数量的零/非零项；若 CG 列未同步置换，数组仍可乘但每个数对应错误的 \((m_1,m_2)\)。因此必须检查显式索引、选择定则、规范表和一般轴 intertwiner。

## A18-02 选择定则与 CG--\(3j\)

规范关系为

\[
C^{LM}_{\ell_1m_1,\ell_2m_2}
=
(-1)^{\ell_1-\ell_2+M}\sqrt{2L+1}
\begin{pmatrix}
\ell_1&\ell_2&L\\
m_1&m_2&-M
\end{pmatrix}.
\]

逐项判断：

- \(C^{20}_{1\,1,1\,-1}\)：三角条件满足且 \(M=0=1+(-1)\)，可能非零；规范值为 \(1/\sqrt6\)。
- \(C^{21}_{1\,1,1\,-1}\)：要求 \(M=1\)，但 \(m_1+m_2=0\)，必为零。
- \(C^{30}_{1\,0,1\,0}\)：\(1\otimes1\) 只允许 \(L=0,1,2\)，三角条件失败，必为零。
- \(C^{1,-1}_{1\,0,1\,-1}\)：三角条件满足且 \(-1=0+(-1)\)，可能非零；规范值为 \(1/\sqrt2\)。

选择定则是必要条件；满足选择定则并不单独确定系数数值。

## A18-03 构造 \(1\otimes1\) 的三个 \(M=0\) 行

按题面列出的顺序，三个规范行是

\[
|0,0\rangle
=
\frac1{\sqrt3}
\begin{pmatrix}
1\\-1\\1
\end{pmatrix},
\]

\[
|1,0\rangle
=
\frac1{\sqrt2}
\begin{pmatrix}
-1\\0\\1
\end{pmatrix},
\]

\[
|2,0\rangle
=
\frac1{\sqrt6}
\begin{pmatrix}
1\\2\\1
\end{pmatrix}.
\]

范数平方分别为

\[
\frac{1+1+1}{3}=1,
\qquad
\frac{1+1}{2}=1,
\qquad
\frac{1+4+1}{6}=1.
\]

行内积为

\[
\frac{-1+0+1}{\sqrt6}=0,
\]

\[
\frac{1-2+1}{\sqrt{18}}=0,
\]

\[
\frac{-1+0+1}{\sqrt{12}}=0.
\]

\(L=0\) 行由锚点

\[
C^{00}_{1\,1,1\,-1}=+1/\sqrt3
\]

直接定相位；\(L=1,M=0\) 行的整体相位由同一 \(L=1\) 通道的锚点

\[
C^{11}_{1\,1,1\,0}=+1/\sqrt2
\]

经降算符传递；\(L=2,M=0\) 行由

\[
C^{22}_{1\,1,1\,1}=1
\]

经降算符传递。

## A18-04 正交、完整性与 intertwiner

\[
CC^{\mathsf T}=I
\]

表示不同 \((L,M)\) 输出态正交且归一。

\[
C^{\mathsf T}C=I
\]

表示所有允许输出通道对整个乘积基完备；删去完整 \(L\) 块时第一式在保留行上仍可成立，而第二式必失败。

\[
C(D^{(1)}\otimes D^{(1)})
=(1\oplus D^{(1)}\oplus D^{(2)})C
\]

表示耦合矩阵是群作用 intertwiner，即旋转后耦合与耦合后按输出类型旋转相同。

只检查行范数发现不了不同行不正交；只检查三个锚点发现不了非锚点局部错误；只检查 \(R_z\) 发现不了与对角 \(D(R_z)\) 对易的部分 \(M\) 相位变异。因此 T-E05 必须同时检查全表、零模式、两类正交关系和一般轴 intertwiner。

## A18-05 输入交换与宇称

交换相位为

\[
(-1)^{\ell_1+\ell_2-L}
=(-1)^{2-L}.
\]

所以：

- \(L=0\)：相位 \(+1\)，对称；
- \(L=1\)：相位 \(-1\)，反对称；
- \(L=2\)：相位 \(+1\)，对称。

输入宇称相乘为

\[
p_{\mathrm{out}}=(-1)(-1)=+1.
\]

三条输出类型为

\[
(0,+1),\qquad(1,+1),\qquad(2,+1).
\]

\((1,+1)\) 在正旋转下与普通向量具有同一 \(D^{(1)}\)，但反演时不变，因此是轴向量。只做 \(SO(3)\) 测试不能区分 \((1,+1)\) 与 \((1,-1)\)；必须加入至少一个 \(\det R=-1\) 的 \(O(3)\) 变换。

## A18-06 合法通道相位与错误局部相位

变异 A 把整个 \(L=2\) 块乘 \(-1\)。它仍保持

\[
CC^{\mathsf T}=I,\qquad C^{\mathsf T}C=I
\]

和 intertwiner，因为 \(-I_5\) 与所有 \(D^{(2)}(R)\) 对易；但 DLMF 规范表和 \(L=2\) 锚点失败。报告应写“规范表不一致、等变性通过”，不得写成数学等变错误。

变异 B 只翻 \(L=2,M=0\) 行。左乘仍是正交行变换，所以两类正交关系保持；但该行相位矩阵一般不与非对角 \(D^{(2)}(R)\) 对易，故一般轴 intertwiner 失败。规范表也失败。

变异 C 只翻一个非零系数。它通常破坏行间正交、列完备和一般轴 intertwiner，同时逐项规范表失败。正文例 18-8 给出 \(L=0,M=0\) 与 \(L=2,M=0\) 行内积变为 \(2\sqrt2/3\) 的显式见证。

## A18-07 实笛卡尔三通道

给定

\[
u=(1,0,1)^{\mathsf T},
\qquad
v=(0,2,1)^{\mathsf T},
\]

点积为

\[
u\cdot v=1.
\]

所以

\[
z_{00}=-\frac1{\sqrt3}.
\]

叉积为

\[
u\times v
=
\begin{pmatrix}
0\cdot1-1\cdot2\\
1\cdot0-1\cdot1\\
1\cdot2-0\cdot0
\end{pmatrix}
=
\begin{pmatrix}
-2\\-1\\2
\end{pmatrix}.
\]

对称部分为

\[
\frac12(uv^{\mathsf T}+vu^{\mathsf T})
=
\begin{pmatrix}
0&1&1/2\\
1&0&1\\
1/2&1&1
\end{pmatrix}.
\]

减去 \(I/3\) 得

\[
Q=
\begin{pmatrix}
-1/3&1&1/2\\
1&-1/3&1\\
1/2&1&2/3
\end{pmatrix}.
\]

显然 \(Q^{\mathsf T}=Q\)，且

\[
\operatorname{tr}Q=-\frac13-\frac13+\frac23=0.
\]

交叉复算路线为：

\[
x=K_1u,\qquad y=K_1v,
\]

直接求 \(C(x\otimes y)\)；另一方面用 \(-u\cdot v/\sqrt3\)、\(-i(u\times v)/\sqrt2\) 和

\[
q_a=\operatorname{tr}(B_a^{\mathsf T}Q)
\]

构造实通道。对 \(L=2\)，冻结规范不是“拟合后相等”，而是精确矩阵合同

\[
\boxed{
z^{(2)}
=
C^{(2)}
\left[(K_1u)\otimes(K_1v)\right]
=K_2q
}.
\]

比例为 \(+1\)。测试必须直接逐项比较，不得对每个样例拟合比例或相位。例 18-6 的另一固定向量使五个 \(q_a\) 全部非零，并给出完整五分量锚点；错误比例 \(\sqrt2\) 和局部 \(M\) 相位必须失败。若整体更换 \(L=2\) 基相位，必须同步变换 CG 规范身份、\(K_2\) 映射及全部下游对象。

## A18-08 multiplicity、路径和裁剪

\((1,-1)\otimes(2,+1)\) 允许

\[
L=1,2,3,
\]

且所有输出宇称为

\[
p_{\mathrm{out}}=(-1)(+1)=-1.
\]

输出类型为

\[
(1,-1),\qquad(2,-1),\qquad(3,-1).
\]

每个输入副本对产生每个允许 \(L\) 的一个路径，因此每个 \(L\) 的原始路径 multiplicity 为

\[
n_1n_2=3\cdot2=6.
\]

全部三种 \(L\) 合计 \(18\) 条路径。若只保留 \(L=1,3\)，则保留 \(12\) 条。每条保留路径仍可严格等变，但映射不再是完整 \(1\otimes2\) 分解；被删 \(L=2\) 可能降低表达力，不能由等变性通过推出“无性能损失”。

最小 provenance 包括：两个输入的 node/edge identity、\((\ell,p,\mu)\)、component 顺序，输出 \((L,p,\nu)\)，CG 表版本/hash、\(m_2\) 快轴、输入交换方向，allowed/kept 状态，路径权重身份，dtype/shape/mask/容差，以及完整 edge-row 映射。

三个最高 \(M=L\) 规范行为

\[
\begin{aligned}
|1,1\rangle
&=
\sqrt{\frac35}|-1,2\rangle
-\sqrt{\frac3{10}}|0,1\rangle
+\frac1{\sqrt{10}}|1,0\rangle,\\
|2,2\rangle
&=
-\sqrt{\frac23}|0,2\rangle
+\frac1{\sqrt3}|1,1\rangle,\\
|3,3\rangle
&=|1,2\rangle.
\end{aligned}
\]

范数平方分别为

\[
\frac35+\frac3{10}+\frac1{10}=1,
\qquad
\frac23+\frac13=1,
\qquad1.
\]

交换相位为

\[
(-1)^{1+2-L}=(-1)^{3-L},
\]

所以 \(L=1,3\) 为 \(+1\)，\(L=2\) 为 \(-1\)。固定一般轴 \((1,2,3)/\sqrt{14}\)、角度 \(0.7\) 的归一化 intertwiner 残差锚点为 \(2.64\times10^{-16}\)；错写 Kronecker 轴时为 \(0.9192367498522585\)，遗漏 \(L=2\) 交换负号时最大系数误差为 \(1.6329931618554523\)。T-E05 仍须生成完整 \(15\times15\) 表并验证正交、完备、全表和一般轴。

## A18-09 门控与失败非线性

偶标量 \(g_+:(0,+1)\) 在正旋转和反演下都不变，所以

\[
(gx)'=gD^{(\ell)}x
=D^{(\ell)}(gx).
\]

因此偶标量门控保持类型 \((\ell,p_x)\)。一般门值 \(g:(0,p_g)\) 给出

\[
g\,x^{(\ell,p_x)}
\sim(\ell,p_gp_x).
\]

伪标量门值会翻转输出宇称，不能标成原类型。若输入 \(s_-:(0,-1)\)，奇函数 \(s_-^3\) 仍为伪标量，偶函数 \(s_-^2\) 为偶标量；普通函数

\[
\sigma_{\mathrm{bad}}(s_-)=1+s_-
\]

在反演下变为 \(1-s_-\)，一般既不等于原值也不等于其负值，没有确定宇称，必须拒绝。

对题面向量，

\[
f(u)=(1,4,0)^{\mathsf T}.
\]

\[
Ru=(-2,1,0)^{\mathsf T},
\qquad
f(Ru)=(4,1,0)^{\mathsf T}.
\]

而

\[
Rf(u)=(-4,1,0)^{\mathsf T}.
\]

差为

\[
f(Ru)-Rf(u)=(8,0,0)^{\mathsf T},
\]

绝对二范数为 \(8\)。因此逐分量平方不是一般向量等变非线性。

T-E07/T-E08/T-E12 必须执行偶标量反演正例、合法伪标量奇/偶函数的类型更新和 \(1+s_-\) 拒绝例。图批处理中还须验证门值与特征共享 batch/node/edge 身份、multiplicity 行和 active mask；inactive padding 必须在乘法前切除，非有限 active 值必须拒绝，不能依赖广播自动建立语义对应。

## A18-10 端到端材料与测试合同

消息 contraction 为

\[
m_{ij,\,\nu M}^{(L)}
=
\sum_{\mu,m,m_f}
W_{\nu\mu}^{(L)}
C^{LM}_{\ell_{\mathrm{in}}m,\ell_fm_f}
x_{j,\mu m}^{(\ell_{\mathrm{in}})}
Y_{m_f}^{(\ell_f)}(\widehat d_{ij})
\;w_{\mathrm{rad}}(r_{ij}),
\]

其中只依赖距离的径向因子是偶标量 \((0,+1)\)，输出宇称为

\[
p_{\mathrm{out}}=p_{\mathrm{in}}p_f.
\]

若另外乘以门值 \(g:(0,p_g)\)，一般输出宇称是 \(p_gp_{\mathrm{in}}p_f\)。要求保持原路径宇称时必须使用 \(p_g=+1\)；伪标量门值会翻转类型，而 \(1+s_-\) 这类无确定宇称的门值必须拒绝。

完整 edge identity 固定为

\[
(\text{stageD-edge-v1},
\text{structure ID},
\text{receiver},
\text{sender},
n_x,n_y,n_z).
\]

路径 provenance 至少记录发送节点 shell/multiplicity/component 顺序、filter 类型与方向基版本、输出 \((L,p,\nu,M)\)、CG 表版本/hash、Kronecker 快轴、输入交换方向、径向/同型权重身份、edge-row、dtype/shape/mask/容差和路径裁剪状态。

mask/padding 顺序为：

1. 验证完整 irrep shell 的 component mask 全真或全假；
2. 在 contraction 前切除 inactive padding；
3. 对 active 有限值执行方向 validator、CG contraction 和同型混合；
4. 保持完整 edge key 与行映射进行 receiver 聚合；
5. 按明确槽位回填 inactive padding，并保持全假 mask。

T-E05 的正确检查包括选择定则、全规范表、零模式、\(1\otimes1\) 三锚点、\(1\otimes2\) 三个最高行、交换相位、两类正交关系、一般轴 intertwiner，以及不拟合比例/相位的 \(z^{(2)}=K_2q\)。T-E07/T-E08 逐层及端到端比较正旋转和反演前后消息；T-E12 执行 schema 与全部失败矩阵。

至少六类实际失败注入为：

- 单个非零 CG 系数翻转；
- 固定 \(L\) 的部分 \(M\) 行翻相位；
- Kronecker 快轴错位；
- 输入交换但遗漏 \((-1)^{\ell_1+\ell_2-L}\)；
- \(z^{(2)}=K_2q\) 使用错误比例或局部 \(M\) 相位；
- 高阶分量逐元素非线性；
- 对伪标量施加 \(1+s_-\) 却宣称确定宇称；
- edge-row 或 receiver/sender 方向错位；
- partial component mask；
- NaN/极大 inactive padding 在切除前进入 contraction；
- 旋转时改变完整离散 edge key。

整通道统一相位只应使 canonical-table 检查失败，不能计入 intertwiner 强制失败。

D-E09/T-E10 必须分开记录乘积形成、系数缩放/MAC、真实累加、按冻结口径换算的实 FLOP、receiver 聚合加法、逐数组 nbytes、完整物化 total、参考流式 peak 和排除项。单个 \(1\otimes1\) 副本对若先物化乘积，需要 9 次乘积形成；稀疏投影有 18 个非零项和 9 次同输出累加，零初始化 FMA 口径可写 18 MAC，但不能漏掉前述 9 次乘积。复 MAC 不得直接按实 MAC 的每 MAC=2 FLOP 外推。可选 wall-time 单独报告，不进入确定性 stdout hash；本章子操作图也不得代替 T-E10 的完整 reference kernel 成本。

M8 前不得安装 DeepH/e3nn 本体、下载正式训练数据、生成 DFT 标签，或隐含选择材料体系、DFT/数据后端、DeepH 软件对象和实践版本。本章来源只支持一般 CG/表示论和等变张量积机制，不授权具体实践对象。
