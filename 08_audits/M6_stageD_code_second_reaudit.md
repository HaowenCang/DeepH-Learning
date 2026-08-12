# M6-07 阶段 D 代码第二次定点复核

## 1. 复核结论

- 复核类型：原独立审计员第二次定点复核
- 复核日期：2026-08-09
- 复核基准：`M6_stageD_code_blocking_reaudit.md`
- 总结论：`FAIL`
- B03：`CLOSED`
- B04：`OPEN`
- B01/B02/B05/N01：`CLOSED，无回归`
- 剩余 `BLOCKING`：1
- 剩余 `NON_BLOCKING`：0
- 新增独立问题 ID：0；新反例归入原 B04 的“完整批 schema”关闭条件
- 是否允许完成 M6-07：否
- 是否允许启动 M6-08：否

第二次修复已经关闭第一次复核发现的全部直接穿透：edge-output 额外/缺失分量行、concat/padded 几何与特征滚动、padded prediction 宽度增减均被拒绝。B03 可以关闭。B04 仍未完全关闭，因为新加入的 `cell/cutoff` 只被作有限性和形状检查，没有执行阶段 D 的晶胞条件数、规范分数坐标、正距离和 cutoff 边界；padded node feature 也未严格限制为三维张量。独立构造的自洽但非法批对象仍能通过 validator。

## 2. 复核快照

| 文件 | SHA-256 |
|---|---|
| `08_audits/M6_stageD_code_independent_audit.md` | `0172DB26202A2D3102EABD58B911ABC83CCBB631E68C8CF7FC405ACE5312DC3E` |
| `08_audits/M6_stageD_code_blocking_reaudit.md` | `81B4081078F0830AB02A7A82E8974F9B03E245325094802CC526115239AF6FE1` |
| `05_code_exercises/stageD_synthetic_mpnn/README.md` | `D93B68A5185A85CE96751302FC2BA315014051B618E9AC9022FDBBD716919CFF` |
| `05_code_exercises/stageD_synthetic_mpnn/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/stageD_synthetic_mpnn/run_experiments.py` | `6B786D104546884C28777469C322567962AC75059CB50EC8F4451D0A5FFCE290` |
| `05_code_exercises/stageD_synthetic_mpnn/staged_models.py` | `278BBC3003CD165FC17342C7401D14066F7BDDA789DD96F54E18935E3F22CF22` |
| `05_code_exercises/stageD_synthetic_mpnn/test_staged_models.py` | `7DC73BCD1FFFFC1BE3B78DE1DF2E3A3AE37261D66000E68FF2D4F844330BAC7F` |

工作区不是 Git 仓库。本复核没有修改实现，只新增本报告。

## 3. 固定环境和自动回归

- Python 3.12.13；
- NumPy 2.3.5；
- SciPy 1.18.0；
- `pip check`：无破损依赖；
- unittest：13 项全部通过，耗时约 3.82 s；
- 错误 seed：退出码 2。

实际子进程 stdout 结果：

| 配置 | 退出码 | 字节数 | SHA-256 | 两次运行 | T-D09 失败 |
|---|---:|---:|---|---|---|
| A / 20260806 | 0 | 11625 | `56FCA92A901A32752B021334477FD8C42E0D5AE2D6C5EE4397ECBF5A4509955D` | 字节一致 | 30/30 |
| B / 20260817 | 0 | 11682 | `261F74EDB35E0F7702B1BE7288B404EE3CC5717555EA14D36D9A22D4BE4914D2` | 字节一致 | 30/30 |

两配置均为 `overall_pass=true`。T-D03 测试 MSE 保持 `0.00194424` 与 `0.00501318`，低于冻结 `0.02`；B01 五类梯度故障、B02 生成式/预算、B05 十六个硬输入失败和 N01 子进程门控均未回归。

## 4. B03 定点复核：CLOSED

`validate_edge_output` 现在把 provenance 的 `mask.shape` 作为唯一 `(E,Pmax)` 形状，并分别要求：

- receiver/sender 为 `(E,)`；
- shift 为 `(E,3)`；
- edge ID 为 `(E,)`；
- prediction、mask、局部轨道下标和实际轨道 ID 均为同一 `(E,Pmax)`；
- block shape 为 `(E,2)`；
- 完整键与原图形成集合双射，并逐键核对 edge ID 与 provenance。

