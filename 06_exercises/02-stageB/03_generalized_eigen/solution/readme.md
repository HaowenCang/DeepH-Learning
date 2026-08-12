# 第 3 章练习参考解答

## Q3-01

由内积的共轭对称性，\(S_{\nu\mu}^*=S_{\mu\nu}\)，故 \(S=S^\dagger\)。对任意 \(x\)，

\[
x^\dagger Sx
=\left\|\sum_\mu x_\mu|\phi_\mu\rangle\right\|^2\ge0,
\]

所以 \(S\) 半正定。若基线性无关，非零 \(x\) 对应的线性组合不为零，二次型严格为正，故 \(S\succ0\)。若基线性相关，存在非零 \(x\) 使线性组合为零，故 \(x^\dagger Sx=0\)，\(S\) 不正定。

当 \(S\) 奇异时，存在非零零空间向量 \(x\) 满足 \(\Phi x=0\)。于是 \(c\) 与 \(c+x\) 表示同一态，系数不唯一。常见错误是把半正定误写成正定，遗漏线性无关条件。

## Q3-02

因为 \(S^{-1}\) 也是 Hermitian，

\[
\begin{aligned}
\langle\phi^\mu|\phi_\nu\rangle
&=\sum_\alpha(S^{-1})_{\mu\alpha}
  \langle\phi_\alpha|\phi_\nu\rangle\\
&=(S^{-1}S)_{\mu\nu}=\delta^\mu_{\ \nu}.
\end{aligned}
\]

另一方面，

\[
\langle\phi_\mu|\psi\rangle
=\sum_\nu\langle\phi_\mu|\phi_\nu\rangle c^\nu
=\sum_\nu S_{\mu\nu}c^\nu.
\]

展开系数由对偶基抽取，直接与原基取内积得到的分量则多一个 \(S\)。只有 \(S=I\) 时两者逐项相同。

## Q3-03

逐个 \(\mu\) 左乘 \(\langle\phi_\mu|\)：

\[
\sum_\nu
\langle\phi_\mu|\hat H|\phi_\nu\rangle c_\nu
=E\sum_\nu
\langle\phi_\mu|\phi_\nu\rangle c_\nu.
\]

按定义即 \(\sum_\nu H_{\mu\nu}c_\nu=E\sum_\nu S_{\mu\nu}c_\nu\)，收集全部指标得 \(Hc=ESc\)。形状为

\[
H,S\in\mathbb C^{M\times M},
\qquad c,Hc,Sc\in\mathbb C^{M\times1}.
\]

若完整本征态不在有限子空间内，所得问题是算符在该子空间上的投影近似。它不能被称为完整问题的精确有限维表示。

## Q3-04

取

\[
\mathcal L=c^\dagger Hc-E(c^\dagger Sc-1).
\]

把 \(c\) 与 \(c^*\) 作为独立变分变量，对任意 \(\delta c^\dagger\) 有

\[
\delta_{c^*}\mathcal L
=\delta c^\dagger(Hc-ESc).
\]

驻值要求括号为零，故 \(Hc=ESc\)。\(S\succ0\) 保证任意非零 \(c\) 的 \(c^\dagger Sc>0\)，Rayleigh 商有定义且约束代表合法态归一化。欧氏归一化 \(c^\dagger c=1\) 一般不等于态归一化；只有正交基 \(S=I\) 时两者一致。

## Q3-05

对本征对，

\[
E_n=\frac{c_n^\dagger Hc_n}{c_n^\dagger Sc_n}.
\]

Hermitian 二次型为实数，且分母严格为正，所以 \(E_n\in\mathbb R\)。对两个本征对，Hermiticity 给出

\[
c_m^\dagger Hc_n
=E_n c_m^\dagger Sc_n
=E_m c_m^\dagger Sc_n.
\]

故 \((E_n-E_m)c_m^\dagger Sc_n=0\)。若本征值不同，即得 \(S\)-正交。

简并子空间内任意 \(S\)-幺正混合仍是合法本征基，因此两个求解器可以返回不同的列向量。应比较子空间投影、主角度或其他规范不变量。

## Q3-06

代入 \(c=L^{-\dagger}y\)：

\[
HL^{-\dagger}y
=E LL^\dagger L^{-\dagger}y
=ELy.
\]

左乘 \(L^{-1}\) 得

\[
L^{-1}HL^{-\dagger}y=Ey.
\]

其伴随为

\[
(L^{-1}HL^{-\dagger})^\dagger
=L^{-1}H^\dagger L^{-\dagger}
=L^{-1}HL^{-\dagger}.
\]

实现时先解三角方程 \(LX=H\) 得 \(X=L^{-1}H\)，再通过另一个三角求解施加右侧 \(L^{-\dagger}\)。求得 \(y\) 后解 \(L^\dagger c=y\) 回代。显式形成 \(L^{-1}\) 会增加舍入误差和不必要计算。

## Q3-07

若 \(S=U\operatorname{diag}(s_i)U^\dagger\)、\(s_i>0\)，定义

\[
S^{-1/2}=U\operatorname{diag}(s_i^{-1/2})U^\dagger.
\]

令 \(y=S^{1/2}c\)，即 \(c=S^{-1/2}y\)，代入并左乘 \(S^{-1/2}\) 得

\[
S^{-1/2}HS^{-1/2}y=Ey.
\]

两种约化必须给出相同本征值，并在映射回原基后给出相同物理本征态子空间和 \(S\)-归一化。约化矩阵的元素和标准坐标中的本征矢一般不同，因为 Cholesky 正交基与对称正交基不同。

