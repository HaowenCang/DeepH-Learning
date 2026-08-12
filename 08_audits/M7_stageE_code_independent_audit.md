# M7-09 阶段 E 合成代码包正式独立审计

## 1. 审计身份、范围与结论

- 审计日期：2026-08-11
- 审计对象：M7-09 阶段 E 合成表示、等变层、自动测试与失败矩阵
- 审计性质：正式独立代码审计；审计员未修改被审代码、教材、推导、工作包或进度台账
- 固定运行时：Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0
- 最终结论：**FAIL**
- `BLOCKING=5`
- `NON_BLOCKING=0`
- M7-09 完成许可：**不允许**
- 后续阶段许可：**不得启动 M7-10**

现有包的正确基准对象能够复现：14/14 unittest 通过，A/B 与 144 点扫描均生成字节确定的规范 JSON，38 个已列故障确实被逐项执行并拒绝，规范 payload/hash、成本锚点和 padding 三探针也与材料一致。然而，主动变异证明消息方向 provenance、Hamiltonian edge identity 和逐 dtype 扫描阈值存在可穿透路径；T-E11 的 Hamiltonian k-pair 检查是同一表达式与自身比较，且若干冻结强制失败入口没有进入可执行 oracle。因此，现有“全部 T-E 通过”不能支持 M7-09 零问题门控。

## 2. 被审对象与 SHA-256

### 2.1 代码包

| 文件 | SHA-256 |
|---|---|
| `05_code_exercises/stageE_synthetic_equivariance/stagee_models.py` | `552FB76D770A258D361E7E5425A832D4624C02195C0521A852A295EB8920CCC7` |
| `05_code_exercises/stageE_synthetic_equivariance/run_experiments.py` | `E40FADF1BA7245825F3819CDEBB36FEDE8084C7247CCDF00CBACB569B4CF0C46` |
| `05_code_exercises/stageE_synthetic_equivariance/test_stagee_models.py` | `334DA99C909D1121702D6A07690E8987852656F1FFD2E8F19DEA19792CE8082D` |
| `05_code_exercises/stageE_synthetic_equivariance/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/stageE_synthetic_equivariance/README.md` | `8FD2D991B23E5776AFC43EE92BF7431896935D8F8F87C3D19CF23CD98FFFFA8F` |

### 2.2 冻结合同与推导

| 文件 | SHA-256 |
|---|---|
| `08_audits/M7_stageE_work_package.md` | `607BD119A8C8B51C30D3E41D883497DB077BBE78F5F2F27BBE8009EB810B52C6` |
| `03_textbook/stageE_representation_conventions.md` | `139BB534474A6D585CD5A31D6DF08B2DEE74F9E855929786D075C81FB34579BC` |
| `04_derivations/stageE/README.md` | `A65BC7199E9852A49408E31CB1E53BD0F8A3AA4F329DCB931DC1E0E8B016CCFB` |
| `04_derivations/stageE/15_group_actions_equivariance.md` | `914FAEBC4C8B36C37EE647A42B35832682BE4A866834CB7F7EBA9A19696F3DB9` |
| `04_derivations/stageE/16_real_spd_representations.md` | `EE59FC78011C45691345D4C7D83651446582D858F83522AD055CFE77C851A23F` |
| `04_derivations/stageE/17_spherical_harmonics_wigner.md` | `0FE372A2AD42E60374F5FADEFCA30CADFA9B8FA904CAE22544419C9C9AA55179` |
| `04_derivations/stageE/18_tensor_products_clebsch_gordan.md` | `645BA9326EDFACEC64B276F9029D86C89E63F2E71900DC47CC67121B29E7120A` |
| `04_derivations/stageE/19_equivariant_graph_hamiltonian.md` | `E021C84430750F1E3B857258BD0388AEB8D990AB60CF2D4DDF4BD98E41183F2B` |
| `04_derivations/stageE/20_spin_time_reversal_complex.md` | `E3397B367E8AE477B2026AA6935240FC811C458AAAEEBB435621904FA337BE96` |

## 3. 独立执行证据

### 3.1 固定环境、回归与 CLI

固定解释器报告 Python 3.12.13；独立导入得到 NumPy 2.3.5、SciPy 1.18.0，`pip check` 返回 `No broken requirements found.`。`requirements.txt` 仅固定 `numpy==2.3.5` 与 `scipy==1.18.0`。

`python -m unittest discover -s 05_code_exercises/stageE_synthetic_equivariance -p test_*.py -v` 独立执行 14 项，结果为 14/14 `OK`。这只能说明当前回归套件内部通过，不能消除第 5 节主动穿透。

