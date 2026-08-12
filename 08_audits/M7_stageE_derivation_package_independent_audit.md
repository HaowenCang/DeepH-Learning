# M7-08 阶段 E 解析推导包正式独立审计

## 1. 审计结论

**结论：FAIL。** 本轮发现 `BLOCKING=2`、`NON_BLOCKING=0`。

六份逐项推导中的 D-E02—D-E08 核心数学链、README 中 D-E01—D-E09/T-E01—T-E12 的编号覆盖、跨文件表示合同、来源边界、严格 Markdown/MathML 和 M8/M9 授权边界均通过独立复核。独立复算也确认 19/17、32/50、\(G_A\) 的 168/52/2728/2280 与 \(G_B\) 的 378/143/5584/4576 数值本身正确。

但是，当前推导包还不能完成 M7-08：

- `M7-DE-B01`：D-E01 覆盖矩阵和映射表宣称已经包含“主动/被动”推导，但 D-E01 推导文件只定义主动作用并把转置当作主动语义下的错误对象，没有推导被动换基的对象、条件和坐标公式；
- `M7-DE-B02`：D-E09 要求逐数组唯一冻结 shape/dtype/nbytes，但 `rotations` 只给出名称，前文同时出现 shape \((n_R,4)\) 的原始四元数。当前文档没有说明计入成本的 `rotations` 是 shape \((n_R,3,3)\) 的旋转矩阵，也没有说明原始四元数是否物化、何时释放及是否排除。四个 total/peak 锚点只能通过反推 72-byte 旋转矩阵项恢复，不能从明示的逐数组合同唯一导出。

因此不允许把 M7-08 标记为 `COMPLETED`，也不允许启动 M7-09。主 agent 修订后应交回同一审计员定点复核。

## 2. 独立性、范围与快照

本审计由新的独立子 agent 执行。七个被审推导文件、统一表示约定、工作包、第 15—20 章正文/例题/练习与参考解答以及阶段 E 来源均保持只读；本报告是唯一新增文件。审计没有安装依赖、没有调用 DeepH/e3nn、没有下载数据或生成标签。

被审快照 SHA-256 为：

| 文件 | SHA-256 |
|---|---|
| `04_derivations/stageE/README.md` | `75E47FD00149D667DE64597856B54FE284D9E4EAA5D15057FBF5BA105C49B2F8` |
| `15_group_actions_equivariance.md` | `3D8618858684BDDDD2278388BDD5AC56D96693D23895D37E150650C992CDAA5D` |
| `16_real_spd_representations.md` | `EE59FC78011C45691345D4C7D83651446582D858F83522AD055CFE77C851A23F` |
| `17_spherical_harmonics_wigner.md` | `0FE372A2AD42E60374F5FADEFCA30CADFA9B8FA904CAE22544419C9C9AA55179` |
| `18_tensor_products_clebsch_gordan.md` | `645BA9326EDFACEC64B276F9029D86C89E63F2E71900DC47CC67121B29E7120A` |
| `19_equivariant_graph_hamiltonian.md` | `E021C84430750F1E3B857258BD0388AEB8D990AB60CF2D4DDF4BD98E41183F2B` |
| `20_spin_time_reversal_complex.md` | `E3397B367E8AE477B2026AA6935240FC811C458AAAEEBB435621904FA337BE96` |
| `03_textbook/stageE_representation_conventions.md` | `2826352EDD07089695B221BAD0C0461F61536FFB3492353118CE1111AD6CBD1C` |

独立数值环境为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；`pip check` 返回 `No broken requirements found.`。

## 3. 审计方法

本轮没有采用主验证摘要作为通过证据，而是独立执行：

