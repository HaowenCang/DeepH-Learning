# 阶段 C 自学导航：DFT、SCF、标签语义与局域性

## 1. 使用方式与完成口径

阶段 C 把固定核多电子问题、密度泛函理论、Kohn–Sham 构造、自洽场算法、离散表示和局域截断连接为一条可审计对象链，并说明这些环节如何共同决定 DeepH Hamiltonian 标签的语义。依据材料建设模式，检查题、练习和综合题均保留参考解答与失败分析，但不要求学习者提交闭卷作答、口头解释或阶段自测。完成证据来自教材覆盖、解析推导、例题、练习与解答、可执行代码、强制失败样例和独立审计。

本阶段不安装或调用真实 DFT/DeepH 后端，不下载正式数据，不生成正式标签，也不选择材料、交换相关泛函、赝势、基、采样、投影软件或实践版本。相关字段在 M8 前保持 `UNRESOLVED_M8`；合成测试只能使用明确标记的教学白名单值。

## 2. 前置条件与建议顺序

前置知识为阶段 B 的有限基表示、Hermitian-definite 广义本征问题和周期实空间—倒空间对象链，以及基础多变量微积分和变分法。

| 单元 | 核心问题 | 教材与推导 | 例题、练习与验证 |
|---|---|---|---|
| C1 多电子对象 | 波函数、密度、1RDM、determinant、Hartree、HF 和 KS 为何不能互换？ | [第 5 章](05_many_electron_mean_field/chapter.md)；[D-C01/D-C02](../../04_derivations/stageC/05_many_electron_mean_field.md) | [例题](05_many_electron_mean_field/examples.md)；[问题](../../06_exercises/03-stageC/05_many_electron_mean_field/problem/readme.md)与[解答](../../06_exercises/03-stageC/05_many_electron_mean_field/solution/readme.md) |
| C2 DFT 与 KS | HK、Levy、Lieb 和 KS 的域、条件与结论分别是什么？ | [第 6 章](06_kohn_sham_dft/chapter.md)；[D-C03/D-C04](../../04_derivations/stageC/06_kohn_sham_variation.md) | [例题](06_kohn_sham_dft/examples.md)；[问题](../../06_exercises/03-stageC/06_kohn_sham_dft/problem/readme.md)与[解答](../../06_exercises/03-stageC/06_kohn_sham_dft/solution/readme.md) |
| C3 SCF | 混合、Jacobian、停止条件、约束和失败状态如何验证？ | [第 7 章](07_scf_algorithms/chapter.md)；[D-C05](../../04_derivations/stageC/07_scf_fixed_point.md) | [例题](07_scf_algorithms/examples.md)；[问题](../../06_exercises/03-stageC/07_scf_algorithms/problem/readme.md)与[解答](../../06_exercises/03-stageC/07_scf_algorithms/solution/readme.md)；T-C01—T-C04 |
| C4 表示与标签 | 理论、基/采样、SCF、投影和矩阵坐标误差如何分层？ | [第 8 章](08_basis_pseudopotential_errors/chapter.md)；[D-C06/D-C07](../../04_derivations/stageC/08_representation_and_label_error.md) | [例题](08_basis_pseudopotential_errors/examples.md)；[问题](../../06_exercises/03-stageC/08_basis_pseudopotential_errors/problem/readme.md)与[解答](../../06_exercises/03-stageC/08_basis_pseudopotential_errors/solution/readme.md)；T-C05—T-C09 |
| C5 局域与稀疏 | 密度响应、1RDM 衰减和矩阵块稀疏为何是不同陈述？ | [第 10 章](10_nearsightedness_locality_sparsity/chapter.md)；[D-C08](../../04_derivations/stageC/10_nearsightedness_sparsity.md) | [例题](10_nearsightedness_locality_sparsity/examples.md)；[问题](../../06_exercises/03-stageC/10_nearsightedness_locality_sparsity/problem/readme.md)与[解答](../../06_exercises/03-stageC/10_nearsightedness_locality_sparsity/solution/readme.md)；T-C10 |

