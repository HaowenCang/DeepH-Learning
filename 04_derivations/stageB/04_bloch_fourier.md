# D-B05/D-B06：Bloch 和、离散 Fourier 对与实空间厄米关系

## 1. 条件、有限晶格与符号

证据类型：来源定义配合 `DIRECT_DERIVATION`。

直接晶格基矢为 \(\mathbf a_i\)，倒格基矢为 \(\mathbf b_i\)，满足

\[
\mathbf b_i\cdot\mathbf a_j=2\pi\delta_{ij}.
\]

取 Born–von Karman 超胞长度 \(N_i\mathbf a_i\)，总晶胞数 \(N=\prod_iN_i\)。有限平移与波矢集合可写为

\[
\mathcal R_N=
\left\{\sum_i n_i\mathbf a_i:0\le n_i<N_i\right\},
\]

\[
\mathcal K_N=
\left\{\sum_i\frac{m_i}{N_i}\mathbf b_i:0\le m_i<N_i\right\}.
\]

所有晶格指标均按超胞周期等价。局域轨道方向、Fourier 相位和轨道中心规范服从[阶段 B 统一约定](../../03_textbook/stageB_conventions.md)。

## 2. 有限群角色正交关系

证据类型：`DIRECT_DERIVATION`。

在一维，令 \(R_n=na\)、\(k_m=2\pi m/(Na)\)，则