1. 逐式阅读七个推导文件，并按工作包 D-E01—D-E09 的结构合同核对符号、rank/shape、dtype、基、身份、成立条件、推导、正反例、最终不变量、定义域和 T-E 入口；
2. 交叉核对主动复合/行晶格、实 \(p,d\) 基、\(C/K\)、点值 \(D^*\)/coefficient \(D\)、CG 相位/宇称、Hamiltonian 左右作用、逆边、局部架、自旋顺序、反幺正基变换和 k-pair/Kramers 合同；
3. 用独立 Python 脚本重建 \(B_a,K_1,K_2\)、Racah 有限和 CG 表、一般轴旋转、非方 Hamiltonian、时间反演矩阵和 D-E09 成本；
4. 独立计算阶段 E 直接来源快照 SHA-256，并与来源索引和台账对照；
5. 对七个文件分别运行 `pandoc --from=markdown+tex_math_single_backslash --to=html5 --mathml --fail-if-warnings`，另解析 Pandoc JSON AST 的 Math、Link、RawInline/RawBlock 和普通文本节点；
6. 逐码点扫描 C0/DEL 控制字符，并检查数学节点外 TeX 命令候选；
7. 核对 README 的 D-E/T-E 编号、章节/例题/练习/题解入口、M7-09 待执行边界，以及 D-011、M8/M9 双授权点。

## 4. D-E01—D-E09 结构门控

| D-E | 独立判断 | 主要证据 |
|---|---|---|
| D-E01 | **FAIL** | 主动列向量、\(R_2R_1\)、行晶格、极/轴向量、二阶张量、周期边和定量错误转置均完整；但被动换基只出现在索引宣称中，没有逐步推导，见 `M7-DE-B01` |
| D-E02 | PASS | \(s,p,d\) 维数、STF 冻结基、\(D^d_{ab}=\operatorname{tr}(B_a^TRB_bR^T)\)、正交、群律、宇称、multiplicity、失败投影和 T-E03/07/10/12 完整 |
| D-E03 | PASS | DLMF-CS、\(m\) 升序、Wigner 操作定义、\(C_ell/K_ell\)、点值 \(D^*\)/系数 \(D\)、一般轴例、零长度、完整 shell/mask/edge/provenance 和 T-E04/06/07/12 完整 |
| D-E04 | PASS | CG--3j、有限和、选择定则、\(1\otimes1\) 全表、\(1\otimes2\) 三锚点、正交/完整/intertwiner、整通道相位、宇称、mask/provenance、成本和 T-E05/08/10/12 完整 |
| D-E05 | PASS | 统一 shape/dtype/basis/edge 表、非方 \(4\times8\) 双侧作用、实复路线、逆边 Hermiticity、batch/mask/padding、定向故障与 T-E06/12 完整 |
| D-E06 | PASS | \(z^{\mathrm{cf}}=\overline{y^{\mathrm{pv}}}\)、径向偶标量、coefficient CG、逐边消息、receiver sum、同型混合、门控、置换、一般轴复正反例和 T-E08/12 完整 |
| D-E07 | PASS | 两向量无量纲阈值、唯一 Gram--Schmidt 右手架、\(4\times8\) 局部化/回拉、等号拒绝、后备轴失败、正负近共线有限跳变和 T-E09/12 完整 |
| D-E08 | PASS | 标准 Pauli、自旋顺序 \((+1/2,-1/2)\)、SU(2) lift、\(\Theta=JK\)、\(\Theta^2=JJ^*\)、\(J_c=KJ_rK^T\)、H/S k-pair、Kramers/TRIM、破缺例和 T-E11/12 完整 |
| D-E09 | **FAIL** | 维数、参数、reference kernel、MAC/FLOP、聚合、A/B、\(G_A/G_B\)、PCG64、144 点、scan/config、wall-time 和局部成本边界均明确；但逐数组 shape 与 quaternion/rotation 生命周期不唯一，见 `M7-DE-B02` |

除上述两个阻塞缺口外，没有发现其余 D-E 项的条件、定义域或 T-E 入口缺失。

## 5. 跨文件表示合同与独立复算

