# 第 3 章练习：非正交基与广义本征值问题

这些练习用于检验材料的覆盖性、可自学性和可验证性，不要求学习者提交个人作答。每题均有一一对应的参考解答、条件边界和错误判据。

## Q3-01 Gram 矩阵与线性无关

设 \(S_{\mu\nu}=\langle\phi_\mu|\phi_\nu\rangle\)。证明 \(S\) Hermitian 半正定，并证明有限基线性无关当且仅当 \(S\succ0\)。说明 \(S\) 奇异时系数表示为何不唯一。

## Q3-02 对偶基与分量

在 \(S\succ0\) 条件下定义

\[
|\phi^\mu\rangle=\sum_\nu|\phi_\nu\rangle(S^{-1})_{\nu\mu}.
\]

证明 \(\langle\phi^\mu|\phi_\nu\rangle=\delta^\mu_{\ \nu}\)。若 \(|\psi\rangle=\sum_\mu c^\mu|\phi_\mu\rangle\)，推导 \(\langle\phi_\mu|\psi\rangle=\sum_\nu S_{\mu\nu}c^\nu\)，并解释为什么一般不能把这两组分量混同。

## Q3-03 投影推导与形状检查

从 \(\hat H|\psi\rangle=E|\psi\rangle\) 和 \(|\psi\rangle=\sum_\nu c_\nu|\phi_\nu\rangle\) 出发，逐指标推导 \(Hc=ESc\)。列出 \(H,S,c,Hc,Sc\) 的形状，并指出所选子空间不包含完整本征态时该方程的含义。

## Q3-04 Rayleigh 商驻值

对

\[
\mathcal R(c)=\frac{c^\dagger Hc}{c^\dagger Sc}
\]

在 \(c^\dagger Sc=1\) 约束下作复变量变分，推导驻值方程。明确说明为什么需要 \(S\succ0\)，以及 \(S\)-归一化与欧氏归一化的区别。

## Q3-05 实谱、\(S\)-正交与简并

在 \(H=H^\dagger,S=S^\dagger\succ0\) 下证明本征值为实数，并证明不同本征值的本征矢满足 \(c_m^\dagger Sc_n=0\)。说明简并时为何不能要求两个独立求解器返回逐列相同的本征矢。

## Q3-06 Cholesky 约化

设 \(S=LL^\dagger\)。从 \(Hc=ESc\) 推导

\[
L^{-1}HL^{-\dagger}y=Ey,
\qquad y=L^\dagger c.
\]

证明约化矩阵 Hermitian，并说明如何用线性方程求解而非显式矩阵逆实现矩阵构造和本征矢回代。

## Q3-07 对称正交化与两种坐标

由 \(S=U\operatorname{diag}(s_i)U^\dagger\) 构造 \(S^{-1/2}\)，推导 \(S^{-1/2}HS^{-1/2}y=Ey\)。比较该约化与 Cholesky 约化：哪些量必须一致，哪些矩阵元素一般不一致？

## Q3-08 一般可逆基变换

从 \(\boldsymbol\Phi'=\boldsymbol\Phi A\) 推导

\[
c'=A^{-1}c,
\quad H'=A^\dagger HA,
\quad S'=A^\dagger SA.
\]

证明广义谱与态范数不变。再解释只变换 \(H\) 或把 \(c'=Ac\) 当作坐标规则会破坏什么关系。

## Q3-09 两轨道闭式复算

对

\[
H=\begin{pmatrix}1&0\\0&2\end{pmatrix},
\qquad
S=\begin{pmatrix}1&1/2\\1/2&1\end{pmatrix},
\]

求 \(S\) 的特征值和条件数、广义本征值、Cholesky 约化矩阵，并比较忽略 \(S\) 得到的普通谱。结果应与[例题](../../../../03_textbook/chapters/03_nonorthogonal_generalized_eigen/examples.md)独立复算一致。

## Q3-10 失败分类与验证指标

分别讨论以下三族重叠矩阵：

\[
S_1=\begin{pmatrix}1&1\\1&1\end{pmatrix},
\quad
S_2=\begin{pmatrix}1&1.2\\1.2&1\end{pmatrix},
\quad
S_\varepsilon=\begin{pmatrix}1&1-\varepsilon\\1-\varepsilon&1\end{pmatrix}, 0<\varepsilon\ll1.
\]

判定它们分别属于奇异、非正定还是病态正定输入。说明标准求解器应拒绝哪些输入；对仍可求解的病态输入，应至少报告哪些量，为什么小本征残差不足以单独证明前向谱误差很小？

再使用 Q3-09 的 \(H,S\)，取

\[
\widehat c=\frac1{\sqrt{39}}\begin{pmatrix}5\\2\end{pmatrix},
\qquad
\widehat E=\mathcal R(\widehat c)=\frac{11}{13}.
\]

计算 \(q=H\widehat c-\widehat E S\widehat c\)，按第 3 章 3.5.2 构造 Hermitian \(\Delta H\)，验证它精确消去残差并满足给定范数界。再计算 \(\rho=S^{-1/2}q\)，复核本征值包含界和带 \(\operatorname{sep}_-(\widehat E)\) 的正交坐标角度界。所有不等式必须写出适用条件，不得只报告数值。
