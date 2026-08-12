# 阶段 C 标签语义模板：从理论对象到可验证矩阵记录

## 1. 模板用途与状态

本模板定义 Hamiltonian/overlap 标签在进入训练前应携带的最低语义和验证证据。它用于区分“同一理论对象的不同坐标表示”“不同离散近似产生的不同数值对象”和“相同文件形状但语义不相容的记录”。模板本身不是正式标签，也不授权生成正式数据。

M5 只允许 `generation_status=SYNTHETIC_M5`。真实后端、材料、理论层级、泛函、赝势/全电子处理、自旋、smearing、软件版本和投影方法在 M8 前保持 `UNRESOLVED_M8`。可执行合成实例由 [synthetic_label_record](../05_code_exercises/stageC_teaching_scf/teaching_scf.py) 生成，并由 T-C09 验证；不得把下面的说明性占位文本直接冒充已通过 schema 的 JSON。

## 2. 四层对象与误差边界

| 层级 | 典型对象 | 必须登记的选择或条件 | 误差或歧义 |
|---|---|---|---|
| 理论层 | 固定核电子 Hamiltonian、HK/KS 泛函、有限温度或自旋扩展 | 电子结构层级、\(E_{xc}\)、相对论/自旋、全电子或赝势 | 理论近似、模型适用域；不能由数值收敛消除 |
| 数值层 | SCF 固定点、基/网格、\(k\) 采样、占据 | 基定义、cutoff/网格、采样、阈值、实际收敛指标 | 离散、采样、迭代和求解器误差 |
| 表示层 | \(H,S\)、轨道顺序、实空间块、Fourier、规范 | 单位、bra/ket、位移方向、相位、overlap 处理 | 语义错配、规范/基变换、索引错误 |
| 投影与模型层 | 完整空间到目标子空间、预测矩阵与派生谱 | 投影方法、能窗/目标空间、回投损失、矩阵/能带验证 | 信息丢失、目标定义变化、学习误差 |

“DFT 已收敛”只能描述在指定理论和表示选择下某些数值指标达到阈值，不能说明理论近似误差、投影损失或模型误差为零。“能带一致”也不能单独证明固定坐标矩阵标签一致。

## 3. `stageC-label-v1` 字段契约

| 路径 | 类型/形状 | M5 合成状态 | 后续实际记录的语义 |
|---|---|---|---|
| `schema_version` | 非空字符串 | `stageC-label-v1` | schema 版本 |
| `generation_status` | 枚举字符串 | `SYNTHETIC_M5` | 正式生成状态须在 M8/M9 另行冻结 |
| `backend.name/version/commit` | 字符串 | 均为 `UNRESOLVED_M8` | 实际软件对象与精确版本/commit |
| `artifacts.inputs[0].uri_or_path/sha256` | 字符串；SHA 为 64 位小写十六进制 | `synthetic/...` 与真实合成内容哈希 | 输入制品身份与内容哈希 |
| `artifacts.outputs[0].uri_or_path/sha256` | 同上 | 同上 | 输出制品身份与内容哈希 |
| `structure.id/sha256` | 字符串与 SHA-256 | `SYNTHETIC` 与合成内容哈希 | 结构身份不得仅依赖文件名 |
| `structure.lattice` | 有限数值 \(3\times3\)，非奇异 | 单位阵 | 晶格矩阵及其单位约定 |
| `structure.species` | 长度 \(N\) 的字符串数组 | `X,Y` 占位物种 | 原子种类/赝原子定义 |
| `structure.positions` | 有限数值 \(N\times3\) | 两个合成位置 | 坐标类型与单位需另行冻结 |
| `structure.boundary_conditions` | 长度 3 字符串数组 | 三方向 `periodic` | 周期/非周期边界 |
| `theory.*` | 字符串或嵌套映射 | 全部 `UNRESOLVED_M8` | 理论层级、XC、全电子/赝势、势数据集、相对论处理 |
| `basis.type/definition/cutoff_or_grid/id/sha256` | 字符串、映射与 SHA-256 | 冻结合成白名单 | 实际基/网格和数据集身份 |
| `spin.polarization/noncollinear/soc` | 字符串状态 | 全部 `UNRESOLVED_M8` | 三项不得由单个布尔值含混替代 |
| `sampling.kind` | 字符串 | `synthetic_equal_weight` | 实际采样类型 |
| `sampling.k_mesh/k_shift` | 长度 3；正整数/有限数值 | `[1,1,1]` / `[0,0,0]` | 网格和位移 |
| `sampling.k_weights` | 有限数值数组，权重和为 1 | `[1.0]` | 与采样点一一对应 |
| `occupation.electron_count` | 正有限数值 | `1.0` | 电子数与电荷态 |
| `occupation.smearing_method/temperature` | 字符串状态 | `UNRESOLVED_M8` | 数值 smearing 与物理温度必须区分 |
| `occupation.reported_energy_functional` | 字符串 | `teaching_energy` | 报告的是自由能、内能还是外推量 |
| `convergence.scf_residual_definition` | 字符串 | `l2_over_electron_count` | 残差对象、范数和归一化 |
| `convergence.*_tolerance` | 正有限数值 | 冻结教学阈值 | SCF、能量和本征求解阈值 |
| `convergence.max_iterations` | 正整数 | `80` | 上限本身不代表收敛 |
| `convergence.achieved_metrics` | 非空映射，值为有限数值 | 含实际教学残差 | 必须与阈值分开保存 |
| `representation.output_object` | 字符串数组 | `[H,S]`，即数学对象 \(H,S\) | 预测/存储对象集合 |
| `representation.units` | 字符串 | `atomic_units` | 每个输出对象的单位 |
| `representation.orbital_ordering` | 唯一非空字符串数组 | `X:s,Y:s` | 轨道、原子、\(l,m\) 与自旋顺序 |
| `representation.atom_orbital_index_map` | 映射到非负整数数组 | 覆盖索引 0、1 | 显式原子—轨道切片 |
| `representation.lattice_displacement_direction` | 字符串 | `ket_cell_minus_bra_cell` | \(R\) 的方向 |
| `representation.bra_ket_order` | 字符串 | `row_is_bra_column_is_ket` | 行列指标方向 |
| `representation.fourier_forward/inverse` | 字符串 | 冻结正负号与归一化 | 正逆 Fourier 约定必须成对 |
| `representation.phase_or_gauge` | 字符串 | `cell_phase` | 轨道中心相位/规范 |
| `representation.overlap_treatment` | 字符串 | `explicit_generalized_eigenproblem` | 是否显式保留 \(S\) |
| `projection.method` | 字符串 | `synthetic_orthogonal_subspace` | 实际投影软件/算法留待 M8 |
| `projection.window` | 两个递增有限数值 | `[-1,1]` | 目标能窗或子空间选择 |
| `projection.source_dimension/target_dimension` | 正整数且目标不大于源 | `12/5` | 子空间维数 |
| `projection.loss_metric/loss_value` | 字符串与有限数值 | 相对 Frobenius / 教学值 | 需与能带和矩阵验证并列 |
| `projection.band_validation/matrix_validation` | 映射 | `synthetic_pass` | 派生谱与固定表示矩阵两类验证 |
| `validation.commands` | 非空字符串数组 | 合成复现命令 | 完整可执行命令 |
| `validation.environment.*` | 精确版本字符串 | Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 | 用户态依赖锁定 |
| `validation.seed` | 整数 | 固定 seed | 随机对象可重建 |
| `validation.audit_status` | 字符串 | `PENDING_M5_INDEPENDENT_AUDIT` | 不能把主实现自检写成独立通过 |