A、B、scan 分别在两个真实子进程中执行两次，stdout 字节完全一致：

| 模式 | stdout SHA-256 | 字节数 | 报告状态 |
|---|---|---:|---|
| config A | `AD66BD4B66AEB95A08701C45EE12BE84B8FCDC749045E4DE5866A50942DC9A03` | 13975 | `overall_pass=true` |
| config B | `2275F848AFB33917EF4EB0DAE7BD44AF7AFB1FF3D097FFBF9C9587ADDEA76EAC` | 14037 | `overall_pass=true` |
| scan | `4B5E51D5E0D36BAF6F24AFDBE7FCDD0A1ADBB8EC95D58CCA4EC69A09BE50AC46` | 53013 | `pass=true` |

错误 config seed、scan 加 seed、config 与 scan 同时提交、scan 加 benchmark 均以退出码 2 拒绝。规范摘要未出现 wall-time、绝对路径、进程 ID 或数值 NaN/Infinity。

### 3.2 A/B、144 点、成本与数组锚点

独立执行得到 144 个唯一 case，最大残差为 `1.9468769400071583e-07`，最坏 case 为 `float32-s20260809-r257-m1-a1e+03`，case 摘要 SHA-256 为 `18F72620BBB33D03922B0BD74ADE76E057C21D701B84F1EDFA3EB79AA44D8650`。A 配置 reference equivariance 最大残差为 `2.540796777430829e-16`；B 配置为 `1.2969077369289507e-07`，均低于相应 dtype 阈值。

从图入度、contraction shape 和实际 `nbytes` 独立重算得到：

| 图 | MAC/rotation | 聚合加法/rotation | total bytes | reference peak bytes |
|---|---:|---:|---:|---:|
| G_A | 168 | 52 | 2728 | 2280 |
| G_B | 378 | 143 | 5584 | 4576 |

这些正确基准值不能掩盖 `run_scan()` 对所有 dtype 统一使用 float32 阈值的问题，见 M7E-CODE-B03。

### 3.3 规范 payload/hash 与 padding

独立复算得到：K1 `347E3526...76972A2`、K2 `5E783D9C...F7B82`；三个 coefficient filter 依次为 `549A79B3...F58692`、`55144ADB...77D06`、`1A940F1C...97295`；无自旋、自旋 1/2、轨道 l=1 时间反演依次为 `56342DB6...DF6EC`、`F8B5E959...AFF444`、`230AA31F...250980`。完整值与 README 和 unittest 冻结值一致。

T-E12 的 38 个已列故障全部实际执行，`rejected=total=38`，名称 38/38 唯一，异常类型均来自真实 validator 调用。`NaN`、0、`1e300` 三个不活动 padding 探针的活动输出最大残差为 0，三个 masked loss 均为 0。该结果证明现有 38 项不是只列预期异常；但它不证明失败矩阵覆盖了冻结合同要求的全部故障，见 M7E-CODE-B05。

### 3.4 README、依赖和授权边界

README 在 Pandoc 3.6.4 下以 `markdown+tex_math_dollars+raw_tex -> html5 --mathml --fail-if-warnings` 严格渲染成功；UTF-8 BOM 为否，非法控制字符为 0。复现命令与实际固定解释器一致。

代码包没有导入 DeepH、e3nn、ASE、pymatgen 或 DFT 软件，也未接触正式训练数据和 DFT 标签。A/B case 的六个 M8 决策字段均保持 `UNRESOLVED_M8`。因此，本审计未发现 M8/M9 授权边界实际越界。

## 4. 逐 T-E 判定

