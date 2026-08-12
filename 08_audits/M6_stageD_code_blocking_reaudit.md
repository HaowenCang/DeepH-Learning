# M6-07 阶段 D 代码阻塞项定点复核

## 1. 复核结论

- 复核类型：原独立审计员定点复核
- 复核日期：2026-08-09
- 基准报告：`M6_stageD_code_independent_audit.md`
- 总结论：`FAIL`
- 原问题状态：B01 `CLOSED`；B02 `CLOSED`；B03 `OPEN`；B04 `OPEN`；B05 `CLOSED`；N01 `CLOSED`
- 剩余 `BLOCKING`：2
- 剩余 `NON_BLOCKING`：0
- 新增独立问题 ID：0；新增对抗反例归入原 B03/B04 的未满足关闭条件
- 是否允许完成 M6-07：否
- 是否允许启动 M6-08：否

修复版显著扩大了自动验收范围：13 项 unittest、A/B CLI、完整梯度故障矩阵、冻结分组生成式、边键双射、NaN padding 执行路径、硬输入失败矩阵和子进程确定性均通过。然而，原 B03/B04 的“完整行映射”和“完整 dtype/shape/schema”关闭条件仍未达到。独立变异证明 edge-output 可携带没有对应边键的额外预测/分量行，concat/padded 批可静默接受几何行错位，padded 批还可接受预测宽度与 component mask 宽度不一致。因此，当前 `overall_pass=true` 仍不能作为 M6-07 放行证据。

## 2. 已复核快照

工作区仍不是 Git 仓库，本次以 SHA-256 固定对象。审计员没有修改实现文件，只新增本复核报告。

| 文件 | SHA-256 |
|---|---|
| `08_audits/M6_stageD_code_independent_audit.md` | `0172DB26202A2D3102EABD58B911ABC83CCBB631E68C8CF7FC405ACE5312DC3E` |
| `08_audits/M6_stageD_work_package.md` | `4A97203E84A95F9C4637A9C3CA8C54C600B7874D0BFC32E1D8F6A31825B19717` |
| `03_textbook/stageD_graph_conventions.md` | `BEBC75E5390E078A523331837E667DEE532919F1620F4037E11059888D05D265` |
| `04_derivations/stageD/README.md` | `AD2EDD36B524363B26EB7A8CBEEB1DD7D3629D17C5896D50BD4CE74B073A2F10` |
| `05_code_exercises/stageD_synthetic_mpnn/README.md` | `E5646C72AB5BDC57EBBDE0F06C2D76959F62D3950A00FEAE0B360072162E07FC` |
| `05_code_exercises/stageD_synthetic_mpnn/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/stageD_synthetic_mpnn/run_experiments.py` | `91522892CC33ED7D04CFFE8E0B91451AEF8D08B990A356430887CF43822B5DE3` |
| `05_code_exercises/stageD_synthetic_mpnn/staged_models.py` | `550E36A373B6CA5B96686B2C42F6E025411D84EB9ED125DE51538215E0E4905B` |
| `05_code_exercises/stageD_synthetic_mpnn/test_staged_models.py` | `3F7095D900618ACBF9E61137E429CF49D257562D8C68E59E23D5D9F1D9E9DB97` |

## 3. 固定环境与命令结果

固定解释器：

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
- `pip check` 无破损依赖；
- 13 项 unittest 全部通过，耗时约 3.12 s；
- 错误 seed `config=A, seed=0` 以退出码 2 拒绝。

独立以 Python `subprocess` 捕获实际 stdout 字节，包括 Windows `CRLF`：

| 配置 | 退出码 | stdout 字节数 | SHA-256 | 第二次运行 |
|---|---:|---:|---|---|
| A / 20260806 | 0 | 10265 | `5BC7FABFFF309359B53F4ADA588E016B42CBFA45BC00BD0F2F3B6892A9D03627` | 字节一致 |
| B / 20260817 | 0 | 10322 | `344272A03F175B7DC253E1A27642C2BB112EB1C95D69B2EDDC6CC245D80BC8D7` | 字节一致 |

## 4. 原问题逐项复核

### B01：T-D02 强制梯度故障矩阵——CLOSED

正确反传继续执行全部参数中心差分：配置 A 为 132 个参数坐标、最大相对误差 `1.2661500993e-10`；配置 B 为 300 个参数坐标、最大相对误差 `1.1298946934e-10`，均低于 `1e-5`。