每个单元应按“对象与条件—逐式推导—例题—练习—参考解答—自动测试—失败诊断”核对。查看参考解答不使材料门控失效，但最终数值必须能从公式、代码或冻结输入独立复算。

## 3. D-C01—D-C08 能力—材料—验证映射

| 推导 | 可验证能力 | 正例或验证 | 关键失败边界 |
|---|---|---|---|
| D-C01 | 从电子—核 Hamiltonian 到 BO 通道方程，识别导数耦合、Berry 连接和 Born–Huang 项 | Q5-01/Q5-02；C-C01 | 固定核不是“核动能恒为零”；局部规范不能删除全局几何相位 |
| D-C02 | 区分多体态、determinant、密度、1RDM、Hartree/HF/KS，推出占据旋转不变量 | Q5-03—Q5-10；C-C01 | 单 determinant 的幂等 1RDM 不能推广到一般相关态 |
| D-C03 | 区分 HK、Levy 纯态搜索、系综扩展与 Lieb 凸闭包 | Q6-01—Q6-04；C-C02 | 共同基态、简并、势加常数、minimum/infimum 和可表示性必须限定 |
| D-C04 | 从正交约束变分推出 KS 方程和总能量修正 | Q6-05—Q6-10；C-C03 | KS 本征值和不是总能量；精确形式不提供现成 \(E_{xc}\) |
| D-C05 | 把 SCF 写成受约束固定点，分析混合、Jacobian、谱半径和双停止判据 | T-C01—T-C04；C-C04/C-C05 | `max_iter` 不等于收敛；单判据和局部稳定都可能误判 |
| D-C06 | 从连续问题到 Galerkin 矩阵束，区分基、采样和占据语义 | T-C05/T-C06；C-C06 | 加密单一数值轴不能证明其他误差轴已收敛 |
| D-C07 | 推导投影/回投，区分谱、子空间与固定坐标矩阵 | T-C07—T-C09；C-C07/C-C08 | 忽略 \(S\)、不稳定求逆、等谱即同矩阵和弱 schema 均须失败 |
| D-C08 | 从衰减条件到距离/块截断，区分近视性、1RDM 与 \(H/S\) 稀疏 | T-C10；C-C09 | 指数短窗不能外推全部体系；表示变换可改变稀疏性 |

[推导总索引](../../04_derivations/stageC/README.md)冻结前提与来源等级；[标签语义模板](../stageC_label_semantics_template.md)冻结记录结构；[综合问题](../../06_exercises/03-stageC/comprehensive/problem/readme.md)与[参考解答](../../06_exercises/03-stageC/comprehensive/solution/readme.md)用于端到端复核。

## 4. T-C01—T-C10 可执行映射

| 测试 | 验证对象 | 强制失败 | 不能推出的结论 |
|---|---|---|---|
| T-C01 | 三维线性混合、速率与第 0 步边界 | \(\alpha=2\) 恰 12 次更新后残差增长 | 不代表真实 SCF 最优混合参数 |
| T-C02 | 非线性密度的残差、粒子数与正性 | \(\alpha=1\) 两周期 | 不代表真实密度只含两分量 |
| T-C03 | 密度残差与教学能量双判据 | 缩放伪能量使 energy-only 误通过 | 教学能量不是 DFT 总能量 |
| T-C04 | 混合扫描、终止原因和确定性 JSON | 20 步上限不得标记收敛 | 不测量真实墙钟成本 |
| T-C05 | 五层离散序列 | 局部假平台被参考误差拒绝 | 不校准真实 cutoff |
| T-C06 | \(k\) 采样轴与独立基偏置 | 采样差小但总误差仍大 | 不选择真实基或采样方案 |
| T-C07 | 合同变换后的广义谱与残差 | 忽略 \(S\) 的普通谱被拒绝 | 不规定实际 AO 顺序 |
| T-C08 | 投影、回投、丢失范数与等谱反例 | 固定坐标矩阵差大而谱相同 | 不选择实际投影软件或能窗 |
| T-C09 | 67 路径与 47 个对抗变异 | 任一缺失或变异被接受即失败 | schema 有效不证明标签物理正确 |
| T-C10 | 两类衰减和截断三指标 | 短窗指数拟合不能解释代数尾 | 不确定真实局域半径 |