## Q3-08

由 \(\Phi c=\Phi'c'=\Phi Ac'\) 和基线性无关性得 \(c'=A^{-1}c\)。按矩阵元定义得 \(H'=A^\dagger HA\)、\(S'=A^\dagger SA\)。于是

\[
H'c'=A^\dagger Hc=E A^\dagger Sc=ES'c'.
\]

此外，

\[
\det(H'-ES')=|\det A|^2\det(H-ES),
\qquad
c'^\dagger S'c'=c^\dagger Sc.
\]

只变换 \(H\) 会破坏同一矩阵束的合同关系；把 \(c'=Ac\) 当作坐标规则会破坏 \(\Phi c=\Phi'c'\)。这两种错误都改变了所表示的态或算符问题。

## Q3-09

\(S\) 的特征值为 \(1/2,3/2\)，故 \(\kappa_2(S)=3\)。广义特征多项式为

\[
\det(H-ES)=2-3E+\frac34E^2,
\]

所以

\[
E_\pm=2\pm\frac2{\sqrt3}
\approx0.8452994616, 3.1547005384.
\]

Cholesky 因子与约化矩阵为

\[
L=\begin{pmatrix}1&0\\1/2&\sqrt3/2\end{pmatrix},
\qquad
L^{-1}HL^{-\mathsf T}
=\begin{pmatrix}1&-1/\sqrt3\\-1/\sqrt3&3\end{pmatrix}.
\]

该矩阵的普通谱等于正确广义谱。若忽略 \(S\)，\(H\) 的普通谱为 \(1,2\)，不等于上述结果。

## Q3-10

\(S_1\) 的特征值为 \(0,2\)，是奇异半正定输入；\(S_2\) 的特征值为 \(-0.2,2.2\)，是不定输入。二者都不满足 \(S\succ0\)，标准 Hermitian-definite 路径应拒绝。

\(S_\varepsilon\) 的特征值为 \(\varepsilon,2-\varepsilon\)，所以对 \(0<\varepsilon<2\) 它正定，但

\[
\kappa_2(S_\varepsilon)=\frac{2-\varepsilon}{\varepsilon}
\]

在 \(\varepsilon\) 很小时很大。应至少报告 \(\lambda_{\min}(S)\)、\(\kappa_2(S)\)、归一化本征残差和 \(\|C^\dagger SC-I\|\)，近简并时还应报告子空间量。

小残差是后向稳定性证据：近似本征对精确满足附近矩阵束。病态性可把很小的矩阵扰动放大为较大的前向谱或本征矢变化，因此仅凭残差不足以给出无条件的前向误差保证。

对给定 \(S\)-归一化近似向量，直接计算得

\[
q=\frac1{\sqrt{39}}
\begin{pmatrix}-1/13\\5/26\end{pmatrix},
\qquad
\widehat c^\mathsf Tq=0.
\]

令 \(u=\widehat c/\|\widehat c\|_2\)、\(p=-q/\|\widehat c\|_2\)。因为 \(\widehat E\) 是 Rayleigh 商，可取证据类型为 `DIRECT_DERIVATION` 的结构保持扰动

\[
\Delta H=pu^\mathsf T+up^\mathsf T
\approx
\begin{pmatrix}
0.0265251989&-0.0278514589\\
-0.0278514589&-0.0265251989
\end{pmatrix}.
\]

它为实对称矩阵，且 \(\Delta H\widehat c=-q\)，所以

\[
(H+\Delta H)\widehat c=\widehat E S\widehat c.
\]

本例 \(\|\Delta H\|_2=1/26\)，而

\[
2\frac{\|q\|_2}{\|\widehat c\|_2}=\frac1{13},
\]

故后向界成立。由于 \(S\succ0\)、\(\widehat c^\mathsf TS\widehat c=1\) 且 \(\widehat E\in\mathbb R\)，可令 \(A=S^{-1/2}HS^{-1/2}\)、\(y=S^{1/2}\widehat c\)、\(\rho=S^{-1/2}q\)。数值为

\[
\|\rho\|_2\approx0.0444115592,
\qquad
|\widehat E-E_-|\approx0.0008543845,
\]

所以 \(|\widehat E-E_-|\le\|\rho\|_2\)。又有

\[
\operatorname{sep}_-(\widehat E)\approx2.3085466922,
\]

以及

\[
\sin\angle(y,u_-)
\approx0.0192343275
\le
\frac{0.0444115592}{2.3085466922}
\approx0.0192378865.
\]

上述逐向量角度界要求目标为单本征值且与其余谱的分离量严格为正。若谱隙为零，应改比较不变子空间；从 \(y\) 映回原系数时还会引入至多以 \(\sqrt{\kappa_2(S)}\) 为尺度的范数放大，不能删除该条件依赖。

## 错误诊断汇总

| 现象 | 机制 | 修复 |
|---|---|---|
| 把 \(c^\dagger c\) 当作态范数 | 忽略 Gram 度量 | 使用 \(c^\dagger Sc\) |
| Cholesky 约化后无法恢复原系数 | 漏掉 \(c=L^{-\dagger}y\) | 用三角方程回代 |
| 基变换后广义谱改变 | \(H,S,c\) 未同步变换 | 使用同一可逆 \(A\) 的合同/逆变换 |
| 奇异 \(S\) 被当作普通正定输入 | 混淆半正定与正定 | 检查最小特征值或 Cholesky 成功性 |
| 病态输入因残差小被称为准确 | 混淆后向误差与前向误差 | 同时报条件数、正交残差和子空间指标 |