| ID | 判定 | 独立依据 |
|---|---|---|
| T-E01 | **FAIL** | A/B 旋转正交、行列式、逆、正确复合及阈值两侧通过；但未执行 NaN/Infinity 四元数/旋转、错误复合顺序和规范四元数符号的冻结失败/序列化 oracle，见 B05。 |
| T-E02 | PASS | 标量、距离、二阶张量、主动/被动回构和极/轴向量定向失败可复现。 |
| T-E03 | **FAIL** | 正确 STF Gram、无迹、对称、p/d 正交与群律通过；存在顺序和方向故障，但未执行冻结的漏归一化故障，见 B05。 |
| T-E04 | **FAIL** | K1/K2、相似变换、点值/系数协变和 m 逆序故障通过；未执行 Condon--Shortley 局部相位与错误 Euler 接口故障，见 B05。 |
| T-E05 | **FAIL** | 1x1、1x2 正交/完备、锚点、部分 M 相位与单系数故障通过；全表只由被审实现自算后哈希，未与冻结 DLMF 全表 hash/常量逐项比对，也未执行输入轴互换未施加交换相位，见 B05。 |
| T-E06 | **FAIL** | 4x8 双侧实/复路线、奇异值和构造出的逆转置关系数值通过；Hamiltonian edge payload 可伪造后重哈希通过，且没有独立逆边 identity/Hermiticity row oracle，见 B02。 |
| T-E07 | PASS | O(3) 极/轴分类、宇称乘积与伪标量坏门值的定向残差满足合同。 |
| T-E08 | **FAIL** | 正确 coefficient filter 消息层等变性通过；计算所用 `directions` 未绑定 provenance，陈旧 provenance 可被接受且改变输出，错误 CG 通道也未进入故障矩阵，见 B01/B05。 |
| T-E09 | PASS | 两 dtype 的零长度、共线阈值两侧、等号方向、局部架等变、4x8 局部不变/回拉及后备轴/近退化故障均可复现。 |
| T-E10 | **FAIL** | 144 点、成本和数组锚点当前数据正确；scan 的通过条件错误地统一使用 `5e-6`，且逐 case 未报告最坏旋转索引，见 B03。 |
| T-E11 | **FAIL** | SU(2) 一般角 lift、spin Theta 平方、反线性、轨道 J/D 和部分负例通过；k-pair 是同式自比，spinless Theta、2pi/4pi、H/S partner、TRIM/Kramers 定义域等冻结接口未执行，见 B04。 |
| T-E12 | **FAIL** | 现有 38/38 和三 padding 探针真实通过，但未覆盖已确认的 provenance/payload/阈值穿透及若干冻结故障，不能作为“全失败矩阵”，见 B01--B05。 |

## 5. 阻塞问题与最小关闭条件

### M7E-CODE-B01：消息方向未与 provenance 绑定

**证据。** `message_layer()` 在验证 provenance 后，只对独立参数 `directions` 检查 shape、dtype 和有限性；没有比较 `directions` 与 `provenance["direction"]`。独立变异保持原 provenance 不变，仅把第 0 条计算方向反号，函数仍接受，输出相对基线最大归一化残差为 `0.6579954457056266`。因此，同一 edge ID 可以携带与实际 contraction 不一致的方向，违反 D-E06/T-E08 的完整 edge/path provenance 合同。

**最小关闭条件。** 在进入 coefficient filter/CG kernel 前，严格比较实际 `directions` 与 provenance 中冻结方向，并同时验证 edge row、receiver、sender、shift、edge ID、basis、m 顺序和 dtype；加入 stale direction、独立 row permutation、方向/receiver 不同步以及错误 CG 通道的实际拒绝测试。A/B、三 padding 与 T-E08 等变正例必须无回归。

### M7E-CODE-B02：Hamiltonian edge identity 可由任意 payload 重哈希伪造

**证据。** `validate_hamiltonian_edge()` 只检查 `edge_id == sha256(edge_payload)`，不解析 `edge_payload` 是否为 `stageD-edge-v1`、是否具有合法 structure/receiver/sender/shift，亦不把 payload 端点与左右 shell/轨道行身份绑定。独立变异把 payload 改为 `not-json-and-not-stageD-edge-v1` 并重算 hash，validator 仍接受。T-E06 的“逆边”由 `transformed.T` 直接构造，未建立第二条规范逆边 row，也没有独立核验 payload、shift、端点交换和 Hermiticity。

**最小关闭条件。** 提供严格 edge payload 解析/规范重编码 validator，核对版本、structure、端点、整数 shift、canonical bytes 与 hash；在 Hamiltonian row schema 中显式绑定 receiver/sender/shift 与左右 shell/actual orbital identity。T-E06/T-E12 必须加入伪 payload 重哈希、合法 payload 错端点/shift、逆边未交换、轨道行独立漂移，并以两条独立 edge row 验证 `H_ji,-n = H_ij,n^dagger`。

### M7E-CODE-B03：144 点 scan 使用错误的统一阈值并缺逐 case 最坏旋转

**证据。** `run_scan()` 最终条件为 `max_residual <= 5.0e-6`，没有按每个 case 的 dtype 使用 `5e-12`/`5e-6`。独立注入使全部 float64 case 返回 `1e-6`、float32 返回 0；虽然 `1e-6` 超过 float64 阈值 200000 倍，scan 仍返回 `pass=true`。此外，`reference_equivariance()` 已返回 `{rotation, ell}`，但 case 摘要只保留 `max_residual`，未按中央约定报告每个组合的最坏旋转索引。

