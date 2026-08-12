# 阶段 E 合成表示与等变性验证包

## 1. 范围与证据边界

本目录是 M7-09 的确定性合成代码包，用于把阶段 E 已审定的表示约定、解析推导和 T-E01—T-E12 门控转化为可执行证据。实现只使用合成旋转、冻结合成图、合成轨道块和固定随机数流；它验证项目内数学与 schema 契约，不构成 DeepH 本体、正式数据、真实材料或 DFT 后端的功能测试。

M8 前仍禁止安装 DeepH/e3nn、下载正式训练数据、生成 DFT 标签，或隐含选择材料体系、DFT/数据后端、DeepH 软件对象及其实践版本。代码中的相关字段必须保持 `UNRESOLVED_M8`，并由 T-E12 强制拒绝提前选择。

目录内容如下：

- `stagee_models.py`：冻结表示、旋转、CG、Hamiltonian、消息层、局部架、时间反演、成本和 schema 原语；
- `run_experiments.py`：配置 A/B、144 点扫描和 T-E01—T-E12 规范 JSON CLI；
- `test_stagee_models.py`：17 项自动回归，包括子进程字节确定性、逐 dtype 扫描注入和 63 项强制拒绝矩阵；
- `requirements.txt`：精确固定的用户态 Python 依赖。

## 2. 固定环境与复现命令

唯一送审环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。Windows PowerShell 复现命令为：

```powershell
$python = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -m pip install -r .\05_code_exercises\stageE_synthetic_equivariance\requirements.txt
& $python -m pip check
& $python -m unittest discover -s .\05_code_exercises\stageE_synthetic_equivariance -p 'test_*.py' -v
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --config A --seed 20260809
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --config B --seed 20260810
& $python .\05_code_exercises\stageE_synthetic_equivariance\run_experiments.py --scan
```

依赖安装命令只允许安装 `requirements.txt` 中的精确版本；不得借此增加 DeepH、e3nn、ASE、pymatgen 或 DFT 软件。`--benchmark` 是配置模式的可选非规范 wall-time 测量，采用 3 次预热、7 次测量并单独报告 median/IQR；其结果不得进入确定性摘要或哈希。

## 3. 冻结配置与 CLI 合同

| 配置 | seed | dtype | 旋转数 | multiplicity | 冻结图 | 尺度 |
|---|---:|---|---:|---|---|---:|
| A | 20260809 | float64 | 64 | (3,2,2) | G_A: (N,E)=(4,8) | 1 |
| B | 20260810 | float32 | 257 | (5,4,3) | G_B: (N,E)=(7,18) | 1000 |

`--config` 与 `--scan` 互斥；配置的 seed 不允许覆盖，scan 不接受 seed 或 benchmark。非法组合和错误 seed 必须以退出码 2 终止。规范 JSON 使用排序键、紧凑分隔符并禁止数值 NaN/Infinity；同一命令在独立子进程中的 stdout 必须逐字节一致。字符串形式的失败夹具标签不属于数值 NaN，数值字段另由递归有限性检查约束。

旋转从 NumPy `PCG64` 的冻结抽样顺序生成：先抽取 `(n_R,4)` 原始四元数，完成单位化与唯一符号规范，转换成目标 dtype 的 `(n_R,3,3)` 矩阵，随后释放原始四元数。配置和扫描使用相同生命周期，不允许静默更换随机源、抽样顺序或 dtype 转换位置。

## 4. T-E01—T-E12 可执行映射

| ID | 正向证据 | 强制失败或拒绝证据 |
|---|---|---|
| T-E01 | Haar 四元数、SO(3) 正交/行列式、逆、群复合、规范符号 | 零/非有限四元数、阈值边界、反射、错误顺序、错误 seed |
| T-E02 | 标量、极向量、轴向量、二阶张量与主动/被动回构 | 转置混淆、极/轴宇称混淆 |
| T-E03 | 实 p/d 表、STF 基、正交、群律、闭合与无迹 | d 顺序、归一化和双侧作用错误 |
| T-E04 | K1/K2 幺正桥、Wigner 相似变换、点值与 coefficient 协变 | m 逆序、相位、共轭和接口方向错误 |
| T-E05 | 1×1、1×2 CG 全表、选择定则、正交/完备、intertwiner 与相位锚点 | 部分 M 相位、单系数、未同步交换相位；整通道统一相位保留等变性 |
| T-E06 | 独立正/逆 edge row 的 4×8/8×4 Hamiltonian 双侧协变、奇异值、Hermiticity、轨道与边 provenance | 只左乘、漏共轭转置、伪 payload 重哈希、端点/shift/轨道行或逆边身份漂移 |
| T-E07 | SO(3)/O(3) 极向量、轴向量、偶标量与伪标量门控 | 错误宇称类型和无确定宇称门值 |
| T-E08 | coefficient filter、CG 消息、receiver 聚合和同型混合逐层/端到端协变；provenance 冻结输入/filter 为 `[1,-1]`、输出为 `[[0,1],[1,1],[2,1]]` | 高阶逐分量非线性、错误输入/output 宇称、错误 CG 元数据、陈旧 direction provenance、边方向或行映射漂移 |
| T-E09 | 无量纲零长度/共线阈值、唯一右手局部架、4×8 回拉/推出 | 有量纲阈值、后备轴、零除、等号方向和近退化故障 |
| T-E10 | 144 点逐 case dtype 阈值、最坏旋转/ell、完整成本/数组摘要、冻结图与 edge identity | scan/config 混用、图漂移、float64 宽松阈值穿透、非有限残差、MAC/FLOP 或 total/peak 口径混淆 |
| T-E11 | 无自旋/自旋时间反演、SU(2) lift、2π/4π、独立 H/S k/-k partner、TRIM 广义本征 Kramers 接口 | 错 partner/map/mask/轨道行、漏共轭、平方符号错误、一般 k 冒充 TRIM 和 Zeeman 破缺 |
| T-E12 | dtype/rank/shape/有限性/schema/provenance/授权边界硬验证 | 实际执行 63 个唯一故障，并报告 `rejected=total=63`、异常类型和非空消息 |

