# D-C01—D-C02：固定核分离、多电子反对称性与一体约化对象

本推导包对应第 5 章，只使用后端无关的非相对论 Coulomb Hamiltonian、有限粒子数 Hilbert 空间和教学矩阵。目标是把正文中的关键结论写成可逐步复核的等式，并明确每一步所需条件。

## D-C01 从电子—核 Hamiltonian 到固定核电子问题

### D-C01.1 起点与条件

采用原子单位，忽略外磁场、相对论、量子电动力学和核自旋。完整 Hamiltonian 分解为

\[
\hat H=\hat T_N+\hat H_{\mathrm e}(\mathbf R)+E_{\mathrm{NN}}(\mathbf R),
\]

其中

\[
\hat T_N=-\sum_I\frac{\nabla_I^2}{2M_I},
\]

\[
\hat H_{\mathrm e}(\mathbf R)
=-\frac12\sum_i\nabla_i^2
+\sum_{i<j}\frac1{r_{ij}}
-\sum_{iI}\frac{Z_I}{|\mathbf r_i-\mathbf R_I|},
\]

\[
E_{\mathrm{NN}}(\mathbf R)
=\sum_{I<J}\frac{Z_IZ_J}{|\mathbf R_I-\mathbf R_J|}.
\]

电子本征态在每个固定 \(\mathbf R\) 上满足

\[
\hat H_{\mathrm e}(\mathbf R)|\Phi_a(\mathbf R)\rangle
=E_a^{\mathrm e}(\mathbf R)|\Phi_a(\mathbf R)\rangle,
\qquad
\langle\Phi_a(\mathbf R)|\Phi_b(\mathbf R)\rangle_{\mathbf r}
=\delta_{ab}.
\]

这里假设在所用电子子空间中可以选择足够光滑的局部规范。简并点附近单条本征矢可能无法全局光滑选取，必须改用简并子空间或 diabatic 表示。

### D-C01.2 绝热基展开

将总态展开为

\[
|\Psi\rangle=\sum_b \chi_b(\mathbf R)|\Phi_b(\mathbf R)\rangle.
\]

对单个核坐标梯度，

\[
\nabla_I(\chi_b\Phi_b)
=(\nabla_I\chi_b)\Phi_b
+\chi_b\nabla_I\Phi_b,
\]

\[
\nabla_I^2(\chi_b\Phi_b)
=(\nabla_I^2\chi_b)\Phi_b
+2(\nabla_I\chi_b)\cdot(\nabla_I\Phi_b)
+\chi_b\nabla_I^2\Phi_b.
\]

左乘 \(\langle\Phi_a|\) 并对电子坐标积分。定义

\[
\mathbf d_{ab}^{I}
=\langle\Phi_a|\nabla_I\Phi_b\rangle_{\mathbf r},
\qquad
\tau_{ab}^{I}
=\langle\Phi_a|\nabla_I^2\Phi_b\rangle_{\mathbf r}.
\]

得到耦合核方程

\[
\begin{aligned}
&\left[
-\sum_I\frac{\nabla_I^2}{2M_I}
+E_a^{\mathrm e}(\mathbf R)
+E_{\mathrm{NN}}(\mathbf R)
\right]\chi_a(\mathbf R) \\\
&\quad
-\sum_{I,b}\frac1{M_I}
\mathbf d_{ab}^{I}\cdot\nabla_I\chi_b
-\sum_{I,b}\frac1{2M_I}
\tau_{ab}^{I}\chi_b
=E\chi_a.
\end{aligned}
\]

这一步没有作 BO 近似；它只是把完整问题写到 \(\mathbf R\)-依赖电子基中。

### D-C01.3 单面 BO 方程

若选定电子态 \(a\) 并只忽略 \(b\ne a\) 的非对角耦合，前一节方程中仍保留 \(\mathbf d_{aa}^{I}\) 和 \(\tau_{aa}^{I}\)。由归一化条件可知 \(\mathbf d_{aa}^{I}\) 为纯虚量，并且