\[
\frac1N\sum_{m=0}^{N-1}e^{ik_m(R_n-R_{n'})}
=\frac1N\sum_{m=0}^{N-1}z^m,
\]

其中 \(z=e^{2\pi i(n-n')/N}\)。若 \(n=n'\pmod N\)，和为 1；否则 \(z\ne1\)、\(z^N=1\)，故几何级数为

\[
\frac{1-z^N}{N(1-z)}=0.
\]

各方向乘积给出

\[
\frac1N\sum_{\mathbf k\in\mathcal K_N}
e^{i\mathbf k\cdot(\mathbf R-\mathbf R')}
=\delta_{\mathbf R,\mathbf R'},
\]

以及对偶关系

\[
\frac1N\sum_{\mathbf R\in\mathcal R_N}
e^{i(\mathbf k-\mathbf k')\cdot\mathbf R}
=\delta_{\mathbf k,\mathbf k'}.
\]

这里的 Kronecker delta 均按有限超胞等价类理解。

## 3. 平移算符、Bloch 条件与相位符号

证据类型：`DIRECT_DERIVATION`；Bloch 定理的周期体系语境由 FND-01 锚定。

采用主动平移算符

\[
(\hat T_{\mathbf R}\psi)(\mathbf r)=\psi(\mathbf r-\mathbf R).
\]

晶格平移构成交换的有限 Abel 群。若 \([\hat H,\hat T_{\mathbf R}]=0\)，可在每个能量子空间中选取平移共同本征态。群乘法要求本征值为角色：

\[
\hat T_{\mathbf R}|\psi_{n\mathbf k}\rangle
=e^{-i\mathbf k\cdot\mathbf R}|\psi_{n\mathbf k}\rangle.
\]

写成坐标波函数即

\[
\psi_{n\mathbf k}(\mathbf r+\mathbf R)
=e^{+i\mathbf k\cdot\mathbf R}
\psi_{n\mathbf k}(\mathbf r).
\]

两式指数符号相反并不矛盾：第一式使用主动平移 \(\psi(\mathbf r-\mathbf R)\)，第二式比较坐标点 \(\mathbf r+\mathbf R\)。若改用另一平移算符定义，必须同步改变角色符号。

## 4. 局域轨道 Bloch 和与块对角化

证据类型：`DIRECT_DERIVATION`。

冻结 cell-phase Bloch 和

\[
|\phi_{a\mathbf k}\rangle
=\frac1{\sqrt N}\sum_{\mathbf R\in\mathcal R_N}
e^{+i\mathbf k\cdot\mathbf R}|\phi_{a\mathbf R}\rangle.
\]

由 \(\hat T_{\mathbf T}|\phi_{a\mathbf R}\rangle=|\phi_{a,\mathbf R+\mathbf T}\rangle\)，重标记求和指标可得

\[
\hat T_{\mathbf T}|\phi_{a\mathbf k}\rangle
=e^{-i\mathbf k\cdot\mathbf T}|\phi_{a\mathbf k}\rangle,
\]

与第 3 节一致。

定义

\[
H_{ab}(\mathbf D)
=\langle\phi_{a\mathbf0}|\hat H|\phi_{b\mathbf D}\rangle,
\qquad
S_{ab}(\mathbf D)
=\langle\phi_{a\mathbf0}|\phi_{b\mathbf D}\rangle.
\]

平移不变性给出

\[
\langle\phi_{a\mathbf R}|\hat H|\phi_{b\mathbf R'}\rangle
=H_{ab}(\mathbf R'-\mathbf R).
\]

于是

\[
\begin{aligned}
\langle\phi_{a\mathbf k}|\hat H|\phi_{b\mathbf k'}\rangle
&=\frac1N\sum_{\mathbf R,\mathbf R'}
e^{-i\mathbf k\cdot\mathbf R}
e^{+i\mathbf k'\cdot\mathbf R'}
H_{ab}(\mathbf R'-\mathbf R)\\
&=\delta_{\mathbf k,\mathbf k'}
\sum_{\mathbf D}e^{+i\mathbf k\cdot\mathbf D}H_{ab}(\mathbf D).
\end{aligned}
\]

因此不同 \(\mathbf k\) 块解耦，并定义

\[
H(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}H(\mathbf R),
\qquad
S(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}S(\mathbf R).
\]

## 5. Fourier 逆变换

证据类型：`DIRECT_DERIVATION`。

将正变换代入候选逆变换：

\[
\begin{aligned}
\frac1N\sum_{\mathbf k}
e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k)
&=\frac1N\sum_{\mathbf k}\sum_{\mathbf R'}
e^{i\mathbf k\cdot(\mathbf R'-\mathbf R)}H(\mathbf R')\\
&=\sum_{\mathbf R'}
\delta_{\mathbf R,\mathbf R'}H(\mathbf R')\\
&=H(\mathbf R).
\end{aligned}
\]

所以闭合 Fourier 对为

\[
H(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}H(\mathbf R),
\qquad
H(\mathbf R)=\frac1N\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\]

\(S\) 完全同理。正负号和 \(1/N\) 位置属于一套整体定义，不能只改变其中一式。

## 6. 实空间厄米关系与 \(k\) 空间 Hermiticity

证据类型：`DIRECT_DERIVATION`。

若 \(\hat H=\hat H^\dagger\)，则

\[
\begin{aligned}
H_{ab}(\mathbf R)^*
&=\langle\phi_{b\mathbf R}|\hat H|\phi_{a\mathbf0}\rangle\\
&=\langle\phi_{b\mathbf0}|\hat H|\phi_{a,-\mathbf R}\rangle\\
&=H_{ba}(-\mathbf R).
\end{aligned}
\]

矩阵形式为

\[
H(\mathbf R)^\dagger=H(-\mathbf R).
\]

于是

\[
\begin{aligned}
H(\mathbf k)^\dagger
&=\sum_{\mathbf R}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf R)^\dagger\\
&=\sum_{\mathbf R}e^{-i\mathbf k\cdot\mathbf R}H(-\mathbf R)\\
&=\sum_{\mathbf D}e^{+i\mathbf k\cdot\mathbf D}H(\mathbf D)\\
&=H(\mathbf k).
\end{aligned}
\]

重叠矩阵满足同样的共轭配对，但 \(S(\mathbf k)\succ0\) 仍须另行检查；Hermiticity 本身不推出正定性。

## 7. 倒格等价与轨道中心规范

证据类型：`DIRECT_DERIVATION`。

对任意倒格矢 \(\mathbf G\)，\(e^{i\mathbf G\cdot\mathbf R}=1\)，所以 cell-phase 基满足

\[
|\phi_{a,\mathbf k+\mathbf G}\rangle
=|\phi_{a\mathbf k}\rangle.
\]

若把轨道中心写入相位，定义

\[
|\bar\phi_{a\mathbf k}\rangle
=\frac1{\sqrt N}\sum_{\mathbf R}
e^{i\mathbf k\cdot(\mathbf R+\boldsymbol\tau_a)}
|\phi_{a\mathbf R}\rangle,
\]

则列基满足

\[
\bar{\boldsymbol\Phi}_{\mathbf k}
=\boldsymbol\Phi_{\mathbf k}U(\mathbf k),
\qquad
U_{ab}(\mathbf k)=\delta_{ab}e^{i\mathbf k\cdot\boldsymbol\tau_a}.
\]

因此

\[
\bar H=U^\dagger HU,
\qquad
\bar S=U^\dagger SU,
\qquad
\bar c=U^{-1}c.
\]

由于此处 \(U(\mathbf k)^\dagger U(\mathbf k)=I\)，同步 unitary 变换保持广义谱、态范数以及阶段 B 所定义的 Euclidean 归一化残差标量；相应残差向量按 \(\bar r=U^\dagger r\) 变换。一般非 unitary 的可逆合同变换仍保持广义谱和零残差方程，但不保证该 Euclidean 残差标量不变。对 \(\mathbf k+\mathbf G\)，中心规范还带有 \(e^{i\mathbf G\cdot\boldsymbol\tau_a}\) 的轨道依赖相位；这属于基规范，不是能带变化。

## 8. 有限和到无限积分的边界

证据类型：来源定义配合 `DIRECT_DERIVATION`。

当各 \(N_i\to\infty\) 且函数足够规则时，有限平均趋于 Brillouin 区平均：

\[
\frac1N\sum_{\mathbf k\in\mathcal K_N}f(\mathbf k)
\longrightarrow
\frac1{V_{\mathrm{BZ}}}\int_{\mathrm{BZ}}f(\mathbf k)\,d^d\mathbf k
=\frac{\Omega_c}{(2\pi)^d}\int_{\mathrm{BZ}}f(\mathbf k)\,d^d\mathbf k.
\]

有限离散 Fourier 恒等式在完整 \(\mathcal R_N/\mathcal K_N\) 对上精确；无限极限、有限采样和实空间截断是不同操作，不得相互替代。

## 9. 失败边界与验证入口

- 正变换和逆变换使用同号指数：一般不能重建原块；
- 删除 \(-\mathbf R\) 共轭块：\(H(\mathbf k)\) 一般不再 Hermitian；
- 只对 \(H\) 应用轨道中心规范而不变换 \(S,c\)：广义谱或态改变；
- 把有限网格正交关系直接写成连续 Dirac delta：混淆有限群和无限极限；
- 仅因 \(S(\mathbf k)\) Hermitian 就认为其正定：缺少必要的特征值或 Cholesky 检查。

确定性例题和断言见第 4 章 `examples.md`；随机复矩阵块、完整正反变换和故障注入将在 M4-07 的 T-B05、T-B06、T-B08 固化。
