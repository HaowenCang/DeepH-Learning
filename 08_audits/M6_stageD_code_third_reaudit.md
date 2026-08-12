# M6-07 阶段 D 代码第三次定点复核

## 1. 复核结论

- 复核类型：原独立审计员第三次定点复核
- 复核日期：2026-08-09
- 复核基准：`M6_stageD_code_second_reaudit.md`
- 总结论：`PASS`
- B04：`CLOSED`
- B01/B02/B03/B05/N01：`CLOSED，无回归`
- 剩余 `BLOCKING`：0
- 剩余 `NON_BLOCKING`：0
- 新增问题：0
- 是否允许完成 M6-07：是
- 是否允许启动 M6-08：是

本次定点复核独立重放了第二次报告中仍能穿透 validator 的六个 B04 反例。修复后的 concat/padded validator 均拒绝小 cutoff、奇异晶胞、自洽重算后的非规范分数坐标以及 rank-4 padded node feature。逐图晶胞与 cutoff 验证、活动边距离边界、规范分数坐标和完整张量 ndim/shape 已形成实际执行的验证路径，而不只是文档声明。NaN 与 `1e300` 非活动 padding 在聚合、归一化和 loss 前被活动切片排除；两种 padding 内容得到逐图预测和 loss 完全一致的结果。因此 B04 的最小关闭条件已经全部满足。

## 2. 复核快照

| 文件 | SHA-256 |
|---|---|
| `08_audits/M6_stageD_code_independent_audit.md` | `0172DB26202A2D3102EABD58B911ABC83CCBB631E68C8CF7FC405ACE5312DC3E` |
| `08_audits/M6_stageD_code_blocking_reaudit.md` | `81B4081078F0830AB02A7A82E8974F9B03E245325094802CC526115239AF6FE1` |
| `08_audits/M6_stageD_code_second_reaudit.md` | `D00242DBDF8BD2DBD2DC5652576B5771448B7CE58C9C540D82CDF60C96219197` |
| `05_code_exercises/stageD_synthetic_mpnn/README.md` | `A02493AEFE386C9E7823C5A8AA0C36EFC3C4F39B68823D6C87B350070FF398B8` |
| `05_code_exercises/stageD_synthetic_mpnn/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/stageD_synthetic_mpnn/run_experiments.py` | `32B0B8F725B8695C182D3EEA500D24708B240D74F95B2AB2AE8FFC73CFA44149` |
| `05_code_exercises/stageD_synthetic_mpnn/staged_models.py` | `B640F81C2DED530C53A42AB5D707685DBDD6A6C872687518C3CAF2C49739DDD5` |
| `05_code_exercises/stageD_synthetic_mpnn/test_staged_models.py` | `611926403A3819DECFAD29C705AF696B0BA0EBDD3FC185549587CBE7B868F403` |

工作区不是 Git 仓库。本复核没有修改任何实现文件，只创建本报告。

## 3. 固定环境与复现命令

固定解释器为：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

环境结果：Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`python -m pip check` 返回 `No broken requirements found.`。本次复核未安装依赖。

执行命令：

```powershell
& $py -m unittest discover -s .\05_code_exercises\stageD_synthetic_mpnn -p 'test_*.py' -v
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config A --seed 20260806
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config B --seed 20260817
& $py .\05_code_exercises\stageD_synthetic_mpnn\run_experiments.py --format json --config A --seed 20260817
```

unittest 共 13 项，全部通过，独立运行耗时约 5.96 s。A、B 两配置分别启动两个新子进程，直接比较原始 stdout 字节：

| 配置 | 两次退出码 | 字节数 | SHA-256 | 字节确定性 | `overall_pass` | T-D09 |
|---|---|---:|---|---|---|---|
| A / 20260806 | 0 / 0 | 12316 | `2F45DC8C53C1E1D968B3F4633CCC8590540AB8E08667A340054F15F9F3CCA6EE` | 完全一致 | true | 36/36 |
| B / 20260817 | 0 / 0 | 12373 | `88BF70A4218E2B10C8410644B7B899ECF50A6F6993E83E93C496450069693BD6` | 完全一致 | true | 36/36 |

错误组合 `config=A, seed=20260817` 的退出码为 2，stdout 为 0 字节，stderr 明确报告配置 A 要求 seed 20260806。

## 4. B04 定点复核：CLOSED

### 4.1 六个原穿透反例

独立脚本从 `_main_graph()` 和 `_multi_graph()` 重新构造 concat/padded 批，并在不调用项目 expected-failure 包装器的条件下直接调用 validator。结果如下：

