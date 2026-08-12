# 阶段 C 解析推导包：DFT、SCF、表示与局域性

本索引把 D-C01—D-C08 组织为一条从固定核多电子问题到可审计局域 Hamiltonian 标签的推导链。各推导文件保留完整条件、失败边界、例题和练习入口；本文件只建立依赖、对象接口和统一验收，不用摘要替代原推导。

阶段 C 仍处于材料建设模式。真实材料、DFT 后端、赝势/全电子对象、基、投影软件、DeepH 版本和训练预算均保留到 M8；M9 外部动作还需明确授权。

## 1. 统一对象链

\[
\begin{aligned}
&\text{电子—核问题}
\xrightarrow{\mathrm{D\mbox{-}C01}}
\text{固定核多电子问题}\\
&\xrightarrow{\mathrm{D\mbox{-}C02}}
\text{反对称态、密度与 1RDM}\\
&\xrightarrow{\mathrm{D\mbox{-}C03}}
\text{密度变分与普适泛函}\\
&\xrightarrow{\mathrm{D\mbox{-}C04}}
\text{KS 有效单粒子方程}\\
&\xrightarrow{\mathrm{D\mbox{-}C05}}
\text{SCF 固定点与收敛状态}\\
&\xrightarrow{\mathrm{D\mbox{-}C06}}
\text{普通/广义矩阵本征问题}\\
&\xrightarrow{\mathrm{D\mbox{-}C07}}
\text{投影、重建与标签表示}\\
&\xrightarrow{\mathrm{D\mbox{-}C08}}
\text{局域块、截断与稀疏验证}.
\end{aligned}
\]

每个箭头都改变或约束对象。后一个箭头的数值精度不能消除前一个箭头的理论、表示或来源误差。

## 2. D-C01—D-C08 覆盖矩阵

| ID | 核心产物 | 强制条件 | 主要失败边界 | 推导文件 |
|---|---|---|---|---|
| D-C01 | 固定核电子 Hamiltonian 与单面 BO 方程 | 绝热基、质量比、规范协变导数 | 非绝热耦合、简并子空间、几何项不能静默删除 | [05_many_electron_mean_field.md](05_many_electron_mean_field.md) |
| D-C02 | determinant、密度、1RDM、HF 能量 | 反对称性、占据、自旋和归一化 | 平均场不等于消除关联；相关 1RDM 不幂等 | [05_many_electron_mean_field.md](05_many_electron_mean_field.md) |
| D-C03 | HK/Levy/Lieb 变分结构 | 固定 \(N,\hat T,\hat W\)、密度域、拓扑、纯态/系综 | 简并、可表示性、minimum/infimum、次梯度 | [06_kohn_sham_variation.md](06_kohn_sham_variation.md) |
| D-C04 | KS 能量泛函与轨道方程 | 原子单位、正交约束、占据、可微/次微分边界 | 精确形式不等于已知 \(E_{xc}\)；本征值和不等于总能 | [06_kohn_sham_variation.md](06_kohn_sham_variation.md) |
| D-C05 | \(F[n]=n\)、混合与 Jacobian | 明确残差、可微邻域、约束和停止条件 | 谱半径只给局部渐近结论；伪收敛与最大步数失败 | [07_scf_fixed_point.md](07_scf_fixed_point.md) |
| D-C06 | \(Hc=ESc\) | Galerkin 空间、Hermitian \(H\)、\(S\succ0\) | 平面波 \(S=I\) 有条件；非正交基不能删 overlap | [08_representation_and_label_error.md](08_representation_and_label_error.md) |
| D-C07 | 投影/重建、误差轴与标签身份 | 固定基、窗口、规范、源/目标维数和损失 | 等谱不等矩阵；非正交回投需双侧 \(S_B^{-1}\) | [08_representation_and_label_error.md](08_representation_and_label_error.md) |
| D-C08 | 近视性、密度矩阵衰减和稀疏截断 | 体系类别、温度、维数、边界、基与误差范数 | 金属/长程/基变换；短窗指数不能外推代数尾 | [10_nearsightedness_sparsity.md](10_nearsightedness_sparsity.md) |

## 3. 章节、例题与练习入口

