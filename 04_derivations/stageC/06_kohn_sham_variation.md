# D-C03—D-C04：HK/Levy/Lieb 结构与 Kohn–Sham 变分

本推导包对应第 6 章。D-C03 分离 Hohenberg–Kohn 唯一性、Levy 纯态 constrained search 与 Lieb 凸对偶形式；D-C04 从轨道正交约束推导常规局域 Kohn–Sham 方程，并给出总能量重建和适用边界。所有积分均采用原子单位；真实泛函、材料、后端和实践版本保持未决。

## D-C03 外势—密度结构与普适泛函

### D-C03.1 问题族和势的等价类

固定电子数 \(N\)、相互作用 \(\hat W\)、动能 \(\hat T\)、边界条件和 Hilbert 空间，定义

\[
\hat H[v]=\hat T+\hat W+\sum_{i=1}^{N}v(\mathbf r_i).
\]

若 \(v'=v+C\)，则

\[
\hat H[v']=\hat H[v]+NC.
\]

本征态和密度不变，能量整体平移。因此 HK 映射的势对象不是单个函数，而是模掉常数后的等价类 \([v]\)。如果同时改变 \(N\)、\(\hat W\) 或边界条件，就离开了这个问题族。

### D-C03.2 非简并 HK 反证

设 \(v\) 和 \(v'\) 是允许的局域标量势且不相差常数，分别有非简并基态 \(\Psi\)、\(\Psi'\)，两者产生同一密度 \(n\)。先证明两势不能共享同一个基态。若非零波函数 \(\Phi\) 同时满足

\[
\hat H[v]\Phi=E\Phi,
\qquad
\hat H[v']\Phi=E'\Phi,
\]

两式相减得到

\[
\left[\sum_{i=1}^{N}(v-v')(\mathbf r_i)\right]\Phi
=(E-E')\Phi.
\]

在共同算符定义域、允许的局域势类以及 \(\Phi\) 几乎处处非零或相应唯一延拓条件下，

\[
\sum_{i=1}^{N}(v-v')(\mathbf r_i)=E-E'
\]

在构型空间几乎处处成立。固定其余坐标而分别改变任一 \(\mathbf r_i\)，可推出 \(v-v'\) 几乎处处为常数，与假设矛盾。因此 \(\Psi'\) 不是 \(\hat H[v]\) 的基态，Rayleigh–Ritz 严格不等式给出

\[
\begin{aligned}
E_0[v]
&<\langle\Psi'|\hat H[v]|\Psi'\rangle\\
&=E_0[v']+
\int [v(\mathbf r)-v'(\mathbf r)]n(\mathbf r)\,d\mathbf r.
\end{aligned}
\]

交换 \(v\) 与 \(v'\)，

\[
E_0[v']
<E_0[v]+
\int [v'(\mathbf r)-v(\mathbf r)]n(\mathbf r)\,d\mathbf r.
\]

两式相加得到

\[
E_0[v]+E_0[v']<E_0[v]+E_0[v'],
\]

产生矛盾。故在上述条件下，同一基态密度不能由两个不等价外势产生。

这段证明的逻辑门控是：

- 两个问题具有相同 \(\hat T\)、\(\hat W\)、\(N\) 和边界条件；
- trial state 属于对方 Hamiltonian 的定义域；
- 共同本征态方程在允许的局域势类和几乎处处/唯一延拓条件下只容许 \(v-v'\) 为常数；
- 非简并性与共同基态排除使 trial state 不是对方的基态；
- 势只确定到加法常数。

若基态简并且两个**纯态**基态产生同一密度，Rayleigh–Ritz 先只给两条非严格不等式。相加后两边完全抵消，因而两条不等式必须同时取等号；每个交叉 trial state 都成为对方 Hamiltonian 的基态。随后使用上述共同基态步骤，仍推出局域标量势等价类唯一，但不推出简并子空间内某条波函数唯一。对简并**系综**必须另行声明组成系综的共同能量基态及权重；对自旋密度或流密度等多基本变量理论，势非唯一性可能出现额外结构。该边界由 C-FND-07 直接支持，不从 HK 1964 的非简并证明无条件外推。

### D-C03.3 HK 变分结构的域限制

若 \(n\) 是某个允许外势的基态密度，并且 \(\Psi[n]\) 的选取没有歧义，可写

\[
F_{\mathrm{HK}}[n]
=\langle\Psi[n]|\hat T+\hat W|\Psi[n]\rangle.
\]

对任意可接受 trial density \(n'\) 及其对应 trial state，

\[
E_v[n']=F_{\mathrm{HK}}[n']+\int vn'\ge E_0[v].
\]

这个表述在原始形式中仍携带 interacting \(v\)-representability 和简并问题。它给出变分结构，但没有给出 \(F[n]\) 的闭式，也没有自动把泛函扩展到所有非负归一化函数。

### D-C03.4 Levy 两层搜索

设 \(\mathcal W_N\) 是归一化、反对称、具有有限内部能量的 \(N\) 电子纯态集合。定义 pure-state \(N\)-representable 密度域

\[
\mathcal I_N^{\mathrm{pure}}
=\{n:\exists\Psi\in\mathcal W_N,\ \Psi\mapsto n\}.
\]

对 \(n\in\mathcal I_N^{\mathrm{pure}}\)，在本章标准三维 Coulomb 条件下定义

\[
F_{\mathrm{LL}}^{\mathrm{pure}}[n]
=\min_{\Psi\in\mathcal W_N,\ \Psi\mapsto n}
\langle\Psi|\hat T+\hat W|\Psi\rangle.
\]

从全波函数变分原理出发，

\[
E_0[v]
=\inf_{\Psi\in\mathcal W_N}
\left\{
\langle\Psi|\hat T+\hat W|\Psi\rangle
+\int v n_\Psi
\right\}.
\]

按密度纤维对搜索域分组：每个 \(\Psi\) 唯一产生一个 \(n_\Psi\)，而每个 \(n\in\mathcal I_N^{\mathrm{pure}}\) 对应一个非空纤维。于是

\[
\begin{aligned}
E_0[v]
&=\inf_{n\in\mathcal I_N^{\mathrm{pure}}}
\min_{\Psi\mapsto n}
\left\{
\langle\Psi|\hat T+\hat W|\Psi\rangle+\int vn
\right\}\\
&=\inf_{n\in\mathcal I_N^{\mathrm{pure}}}
\left\{F_{\mathrm{LL}}^{\mathrm{pure}}[n]+\int vn\right\}.
\end{aligned}
\]

外势只出现在外层线性项，故 \(F_{\mathrm{LL}}^{\mathrm{pure}}\) 对问题族是普适的。Levy 的构造使用 constrained minimum；Lieb 对标准 Coulomb 密度域的存在性结果保证内层下确界达到，因此最小化波函数存在但可以不唯一。外层对密度的搜索仍写 infimum；其是否达到取决于给定外势问题是否有基态。离开标准函数空间、改变相互作用或算符条件时，必须重新审查内层可达性。

### D-C03.5 系综 constrained search 与 Lieb 对偶

允许统计密度算符 \(\Gamma\) 后，在同一标准条件下定义

\[
F_{\mathrm{ens}}[n]
=\min_{\Gamma\mapsto n}
\operatorname{Tr}\Gamma(\hat T+\hat W).
\]

混合两个可行 \(\Gamma_1,\Gamma_2\) 会产生混合密度，且内部能量对 \(\Gamma\) 线性。因此对 \(0\le\lambda\le1\)，

\[
F_{\mathrm{ens}}[\lambda n_1+(1-\lambda)n_2]
\le
\lambda F_{\mathrm{ens}}[n_1]
+(1-\lambda)F_{\mathrm{ens}}[n_2],
\]

即该泛函是凸的。

令

\[
X=L^1(\mathbb R^3)\cap L^3(\mathbb R^3),
\qquad
\|n\|_X=\|n\|_1+\|n\|_3,
\]

并以范数拓扑讨论收敛。其对偶配对势空间可取

\[
X^*=L^\infty(\mathbb R^3)+L^{3/2}(\mathbb R^3).
\]

固定 \(N\) 时，势唯一性使用商空间 \(X^*/\mathbb R\)，或先固定势零点。把密度泛函在不可接受密度上扩展为 \(+\infty\)，再把基态能量视为 \(X^*\) 上的凹泛函，Legendre–Fenchel 变换给出

\[
F_{\mathrm L}[n]
=\sup_{v\in X^*}
\left\{
E_0[v]-\int vn
\right\}.
\]

在 Lieb 的标准 Coulomb 函数空间设置中，可取

\[
\mathcal I_N=
\{n\ge0:\int n=N,\ \sqrt n\in H^1(\mathbb R^3)\}
\subset L^1\cap L^3.
\]

在相应标准 Coulomb 定理条件和扩展约定下，\(F_{\mathrm L}\) 是 \(X\) 的范数拓扑中凸、下半连续的扩展值泛函，并满足

\[
E_0[v]=\inf_{n\in\mathcal I_N}
\left\{F_{\mathrm L}[n]+\int vn\right\}.
\]

在本章的标准三维 Coulomb 条件、固定 \(N\)、共同扩展值约定和 \(X\) 的范数拓扑下，

\[
F_{\mathrm L}
=F_{\mathrm{ens}}
=\operatorname{cl}_{\|\cdot\|_X}
\operatorname{conv}F_{\mathrm{LL}}^{\mathrm{pure}}.
\]

这里 \(F_{\mathrm{ens}}\) 的搜索对象是归一化、有限内部能量的反对称 \(N\) 电子统计密度算符；\(\operatorname{conv}\) 是凸包，\(\operatorname{cl}_{\|\cdot\|_X}\) 是 \(X\) 范数拓扑中的下半连续闭包。在适当连续空间条件下，pure-state 与 ensemble \(N\)-representable 的**密度集合**可同为上述 \(\mathcal I_N\)，但 \(F_{\mathrm{LL}}^{\mathrm{pure}}\) 不能与其凸、下半连续闭包逐点无条件混同。教材不把该等式外推到未声明的函数空间或相互作用，也不宣称 \(F_{\mathrm L}\) 处处可微或每个 trial density 都是某个纯态基态密度。

### D-C03.6 Euler 条件与次梯度

固定粒子数约束下，若 \(F\) 在最优密度 \(n_*\) 可微，可形式上写

\[
\frac{\delta F}{\delta n(\mathbf r)}
+v(\mathbf r)=\mu,
\]

其中 \(\mu\) 是归一化约束的 Lagrange 乘子。若 \(F\) 只有凸次梯度，则相应条件是

\[
-v+\mu\in\partial F[n_*].
\]

常数 \(\mu\) 再次反映势的加法常数自由度。该次梯度表述不能简化为“每处都有唯一普通函数导数”。

### D-C03.7 D-C03 验收边界

D-C03 通过需要同时满足：

- HK 反证明示共同问题族、非简并/严格不等式条件和势的常数等价类；
- 不由非简并证明无条件推出简并情形中的唯一波函数；
- Levy 搜索域是 pure-state \(N\)-representable 密度；标准 Coulomb 域的内层 minimum 与外层 infimum 不混用；
- 系综搜索与凸性推导写出混合态线性结构；
- Lieb 对偶声明 \(X\)、\(X^*\)、范数拓扑、扩展值约定和势常数规范；
- HK、Levy 和 Lieb 的来源不互相冒名；
- 不声称精确泛函已知闭式或处处可微。

## D-C04 Kohn–Sham 分解与轨道变分

### D-C04.1 辅助非相互作用动能

对能由允许的非相互作用态产生的密度，先定义纯态搜索

\[
T_s^{\mathrm{pure}}[n]
=\inf_{\Phi\mapsto n}
\langle\Phi|\hat T|\Phi\rangle,
\]

其中 \(\Phi\) 限于归一化、有限动能的 Slater determinant。再定义系综搜索

\[
T_s^{\mathrm{ens}}[n]
=\inf_{\Gamma_s\mapsto n}
\operatorname{Tr}(\Gamma_s\hat T).
\]

这里

\[
\Gamma_s=\sum_a w_a|\Phi_a\rangle\langle\Phi_a|,
\qquad
w_a\ge0,
\qquad
\sum_a w_a=1,
\]

每个 \(\Phi_a\) 都是归一化、有限动能的 Slater determinant。本章后文无上标的 \(T_s\) 采用 \(T_s^{\mathrm{ens}}\)；单 determinant 特例明确写 \(T_s^{\mathrm{pure}}\)。定义这些泛函需要相应的 noninteracting \(N\)-representability，而不是密度已经作为某个局域一体势的基态出现。更强的 noninteracting \(v\)-representability 与普通局域 KS Euler 方程的势实现有关；若普通局域势不存在，则仍可使用 constrained-search 泛函、系综/次梯度或 generalized KS。

零温、整数占据且密度可由单个 determinant 表示时，取一组正交占据轨道：

\[
n(\mathbf r)=\sum_{i=1}^{N}|\phi_i(\mathbf r)|^2,
\]

\[
T_s[\{\phi_i\}]
=-\frac12\sum_{i=1}^{N}
\int\phi_i^*(\mathbf r)\nabla^2\phi_i(\mathbf r)\,d\mathbf r.
\]

简并或分数占据应使用系综及占据数 \(f_i\)，不能把单 determinant 整数占据公式无条件延伸到所有密度。

### D-C04.2 Hartree 导数

定义

\[
E_H[n]
=\frac12\iint
\frac{n(\mathbf r)n(\mathbf r')}{|\mathbf r-\mathbf r'|}
\,d\mathbf r\,d\mathbf r'.
\]

令 \(n\mapsto n+\eta\,\delta n\)，保留一阶项：

\[
\begin{aligned}
\delta E_H
&=\frac12\iint
\frac{\delta n(\mathbf r)n(\mathbf r')
+n(\mathbf r)\delta n(\mathbf r')}
{|\mathbf r-\mathbf r'|}
\,d\mathbf r\,d\mathbf r'\\
&=\int\delta n(\mathbf r)
\left[
\int\frac{n(\mathbf r')}{|\mathbf r-\mathbf r'|}\,d\mathbf r'
\right]\,d\mathbf r.
\end{aligned}
\]

交换哑变量后两项相等，因而

\[
v_H(\mathbf r)=\frac{\delta E_H}{\delta n(\mathbf r)}
=\int\frac{n(\mathbf r')}{|\mathbf r-\mathbf r'|}\,d\mathbf r'.
\]

同时

\[
\int v_H n=2E_H.
\]

### D-C04.3 交换相关定义和可微边界

KS 分解按定义写为

\[
F[n]=T_s[n]+E_H[n]+E_{xc}[n].
\]

因此

\[
E_{xc}[n]=F[n]-T_s[n]-E_H[n].
\]

若 \(E_{xc}\) 在所考虑方向上具有普通函数导数，定义

\[
v_{xc}(\mathbf r)=\frac{\delta E_{xc}}{\delta n(\mathbf r)}.
\]

这是条件性定义。整数粒子数处的导数不连续、仅存在次梯度或非局域 orbital-dependent 近似都可能要求系综、generalized KS 或其他变分对象。

### D-C04.4 正交约束变分

对整数占据轨道，能量泛函为

\[
\begin{aligned}
E[\{\phi_i\}]
&=-\frac12\sum_i\int\phi_i^*\nabla^2\phi_i\,d\mathbf r
+\int v_{\mathrm{ext}}n\,d\mathbf r\\
&\quad+E_H[n]+E_{xc}[n].
\end{aligned}
\]

施加

\[
\langle\phi_i|\phi_j\rangle=\delta_{ij}
\]

并引入 Hermitian 乘子矩阵 \(\Lambda\)：

\[
\mathcal L
=E-\sum_{ij}\Lambda_{ij}
(\langle\phi_i|\phi_j\rangle-\delta_{ij}).
\]

密度对复共轭轨道的一阶变化满足

\[
\frac{\delta n(\mathbf r)}{\delta\phi_i^*(\mathbf r')}
=\phi_i(\mathbf r)\delta(\mathbf r-\mathbf r').
\]

分别对 \(\phi_i^*\) 变分，得到

\[
\left[-\frac12\nabla^2
+v_{\mathrm{ext}}(\mathbf r)
+v_H(\mathbf r)
+v_{xc}(\mathbf r)
\right]\phi_i(\mathbf r)
=\sum_j\Lambda_{ji}\phi_j(\mathbf r).
\]

定义

\[
\hat h_{\mathrm{KS}}
=-\frac12\nabla^2+v_{\mathrm{ext}}+v_H+v_{xc}.
\]

由于 \(\Lambda\) Hermitian，存在占据子空间内的 unitary 变换将其对角化。变换不改变密度和 \(T_s\)，于是得到规范轨道方程

\[
\hat h_{\mathrm{KS}}\phi_i=\varepsilon_i\phi_i.
\]

该对角化只固定一种方便规范；简并子空间内仍有 unitary 自由度。

### D-C04.5 分数占据接口

若

\[
n=\sum_i f_i|\phi_i|^2,
\qquad
0\le f_i\le g_i,
\qquad
\sum_i f_i=N,
\]

则轨道变分、占据变分和粒子数约束必须一致处理。在固定 \(f_i>0\) 的简化变分中，每一轨道项携带相同的 \(f_i\) 权重；不能从整数占据推导中漏掉权重后宣称已覆盖有限温度。热平衡占据还来自自由能对 \(f_i\) 的变分并包含熵项。零温简并系综、数值 smearing 和物理 Mermin 温度是三个不同口径。

### D-C04.6 单电子精确抵消

对一个电子，\(\hat W=0\)，故在适当表示域上

\[
F[n]=T_s[n].
\]

因此

\[
E_{xc}[n]=-E_H[n],
\]

固定 \(\int n=1\) 时，允许变化满足 \(\int\delta n=0\)。若两个泛函在该约束流形上可微，只能推出

\[
v_{xc}(\mathbf r)=-v_H(\mathbf r)+C
\]

几乎处处成立。选定相同势零点后可取 \(C=0\)；一般常数只整体平移 KS 本征值，不改变轨道与密度。这是精确泛函的约束，不是对任意近似泛函的经验假设，也不能外推到一般多电子体系。

### D-C04.7 本征值和与总能量

对每条规范 KS 方程左乘 \(\phi_i^*\)、积分并按占据数求和：

\[
\sum_i f_i\varepsilon_i
=T_s+\int v_{\mathrm{ext}}n
+\int v_Hn+\int v_{xc}n.
\]

另一方面，

\[
E=T_s+\int v_{\mathrm{ext}}n+E_H+E_{xc}.
\]

利用 \(\int v_Hn=2E_H\)，消去 \(T_s+\int v_{\mathrm{ext}}n\)，得到

\[
E=\sum_i f_i\varepsilon_i
-E_H+E_{xc}-\int v_{xc}n.
\]

该式适用于本推导所声明的常规局域乘法 KS 势。含非局域算符的 generalized KS、不同自由能定义或后端特有能量修正需要单独公式，不能静默套用。

### D-C04.8 自洽固定点

方程中的 \(v_H\) 和 \(v_{xc}\) 依赖轨道产生的密度，因此完整问题是

\[
n_{\mathrm{in}}
\xrightarrow{v_H+v_{xc}}
h_{\mathrm{KS}}
\xrightarrow{\mathrm{solve}}
\{\phi_i,f_i\}
\xrightarrow{\mathrm{density}}
n_{\mathrm{out}}.
\]

自洽解满足 \(n_*=F[n_*]\)。只对一个冻结输入密度求解本征问题并不等于完成 KS 基态计算。混合、残差、Jacobian 稳定性和停止条件在第 7 章推导。

### D-C04.9 D-C04 验收边界

D-C04 通过需要同时满足：

- \(T_s\) 的 noninteracting \(N\)-representability 搜索域、局域势所需的 noninteracting \(v\)-representability 和单 determinant 特例分开陈述；
- Hartree 导数的因子 (1/2) 通过两项对称性正确消去；
- \(E_{xc}\) 被写成恒等定义，不缩减为“经典 Coulomb 剩余”；
- 轨道正交约束产生 Hermitian 乘子矩阵，规范方程来自 unitary 对角化；
- 普通 \(v_{xc}\) 的可微条件、次梯度与 generalized KS 边界明确；
- 分数占据、零温简并系综、数值 smearing 与 Mermin 温度不混用；
- 本征值和修正公式的局域 KS 条件和双计数来源明确；
- 完整 KS 是密度固定点问题；
- 不在 M5 隐含选择真实泛函、后端、材料、赝势或软件版本。

## 推导包来源与证据状态

| 内容 | 来源 | 状态 |
|---|---|---|
| 外势—密度唯一性与基态密度变分结构 | C-FND-02 | `PRIMARY_EXPLICIT`；本文件统一符号并显式补出条件 |
| pure-state constrained search | C-FND-05；C-FND-06 | `PRIMARY_EXPLICIT`；内层 minimum、外层 infimum 的分组为 `DIRECT_DERIVATION` |
| 凸、下半连续与势—密度对偶 | C-FND-06 | `PRIMARY_EXPLICIT`；函数空间边界按来源保留 |
| KS 辅助体系、能量分解与轨道方程 | C-FND-03；FND-01 | `PRIMARY_EXPLICIT`；变分和双计数代数为 `DIRECT_DERIVATION` |
| 有限温度统计 DFT 接口 | C-FND-04 | `PRIMARY_EXPLICIT`；本文件不选择实践温度或占据方案 |
| 两站点、单电子和数值口径例 | 第 6 章 `examples.md` | `PEDAGOGICAL` |