第一次复核的“端点键仍为 E 行，但 prediction/mask/轨道分量追加第 E+1 行”变异现在抛出 `ValueError`；相应删行也被拒绝。T-D04/T-D05 的完整键映射、边行倒序和换胞双射继续通过。B03 最小关闭条件全部满足，B03 关闭。

## 5. B04 定点复核：OPEN

### 5.1 已关闭的第一次穿透

修复版为 concat/padded 批增加：

- 逐图 cell 和 cutoff；
- `distance-displacement-prefix-zero-pad-v1` 特征契约；
- 由 fractional、receiver、sender、shift 和 cell 重算 displacement；
- 由 displacement 重算 distance；
- 由 distance/displacement 前缀和零 padding 重算 edge feature；
- padded prediction、component mask 和轨道分量的统一 `(B,Emax,Pmax)`。

独立重放结果：

| 变异 | concat | padded |
|---|---|---|
| displacement 行滚动 | 拒绝 | 拒绝 |
| distance 行滚动 | 拒绝 | 拒绝 |
| edge feature 行滚动 | 拒绝 | 拒绝 |
| prediction 宽度加一 | 不适用 | 拒绝 |

prediction 宽度减一也由项目失败矩阵拒绝。原先的负 graph ID、计数错配、跨图边和轨道行错位继续拒绝；NaN padding 仍在读取前切除。以上修复有效。

### 5.2 仍可穿透的完整 schema 反例

独立对抗样例得到：

| 非法对象 | validator 结果 | 违反的冻结条件 |
|---|---|---|
| concat cutoff 全改为 `1e-12`，而现有边距离远大于 cutoff | 接受 | 所有边必须满足 `0<r<=r_c` |
| padded cutoff 全改为 `1e-12` | 接受 | 同上 |
| concat cell 全改为奇异零矩阵，并同步把 active displacement/distance/edge feature 改为零 | 接受 | `sigma_min>0`、`kappa_2<1e8`、正边距离 |
| padded 执行同一奇异零晶胞自洽变异 | 接受 | 同上 |
| concat 某 fractional 分量加 1，并按新值重算几何与特征 | 接受 | 序列化 fractional 必须在 `[0,1)` |
| padded node_features 从 `(B,Nmax,d)` 改为 `(B,Nmax,d,1)` | 接受 | 精确张量 shape 契约 |

原因是 concat/padded validator 目前只检查 cell/cutoff 的 dtype、shape、有限性和 cutoff 正值，没有逐图调用 `validate_cell`，没有检查 active distance 的正性和 cutoff 上界，也没有检查 fractional 的规范区间。padded `node_features` 只比较前两维，未要求 `ndim==3`。

这些不是新的路线要求，而是第一次报告 B04 最小关闭条件中“覆盖第 12—14 章冻结字段、精确 dtype/shape”和当前修复自行引入的 cell/cutoff 语义。因此 B04 保持 OPEN。

### 5.3 最小剩余关闭条件

- concat/padded 对每个 cell 执行与单图一致的 `validate_cell`，拒绝奇异或 `kappa_2>=1e8`；
- 对每个 cutoff 执行统一 cutoff validator，并断言每条 active edge 满足 `0<distance<=cutoff[graph]`；
- concat/padded fractional 必须是 float64、最后一维 3、active 值有限且位于 `[0,1)`；
- padded node_features 必须严格为 `float64[B,Nmax,d]`；其他节点/边张量也应显式断言完整 ndim，而不只比较 shape 前缀；
- 将上述六类变异加入 CLI expected-failure 和 unittest；
- 保持 NaN 只允许出现在 inactive padding 行，不能借严格 shape 修复破坏既有 padding 切除测试。

## 6. 回归、授权和最终判定

| 问题 | 状态 |
|---|---|
| B01 | `CLOSED，无回归` |
| B02 | `CLOSED，无回归` |
| B03 | `CLOSED` |
| B04 | `OPEN` |
| B05 | `CLOSED，无回归` |
| N01 | `CLOSED，无回归` |

未发现 DeepH 安装或导入、正式数据下载、DFT 标签生成、材料体系选择或 M8 软件对象冻结。本复核未安装依赖。

最终结论为 `FAIL`，剩余 `BLOCKING=1`、`NON_BLOCKING=0`。不得完成 M6-07，不得启动 M6-08。

主 agent 应只修复 B04 的第 5.3 节。修复后仍须由本原独立审计员执行第三次定点复核；只有剩余和新增问题均为零，才允许完成 M6-07 并启动 M6-08。
