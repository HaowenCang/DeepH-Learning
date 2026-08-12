# 第 6 章资料包：Kohn–Sham DFT

## 核心来源

| ID | 固定范围 | 用途 | 证据边界 |
|---|---|---|---|
| C-FND-02 | [Hohenberg–Kohn 1964](https://doi.org/10.1103/PhysRev.136.B864)，B864—B871，尤其 theorem I/II | 基态密度、普适泛函和变分原理 | 不提供可直接计算的精确 \(F[n]\) 或 KS 轨道；原始论证明确采用非简并主线 |
| C-FND-03 | [Kohn–Sham 1965](https://doi.org/10.1103/PhysRev.140.A1133)，A1133—A1138，尤其 Eqs. (1)—(7) | 非相互作用参考、\(T_s\)、Hartree/xc 分解与自洽方程 | 不把全部 KS 本征值解释为精确激发能 |
| C-FND-04 | [Mermin 1965](https://doi.org/10.1103/PhysRev.137.A1441)，A1441—A1443 | 有限温度密度泛函接口 | 数值 smearing 与物理温度必须区分 |
| C-FND-05 | [Levy 1979](https://doi.org/10.1073/pnas.76.12.6062)，6062—6065，尤其 Eqs. (7)—(10) | 在产生给定纯态 \(N\)-representable 密度的反对称波函数上定义 constrained minimum | 不是 HK 1964 的逐式代数推论；不自动支持系综凸扩展、闭包或处处可微性 |
| C-FND-06 | [Lieb 1983](https://doi.org/10.1002/qua.560240302)，243—277，尤其 Secs. 2—4 | Coulomb 体系密度域、内层 minimum 的存在性、\(F_{\mathrm L}=F_{\mathrm{ens}}=\operatorname{cl}_X\operatorname{conv}F_{\mathrm{LL}}^{\mathrm{pure}}\)、变分与 Legendre–Fenchel 对偶 | 使用时须声明 \(X=L^1\cap L^3\) 的拓扑、对偶势空间、共同扩展约定、纯态/系综和内/外层 minimum/infimum |
| C-FND-07 | [Capelle–Ullrich–Vignale 2007](https://doi.org/10.1103/PhysRevA.76.012508)，012508-1—5 | 简并基态、共同基态与多基本变量 DFT 中的势非唯一性边界 | 标量粒子密度的 HK 命题不得无条件外推到自旋/流密度等多变量理论 |
| FND-01 | Martin 2004，第 6—8 章第 119—170 页 | HK、KS、交换相关近似与自旋的教材主线 | 不支持具体后端默认泛函或参数 |
| DH-01 | 原始 DeepH 任务定义 | 标签继承固定 DFT 设置的理论层级 | 网络拟合不消除 xc 近似误差 |

## 来源—推导映射

HK、KS、Levy constrained search、Lieb 形式化与简并边界各自按原始来源标记为 `PRIMARY_EXPLICIT`。由共同基态方程、两层搜索重排、正交约束变分和基离散逐步得到的公式标记为 `DIRECT_DERIVATION`；有限维密度泛函例题标记为 `PEDAGOGICAL`。标准 Coulomb 域中固定密度的 Levy–Lieb 内层搜索写为 minimum；对密度的外层搜索保留 infimum，并单独声明外势基态存在性。不得把 Levy/Lieb 形式化写成 HK 1964 的直接代数推导，也不得在没有声明 \(X\)、\(X^*\) 和拓扑时使用“下半连续”。近似泛函名称只用于分类，不冻结 M8 实践选择。
