# 阶段 E 自学导航：群表示、等变 Hamiltonian 与时间反演接口

## 1. 使用方式与完成口径

阶段 E 把三维几何作用、群表示、实球谐与 Wigner 表示、Clebsch--Gordan 耦合、等变消息、Hamiltonian 轨道块、局部架以及自旋—时间反演接口连接为一条可审计对象链。材料建设模式不要求学习者提交闭卷作答、口头解释或逐阶段自测；阶段证据来自来源受控教材、D-E01—D-E09 解析推导、章节例题与题解、C-E01—C-E12 综合题解、T-E01—T-E12 自动验证、定向故障以及独立材料审计。

本阶段只使用合成旋转、合成周期图、合成轨道块和固定随机数流。它不安装 DeepH 或 e3nn，不下载正式数据，不生成 DFT 标签，也不选择材料体系、DFT/数据后端、DeepH 软件对象、实践版本、训练预算或高级物理范围；这些字段在 M8 前保持 `UNRESOLVED_M8`。

## 2. 前置条件与建议顺序

学习前应能使用阶段 B 的行晶格、周期逆边和广义本征对象，阶段 C 的 Hamiltonian 标签语义、表示误差与局域性边界，以及阶段 D 的完整边键、轨道 provenance、mask、批处理和普通 MPNN。阶段 E 不重新定义这些身份对象，只增加几何群作用与表示类型。

| 单元 | 核心问题 | 教材与冻结推导 | 例题、练习与验证 |
|---|---|---|---|
| E1 几何作用与实表示 | 主动/被动、复合顺序、极/轴向量和实 \(s,p,d\) 表如何统一？ | [第 15 章](15_geometric_transformations_equivariance/chapter.md)、[第 16 章](16_groups_representations/chapter.md)；[D-E01](../../04_derivations/stageE/15_group_actions_equivariance.md)、[D-E02](../../04_derivations/stageE/16_real_spd_representations.md) | [第 15 章例题](15_geometric_transformations_equivariance/examples.md)、[第 16 章例题](16_groups_representations/examples.md)及两章题解；T-E01—T-E03/T-E07；C-E01—C-E03 |
| E2 球谐与 Wigner 表示 | 点值、展开系数、复—实桥和相位规范如何区分？ | [第 17 章](17_spherical_harmonics_wigner/chapter.md)；[D-E03](../../04_derivations/stageE/17_spherical_harmonics_wigner.md) | [第 17 章例题](17_spherical_harmonics_wigner/examples.md)及题解；T-E04；C-E04 |
| E3 张量积与 CG | 允许哪些耦合路径，规范相位与合法通道相位自由如何区分？ | [第 18 章](18_tensor_products_clebsch_gordan/chapter.md)；[D-E04](../../04_derivations/stageE/18_tensor_products_clebsch_gordan.md) | [第 18 章例题](18_tensor_products_clebsch_gordan/examples.md)及题解；T-E05/T-E07/T-E08；C-E05/C-E08 |
| E4 图 Hamiltonian | 轨道块左右作用、逆边、消息层与局部架怎样保持身份和协变？ | [第 19 章](19_equivariant_graph_hamiltonian/chapter.md)；[D-E05—D-E07](../../04_derivations/stageE/19_equivariant_graph_hamiltonian.md) | [第 19 章例题](19_equivariant_graph_hamiltonian/examples.md)及题解；T-E06/T-E08/T-E09/T-E12；C-E06—C-E09 |
| E5 自旋、时间反演与成本 | 反幺正约束何时成立，数值阈值与计算预算怎样解释？ | [第 20 章](20_spin_time_reversal_complex/chapter.md)；[D-E08](../../04_derivations/stageE/20_spin_time_reversal_complex.md)、[D-E09 成本总表](../../04_derivations/stageE/README.md) | [第 20 章例题](20_spin_time_reversal_complex/examples.md)及题解；T-E10—T-E12；C-E10—C-E12 |

每个单元按“对象和定义域—表示约定—逐式推导—解析例题—代码正例—定向故障—综合题—参考解答”核对。数值相近不能替代 basis、component 顺序、群作用方向、edge identity、provenance、dtype、shape 与 tolerance 的一致性。

## 3. 能力到材料的正向矩阵