## 4. 说明性骨架

下列骨架用于理解嵌套关系，`<...>` 不是可执行值：

```json
{
  "schema_version": "stageC-label-v1",
  "generation_status": "SYNTHETIC_M5",
  "backend": {
    "name": "UNRESOLVED_M8",
    "version": "UNRESOLVED_M8",
    "commit": "UNRESOLVED_M8"
  },
  "structure": {
    "id": "SYNTHETIC",
    "sha256": "<64-lowercase-hex>",
    "lattice": "<finite-3x3>",
    "species": ["X", "Y"],
    "positions": "<finite-Nx3>",
    "boundary_conditions": ["periodic", "periodic", "periodic"]
  },
  "theory": {
    "electronic_structure_level": "UNRESOLVED_M8",
    "xc": "UNRESOLVED_M8",
    "all_electron_or_pseudopotential": "UNRESOLVED_M8",
    "potential_dataset": {
      "id": "UNRESOLVED_M8",
      "sha256": "UNRESOLVED_M8"
    },
    "relativistic_treatment": "UNRESOLVED_M8"
  },
  "representation": {
    "output_object": ["H", "S"],
    "units": "atomic_units",
    "orbital_ordering": ["X:s", "Y:s"],
    "lattice_displacement_direction": "ket_cell_minus_bra_cell",
    "bra_ket_order": "row_is_bra_column_is_ket",
    "fourier_forward": "sum_R A_R exp(+ikR)",
    "fourier_inverse": "mean_k A_k exp(-ikR)",
    "phase_or_gauge": "cell_phase",
    "overlap_treatment": "explicit_generalized_eigenproblem"
  }
}
```

完整 67 路径集合以 [M5 工作包第 8 节](../08_audits/M5_stageC_work_package.md)和代码中的 `REQUIRED_PATHS` 为准；该二者必须保持一致。

## 5. 验证顺序

标签记录应按以下顺序验证：

1. 路径存在性：67 个必填路径及数组内成员全部存在；
2. 结构验证：标量、数组、映射类型，数值有限性，shape 和数组间长度关系；
3. 身份验证：实际制品哈希格式正确，并与冻结内容重算一致；
4. 授权验证：M8 哨兵未提前解析，合成字段只取白名单值；
5. 数值验证：Hermiticity、\(S\succ0\)、SCF 残差、投影回投和截断指标；
6. 语义验证：单位、轨道顺序、bra/ket、\(R\) 方向、Fourier、规范和 overlap 处理一致；
7. 前向验证：矩阵、能带/谱、目标子空间及适用的物理量分别验收；
8. 独立审计：主实现的 `pass` 不替代独立报告。

T-C09 实际执行 67 个逐路径删除样例以及 47 个类型、形状、哈希和 M8 选择变异。schema 验证通过仍只说明记录满足最低契约；它不能证明理论选择合适、DFT 标签正确或模型具有泛化能力。

## 6. M8/M9 转换规则

准备 M8 时，应集中冻结计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算和高级物理范围。冻结后应产生新版本 schema 或明确的迁移记录，不得静默把 `UNRESOLVED_M8` 替换为某个本地默认值。

即使 M8 已冻结，开始 M9 的正式 DeepH 安装、数据下载、DFT 标签生成或复现实验前仍须取得明确执行授权。本模板不构成该授权。
