# 第 6 章练习参考解答

## Q6-01

固定电子数 \(N\) 时，

\[
\hat V[v+C]
=\sum_{i=1}^{N}[v(\mathbf r_i)+C]
=\hat V[v]+NC.
\]

因此

\[
\hat H[v+C]=\hat H[v]+NC.
\]

单位算符的常数倍不改变任何本征矢，只把每个 \(N\) 电子本征值平移 \(NC\)。由同一本征态计算的密度不变。若电子数改变，平移量也随扇区变为 \(N'C\)，不同粒子数能量差会受化学势/能量零点约定影响，所以“无影响”不能跨粒子数问题无条件使用。

在周期问题中，绝对势零点通常具有规范自由度，但输出矩阵元素和本征值会随选定零点整体移动。比较两个标签时必须登记共同的势/能量对齐约定，否则一个纯规范差可能被误判为模型误差。

## Q6-02

在两个允许的局域标量外势产生同一密度 \(n\) 的假设下，先排除共享基态。若非零 \(\Phi\) 同时是两势的基态，两条 Schrödinger 方程相减得到

\[
\left[\sum_i(v-v')(\mathbf r_i)\right]\Phi=(E-E')\Phi.
\]

在共同算符定义域、允许势类及 \(\Phi\) 几乎处处非零或相应唯一延拓条件下，括号内的一体函数和必须几乎处处为常数；逐一改变电子坐标推出 \(v-v'\) 几乎处处为常数。由于题设排除这一情形，非简并基态必不同，反证才可使用两条严格不等式

\[
E_0[v]
<E_0[v']+\int(v-v')n,
\]

\[
E_0[v']
<E_0[v]+\int(v'-v)n.
\]

需要的条件包括：固定同一 \(N\)、\(\hat T\)、\(\hat W\)、边界条件和 Hilbert 空间；\(v,v'\) 属于允许的局域势域；两边 trial state 都属于相应算符定义域；共同基态引理的几乎处处/唯一延拓条件成立；基态非简并；\(v-v'\) 不是常数。

简并纯态情形先使用两条非严格 Rayleigh–Ritz 不等式；相加时两边抵消，迫使两式均取等号，因此交叉 trial state 成为对方 Hamiltonian 的基态，再由共同基态步骤推出标量势等价类唯一。该结论不唯一选择简并子空间中的波函数。简并系综还必须声明共同能量基态集合及权重。自旋/流密度等多基本变量理论可能出现额外势非唯一性，不能从标量粒子密度命题直接外推。

## Q6-03

- pure-state \(N\)-representable：存在归一化反对称 \(N\) 电子纯态产生该密度；
- ensemble \(N\)-representable：存在允许混合态的 \(N\) 电子统计密度算符产生该密度；
- interacting \(v\)-representable：该密度是某个具有相互作用 \(\hat W\) 的允许外势问题的基态密度；
- noninteracting \(v\)-representable：该密度是某个局域一体势下辅助非相互作用体系的基态密度，必要时以系综实现。

在标准连续空间和有限动能条件下，pure-state 与 ensemble \(N\)-representable 的密度集合可同为 \(\mathcal I_N\)，但搜索的状态类不同，pure/ensemble constrained-search 泛函值和凸性仍不能混同。题中推理不成立：非负和归一化只是必要条件的一部分，有限动能还要求如 \(\sqrt n\in H^1\) 的正则性。即使密度是 \(N\)-representable，也不能由此推出它是某个局域非相互作用势的基态密度；即使 noninteracting \(v\)-representable，也可能需要简并系综或分数占据，不能保证单 determinant 整数占据表示。

## Q6-04

Levy 纯态 constrained-search 泛函为

\[
F_{\mathrm{LL}}^{\mathrm{pure}}[n]
=\min_{\Psi\mapsto n}
\langle\Psi|\hat T+\hat W|\Psi\rangle,
\]

搜索域是归一化反对称、有限内部能量的纯态。Lieb 对偶泛函为

\[
F_{\mathrm L}[n]
=\sup_v\left\{E_0[v]-\int vn\right\},
\]

其中

\[
X=L^1\cap L^3,\qquad
\|n\|_X=\|n\|_1+\|n\|_3,\qquad
X^*=L^\infty+L^{3/2},
\]

并在 \(X\) 的范数拓扑中讨论下半连续性；不可接受密度上的泛函值扩展为 \(+\infty\)。固定 \(N\) 时势使用 \(X^*/\mathbb R\) 的等价类，或先固定势零点。

本章采用的标准三维 Coulomb 密度域及有限内部能量状态类满足 Lieb 的存在性结果，因此固定密度的内层下确界达到，写为 `min`；最小化态仍可不唯一。对密度的外层搜索写为 `inf`，其是否达到取决于给定外势 Hamiltonian 是否存在基态。若离开标准函数空间或改变相互作用、算符条件，内层可达性必须重新证明。

对两个系综可行解 \(\Gamma_1\mapsto n_1\)、\(\Gamma_2\mapsto n_2\)，混合态

\[
\Gamma_\lambda=\lambda\Gamma_1+(1-\lambda)\Gamma_2
\]

产生 \(n_\lambda=\lambda n_1+(1-\lambda)n_2\)，且内部能量线性。因此直接由各自最小化态或趋近序列得到

\[
F_{\mathrm{ens}}[n_\lambda]
\le\lambda F_{\mathrm{ens}}[n_1]+(1-\lambda)F_{\mathrm{ens}}[n_2].
\]

在本章声明的标准三维 Coulomb 条件、固定 \(N\)、共同扩展值约定和 \(X\) 范数拓扑下，精确关系为

\[
F_{\mathrm L}
=F_{\mathrm{ens}}
=\operatorname{cl}_{\|\cdot\|_X}
\operatorname{conv}F_{\mathrm{LL}}^{\mathrm{pure}}.
\]

\(F_{\mathrm{ens}}\) 搜索归一化、有限内部能量的反对称 \(N\) 电子统计密度算符；\(\operatorname{conv}\) 是凸包，\(\operatorname{cl}_{\|\cdot\|_X}\) 是 \(X\) 范数拓扑中的下半连续闭包。pure/ensemble \(N\)-representable 的密度域可以相同，但 \(F_{\mathrm{LL}}^{\mathrm{pure}}\) 不能与其凸闭包逐点无条件混同。

来源分工如下：HK 1964 支持基态密度—外势唯一性和基态变分结构，但不提供精确泛函闭式；Levy 1979 支持 pure-state \(N\)-representable 密度上的 constrained minimum，但不自动给出系综凸闭包；Lieb 1983 在指定 Coulomb 函数空间内提供内层可达性、凸、下半连续和势—密度对偶，但不能被简化为“任意非负归一化函数都是纯态基态密度”。

## Q6-05

Hartree 能为

\[
E_H[n]=\frac12\iint\frac{n(\mathbf r)n(\mathbf r')}{|\mathbf r-\mathbf r'|}
\,d\mathbf r\,d\mathbf r'.
\]

对密度作一阶变化并交换两个积分哑变量，得到

\[
v_H(\mathbf r)=\frac{\delta E_H}{\delta n(\mathbf r)}
=\int\frac{n(\mathbf r')}{|\mathbf r-\mathbf r'|}\,d\mathbf r'.
\]

对整数占据轨道施加

\[
\langle\phi_i|\phi_j\rangle=\delta_{ij}
\]

并构造

\[
\mathcal L=E-\sum_{ij}\Lambda_{ij}
(\langle\phi_i|\phi_j\rangle-\delta_{ij}).
\]

若 \(E_{xc}\) 在所考虑密度方向上可微，令

\[
v_{xc}=\frac{\delta E_{xc}}{\delta n}.
\]

对 \(\phi_i^*\) 变分得到

\[
\left[-\frac12\nabla^2+v_{\mathrm{ext}}+v_H+v_{xc}\right]\phi_i
=\sum_j\Lambda_{ji}\phi_j.
\]

\(\Lambda\) 是 Hermitian 矩阵，可在占据子空间内作 unitary 对角化。该变换不改变密度或 \(T_s\)，于是可选规范轨道满足

\[
\hat h_{\mathrm{KS}}\phi_i=\varepsilon_i\phi_i.
\]

若 \(E_{xc}\) 只存在次梯度、在整数粒子数处发生导数不连续，或近似泛函产生非局域算符，就不能无条件把 \(v_{xc}\) 写成处处存在的普通局域乘法函数；应使用系综、次微分或 generalized KS 等相应框架。

## Q6-06

一个电子时没有电子—电子相互作用，故在适当密度表示域上

\[
F[n]=T[n]=T_s[n].
\]

由定义

\[
E_{xc}=F-T_s-E_H
\]

得到

\[
E_{xc}[n]=-E_H[n].
\]

固定 \(\int n=1\) 后，只允许 \(\int\delta n=0\) 的变化。若两个泛函在该约束流形上可微，则只能推出

\[
v_{xc}(\mathbf r)=-v_H(\mathbf r)+C,
\]

其中 \(C\) 是势零点自由度；选定相同规范后可令 \(C=0\)。所以 KS 有效势中的单电子 Hartree 自排斥在物理上被精确抵消，剩余常数只平移本征值。该结论是精确泛函约束；常见近似泛函可能不能精确满足。它也不适用于一般多电子体系，因为真实交换、相关和相互作用动能修正不能整体简化为 \(-E_H\)。

## Q6-07

局域 KS 的重建公式为

\[
E=\sum_i f_i\varepsilon_i-E_H+E_{xc}-\int v_{xc}n.
\]

代入数据：

\[
E=-8.40-1.35-0.72+1.05=-9.42.
\]

若错误报告本征值和，定义有符号误差为“错误值减正确值”，则

\[
\Delta E=(-8.40)-(-9.42)=+1.02.
\]

generalized KS 可能包含非局域交换相关算符；其本征值和中相应算符期望值与能量泛函项的双计数关系不同。有限温度还会区分自由能、内能和熵修正量，因此不能不经重推就沿用上述局域零温公式。

## Q6-08

Fermi–Dirac 占据为

\[
f_i=\frac1{1+\exp[(\varepsilon_i-\mu)/\tau]}.
\]

代入 \(\tau=0.1\)：

\[
f_1=\frac1{1+e^{-2}}\approx0.880797,
\qquad
f_2=\frac1{1+e^{2}}\approx0.119203.
\]

二者之和为 1。可执行复算为：

```python
import numpy as np

eps = np.array([-0.2, 0.2])
tau = 0.1
occ = 1.0 / (1.0 + np.exp(eps / tau))
assert np.allclose(occ, [0.8807970779778823, 0.11920292202211755])
assert np.isclose(occ.sum(), 1.0)
```

至少应登记：占据函数名称；宽化参数及单位；是否解释为物理电子温度；系综与化学势/电子数约束；是否包含熵项；SCF 最小化的是能量还是自由能；最终报告自由能、内能还是零温外推量；简并态的占据分配规则。零温简并系综可有分数占据而没有物理有限温度，数值 smearing 也不能仅凭参数值被解释为 Mermin 温度。

## Q6-09

以下是一个后端无关的合成语义摘要。它不是正式 DFT 标签；所有会构成实践选择的字段保持 `UNRESOLVED_M8`。四个哈希分别对应固定字节串 `stageC synthetic input v1\n`、`stageC synthetic output v1\n`、`synthetic two-site structure v1\n` 和 `synthetic basis definition v1\n`，因而是可复算的真实 SHA-256，而非虚构材料制品哈希。

```json
{
  "schema_version": "stageC-label-v1",
  "generation_status": "SYNTHETIC_M5",
  "backend": {
    "name": "UNRESOLVED_M8",
    "version": "UNRESOLVED_M8",
    "commit": "UNRESOLVED_M8"
  },
  "artifacts": {
    "inputs": [{
      "uri_or_path": "inline:stageC synthetic input v1\\n",
      "sha256": "b93849b78dafc6ddc91074fd4e0b92dd49b979783a20241cdbc0398521c569dc"
    }],
    "outputs": [{
      "uri_or_path": "inline:stageC synthetic output v1\\n",
      "sha256": "84105046a23147a82270c9fd8ee28d8935abcfbc2bbef9f1edb06daa48f2b5b6"
    }]
  },
  "structure": {
    "id": "SYNTHETIC_TWO_SITE_V1",
    "sha256": "443a72c148b0728ea175d5aeedacf1e2b430a6fbd824b012afda8b2e31b06f3d",
    "lattice": "SYNTHETIC",
    "species": ["X", "X"],
    "positions": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
    "boundary_conditions": "SYNTHETIC_FINITE_MODEL"
  },
  "theory": {
    "electronic_structure_level": "SYNTHETIC_KS_ALGEBRA",
    "xc": "UNRESOLVED_M8",
    "all_electron_or_pseudopotential": "UNRESOLVED_M8",
    "potential_dataset": {
      "id": "UNRESOLVED_M8",
      "sha256": "UNRESOLVED_M8"
    },
    "relativistic_treatment": "UNRESOLVED_M8"
  },
  "basis": {
    "type": "SYNTHETIC_FINITE_MODEL",
    "definition": "synthetic basis definition v1",
    "cutoff_or_grid": "NOT_APPLICABLE_SYNTHETIC",
    "id": "SYNTHETIC_BASIS_V1",
    "sha256": "649df27a758c676f0f8bdd26e2d6f169cd930b9df393faf1fcb63c1ac8b310ff"
  },
  "spin": {
    "polarization": "UNRESOLVED_M8",
    "noncollinear": "UNRESOLVED_M8",
    "soc": "UNRESOLVED_M8"
  },
  "sampling": {
    "kind": "SYNTHETIC_SINGLE_POINT",
    "k_mesh": [1, 1, 1],
    "k_shift": [0.0, 0.0, 0.0],
    "k_weights": [1.0]
  },
  "occupation": {
    "electron_count": 1,
    "smearing_method": "SYNTHETIC_FIXED_OCCUPATION",
    "temperature": "NOT_PHYSICAL_SYNTHETIC",
    "reported_energy_functional": "SYNTHETIC_KS_IDENTITY"
  },
  "convergence": {
    "scf_residual_definition": "NOT_RUN_CHAPTER6_ALGEBRA",
    "scf_residual_tolerance": "NOT_RUN_CHAPTER6_ALGEBRA",
    "energy_tolerance": "NOT_RUN_CHAPTER6_ALGEBRA",
    "eigensolver_tolerance": "1e-12_2NORM",
    "max_iterations": 0,
    "achieved_metrics": {"algebraic_assertions": "PASS"}
  },
  "representation": {
    "output_object": "SYNTHETIC_2X2_HAMILTONIAN",
    "units": "HARTREE_SYNTHETIC",
    "orbital_ordering": ["site_1", "site_2"],
    "atom_orbital_index_map": {"0": [0], "1": [1]},
    "lattice_displacement_direction": "NOT_APPLICABLE_FINITE",
    "bra_ket_order": "row_bra_column_ket",
    "fourier_forward": "NOT_APPLICABLE_FINITE",
    "fourier_inverse": "NOT_APPLICABLE_FINITE",
    "phase_or_gauge": "REAL_SITE_BASIS",
    "overlap_treatment": "ORTHONORMAL_SYNTHETIC"
  },
  "projection": {
    "method": "IDENTITY_SYNTHETIC",
    "window": "FULL_2D_SPACE",
    "source_dimension": 2,
    "target_dimension": 2,
    "loss_metric": "FROBENIUS_NORM",
    "loss_value": 0.0,
    "band_validation": "EXACT_SYNTHETIC",
    "matrix_validation": "EXACT_SYNTHETIC"
  },
  "validation": {
    "commands": ["chapter6 embedded assertions"],
    "environment": {
      "python": "3.12.13",
      "numpy": "2.3.5",
      "scipy": "1.18.0"
    },
    "seed": 0,
    "audit_status": "PEDAGOGICAL_EXAMPLE_NOT_FORMAL_LABEL"
  }
}
```

误差分类如下：xc 近似误差属于理论近似层；\(k\)-点积分误差属于采样/离散层；SCF 未收敛属于数值求解层；投影到局域基的重建误差属于表示转换层；DeepH 预测矩阵误差属于固定标签语义之上的统计学习层。后层误差变小不能证明前层误差已经消失。

## Q6-10

完整对象链可写为

\[
(N,\hat T,\hat W,v_{\mathrm{ext}},\text{边界})
\to E_v[n]
\to n_*
\to h_{\mathrm{KS}}[n_*]
\to (H,S,\text{约定})
\to \text{label artifact}
\to \widehat H_{\mathrm{DeepH}}.
\]

- 第一条箭头要求固定问题族和声明过的密度域；HK、Levy、Lieb 的条件不能省略。
- \(E_v[n]\to n_*\) 是受粒子数约束的变分问题；实践中还依赖近似 \(E_{xc}\) 和收敛算法。
- \(n_*\to h_{\mathrm{KS}}[n_*]\) 要求 \(T_s\) 表示、Hartree/xc 势和自旋/温度口径明确；完整对象是自洽固定点。
- 算符到 \(H,S\) 依赖基、排序、归一化、相位、胞位移和 Fourier 约定；非正交基还需要 overlap。
- 矩阵到 label artifact 依赖制品哈希、单位、投影/重建质量、结构身份和验证血缘。
- label 到 DeepH 输出只定义固定语义下的监督学习误差，不修复上游理论和数值误差。

M7-I 必须在 M7 完成后，由新建的独立子 agent 使用 `gpt-5.6-sol`、`max` 推理强度审计 M3—M7 的全部已完成教材、推导、题解、代码、测试、来源和授权边界。主 agent 修复，总审计 agent 定点复核；新增及剩余问题均为 0 后才通过。

M8 集中冻结计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算以及高级物理范围。M8 前禁止安装 DeepH 本体、下载正式训练数据、生成正式 DFT 标签或隐含选择材料、后端和实践软件版本。M8 方案冻结后，在 M9 开始正式安装、数据下载或复现实验前，仍需取得用户的明确执行授权。

## 错误诊断汇总

- 把势唯一性写成绝对势零点唯一：回到 Q6-01；
- 把非简并反证复制到任意简并体系：回到 Q6-02；
- 把非负归一化等同于单 determinant KS 可表示：回到 Q6-03；
- 把 HK、Levy、Lieb 合并为一个来源：回到 Q6-04；
- 把普通 \(v_{xc}\) 当作无条件存在：回到 Q6-05；
- 把单电子精确抵消外推到任意体系或近似：回到 Q6-06；
- 把本征值和当总能量：执行 Q6-07；
- 把 smearing 参数直接当物理温度：执行 Q6-08；
- 用模型误差掩盖标签上游误差：按 Q6-09 分层；
- 在 M8/M9 授权前隐含选择实践对象：按 Q6-10 停止外部动作。