T-E12 还用三个不活动 padding 探针验证 `NaN`、0 和 `1e300`。实现必须在任何 contraction、预测或 loss 之前切除 mask 外元素；三次有效输出逐元素一致，活动残差和 loss 均为 0。活动位置的非有限值仍必须拒绝。

## 5. 扫描、成本与内存口径

扫描轴为 dtype 2 种、seed 2 种、旋转数 4 种、multiplicity 倍率 3 种和尺度 3 种，共 144 个唯一 case。seed 只选择冻结图和 edge identity；其余轴不得重写图。

确定性成本字段同时给出：

- `mac_per_rotation` 与 `mac_total`；
- 只针对 contraction、按 1 MAC = 2 FLOP 换算的 `flop_total`；
- 独立统计的 receiver 聚合加法；
- 每个显式数组的 shape、dtype 与 nbytes；
- 完整物化 `array_bytes_total` 与冻结参考流式调度 `array_bytes_peak`。

运行时、解释器/BLAS 临时量和未暴露内部缓冲不纳入数组字节。冻结锚点为：

| 图 | MAC/rotation | 聚合加法/rotation | total bytes | reference peak bytes |
|---|---:|---:|---:|---:|
| G_A | 168 | 52 | 2728 | 2280 |
| G_B | 378 | 143 | 5584 | 4576 |

每个 case 独立保存 `threshold`、`pass`、`worst_rotation` 和 `worst_ell`；float64/float32 分别采用 `5e-12`/`5e-6`，等号接受，任一非有限残差在序列化前拒绝。当前 144 点规范扫描最大残差为 `1.9468769400071583e-07`，最坏 case 为 `float32-s20260809-r257-m1-a1e+03` 的 rotation 189、ell 2，case 摘要 SHA-256 为 `5317a387bfb026e53dceb31a85074d52ff520448c2fbac9649cb8013064cca7e`。

## 6. 规范 payload 与送审执行证据

以下 payload/hash 是基顺序、相位、共轭和时间反演接口的回归锚点：

| 对象 | SHA-256 |
|---|---|
| K1 复—实桥 | `347e352605a3f4f3ccb078b6cedf5c755fdc6aa3527ea41a8ea3e93d076972a2` |
| K2 复—实桥 | `5e783d9cdfe025238977f9e92d64d8b46e9a0e79eb8c9deba1af116aaafc7b82` |
| l=0 coefficient filter | `549a79b3656baa8736315f6d12f195013301c0fcdfe97bfdf3c73ecd85f58692` |
| l=1 coefficient filter | `55144adbd95056208733ab51ff2efb16789a95a855234641a4521c41fb577d06` |
| l=2 coefficient filter | `1a940f1cdcbc62b99ba56d6aa5e50619fb96c85fb0ddcc86913405cbaca97295` |
| 无自旋时间反演 | `56342db661da6f8d9cc8c3bf6e241dcb9817f42e63a33cad9af9364bcc8df6ec` |
| 自旋 1/2 时间反演 | `f8b5e9591b791a2dbd9b262736718c8b391b75de6ce720335d1ad5b8f1aff444` |
| l=1 轨道时间反演 | `230aa31fc0201b4f2d7f8981a3244049c280f75cb2c753f38f9ce9d86a250980` |
| 1×1/1×2 DLMF CG 全表 | `fd40673f73059974962cf9b8b3c9152b9af1bd28bb87028b9e4bffe797fd1a04` |

初次独立代码审计报告 `08_audits/M7_stageE_code_independent_audit.md` 判定 `FAIL` 并冻结 B01—B05。修订随后把实际 direction 与完整 provenance 绑定；对 `stageD-edge-v1` payload 作解析、规范重编码和端点/shift/轨道身份核验；按逐 case dtype 阈值判定 scan；用独立硬编码的 H/S k/-k row 取代同式自比，并执行 spinless/spin-half、2π/4π、TRIM 广义本征 Kramers；把全表常量和缺失定向故障纳入 oracle。原独立审计员已在 [`M7_stageE_code_blocking_reaudit.md`](../../08_audits/M7_stageE_code_blocking_reaudit.md) 中确认 B01—B05 全部关闭，M7-09 已完成。

2026-08-11 修订后主验证得到：17/17 unittest 通过、`pip check` 无破损依赖、错误 seed 退出码 2，A/B/scan 分别在两个真实子进程中逐字节一致。stdout SHA-256 为：

- A：`6a656a18bbfef042cbcd3049278c15fd0644f4b593d06e44a2b63c5fc78be856`；
- B：`b9e4ca3de9e671f4f9b674e40b5f62068f3a91e6ba886d4640d3b90aa6fd82d1`；
- scan：`c13944029e29ef6b47919646952a5d9bdf6a018cee3f101429fab09967982a81`。

上述结果属于主 agent 验证，不替代 M7-09 的独立代码审计；当前放行依据是原审计员定点复核给出的 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0`。该结论不授权启动 M8 或 M9 的任何外部动作。
