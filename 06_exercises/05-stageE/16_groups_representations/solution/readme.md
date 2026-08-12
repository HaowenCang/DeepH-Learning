# 第 16 章练习：参考解答

## A16-01

线性表示是同态

\[
D:G\to GL(V),
\qquad
D(g_2g_1)=D(g_2)D(g_1),
\qquad
D(e)=I.
\]

核为

\[
\ker D=\{g:D(g)=I\}.
\]

核只有单位元时表示忠实。对任意 \(R_1,R_2\in SO(3)\)，

\[
D^{(0)}(R_2R_1)=1
=1\cdot1
=D^{(0)}(R_2)D^{(0)}(R_1),
\]

故平凡表示合法。其核是整个 \(SO(3)\)，所以不忠实。若标量映射满足

\[
F(RX)=F(X)=D^{(0)}(R)F(X),
\]

它仍严格等变。忠实性描述表示能否区分群元素，等变性描述映射是否 intertwine 两端作用。

## A16-02

不变子空间 \(W\) 满足

\[
D(g)W\subseteq W
\quad\text{对所有 }g.
\]

除零空间和全空间外没有不变子空间的表示不可约。给定直和包含一个一维 \(\ell=0\) 和两个三维 \(\ell=1\) 副本，总维数为

\[
1+3+3=7.
\]

类型与 multiplicity 是

\[
m_0=1,\qquad m_1=2.
\]

两个向量副本可由任意 \(2\times2\) 矩阵 \(W_1\) 混合，但表示分量轴保持单位：

\[
L_1=W_1\otimes I_3.
\]

若两副本宇称不同，则在 \(O(3)\) 下不能无条件这样混合。

## A16-03

\[
D^p(R_z(\pi/2))=
\begin{pmatrix}
0&-1&0\\
1&0&0\\
0&0&1
\end{pmatrix}.
\]

第一、二、三列分别表示

\[
p_x\mapsto p_y,\qquad
p_y\mapsto-p_x,\qquad
p_z\mapsto p_z.
\]

外部列顺序 \((p_y,p_z,p_x)\) 相对项目顺序可用

\[
P=
\begin{pmatrix}
0&1&0\\
0&0&1\\
1&0&0
\end{pmatrix}
\]

表示，即 \(c_{\mathrm{ext}}=Pc_{\mathrm{project}}\)。因此

\[
D_{\mathrm{ext}}=P D_{\mathrm{project}}P^{\mathsf T}.
\]

比较后若要返回项目数组，还必须同步逆置换特征和 provenance。

## A16-04

冻结基为

\[
\begin{aligned}
B_{xy}&=(e_xe_y^{\mathsf T}+e_ye_x^{\mathsf T})/\sqrt2,\\
B_{yz}&=(e_ye_z^{\mathsf T}+e_ze_y^{\mathsf T})/\sqrt2,\\
B_{zx}&=(e_ze_x^{\mathsf T}+e_xe_z^{\mathsf T})/\sqrt2,\\
B_{x^2-y^2}&=(e_xe_x^{\mathsf T}-e_ye_y^{\mathsf T})/\sqrt2,\\
B_{3z^2-r^2}&=(-e_xe_x^{\mathsf T}-e_ye_y^{\mathsf T}+2e_ze_z^{\mathsf T})/\sqrt6.
\end{aligned}
\]

每项显然对称；对角系数之和为零，非对角项的迹也为零。显式内积为

\[
\langle B_{xy},B_{xy}\rangle_F
=\frac12+\frac12=1,
\]

\[
\langle B_{x^2-y^2},B_{3z^2-r^2}\rangle_F
=\frac{-1+1}{\sqrt{12}}=0.
\]

例如 \(B_{xy}\) 与 \(B_{yz}\) 的非零矩阵位置不重叠，故内积为 0。其余组合按同一方式得到

\[
\operatorname{tr}(B_a^{\mathsf T}B_b)=\delta_{ab}.
\]

## A16-05

由正交归一性，

\[
c'_a=\operatorname{tr}(B_a^{\mathsf T}T').
\]

代入 \(T'=RTR^{\mathsf T}\) 与 \(T=\sum_b c_bB_b\)：

\[
\begin{aligned}
c'_a
&=\operatorname{tr}
\left(B_a^{\mathsf T}R
\sum_b c_bB_bR^{\mathsf T}\right)\\
&=\sum_b
\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T})c_b.
\end{aligned}
\]

故

\[
D^d_{ab}(R)
=\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T}).
\]

共轭 \(T\mapsto RTR^{\mathsf T}\) 保持 Frobenius 内积，所以其在正交归一基中的矩阵正交。复合满足

\[
R_2(R_1TR_1^{\mathsf T})R_2^{\mathsf T}
=(R_2R_1)T(R_2R_1)^{\mathsf T},
\]

因此

\[
D^d(R_2R_1)=D^d(R_2)D^d(R_1).
\]

## A16-06

由 \(e_x\mapsto e_y\)、\(e_y\mapsto-e_x\)、\(e_z\mapsto e_z\)：