固定环境和命令见[代码说明](../../05_code_exercises/stageC_teaching_scf/README.md)。两组 CLI 必须均报告 T-C01—T-C10 为 `pass`、所有 `expected_failure.detected=true`、`overall_pass=true`，相同参数的输出哈希完全一致。

## 5. 关键自学检查与答案定位

| 检查问题 | 答案定位 | 验证入口 |
|---|---|---|
| 为什么占据轨道可作 unitary 混合而 determinant/密度不变？ | 第 5 章 5.2—5.3；D-C02 | Q5-04/Q5-05 |
| 为什么 \(F_{\mathrm L}\) 不能写成任意密度上必取到的 minimum？ | 第 6 章 6.2.3—6.2.5；D-C03 | Q6-03/Q6-04 |
| 为什么 KS 本征值和含双计数？ | 第 6 章 6.3；D-C04 | Q6-07；C-C03 |
| 为什么 \(\rho(M_\alpha)<1\) 只是冻结点附近的局部结论？ | 第 7 章 7.3；D-C05 | Q7-03—Q7-06；T-C01 |
| 为什么 \(k\) 点收敛不能证明基组误差也小？ | 第 8 章 8.3、8.7；D-C06 | Q8-05/Q8-06；T-C05/T-C06 |
| 为什么等谱矩阵仍可能不是同一监督标签？ | 第 8 章 8.6；D-C07 | Q8-08；T-C08 |
| 为什么近视性不能推出任意基下 \(H\) 严格稀疏？ | 第 10 章 10.1—10.3；D-C08 | Q10-01—Q10-05；T-C10 |

## 6. 诊断顺序与常见误区

| 现象 | 优先检查 | 机制边界 | 验证 |
|---|---|---|---|
| KS/SCF 能量项重复或缺失 | 对象域、约束、Hartree 与 \(E_{xc}\) | 本征值和含已计入势贡献 | D-C04；Q6-05—Q6-07 |
| 达到步数上限但残差大 | `converged`、终止原因和双判据 | 上限退出不是收敛 | T-C02—T-C04 |
| 加密 \(k\) 网格后总误差不降 | 基/网格、赝势、SCF、投影 | 单轴收敛不删除其他偏差 | T-C05/T-C06 |
| 广义谱异常 | \(H/S\) 同步、\(S\succ0\)、单位与轨道顺序 | 忽略 overlap 改变问题本身 | T-C07 |
| 能带相同但矩阵 MAE 大 | 固定表示、规范、子空间 | 谱不含全部坐标信息 | T-C08 |
| 字段齐全仍不可用 | 类型、shape、内容哈希、占位状态和语义 | 存在性不证明物理正确 | T-C09 |
| 短距离拟合好但远程误差大 | 衰减族、拟合窗、体系条件 | 代数尾不能由短窗指数外推 | T-C10 |

诊断应依次确认对象与语义、前提和约定、结构不变量、数值残差、前向物理量，最后才讨论模型误差。

## 7. 阶段边界

M5-09 完成后仍须由新的独立子 agent 执行 M5-10 阶段 C 总审计。只有总审计明确 `BLOCKING=0` 并允许进入 M6，M5 才能完成。

M8 前继续禁止安装 DeepH、下载正式数据、生成正式 DFT 标签或隐含选择材料、后端和版本。M7-I 全量独立总审计通过后才集中冻结 M8；M8 冻结后，M9 的正式安装、下载或复现实验仍须取得明确执行授权。