代码入口均位于[阶段 E 合成实现](../../05_code_exercises/stageE_synthetic_equivariance/stagee_models.py)和[验收驱动](../../05_code_exercises/stageE_synthetic_equivariance/run_experiments.py)。统一表示优先级见[阶段 E 表示约定](../stageE_representation_conventions.md)，逐字段记录使用[表示追踪模板](../stageE_representation_trace_template.md)。

| 能力 | 教材与推导 | 具体例题 | 代码与失败入口 | 章节练习/解答 | 综合题/解答 |
|---|---|---|---|---|---|
| C-E01 主动/被动与复合 | [第 15 章 15.2—15.4](15_geometric_transformations_equivariance/chapter.md)；[D-E01](../../04_derivations/stageE/15_group_actions_equivariance.md) | [例 15-1、15-8](15_geometric_transformations_equivariance/examples.md) | `axis_angle_rotation`、`validate_rotation`；T-E01/T-E02；错误转置/顺序/反射 | [Q15-02/Q15-09](../../06_exercises/05-stageE/15_geometric_equivariance/problem/readme.md)；[A15-02/A15-09](../../06_exercises/05-stageE/15_geometric_equivariance/solution/readme.md) | [C-E01](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E01](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E02 类型与宇称 | [第 15 章 15.5](15_geometric_transformations_equivariance/chapter.md)、[第 16 章 16.5](16_groups_representations/chapter.md)；[D-E01](../../04_derivations/stageE/15_group_actions_equivariance.md)、[D-E02](../../04_derivations/stageE/16_real_spd_representations.md)、[D-E04](../../04_derivations/stageE/18_tensor_products_clebsch_gordan.md)、[D-E06](../../04_derivations/stageE/19_equivariant_graph_hamiltonian.md) | [例 15-4](15_geometric_transformations_equivariance/examples.md)、[例 16-7](16_groups_representations/examples.md)、[例 18-9](18_tensor_products_clebsch_gordan/examples.md) | `test_t_e02/test_t_e07`（T-E02/T-E07）；polar/axial 与偶/伪标量门控故障 | [Q15-05](../../06_exercises/05-stageE/15_geometric_equivariance/problem/readme.md)、[Q16-07](../../06_exercises/05-stageE/16_groups_representations/problem/readme.md)；[A15-05](../../06_exercises/05-stageE/15_geometric_equivariance/solution/readme.md)、[A16-07](../../06_exercises/05-stageE/16_groups_representations/solution/readme.md) | [C-E02](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E02](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E03 实 \(s,p,d\) 表 | [第 16 章 16.3—16.4](16_groups_representations/chapter.md)；[D-E02](../../04_derivations/stageE/16_real_spd_representations.md) | [例 16-4、16-5、16-8](16_groups_representations/examples.md) | `_stf_basis`、`d_representation`；T-E03；错序/归一化/RBR 故障 | [Q16-04—Q16-06](../../06_exercises/05-stageE/16_groups_representations/problem/readme.md)；[A16-04—A16-06](../../06_exercises/05-stageE/16_groups_representations/solution/readme.md) | [C-E03](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E03](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E04 Wigner 与复—实桥 | [第 17 章 17.2—17.7](17_spherical_harmonics_wigner/chapter.md)；[D-E03](../../04_derivations/stageE/17_spherical_harmonics_wigner.md) | [例 17-2、17-4、17-8](17_spherical_harmonics_wigner/examples.md) | `coefficient_bridge`、`complex_representation`、`coefficient_filter`；T-E04；相位/m 顺序/共轭故障 | [Q17-04/Q17-06/Q17-09](../../06_exercises/05-stageE/17_spherical_harmonics_wigner/problem/readme.md)；[A17-04/A17-06/A17-09](../../06_exercises/05-stageE/17_spherical_harmonics_wigner/solution/readme.md) | [C-E04](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E04](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E05 CG 耦合 | [第 18 章 18.2—18.7](18_tensor_products_clebsch_gordan/chapter.md)；[D-E04](../../04_derivations/stageE/18_tensor_products_clebsch_gordan.md) | [例 18-3、18-5、18-7、18-13](18_tensor_products_clebsch_gordan/examples.md) | `cg_matrix`、`cg_couple`；T-E05；部分相位/单系数/漏交换相位 | [Q18-03—Q18-06](../../06_exercises/05-stageE/18_tensor_products_clebsch_gordan/problem/readme.md)；[A18-03—A18-06](../../06_exercises/05-stageE/18_tensor_products_clebsch_gordan/solution/readme.md) | [C-E05](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E05](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E06 Hamiltonian 子块 | [第 19 章 19.4](19_equivariant_graph_hamiltonian/chapter.md)；[D-E05](../../04_derivations/stageE/19_equivariant_graph_hamiltonian.md) | [例 19-3、19-4](19_equivariant_graph_hamiltonian/examples.md) | `fixed_hamiltonian`、`make_hamiltonian_edge`；T-E06；只左/只右/漏 dagger | [Q19-04/Q19-05](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/problem/readme.md)；[A19-04/A19-05](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/solution/readme.md) | [C-E06](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E06](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E07 Hermiticity 与身份 | [第 19 章 19.5](19_equivariant_graph_hamiltonian/chapter.md)；[D-E05](../../04_derivations/stageE/19_equivariant_graph_hamiltonian.md) | [例 19-5—19-7](19_equivariant_graph_hamiltonian/examples.md) | `edge_payload`、`validate_hamiltonian_edge`；T-E06/T-E12；payload/端点/shift/轨道/逆边故障 | [Q19-06/Q19-07](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/problem/readme.md)；[A19-06/A19-07](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/solution/readme.md) | [C-E07](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E07](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E08 等变消息层 | [第 18 章 18.8](18_tensor_products_clebsch_gordan/chapter.md)、[第 19 章 19.1—19.3](19_equivariant_graph_hamiltonian/chapter.md)；[D-E04](../../04_derivations/stageE/18_tensor_products_clebsch_gordan.md)、[D-E06](../../04_derivations/stageE/19_equivariant_graph_hamiltonian.md) | [例 18-9、18-10](18_tensor_products_clebsch_gordan/examples.md)、[例 19-2、19-13、19-14](19_equivariant_graph_hamiltonian/examples.md) | `make_message_provenance`、`message_layer`；T-E08；`wrong_irrep_parity_metadata`、方向/CG 元数据/逐分量非线性故障 | [Q18-09](../../06_exercises/05-stageE/18_tensor_products_clebsch_gordan/problem/readme.md)、[Q19-03](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/problem/readme.md)；[A18-09](../../06_exercises/05-stageE/18_tensor_products_clebsch_gordan/solution/readme.md)、[A19-03](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/solution/readme.md) | [C-E08](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E08](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E09 局部架 | [第 19 章 19.6](19_equivariant_graph_hamiltonian/chapter.md)；[D-E07](../../04_derivations/stageE/19_equivariant_graph_hamiltonian.md) | [例 19-9、19-10](19_equivariant_graph_hamiltonian/examples.md) | `local_frame`；T-E09；零/共线/等号/后备轴/正负极限 | [Q19-08](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/problem/readme.md)；[A19-08](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/solution/readme.md) | [C-E09](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E09](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E10 精度与成本 | [第 19 章 19.7](19_equivariant_graph_hamiltonian/chapter.md)；[D-E09](../../04_derivations/stageE/README.md) | [例 19-11、19-12](19_equivariant_graph_hamiltonian/examples.md) | `normalized_residual`、`reference_cost`、`run_scan`；T-E10；阈值/图/成本口径故障 | [Q19-09](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/problem/readme.md)；[A19-09](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/solution/readme.md) | [C-E10](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E10](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E11 自旋与时间反演 | [第 20 章 20.2—20.7](20_spin_time_reversal_complex/chapter.md)；[D-E08](../../04_derivations/stageE/20_spin_time_reversal_complex.md) | [例 20-3、20-6—20-8、20-12](20_spin_time_reversal_complex/examples.md) | `orbital_time_reversal`、`make_time_reversal_pair`；T-E11；partner/共轭/TRIM/Zeeman 故障 | [Q20-03/Q20-05/Q20-07](../../06_exercises/05-stageE/20_spin_time_reversal_complex/problem/readme.md)；[A20-03/A20-05/A20-07](../../06_exercises/05-stageE/20_spin_time_reversal_complex/solution/readme.md) | [C-E11](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E11](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |
| C-E12 端到端审计 | [第 15—20 章边界节](20_spin_time_reversal_complex/chapter.md)；[D-E01—D-E09 总索引](../../04_derivations/stageE/README.md) | [例 19-14](19_equivariant_graph_hamiltonian/examples.md)、[例 20-12](20_spin_time_reversal_complex/examples.md) | `test_t_e01`—`test_t_e12`（T-E01—T-E12）、63 项故障、padding 与授权扫描 | [Q19-10](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/problem/readme.md)、[Q20-10](../../06_exercises/05-stageE/20_spin_time_reversal_complex/problem/readme.md)；[A19-10](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/solution/readme.md)、[A20-10](../../06_exercises/05-stageE/20_spin_time_reversal_complex/solution/readme.md) | [C-E12](../../06_exercises/05-stageE/comprehensive/problem/readme.md)；[A-E12](../../06_exercises/05-stageE/comprehensive/solution/readme.md) |

## 4. 代码、失败与症状的反向索引

| 从此入口开始 | 回查能力与教材 | 继续核对 |
|---|---|---|
| `validate_rotation`、四元数或复合失败 | C-E01；第 15 章 | D-E01、T-E01，主动/被动和矩阵乘法顺序 |
| 反演下符号异常 | C-E02；第 15/16/18 章 | D-E01/D-E02/D-E04/D-E06、T-E02/T-E07，\((\ell,p)\) 与 polar/axial 类型 |
| `d_representation` 群律或正交失败 | C-E03；第 16 章 | D-E02、T-E03，STF 基顺序与 Frobenius 归一化 |
| K1/K2 hash、Wigner 或 filter 失败 | C-E04；第 17 章 | D-E03、T-E04，\(m\) 顺序、点值/系数、相位与共轭 |
| CG 表、交换或 intertwiner 失败 | C-E05；第 18 章 | D-E04、T-E05，DLMF 规范与整通道相位自由 |
| Hamiltonian block/provenance validator 失败 | C-E06/C-E07；第 19 章 | D-E05、T-E06/T-E12，左右表示、完整 edge payload、逆边和轨道表 |
| message direction、parity 或 CG metadata 失败 | C-E08；第 18/19 章 | D-E04/D-E06、T-E07/T-E08，coefficient filter、宇称乘法与逐层类型 |
| local-frame 退化或结果跳变 | C-E09；第 19 章 | D-E07、T-E09，无量纲 \(\zeta_u,\zeta_v,\eta\) 与拒绝域 |
| scan hash、worst case 或数组字节改变 | C-E10；推导总索引 4 | D-E09、T-E10，冻结图、PCG64 生命周期和成本口径 |
| k/-k、\(2\pi/4\pi\) 或 Kramers 失败 | C-E11；第 20 章 | D-E08、T-E11，反幺正共轭、定义域、H/S partner |
| 63 项故障数、padding 或授权字段异常 | C-E12；各章边界节 | T-E12，schema/provenance/有限性与 `UNRESOLVED_M8` |

## 5. D-E01—D-E09 能力边界

| 推导 | 可验证结论 | 成立条件 | 不能据此推出 |
|---|---|---|---|
| D-E01 | 主动/被动作用、表示复合以及 scalar/polar/axial/tensor 的 \(SO(3)/O(3)\) 作用一致 | 列向量、主动 \(R\)、先 \(R_1\) 后 \(R_2\)，反演显式记录 \(\det Q\) | 任意软件 Euler 接口自动同约定；只测 \(SO(3)\) 可判定宇称 |
| D-E02 | STF 基诱导实 \(s,p,d\) 表、直和和轨道宇称 | 冻结五基顺序、归一化、双侧作用和 \((\ell,p)\) | 任意实球谐排列具有相同数组 |
| D-E03 | DLMF-CS 复球谐、Wigner 与实基桥一致 | \(m=-\ell,\ldots,\ell\)，区分点值和 coefficient | 仅 hash 相同即可证明任意实现正确 |
| D-E04 | CG 选择定则、正交完备、intertwiner、交换与相位自由 | 固定输入/输出顺序、宇称乘法和相位元数据 | 整通道相位改变必然破坏等变性 |
| D-E05 | 轨道块按 \(D_iHD_j^\dagger\) 协变并保持逆边身份 | receiver/sender 轨道基、完整 edge 和正逆 row 同步 | 奇异值不变即可确定块元素身份 |
| D-E06 | coefficient filter、CG 消息、receiver sum 与同型混合闭合 | 两个 coefficient-D 输入、parity 元数据和完整 edge/direction provenance | 任意逐分量非线性或任意架构名称都等变 |
| D-E07 | 非退化局部架可回拉/推出 | \(u,v\) 均非零、归一化叉积超过阈值、无后备轴 | 局部架在退化域连续 |
| D-E08 | SU(2)、反幺正时间反演、H/S partner 与 Kramers/TRIM 接口可验证 | basis/spin 顺序、复共轭、独立 partner、\(S\succ0\) 与 TRIM 条件明确 | M7 已选择高级物理实践范围 |
| D-E09 | 表示维数、MAC/FLOP、聚合加法和显式数组字节唯一 | 冻结 \((N,E)\)、multiplicity、dtype、流式调度 | 数组字节等于进程峰值；合成成本等于真实 DeepH 成本 |

## 6. T-E01—T-E12 执行门控

统一环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。配置 A/B 分别使用 `float64`/`float32`、64/257 个旋转、图 \((N,E)=(4,8)/(7,18)\)；归一化残差阈值分别为 \(5\times10^{-12}\) 与 \(5\times10^{-6}\)，等号接受，非有限值拒绝。

| 测试 | 正向证据 | 强制反证 |
|---|---|---|
| T-E01 | SO(3)、逆、复合和规范四元数 | 11 类旋转/四元数/顺序失败 |
| T-E02 | 标量、polar、axial、二阶张量及主动/被动回构 | 转置与宇称混淆 |
| T-E03 | 实 p/d、STF、正交、群律、无迹 | d 顺序、归一化和双侧作用错误 |
| T-E04 | K1/K2、Wigner、点值和 coefficient 协变 | m 逆序、局部相位、漏共轭、接口方向错误 |
| T-E05 | 1×1/1×2 全 CG 表、选择定则、完备和相位锚点 | 部分相位、单系数、漏交换相位；合法整通道相位仍保持 intertwiner |
| T-E06 | 正/逆 edge row、4×8/8×4 块、Hermiticity 和 provenance | 左右作用、共轭、payload、端点/shift/轨道/逆边漂移 |
| T-E07 | \(SO(3)/O(3)\) 类型和标量门控 | 极/轴或偶/伪标量混淆 |
| T-E08 | filter、CG、聚合、同型混合逐层及端到端协变 | 高阶逐分量非线性、错误元数据与陈旧方向身份 |
| T-E09 | 无量纲退化阈值、右手架、4×8 回拉/推出 | 有量纲阈值、后备轴、等号方向和近退化跳变 |
| T-E10 | 144 点逐 case 阈值、最坏旋转/ell、成本和数组摘要 | 模式混用、图漂移、宽阈值、非有限与成本口径混淆 |
| T-E11 | spinless/spin-half、\(2\pi/4\pi\)、独立 H/S partner 与 TRIM Kramers | map/mask/轨道行/共轭/平方/partner/定义域错误及 Zeeman 破缺 |
| T-E12 | schema、有限性、provenance、padding 和授权边界 | 63 个唯一故障全部实际拒绝；活动 NaN 拒绝 |

三个 inactive padding 探针为 NaN、0 和 \(10^{300}\)。必须在 contraction、预测和 loss 之前切除 inactive 元素；三次活动输出残差和 loss 都为 0，不能用末端乘 mask 掩盖上游污染。

## 7. 表示追踪最短路径

遇到任一表示型数组或 Hamiltonian 分量时，按以下顺序追踪：

1. 核对授权边界、`schema_version`、结构/配置 ID 和 dtype；
2. 写明物理对象、主动或被动作用、群元素、行列式和复合顺序；
3. 对每层记录 \((\ell,p)\)、multiplicity、component 顺序、basis、shape 和 dtype；
4. 区分函数点值、展开 coefficient、轨道 basis 与 Hamiltonian 行列索引；
5. 对边对象重算紧凑 JSON payload、edge ID、端点、shift 和 direction provenance；
6. 对 CG 路径记录 \((\ell_1,p_1)\otimes(\ell_2,p_2)\to(L,p_1p_2)\)、表 hash 和交换相位；
7. 对 Hamiltonian 记录 receiver 左作用、sender 右侧 \(\dagger\)、正逆边和轨道表；
8. 在读取前应用 mask，按 dtype 使用冻结容差，再比较归一化残差；
9. 执行相应定向故障，确认错误实现实际被拒绝或残差超过阈值；
10. 最后陈述证据只能支持阶段 E 合成契约，不能外推到真实软件、材料或 DFT。

## 8. 关键锚点与复现记录

固定 K1/K2 hash 分别为 `347e352605a3f4f3ccb078b6cedf5c755fdc6aa3527ea41a8ea3e93d076972a2` 与 `5e783d9cdfe025238977f9e92d64d8b46e9a0e79eb8c9deba1af116aaafc7b82`；1×1/1×2 CG 全表 hash 为 `fd40673f73059974962cf9b8b3c9152b9af1bd28bb87028b9e4bffe797fd1a04`。Hamiltonian 正向 edge payload 为 `["stageD-edge-v1","stageE-H",0,1,0,0,0]`，SHA-256 为 `1a8d2a609fbe3cc7c5e9de863375420544fc64f1887b2f1df26d5defd9b2a4a8`。

144 点扫描的冻结整数锚点为 G_A `168/52/2728/2280`、G_B `378/143/5584/4576`，依次表示每旋转 MAC、每旋转聚合加法、完整物化数组字节和参考流式 peak 字节。规范扫描最大残差为 `1.9468769400071583e-07`，最坏 case 为 `float32-s20260809-r257-m1-a1e+03` 的 rotation 189、ell 2，case 摘要 SHA-256 为 `5317a387bfb026e53dceb31a85074d52ff520448c2fbac9649cb8013064cca7e`。

固定复现命令和 A/B/scan stdout SHA-256 见[代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md)。墙钟 benchmark 不进入规范 hash。

## 9. 诊断顺序与证据边界

| 现象 | 优先检查 | 验证入口 |
|---|---|---|
| 群律失败但单个旋转正交 | 主动/被动、先后顺序、矩阵乘法方向 | C-E01、T-E01 |
| \(SO(3)\) 通过而反演失败 | polar/axial 与 \((\ell,p)\) | C-E02、T-E07 |
| 实/复路线数值互为共轭或置换 | \(m\) 顺序、K1/K2 方向、点值/系数接口 | C-E04、T-E04 |
| CG 正交但与规范表不一致 | 整通道相位与局部相位的区分 | C-E05、T-E05 |
| Hamiltonian 奇异值正确但元素错位 | 左右轨道表、完整 edge identity、逆边 | C-E06/C-E07、T-E06 |
| 消息输出 shape 正确但旋转残差大 | direction provenance、CG 元数据、逐分量非线性 | C-E08、T-E08 |
| 局部架偶发符号跳变 | 无量纲退化度、等号方向、近共线正负极限 | C-E09、T-E09 |
| float64 错误仍通过 | 是否错误使用统一 \(5\times10^{-6}\) 阈值 | C-E10、T-E10 |
| 时间反演同式自比通过 | 是否使用独立 k/-k 的 H/S partner 和 TRIM 条件 | C-E11、T-E11 |
| 所有正例通过但 validator 可穿透 | 63 项故障是否真实执行且记录异常类型/消息 | C-E12、T-E12 |

阶段 E 通过只能证明冻结的理论、合成对象和 schema 契约自洽且可复算。由此不能推出 DeepH/e3nn 已安装、正式数据正确、某材料可迁移、某 DFT 后端可靠、真实训练预算充分或高级物理项已进入实践范围。

## 10. 阶段与授权停点

M7-10 材料完成后仍须由新的独立子 agent 执行材料完备性、可自学性和可验证性审计；随后 M7-11 对阶段 E 全快照执行独立总审计。M7 总审计清零后，还须用指定的 `gpt-5.6-sol`/`max` 独立审计 M3—M7，并由主 agent 修复、同一审计员复核至零问题。

上述审计全部通过后才进入 M8 集中决策冻结。M8 应集中确定计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算及高级物理范围；在 M8 冻结前继续保持 `UNRESOLVED_M8`。M8 完成后也不得直接开始 M9；正式安装、数据下载或复现实验仍须再次取得用户明确授权。
