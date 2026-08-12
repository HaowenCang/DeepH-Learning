# M6-07 阶段 D 合成周期图与普通 MPNN 独立代码审计

## 1. 审计结论

- 审计类型：正式、独立、阻塞式代码审计
- 审计日期：2026-08-04
- 审计对象：M6-07 合成数据、普通 MPNN、自动测试与失败样例
- 总结论：`FAIL`
- `BLOCKING`：5
- `NON_BLOCKING`：1
- 是否允许完成 M6-07：否
- 是否允许启动 M6-08：否

固定环境中的现有测试均能运行，双配置 CLI 也会自报 `overall_pass=true`；但是，这一结果不足以证明 M6-07 达到冻结门控。独立核对发现 T-D02、T-D03、T-D04/T-D05、T-D09 和 T-D10 的强制失败样例或跨对象接口没有被实现，且部分违反章节 schema 的输入会被当前 validator 静默接受。因此，本报告不接受自动套件的自我判定作为阶段通过证据。

## 2. 审计范围与快照

工作区不是 Git 仓库，无法用 commit 固定快照；本次以 SHA-256 固定已审文件。审计员没有修改实现文件，只新增本报告。

| 文件 | SHA-256 |
|---|---|
| `08_audits/M6_stageD_work_package.md` | `4A97203E84A95F9C4637A9C3CA8C54C600B7874D0BFC32E1D8F6A31825B19717` |
| `03_textbook/stageD_graph_conventions.md` | `BEBC75E5390E078A523331837E667DEE532919F1620F4037E11059888D05D265` |
| `04_derivations/stageD/README.md` | `AD2EDD36B524363B26EB7A8CBEEB1DD7D3629D17C5896D50BD4CE74B073A2F10` |
| `04_derivations/stageD/11_supervised_gradients_leakage.md` | `1340AB3B01581429259BF7BC7AC13204D5CDD85854012DCC14C323099314D8CC` |
| `04_derivations/stageD/12_permutation_aggregation.md` | `C550F89B728822F42693597CC7EBB27550488B9C3CBAE3D020B4C3333623EFB5` |
| `04_derivations/stageD/13_receptive_field_complexity.md` | `94D36A0C9206D186E1D2B64AF8D3E4ED835DC2FEA2E6A9F2655F27FB67F50E93` |
| `04_derivations/stageD/14_periodic_enumeration_provenance.md` | `18F0D6E0CD09FD510FB048B6CB05018A130C20E34DF6E2A0F0919BF3234C130F` |
| `05_code_exercises/stageD_synthetic_mpnn/README.md` | `F96A97FEB1DA8100BEC2DB7EFD110F8C1F4A17CBA2F426A08AC468D3020FA252` |
| `05_code_exercises/stageD_synthetic_mpnn/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/stageD_synthetic_mpnn/run_experiments.py` | `0518CA6524F404B466AA94DDF6C11B839145FF7924247C61AF3225BEDE64C48E` |
| `05_code_exercises/stageD_synthetic_mpnn/staged_models.py` | `19C5ED16C2932A42555D23912722B2C4CFB2EB0B3A30FA9C09927C30A89A3B09` |
| `05_code_exercises/stageD_synthetic_mpnn/test_staged_models.py` | `8F159632942E8FD77213F41B616C680FAF74C4E39192B15E31E77457C92A3FF5` |

同时核对了第 11—14 章的 `chapter.md`、`examples.md`、`outline.md` 与 `sources.md`。与本审计直接相关的正文快照如下。

| 正文 | SHA-256 |
|---|---|
| 第 11 章 `chapter.md` | `4FB33A4E5CB49F4A4AC728958C047A3641D6C48600E1938E3CAF8DB268E75E88` |
| 第 12 章 `chapter.md` | `6034592C3A3407DD90298B4C05C7BAD2E5464C7AEE87CDD72B698FFE03938880` |
| 第 13 章 `chapter.md` | `E613DE99535C43115873596D1F24F6A6ED6990555E9E6511960750640C8EFB61` |
| 第 14 章 `chapter.md` | `F1C83F0F705C56760DDB6B17B82B19D93AFE6C46296534C39630079290BFF784` |

## 3. 环境与可复现实验

