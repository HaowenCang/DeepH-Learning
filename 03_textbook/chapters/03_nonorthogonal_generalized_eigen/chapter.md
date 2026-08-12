# 第 3 章　非正交基与广义本征值问题

## 3.0 学习目标、范围与来源边界

本章建立从非正交局域基到 Hermitian-definite 广义本征问题的完整代数链。完成本章后，应能从 Gram 矩阵解释态内积，分别由投影与变分原理推导

\[
Hc=ESc,
\]

证明实谱与 \(S\)-正交性，实施 Cholesky 和对称正交化约化，并判断近线性相关、奇异或非正定重叠矩阵何时使标准结论失效。

主问题始终限定为

\[
H,S\in\mathbb C^{M\times M},\qquad
H=H^\dagger,\qquad S=S^\dagger\succ0,
\]

本征矢 \(c_n\in\mathbb C^{M\times1}\)，本征值 \(E_n\in\mathbb R\)。来源范围见[资料包](sources.md)，逐式证明见[推导 D-B02/D-B03](../../../04_derivations/stageB/03_generalized_eigen.md)。本章的两轨道模型和病态扫描均为 `PEDAGOGICAL`，不代表任何真实材料或具体软件格式。

## 3.1 非正交基的几何

### 3.1.1 Gram 矩阵与态内积

令

\[
\boldsymbol\Phi=(|\phi_1\rangle,\ldots,|\phi_M\rangle),
\qquad
|\psi\rangle=\boldsymbol\Phi c=\sum_{\mu=1}^M c_\mu|\phi_\mu\rangle.
\]

Gram 矩阵定义为

\[
S_{\mu\nu}=\langle\phi_\mu|\phi_\nu\rangle.
\]

若 \(|\psi\rangle=\boldsymbol\Phi c\)、\(|\chi\rangle=\boldsymbol\Phi d\)，则

\[
\langle\psi|\chi\rangle=c^\dagger Sd,
\qquad
\|\psi\|^2=c^\dagger Sc.
\]

因此，非正交基中的系数内积通常不是 \(c^\dagger d\)。删去 \(S\) 会把系数坐标的欧氏几何误当成物理态空间的内积几何。

### 3.1.2 线性无关与正定性

证据类型：`DIRECT_DERIVATION`。以下结论由 Gram 矩阵定义与线性无关性直接推出。

对任意 \(x\in\mathbb C^{M\times1}\)，

\[
x^\dagger Sx
=\left\|\sum_\mu x_\mu|\phi_\mu\rangle\right\|^2\ge0.
\]

若基线性无关，则 \(x\ne0\) 时右侧严格为正，故 \(S\succ0\)。反之，若基线性相关，存在非零 \(x\) 使线性组合为零，从而 \(x^\dagger Sx=0\)。所以

\[
\{|\phi_\mu\rangle\}_{\mu=1}^M\text{ 线性无关}
\quad\Longleftrightarrow\quad S\succ0.
\]

Hermitian 半正定但奇异的 \(S\) 对应冗余坐标；不定或非 Hermitian 的 \(S\) 已不再是该组态的合法 Gram 矩阵。

### 3.1.3 对偶基与分量

定义对偶 ket

\[
|\phi^\mu\rangle=\sum_\nu|\phi_\nu\rangle(S^{-1})_{\nu\mu},
\]

则

\[
\langle\phi^\mu|\phi_\nu\rangle=\delta^\mu_{\ \nu},
\qquad
\sum_\mu|\phi_\mu\rangle\langle\phi^\mu|=P,
\]

其中 \(P\) 是所选子空间上的恒等投影。态的展开系数满足 \(c^\mu=\langle\phi^\mu|\psi\rangle\)，而与原基直接取内积得到的量为

\[
c_\mu=\langle\phi_\mu|\psi\rangle=\sum_\nu S_{\mu\nu}c^\nu.
\]

