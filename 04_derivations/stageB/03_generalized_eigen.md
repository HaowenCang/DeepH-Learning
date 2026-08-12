# D-B02/D-B03：非正交基、广义本征与正交化约化

## 1. 条件与对象

设 \(\boldsymbol\Phi=(|\phi_1\rangle,\ldots,|\phi_M\rangle)\) 是同一 \(M\) 维子空间的一组线性无关基，定义

\[
H_{\mu\nu}=\langle\phi_\mu|\hat H|\phi_\nu\rangle,
\qquad
S_{\mu\nu}=\langle\phi_\mu|\phi_\nu\rangle,
\qquad H,S\in\mathbb C^{M\times M}.
\]

本章主问题限定为

\[
H=H^\dagger,\qquad S=S^\dagger\succ0.
\]

若 \(\hat H\) 的伴随关系在所选基函数上成立，则第一项由矩阵元定义得到；第二项由 Gram 矩阵定义与基的线性无关性得到。半正定但奇异、非 Hermitian 或不定矩阵束属于另外的问题类别，不能静默套用以下结论。

## 2. Gram 矩阵正定性

证据类型：`DIRECT_DERIVATION`。

对任意 \(x\in\mathbb C^{M\times1}\)，

\[
\begin{aligned}
x^\dagger Sx
&=\sum_{\mu\nu}x_\mu^*
\langle\phi_\mu|\phi_\nu\rangle x_\nu\\
&=\left\langle\sum_\mu x_\mu\phi_\mu
\middle|
\sum_\nu x_\nu\phi_\nu\right\rangle\\
&=\left\|\sum_\nu x_\nu|\phi_\nu\rangle\right\|^2\ge0.
\end{aligned}
\]

若基线性无关，则 \(x\ne0\) 时线性组合不为零，故 \(x^\dagger Sx>0\)，即 \(S\succ0\)。反之，若基线性相关，存在 \(x\ne0\) 使线性组合为零，于是 \(x^\dagger Sx=0\)，\(S\) 不正定。因此：

\[
\{\phi_\mu\}_{\mu=1}^{M}\text{ 线性无关}
\quad\Longleftrightarrow\quad
S\succ0.
\]

## 3. 从算符方程投影得到 \(Hc=ESc\)

证据类型：`DIRECT_DERIVATION`。

将子空间中的态写为

\[
|\psi\rangle=\sum_{\nu=1}^{M}c_\nu|\phi_\nu\rangle.
\]

若该态满足投影范围内的本征方程 \(\hat H|\psi\rangle=E|\psi\rangle\)，左乘 \(\langle\phi_\mu|\)：

\[
\sum_\nu
\langle\phi_\mu|\hat H|\phi_\nu\rangle c_\nu
=
E\sum_\nu
\langle\phi_\mu|\phi_\nu\rangle c_\nu.
\]

逐个 \(\mu\) 收集即得

\[
Hc=ESc.
\]

正交基只是 \(S=I\) 的特例。把非正交基中的 \(S\) 删除，相当于错误地把系数空间的欧氏内积当成物理态内积。

## 4. 从 Rayleigh 商驻值得到广义本征方程

证据类型：`DIRECT_DERIVATION`。

非零系数向量的 Rayleigh 商定义为

\[
\mathcal R(c)=\frac{c^\dagger Hc}{c^\dagger Sc}.
\]

因为 \(S\succ0\)，分母对 \(c\ne0\) 严格为正。等价地，在约束 \(c^\dagger Sc=1\) 下令

\[
\mathcal L(c,c^*,E)
=c^\dagger Hc-E(c^\dagger Sc-1).
\]

对复变量采用 \(c\) 与 \(c^*\) 独立变化的标准有限维变分记法，对 \(c^*\) 的任意变化 \(\delta c^\dagger\) 有

\[
\delta_{c^*}\mathcal L
=\delta c^\dagger(Hc-ESc).
\]

驻值要求该式对任意 \(\delta c^\dagger\) 为零，因此

\[
Hc=ESc.
\]

这条推导还说明 \(S\)-归一化是变分约束，而不是事后任意选择的欧氏归一化。

## 5. 实谱与 \(S\)-正交性

