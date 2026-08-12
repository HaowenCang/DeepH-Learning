# 第 2 章练习：态、算符、矩阵与基变换

这些练习用于检查材料覆盖，不要求学习者提交个人作答。每题均有对应参考解答、错误判据和验证入口。

## Q2-01 对象分类

分别说明 \(\hat H\)、有序基 \(\boldsymbol\Phi\)、系数 \(c\)、矩阵 \(H\)、重叠矩阵 \(S\) 和本征值 \(E_n\) 的对象类型。指出更换同一子空间内的基时哪些对象改变表示，哪些物理结论在一致变换下不变。

## Q2-02 整体相位与相对相位

在正交基中取

\[
c_1=\frac1{\sqrt2}\begin{pmatrix}1\\1\end{pmatrix},
\qquad
c_2=\frac1{\sqrt2}\begin{pmatrix}1\\i\end{pmatrix},
\qquad
X=\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

计算两态的 \(X\) 期望值。再证明对任意实数 \(\theta\)，把 \(c\) 替换为 \(e^{i\theta}c\) 不改变归一化期望值。解释为什么这两项结果不矛盾。

## Q2-03 复数 Hermitian 矩阵

判断

\[
A=\begin{pmatrix}1&i\\-i&2\end{pmatrix}
\]

是否 Hermitian。说明“矩阵含复数元素”为什么不能作为否定 Hermiticity 的理由，并证明任意归一化 \(c\) 的 \(c^\dagger Ac\) 为实数。

## Q2-04 列基与系数方向

已知 \(\boldsymbol\Phi'=\boldsymbol\Phi A\)，其中 \(A\) 可逆。从同一态 \(\boldsymbol\Phi c=\boldsymbol\Phi'c'\) 推导 \(c'=A^{-1}c\)。再从矩阵元定义推导 \(H'=A^\dagger H A\) 和 \(S'=A^\dagger S A\)。

## Q2-05 非幺正变换后的本征问题

旧基正交，\(S=I\)。若 \(A\) 可逆但非幺正，证明 \(S'=A^\dagger A\ne I\)（一般情形），并说明为什么新表示应求解 \(H'c'=ES'c'\)，而不是 \(H'c'=Ec'\)。

## Q2-06 广义谱不变性

证明

\[
\det(H'-ES')=|\det A|^2\det(H-ES).
\]

说明该式为什么只要求 \(A\) 可逆，不要求 \(A\) 幺正；同时说明 \(A\) 奇异时论证为何失效。

## Q2-07 表示变换与子空间改变

比较以下两种操作：

1. 在 \(M\) 维子空间内用可逆 \(A\in\mathbb C^{M\times M}\) 更换基；
2. 删除一个基函数，把问题投影到 \(M-1\) 维子空间。

解释为什么第一种操作保持广义谱，而第二种操作通常不保持。指出把有限基误差归为“纯规范差异”会造成什么判断错误。

## Q2-08 确定性失败复算

复算[第 2 章二能级例题](../../../../03_textbook/chapters/02_quantum_states_operators_matrices/examples.md)中的非幺正变换：

\[
H=\begin{pmatrix}1&2\\2&-1\end{pmatrix},
\qquad
A=\begin{pmatrix}1&\tfrac12\\0&1\end{pmatrix}.
\]

求 \(H'=A^\dagger HA\)、\(S'=A^\dagger A\)，比较广义谱和错误的 \(H'\) 普通谱，并给出差异的机制解释。
