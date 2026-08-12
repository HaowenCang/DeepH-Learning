# 阶段 B 统一表示与 Fourier 约定

## 1. 适用范围

本表冻结第 2、3、4、9 章共用的列基、实空间矩阵和离散 Fourier 约定。它只适用于阶段 B 的有限 Born–von Karman 周期晶格与相应无限极限，不声明任何 DeepH 软件文件格式。后续若对接具体软件，必须把软件约定显式映射到本表，不能静默替换相位、轨道顺序或晶胞方向。

## 2. 列基与复合指标

用 \(a=(i,\mu)\)、\(b=(j,\nu)\) 表示原胞内原子和轨道的复合指标。局域轨道列写作

\[
\boldsymbol\Phi_{\mathbf R}
=(|\phi_{1\mathbf R}\rangle,\ldots,|\phi_{M\mathbf R}\rangle),
\]

其中 \(\mathbf R\) 属于含 \(N\) 个晶胞的有限 Born–von Karman 平移集合 \(\mathcal R_N\)。对同一有限维子空间内的基变换，采用

\[
\boldsymbol\Phi'=\boldsymbol\Phi A,
\qquad
c'=A^{-1}c,
\qquad
H'=A^\dagger H A,
\qquad
S'=A^\dagger S A,
\]

其中 \(A\) 可逆。若旧基正交而 \(A\) 非幺正，则新基 \(S'=A^\dagger A\ne I\)，因此必须求解广义本征问题，不能只变换 \(H\)。

## 3. 实空间矩阵块

冻结 bra/ket 方向为

\[
H_{ab}(\mathbf R)
=\langle\phi_{a\mathbf 0}|\hat H|\phi_{b\mathbf R}\rangle,
\qquad
S_{ab}(\mathbf R)
=\langle\phi_{a\mathbf 0}|\phi_{b\mathbf R}\rangle.
\]

在平移不变且 \(\hat H=\hat H^\dagger\) 时，

\[
H_{ab}(\mathbf R)^*=H_{ba}(-\mathbf R),
\qquad
S_{ab}(\mathbf R)^*=S_{ba}(-\mathbf R),
\]

即 \(H(\mathbf R)^\dagger=H(-\mathbf R)\)、\(S(\mathbf R)^\dagger=S(-\mathbf R)\)。这里的矩阵 dagger 同时包含复共轭和 \(a,b\) 指标交换。

## 4. 有限周期晶格的闭合 Fourier 对

令 \(\mathcal K_N\) 为与 \(\mathcal R_N\) 对偶的 \(N\) 个离散波矢，满足

\[
\frac1N\sum_{\mathbf k\in\mathcal K_N}
e^{i\mathbf k\cdot(\mathbf R-\mathbf R')}
=\delta_{\mathbf R,\mathbf R'}.
\]

本教材采用 cell-phase Bloch 和

\[
|\phi_{a\mathbf k}\rangle
=\frac1{\sqrt N}\sum_{\mathbf R\in\mathcal R_N}
e^{+i\mathbf k\cdot\mathbf R}|\phi_{a\mathbf R}\rangle.
\]

与实空间定义相容的正反变换为

\[
H(\mathbf k)=\sum_{\mathbf R\in\mathcal R_N}
e^{+i\mathbf k\cdot\mathbf R}H(\mathbf R),
\qquad
H(\mathbf R)=\frac1N\sum_{\mathbf k\in\mathcal K_N}
e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\]

\[
S(\mathbf k)=\sum_{\mathbf R\in\mathcal R_N}
e^{+i\mathbf k\cdot\mathbf R}S(\mathbf R),
\qquad
S(\mathbf R)=\frac1N\sum_{\mathbf k\in\mathcal K_N}
e^{-i\mathbf k\cdot\mathbf R}S(\mathbf k).
\]

因此实空间共轭配对推出 \(H(\mathbf k)=H(\mathbf k)^\dagger\) 和 \(S(\mathbf k)=S(\mathbf k)^\dagger\)。阶段 B 的标准广义本征问题还要求每个受测 \(\mathbf k\) 上 \(S(\mathbf k)\succ0\)。

若无限晶格的原胞体积为 \(\Omega_c\)，则对充分规则的周期函数，有限平均的形式极限为

\[
\frac1N\sum_{\mathbf k\in\mathcal K_N}f(\mathbf k)
\longrightarrow
\frac1{V_{\mathrm{BZ}}}\int_{\mathrm{BZ}}f(\mathbf k)\,d^d\mathbf k
=\frac{\Omega_c}{(2\pi)^d}\int_{\mathrm{BZ}}f(\mathbf k)\,d^d\mathbf k,
\]

其中 \(V_{\mathrm{BZ}}=(2\pi)^d/\Omega_c\)。正文必须区分有限离散恒等式与这一极限。

## 5. 含轨道中心的替代规范

设原胞内轨道中心为 \(\boldsymbol\tau_a\)。若改用

\[
|\bar\phi_{a\mathbf k}\rangle
=\frac1{\sqrt N}\sum_{\mathbf R}
e^{+i\mathbf k\cdot(\mathbf R+\boldsymbol\tau_a)}
|\phi_{a\mathbf R}\rangle,
\]

则 \(\bar{\boldsymbol\Phi}_{\mathbf k}=\boldsymbol\Phi_{\mathbf k}U(\mathbf k)\)，其中

\[
U_{ab}(\mathbf k)=\delta_{ab}e^{+i\mathbf k\cdot\boldsymbol\tau_a}.
\]

相应对象必须同步变换：

\[
\bar H(\mathbf k)=U(\mathbf k)^\dagger H(\mathbf k)U(\mathbf k),
\quad
\bar S(\mathbf k)=U(\mathbf k)^\dagger S(\mathbf k)U(\mathbf k),
\quad
\bar c=U(\mathbf k)^{-1}c.
\]

两种规范给出相同广义谱。若采用负号 Bloch 相位，则正变换、逆变换和 \(U(\mathbf k)\) 的指数必须整体反号；本教材不允许只改变其中一式。

## 6. 数值验收含义

Fourier 逆变换只在同一完整离散 \(\mathcal R_N/\mathcal K_N\) 对上要求达到浮点容差。实空间截断、有限 \(k\) 采样和相位错配是三种不同误差源：截断删除 \(H(\mathbf R)\) 块，采样改变可逆离散网格，相位错配则破坏定义的一致性。测试和教材必须分别构造，不得合并归因。
