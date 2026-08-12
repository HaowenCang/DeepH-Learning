# 第 5 章 多电子问题与平均场

本章建立从电子—核多体问题到单粒子有效 Hamiltonian 的对象链。核心任务不是把所有近似归入“DFT 计算”这一宽泛标签，而是逐层回答：被求解的态属于哪个 Hilbert 空间，哪些自由度已被固定或积分掉，反对称性如何进入，多体态如何映射为密度和一体密度矩阵，以及 Hartree、Hartree–Fock、Kohn–Sham 与 DeepH 标签分别代表什么。

本章采用原子单位 \(\hbar=m_e=e=4\pi\varepsilon_0=1\)。除非另行声明，讨论限于非相对论、固定粒子数的电子问题；核自旋、量子电动力学修正和显式非绝热动力学不在本章范围内。Born–Oppenheimer（BO）材料依据 FND-01 与 FND-07，Hartree/Hartree–Fock（HF）材料依据 FND-01 与 FND-08。Kohn–Sham（KS）只作为第 6 章接口，不在本章提前宣称其交换相关泛函已知。

## 5.1 从电子—核问题到固定核电子问题

### 5.1.1 全 Hamiltonian 的对象与五类项

设电子坐标为 \(\mathbf r_i\)，核坐标为 \(\mathbf R_I\)，核质量和电荷数分别为 \(M_I\) 与 \(Z_I\)。忽略整体质心分离等技术细节时，非相对论 Coulomb Hamiltonian 可写为

\[
\hat H =
-\sum_I \frac{\nabla_I^2}{2M_I}
-\frac12\sum_i \nabla_i^2
+\sum_{I<J}\frac{Z_IZ_J}{|\mathbf R_I-\mathbf R_J|}
+\sum_{i<j}\frac{1}{|\mathbf r_i-\mathbf r_j|}
-\sum_{iI}\frac{Z_I}{|\mathbf r_i-\mathbf R_I|}.
\]

五项依次是核动能、电子动能、核—核排斥、电子—电子排斥和电子—核吸引。它作用于同时依赖所有电子和核坐标的总波函数

\[
\Psi=\Psi(\mathbf r_1,s_1,\ldots,\mathbf r_N,s_N;
\mathbf R_1,\ldots,\mathbf R_M),
\]

其中 \(s_i\) 是电子自旋变量。把一个结构文件中的 \(\mathbf R_I\) 当作固定数字，已经改变了问题：核坐标从量子变量变成了外部参数。这一改变不是“把同一个精确问题换一种写法”，而是固定核电子结构近似的入口。

### 5.1.2 固定核电子方程与能量常数

对给定核构型 \(\mathbf R=(\mathbf R_1,\ldots,\mathbf R_M)\)，定义

\[
\hat H_{\mathrm e}(\mathbf R)
=-\frac12\sum_i\nabla_i^2
+\sum_{i<j}\frac1{r_{ij}}
-\sum_{iI}\frac{Z_I}{|\mathbf r_i-\mathbf R_I|}.
\]

电子本征问题为

\[
\hat H_{\mathrm e}(\mathbf R)\Phi_a(\mathbf r;\mathbf R)
=E_a^{\mathrm e}(\mathbf R)\Phi_a(\mathbf r;\mathbf R).
\]

核—核排斥

\[
E_{\mathrm{NN}}(\mathbf R)
=\sum_{I<J}\frac{Z_IZ_J}{|\mathbf R_I-\mathbf R_J|}
\]

对固定 \(\mathbf R\) 是常数，因而不改变电子本征函数，但会改变给定构型的总势能面。必须区分仅含电子项的 \(E_a^{\mathrm e}\) 和

\[
U_a(\mathbf R)=E_a^{\mathrm e}(\mathbf R)+E_{\mathrm{NN}}(\mathbf R).
\]

若不同资料对“总能量”是否包含 \(E_{\mathrm{NN}}\) 采用不同约定，数值可以相差一个结构依赖量。标签语义因此必须登记所报告能量的组成。

### 5.1.3 BO 展开与被忽略的导数耦合

对每个 \(\mathbf R\) 取电子本征态 \({\Phi_a(\mathbf r;\mathbf R)}\)，总态可展开为

\[
\Psi(\mathbf r,\mathbf R)=\sum_a \chi_a(\mathbf R)\Phi_a(\mathbf r;\mathbf R).
\]

把该展开代回完整 Schrödinger 方程时，核动能不仅作用于 \(\chi_a\)，还作用于电子态对核坐标的参数依赖。会出现一阶和二阶导数耦合

