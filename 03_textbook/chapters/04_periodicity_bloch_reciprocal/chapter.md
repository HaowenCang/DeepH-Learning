# 第 4 章　周期性、Bloch 定理与倒空间

## 4.0 学习目标、范围与约定

本章在有限 Born–von Karman 周期晶格上建立“平移对称—Bloch 标记—局域轨道 Bloch 和—实/倒空间 Fourier 对”的完整链条。完成本章后，应能区分主动平移本征值与坐标波函数准周期条件，逐式验证正反变换的符号和归一化，并判断实空间共轭配对、轨道中心规范及 \(\mathbf k\sim\mathbf k+\mathbf G\) 的适用方式。

本章所有定义服从[阶段 B 统一约定](../../stageB_conventions.md)，来源边界见[资料包](sources.md)，逐式推导见[D-B05/D-B06](../../../04_derivations/stageB/04_bloch_fourier.md)。例题仅使用有限循环晶格和合成矩阵块，均为 `PEDAGOGICAL`；不声明 DeepH 软件格式、真实材料跃迁参数或 DFT 后端约定。

## 4.1 晶格、倒格子与有限周期条件

### 4.1.1 直接晶格与原胞

直接晶格由

\[
\mathbf R=\sum_{i=1}^{d}n_i\mathbf a_i,
\qquad n_i\in\mathbb Z
\]

生成。原胞是平移后铺满空间的基本区域，体积记为 \(\Omega_c\)。原胞选择并不唯一；改变原胞或轨道原点时，必须重新登记晶格坐标和相位约定。

### 4.1.2 倒格子与 Brillouin 区

倒格基矢满足

\[
\mathbf b_i\cdot\mathbf a_j=2\pi\delta_{ij},
\]

倒格矢为 \(\mathbf G=\sum_i m_i\mathbf b_i\)。因此对任意晶格矢 \(\mathbf R\)，

\[
e^{i\mathbf G\cdot\mathbf R}=1.
\]

第一 Brillouin 区是倒格子 Wigner–Seitz 原胞；任意等体积倒空间原胞也可用于积分，只要边界和权重定义一致。

### 4.1.3 Born–von Karman 离散化

令超胞在第 \(i\) 个方向包含 \(N_i\) 个原胞，总数 \(N=\prod_iN_i\)。有限平移类和对偶波矢为

\[
\mathcal R_N=\left\{\sum_i n_i\mathbf a_i:0\le n_i<N_i\right\},
\]

\[
\mathcal K_N=\left\{\sum_i\frac{m_i}{N_i}\mathbf b_i:0\le m_i<N_i\right\}.
\]

证据类型：`DIRECT_DERIVATION`。有限角色正交关系为