证据类型：`DIRECT_DERIVATION`。

若 \(Hc_n=E_nSc_n\)，左乘 \(c_n^\dagger\) 得

\[
E_n=\frac{c_n^\dagger Hc_n}{c_n^\dagger Sc_n}\in\mathbb R,
\]

因为分子、分母均为实数且分母为正。

对两个本征对，

\[
Hc_n=E_nSc_n,\qquad Hc_m=E_mSc_m.
\]

左乘 \(c_m^\dagger\) 到第一式得

\[
c_m^\dagger Hc_n=E_n c_m^\dagger Sc_n.
\]

利用 Hermiticity 对第二式取共轭并右配 \(c_n\)，也有

\[
c_m^\dagger Hc_n=E_m c_m^\dagger Sc_n.
\]

故

\[
(E_n-E_m)c_m^\dagger Sc_n=0.
\]

当 \(E_n\ne E_m\) 时，\(c_m^\dagger Sc_n=0\)。各本征矢可缩放为

\[
C^\dagger SC=I.
\]

简并时，单个本征矢不唯一，但可在简并子空间内进行 \(S\)-正交化；应比较子空间而非未经规范固定的逐列向量。

## 6. Cholesky 约化

证据类型：`DIRECT_DERIVATION`；约化对象与条件由 FND-02、FND-04 锚定。

由于 \(S\succ0\)，存在唯一的正对角下三角矩阵 \(L\) 使

\[
S=LL^\dagger.
\]

令

\[
y=L^\dagger c,\qquad c=L^{-\dagger}y.
\]

代入 \(Hc=ESc\) 并左乘 \(L^{-1}\)：

\[
\underbrace{L^{-1}HL^{-\dagger}}_{\widetilde H_{\mathrm C}}y
=Ey.
\]

\(\widetilde H_{\mathrm C}\) 是 Hermitian：

\[
\widetilde H_{\mathrm C}^\dagger
=L^{-1}H^\dagger L^{-\dagger}
=\widetilde H_{\mathrm C}.
\]

若 \(y_m^\dagger y_n=\delta_{mn}\)，则

\[
c_m^\dagger Sc_n
=y_m^\dagger L^{-1}LL^\dagger L^{-\dagger}y_n
=\delta_{mn}.
\]

实际实现应通过三角求解应用 \(L^{-1}\) 或 \(L^{-\dagger}\)，而不显式形成矩阵逆。

## 7. 对称正交化

证据类型：`DIRECT_DERIVATION`；约化对象与条件由 FND-04 锚定。

对 \(S\) 作谱分解

\[
S=U\operatorname{diag}(s_1,\ldots,s_M)U^\dagger,
\qquad s_i>0,
\]

定义唯一 Hermitian 正定平方根及其逆

\[
S^{1/2}=U\operatorname{diag}(\sqrt{s_i})U^\dagger,
\qquad
S^{-1/2}=U\operatorname{diag}(s_i^{-1/2})U^\dagger.
\]

令 \(y=S^{1/2}c\)，则 \(c=S^{-1/2}y\)。原问题化为

\[
\underbrace{S^{-1/2}HS^{-1/2}}_{\widetilde H_{\mathrm S}}y
=Ey.
\]

\(\widetilde H_{\mathrm S}\) 同样 Hermitian，且

\[
c^\dagger Sc=y^\dagger y.
\]

Cholesky 与对称正交化给出不同的正交基坐标，但都保持广义谱。前者通常适合稳定数值求解；后者在分析规范对称性和小特征值方向时更直观。不能仅因公式简洁便默认在数值代码中显式形成 \(S^{-1/2}\)。

完整本征基的存在还需要标准 Hermitian 谱定理，而不能只由第 5 节的逐对正交关系推出。有限维 Hermitian 矩阵 \(\widetilde H_{\mathrm C}\)（等价地 \(\widetilde H_{\mathrm S}\)）存在由 \(M\) 个正交本征矢组成的完备基；\(c=L^{-\dagger}y\) 或 \(c=S^{-1/2}y\) 是双射，故其逆映射给出原广义问题的 \(M\) 个完备本征矢，并满足 \(C^\dagger SC=I\)。

## 8. 一般可逆基变换与谱不变性