\[
\begin{aligned}
B_{xy}&\mapsto-B_{xy},&
B_{yz}&\mapsto-B_{zx},\\
B_{zx}&\mapsto B_{yz},&
B_{x^2-y^2}&\mapsto-B_{x^2-y^2},\\
B_{3z^2-r^2}&\mapsto B_{3z^2-r^2}.
\end{aligned}
\]

所以

\[
D^d=
\begin{pmatrix}
-1&0&0&0&0\\
0&0&1&0&0\\
0&-1&0&0&0\\
0&0&0&-1&0\\
0&0&0&0&1
\end{pmatrix}.
\]

逐列为标准正交向量，故 \(D^{d\mathsf T}D^d=I_5\)。其行列式为 1，迹为 \(-1\)。字符公式

\[
\chi^{(2)}(\theta)
=1+2\cos\theta+2\cos2\theta
\]

在 \(\theta=\pi/2\) 时同样给出 \(-1\)。

## A16-07

一般 \(O(3)\) 表示需要 \((\ell,p)\)，其中 \(p=\pm1\) 指定反演作用。由球谐轨道构造的 \(s,p,d\) 专门满足

\[
p_{\mathrm{orbital}}=(-1)^\ell,
\]

故分别为 \(+\)、\(-\)、\(+\)。这不是一般特征对给定 \(\ell\) 的唯一宇称。

\(p\) 轨道和极向量都是 \((1,-)\)，在 \(Q=-I\) 下乘 \(-I_3\)。轴向量是 \((1,+)\)，在反演下乘 \(+I_3\)。对所有 \(R\in SO(3)\)，两种向量都使用同一个三维 \(R\)，所以只测正旋转无法区分它们。

## A16-08

配置 A：

\[
n_A=3+3\cdot2+5\cdot2=19,
\]

\[
N_{\mathrm{param},A}=3^2+2^2+2^2=17.
\]

float64 单节点字节为

\[
19\cdot8=152,
\]

\(N=4\) 的节点值数组为

\[
4\cdot152=608\ \mathrm{bytes}.
\]

配置 B：

\[
n_B=5+3\cdot4+5\cdot3=32,
\]

\[
N_{\mathrm{param},B}=5^2+4^2+3^2=50.
\]

float32 单节点字节为

\[
32\cdot4=128,
\]

\(N=7\) 时为

\[
7\cdot128=896\ \mathrm{bytes}.
\]

这些数字只含节点连续值和纯同型线性权重，不含 edge、球谐、CG contraction、输出、mask、provenance、中间数组或运行时开销，因此不能作为 T-E10 的端到端 total/peak。

## A16-09

在单位旋转，

\[
\widetilde D_{ab}(I)
=\operatorname{tr}(C_a^{\mathsf T}C_b)
=G_{ab}.
\]

给定缩放产生

\[
\widetilde D(I)
=\operatorname{diag}(4,1,1,1,1).
\]

差矩阵 Frobenius 范数为 3，\(\lVert\widetilde D(I)\rVert_F=\sqrt{20}\)，故

\[
\rho(\widetilde D(I),I_5)
=\frac3{\sqrt{20}}
\approx0.6708203932.
\]

该结果只证明“把正交归一投影公式用于非正交基”错误。非正交基仍可承载表示；应使用 Gram 逆

\[
c=G^{-1}b,
\qquad
b_a=\langle C_a,T\rangle_F,
\]

或构造对偶基，也可恢复项目冻结的正交归一 \(B_a\)。

## A16-10

逐项判断：

1. shape \(5\times5\) 只说明数组大小可能对应 \(\ell=2\)，不确定基函数、顺序、相位或作用方向；
2. 正交性说明每个样本近似保持内积，但不能证明单位元、复合顺序、宇称或与几何旋转的对应；
3. 总维数相同不能识别壳层 multiplicity、shell ID、component index 和 orbital ID；
4. Frobenius 范数是左右幺正作用下的必要弱不变量，许多错误块也具有同一范数。

接入门控应冻结并验证：

- 五个实际基函数与归一化，外部基到项目基的显式置换—符号或一般基变换；
- 列为输入、行为输出的数组轴语义；
- \(D(I)=I\)、有限性、dtype、严格 shape、正交性与
  \[
  D(R_2R_1)=D(R_2)D(R_1);
  \]
- 项目 \(R_z(\pi/2)\) 五维锚点和非交换旋转；
- \(O(3)\) 下的 \((\ell,p)\) 与反演夹具；
- multiplicity、shell/component/orbital ID、mask 和表示矩阵的统一行映射；
- Hamiltonian 块
  \[
  H_{ij}(RX)=D_iH_{ij}(X)D_j^\dagger
  \]
  的两端维数、轨道顺序和完整 edge provenance；
- float64/32 的归一化残差阈值；
- 错序、漏归一化、错误 \(R^{\mathsf T}BR\)、只左乘、错宇称和静默广播的故障注入。

只有这些对象同时通过，才有证据支持项目约定下的表示兼容；仍不能推出任何 DeepH/e3nn 软件版本、正式数据、材料或 DFT 设置已经验证。