五类实际错误反传均执行并超过检测阈值。A/B 的最小故障差异分别不低于 `0.0300966` 与 `0.134047` 的量级，远高于 `1e-5`：

- 漏掉 `1/S`；
- receiver scatter 改为 sender；
- tanh 导数错误；
- padding 梯度泄漏；
- 输出梯度符号翻转。

padding 正确输出梯度最大值为 0。原最小关闭条件全部满足，B01 关闭。

### B02：T-D03 冻结生成式、MPNN 对象和评价证据——CLOSED

当前代码与 README 固定：

- `x=[u_g,tau_t]+xi`；
- `y=1.5u_g-0.7tau_t+b_g+epsilon`；
- `xi_std=0.005`、`bias_std=0.03`、`epsilon_std=0.002`；
- A/B 的组数、帧数、层数、隐藏宽度、边宽度、输出宽度、步数和学习率；
- 绝对测试阈值 `2e-2`；
- 测试 MSE 还必须低于零预测基线的四分之一。

两配置真实使用冻结参数构造节点/边特征、层数和边头，并只训练 `Wo/bo`。独立改变层数、边宽度、输出宽度或把训练步数改为 0，都会改变训练和测试结果；步数为 0 时测试 MSE 分别升至约 0.255 和 0.251，证明预算不是仅记录未使用。

| 配置 | 初始训练 MSE | 最终训练 MSE | 验证 MSE | 测试 MSE | 阈值 | 零预测基线 |
|---|---:|---:|---:|---:|---:|---:|
| A | 0.220659 | 0.002224 | 0.001058 | 0.001944 | 0.02 | 0.151155 |
| B | 0.200629 | 0.001618 | 0.004590 | 0.005013 | 0.02 | 0.169820 |

输出包含三个集合的组 ID、组数、样本数、edge-output 数、空交集、11 个训练—验证轨迹点、MSE/MAE、损坏目标误差和逐帧泄漏反例。逐帧表观 MSE 为 `2.104e-5/3.135e-5`，均低于独立组线性 MSE `1.525e-4/2.040e-3`。

关于“实现前冻结且不得事后放宽”：仓库记录明确声明修复时先把生成式、噪声和 `0.02` 阈值共同冻结，随后改正特征构造，而不是按运行输出放宽；A/B 实测分别只使用阈值的约 9.7% 和 25.1%，并另受相对零基线门控约束。当前快照没有出现更早的其他修复阈值，也没有阈值回退分支。结合可执行结果，本定点复核接受该冻结记录。B02 关闭。该结论只适用于当前合成族。

### B03：T-D04/T-D05 预测—完整键—provenance 统一行映射——OPEN

已确认的修复：

- `stageD-edge-output-v1` 包含结构 ID、receiver、sender、shift、edge ID、prediction、block shape、mask、局部/实际轨道身份、unit 和 schema；
- T-D04 在非对称图、节点置换和独立边行倒序下用完整键比较，A/B 预测残差分别为 `5.55e-17`、`1.11e-16`；
- mask 行错位被 validator 拒绝；prediction 行错位产生 `0.5828/0.5284` 残差；
- T-D05 的 18 个完整 `K_q` 键建立字典和双射，逐原子换胞残差不超过 `6.67e-16`，错误原行读取产生 `0.4299/0.5356` 残差。

但是，独立长度变异仍可穿透 `validate_edge_output`：保持 receiver/sender/shift 为 E 行，保持 `block_shape` 为 E 行，却给 `prediction`、`mask`、四个轨道分量数组各追加一行。validator 没有断言 `mask.shape[0] == E`，只遍历前 E 个完整键，因此静默忽略额外的无键预测/身份行并返回成功。

这直接违反原关闭条件中“预测、完整键、mask、轨道身份采用同一行映射”及 edge-output 的 `float64[E,Pmax]` 形状。B03 保持 OPEN。

最小关闭条件：

- `validate_edge_output` 对 prediction、mask、全部分量数组和 edge ID 显式要求第一维严格等于 E；
- 要求所有边级数组具有同一 `(E,Pmax)` 或对应 `(E,...)` 形状；
- 把“端点键 E 行而预测/分量 E+1 行”及删行变异加入 unittest 和 CLI expected-failure 矩阵。

### B04：T-D09 完整批 schema、padding 和空入边——OPEN

已确认的修复：