### 5.1 主动作用、实表示与复—实桥接

统一约定、README 与第 15—20 章在下列对象上保持一致：

- 列向量主动作用，先 \(R_1\) 后 \(R_2\) 为 \(R_2R_1\)，行晶格 \(A'=AR^T\)；
- 实轨道顺序为 \((p_x,p_y,p_z)\) 与 \((d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2})\)；
- \(D^d_{ab}(R)=\operatorname{tr}(B_a^TRB_bR^T)\)；
- \(K_ell=C_ell^*\)，普通线性 coefficient 算符走 \(KAK^\dagger\)，反幺正 unitary part 走 \(KJK^T\)；
- 点值满足 \(y(R\widehat d)=D^*y(\widehat d)\)，进入 coefficient CG 前必须构造 \(z^{\mathrm{cf}}=\overline{y^{\mathrm{pv}}}\)。

对 300 组独立一般轴旋转，独立复算得到：

| 对象 | 最大归一化残差 |
|---|---:|
| \(D^d(R_2R_1)=D^d(R_2)D^d(R_1)\) | \(4.49\times10^{-16}\) |
| 复球谐点值 \(y(R\widehat d)=D^*y(\widehat d)\) | \(2.57\times10^{-16}\) |
| coefficient filter \(z(R\widehat d)=Dz(\widehat d)\) | \(2.57\times10^{-16}\) |
| \(J_1D^{(1)*}J_1^\dagger=D^{(1)}\) | \(4.31\times10^{-16}\) |

\(K_1,K_2\) 规范 payload 的独立 SHA-256 分别为 `347E352605A3F4F3CCB078B6CEDF5C755FDC6AA3527EA41A8EA3E93D076972A2` 与 `5E783D9CDFE025238977F9E92D64D8B46E9A0E79EB8C9DEBA1AF116AAAFC7B82`，与推导一致。

### 5.2 CG、宇称与消息

独立实现推导文件给出的 Racah 有限和，而非读取材料中的 CG 数组。结果为：

| 对象 | 独立结果 |
|---|---:|
| \(1\otimes1\) 输出正交误差 | \(6.00\times10^{-16}\) |
| \(1\otimes1\) 输入完整误差 | \(5.77\times10^{-16}\) |
| \(1\otimes2\) 输出正交误差 | \(1.05\times10^{-15}\) |
| \(1\otimes2\) 输入完整误差 | \(1.13\times10^{-15}\) |
| 一般轴 \(1\otimes1\) intertwiner 残差 | \(2.98\times10^{-16}\) |
| 一般轴 \(1\otimes2\) intertwiner 残差 | \(4.01\times10^{-16}\) |

\(1\otimes2\) 三个最高行独立恢复为 \(\sqrt{3/5},-\sqrt{3/10},1/\sqrt{10}\)、\(-\sqrt{2/3},1/\sqrt3\) 与 1，和材料相同。宇称输出始终取输入宇称乘积，未发现把 \((-1)^L\) 错加到一般表示类型的情况；整通道相位自由与局部 \(M\) 相位错误也保持区分。

### 5.3 Hamiltonian、局部架与时间反演

对冻结 \(4\times8\) 块，独立复算三种定向故障相对正确 \(D_iHD_j^T\) 的残差为：

| 故障 | 残差 |
|---|---:|
| 只左乘 | `0.5461588700222612` |
| 只右乘 | `0.059952649769071845` |
| 右侧误用 \(D_j\) | `0.9216691727258702` |

这些值与推导锚点一致。复基仍明确使用 \(D_j^\dagger\)；逆边 \((j,i,-n)\)、完整 edge row、左右 shell、actual orbital、mask 和 provenance 没有被 shape 或谱替代。