\[
\mathbf d_{ab}^{I}(\mathbf R)
=\langle\Phi_a|\nabla_I\Phi_b\rangle_{\mathbf r},
\qquad
\tau_{ab}^{I}(\mathbf R)
=\langle\Phi_a|\nabla_I^2\Phi_b\rangle_{\mathbf r}.
\]

仅忽略与其他电子面 \(b\ne a\) 的非对角耦合，并不会自动删除 \(d_{aa}^{I}\) 和 \(\tau_{aa}^{I}\)。定义对角 Berry 连接与 Born–Huang 标量修正

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

在忽略非对角面间耦合后，规范协变的单面方程应写为

\[
\left[
\sum_I\frac{(-i\nabla_I-\mathbf A_a^I)^2}{2M_I}
+U_a(\mathbf R)
+\Phi_a^{\mathrm{BH}}(\mathbf R)
\right]\chi_a
=E\chi_a.
\]

在局部、无简并且可选择平行输运规范的区域，可以令 \(\mathbf d_{aa}^{I}=0\)，即 \(\mathbf A_a^I=0\)；若再单独忽略对角 Born–Huang 修正，才得到只含裸核动能与 \(U_a\) 的最简方程。局部规范选择不能无条件消除全局 Berry 相位或非平凡拓扑；简并电子子空间还需要矩阵值 Berry 连接，不能强行压缩为单条势能面。

单势能面 BO 近似的物理动机是核质量远大于电子质量，使核动能尺度通常较小；但质量比本身不构成无条件误差界。FND-07 明确展示了近简并或避免交叉附近的失效机制：当电子能隙变小时，电子态随 \(\mathbf R\) 的变化可以很快，导数耦合随之增大。

因此，以下陈述是不同强度的：

- “对固定核构型求解电子方程”是问题定义；
- “核与电子运动可近似分离”是带条件的 BO/绝热近似；
- “所有目标态上非绝热耦合都可忽略”需要额外证据，不能由核较重单独推出；
- “固定结构的电子标签是无近似精确值”是错误结论，因为电子相关、相对论处理、基组、采样和数值收敛等误差仍然存在。

## 5.2 多电子态、反对称性与 Slater determinant

### 5.2.1 多电子态的坐标层级

把空间和自旋合并为 \(x_i=(\mathbf r_i,s_i)\)。\(N\) 电子纯态是

\[
\Psi(x_1,\ldots,x_N),
\qquad
\int |\Psi|^2,dx_1\cdots dx_N=1.
\]

它不是 \(N\) 个互不相关单电子波函数的列表。电子—电子相互作用使坐标不可分离，而费米统计还要求任意两电子交换时

\[
\Psi(\ldots,x_i,\ldots,x_j,\ldots)
=-\Psi(\ldots,x_j,\ldots,x_i,\ldots).
\]

若两个电子被放入完全相同的自旋轨道，交换前后的函数相同，而反对称性又要求其相反，因此该态只能为零。这是 Pauli 排斥的波函数表述。

### 5.2.2 determinant 自动实现反对称性

给定 \(N\) 个正交归一自旋轨道 \(\chi_p(x)\)，Slater determinant 为

\[
\Phi(x_1,\ldots,x_N)
=\frac1{\sqrt{N!}}
\det[\chi_p(x_q)]_{q,p=1}^{N}.
\]

交换两个电子坐标等于交换 determinant 的两行，因此自动改变符号。若轨道正交归一，\(1/\sqrt{N!}\) 保证多体态归一化。若轨道线性相关，determinant 为零。

determinant 是一种特殊的反对称态，而不是所有反对称态。一般相关波函数需要多个 determinant 的线性组合，或采用其他等价的反对称表示。因此，“已经使用 determinant”只说明费米反对称性得到满足，不说明电子相关已经精确处理。

### 5.2.3 占据子空间比单条轨道更基本

对占据轨道作 unitary 混合

\[
\widetilde\chi_p=\sum_q \chi_q U_{qp},
\qquad U^\dagger U=I,
\]

新的 determinant 满足

\[
|\widetilde\Phi\rangle=\det(U)|\Phi\rangle.
\]

因为 \(|\det U|=1\)，两者仅差整体相位，表示同一纯态射线。由此可见，固定 determinant 的物理内容主要由占据子空间投影算符决定，而不是由子空间中某组规范轨道的单独名称决定。该事实将在后续标签表示和 gauge 约定中反复出现。