使用固定解释器：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -c "import sys,numpy,scipy; print(sys.version); print(numpy.__version__); print(scipy.__version__)"
& $py -m pip check
& $py -m unittest discover -s .\05_code_exercises\stageD_synthetic_mpnn -p 'test_*.py' -v
```

结果：

- Python 3.12.13；
- NumPy 2.3.5；
- SciPy 1.18.0；
- `pip check`：`No broken requirements found.`；
- unittest：8 项全部通过，耗时约 0.69 s。

双配置 CLI 各运行两次，均以退出码 0 结束：

| 配置 | 规范输出字节数 | SHA-256 | 重复运行 | T-D02 最大相对误差 | T-D03 测试 MSE |
|---|---:|---|---|---:|---:|
| A / 20260806 | 5696 | `DBE94F36B1EDF742FBB0824DB6A30BA52E1C1A47CE5A8B29F04D96A1F7FB80F2` | 字节一致 | `1.26615009926265e-10` | `2.58160209434307e-31` |
| B / 20260817 | 5734 | `3D989574E83B7FE2AD849F0B317E3884C10AF510A3C482297C69C61E582A9FE6` | 字节一致 | `1.12989469343294e-10` | `6.09364234404121e-31` |

全参数有限差分分别覆盖 132 个和 300 个参数坐标，均低于 `1e-5` 阈值。错误 seed 组合以 argparse 退出码 2 拒绝。非规范 benchmark 本机复算为：

| 配置 | 构图 s/call | 前向 s/call |
|---|---:|---:|
| A | 0.00922366 | 0.0000529960 |
| B | 0.00862752 | 0.0000593760 |

这些通过项只证明已执行路径的确定性和数值结果，不关闭下列缺失路径。

## 4. 独立对抗复算

独立脚本没有复用项目的预期结果常量来计算规范边哈希。对 UTF-8 字节

```text
["stageD-edge-v1","fixture",1,2,0,-1,3]
```

独立 SHA-256 为 `3b88233a229375fef60c1f1bb00349ae4913d2672eeedd9b2b4a739b665e2a96`，与实现一致。

另外选择 8 个独立随机斜晶胞、3 个原子及随机有限 cutoff，对解析镜像盒和逐轴外扩一层的盒子重新构图；8/8 的完整离散边键集合一致。主夹具为 `bounds=[2,2,2]`、候选数 2000、保留边数 18；多重边夹具保留 8 条边。周期有限枚举、非零自镜像保留和规范 edge ID 的核心正路径由该复算支持。

对抗输入得到以下反例：

- `validate_concat_batch` 静默接受 `node_graph_id=edge_graph_id=-1` 的图，因为只检查“相等”，没有验证图 ID 的非负范围、批大小及逐图计数；
- 零边图把 `structure_id` 改为空字符串，并把 `cell`、`fractional` 改为 float32 后，`validate_graph` 仍接受；
- 把图中的 `bounds` 改为 `[-999,-999,-999]`、`candidate_count` 改为 -1，`validate_graph` 仍接受；
- 拼接批只生成 `node_graph_id, edge_graph_id, receiver, sender`；padding 批只生成 `node_mask, edge_mask, receiver, sender`；
- 当前代码没有 mean/`has_incoming`/max 空集合策略的可执行聚合接口；
- T-D10 的 11 个捕获失败中没有“分组污染”，`group_pollution_captured` 只是复用了 T-D01 内部生成的布尔量，并未对受污染的外部划分执行拒绝。

## 5. 逐 T-D 判定

| ID | 判定 | 主要依据 |
|---|---|---|
| T-D01 | `PASS` | 分组集合两两无交集，逐帧划分反例产生三组非空交集；A/B 均确定。该结论仅覆盖显式 group ID 交集。 |
| T-D02 | `FAIL` | 正确实现的全参数有限差分通过，符号翻转坐标也被识别；但冻结章节要求的漏掉 `1/S`、receiver scatter 改 sender、错误 tanh 导数、padding 梯度泄漏四类定向故障没有全部注入，工作包要求的“漏批平均”失败样例也未出现。 |
| T-D03 | `FAIL` | 当前 `grouped_regression` 是无组随机效应、无噪声的三维精确线性回归；`layers/hidden_dim/edge_dim/output_dim` 不参与该训练。它不实现第 11 章冻结的 `u_g, tau_t, b_g` 泄漏族，也不输出组 ID、样本/组计数、训练/验证曲线、MSE/MAE 和随机帧表观误差。近零测试 MSE 因此不是冻结 T-D03 对象的验收证据。 |
| T-D04 | `FAIL` | 节点状态与边数值输出在节点/边行重排下残差通过，错误端点重标也产生非零残差；但没有构造边输出 provenance 对象，也没有同步置换并逆映射 `edge key / edge ID / mask / 轨道身份`，违反第 13 章 T-D04 的明确接口。 |
| T-D05 | `FAIL` | 公共和逐原子换胞的位移、距离、规范 shift 和 edge ID 正路径通过，错误固定 shift 失败；但实现依赖原边行顺序逐行比较，没有按冻结的完整 `K_q` 建立字典、排序和双射，也没有把预测与 provenance 纳入同一行映射。边行错配仍缺少端到端拒绝证据。 |
| T-D06 | `PASS` | 冻结盒与外扩一层盒的完整键一致；固定 `[-1,1]^3` 漏边和最小镜像漏多重边反例均执行。8 个独立随机斜晶胞复算也一致。 |
| T-D07 | `PASS` | 多镜像保留、零位移自环排除、非零自镜像保留、完整键唯一；按原子对去重会减少边数。 |
| T-D08 | `PASS` | 线性局部同步消息传递对单输入扰动的一至三层支持集合与有向前驱集合一致；同层原地更新在一层内越级传播的失败样例被捕获。 |
| T-D09 | `FAIL` | 轨道局部索引和实际合成 ID 的单图正路径较完整，但输出未与 `structure_id/receiver/sender/shift/edge_instance_id/unit` 及预测组成可验证的统一 schema；拼接和 padding 批缺少章节规定的大部分字段、逐图计数和真实计算路径；没有证明 padding 在聚合、统计、归一化和损失前被排除；mean/`has_incoming` 和 max 空集合策略缺失。 |
| T-D10 | `FAIL` | 非有限坐标、奇异/阈值病态晶胞、非法 cutoff、越界端点和重复记录能被拒绝，`A_-` 接受且 `A_0/A_+` 拒绝；但分组污染没有进入拒绝函数，非法 graph ID、空结构 ID、float32 schema 和损坏的复杂度元数据存在静默接受反例。 |

## 6. BLOCKING 清单

### B01：T-D02 强制梯度故障矩阵不完整

第 13 章明确要求至少注入漏掉 `1/S`、receiver scatter 改为 sender scatter、tanh 导数错误和 padding 梯度泄漏；工作包也要求遗漏平均因子必须失败。当前只做了一个 `Wo` 坐标的符号翻转，以及对正确 padding 梯度的直接读取，没有执行其余错误实现。

最小关闭条件：

- 为四类错误分别提供实际错误梯度或错误反传变体；
- 每类都必须由独立有限差分或定向不变量拒绝；
- A/B CLI 和 unittest 输出每个故障名称、检测量、阈值与被捕获状态；
- 保留现有 132/300 全参数正向检查。

### B02：T-D03 验收的生成式和评价对象被替换

`grouped_regression` 使用所有组共享的无噪声线性真值，组划分对可学习规律没有作用，且网络层数、宽度和输出维数不参与训练。第 11 章冻结的组潜变量/帧变量/组偏置泄漏族及其评价证据没有实现。因此，当前测试不能证明“逐帧划分产生表观低误差而独立组评价揭示泛化差距”，也不能作为 M6-07 普通 MPNN 训练门控。

最小关闭条件：

- 实现与第 11 章一致的确定性分组生成式，或先正式修订工作包与章节使另一生成式成为唯一冻结契约；
- 在运行前固定并真实使用样本数、宽度、层数、学习率、步数和阈值；
- 输出 train/validation/test 组 ID、样本数/组数、交集、训练与验证轨迹、冻结模型的 MSE/MAE，以及逐帧反例的交集与表观误差；
- 强制证明“训练下降而独立组阈值失败”不能通过，并证明重复运行一致。

### B03：T-D04/T-D05 没有验证预测—完整键—provenance 的统一行映射

当前置换测试只比较节点状态和预测数组；当前换胞测试按原数组行直接比较。它们没有创建第 13/14 章规定的边输出对象，也没有以完整 `K_q=(structure_id,i,j,nx,ny,nz)` 建字典、排序和验证双射。因此，预测、edge ID、mask 或轨道身份采用不同排序规则的错误不在检测范围内。

最小关闭条件：

- 定义包含预测、完整键、edge ID、块形状、mask、局部/实际轨道身份、unit 和 schema 版本的边输出 schema；
- T-D04 在非对称图、节点置换和独立随机边行重排下，同步映射所有字段并在逆映射后逐项比较；
- T-D05 对公共/逐原子换胞显式构造 `K_q` 字典、排序和双射，再独立比较位移与距离；
- 注入预测、键、mask 或轨道身份行错位，以及按原子对/距离配对的失败样例。

### B04：T-D09 批处理、padding 和空入边接口不完整

拼接批缺少 `node_count/edge_count` 以及节点/边特征和 provenance；padding 批缺少章节规定的节点/边张量、shift、几何、特征和逐图计数。现有测试只验证端点/mask 外形，没有让 padding 数据经过聚合、统计、归一化和损失，也没有实现 mean 的零输出与 `has_incoming=false`，或 max 对空入边的拒绝。输出 provenance 也未携带完整边身份和单位。

最小关闭条件：

- 使 concat/padded schema 覆盖第 12—14 章冻结字段、精确 dtype/shape、逐图计数和图 ID 范围；
- 在同一批上实际执行聚合、统计/归一化和 masked loss，并用非零/NaN padding 注入证明其在读取前被排除；
- 实现并测试空入边 sum、mean+`has_incoming` 及 max 拒绝策略；
- 对排序、拼接、padding 和预测输出执行完整 provenance 行映射验证；
- 增加跨图、负 graph ID、计数不一致、非连续 mask、padding 泄漏和字段行错位故障。

### B05：T-D10 没有实际拒绝分组污染，schema validator 仍可静默接受非法对象

T-D10 的 `group_pollution_captured` 不调用任何接受外部 split 的 validator；它只是复用内部构造的 T-D01 布尔值。独立反例还证明负 graph ID、零边图的空 `structure_id` 与 float32 核心字段，以及损坏的 `bounds/candidate_count` 能穿过 validator。这与章节规定的 ID 范围、float64 schema、身份和成本可验证性不一致。

最小关闭条件：

- 提供接收显式 split/group lineage 的 validator，并把组交集污染作为实际 `expected failure`；
- 严格验证非空 `structure_id`、核心字段 dtype、graph ID 范围、逐图计数；
- 将 `bounds`、`candidate_count` 纳入可重算的一致性验证，或从受信 schema 中移除并在报告时现场重算；
- 对零边图也执行身份和 dtype 验证；
- 将上述反例纳入 A/B CLI 与 unittest。

## 7. NON_BLOCKING 清单

### N01：CLI 字节确定性尚未由项目测试通过子进程验证

现有 unittest 对 `run_suite` 返回值进行两次 JSON 编码，不能覆盖 argparse、stdout 编码、换行和实际退出码。本次独立审计已证明当前固定环境下 A/B 子进程输出字节一致，因此不单独阻塞；在关闭 B01—B05 时应增加 subprocess 级回归，避免未来 CLI 包装层漂移。

## 8. 已通过的边界

- 依赖以精确版本固定，`pip check` 无冲突，本次审计没有安装任何依赖；
- 没有发现 DeepH 导入、正式数据访问、DFT 标签生成、网络下载或材料体系选择；
- 输出继续把材料体系、DFT 后端和 DeepH 软件对象标为 `UNRESOLVED_M8`；
- M8/M9 授权边界文本与当前路线一致；
- 本报告不对真实材料精度、旋转等变性、Hamiltonian 物理语义或任何 DFT 后端作外推。

## 9. 放行条件

当前结论为 `FAIL`。主 agent 应修复 B01—B05；完成后必须由本独立审计 agent 对新的文件哈希和关闭条件进行定点复核。只有定点复核确认：

- `BLOCKING=0`；
- 所有 T-D01—T-D10 均满足工作包、统一约定和第 11—14 章接口；
- A/B CLI、unittest、子进程字节确定性和对抗失败矩阵全部通过；

方可将 M6-07 标记为 `COMPLETED` 并启动 M6-08。