\[
\tau_{aa}^{I}
=\nabla_I\cdot\mathbf d_{aa}^{I}
-\langle\nabla_I\Phi_a|\nabla_I\Phi_a\rangle.
\]

定义

\[
\mathbf A_a^I=i\mathbf d_{aa}^{I},
\]

\[
\Phi_a^{\mathrm{BH}}
=\sum_I\frac1{2M_I}
\left[
\langle\nabla_I\Phi_a|\nabla_I\Phi_a\rangle
-|\mathbf d_{aa}^{I}|^2
\right].
\]

将对角导数项配方，得到规范协变的单面有效核方程

\[
\left[
\sum_I\frac{(-i\nabla_I-\mathbf A_a^I)^2}{2M_I}
+U_a(\mathbf R)
+\Phi_a^{\mathrm{BH}}(\mathbf R)
\right]\chi_a
=E\chi_a,
\qquad
U_a=E_a^{\mathrm e}+E_{\mathrm{NN}}.
\]

若电子态作局部规范变换

\[
|\Phi_a\rangle\mapsto e^{i\vartheta(\mathbf R)}|\Phi_a\rangle,
\qquad
\chi_a\mapsto e^{-i\vartheta(\mathbf R)}\chi_a,
\]

则

\[
\mathbf A_a^I\mapsto
\mathbf A_a^I-\nabla_I\vartheta,
\]

而 \((-i\nabla_I-\mathbf A_a^I)\chi_a\) 按同一相位协变。\(\Phi_a^{\mathrm{BH}}\) 对该相位变换不变。若电子基在所取子空间中完备，还可写成

\[
\Phi_a^{\mathrm{BH}}
=\sum_{I,b\ne a}\frac{|\mathbf d_{ba}^{I}|^2}{2M_I},
\]

从而看出它一般不因令 \(\mathbf d_{aa}^{I}=0\) 而消失。

在局部、无简并且可选平行输运规范的区域，可以令 \(\mathbf d_{aa}^{I}=0\)，即 \(\mathbf A_a^I=0\)。若再作一个独立近似，忽略 \(\Phi_a^{\mathrm{BH}}\)，才得到

\[
\left[
-\sum_I\frac{\nabla_I^2}{2M_I}
+U_a(\mathbf R)
\right]\chi_a
\approx E\chi_a.
\]

因此，“忽略非对角面间耦合”“选择局部平行输运规范”和“忽略对角 Born–Huang 修正”是三个不同操作。局部规范不能无条件消除全局 Berry 相位或非平凡曲率；若存在简并电子子空间，Berry 连接和有效核方程应采用矩阵值形式，不能强行化成单态标量方程。

### D-C01.4 能隙与导数耦合的关系

对非简并电子态，微分本征方程：

\[
(\nabla_I\hat H_{\mathrm e})|\Phi_b\rangle
+\hat H_{\mathrm e}|\nabla_I\Phi_b\rangle
=(\nabla_I E_b)|\Phi_b\rangle
+E_b|\nabla_I\Phi_b\rangle.
\]

左乘 \(\langle\Phi_a|\)，取 \(a\ne b\)，利用正交性得到

\[
\langle\Phi_a|\nabla_I\Phi_b\rangle
=\frac{\langle\Phi_a|\nabla_I\hat H_{\mathrm e}|\Phi_b\rangle}
{E_b-E_a}.
\]

因此，若分子保持有界而能隙 \(|E_b-E_a|\) 变小，导数耦合可以变大。该式要求非简并、可微本征态和足够规则的算符族；在严格简并点不能直接除以零。

### D-C01.5 D-C01 验收边界

D-C01 通过需要同时满足：

