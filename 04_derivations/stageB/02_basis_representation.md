# D-B01：有限维基表示与一致变换推导

## 1. 条件与记号

证据类型：第 2 章[资料包](../../03_textbook/chapters/02_quantum_states_operators_matrices/sources.md)中的对象定义配合 `DIRECT_DERIVATION`。

设 \(\mathcal V_M\) 是复内积空间的 \(M\) 维子空间，\(\boldsymbol\Phi=(|\phi_1\rangle,\ldots,|\phi_M\rangle)\) 是其线性无关有序基。令 \(A\in\mathbb C^{M\times M}\) 可逆，并定义新基

\[
\boldsymbol\Phi'=\boldsymbol\Phi A.
\]

本推导只比较同一 \(\mathcal V_M\) 中的两个基，不覆盖删除/新增基函数造成的子空间变化。

## 2. 系数的逆变换

证据类型：`DIRECT_DERIVATION`。

同一态同时写为

\[
|\psi\rangle=\boldsymbol\Phi c=\boldsymbol\Phi'c'
=\boldsymbol\Phi A c'.
\]

因 \(\boldsymbol\Phi\) 的列线性无关，\(c=Ac'\)，故

\[
c'=A^{-1}c.
\]

## 3. 矩阵元的合同变换

证据类型：`DIRECT_DERIVATION`。

对任意线性算符 \(\hat H\)，新基矩阵元为

\[
\begin{aligned}
H'_{\alpha\beta}
&=\langle\phi'_\alpha|\hat H|\phi'_\beta\rangle\\
&=\sum_{\mu\nu}A_{\mu\alpha}^*
\langle\phi_\mu|\hat H|\phi_\nu\rangle
A_{\nu\beta}.
\end{aligned}
\]

因此

\[
H'=A^\dagger H A.
\]

令 \(\hat H\) 为恒等算符，同理得到 Gram 矩阵

\[
S'=A^\dagger S A.
\]

这属于合同变换，不应与对线性映射坐标常见的相似变换 \(A^{-1}HA\) 静默混用；此处 \(H\) 的定义是带有 bra 与 ket 的矩阵元。

## 4. 范数与期望值不变

证据类型：`DIRECT_DERIVATION`。

利用 \(c'=A^{-1}c\)，

\[
\begin{aligned}
c'^\dagger S'c'
&=c^\dagger(A^{-1})^\dagger A^\dagger SAA^{-1}c\\
&=c^\dagger Sc,
\end{aligned}
\]

并同理有 \(c'^\dagger H'c'=c^\dagger Hc\)。所以归一化期望值

\[
\frac{c^\dagger Hc}{c^\dagger Sc}
\]

在一致可逆基变换下保持不变。

## 5. 广义本征方程不变

证据类型：`DIRECT_DERIVATION`。

若

\[
Hc=ESc,
\]

则

\[
H'c'=A^\dagger Hc=EA^\dagger Sc=ES'c'.
\]

特征行列式满足

\[
\det(H'-ES')
=\det(A^\dagger)\det(H-ES)\det(A)
=|\det A|^2\det(H-ES).
\]

由于 \(A\) 可逆，前因子非零，故广义特征值集合不变。若 \(A\) 幺正且旧基正交，则 \(S'=I\)，普通谱也直接保持；若 \(A\) 非幺正，则必须保留 \(S'\)。

## 6. 失败边界

证据类型：定义后的 `DIRECT_DERIVATION` 边界；数值反例属于 `PEDAGOGICAL`。

- \(A\) 奇异：新列线性相关或发生降维，\(A^{-1}\) 不存在，不再是同一子空间的基变换。
- 只变换 \(H\)：若 \(S,c\) 未同步改变，所得问题不是原对象的同一表示。
- 子空间改变：即使新旧基分别线性无关，也不能用同一个方阵 \(A\) 双向连接，谱差可包含基截断误差。
- 无界算符：连续空间中还应检查基函数是否属于算符和伴随关系的适用定义域；有限矩阵代数不自动消除该条件。

解析复算见[第 2 章例题](../../03_textbook/chapters/02_quantum_states_operators_matrices/examples.md)，对应练习与答案见 `06_exercises/02-stageB/02_basis/`。