上下指标在此只用于区分由 \(S\) 联系的两类分量；后续矩阵方程继续把展开系数组成列向量 \(c\)，避免在有限维计算中混用记号。

## 3.2 广义本征方程

### 3.2.1 投影推导

证据类型：`DIRECT_DERIVATION`。以下公式链由矩阵元定义和算符方程投影直接推出。

Hamiltonian 矩阵元为

\[
H_{\mu\nu}=\langle\phi_\mu|\hat H|\phi_\nu\rangle.
\]

把 \(|\psi\rangle=\sum_\nu c_\nu|\phi_\nu\rangle\) 代入 \(\hat H|\psi\rangle=E|\psi\rangle\)，并逐个左乘 \(\langle\phi_\mu|\)，得到

\[
\sum_\nu H_{\mu\nu}c_\nu
=E\sum_\nu S_{\mu\nu}c_\nu.
\]

收集全部 \(\mu\) 即为 \(Hc=ESc\)。若完整本征态不在所选有限子空间中，这一方程表达的是投影近似，而非完整算符问题的精确有限维改写。

### 3.2.2 Rayleigh 商驻值

证据类型：`DIRECT_DERIVATION`。以下公式链在 \(S\succ0\) 和复变量变分条件下直接推出。

对 \(c\ne0\)，定义

\[
\mathcal R(c)=\frac{c^\dagger Hc}{c^\dagger Sc}.
\]

由于 \(S\succ0\)，分母严格为正。在约束 \(c^\dagger Sc=1\) 下，Lagrange 函数

\[
\mathcal L=c^\dagger Hc-E(c^\dagger Sc-1)
\]

对 \(c^*\) 的驻值条件为

\[
\delta c^\dagger(Hc-ESc)=0.
\]

该式对任意 \(\delta c^\dagger\) 成立，故再次得到 \(Hc=ESc\)。这里的 \(S\)-归一化是物理态归一化在系数坐标中的表达。

### 3.2.3 实谱、正交性与简并

对任一本征对，

\[
E_n=\frac{c_n^\dagger Hc_n}{c_n^\dagger Sc_n}\in\mathbb R.
\]

若 \(E_m\ne E_n\)，由 Hermiticity 可得

\[
(E_n-E_m)c_m^\dagger Sc_n=0,
\]

所以不同本征值对应的本征矢在 \(S\)-内积下正交。可以把完整本征矢矩阵 \(C\in\mathbb C^{M\times M}\) 规范化为

\[
C^\dagger SC=I.
\]

简并本征子空间内的单个本征矢不唯一；可在该子空间中进行 \(S\)-正交化，但比较计算结果时应优先比较子空间投影，而不是未固定规范的逐列向量。

## 3.3 正交化约化

### 3.3.1 Cholesky 约化

由 \(S\succ0\) 可写

\[
S=LL^\dagger,
\]

其中 \(L\) 是正对角下三角矩阵。令 \(y=L^\dagger c\)，即 \(c=L^{-\dagger}y\)，则

\[
\widetilde H_{\mathrm C}y=Ey,
\qquad
\widetilde H_{\mathrm C}=L^{-1}HL^{-\dagger}.
\]

\(\widetilde H_{\mathrm C}\) 为 Hermitian，且 \(y_m^\dagger y_n=\delta_{mn}\) 等价于 \(c_m^\dagger Sc_n=\delta_{mn}\)。数值实现应使用三角求解应用 \(L^{-1}\) 和 \(L^{-\dagger}\)，不应把显式求逆作为默认方案。

### 3.3.2 对称正交化

若

\[
S=U\operatorname{diag}(s_1,\ldots,s_M)U^\dagger,
\qquad s_i>0,
\]

则唯一 Hermitian 正定逆平方根为

\[
S^{-1/2}=U\operatorname{diag}(s_1^{-1/2},\ldots,s_M^{-1/2})U^\dagger.
\]

令 \(y=S^{1/2}c\)，得到标准 Hermitian 问题