| 推导 | 正文与例题 | 问题与参考解答 |
|---|---|---|
| D-C01—D-C02 | [第 5 章](../../03_textbook/chapters/05_many_electron_mean_field/) | [第 5 章练习](../../06_exercises/03-stageC/05_many_electron_mean_field/) |
| D-C03—D-C04 | [第 6 章](../../03_textbook/chapters/06_kohn_sham_dft/) | [第 6 章练习](../../06_exercises/03-stageC/06_kohn_sham_dft/) |
| D-C05 | [第 7 章](../../03_textbook/chapters/07_scf_algorithms/) | [第 7 章练习](../../06_exercises/03-stageC/07_scf_algorithms/) |
| D-C06—D-C07 | [第 8 章](../../03_textbook/chapters/08_basis_pseudopotential_errors/) | [第 8 章练习](../../06_exercises/03-stageC/08_basis_pseudopotential_errors/) |
| D-C08 | [第 10 章](../../03_textbook/chapters/10_nearsightedness_locality_sparsity/) | [第 10 章练习](../../06_exercises/03-stageC/10_nearsightedness_locality_sparsity/) |

## 4. 跨推导不变量

### 4.1 粒子数、对象域与单位

- D-C01—D-C04 默认固定电子数；势的加法常数自由度只在固定 \(N\) 问题中使用。
- D-C03 的密度域、纯态/系综和 \(v\)-/\(N\)-representability 必须随泛函保留。
- D-C04—D-C08 默认原子单位，若标签输出改变单位必须显式登记。

### 4.2 物理态与矩阵坐标

- 一致基变换必须同步变换 \(H,S,c\)；谱保持不等于矩阵元素保持。
- 非正交基的物理范数为 \(c^\dagger Sc\)，标准广义求解要求 \(S\succ0\)。
- 投影、规范、轨道排序、bra/ket 和 Fourier 约定属于标签身份。

### 4.3 误差层次

\[
e_{\mathrm{total}}
\leftarrow
(e_{\mathrm{theory}},
e_{\mathrm{core}},
e_{\mathrm{basis}},
e_k,
e_{\mathrm{SCF}},
e_{\mathrm{projection}},
e_{\mathrm{truncation}},
e_{\mathrm{ML}}).
\]

该记号只表示误差来源，不假定统计独立或可简单相消。每个轴应在其余条件固定时验证。

### 4.4 局部性与表示

- 近视性是局部响应陈述，密度矩阵衰减是核的陈述，\(H/S\) 稀疏是表示陈述。
- 稠密 unitary 或非正交正交化可保持物理谱却改变稀疏率。
- 图、标签和后处理 cutoff 控制不同对象，均需单独登记与扫描。

## 5. 来源等级与推导标签

阶段 C 采用三类证据标签：

- PRIMARY_EXPLICIT：来源直接给出的定理、定义、算法对象或方法条件；
- DIRECT_DERIVATION：从已声明定义和线性代数逐步推出的公式；
- PEDAGOGICAL：为验证机制构造的有限维、离散或合成模型。

来源边界由[阶段 C 工作包](../../08_audits/M5_stageC_work_package.md)和各章 sources.md 冻结。不得把 Levy/Lieb 写成 HK 1964 的直接推论，不得把 norm-conserving 条件推广为全部赝势形式，不得把 Prodan–Kohn 的近视性无条件等同于任意矩阵指数稀疏，也不得把现代软件接口从历史论文推断出来。

## 6. 可执行验证映射

| 推导 | 冻结验证 |
|---|---|
| D-C01—D-C04 | 章内解析例题、占据/能量/密度矩阵 Python 断言 |
| D-C05 | T-C01—T-C04：线性/非线性 SCF、双停止条件、确定性 JSON |
| D-C06—D-C07 | T-C05—T-C09：多层收敛、采样/基分离、广义谱、投影、schema 删除失败 |
| D-C08 | T-C10：指数/代数衰减、截断三指标、错误尾外推拒绝 |

正式阶段 C 代码包在 M5-08 建设。推导包只规定对象、输入、容差和失败语义，不把嵌入式例题冒充正式 CLI 完成。

## 7. 推导包验收

M5-07 通过需要：

- D-C01—D-C08 全部可从本索引定位到正文、例题、题目、答案和验证；
- 每项推导声明对象域、单位、索引/形状、近似条件和失效边界；
- HK/Levy/Lieb、KS、SCF、普通/广义谱、投影/重建和局域性之间无对象偷换；
- T-C01—T-C10 的公式和失败语义与工作包一致；
- 全部相对链接、严格 MathML 和控制字符检查通过；
- 独立子 agent 判定剩余及新增 BLOCKING 为 0。

## 8. M8/M9 边界

本索引不构成实践方案选择。M7-I 全量独立总审计通过后才准备 M8 决策冻结；M8 冻结后，在 M9 正式安装 DeepH、下载正式数据或开始复现实验前仍需明确执行授权。