## 5.3 从多体态到密度和一体密度矩阵

### 5.3.1 一体密度是多体概率的边缘

自旋分辨一体密度定义为

\[
n(x)=N\int |\Psi(x,x_2,\ldots,x_N)|^2,dx_2\cdots dx_N.
\]

空间密度是对自旋求和：

\[
n(\mathbf r)=\sum_s n(\mathbf r,s),
\qquad
\int n(\mathbf r),d\mathbf r=N.
\]

前面的因子 \(N\) 确保积分得到电子数而不是 1。密度只保留同一点的概率信息，不直接保留不同点之间的相干性。

### 5.3.2 一体约化密度矩阵

一体约化密度矩阵（1RDM）定义为

\[
\gamma(x,x')
=N\int \Psi(x,x_2,\ldots,x_N)
\Psi^*(x',x_2,\ldots,x_N),dx_2\cdots dx_N.
\]

它满足

\[
\gamma(x,x')=\gamma^*(x',x),\qquad
\operatorname{Tr}\gamma=N,\qquad
n(x)=\gamma(x,x).
\]

对任意测试函数 \(f\)，有 \(\langle f|\gamma|f\rangle\ge0\)，因此 \(\gamma\) 是 Hermitian 半正定算符。对一般相互作用纯态，其自然占据数可以位于 0 与 1 之间，并不满足幂等性。

### 5.3.3 单 determinant 的幂等性边界

对由正交占据自旋轨道构成的单 determinant，

\[
\gamma_{\Phi}(x,x')=\sum_{p=1}^{N}\chi_p(x)\chi_p^*(x').
\]

于是

\[
\gamma_{\Phi}^2=\gamma_{\Phi}.
\]

幂等性来自“占据数只能为 0 或 1”的单 determinant 结构。相反，

- 一般相关纯态的 1RDM 通常非幂等；
- 有限温度或系综态的 1RDM 通常非幂等；
- 对空间轨道使用闭壳层占据 2 的约定时，矩阵本征值与幂等关系要相应改写；
- 有限非正交基中，幂等条件必须显式包含 overlap，不能把正交表示的 \(P^2=P\) 原样照搬。

### 5.3.4 四类对象不可互换

| 对象 | 典型自变量/索引 | 含义 | 不能由它自动推出什么 |
|---|---|---|---|
| 多体波函数 \(\Psi\) | \(N\) 组空间—自旋坐标 | 纯态振幅和全部相关信息 | 不等于单粒子矩阵 |
| 密度 \(n(\mathbf r)\) | 一个空间点 | 电子数的空间分布 | 不直接给出相干性或唯一轨道规范 |
| 1RDM \(\gamma(x,x')\) | 两个一体坐标 | 所有一体算符期望值 | 一般不唯一确定完整多体态 |
| 有效 Hamiltonian \(H_{\mu\nu}\) | 选定基、胞与轨道索引 | 某理论和状态下的一体算符表示 | 不等于 \(\gamma\)，也不等于精确多体 Hamiltonian |

这一表格是本章到 DeepH 的关键对象防错表。相同尺寸的矩阵也可能代表完全不同的算符和语义。

## 5.4 Hartree 与 Hartree–Fock 平均场

### 5.4.1 Hartree 乘积与自洽性

Hartree 近似采用可分离乘积

\[
\Psi_H(x_1,\ldots,x_N)=\prod_{i=1}^{N}\chi_i(x_i).
\]

该乘积一般不满足电子交换反对称性。对乘积态变分会得到每条轨道在其他轨道平均 Coulomb 场中运动的方程。以空间部分示意，

\[
\left[
\hat h
+\sum_{j\ne i}J_j(\mathbf r)
\right]\phi_i(\mathbf r)
=\varepsilon_i\phi_i(\mathbf r),
\]

其中

\[
J_j(\mathbf r)
=\int \frac{|\phi_j(\mathbf r')|^2}{|\mathbf r-\mathbf r'|},d\mathbf r'.
\]

势依赖未知轨道，而轨道又由该势决定，所以 Hartree 方程是自洽固定点问题。把最终一体本征值直接相加会重复计入成对相互作用；总能量必须使用相应能量泛函，或从本征值和中减去双计数项。

### 5.4.2 HF 变分空间与能量

HF 把变分空间限制为所有单 Slater determinant。记一体算符为 \(\hat h\)，双电子 Coulomb 与交换积分为

\[
J_{pq}=\iint
\frac{|\chi_p(x)|^2|\chi_q(x')|^2}{r_{12}},dx,dx',
\]

\[
K_{pq}=\iint
\frac{\chi_p^*(x)\chi_q^*(x')\chi_p(x')\chi_q(x)}
{r_{12}},dx,dx'.
\]

则 determinant 的能量为

\[
E_{\mathrm{HF}}
=\sum_p\langle p|\hat h|p\rangle
+\frac12\sum_{pq}(J_{pq}-K_{pq}).
\]

\(1/2\) 消除电子对 \((p,q)\) 与 \((q,p)\) 的重复计数。对 \(p=q\)，\(J_{pp}=K_{pp}\)，单 determinant 中同一自旋轨道的自相互作用在 HF 交换项中精确抵消。

在轨道正交约束下变分得到

\[
\hat f\chi_p=\sum_q\lambda_{qp}\chi_q,
\qquad
\hat f=\hat h+\sum_{q\in\mathrm{occ}}(\hat J_q-\hat K_q).
\]

对占据空间内的 Lagrange 乘子矩阵作 unitary 对角化后，可写成规范 HF 方程

\[
\hat f\chi_p=\varepsilon_p\chi_p.
\]

交换算符作用为

\[
(\hat K_q\chi_p)(x)
=\chi_q(x)\int\frac{\chi_q^*(x')\chi_p(x')}{r_{12}},dx',
\]

其在 \(x\) 处的值依赖 \(\chi_p\) 在所有 \(x'\) 处的值，因此是非局域算符。Hartree 的 Coulomb 势与 HF 的非局域交换不能仅凭都出现在“一体方程”中而混为同一对象。

### 5.4.3 交换、相关与“平均场”的边界

HF 精确实现单 determinant 内的交换反对称性，但把真实基态限制在 determinant 流形上。若定义 \(E_0^{\mathrm{NR,BO}}\) 为非相对论、固定核电子 Hamiltonian 的精确基态能量，并定义 \(E_{\mathrm{HF}}^{\mathrm{CBS}}\) 为同一 Hamiltonian 在完整一体基极限下的 HF 最小值，则相关能可定义为

\[
E_{\mathrm c}
=E_0^{\mathrm{NR,BO}}-E_{\mathrm{HF}}^{\mathrm{CBS}}\le0.
\]

这个定义的比较对象必须一致。有限基 HF 能量与有限基“精确”对角化之间的差、不同相对论层级之间的差、不同核构型之间的差都不能无条件称为上述相关能。交换也不是相关的同义词：HF 已含精确的 determinant 交换，但仍缺少超出单 determinant 的相关。

“平均场”在不同文献中可以宽泛指自洽有效一体方程，也可以狭义指 Hartree/HF 类近似。本项目在对象表中显式写出 Hartree、HF 或 KS，不用“平均场”替代具体理论层级。

## 5.5 KS 与 DeepH 的接口

### 5.5.1 KS determinant 是辅助构造

第 6 章将说明 KS 非相互作用参考体系的构造及其可表示性边界。在假定目标密度具有所需的非相互作用 \(v\)-representability、采用常规零温整数占据且不存在需要系综处理的简并时，可以用占据 KS 轨道构成的单 determinant 表示辅助体系，并使其密度匹配目标相互作用基态密度。若存在简并、分数占据或更一般的可表示性问题，应改用非相互作用系综和占据数来陈述密度匹配，不能无条件声称任意相互作用密度都由一个纯 KS determinant 表示。无论采用单 determinant 还是系综辅助表示，它都不是一般真实相互作用多体波函数。

HF 与 KS 都产生自洽一体方程，但来源不同：

| 层级 | 变分/构造对象 | 一体算符中的关键项 | 主要未解决部分 |
|---|---|---|---|
| Hartree | 可分离轨道乘积 | 局域 Coulomb 平均场 | 反对称交换与相关 |
| HF | 单 Slater determinant | Coulomb 加非局域精确交换 | 超出单 determinant 的相关 |
| KS | 在相应非相互作用可表示域中的密度与辅助非相互作用体系；整数占据时可为单 determinant，简并/分数占据时须允许系综 | Hartree 加 \(v_{xc}[n]\) | 精确 \(E_{xc}[n]\) 未知，实践需近似；可表示性和占据条件必须声明 |

### 5.5.2 从结构到 DeepH 标签的对象链

在固定材料体系、电子结构理论、数值离散和表示约定后，实际流程可抽象为

\[
\{Z_I,\mathbf R_I\}
\longrightarrow n
\longrightarrow v_{\mathrm{eff}}[n]
\longrightarrow \hat H_{\mathrm{KS}}[n]
\longrightarrow H_{i\alpha,j\beta}(\mathbf R).
\]

最后一个对象是选定局域轨道、胞位移、轨道排序、相位和单位下的 KS Hamiltonian 矩阵块。原始 DeepH 学习的是这一类一体有效 Hamiltonian 标签，而不是

- 全电子—核多体 Hamiltonian 的完整张量；
- 精确相互作用多体波函数；
- 一体密度矩阵本身；
- 与基、泛函、赝势、采样和收敛设置无关的“材料固有矩阵”。

网络预测可以替代新结构上重复执行标签生成流程的某些昂贵步骤，但不会自动消除标签所继承的 BO、交换相关、离散、投影和数值误差。

### 5.5.3 双计数与状态依赖

有效一体 Hamiltonian 往往依赖由其占据态产生的密度。因此，自洽方程的本征值和通常不等于总能量。Hartree、HF 和 KS 各有自己的双计数或能量泛函修正。只保存 \(H\) 而不登记占据、电子数、温度/smearing 和能量口径，无法唯一重建标签生成时所报告的总能量。

这也是 M5 标签语义模板要求同时记录理论、占据、收敛和表示字段的原因。

### 5.5.4 M8 前授权边界

本章及阶段 C 的全部波函数、轨道、矩阵、密度和收敛轨迹均为解析推导或合成教学对象。在准备进入 M8 前，继续禁止：

- 安装 DeepH 本体；
- 下载正式训练数据；
- 生成正式 DFT 标签；
- 显式或隐含选择首个材料体系、DFT/数据后端或实践软件版本。

当 M3—M7 的材料建设与独立门控全部完成、准备进入 M8 时，必须暂停自主推进，并集中提交计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算及高级物理范围的候选方案和推荐，等待用户冻结。即使 M8 方案已经冻结，在开始 M9 的正式安装、数据下载或复现实验前，仍须再次请求明确执行授权。

因此，本章出现的 Hubbard 模型、两能级避免交叉和有限轨道 determinant 只承担教学与验证功能，不构成对真实材料、泛函、赝势、后端或 DeepH 版本的预先选择。Q5-10 的端到端对象审计应连同本小节一起核对。

## 5.6 本章可验证结论

读完本章后，应能从材料本身定位并复核下列结论：

- 固定核电子问题删除或参数化了哪些项，\(E_{\mathrm{NN}}\) 是否计入能量；
- BO 近似中的一阶/二阶导数耦合从何而来，近简并为何削弱绝热分离；
- Slater determinant 如何保证反对称性，以及 occupied-unitary 变换为何只改变整体相位；
- 密度为何是 1RDM 的对角，单 determinant 的 1RDM 为何幂等，而一般相关态为何不必幂等；
- Hartree、HF、KS 的变分对象和有效算符为何不同；
- HF 本征值和为何包含双计数，交换为何不等于相关；
- DeepH 的 KS Hamiltonian 矩阵为何不是精确多体 Hamiltonian，也不是基组无关对象。

对应的完整推导见 `04_derivations/stageC/05_many_electron_mean_field.md`，数值与解析例题见 `examples.md`，练习和逐题参考解答见 `06_exercises/03-stageC/05_many_electron_mean_field/`。

## 本章检查题

1. 固定 \(\mathbf R\) 后，\(E_{\mathrm{NN}}\) 为何不改变电子本征函数，却仍影响势能面？
2. 仅凭 \(M_I\gg m_e\) 能否证明任意电子态上的 BO 误差都很小？还缺少什么条件？
3. occupied-unitary 混合为什么不改变单 determinant 的物理态？
4. \(n(\mathbf r)\)、\(\gamma(x,x')\) 和 \(H_{\mu\nu}\) 分别是什么对象？
5. 为什么 \(\gamma^2=\gamma\) 不是所有纯多电子态的普遍性质？
6. HF 中 \(J_{pp}-K_{pp}=0\) 说明什么，又不说明什么？
7. 为什么不能把 HF 或 KS 轨道本征值直接相加当作总能量？
8. 一个 DeepH 预测矩阵若未登记基、轨道排序和相位约定，为什么不能与另一个矩阵逐元素比较？

这些题的逐项答案与误区诊断包含在本章练习参考解答中；材料完备性审计检查答案是否存在、可定位且可验证，不要求学习者本人提交闭卷作答。
