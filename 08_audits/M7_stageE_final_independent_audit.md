# M7-11 阶段 E 当前总快照正式独立材料总审计

## 1. 审计结论

**最终判定：PASS。**

- `BLOCKING=0`
- `NON_BLOCKING=0`
- 新增问题：0
- 剩余问题：0
- 允许将 M7 标记为 `COMPLETED`：是
- 允许进入 D-011 规定的 M7-I：是
- 允许直接进入 M8：否
- 允许任何 M9 外部动作：否

阶段 E 当前快照在来源血缘、知识范围、公式条件、表示语义、教材—推导—题解—代码对象链、自学导航、可执行失败样例和授权边界方面均达到正式材料总门控。第 15—20 章、D-E01—D-E09、T-E01—T-E12、C-E01—C-E12/A-E01—A-E12 与统一表示约定使用同一套主动/被动、基/component、点值/coefficient、宇称、CG、Hamiltonian 左右作用、周期逆边、局部架、SU(2) 和时间反演合同；没有发现只能依赖既有章级审计才能成立的缺口。

本结论只完成 M7。下一门控必须是 D-011 指定的 M7-I：由 `gpt-5.6-sol`、推理强度 `max` 的独立子 agent 对 M3—M7 执行全量总审计，并由主 agent 修复、原总审计员复核至问题为 0。M7-I 通过后才可准备 M8 集中决策冻结；本报告不授权 M8，更不授权 M9 的安装、数据、标签或复现实验。

## 2. 独立性、权限和审计范围

本审计由新的独立审计 agent 执行。既有 M7-01—M7-10 报告只用于核定送审范围和稳定问题 ID，不作为本轮通过证据。本轮重新读取当前文件字节，独立执行来源哈希、CSV/Bib、严格 Markdown AST、数学复算、Python 环境、单元测试、三种 CLI、失败样例和授权扫描。

审计期间没有修改任何来源、教材、提纲、例题、推导、题目、解答、代码、工作包、计划、台账或既有报告；没有安装依赖、访问网络、下载数据、调用 DeepH/e3nn 或 DFT 后端，也没有生成正式标签。本报告是唯一新增文件。

审计范围包括：

- 阶段 E 的 11 个本地来源快照、来源索引、中央 `source_table.csv` 和 `bibliography.bib`；
- M7 工作包与阶段 E 统一表示约定；
- 第 15—20 章各自的 `sources.md`、`outline.md`、`chapter.md` 和 `examples.md`；
- 推导总索引及六份推导文件，覆盖 D-E01—D-E09；
- 六章和 comprehensive 的 14 份成对 problem/solution；
- 自学导航与表示追踪模板；
- Stage E 合成代码、CLI、测试、说明和精确依赖；
- M7-01—M7-10 的正式独立审计与定点复核关闭结论；
- D-010、D-011、BLK-03、M8 集中冻结和 M9 再授权边界。

## 3. 来源、台账和当前快照 SHA-256

### 3.1 来源快照

11 个本地快照的实际 SHA-256 与阶段 E 来源索引逐字节一致：

| 来源身份 | 本地文件 | 实际 SHA-256 | 论证边界 |
|---|---|---|---|
| E-FND-01 | `dlmf_14_30_spherical_harmonics.html` | `D4547C98B7DAA72A6358233A78646A49013D9110FDD817E8CAF139F3CBDA9154` | DLMF-CS 球谐，不选择实轨道顺序或软件约定 |
| E-FND-02 | `dlmf_34_1_cg_relation.html` | `D18A8C7EC7C6021C68585B40084CE882B841D018920459B82CBDF1FC36C15211` | CG 与 3j 关系 |
| E-FND-02 | `dlmf_34_3_3j_properties.html` | `075E37CF5EF5656BAAABAAEF18C7F768FA66ED0F5FB84DFFF314FB0852BFD06A` | 3j 对称性、选择定则和正交关系 |
| E-FND-03 | `mit_8_321_lecture20_rotations.pdf` | `D7FE6547B80C9E1C1B5652AFA414AA82A0CA8E08148153536BFB5305C5016169` | 旋转与角动量基础 |
| E-FND-03 | `mit_8_321_lecture21_su2_addition.pdf` | `3984AC09661CBA332BF1D077DD547FCDE2A7A3B14CF33CB13EE68A06D6EFE72D` | SO(3)/SU(2) 与角动量耦合 |
| E-FND-03 | `mit_8_321_lecture22_parity_time_reversal.pdf` | `A5EBCEFC91FA09AB6D37812FA00678C7E59BD08FFD9E0CDD627D5361BFD9AF4D` | 宇称和反幺正时间反演 |
| E-FND-03 | `mit_8_321_lecture23_time_reversal_consequences.pdf` | `5529C63E13970D58674DE2B942224821E2D3710F7603485A3777C8F50882D297` | Kramers 条件与后果 |
| E-GNN-01 | `thomas_2018_tensor_field_networks.pdf` | `21E19CC0148B8337198E4FA802D846B9C30D45FBA3C6AD76AC97788DF0F92D74` | 表示分型和球谐/CG filter 机制 |
| E-GNN-02 | `geiger_2022_e3nn.pdf` | `C04B2DE728EB8C0D06405043EE4FB0EEA666AC6C9615A396F1579A35D4BCEEDC` | E(3) 表示、宇称与张量积的一般框架 |
| DH-02 | `gong_2023_deeph_e3.pdf` | `379B288B66365D5202A481923746D5F01D8EB03433D2C67EA3E5E7261074596E` | 论文层 Hamiltonian 等变对象，不冻结软件/数据/材料 |
| E-SUP-01 | `mit_8_512_lecture10_time_reversal.pdf` | `426E41E4ED6BCC48DF8256572F7D969DD47024E75DC0DAB96F0B04C0C0B70BFA` | 补充检索档案，不进入 M7 直接论证链 |