- 明确完整 Hamiltonian 与固定核电子 Hamiltonian 的差；
- 区分 \(E_a^{\mathrm e}\)、\(E_{\mathrm{NN}}\) 和势能面 \(U_a\)；
- 从乘积求导显式产生 \(\mathbf d_{ab}^{I}\) 与 \(\tau_{ab}^{I}\)；
- 区分非对角面间耦合、对角 Berry 连接、Born–Huang 修正和进一步的最简方程近似；
- 说明局部平行输运规范不等于全局消除 Berry 几何，简并子空间需要矩阵值处理；
- 不把质量比较写成普适定量误差界；
- 说明近简并、避免交叉、激发态或显著非绝热动力学会破坏单面近似；
- 不在 M5 选择真实材料、DFT 后端或核运动软件。

## D-C02 Slater determinant、密度与一体密度矩阵

### D-C02.1 determinant 的反对称性

给定 \(N\) 个自旋轨道，定义矩阵 \(M_{ip}=\chi_p(x_i)\)。多体态

\[
\Phi(x_1,\ldots,x_N)=\frac1{\sqrt{N!}}\det M.
\]

交换电子 \(i\) 和 \(j\) 等于交换 \(M\) 的两行。determinant 在两行交换下变号，因此

\[
P_{ij}\Phi=-\Phi.
\]

若两条占据轨道相同，\(M\) 有两列相同，\(\det M=0\)。这给出 Pauli 禁止相同自旋轨道重复占据的 determinant 版本。

### D-C02.2 determinant 的归一化

展开两个 determinant 后，

\[
\langle\Phi|\Phi\rangle
=\frac1{N!}\sum_{P,Q}
(-1)^{P+Q}
\prod_{i=1}^{N}
\langle\chi_{P(i)}|\chi_{Q(i)}\rangle.
\]

若轨道正交归一，乘积仅在 \(P=Q\) 时非零。共有 \(N!\) 个这样的项，所以

\[
\langle\Phi|\Phi\rangle=\frac{N!}{N!}=1.
\]

若轨道非正交，归一化由占据轨道 Gram determinant 决定，不能继续使用上述正交简化而不作修正。

### D-C02.3 occupied-unitary 不变性

把占据轨道列向量记为 \(X=(\chi_1,\ldots,\chi_N)\)，令 \(\widetilde X=XU\)。对每组电子坐标，相应 Slater 矩阵满足 \(\widetilde M=MU\)，故

\[
\det\widetilde M=\det M\det U.
\]

若 \(U\) unitary，则 \(|\det U|=1\)。因此新旧多体态仅差整体相位。若变换混入未占据空间但仍保持相同占据投影，则应把它理解为同一子空间的另一组基；若改变占据子空间，物理 determinant 一般改变。

### D-C02.4 一体算符与 1RDM

定义