证据类型：`DIRECT_DERIVATION`。

令同一子空间中的新基满足

\[
\boldsymbol\Phi'=\boldsymbol\Phi A,
\qquad A\in\mathbb C^{M\times M},\quad\det A\ne0.
\]

同一抽象态的两组系数由

\[
\boldsymbol\Phi c=\boldsymbol\Phi'c'
=\boldsymbol\Phi Ac'
\]

联系。基的线性无关性给出

\[
c'=A^{-1}c.
\]

按矩阵元定义逐指标代入，有

\[
H'=A^\dagger HA,
\qquad
S'=A^\dagger SA.
\]

于是

\[
H'c'=A^\dagger HAA^{-1}c
=A^\dagger Hc
=E A^\dagger Sc
=E A^\dagger SAA^{-1}c
=ES'c'.
\]

等价的行列式证明为

\[
\begin{aligned}
\det(H'-ES')
&=\det\!\left(A^\dagger(H-ES)A\right)\\
&=\det(A^\dagger)\det(H-ES)\det(A)\\
&=|\det A|^2\det(H-ES).
\end{aligned}
\]

因 \(|\det A|^2>0\)，两矩阵束具有相同的特征多项式零点及代数重数。态范数也保持：

\[
c'^\dagger S'c'
=c^\dagger A^{-\dagger}A^\dagger SAA^{-1}c
=c^\dagger Sc.
\]