**最小关闭条件。** 对 144 个 case 分别执行 `residual <= tolerance(case.dtype)`，总通过条件要求全部 case 通过；每个 case 输出 threshold、pass、最坏 rotation 和 ell，并保留规范 case ID。加入受控注入回归：float64 `1e-6` 必须失败，float64/32 等号必须接受，任一 case NaN/Infinity 必须在序列化前拒绝。更新规范 scan hash 与 README 证据。

### M7E-CODE-B04：T-E11 的 k-pair 是恒等自比，冻结 D-E08 接口未执行

**证据。** 代码先令 `h_minus_k = J H_k^* J^dagger`，随后计算该对象与完全相同表达式的残差，故 `k_pair_residual` 无条件为 0，不能检测错误 k partner、漏共轭或行映射漂移。现有 T-E11 也没有独立执行 spinless `Theta=K` 的 `Theta^2=+I`、2pi=-I/4pi=I、H 与 S 的独立 k/-k row、Hermiticity、TRIM 与一般 k 的区分、Kramers 同能量以及破缺 H 不得宣称简并；这些均已在 D-E08/D-E09 映射中冻结。时间反演 payload hash 不能替代运行时对象测试。

**最小关闭条件。** 使用独立构造并带 partner/provenance 的 `H(k),H(-k),S(k),S(-k)`，分别验证 Hermiticity、时间反演关系和错误 partner/漏共轭/错 mask/轨道行；执行 spinless 与 spin-half 的反线性和 `Theta^2`，2pi/4pi lift identity，TRIM 下的 Kramers 同能与正交，以及一般 k/Zeeman 破缺的拒绝结论。k-pair 两侧不得由同一表达式即时定义。补报 D-E09 已要求的 H、J、partner map、临时 conjugate 和输出数组 shape/dtype/nbytes。

### M7E-CODE-B05：若干冻结定向故障没有进入可执行 oracle，38 项不能称为全失败矩阵

**证据。** 现有 38 项确实执行，但其集合缺少合同明确要求的多个入口：T-E01 的 NaN/Infinity、错误复合顺序和规范四元数符号；T-E03 的 STF 漏归一化；T-E04 的 Condon--Shortley 局部相位和错误 Euler 接口；T-E05 的 DLMF 全表逐项独立 oracle、输入轴互换未施加交换相位和未同步规范元数据；T-E08 的错误 CG 通道；T-E12 对其余四个 M8 字段以及 B01--B04 穿透的实际拒绝。`canonical_table_sha256` 当前只是对被审实现生成的表求 hash，测试没有与冻结常量比较，不能构成独立全表 oracle。

**最小关闭条件。** 以冻结常量或独立于被测 Racah/CG 生成路径的表为 oracle，补齐上述定向故障；每项必须实际调用生产 validator/kernel，记录唯一名称、异常类型与非空消息，不能只比较测试内自造的同式对象。README 的故障声明、T-E01--T-E12 输出、unittest 和 `rejected/total` 应同步更新；`rejected=total` 仍是必要但非充分条件。

## 6. 已通过且需保持无回归的对象

- 固定环境、精确依赖和 `pip check`；
- A/B 的当前全部正向数值残差；
- 144 个唯一 case 的轴枚举、seed 到 G_A/G_B 的映射与 PCG64 当前确定性；
- K1/K2、三个 filter、三个时间反演 payload/hash；
- 1x1、1x2 当前 CG 正交/完备与已冻结锚点；
- reference kernel 的 MAC/FLOP、receiver 聚合与数组 total/peak 四个锚点；
- 局部架阈值两侧、等号方向、4x8 回拉及近退化失败；
- padding 的 NaN/0/`1e300` 三探针，活动输出和 loss 均为 0；
- CLI config/scan 互斥、错误 seed 退出码 2、双子进程字节确定性；
- README 严格 Pandoc/MathML、UTF-8 与控制字符检查；
- 未安装或导入 DeepH/e3nn，未接触正式数据/DFT，M8 字段仍未决。

## 7. 复核入口

主 agent 完成 M7E-CODE-B01--B05 后，应把修订后的同一代码包交回本审计员定点复核。复核至少重跑固定环境、14 项以上回归、A/B/scan 双子进程、规范 payload/hash、成本/数组锚点、三 padding、更新后的完整失败矩阵，并逐项重放本报告的三个穿透脚本和 T-E11 独立 partner 变异。只有所有稳定问题均 `CLOSED`，新增问题为 0，且 `BLOCKING=0`、`NON_BLOCKING=0` 时，才允许 M7-09 标记为 `COMPLETED` 并启动 M7-10。