\[
\frac1N\sum_{\mathbf k\in\mathcal K_N}
e^{i\mathbf k\cdot(\mathbf R-\mathbf R')}
=\delta_{\mathbf R,\mathbf R'},
\]

其中等号按超胞周期等价类理解。它是后续逆变换的代数核心。

## 4.2 平移对称与 Bloch 定理

### 4.2.1 平移算符约定

本章采用主动平移

\[
(\hat T_{\mathbf R}\psi)(\mathbf r)=\psi(\mathbf r-\mathbf R).
\]

若周期 Hamiltonian 满足 \([\hat H,\hat T_{\mathbf R}]=0\)，平移算符彼此交换且为幺正算符。可在每个能量子空间中选择平移共同本征态；简并时共同本征基不唯一，但角色标签仍可选择。

### 4.2.2 Bloch 条件的两个等价写法

证据类型：`DIRECT_DERIVATION`。有限平移群的一维角色可写为

\[
\hat T_{\mathbf R}|\psi_{n\mathbf k}\rangle
=e^{-i\mathbf k\cdot\mathbf R}|\psi_{n\mathbf k}\rangle.
\]

按主动平移定义，坐标波函数满足

\[
\psi_{n\mathbf k}(\mathbf r+\mathbf R)
=e^{+i\mathbf k\cdot\mathbf R}\psi_{n\mathbf k}(\mathbf r).
\]

第一式的负号与第二式的正号来自主动平移和坐标移位的方向差异。若在引用资料中看到相反符号，应先核对平移算符和 Bloch 和的定义，不能直接判定其中一方错误。

等价地，写成

\[
\psi_{n\mathbf k}(\mathbf r)
=e^{i\mathbf k\cdot\mathbf r}u_{n\mathbf k}(\mathbf r),
\qquad
u_{n\mathbf k}(\mathbf r+\mathbf R)=u_{n\mathbf k}(\mathbf r).
\]

### 4.2.3 \(\mathbf k\) 与 \(\mathbf k+\mathbf G\)

因为 \(e^{i\mathbf G\cdot\mathbf R}=1\)，\(\mathbf k\) 与 \(\mathbf k+\mathbf G\) 给出相同的晶格平移角色。能量满足倒格周期性，但周期部分或局域轨道系数可能因所选基规范而变化。因此“相同能带”不等于“所有系数逐元素相同”。

## 4.3 局域轨道 Bloch 和

### 4.3.1 Cell-phase 定义

设 \(a=(i,\mu)\) 是原胞内原子—轨道复合指标，\(|\phi_{a\mathbf R}\rangle\) 是第 \(\mathbf R\) 个晶胞中的局域轨道。本章冻结

\[
|\phi_{a\mathbf k}\rangle
=\frac1{\sqrt N}\sum_{\mathbf R\in\mathcal R_N}
e^{+i\mathbf k\cdot\mathbf R}|\phi_{a\mathbf R}\rangle.
\]

证据类型：`DIRECT_DERIVATION`。重标记求和指标可得

\[
\hat T_{\mathbf T}|\phi_{a\mathbf k}\rangle
=e^{-i\mathbf k\cdot\mathbf T}|\phi_{a\mathbf k}\rangle,
\]

所以该定义与 4.2 节的符号一致。\(1/\sqrt N\) 使不同离散 \(\mathbf k\) 块的归一化与有限角色正交关系相容。

### 4.3.2 矩阵块与 \(\mathbf k\) 块解耦

定义

\[
H_{ab}(\mathbf R)
=\langle\phi_{a\mathbf0}|\hat H|\phi_{b\mathbf R}\rangle,
\qquad
S_{ab}(\mathbf R)
=\langle\phi_{a\mathbf0}|\phi_{b\mathbf R}\rangle.
\]

平移不变性和有限角色正交关系给出

\[
\langle\phi_{a\mathbf k}|\hat H|\phi_{b\mathbf k'}\rangle
=\delta_{\mathbf k,\mathbf k'}H_{ab}(\mathbf k),
\]

其中

\[
H(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}H(\mathbf R),
\qquad
S(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}S(\mathbf R).
\]

不同 \(\mathbf k\) 块因此可以分别处理。第 9 章将在每个块上求解 \(H(\mathbf k)c=ES(\mathbf k)c\)。

## 4.4 闭合 Fourier 对

### 4.4.1 正变换与逆变换

证据类型：`DIRECT_DERIVATION`。与上式相容的逆变换为

\[
H(\mathbf R)=\frac1N\sum_{\mathbf k\in\mathcal K_N}
e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\]

\[
S(\mathbf R)=\frac1N\sum_{\mathbf k\in\mathcal K_N}
e^{-i\mathbf k\cdot\mathbf R}S(\mathbf k).
\]

把正变换代入逆变换后，有限角色正交关系精确恢复原块。\(1/N\) 位置并非普遍唯一；也可在正反变换两侧对称分配归一化，但必须整套一致。本教材不混用不同规范。

### 4.4.2 有限、采样与截断的区别

完整有限离散对上的正反变换在浮点误差范围内可逆。减少 \(\mathbf k\) 点会改变离散对；删除远程 \(H(\mathbf R)\) 块会改变被变换的函数；两者是不同误差源。仅在同一完整离散对内增加计算精度，不能恢复已经删除的实空间信息。

### 4.4.3 无限极限

若各 \(N_i\to\infty\) 且 \(f\) 足够规则，则

\[
\frac1N\sum_{\mathbf k}f(\mathbf k)
\longrightarrow
\frac1{V_{\mathrm{BZ}}}\int_{\mathrm{BZ}}f(\mathbf k)\,d^d\mathbf k
=\frac{\Omega_c}{(2\pi)^d}
\int_{\mathrm{BZ}}f(\mathbf k)\,d^d\mathbf k.
\]

有限 Kronecker delta 与无限体系的 Dirac delta 不是同一对象；正文和代码必须明确当前使用哪一层级。

## 4.5 实空间厄米关系

### 4.5.1 指标交换与负平移

证据类型：`DIRECT_DERIVATION`。由 \(\hat H=\hat H^\dagger\) 和平移不变性，

\[
H_{ab}(\mathbf R)^*=H_{ba}(-\mathbf R),
\]

即

\[
H(\mathbf R)^\dagger=H(-\mathbf R).
\]

矩阵 dagger 同时执行复共轭和 \(a,b\) 指标交换。只检查 \(H(\mathbf R)\) 每个元素是否为实数，或只补充 \(-\mathbf R\) 而不转置指标，都不足以保证 Hermiticity。

### 4.5.2 \(\mathbf k\) 空间 Hermiticity

将上述关系代入 Fourier 和可得

\[
H(\mathbf k)^\dagger=H(\mathbf k),
\qquad
S(\mathbf k)^\dagger=S(\mathbf k).
\]

然而，\(S(\mathbf k)\) Hermitian 不自动意味着正定；广义本征问题仍要求对每个受测 \(\mathbf k\) 检查 \(S(\mathbf k)\succ0\)。

## 4.6 轨道中心规范

### 4.6.1 含中心相位的替代基

若原胞内轨道中心为 \(\boldsymbol\tau_a\)，可定义

\[
|\bar\phi_{a\mathbf k}\rangle
=\frac1{\sqrt N}\sum_{\mathbf R}
e^{i\mathbf k\cdot(\mathbf R+\boldsymbol\tau_a)}
|\phi_{a\mathbf R}\rangle.
\]

列基关系为

\[
\bar{\boldsymbol\Phi}_{\mathbf k}
=\boldsymbol\Phi_{\mathbf k}U(\mathbf k),
\qquad
U_{ab}(\mathbf k)=\delta_{ab}e^{i\mathbf k\cdot\boldsymbol\tau_a}.
\]

### 4.6.2 同步变换与物理不变量

证据类型：`DIRECT_DERIVATION`。同一抽象问题要求

\[
\bar H=U^\dagger HU,
\qquad
\bar S=U^\dagger SU,
\qquad
\bar c=U^{-1}c.
\]

同步变换保持广义谱、态范数和残差。只变换 \(H\) 而保持旧 \(S\) 一般会改变广义谱；这不是规范的物理效应，而是不一致表示造成的错误。

在中心规范中，\(\mathbf k\to\mathbf k+\mathbf G\) 还会带来

\[
D_G=\operatorname{diag}(e^{i\mathbf G\cdot\boldsymbol\tau_a})
\]

的轨道依赖基相位。能量仍倒格周期，但系数比较必须先按 \(D_G\) 对齐基规范。即使完成该对齐，数值本征矢还允许每条非简并带具有任意整体相位；简并处允许简并子空间内的幺正混合，应比较投影算符或先对齐整个简并子空间，而不能要求逐带逐元素相等。

## 4.7 失败边界与验证入口

- 正、逆 Fourier 指数同号：通常重建为错误的平移映射；
- 缺少 \(-\mathbf R\) 共轭块：\(H(\mathbf k)\) 一般出现非零反 Hermitian 部分；
- 轨道中心相位只施加到 \(H\)：广义谱或态范数改变；
- 把有限离散恒等式与无限积分混写：归一化和 delta 对象错误；
- 只检查 \(S(\mathbf k)=S(\mathbf k)^\dagger\)：遗漏正定条件。

[例题](examples.md)给出单轨道复跃迁链、有限正反变换、缺失共轭块和两轨道规范失败。[练习](../../../06_exercises/02-stageB/04_bloch_fourier/problem/readme.md)与[参考解答](../../../06_exercises/02-stageB/04_bloch_fourier/solution/readme.md)逐项覆盖上述链条。随机复矩阵块和批量测试将在 M4-07 固化。

### 自学检查

1. 为什么主动平移本征值的指数与 \(\psi(\mathbf r+\mathbf R)\) 的指数符号相反？
2. 为什么 \(1/\sqrt N\) 出现在 Bloch 和中，而矩阵 Fourier 正变换没有该因子？
3. 如何由 \(H(\mathbf R)^\dagger=H(-\mathbf R)\) 推出 \(H(\mathbf k)\) Hermitian？
4. Cell-phase 与中心规范之间哪些对象必须同步变换？
5. 完整离散逆变换、有限 \(\mathbf k\) 采样和实空间截断为何不能混为同一误差？