中央 CSV 为 46 行、17 字段，`source_id` 全部唯一；阶段 E 关联的 7 条记录为 DH-02、E-FND-01/02/03、E-GNN-01/02 和 E-SUP-01。对应 BibTeX 键 `dlmf1430`、`dlmf34`、`turner2017quantum321`、`thomas2018tfn`、`geiger2022e3nn`、`gong2023deephe3`、`rudner2009solids2lec10` 全部存在。三项台账文件 SHA-256 为：

| 文件 | SHA-256 |
|---|---|
| `01_sources/documentation/stageE/README.md` | `428D005DF19C1FFB0B4010C3F5DA9931AFFD6871344C53ADDEB4B04F68CF504C` |
| `02_source_ledger/source_table.csv` | `EC863C69AB5BAC04961528117DED9B773709D87E91B75FB220295BCFD84763D7` |
| `01_sources/bibliography.bib` | `B1C6F269B563C2205BCA1126280D7AF609CBFA7381B61A06BF1C2147FD656139` |

来源边界保持正确：DLMF 和 MIT 资料不定义 DeepH 软件接口；TFN/e3nn 论文不证明本项目周期 Hamiltonian schema；DH-02 不构成仓库、版本、数据、材料、DFT 后端或 SOC/磁性实践选择；E-SUP-01 没有被悄然提升为主证据。

### 3.2 核心快照

下列文件 SHA-256 与当前被审字节一致：