- concat/padded 批已有版本、逐图计数、非负 graph ID、特征、几何、prediction、provenance、unit 和 mask；
- 负 graph ID、计数错配、跨图边、轨道 provenance 行错位、非连续 padding 和缺字段均被拒绝；
- 配置 A/B 分别保留 66/78 个 NaN padding 哨兵，真实执行前向、归一化和 masked loss，预测残差为 0、loss 为 0；
- 把 NaN padding 替换为正负 `1e300` 后，实际预测仍与基线完全一致，独立残差为 0，证明这些 padding 行在读取前被切除；
- sum/mean 空入边均为零，mean 返回 `has_incoming=[false,true,false]`，max 对空入边抛出错误。

但两个硬 schema 缺口仍存在：

1. concat 和 padded validator 均可接受 active `displacement` 或 `distance` 独立循环滚动一行。二者没有验证 `distance == norm(displacement)`，也没有把几何与完整边键形成可重算关系；因此几何张量行错位会静默穿透。
2. padded validator 只检查 `prediction.shape[:2] == edge_mask.shape`，未检查 prediction 第三维等于 `component_mask`、轨道下标和实际轨道 ID 的 `Pmax`。给 prediction 追加一个输出分量后，validator 仍接受。

独立变异还确认 concat 的任意 edge feature 行滚动不会被识别。通用特征的语义可能无法由独立 validator 重建，但当前冻结 `_edge_features` 由 distance/displacement 确定；至少必须以明确策略将其与相同行键绑定，或者在 schema 中声明并验证可重算的 feature contract。原 B04 要求“完整张量 schema”和“排序、拼接、padding 的统一行映射”，当前尚未满足，故 B04 保持 OPEN。

最小关闭条件：

- concat/padded validator 验证 `distance` 与 `displacement` 的 float64 范数关系，容差与单图契约一致；
- padded validator 显式要求 prediction、component mask、局部/实际轨道分量数组具有同一 `(B,Emax,Pmax)`；
- 对冻结 `_edge_features` 增加 row-wise feature contract，或明确把通用不可重建特征降为 opaque payload，并在构造/反序列化边界使用不可分离的完整键记录保证行绑定；
- 增加 concat/padded 的 displacement 滚动、distance 滚动、prediction 宽度加一/减一和相应行删增失败样例。

### B05：T-D10 硬输入与枚举元数据——CLOSED

修复版实际执行 16 个失败样例。独立变异确认下列对象全部被拒绝：

- 分组交集污染；
- 零边图空 `structure_id`；
- float32 cell；
- float32 fractional；
- 错误 bounds；
- 错误 candidate count；
- 错误 condition-number 元数据。

原有非有限坐标、奇异/阈值病态晶胞、非法 cutoff、越界端点和重复记录继续被拒绝；`A_-` 条件数为 `5e7` 并接受。B05 关闭。

### N01：子进程级字节确定性——CLOSED

unittest 现在通过 `subprocess.run` 两次执行 A/B CLI，比较原始 stdout 字节并检查 JSON 与退出码；错误 seed 也在子进程层检查退出码 2。本复核独立得到与 progress tracker 一致的两个 stdout 哈希。N01 关闭。

## 5. 新增与回归检查

- 新增独立问题 ID：0。额外行、几何错位和宽度漂移均属于原 B03/B04 最小关闭条件的直接对抗实例。
- B01、B02、B05、N01 未发现修复回归。
- T-D01、T-D06、T-D07、T-D08 的原通过结论未受本轮修订影响。
- 没有发现 DeepH 导入、正式数据下载、DFT 标签生成、材料体系选择或 M8 软件对象冻结。
- 依赖仍为 `numpy==2.3.5`、`scipy==1.18.0`；本复核未安装任何依赖。

## 6. 最终判定与下一步

| 问题 | 状态 |
|---|---|
| B01 | `CLOSED` |
| B02 | `CLOSED` |
| B03 | `OPEN` |
| B04 | `OPEN` |
| B05 | `CLOSED` |
| N01 | `CLOSED` |

本轮结论为 `FAIL`，剩余 `BLOCKING=2`、`NON_BLOCKING=0`。不得将 M6-07 标记为 `COMPLETED`，不得启动 M6-08。

主 agent 应只修复 B03/B04 的上述最小剩余条件。修复后必须继续由本原独立审计员对新哈希执行第二次定点复核。只有 B03/B04 均关闭、无新增问题且 A/B CLI、13 项以上 unittest、子进程字节确定性和新增对抗变异全部通过，才允许完成 M6-07 并启动 M6-08。