局部架的 \(\zeta\) 与 \(\eta\) 接受侧、等号拒绝、无后备轴、\(F'=RF\)、局部块不变和回拉均与统一约定一致。正负近共线极限的 \(F_+=I\)、\(F_-=\operatorname{diag}(1,-1,-1)\) 给 Frobenius 跳变 \(2\sqrt2\)，固定全局后备轴在 \(R_x(\pi/2)\) 下给 \(\sqrt2\) 误差，均可独立复算。

时间反演部分固定标准 Pauli 和 spin-minor 顺序。独立复算得到 \(\Theta^2\psi=-\psi\) 残差 0、\(\langle\psi|\Theta\psi\rangle=0\)，并确认 \(J_s\sigma_a^*J_s^\dagger=-\sigma_a\) 对三个 Pauli 矩阵均精确成立。三个 `stageE-time-reversal-v1` payload hash 独立恢复为：

- `56342DB661DA6F8D9CC8C3BF6E241DCB9817F42E63A33CAD9AF9364BCC8DF6EC`；
- `F8B5E9591B791A2DBD9B262736718C8B391B75DE6CE720335D1AD5B8F1AFF444`；
- `230AA31FC0201B4F2D7F8981A3244049C280F75CB2C753F38F9CE9D86A250980`。

H/S 的 k/-k 配对、TRIM 条件、时间反演破缺和“一般 k 不推出同 k 简并”的定义域陈述均正确。

## 6. D-E09 独立整数复算与唯一性缺口

### 6.1 维数、参数与 contraction

配置 A/B 的表示维数独立复算为：

\[
3+3\cdot2+5\cdot2=19,
\qquad
5+3\cdot4+5\cdot3=32.
\]

同型自映射参数为：

\[
3^2+2^2+2^2=17,
\qquad
5^2+4^2+3^2=50.
\]

扫描 multiplicity 基准 \((2,2,1)\) 的每边 component-weighted contraction 数为

\[
2^2\cdot1+2^2\cdot3+1^2\cdot5=21.
\]

所以 \(G_A\) 与 \(G_B\) 的 MAC 分别是 \(8\cdot21=168\) 与 \(18\cdot21=378\)。\(G_A\) 每个节点入度为 2，故 \(\sum_i(\deg_i^--1)=4\)；\(G_B\) 的入度为 \((3,2,3,3,2,3,2)\)，故该和为 11。每条剩余聚合的输出分量数为 \(2+6+5=13\)，所以聚合加法为 52 与 143。

144 点由

\[
2\;\mathrm{dtype}
\times2\;\mathrm{seed}
\times4\;n_R
\times3\;m
\times3\;\alpha
=144
\]

唯一给出；PCG64 draw order、\(G_A/G_B\)、scan/config 互斥和 wall-time 排除均已冻结。

### 6.2 当前锚点隐含的逐数组复算

若额外假定 `rotations` 是目标 dtype 的 shape \((n_R,3,3)\) 旋转矩阵、原始 shape \((n_R,4)\) 四元数在成本摘要前释放且不计入，则 float64、\(n_R=1,m=1\) 的逐数组 nbytes 为：

| 数组族 | \(G_A\) | \(G_B\) |
|---|---:|---:|
| coordinates | 96 | 168 |
| receiver | 64 | 144 |
| sender | 64 | 144 |
| shift | 192 | 432 |
| rotations \((1,3,3)\) | 72 | 72 |
| 全部 \(x_ell\) | 416 | 728 |
| 全部 \(W_ell\) | 576 | 1296 |
| 全部 \(m_ell\) | 832 | 1872 |
| 全部 \(h'_ell\) | 416 | 728 |

总和确为 2728 与 5584。常驻项去掉全部 \(m_ell\)，再加最大单个 \(m_1\) 的 384/864 bytes，得到 2280 与 4576。

然而，这个关键假定没有写入 README 或统一约定。当前唯一明示的 rotation-related shape 是 RNG 原始四元数 \((n_R,4)\)。若 `rotations` 指该数组，则其字节是 32 而不是 72，total/peak 会分别变为 \(2688/2240\) 与 \(5544/4536\)。因此锚点数值正确不等于逐数组合同唯一，构成 `M7-DE-B02`。

### 6.3 各章局部成本边界

第 16 章的表示维数/参数/节点字节、第 17 章实复值字节、第 18 章 CG 乘积/非零缩放/真实累加、第 19 章消息/聚合/Hamiltonian/局部架、第 20 章显式自旋扩维，均明确声明不同操作图与排除项。未发现把局部成本相加为模型总成本、把 complex MAC 当作 2 FLOP，或从解析比率外推软件 wall-time 的表述。

## 7. README、来源、文档和授权边界

### 7.1 索引与材料入口

README 中 D-E01—D-E09 为 9/9，T-E01—T-E12 为 12/12，无缺号。第 15—20 章的 `sources.md`、`outline.md`、`chapter.md`、`examples.md` 均存在；六组问题与参考解答入口均存在。README 明确声明正式代码、CLI、双子进程、A/B、144 点和失败矩阵在 M7-09 建设，当前章内 NumPy 复算不冒充代码执行证据。因此当前不存在“尚未建设的代码被宣称已通过”的越界。

### 7.2 来源等级与不得外推

阶段 E 十一个来源快照的独立 SHA-256 均与来源索引和 `source_table.csv` 一致。E-FND-01/02/03、E-GNN-01/02 与 DH-02 的直接支持范围，以及 E-SUP-01 不进入直接论证链的状态均清楚。材料把实 \(d\) 基、阈值、合成图、payload/hash、固定旋转和成本 kernel 标为项目直接推导或教学冻结，没有把 TFN/e3nn 论文外推为周期 Hamiltonian schema 证明，也没有从 DH-02 外推仓库、数据、材料、DFT、SOC 路线或软件兼容性。

### 7.3 严格 Pandoc/MathML 与 AST

七文件均以严格 Pandoc 设置返回 0：

| 文件 | MathML 节点 |
|---|---:|
| README | 92 |
| D-E01 | 121 |
| D-E02 | 181 |
| D-E03 | 190 |
| D-E04 | 270 |
| D-E05—07 | 228 |
| D-E08 | 143 |
| **合计** | **1225** |

Pandoc JSON AST 共解析 27 个本地活动链接，断链 0；RawInline/RawBlock TeX 为 0；数学节点外 TeX 命令候选为 0；C0/DEL 非法控制字符为 0。没有发现第 19、20 章既往 `operatorname`、`in` 或控制字符问题回归。

### 7.4 M8/M9 与 D-011

README、工作包和 decisions 的边界一致：M7-11 后仍须由 D-011 指定的 `gpt-5.6-sol`/`max` 独立执行 M3—M7 全量总审计，通过后才准备 M8 集中决策冻结；M8 冻结后，在 M9 安装 DeepH/e3nn、下载正式数据、生成 DFT 标签或运行复现实验前仍须再次获得明确授权。本推导包没有隐含选择材料、后端、软件对象、预算或高级物理实践范围。

## 8. 稳定问题

### 8.1 M7-DE-B01：D-E01 缣失被动换基逐步推导

**严重度：BLOCKING。**

**证据：** `README.md` 的 D-E01 覆盖矩阵把产物写为“主动/被动作用”，`15_group_actions_equivariance.md` 第 12 节又把“主动/被动、合法旋转、逆与复合”映射到第 3、5、9、11 节。但该文件正文没有定义被动坐标变换；全文唯一出现“被动”是在映射表中。第 3 节只给主动 \(v'=Rv\)，第 5 节是行晶格存储桥接，第 9 节把 \(R^Tv\) 作为主动目标的定向错误，第 11 节只列测试项。

第 15 章正文、例题和 A15-01 确实另行给出被动坐标公式，因此知识内容没有在整章缺失；但 M7-08 的门控要求每个 D-E 项自身具有逐步推导，且当前索引给出了不真实的完成位置。章级教材不能使错误的推导包定位自动成立。

**最小关闭条件：**

1. 在 D-E01 推导文件中新增明确的被动换基对象：物理向量不变，新基由旧基按 R 旋转时，坐标满足 \([v]_{\mathrm{new}}=R^T[v]_{\mathrm{old}}\)；
2. 从基矩阵等式逐步推出该式，并说明它与主动 \(v'=Rv\) 回答不同问题；
3. 给出至少一个固定解析正例和一个把被动式误用为主动式的定量失败，注明 shape/dtype/Cartesian basis/coordinate-frame identity 和成立条件；
4. 明确被动连续换基的复合顺序，避免只写单次转置；
5. 更新 D-E01/T-E01/T-E02 映射到真实小节，并保持行晶格桥接与主动空间旋转不变。

### 8.2 M7-DE-B02：D-E09 未唯一冻结 rotations 数组及四元数生命周期

**严重度：BLOCKING。**

**证据：** 统一约定第 11.3 节明确先抽取 float64 C-order、shape \((n_R,4)\) 的标准正态四元数，随后要求逐数组摘要包含 `rotations`；README 第 4.3 节同样只列名称。两处均没有写明 `rotations` 的 rank/shape，也没有声明原始四元数是否是命名数组、是否在旋转矩阵形成后释放或是否排除。另一方面，冻结 total/peak 只有把 `rotations` 解释为 shape \((n_R,3,3)\) 的目标 dtype 矩阵并排除原始四元数时才成立。

这不是单纯排版缺失。D-E09 明确要求逐数组 shape/dtype/nbytes 和可独立复算的 total/peak；`rotations=(n_R,4)` 与 `rotations=(n_R,3,3)` 都与当前文字相容，却给不同字节结果。因此当前合同不能唯一生成正式 M7-09 oracle。

**最小关闭条件：**

1. 在 README D-E09 和统一约定中增加完整逐数组表，至少逐名冻结 coordinates、receiver、sender、shift、rotations、全部 \(x_ell,W_ell,m_ell,h'_ell\) 的 rank/shape/dtype/nbytes 公式；
2. 明确 `rotations` 是规范四元数还是 \(3\times3\) 矩阵。若保留现有锚点，应显式写为目标 dtype、shape \((n_R,3,3)\)；
3. 明确原始 float64 shape \((n_R,4)\) RNG 四元数的物化、转换和释放时点，以及它是否被 `array_bytes_total`、reference peak 或排除项计入；
4. 从逐数组表逐项重算并列出 \(G_A/G_B\) 的 2728/2280 与 5584/4576，不得通过已知总数反解缺失数组；
5. 保持 reference kernel、PCG64 draw order、144 点、scan/config 互斥、wall-time 排除和各章局部成本边界不变。

## 9. 退出判断

| 问题 ID | 严重度 | 状态 | 最小关闭条件 |
|---|---|---|---|
| `M7-DE-B01` | BLOCKING | OPEN | D-E01 补足被动换基的对象、逐步推导、复合、正反例和真实映射 |
| `M7-DE-B02` | BLOCKING | OPEN | D-E09 冻结逐数组表、rotations shape、原始四元数生命周期并逐项重算 total/peak |

最终计数为 `BLOCKING=2`、`NON_BLOCKING=0`。因此本轮判定 **FAIL**，不允许完成 M7-08，也不允许启动 M7-09。

修订应只关闭上述两个稳定问题，不改变已经通过的 D-E02—D-E08 数学合同、来源范围、阈值、配置、图、RNG、授权边界或数值锚点。修订完成后应由同一独立审计员执行定点复核，并检查是否引入新问题。

本报告写入后将独立执行严格 Pandoc/MathML、AST 链接、Raw TeX、数学节点外 TeX 和控制字符检查；稳定 SHA-256 作为交付元数据回报，避免报告正文形成自指哈希。
