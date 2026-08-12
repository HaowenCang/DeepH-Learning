# 第 15 章练习：参考解答

## A15-01

主动旋转改变物理对象相对固定坐标轴的方向：

\[
v'=Rv.
\]

被动坐标变换保持物理对象不动，只改变坐标基；若新基由旧基旋转 \(R\) 得到：

\[
v_{\mathrm{new}}=R^{\mathsf T}v_{\mathrm{old}}.
\]

映射 \(F\) 对输入/输出表示 \(\rho_{\mathrm{in/out}}\) 等变，当

\[
F(\rho_{\mathrm{in}}(g)x)
=\rho_{\mathrm{out}}(g)F(x).
\]

若 \(\rho_{\mathrm{out}}(g)=I\)，即得

\[
F(\rho_{\mathrm{in}}(g)x)=F(x),
\]

故不变性是平凡输出表示下的等变。

## A15-02

\[
Rv=
\begin{pmatrix}
-2\\1\\3
\end{pmatrix},
\qquad
R^{\mathsf T}v=
\begin{pmatrix}
2\\-1\\3
\end{pmatrix}.
\]

第一式旋转向量，第二式把同一物理向量重新表示在旋转后的坐标基中；作用对象不同。

## A15-03

由

\[
r_{\mathrm{col}}=A^{\mathsf T}f_{\mathrm{col}}
\]

和

\[
r'_{\mathrm{col}}=RA^{\mathsf T}f_{\mathrm{col}}
\]

转置得

\[
r'_{\mathrm{row}}=f_{\mathrm{row}}AR^{\mathsf T}.
\]

因此

\[
A'=AR^{\mathsf T}.
\]

左乘 \(RA\) 作用在晶格行索引上；除特殊 \(A,R\) 外，它不等于把每条行晶格矢量的列形式乘 \(R\)。

## A15-04

由 \(Q^{\mathsf T}Q=I\)：

\[
\lVert Qu\rVert_2^2
=u^{\mathsf T}Q^{\mathsf T}Qu
=\lVert u\rVert_2^2,
\]

\[
(Qu)^{\mathsf T}(Qv)=u^{\mathsf T}v,
\]

\[
\lVert Qu-Qv\rVert_2
=\lVert Q(u-v)\rVert_2
=\lVert u-v\rVert_2.
\]

没有使用 \(\det Q=1\)，故结论对整个 \(O(3)\) 成立。

## A15-05

利用

\[
\varepsilon_{abc}Q_{bj}Q_{ck}
=\det(Q)Q_{ai}\varepsilon_{ijk}
\]

可得

\[
[(Qu)\times(Qv)]_a
=\det(Q)[Q(u\times v)]_a.
\]

当 \(Q\in SO(3)\) 时 \(\det Q=1\)，轴向量和极向量都按 \(Q\) 变换；只有加入 \(\det Q=-1\) 的反射/反演才可区分。

## A15-06

\[
T'=u'v'^{\mathsf T}
=(Qu)(Qv)^{\mathsf T}
=QTQ^{\mathsf T}.
\]

循环迹给出

\[
\operatorname{tr}(T')
=\operatorname{tr}(Q^{\mathsf T}QT)
=\operatorname{tr}(T).
\]

同理

\[
\lVert T'\rVert_F^2
=\operatorname{tr}(T'^{\mathsf T}T')
=\operatorname{tr}(T^{\mathsf T}T).
\]

若 \(T\) 对称，只左乘 \(QT\) 一般不再对称；它也不满足两次旋转的正确二阶张量复合。

## A15-07

行晶格旋转为

\[
A'=AR^{\mathsf T}.
\]

于是

\[
\begin{aligned}
d'_{ijn,\mathrm{row}}
&=(f_j+n-f_i)A'\\
&=(f_j+n-f_i)AR^{\mathsf T}\\
&=d_{ijn,\mathrm{row}}R^{\mathsf T}.
\end{aligned}
\]

\(f_i,f_j,n\) 和完整键 \((i,j,n)\) 均不改变。节点换胞会改变分数坐标代表并按阶段 D 规则改变 shift，但保持物理位移；它与旋转是不同离散作用。

## A15-08

行存储下

\[
X\xrightarrow{P}PX,
\qquad
X\xrightarrow{R}XR^{\mathsf T}.
\]

结合律给出

\[
P(XR^{\mathsf T})
=(PX)R^{\mathsf T}.
\]

两者交换，但它们检查不同错误：置换测试检查节点/边重新编号与聚合，旋转测试检查几何分量和表示矩阵。一个实现可能同步置换正确但旋转左右作用错误。

## A15-09

一个合格设计如下：

1. 用固定 seed 的归一化四维 Gaussian 生成单位四元数；
2. 验证 shape、有限性、
   \[
   \epsilon_R
   =\frac{\lVert R^{\mathsf T}R-I\rVert_F}
   {\max(1,\lVert I\rVert_F)}
   \le\tau,
   \quad
   |\det R-1|\le\tau;
   \]
3. 用不同轴 \(R_1,R_2\) 检查 \(D(R_2R_1)=D(R_2)D(R_1)\)；
4. 检查标量不变、极向量 \(v'=Rv\)、二阶张量 \(T'=RTR^{\mathsf T}\)；
5. 加一个反射 \(Q\) 检查轴向量 \(a'=\det(Q)Qa\)；
6. float64/32 分别使用 \(5\times10^{-12}\)、\(5\times10^{-6}\)；
7. 强制失败可用 \(R^{\mathsf T}\) 代替 \(R\)，或对二阶张量只左乘。

零向量对任何线性作用都给零；\(T=\lambda I\) 对所有旋转不变；同轴旋转交换。这些对象会使错误实现偶然通过。

## A15-10

逐项判断：

1. 距离不变只证明标量几何预处理与正交旋转相容，不能证明向量、轨道基或输出块正确；
2. 节点置换通过只证明离散重新编号一致，不能推出空间旋转等变；
3. Frobenius 范数不变是必要的弱不变量，许多错误矩阵仍有相同范数；
4. 库名称不是实际数组约定或端到端结果的证据。

改进门控应冻结：

- 输入结构 \(X\)、旋转结构 \(RX\) 和完整边键；
- 每个节点的轨道顺序及块对角表示 \(D_i(R)\)；
- 目标关系
  \[
  H_{ij}(RX)
  =D_i(R)H_{ij}(X)D_j(R)^\dagger;
  \]
- 实基转置/复基共轭转置；
- \(D(R_2R_1)=D(R_2)D(R_1)\)；
- prediction、mask、edge key 和轨道 provenance 的统一行映射；
- float64/32、固定 seed/样本数和归一化残差阈值；
- 只左乘、漏共轭、错轨道顺序、错复合顺序和旋转后修改 edge key 的失败样例。

只有这些对象同时通过，才有证据支持声明的 Hamiltonian 块协变；仍不能由此推出正式 DeepH 软件或数据已经验证。