\[
\widetilde H_{\mathrm S}y=Ey,
\qquad
\widetilde H_{\mathrm S}=S^{-1/2}HS^{-1/2}.
\]

Cholesky 与对称正交化使用不同的正交坐标，但保持同一广义谱。前者适合作为稳定求解器的构造依据，后者便于分析 \(S\) 的本征方向；这不意味着代码应显式形成矩阵逆平方根。

## 3.4 一般可逆基变换

证据类型：`DIRECT_DERIVATION`。以下不变性由同一抽象态的坐标关系和合同变换直接推出。

令新旧基满足

\[
\boldsymbol\Phi'=\boldsymbol\Phi A,
\qquad A\in\mathbb C^{M\times M},\quad \det A\ne0.
\]

保持同一抽象态要求

\[
c'=A^{-1}c,
\qquad H'=A^\dagger HA,
\qquad S'=A^\dagger SA.
\]

于是

\[
H'c'=A^\dagger Hc=E A^\dagger Sc=ES'c'.
\]

特征行列式也满足

\[
\det(H'-ES')=|\det A|^2\det(H-ES),
\]

故零点即广义谱不变。态范数同样保持：\(c'^\dagger S'c'=c^\dagger Sc\)。若只变换 \(H\)、只变换 \(S\) 或使用错误的系数方向，所得矩阵束不再表示同一问题。

轨道重排、单轨道相位改变和正交子空间内的幺正混合都是该规则的特殊情形。改变基所张成的子空间或删除小特征值方向则不是可逆基变换，因为有效投影空间已经改变。

## 3.5 病态性、残差与失败边界

### 3.5.1 条件数与近线性相关

证据类型：`DIRECT_DERIVATION`。由 Hermitian 正定矩阵的谱分解可得

\[
\kappa_2(S)=\frac{\lambda_{\max}(S)}{\lambda_{\min}(S)},
\qquad
\lambda_{\min}(S)\|c\|_2^2
\le c^\dagger Sc
\le\lambda_{\max}(S)\|c\|_2^2.
\]

当 \(\lambda_{\min}(S)\) 很小时，某些欧氏范数不小的系数组合对应物理范数很小的近抵消态；正交化会放大这些方向上的数据和舍入误差。因此，大条件数是敏感性警告，但不足以单独推出某个能量误差的固定大小或增长律。

### 3.5.2 残差与结构保持后向误差

证据类型：`DIRECT_DERIVATION`。固定 \(\widehat E\in\mathbb R\)、\(\widehat c\ne0\)，定义

\[
q=H\widehat c-\widehat E S\widehat c,
\qquad
r=\frac{\|q\|_2}
{\bigl(\|H\|_2+|\widehat E|\,\|S\|_2\bigr)\|\widehat c\|_2}.
\]

令

\[
u=\frac{\widehat c}{\|\widehat c\|_2},
\qquad
p=-\frac{q}{\|\widehat c\|_2},
\qquad
\alpha=u^\dagger p\in\mathbb R.
\]

\(\alpha\) 为实数，因为 \(H,S\) Hermitian 且 \(\widehat E\) 为实数。构造

\[
\Delta H=p u^\dagger+u p^\dagger-\alpha uu^\dagger.
\]

则 \(\Delta H=\Delta H^\dagger\)，并且

\[
\Delta H\,u
=p+u(p^\dagger u)-\alpha u=p,
\]

故

\[
(H+\Delta H)\widehat c=\widehat E S\widehat c.
\]

由三角不等式和 \(|\alpha|\le\|p\|_2\) 得

\[
\|\Delta H\|_2
\le3\|p\|_2
=3\frac{\|q\|_2}{\|\widehat c\|_2}
=3r\bigl(\|H\|_2+|\widehat E|\,\|S\|_2\bigr).
\]

若 \(\widehat E=\mathcal R(\widehat c)\)，则 \(\widehat c^\dagger q=0\)、\(\alpha=0\)，上界中的常数可由 3 改为 2。这一显式构造证明“小残差对应附近 Hermitian 矩阵束”在上述条件下成立；它不是无条件的前向精度保证。

### 3.5.3 本征值、谱隙与向量前向界

证据类型：`DIRECT_DERIVATION`。再令 \(\widehat c^\dagger S\widehat c=1\)，并定义

\[
A=S^{-1/2}HS^{-1/2},
\qquad
y=S^{1/2}\widehat c,
\qquad
\rho=S^{-1/2}q.
\]

于是 \(A=A^\dagger\)、\(\|y\|_2=1\)，且

\[
Ay-\widehat E y=\rho,
\qquad
\|\rho\|_2
\le\frac{\|q\|_2}{\sqrt{\lambda_{\min}(S)}}.
\]

把 \(y\) 展开到 \(A\) 的正交本征基可得本征值包含界

\[
\min_j|\widehat E-E_j|\le\|\rho\|_2.
\]

若 \(E_j\) 为已识别的单本征值，并令

\[
\operatorname{sep}_j(\widehat E)
=\min_{i\ne j}|E_i-\widehat E|>0,
\]

则同一展开给出

\[
\sin\angle(y,u_j)
\le\frac{\|\rho\|_2}{\operatorname{sep}_j(\widehat E)},
\]

其中 \(u_j\) 是 \(A\) 的单位本征矢。映回系数 \(c_j=S^{-1/2}u_j\) 时，适当选择整体相位后有粗略但可核对的界

\[
\frac{\min_\varphi\|\widehat c-e^{i\varphi}c_j\|_2}{\|c_j\|_2}
\le
\sqrt{2\kappa_2(S)}\,
\frac{\|\rho\|_2}{\operatorname{sep}_j(\widehat E)}.
\]

因此，\(S\) 的条件数影响从正交坐标返回原系数坐标的向量误差。若谱隙为零或很小，不得套用逐向量界；应把 \(u_j\) 替换为与其余谱分离的不变子空间，并比较子空间角度。

### 3.5.4 非法输入与截断边界

以下输入不得静默进入标准 Hermitian-definite 结论：

- \(S\) 非正定：标准定广义本征求解器应拒绝；
- \(S\) 奇异：基线性相关，Cholesky 失败且系数表示不唯一；
- \(H\ne H^\dagger\)：实谱和 \(S\)-正交性一般不再保证；
- \(H,S\) 维数不匹配：矩阵束未定义；
- 截断 \(S\) 的小特征值方向：必须记录阈值、删除子空间及结果变化，因为这改变了有效空间。

## 3.6 例题、练习与验证入口

[完整例题](examples.md)使用

\[
H=\begin{pmatrix}1&0\\0&2\end{pmatrix},
\qquad
S=\begin{pmatrix}1&1/2\\1/2&1\end{pmatrix},
\]

比较闭式广义谱、Cholesky 约化、对称正交化和错误忽略 \(S\) 的结果。[练习](../../../06_exercises/02-stageB/03_generalized_eigen/problem/readme.md)与[参考解答](../../../06_exercises/02-stageB/03_generalized_eigen/solution/readme.md)逐项覆盖定义、推导、基变换、病态性和失败样例。自动化随机矩阵、条件数扫描与拒绝性断言将在 M4-07 固定实现；当前例题的确定性复现命令记录在例题末尾。

### 自学检查

1. 为什么非正交基中态范数是 \(c^\dagger Sc\)，而不是一般的 \(c^\dagger c\)？
2. 投影推导和 Rayleigh 商推导分别依赖哪些条件？
3. Cholesky 变量替换为何取 \(y=L^\dagger c\)？
4. 为什么同步合同变换保持广义谱，而只变换 \(H\) 不保持？
5. 为什么大 \(\kappa_2(S)\) 是警告而不是具体谱误差的充分预测？

这些问题的可核对答案可由本章 3.1—3.5 节直接定位；综合计算题及完整步骤见练习参考解答。
