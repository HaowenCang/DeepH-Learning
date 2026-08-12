# 第 6 章 Kohn–Sham 密度泛函理论

本章建立基态密度泛函理论的严格对象链：Hohenberg–Kohn（HK）定理说明在适用域内基态密度为何足以承载外势问题；Levy constrained search 把普适泛函扩展到纯态 \(N\)-representable 密度；Lieb 形式化给出 Coulomb 体系的凸、下半连续与对偶框架；Kohn–Sham（KS）构造再把未知相互作用动能的一部分替换为辅助非相互作用体系的动能。四者互相连接，但不是同一个定理，也不能互相冒名承担来源。

本章继续采用原子单位。主线限于固定核、固定电子数的非相对论 Coulomb 基态；有限温度、分数占据、自旋与 SOC 只在明确接口中讨论。真实泛函、赝势、材料、后端和软件版本继续保留到 M8。

## 6.1 DFT 问题的对象与条件

### 6.1.1 固定核外势问题

对 \(N\) 个电子，写

\[
\hat H[v]=\hat T+\hat W+\hat V[v],
\qquad
\hat V[v]=\sum_{i=1}^{N}v(\mathbf r_i),
\]

其中 \(\hat T\) 和电子—电子相互作用 \(\hat W\) 对所有外势问题相同，体系差异由 \(v(\mathbf r)\) 给出。固定核 Coulomb 外势是

\[
v_{\mathrm{ext}}(\mathbf r)
=-\sum_I\frac{Z_I}{|\mathbf r-\mathbf R_I|}.
\]

核—核排斥是固定结构下的常数，通常在电子问题之外加回。若同时改变 \(N\)、相互作用、边界条件或 Hilbert 空间，就不是 HK 定理中“只改变外势”的同一问题族。

### 6.1.2 密度的物理域

候选密度至少满足

\[
n(\mathbf r)\ge0,
\qquad
\int n(\mathbf r)\,d\mathbf r=N.
\]

仅满足非负和归一化不足以保证有限动能或某个波函数能够产生该密度。常见的 Coulomb 体系密度域还要求 \(\sqrt n\in H^1(\mathbb R^3)\)，从而 \(n\in L^1\cap L^3\)。必须区分：

- pure-state \(N\)-representable：存在归一化反对称纯态产生 \(n\)；
- ensemble \(N\)-representable：存在允许混合态的 \(N\) 电子密度矩阵产生 \(n\)；
- interacting \(v\)-representable：\(n\) 是某个相互作用外势问题的基态密度；
- noninteracting \(v\)-representable：\(n\) 是某个局域一体势下非相互作用体系的基态密度，必要时允许系综。

在标准连续空间与有限动能条件下，pure-state 和 ensemble \(N\)-representable 的**密度集合**可以同为下文的 \(\mathcal I_N\)，但两者搜索的状态类不同，相应 constrained-search 泛函值和凸性也不能因此混同。interacting/noninteracting \(v\)-representability 是更强的“作为某个外势基态密度”条件，也不等于 \(N\)-representability。特别地，定义 \(T_s[n]\) 只需要在非相互作用状态类中对固定密度搜索；要把 Euler 条件实现为普通局域 KS 势，还需要 noninteracting \(v\)-representability 或相应系综/次梯度扩展。

### 6.1.3 外势加常数

若

\[
v'(\mathbf r)=v(\mathbf r)+C,
\]

则