| 核心文件 | SHA-256 |
|---|---|
| `08_audits/M7_stageE_work_package.md` | `1D1CA7C2F7FD2E27956F190F39AC18CEB458751554463EF660F5D3E03F7B7F84` |
| `03_textbook/stageE_representation_conventions.md` | `139BB534474A6D585CD5A31D6DF08B2DEE74F9E855929786D075C81FB34579BC` |
| `03_textbook/chapters/stageE_self_study_guide.md` | `3E253D9B35D58E0D57BE6FA0C7DBFEBE59144AF38BA8D2CE22ADC5E220764B3D` |
| `03_textbook/stageE_representation_trace_template.md` | `56A93A8E4BC6072FF6E3CBDAB03F16570B8E0C51D48589B7E571F7B5A32449DD` |
| `04_derivations/stageE/README.md` | `A65BC7199E9852A49408E31CB1E53BD0F8A3AA4F329DCB931DC1E0E8B016CCFB` |
| comprehensive problem | `6DBDF4D3E1CAECB2071309DD1577E12623B98BAACBEED2528BD575D1FE931C1D` |
| comprehensive solution | `C752A39FA588B1C324A4E4766EBF9076200211BD9378C56054FE369F9C70DC06` |
| `stagee_models.py` | `09BC05AF29DA3C7559D1DA7623257FCA01A319130CCD0ACF0DE46E330A26A535` |
| `run_experiments.py` | `9D62BB9C24EAA09D44032D97A7F9E36324AE81283474569ABE71146BB630D7E5` |
| `test_stagee_models.py` | `DA20B8DF59C1EBCA0BACC68B7AFDCF5D7732310C31F4A7209D491A24D9E9D33A` |
| code `README.md` | `0339ED7021AA84A493FCC1130BD76EAFFC55E0DE324D3F811009119B6EC580F3` |
| `requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |

为覆盖全部送审字节，另以“UTF-8 路径、TAB、该文件小写 SHA-256、LF”逐行组成清单，按路径排序后再取 SHA-256。68 个来源/台账/教材/推导/题解/代码核心文件的清单摘要为：

`4BE8BEBBA69F7539FEE0F398CF694A8EDD6E54461A0651C4856677607793328C`

同一算法得到的分组摘要为：

| 分组 | 文件数 | 清单 SHA-256 |
|---|---:|---|
| 第 15 章 sources/outline/chapter/examples | 4 | `08F433ED696187AD8C3F2DF475BDCAB0972FC5DF7EED9AEAD806EAAFD9207367` |
| 第 16 章 sources/outline/chapter/examples | 4 | `E57071121B909B53CF2F5507619923DE731559C3CF27C7C0347B7D088E386C97` |
| 第 17 章 sources/outline/chapter/examples | 4 | `9C1E2AE27FF6E238C39E44C49E9ECF8C7B4972B996FAB95A83EAF884BB95D50D` |
| 第 18 章 sources/outline/chapter/examples | 4 | `A512613E0532FB2F48FF032FAB2929E78AEECFED309F88F1C17011A9C31F7819` |
| 第 19 章 sources/outline/chapter/examples | 4 | `F912947B569B8CACD11000237D41E8C99D30E1307099A838FF604AE1056F0838` |
| 第 20 章 sources/outline/chapter/examples | 4 | `73FBE3BBABF65778EC2FFB971643E723C314532A6DE126B99BA1FB99DCCB470C` |
| D-E 推导索引与六份推导 | 7 | `9C8745CAF426DE6953F2C4BDE0BF5F538FDCDD80C90B417F306A75B45A72231C` |
| 六章及综合题 problem/solution | 14 | `A9FB641441EF26EBDBAC2F43B833E4E450D7C417EB91BF1C17FAFF3DA85BE282` |

最后一项为对 14 份题解文件共同生成的分组清单摘要；各章题解配对与内容核验见第 4 节。

## 4. 材料完备性、编号和自学性

### 4.1 第 15—20 章

六章均具有非空的来源边界、三级提纲、完整正文和解析例题。例题数依次为 8、8、8、13、14、12。第 17—20 章的 outline/chapter 编号集合与顺序完全一致；第 15、16 章的全部 outline 编号均在 chapter 中同序出现，正文分别增加 13 和 4 个经章级修订形成的更细分节，所有编号唯一，没有删去提纲对象或发生重号。

六章问题与解答均为 Q15—Q20 各 01—10 的 10/10 严格配对。综合题 C-E01—C-E12 与 A-E01—A-E12 为 12/12 严格配对。解答不仅给出结论，还保留了对象域、公式条件、shape/dtype、基/component、数值阈值、失败机制和可执行入口。取消学习者本人闭卷作答没有造成知识范围、条件或验证强度下降。

### 4.2 D-E01—D-E09 与跨章对象链

推导索引能把 D-E01—D-E09 全部定位到逐式推导、正文、例题、章末题解、综合题和 T-E 入口。独立核对结果为：

| ID | 当前闭合对象 | 关键条件与失败边界 |
|---|---|---|
| D-E01 | 主动/被动 SO(3)/O(3) 作用、复合、行晶格桥接 | 列向量主动作用；先 R1 后 R2 为 R2R1；反射不混入 SO(3) |
| D-E02 | 实 s/p/d、STF、直和/multiplicity、宇称 | 冻结实轨道顺序；STF Frobenius 正交归一；极/轴向量区分 |
| D-E03 | DLMF-CS 球谐、Wigner、复—实桥 | m 升序；点值按 D*，coefficient 按 D；完整 shell/mask 同步 |
| D-E04 | CG、选择定则、相位自由、交换 | DLMF 规范全表；整通道相位自由不等于局部相位合法 |
| D-E05 | 非方/多壳 Hamiltonian 双侧协变 | receiver/bra 左、sender/ket 右；复基保留 dagger；逆边独立身份 |
| D-E06 | coefficient filter、CG 消息、receiver sum、门控 | 同一 edge row 先构造 z=conjugate(y)；CG 只收缩表示 component |
| D-E07 | 唯一局部架与全局回拉 | 有限正尺度、非零向量、归一化叉积 eta 严格在接受侧；无后备轴 |
| D-E08 | SU(2)、反幺正时间反演、H/S partner、Kramers | Theta=JK；Theta2=JJ*；Kramers 还要求对称性和 TRIM |
| D-E09 | 维数、残差、MAC/FLOP、数组字节、144 点 | A/B 与 scan 互斥；逐 dtype 阈值；wall-time 不进入规范 hash |

### 4.3 自学导航与表示追踪模板

自学导航的 C-E01—C-E12 正向矩阵逐行含教材、D-E 推导、具体例题、代码/T-E、失败症状、章末问题/解答和综合问题/解答入口。表示追踪模板覆盖 irrep、multiplicity、dtype、shape、basis/component、作用方向、edge/direction、Hamiltonian、局部架和 time-reversal H/S partner 的独立 provenance、mask、shape、dtype 与残差字段。

C-E08 已唯一冻结为

\[
(1,-)\otimes(1,-)\to(0,+)\oplus(1,+)\oplus(2,+),
\]

题面、解答、导航、代码 provenance 和 O(3) 反演失败样例一致。C-E09 使用

\[
\eta=\lVert\widehat u\times\widehat v\rVert_2,
\]

而不是带输入幅值的未归一化投影。模板中的时间反演记录不能再用算符平方替代独立 H/S partner 行。

## 5. 高风险数学对象的独立复算

本节使用独立的内存 NumPy 实现，没有以现有 unittest、CLI 判定或既有审计报告替代复算。旋转由 Rodrigues 公式构造；CG 表由总角动量算符 J2 在各固定 M 子空间独立对角化，而不是调用生产 `wigner_3j` 公式。

### 5.1 STF、实/复表示与球谐作用

对一般轴旋转，独立 STF 基的 Gram 残差为 `2.22e-16`；实 d 表群律、正交性和与生产实现的残差依次为 `2.49e-16`、`3.02e-16`、`9.58e-17`。独立抄录冻结函数恒等式所得 K1/K2 幺正残差为 `1.81e-16`、`1.99e-16`，与生产数组逐元素一致。

在一般非轴方向上，ell=1/2 的球谐点值满足

\[
y^{\mathrm{pv}}(R\widehat r)=D(R)^*y^{\mathrm{pv}}(\widehat r),
\]

残差为 `6.51e-17`、`1.19e-16`；共轭后的 coefficient filter 满足 D 作用，残差相同。该复算确认材料没有把函数点值直接送入要求两个 coefficient-D 输入的 CG intertwiner。

### 5.2 CG 全表、宇称与相位

独立 J2 对角化得到的 `1x1` 与 `1x2` 全表，在仅对每个合法 L 通道对齐整体相位后，与生产表的最大逐项误差为 `3.33e-16`、`5.55e-16`，最小绝对重叠分别为 `0.9999999999999998`、`0.9999999999999996`。生产表的行/列正交残差均低于 `3e-16`，输入交换律最大误差为 0。

三个 `1x1` 规范锚点独立读取为 `1/sqrt(3)`、`1/sqrt(2)`、1；完整规范表 SHA-256 为 `FD40673F73059974962CF9B8B3C9152B9AF1BD28BB87028B9E4BFFE797FD1A04`。材料正确区分“整条 L 通道同步相位是基自由”与“单系数、部分 M 或未同步元数据是规范/等变错误”。T-E08 的反演正例残差为 0，错误输出宇称残差为 2，故 SO(3) 通过没有被误当成 O(3) 宇称证明。

### 5.3 Hamiltonian、逆边和局部架

独立构造一般轴的 `4x8` 双侧变换

\[
H'=D_iHD_j^{\mathsf T}
\]

后，独立 `8x4` 逆边满足旋转后转置关系，归一化残差为 `1.53e-16`；只左乘故障残差为 `0.5674`。因此非方 shape、左右 shell、receiver/bra 与 sender/ket 的方向确实能暴露左右交换和漏右作用。

局部架幅值夹具 `u=(1,0,0)`、`v=(2,1.5e-8,0)`、`s=1` 的规范 `eta=7.5e-9`，应在 float64 拒绝侧；旧未归一化投影为 `1.5e-8`，会错误接受。当前教材、题解、模板和代码均采用前者。

### 5.4 反幺正时间反演与成本

使用固定

\[
J=\begin{pmatrix}0&1\\-1&0\end{pmatrix}
\]

独立复算得到 spin-half 的二次反幺正作用相对 `-I` 残差为 0，H/S 的 k/-k partner 均 Hermitian，S partner 最小本征值为 `1.0765>0`。规范 spin-half payload 的独立 SHA-256 为 `F8B5E9591B791A2DBD9B262736718C8B391B75DE6CE720335D1AD5B8F1AFF444`；K1/K2 payload 的独立 SHA-256 为 `347E352605A3F4F3CCB078B6CEDF5C755FDC6AA3527EA41A8EA3E93D076972A2` 和 `5E783D9CDFE025238977F9E92D64D8B46E9A0E79EB8C9DEBA1AF116AAAFC7B82`。实际材料与代码以无空白规范 JSON 保存，运行测试逐项核验。

由图入度、shape 和逐数组 nbytes 独立重算的 D-E09 锚点为：

| 图 | MAC/rotation | aggregation add/rotation | total bytes | reference peak bytes |
|---|---:|---:|---:|---:|
| G_A | 168 | 52 | 2728 | 2280 |
| G_B | 378 | 143 | 5584 | 4576 |

这些整数与推导、README 和 CLI 完全一致；局部 reference contraction 的 MAC/FLOP/bytes 没有被冒充端到端模型 wall-time。

## 6. 固定环境、代码、CLI 与失败样例

固定运行环境为：

- Python 3.12.13；
- NumPy 2.3.5；
- SciPy 1.18.0；
- `requirements.txt` 精确固定 `numpy==2.3.5`、`scipy==1.18.0`；
- `python -m pip check` 输出 `No broken requirements found.`。

设置 `PYTHONDONTWRITEBYTECODE=1` 后独立运行 `unittest discover`，17/17 通过。A、B 和 scan 均由两个真实独立子进程各执行一次并直接捕获原始 stdout bytes：

| 模式 | 两次字节相等 | bytes | stdout SHA-256 | 结果 |
|---|---|---:|---|---|
| A | 是 | 21,247 | `6A656A18BBFEF042CBCD3049278C15FD0644F4B593D06E44A2B63C5FC78BE856` | T-E01—T-E12 12/12，overall true |
| B | 是 | 21,301 | `B9E4CA3DE9E671F4F9B674E40B5F62068F3A91E6BA886D4640D3B90AA6FD82D1` | T-E01—T-E12 12/12，overall true |
| scan | 是 | 62,206 | `C13944029E29EF6B47919646952A5D9BDF6A018CEE3F101429FAB09967982A81` | 144/144，pass true |

scan 的 case digest 为 `5317A387BFB026E53DCEB31A85074D52FF520448C2FBAC9649CB8013064CCA7E`；最大残差 `1.9468769400071583e-7`，最坏 case 为 `float32-s20260809-r257-m1-a1e+03`、rotation 189、ell 2。每个 case 各自保存 dtype 阈值、pass、最坏旋转和 ell；float64/float32 阈值没有混写。

T-E12 在 A/B 均实际执行 63 个唯一故障并得到 `rejected=total=63`，每项均有异常类型和非空消息。故障覆盖 rotation/quaternion 非有限与边界、STF、基/m 顺序、complete irrep shell、padding、Hamiltonian payload/hash/端点/shift/轨道身份、direction provenance、CG 通道与宇称、time-reversal H/S partner 以及六个 M8 sentinel。NaN、0、`1e300` 三种 inactive padding 探针的活动输出残差和 loss 均为 0，active NaN 仍被前置拒绝。

T-E11 使用独立 H(k)、H(-k)、S(k)、S(-k) 行而非同式自比；A/B partner 数组总字节为 644/332。spinless/spin-half、2pi/4pi、一般 k 与 TRIM、Kramers 广义本征条件、Zeeman 破缺、漏共轭和错误 K-dagger 路线均有可执行证据。config A 使用错误 seed 和 config/scan 冲突均退出码 2、stdout 为空，未允许改变随机对象后沿用冻结摘要。

## 7. 严格 Markdown、AST、控制字符和结构检查

对 50 个核心 Markdown 输入逐个执行：

`pandoc --from=markdown+tex_math_single_backslash --to=html5 --mathml --fail-if-warnings`

结果为 50/50 返回 0，共解析 4,495 个 MathML 节点。对同一集合解析 Pandoc JSON AST，活动本地链接为 226/226 存在，Raw TeX 节点为 0，非法控制字符为 0。所有 problem/solution 目录非空；Q/A 和 C-E/A-E 编号配对均通过。

该结果只证明当前 50 个核心 Markdown 的严格结构和链接闭合；来源 PDF/HTML 的字节完整性由第 3 节 SHA 检查承担，Python 语义由第 5—6 节的独立复算和执行证据承担，三类证据没有相互替代。

## 8. M7-01—M7-10 正式审计闭环

重新核对各任务最后一份有效放行报告，所有稳定问题均已由原独立审计员关闭，且新增及剩余问题为 0：

| 任务 | 最终报告 | 报告 SHA-256 | 当前结论 |
|---|---|---|---|
| M7-01 | `M7_stageE_work_package_second_reaudit.md` | `C1DADFEB238F351167B047070159982CE9C5806185B039BD50D410AB7C66D003` | PASS，B01/B02/N01 全闭合 |
| M7-02 | `M7_chapter15_second_reaudit.md` | `44CC0088788BC1DD253BA4429B3E6E786885CF8F695C0732121FDA616CF09034` | PASS，问题为 0 |
| M7-03 | `M7_chapter16_independent_content_audit.md` | `9D67D6FED4CFC29FC726279362DA7268902F4BDCB1EE1C3ED22DAC65ED8C9C9B` | PASS，问题为 0 |
| M7-04 | `M7_chapter17_blocking_reaudit.md` | `D00149A0F3850641CBA830473212B4E4657C79AB6EA882DF413D02789E7B03B2` | PASS，B01/B02/N01 全闭合 |
| M7-05 | `M7_chapter18_blocking_reaudit.md` | `61BD9EDAA9E95BE6E6D30D64F5F96484FBA4CFCE3C748A12E1EC3B4D183EAC2C` | PASS，B01/B02/N01 全闭合 |
| M7-06 | `M7_chapter19_second_reaudit.md` | `ED8F6F6247EADB3187D942A9ED36831029564B64A6BFB63AC233C79EA756D301` | PASS，B01/B02/N01 全闭合 |
| M7-07 | `M7_chapter20_blocking_reaudit.md` | `5E05B723B5236696119A692CD6077625FEEFB202331670D25F398AACA8791035` | PASS，B01/N01 全闭合 |
| M7-08 | `M7_stageE_derivation_package_blocking_reaudit.md` | `20FC39A4E854813DCC68CCBB722B3860808A45891B95B7FF46A3CB234B8AB506` | PASS，B01/B02 全闭合 |
| M7-09 | `M7_stageE_code_blocking_reaudit.md` | `AE6D507A0FDE1F7E1D136E8687968C0DF5903DF2EBD1E35626C4DD58FBACB4B6` | PASS，B01—B05 全闭合 |
| M7-10 | `M7_stageE_self_study_blocking_reaudit.md` | `7FDD7F3ED4A1DD8855839D3EC4C5A5EE87A3D0652EE726949BE34F2338D86B14` | PASS，B01—B05 全闭合 |

本轮没有仅凭这些历史结论放行；第 3—7 节已对当前快照重新执行全域检查。报告哈希只用于确认既有结论未漂移。

## 9. M8/M9 与 BLK-03 授权边界

代码依赖面只有 NumPy/SciPy；没有导入 DeepH、e3nn、ASE、pymatgen 或 DFT 软件。A/B 的 `material_system`、`dft_backend`、`data_backend`、`deeph_software_object`、`training_budget` 和 `advanced_physics_scope` 六字段均为 `UNRESOLVED_M8`，提前选择它们会在 T-E12 被拒绝。

因此 BLK-03 不阻塞 M7-I 的理论、教材和合成审计，但必须保持 `UNRESOLVED_M8`。只有 M7-I 问题为 0 后，才能向用户集中提交计算资源、DFT/数据后端、DeepH 软件对象、首个材料体系、时间与训练预算、高级物理范围的 M8 决策方案。M8 由用户明确冻结后，M9 的 DeepH/e3nn 正式安装、正式数据下载、DFT 标签生成或复现实验前仍须再次取得明确执行授权。

## 10. 问题清单与最终许可

本轮未发现 BLOCKING 或 NON_BLOCKING 问题，因此没有需要主 agent 修复或由本审计员定点复核的稳定问题 ID。

最终计数为 `BLOCKING=0`、`NON_BLOCKING=0`、新增问题 0、剩余问题 0。允许主 agent 将 M7 标记为 `COMPLETED`，并按 D-011 启动 M7-I。该许可不允许跳过 M7-I，不允许直接启动 M8，也不允许执行任何 M9 外部动作。