这一结论要求 \(H\)、\(S\) 和 \(c\) 使用同一 \(A\) 同步变换。只变换其中一个对象，或把系数误写为 \(c'=Ac\)，均不再表示同一抽象问题。

## 9. 病态性与近线性相关

证据类型：`DIRECT_DERIVATION`。

设 \(S\) 的特征值满足

\[
0<\lambda_{\min}(S)\le\lambda_{\max}(S),
\qquad
\kappa_2(S)=\frac{\lambda_{\max}(S)}{\lambda_{\min}(S)}.
\]

对任意 \(c\)，

\[
\lambda_{\min}(S)\|c\|_2^2
\le c^\dagger Sc
\le\lambda_{\max}(S)\|c\|_2^2.
\]

当 \(\lambda_{\min}\) 很小时，某些欧氏范数不小的系数组合代表物理范数很小的近抵消态；\(S^{-1/2}\) 和 Cholesky 求解会放大这些方向上的舍入与数据误差。由此只能推出数值敏感性增加，不能仅凭较大条件数断言某个具体能带误差必然以固定速率增长。

若要删除小特征值方向，必须同时登记阈值、被删除子空间及其对谱和物理量的影响。这一操作改变有效子空间，不再是无损的可逆基变换。

## 10. 残差、结构保持后向扰动与前向界

证据类型：`DIRECT_DERIVATION`。

### 10.1 Hermitian 后向扰动构造

固定 \(\widehat E\in\mathbb R\)、\(\widehat c\ne0\)，定义

\[
q=H\widehat c-\widehat E S\widehat c.
\]

令

\[
u=\frac{\widehat c}{\|\widehat c\|_2},
\qquad
p=-\frac{q}{\|\widehat c\|_2},
\qquad
\alpha=u^\dagger p.
\]

由于

\[
\widehat c^\dagger q
=\widehat c^\dagger H\widehat c
-\widehat E\widehat c^\dagger S\widehat c\in\mathbb R,
\]

所以 \(\alpha\in\mathbb R\)。构造

\[
\Delta H=p u^\dagger+u p^\dagger-\alpha uu^\dagger.
\]

前两项互为伴随，第三项的系数为实数，故 \(\Delta H=\Delta H^\dagger\)。又因 \(p^\dagger u=\alpha\)，

\[
\Delta H u
=p(u^\dagger u)+u(p^\dagger u)-\alpha u(u^\dagger u)
=p.
\]

乘以 \(\|\widehat c\|_2\) 得 \(\Delta H\widehat c=-q\)，因此

\[
(H+\Delta H)\widehat c=\widehat E S\widehat c.
\]

算子 2-范数满足

\[
\begin{aligned}
\|\Delta H\|_2
&\le\|pu^\dagger\|_2+\|up^\dagger\|_2
+|\alpha|\,\|uu^\dagger\|_2\\
&\le3\|p\|_2
=3\frac{\|q\|_2}{\|\widehat c\|_2}.
\end{aligned}
\]

若 \(\widehat E=\mathcal R(\widehat c)\)，则 \(\widehat c^\dagger q=0\)、\(\alpha=0\)，因而可改用

\[
\Delta H=pu^\dagger+up^\dagger,
\qquad
\|\Delta H\|_2\le2\frac{\|q\|_2}{\|\widehat c\|_2}.
\]

这给出保持 \(H+\Delta H\) Hermitian 且保持 \(S\succ0\) 不变的显式后向解释。

### 10.2 标准约化与本征值包含界

再固定 \(\widehat c^\dagger S\widehat c=1\)，定义

\[
A=S^{-1/2}HS^{-1/2},
\qquad
y=S^{1/2}\widehat c,
\qquad
\rho=S^{-1/2}q.
\]

则 \(A=A^\dagger\)、\(\|y\|_2=1\)，且

\[
Ay-\widehat E y=\rho.
\]

若 \(Au_i=E_i u_i\)、\(y=\sum_i a_i u_i\)，则

\[
\|\rho\|_2^2
=\sum_i|a_i|^2|E_i-\widehat E|^2
\ge\min_i|E_i-\widehat E|^2\sum_i|a_i|^2.
\]

由 \(\sum_i|a_i|^2=1\) 得

\[
\min_i|E_i-\widehat E|\le\|\rho\|_2.
\]

同时

\[
\|\rho\|_2
\le\|S^{-1/2}\|_2\|q\|_2
=\frac{\|q\|_2}{\sqrt{\lambda_{\min}(S)}}.
\]

### 10.3 谱隙、子空间角度与 \(S\) 条件影响

设目标 \(E_j\) 为单本征值，并定义与其余谱的分离量

\[
\operatorname{sep}_j(\widehat E)
=\min_{i\ne j}|E_i-\widehat E|>0.
\]

则

\[
\begin{aligned}
\|\rho\|_2^2
&\ge\sum_{i\ne j}|a_i|^2|E_i-\widehat E|^2\\
&\ge\operatorname{sep}_j(\widehat E)^2
\sum_{i\ne j}|a_i|^2.
\end{aligned}
\]

由于 \(\sin\angle(y,u_j)=\sqrt{\sum_{i\ne j}|a_i|^2}\)，

\[
\sin\angle(y,u_j)
\le\frac{\|\rho\|_2}{\operatorname{sep}_j(\widehat E)}.
\]

令 \(c_j=S^{-1/2}u_j\)，并选择使 \(y\) 与 \(e^{i\varphi}u_j\) 最接近的整体相位。利用

\[
\min_\varphi\|y-e^{i\varphi}u_j\|_2
\le\sqrt2\sin\angle(y,u_j),
\]

以及

\[
\|S^{-1/2}\|_2=\lambda_{\min}(S)^{-1/2},
\qquad
\|c_j\|_2\ge\lambda_{\max}(S)^{-1/2},
\]

得到

\[
\frac{\min_\varphi\|\widehat c-e^{i\varphi}c_j\|_2}{\|c_j\|_2}
\le
\sqrt{2\kappa_2(S)}\,
\frac{\|\rho\|_2}{\operatorname{sep}_j(\widehat E)}.
\]

当谱隙为零或很小时，逐本征矢界失去信息；此时应把目标改为与其余谱分离的简并簇，并比较不变子空间角度。

## 11. 失败边界与验证入口

- \(S\) 非正定：标准 Hermitian-definite 广义本征求解器应拒绝输入。
- \(S\) 奇异：基线性相关，Cholesky 分解失败，系数坐标不唯一。
- \(H\ne H^\dagger\)：实谱和 \(S\)-正交结论一般不再成立。
- 近简并：逐本征矢比较可能不稳定，应改用子空间夹角或投影量。
- 显式求逆：可能放大舍入误差，不能作为默认稳定实现。

固定的数值残差、\(S\)-正交、条件数扫描和失败断言见 M4 工作包 T-B01、T-B02、T-B04；相应自动实现属于 M4-07。
