# M7-09 阶段 E 合成代码包第一次定点复核

## 1. 复核结论

- 复核日期：2026-08-11
- 原审计报告：`08_audits/M7_stageE_code_independent_audit.md`
- 原稳定问题：M7E-CODE-B01—B05
- 复核性质：同一独立审计员第一次定点复核
- 最终结论：**PASS**
- `BLOCKING=0`
- `NON_BLOCKING=0`
- 原问题状态：B01 `CLOSED`、B02 `CLOSED`、B03 `CLOSED`、B04 `CLOSED`、B05 `CLOSED`
- 新增问题：0
- M7-09 完成许可：**允许标记为 `COMPLETED`**

本复核未修改代码、教材、推导、工作包或进度台账，也未启动 M7-10。主 agent 可依据本报告更新 M7-09 状态，并按既定依赖处理后续阶段。

## 2. 被审修订与 SHA-256

| 文件 | SHA-256 |
|---|---|
| `05_code_exercises/stageE_synthetic_equivariance/stagee_models.py` | `16CB3A0DFC34417D11186F3512919D29519315134F596BEA32D60EE722D9E114` |
| `05_code_exercises/stageE_synthetic_equivariance/run_experiments.py` | `66B203E7169BBA1A166743C2F04BC997C09D93859FF0AEE39263A7C98682A8A0` |
| `05_code_exercises/stageE_synthetic_equivariance/test_stagee_models.py` | `A50FDB2430DA5ECE4A6086074BDEC799397AC1B3303CB41618EE665322720715` |
| `05_code_exercises/stageE_synthetic_equivariance/README.md` | `42A98FEDA0E09D602C8CDFAA9F39F9A71B58E49DD4FD7802AB8066BD8D289768` |
| `05_code_exercises/stageE_synthetic_equivariance/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `08_audits/M7_stageE_code_independent_audit.md` | `134FA492B75493AC019EFA4ACD148B72B1AB72CC6BFE1FAA4F45C3D7EE2383C8` |
| `08_audits/M7_stageE_work_package.md` | `468E3DF5AC55EA3F57B9E5A37642396A7344C5827B5EAFDE01408E33C8BBE98D` |
| `03_textbook/stageE_representation_conventions.md` | `139BB534474A6D585CD5A31D6DF08B2DEE74F9E855929786D075C81FB34579BC` |
| `04_derivations/stageE/README.md` | `A65BC7199E9852A49408E31CB1E53BD0F8A3AA4F329DCB931DC1E0E8B016CCFB` |

送审核心 SHA 与实际文件逐项一致。

## 3. 固定环境与全量回归

固定解释器报告 Python 3.12.13；独立导入得到 NumPy 2.3.5、SciPy 1.18.0。`pip check` 返回 `No broken requirements found.`，`requirements.txt` 仍只包含 `numpy==2.3.5` 与 `scipy==1.18.0`。

独立执行：

```text
python -m unittest discover -s 05_code_exercises/stageE_synthetic_equivariance -p test_*.py -v
```

结果为 17/17 `OK`。其中新增回归实际覆盖逐 dtype scan 注入、冻结定向故障、Hamiltonian/message provenance 以及独立 H/S 时间反演 partner row，不是仅检查既有摘要字段。

A、B、scan 分别在两个真实子进程中执行两次，stdout 字节完全一致：

| 模式 | stdout SHA-256 | 字节数 | 状态 |
|---|---|---:|---|
| config A | `18702D7746405D39A6CC3997069FBCD3A31E60F440C64EA46903EA5908787B64` | 21075 | `overall_pass=true` |
| config B | `A8EEA1E0F0A76E365ED709B906645BC2744F3B8CC84EF2061D8FE5C82BD1285B` | 21129 | `overall_pass=true` |
| scan | `C13944029E29EF6B47919646952A5D9BDF6A018CEE3F101429FAB09967982A81` | 62206 | `pass=true` |

三项哈希均与送审记录一致。错误 config seed、config/scan 混用、scan 加 seed 或 benchmark 仍以退出码 2 拒绝；规范摘要不含 wall-time、绝对路径、进程 ID或数值 NaN/Infinity。

## 4. 稳定问题逐项复核

### M7E-CODE-B01：`CLOSED`

生产路径 `message_layer()` 现在调用带实际 `directions` 参数的完整 provenance validator。该 validator 同时核对 graph 字段、edge payload 的规范解析、edge ID、receiver、sender、shift、basis、m 顺序、CG 全表 hash、输出 irrep 顺序、方向 dtype/shape/有限性，并要求实际方向数组与 provenance 中方向逐元素相等。

独立主动重放结果：

| 穿透 | 结果 | 异常 |
|---|---|---|
| 保持旧 provenance、把 directions 整体反号 | REJECT | `ValueError: message directions are stale or row-misaligned relative to provenance` |
| 保持旧 provenance、循环置换 direction rows | REJECT | 同上 |
| 把 `cg_table_sha256` 改为伪 hash | REJECT | `ValueError: message provenance identity is inconsistent` |
| 把 `output_irreps` 改为 `[0,2,1]` | REJECT | 同上 |

T-E08 的正确 coefficient-filter/CG 消息层仍通过 A/B；反向边方向作为带自身一致 provenance 的定向错误保留非零残差，而陈旧/错行 provenance 在 kernel 前硬拒绝。原最小关闭条件全部满足。

### M7E-CODE-B02：`CLOSED`

Hamiltonian row 现在显式包含 `structure_id`、receiver、sender、shift、规范 payload、hash、左右 shell 和 actual orbital identity。`parse_edge_payload()` 要求合法 JSON、`stageD-edge-v1`、严格字段数、整数端点/shift及规范字节重编码；row validator 再把解析结果与行字段、冻结正/逆教学 edge 和左右轨道顺序绑定。

独立主动重放结果：

- 任意非 JSON payload 重哈希：拒绝；
- 合法重编码但 receiver 改为 2：拒绝；
- 合法重编码但 shift 改为 `(1,0,0)`：拒绝；
- 逆 edge row 未同步交换端点：拒绝；
- 轨道顺序、partial mask、dtype 和 hash 漂移：63 项矩阵中分别实际拒绝。

正向复算中，forward row 为 0→1、shape 4×8，reverse row 为 1→0、shape 8×4；二者 block 不共享内存，逐元素满足 `H_reverse = H_forward.T`，旋转后逆边/Hermiticity 残差在 A/B 阈值内，左右 shell、轨道和端点身份同步。原最小关闭条件全部满足。

### M7E-CODE-B03：`CLOSED`

`run_scan()` 现在对每个 case 独立写出 `threshold`、`pass`、`worst_rotation`、`worst_ell`，并要求所有 144 个 case 各自通过。非有限残差在进入摘要前硬拒绝。

独立注入结果：

| 注入 | 结果 |
|---|---|
| float64=`1e-6`、float32=0 | scan `pass=false`；72/72 float64 均失败，72/72 float32 均通过 |
| 每个 dtype 恰等于自身阈值 | 144/144 通过 |
| NaN | `ValueError: scan residual must be finite` |
| `+Infinity` | 同上 |
| `-Infinity` | 同上 |

当前真实 scan 为 144 个唯一 case，最大残差 `1.9468769400071583e-07`，最坏 case `float32-s20260809-r257-m1-a1e+03`，rotation 189、ell 2；case digest 为 `5317A387BFB026E53DCEB31A85074D52FF520448C2FBAC9649CB8013064CCA7E`。原最小关闭条件全部满足。

### M7E-CODE-B04：`CLOSED`

T-E11 不再把即时定义的 k partner 与同一表达式自比。`make_time_reversal_pair()` 物化独立 H(k)、H(-k)、S(k)、S(-k) 数组；validator 分别核验 Hermiticity、S 正定、k/-k、partner ID/map、完整 mask、轨道行和两类时间反演关系。

独立复算得到：

- spinless `Theta=K` 的平方与反线性残差均为 0；
- spin-half `Theta^2=-I`、向量二次作用与反线性残差均为 0；
- 2pi lift 相对 `-I`、4pi lift 相对 `I` 的残差均为 0；
- 独立 H partner、S partner 和四矩阵 Hermiticity 残差均为 0；
- TRIM 广义本征值按 Kramers 成对，pair gap、S-内积正交和 partner 广义本征方程残差均为 0；
- 一般 k 夹具显式满足 k 不等于 -k，不把一般 k 冒充同 fiber 简并；
- Zeeman 破缺、漏共轭、错误 K-dagger 路线和错误反线性均给出不低于 `1e-4` 的定向残差。

partner ID、partner map、partial mask、轨道行、H 漏共轭和 S 错 partner 六类变异均由生产 validator 拒绝。H/S row 各自不共享内存。运行数组摘要逐名报告 kpoint、partner map、mask、J、H/S 行、临时 conjugate 和输出的 shape/dtype/nbytes；A/B total 分别为 644/332 bytes。原最小关闭条件全部满足。

### M7E-CODE-B05：`CLOSED`

1×1/1×2 CG 完整表的实际规范 JSON hash 与冻结常量均为 `FD40673F73059974962CF9B8B3C9152B9AF1BD28BB87028B9E4BFFE797FD1A04`。A/B 同时保持全表正交/完备、intertwiner、三个 1×1 锚点和六个 1×2 锚点。整通道统一相位仍保持 intertwiner；部分 M 相位、单系数和输入轴互换漏交换相位分别得到明确非零失败量。

缺失的冻结定向故障现均进入生产路径或显式数值 oracle：

- T-E01：旋转/四元数 NaN、Infinity、非规范符号硬拒绝；错误复合顺序残差约 `0.192204`；
- T-E03：漏 STF 归一化由 `validate_stf_basis()` 拒绝；
- T-E04：Condon--Shortley 局部相位残差约 `0.732268`；把 Euler 三元组当旋转矩阵硬拒绝；
- T-E05：冻结全表 hash、输入轴交换漏相位、部分 M 和单系数故障均执行；
- T-E08：错误 CG hash/通道元数据、陈旧 direction 和 row permutation 均硬拒绝；
- T-E12：六个 M8 字段、B01—B04 穿透和上述 schema 故障均进入实际拒绝矩阵。

T-E12 在 A/B 均得到 `rejected=total=63`、唯一名称 63/63；每项均有异常类型和非空消息。NaN、0、`1e300` 三个不活动 padding 探针的活动输出最大残差为 0，三个 masked loss 均为 0。原最小关闭条件全部满足。

## 5. T-E01—T-E12 回归判定

| ID | 复核判定 | 核心证据 |
|---|---|---|
| T-E01 | PASS | A/B Haar 旋转、SO(3)、逆、复合、规范符号、阈值与非有限/错序故障均通过。 |
| T-E02 | PASS | 标量、极/轴向量、二阶张量与主动/被动正反例无回归。 |
| T-E03 | PASS | p/d 正交、群律、STF 闭合/无迹及漏归一化拒绝通过。 |
| T-E04 | PASS | K1/K2、Wigner 相似、点值/系数协变、m 顺序、局部相位和接口错误通过。 |
| T-E05 | PASS | 1×1/1×2 全表 hash、锚点、正交/完备、intertwiner、合法/非法相位与交换关系通过。 |
| T-E06 | PASS | 独立正逆 row、4×8/8×4 双侧协变、Hermiticity、实复路线与完整身份拒绝通过。 |
| T-E07 | PASS | O(3) 极/轴分类、宇称和坏门值无回归。 |
| T-E08 | PASS | 消息层逐层/端到端协变、coefficient filter、CG 元数据与方向 provenance 拒绝通过。 |
| T-E09 | PASS | 两 dtype 局部架定义域、阈值、等号、回拉与近退化故障无回归。 |
| T-E10 | PASS | 逐 dtype 144 点、worst rotation/ell、非有限拒绝、成本和数组锚点通过。 |
| T-E11 | PASS | spinless/spin-half、2pi/4pi、独立 H/S partner、TRIM 广义本征 Kramers 与破缺样例通过。 |
| T-E12 | PASS | 63/63 实际拒绝、完整消息、三 padding 与六个 M8 sentinel 通过。 |

## 6. payload、成本、格式与边界无回归

独立复算的 K1/K2、三个 coefficient filter、三个时间反演 payload/hash 与冻结值逐项一致。reference kernel 的 G_A/G_B 锚点仍分别为：

| 图 | MAC/rotation | 聚合加法/rotation | total bytes | reference peak bytes |
|---|---:|---:|---:|---:|
| G_A | 168 | 52 | 2728 | 2280 |
| G_B | 378 | 143 | 5584 | 4576 |

README 在 Pandoc 3.6.4 下以 `markdown+tex_math_dollars+raw_tex -> html5 --mathml --fail-if-warnings` 严格渲染成功。代码包五个文本文件均无 UTF-8 BOM，非法控制字符为 0；README 的 17 unittest、63 failures、scan digest、最坏 rotation/ell、stdout hashes 与本次独立执行一致。

依赖和 import 扫描未发现 DeepH、e3nn、ASE、pymatgen 或 DFT 软件；没有正式训练数据和 DFT 标签。A/B 的 material、DFT backend、data backend、DeepH software object、training budget 和 advanced physics scope 六个字段仍全部为 `UNRESOLVED_M8`，对应六类提前选择在 T-E12 中实际拒绝。因此未发现 M8/M9 授权边界穿透。

## 7. 最终许可

M7E-CODE-B01—B05 均满足原报告的全部最小关闭条件，修订没有引入新的阻塞或非阻塞问题。M7-09 可由主 agent 标记为 `COMPLETED`。本结论只关闭 M7-09 代码门控，不扩大 M8/M9 权限，也不授权安装 DeepH/e3nn、下载正式数据或生成 DFT 标签。