| 第二次报告中的非法对象 | 独立结果 | 主要拒绝依据 |
|---|---|---|
| concat cutoff 全改为 `1e-12` | 拒绝 | 活动边距离超过所属图 cutoff |
| padded cutoff 全改为 `1e-12` | 拒绝 | 活动边距离超过所属图 cutoff |
| concat cell 改为奇异零矩阵，且 displacement/distance/feature 同步改为零 | 拒绝 | `validate_cell` 判定晶胞奇异 |
| padded 执行同一自洽奇异晶胞变异 | 拒绝 | `validate_cell` 判定晶胞奇异 |
| concat fractional 第一分量整体加 1，并由完整键重算 displacement、distance 和 feature | 拒绝 | fractional 不在规范域 `[0,1)` |
| padded node feature 从 `(B,Nmax,d)` 扩为 `(B,Nmax,d,1)` | 拒绝 | node feature 必须严格为三维张量 |

代码检查与反例共同表明：concat/padded 均逐图调用统一的 `validate_cell` 和 `validate_cutoff`；活动边执行 `0 < distance <= cutoff[graph]`；fractional 必须为 float64、完整 shape 且活动值位于 `[0,1)`；padded fractional、node feature、displacement、distance、edge feature、prediction、component mask 和轨道分量均执行完整 ndim/shape 约束。另行扩维 fractional、edge feature、prediction、component mask 和 orbital index 的五个对抗样例也全部被拒绝。

### 4.2 padding 读取边界

基准 padded 批保留生成器写入的 inactive NaN。独立变异将 inactive node feature、fractional、edge feature、displacement、distance 和 prediction 改为绝对值 `1e300`，并将 inactive target 改为 `-1e300`。两批都通过 schema validator；分别调用 `forward_padded_batch` 后得到：

- 逐图 prediction 最大绝对差：`0.0`；
- 基准 losses：`[0.07591655170156028, 0.09839822706278745]`；
- 巨值 padding losses：`[0.07591655170156028, 0.09839822706278745]`；
- 两组 normalized-node-mean 指标逐项一致。

这些结果验证了非活动 padding 在节点归一化、消息聚合、预测和 masked loss 之前即由 `:node_count`、`:edge_count` 活动切片切除。严格 shape 修复没有破坏 NaN padding 契约，也没有使巨值 padding 污染数值路径。

### 4.3 项目失败矩阵

T-D09 的冻结 expected-failure 数量为 36，A、B 两配置均实际捕获 36 项。其中新增六项为：

- `concat_cutoff_too_small`；
- `padded_cutoff_too_small`；
- `concat_singular_cell`；
- `padded_singular_cell`；
- `concat_noncanonical_fractional`；
- `padded_rank4_node_features`。

相应 unittest 同时断言 expected-failure 数量和关键失败名称。未发现仅增加计数而未执行变异、复用旧异常或吞掉“意外接受”的情形。

## 5. 既有问题无回归

| 问题 | 状态 | 独立复核证据 |
|---|---|---|
| B01 | `CLOSED，无回归` | T-D02 全参数有限差分最大相对误差 `1.26615e-10`；五类故障均被检测，padding gradient 最大绝对值为 0 |
| B02 | `CLOSED，无回归` | A/B 的生成式、分组、冻结 MPNN 结构与训练预算继续实际输出；测试 MSE 分别为 `0.0019442386`、`0.0050131762`，均低于预先冻结的 `0.02` |
| B03 | `CLOSED，无回归` | edge-output 额外/缺失行、concat/padded 几何与 feature 滚动、prediction 宽度增减等原反例仍在 36 项矩阵中逐项拒绝；T-D04/T-D05 继续通过 |
| B04 | `CLOSED` | 第 4 节六个原穿透、五个相邻扩维反例和 padding 数值隔离全部通过复核 |
| B05 | `CLOSED，无回归` | T-D10 的 16/16 硬输入失败均捕获，含分组污染、空 structure ID、float32 核心 schema 和枚举元数据不一致 |
| N01 | `CLOSED，无回归` | unittest 的 CLI 子进程门控通过；本次另行得到 A/B 原始 stdout 字节确定性和错误 seed 退出码 2 |

## 6. 授权边界与最终判定

代码和测试扫描只发现显式保持边界的状态字段与断言。没有 DeepH 安装或导入、正式训练数据下载、DFT 标签生成、材料体系选择，亦未冻结 DFT/数据后端或 M8 软件对象。本复核没有执行任何 M8/M9 外部动作。

最终结论为 `PASS`，`BLOCKING=0`、`NON_BLOCKING=0`、新增问题 0。允许将 M6-07 标记为完成，并允许启动 M6-08。该结论仅覆盖本报告所列快照；后续实现文件若发生变化，应重新确认审计有效性。