\[
\hat H[v']=\hat H[v]+NC.
\]

本征态和密度不变，所有 \(N\) 电子能量整体平移 \(NC\)。因此，密度最多把外势确定到加法常数；能量零点和势零点必须有约定。

## 6.2 HK、Levy 与 Lieb 的分工

### 6.2.1 HK 外势—密度唯一性

在非简并基态的标准反证中，假设两个不相差常数的局域标量外势 \(v\)、\(v'\) 产生同一基态密度 \(n\)，基态分别为 \(\Psi\)、\(\Psi'\)，能量为 \(E_0\)、\(E_0'\)。还需先排除两势共享同一基态。若某个非零 \(\Psi\) 同时满足两条 Schrödinger 方程，相减得到

\[
\left[\sum_{i=1}^{N}\bigl(v-v'\bigr)(\mathbf r_i)\right]\Psi
=(E_0-E_0')\Psi.
\]

在允许的局域势类、共同算符定义域以及波函数几乎处处非零或相应唯一延拓条件下，这要求 \(\sum_i(v-v')(\mathbf r_i)\) 在构型空间中几乎处处为常数；逐个改变一个电子坐标可推出 \(v-v'\) 几乎处处为常数，与假设矛盾。因此 \(\Psi\ne\Psi'\)，非简并性使对方基态不是本方基态，Rayleigh–Ritz 严格不等式给出

\[
E_0
<E_0'
+\int [v(\mathbf r)-v'(\mathbf r)]n(\mathbf r)\,d\mathbf r,
\]

\[
E_0'
<E_0
+\int [v'(\mathbf r)-v(\mathbf r)]n(\mathbf r)\,d\mathbf r.
\]

相加得到 \(E_0+E_0'<E_0+E_0'\)，矛盾。因此在这些条件下，基态密度确定外势到常数，进而确定 Hamiltonian 与基态可观测量。

严格不等式依赖共同基态排除步骤。对简并**纯态**基态密度，两个 Rayleigh–Ritz 关系先只是不等号 \(\le\)；若密度相同，两式相加迫使等号同时成立，所以交叉 trial state 也是对方 Hamiltonian 的基态，随后应用同一个共同基态步骤，仍得到局域标量势的等价类唯一。该结论不唯一选出简并子空间中的某条波函数。简并**系综**还需声明由哪些共同能量的基态及何种权重产生密度；对自旋密度、流密度等多基本变量理论，势非唯一性可能更复杂，不能把标量密度命题直接外推。简并与多密度理论的边界见 C-FND-07。

### 6.2.2 HK 变分结构

对由某外势基态产生的密度，可以把内部能量写成与具体外势无关的泛函，形式上

\[
F_{\mathrm{HK}}[n]
=\langle\Psi[n]|\hat T+\hat W|\Psi[n]\rangle.
\]

总能量泛函为

\[
E_v[n]=F_{\mathrm{HK}}[n]
+\int v(\mathbf r)n(\mathbf r)\,d\mathbf r.
\]

真实基态密度使其取基态能量。这里的 \(\Psi[n]\) 写法对 \(v\)-representability 和简并有隐含条件；HK 1964 的结论不等于已经给出所有 \(N\)-representable 密度上的可计算闭式 \(F[n]\)。

### 6.2.3 Levy 纯态 constrained search

Levy 的形式化把“先固定密度，再在所有产生该密度的反对称波函数中搜索”写为

\[
F_{\mathrm{LL}}^{\mathrm{pure}}[n]
=\min_{\Psi\mapsto n}
\langle\Psi|\hat T+\hat W|\Psi\rangle.
\]

搜索域是归一化反对称 \(N\) 电子纯态，并要求有限内部能量。在本章已经声明的标准三维 Coulomb 密度域 \(\mathcal I_N\) 上，Levy 给出 constrained-minimum 构造，Lieb 的存在性结果保证内层下确界可由至少一个波函数达到，因此这里写 minimum；最小化波函数仍可能不唯一。离开该函数空间、改变相互作用或算符条件时必须重新审查可达性。基态能量的**外层**搜索满足

\[
E_0[v]
=\inf_{n\in\mathcal I_N}
\left\{
F_{\mathrm{LL}}^{\mathrm{pure}}[n]
+\int vn
\right\},
\]

其中 \(\mathcal I_N\) 是声明过的 pure-state \(N\)-representable 密度域。外层 infimum 是否取得还取决于给定外势问题是否存在基态。该两层搜索解决了只在 \(v\)-representable 密度上定义泛函的困难，但不是从 HK 1964 逐行代数推出的附带步骤。

### 6.2.4 Lieb 的凸与对偶形式

允许混合态时，可定义系综 constrained-search 泛函

\[
F_{\mathrm{ens}}[n]
=\min_{\Gamma\mapsto n}
\operatorname{Tr}\Gamma(\hat T+\hat W),
\]

其中 \(\Gamma\) 是 \(N\) 电子统计密度算符；在本章标准条件下相应内层 minimum 也可达到。令密度 Banach 空间

\[
X=L^1(\mathbb R^3)\cap L^3(\mathbb R^3),
\qquad
\|n\|_X=\|n\|_1+\|n\|_3,
\]

其对偶配对势空间可取

\[
X^*=L^\infty(\mathbb R^3)+L^{3/2}(\mathbb R^3).
\]

在固定 \(N\) 上，势唯一性使用商空间 \(X^*/\mathbb R\)，或等价地先固定一个势零点。把泛函在不可接受密度上扩展为 \(+\infty\) 后，Lieb 形式化使用 Legendre–Fenchel 对偶

\[
F_{\mathrm L}[n]
=\sup_v
\left\{
E_0[v]-\int v(\mathbf r)n(\mathbf r)\,d\mathbf r
\right\}.
\]

在 \(X\) 的上述范数拓扑中，\(F_{\mathrm L}\) 是凸、下半连续的扩展值泛函，并与能量的凹泛函形成对偶：

\[
E_0[v]
=\inf_n
\left\{
F_{\mathrm L}[n]+\int vn
\right\}.
\]

在标准三维 Coulomb 设置中，可取密度域

\[
\mathcal I_N=
\left\{
n\ge0, 
\int n=N, 
\sqrt n\in H^1(\mathbb R^3)
\right\}
\subset L^1\cap L^3,
\]

在本章的标准三维 Coulomb 条件、固定 \(N\)、共同扩展值约定和 \(X\) 的范数拓扑下，精确关系是

\[
F_{\mathrm L}
=F_{\mathrm{ens}}
=\operatorname{cl}_{\|\cdot\|_X}
\operatorname{conv}F_{\mathrm{LL}}^{\mathrm{pure}}.
\]

这里 \(\operatorname{conv}\) 表示凸包，\(\operatorname{cl}_{\|\cdot\|_X}\) 表示在 \(X\) 范数拓扑中的下半连续闭包；\(F_{\mathrm{ens}}\) 的搜索对象是归一化、有限内部能量的反对称 \(N\) 电子统计密度算符。等式只在已声明的标准条件和共同扩展约定下使用。密度层面的 pure/ensemble \(N\)-representable 域可同为 \(\mathcal I_N\)，但 \(F_{\mathrm{LL}}^{\mathrm{pure}}\) 不能与其凸、下半连续闭包逐点无条件混同。本章不声称最小化态唯一，也不声称泛函处处可微。

### 6.2.5 三层来源防错表

| 结论 | 正确来源层级 | 不允许的外推 |
|---|---|---|
| 基态密度确定外势到常数；基态能量有密度变分结构 | HK 1964 | 已知可计算精确泛函；任意简并情形自动沿用同一严格反证 |
| 在固定 pure-state \(N\)-representable 密度上作 constrained minimum | Levy 1979；可达性由 Lieb 1983 的标准 Coulomb 结果闭合 | 系综凸闭包、处处可微或最小化态唯一 |
| \(X=L^1\cap L^3\) 范数拓扑中的凸、下半连续与势—密度对偶 | Lieb 1983 | 无需声明函数空间；任意 trial density 都是纯态基态密度 |

## 6.3 KS 构造与变分

### 6.3.1 非相互作用动能与能量分解

先分开定义两种非相互作用 constrained search。纯态形式为

\[
T_s^{\mathrm{pure}}[n]
=\inf_{\Phi\mapsto n}
\langle\Phi|\hat T|\Phi\rangle,
\]

其中 \(\Phi\) 限于归一化、有限动能的 Slater determinant。系综形式为

\[
T_s^{\mathrm{ens}}[n]
=\inf_{\Gamma_s\mapsto n}
\operatorname{Tr}(\Gamma_s\hat T).
\]

这里 \(\Gamma_s=\sum_a w_a|\Phi_a\rangle\langle\Phi_a|\)，\(w_a\ge0\)、\(\sum_a w_a=1\)，每个 \(\Phi_a\) 都是归一化、有限动能的 Slater determinant。本章无上标的 \(T_s\) 统一指 \(T_s^{\mathrm{ens}}\)；只有明确限制到单 determinant 时才写 \(T_s^{\mathrm{pure}}\)。定义这些泛函所需的是相应的 noninteracting \(N\)-representability；它不要求 \(n\) 已经是某个局域一体势的基态密度。后者是更强的 noninteracting \(v\)-representability，并关系到普通局域 KS Euler 方程能否实现。

常规零温整数占据且可由单 determinant 表示时，

\[
T_s=
-\frac12\sum_{i=1}^{N}
\int \phi_i^*(\mathbf r)\nabla^2\phi_i(\mathbf r)\,d\mathbf r.
\]

对简并或分数占据，使用

\[
n(\mathbf r)=\sum_i f_i|\phi_i(\mathbf r)|^2,
\qquad
0\le f_i\le g_i,
\qquad
\sum_i f_i=N,
\]

并把 \(T_s\) 写为占据加权和；\(g_i\) 取决于是否显式包含自旋。

定义 Hartree 能

\[
E_H[n]
=\frac12\iint
\frac{n(\mathbf r)n(\mathbf r')}{|\mathbf r-\mathbf r'|}
\,d\mathbf r\,d\mathbf r'.
\]

交换相关泛函按恒等分解定义为

\[
E_{xc}[n]
=F[n]-T_s[n]-E_H[n].
\]

因此，\(E_{xc}\) 不只是“剩余 Coulomb 相关”：它同时补偿真实相互作用动能与 \(T_s\) 的差、非经典交换以及相关效应。

总能量为

\[
E[n]
=T_s[n]+E_H[n]+E_{xc}[n]
+\int v_{\mathrm{ext}}(\mathbf r)n(\mathbf r)\,d\mathbf r.
\]

### 6.3.2 轨道正交约束

以整数占据轨道说明主要变分步骤。对

\[
\langle\phi_i|\phi_j\rangle=\delta_{ij}
\]

引入 Hermitian Lagrange 乘子矩阵 \(\Lambda\)，变分量为

\[
\mathcal L
=E[\{\phi_i\}]
-\sum_{ij}\Lambda_{ij}
(\langle\phi_i|\phi_j\rangle-\delta_{ij}).
\]

若 \(E_{xc}\) 在所考虑密度方向上具有普通函数导数，定义

\[
v_{xc}(\mathbf r)=\frac{\delta E_{xc}}{\delta n(\mathbf r)}.
\]

Hartree 导数为

\[
v_H(\mathbf r)
=\frac{\delta E_H}{\delta n(\mathbf r)}
=\int\frac{n(\mathbf r')}{|\mathbf r-\mathbf r'|}\,d\mathbf r'.
\]

轨道变分得到

\[
\hat h_{\mathrm{KS}}\phi_i
=\sum_j\Lambda_{ji}\phi_j,
\]

\[
\hat h_{\mathrm{KS}}
=-\frac12\nabla^2
+v_{\mathrm{ext}}+v_H+v_{xc}.
\]

在占据子空间内 unitary 对角化 \(\Lambda\)，得到规范 KS 方程

\[
\hat h_{\mathrm{KS}}\phi_i
=\varepsilon_i\phi_i.
\]

若泛函只具有次梯度、存在整数粒子数导数不连续或密度不可由普通局域势表示，不能无条件使用处处存在的乘法函数 \(v_{xc}\)；应改用次微分、系综或更一般广义 KS 框架。

### 6.3.3 自洽性

KS Hamiltonian 依赖由其本征态产生的密度：

\[
n^{(m)}
\longrightarrow v_H[n^{(m)}]+v_{xc}[n^{(m)}]
\longrightarrow \hat h_{\mathrm{KS}}[n^{(m)}]
\longrightarrow \{\phi_i^{(m)},\varepsilon_i^{(m)}\}
\longrightarrow n_{\mathrm{out}}^{(m)}.
\]

目标是求固定点 \(n_*=F[n_*]\)，而不是只对某个冻结势对角化一次。混合和收敛问题留到第 7 章。

### 6.3.4 KS 本征值和不等于总能量

对局域乘法势的常规 KS 方程，

\[
\sum_i f_i\varepsilon_i
=T_s+\int v_{\mathrm{ext}}n
+\int v_Hn+\int v_{xc}n.
\]

由于 \(\int v_Hn=2E_H\)，总能量可重写为

\[
E
=\sum_i f_i\varepsilon_i
-E_H[n]+E_{xc}[n]
-\int v_{xc}(\mathbf r)n(\mathbf r)\,d\mathbf r.
\]

因此直接求本征值和会重复或错误计入 Hartree 与交换相关贡献。KS 轨道和本征值首先是辅助体系对象；不能普遍把全部 \(\varepsilon_i\) 等同于真实多体激发能。

## 6.4 自旋、有限温度与近似泛函接口

### 6.4.1 自旋层级

无自旋极化的标量密度、共线自旋 DFT 的 \((n_\uparrow,n_\downarrow)\)、非共线自旋密度矩阵以及含 SOC 的 spinor Hamiltonian 是不同对象。选择某一层级会改变密度变量、Hamiltonian 块结构和对称性。M5 只登记这些选项，不在 M8 前选择实践层级。

### 6.4.2 Mermin 有限温度

Mermin 扩展针对固定温度和化学势的统计系综。电子自由能包含能量与熵项，常见辅助占据呈 Fermi–Dirac 形式。有限温度自洽所报告的量可能是自由能、内能或带熵修正的外推量；标签必须明确。

数值 smearing 可以用于改善金属占据和积分收敛，但“使用了宽化参数”不自动证明目标物理体系处于对应温度。应分别登记：

- 占据函数与参数；
- 该参数是否被解释为物理电子温度；
- 收敛判据使用的能量或自由能；
- 最终报告量是否作零温外推或熵修正。

### 6.4.3 泛函分类不是实践选择

LDA、GGA、meta-GGA、hybrid 等名称描述不同信息依赖和近似层级。列出类别不等于选择具体泛函。hybrid 或其他 generalized KS 方法还可能引入非局域算符，使“一个局域 \(v_{xc}(\mathbf r)\)”的标准 KS 形式不再完整。M8 前所有具体选择保持 \(\mathrm{UNRESOLVED\_M8}\)。

## 6.5 标签语义与 DeepH 边界

### 6.5.1 误差层级

应区分：

1. HK/Levy/Lieb/KS 的精确形式化边界；
2. \(E_{xc}\) 的近似误差；
3. 全电子或赝势/PAW 等理论对象差异；
4. 基组、网格、采样、占据和有限温度误差；
5. SCF 与本征求解收敛误差；
6. 从后端表示投影/重建到标签矩阵的误差；
7. DeepH 对固定标签映射的统计学习误差。

后层拟合更准确不会自动消除前层误差。网络对近似 KS Hamiltonian 的矩阵误差趋近于零，只说明它复现了该标签语义。

### 6.5.2 必须登记的 DFT 语义

一个 KS Hamiltonian 标签至少需要理论层级、xc、全电子/赝势身份、相对论与自旋处理、基/网格、采样、电子数与占据、smearing/温度、SCF/本征阈值、能量口径、输出单位、轨道映射、相位/Fourier 约定和投影质量。完整 schema 见阶段 C 标签模板。

### 6.5.3 M8/M9 授权边界

本章例题只使用解析密度、有限矩阵和合成泛函。M8 前不安装 DeepH、不下载正式数据、不生成 DFT 标签，也不选择材料、后端、泛函、赝势或实践版本。M7-I 全量独立总审计通过后才准备进入 M8 集中决策；M8 冻结后，M9 外部动作前仍须再次取得明确授权。

## 6.6 本章可验证结论

- HK 的非简并反证为何只确定外势到常数；
- HK、Levy pure-state constrained search 与 Lieb 凸对偶各自承担什么；
- \(N\)-representability、相互作用/非相互作用 \(v\)-representability 和系综边界为何不能混用；
- \(T_s\)、\(E_H\) 与 \(E_{xc}\) 如何组成 KS 恒等分解；
- 正交约束如何产生 Lagrange 乘子矩阵并化为规范 KS 方程；
- \(v_{xc}=\delta E_{xc}/\delta n\) 需要什么可微条件；
- KS 本征值和为什么不是总能量；
- smearing、物理电子温度、自由能和零温外推为何必须分开；
- DeepH 为什么只能继承而不能消除标签理论层级。

完整推导见 `04_derivations/stageC/06_kohn_sham_variation.md`，例题见 `examples.md`，Q6-01—Q6-10 与逐题解答见 `06_exercises/03-stageC/06_kohn_sham_dft/`。