\[
\gamma(x,x')
=N\int \Psi(x,x_2,\ldots,x_N)
\Psi^*(x',x_2,\ldots,x_N),dx_2\cdots dx_N.
\]

对任意一体算符 \(\hat A=\sum_i\hat a(i)\)，其期望值为

\[
\langle\Psi|\hat A|\Psi\rangle
=\int a(x',x)\gamma(x,x'),dx,dx'
=\operatorname{Tr}(a\gamma).
\]

因此 1RDM 足以计算所有一体算符期望值，但一般不足以计算任意二体相互作用；后者需要二体约化密度矩阵。

### D-C02.5 trace、Hermiticity 与正性

令 \(x'=x\) 并积分：

\[
\operatorname{Tr}\gamma
=N\int |\Psi(x,x_2,\ldots,x_N)|^2,dx,dx_2\cdots dx_N=N.
\]

交换 \(x\) 和 \(x'\) 并取复共轭得到 \(\gamma(x,x')=\gamma^*(x',x)\)。对任意 \(f\)，

\[
\begin{aligned}
\langle f|\gamma|f\rangle
&=N\int dx_2\cdots dx_N \\\
&\quad\times
\left|
\int f^*(x)\Psi(x,x_2,\ldots,x_N),dx
\right|^2
\ge0.
\end{aligned}
\]

因此 \(\gamma\) Hermitian、半正定且 trace 为 \(N\)。

### D-C02.6 单 determinant 的 1RDM

对正交占据轨道 determinant，

\[
\gamma_\Phi=\sum_{p=1}^{N}|\chi_p\rangle\langle\chi_p|.
\]

于是

\[
\gamma_\Phi^2
=\sum_{pq}|\chi_p\rangle
\langle\chi_p|\chi_q\rangle
\langle\chi_q|
=\gamma_\Phi,
\qquad
\operatorname{Tr}\gamma_\Phi=N.
\]

该幂等式采用自旋轨道占据数 0/1 的约定。若以空间轨道闭壳层矩阵 \(P=2\sum_i|\phi_i\rangle\langle\phi_i|\) 表示，则 \(P^2=2P\)，不是 \(P^2=P\)。

### D-C02.7 相关态的非幂等反例

取两个正交空间轨道 \(a,b\)，构造归一化双 determinant 教学态

\[
|\Psi\rangle
=\frac1{\sqrt2}
(|a\alpha,a\beta\rangle
+|b\alpha,b\beta\rangle).
\]

其四个自旋轨道 \(a\alpha,a\beta,b\alpha,b\beta\) 的自然占据数均为 \(1/2\)，总和为 2。因此

\[
\operatorname{spec}(\gamma)
=\left(\frac12,\frac12,\frac12,\frac12\right),
\qquad
\operatorname{spec}(\gamma^2)
=\left(\frac14,\frac14,\frac14,\frac14\right).
\]

故纯态也可以有非幂等 1RDM。非幂等不是“数值误差”的充分证据，也不能单独区分相关纯态与热系综。

### D-C02.8 HF 能量中的 Coulomb、交换与双计数

对单 determinant 和 \(\hat H_{\mathrm e}=\sum_i\hat h(i)+\sum_{i<j}r_{ij}^{-1}\)，有

\[
E=\sum_p h_{pp}
+\frac12\sum_{pq}(J_{pq}-K_{pq}).
\]

规范 Fock 方程给出

\[
\varepsilon_p=h_{pp}+\sum_q(J_{pq}-K_{pq}).
\]

故

\[
\sum_p\varepsilon_p
=\sum_p h_{pp}+\sum_{pq}(J_{pq}-K_{pq}),
\]

与总能量相比，双电子部分多了一倍：

\[
E_{\mathrm{HF}}
=\sum_p\varepsilon_p
-\frac12\sum_{pq}(J_{pq}-K_{pq}).
\]

这证明“本征值和不是总能量”来自成对相互作用进入每条有效一体方程的计数结构。

### D-C02.9 D-C02 验收边界

D-C02 通过需要同时满足：

- 反对称性由 determinant 行交换显式证明，归一化证明声明轨道正交条件；
- occupied-unitary 只产生 \(\det U\) 整体相位；
- 密度、1RDM、Hamiltonian 和多体态保持对象分离；
- trace、Hermiticity、正性与 determinant 幂等性逐项推出；
- 给出相关纯态非幂等反例，并区分自旋轨道和闭壳层空间轨道占据约定；
- HF 的 Coulomb、交换与本征值双计数有明确公式；
- 不把单 determinant、HF 或 KS 辅助 determinant 写成精确相互作用多体态。

## 推导包来源与证据状态

| 内容 | 来源 | 状态 |
|---|---|---|
| 全电子—核 Hamiltonian、固定核方程、导数耦合和近简并边界 | FND-07；FND-01 | `PRIMARY_EXPLICIT`，本文件统一符号后 `DIRECT_DERIVATION` |
| Hartree、Slater determinant、Coulomb/交换与 Fock 方程 | FND-08；FND-01 | `PRIMARY_EXPLICIT`，本文件补全归一化和双计数推导 |
| 1RDM trace、正性、幂等与反例 | 从定义和正交性逐步推出 | `DIRECT_DERIVATION`；反例为 `PEDAGOGICAL` |
| 与 KS/DeepH 的对象接口 | C-FND-03、DH-01 | `PRIMARY_EXPLICIT`，仅作范围连接 |
