# 阶段 E 解析推导包：群表示、等变 Hamiltonian 与时间反演

本索引把 D-E01—D-E09 组织为一条从三维群作用，经实/复不可约表示、CG 张量积和等变消息，到 Hamiltonian 双侧协变、局部架、时间反演与完整数值成本的可复核推导链。六份逐项推导文件保留符号表、条件、逐步公式、正反例和最终不变量；本文件只建立依赖、跨文件接口和统一验收，不用摘要替代原推导。

阶段 E 仍处于材料建设模式。全部对象是固定合成旋转、合成图、合成 Hamiltonian 和合成自旋块。真实材料、DFT/数据后端、DeepH/e3nn 软件、SOC/磁性实践范围和训练预算保留到 M8；M9 外部安装、数据或复现实验仍需明确授权。

## 1. 推导依赖与对象链

几何—表示主链为

\[
\text{主动 }SO(3)/O(3)\text{ 群作用}
\xrightarrow{\mathrm{D\mbox{-}E01}}
\text{不变/等变对象与行晶格桥接}
\xrightarrow{\mathrm{D\mbox{-}E02}}
\text{实 }s,p,d\text{ 不可约表示}.
\]

复表示—耦合分支为

\[
\mathrm{D\mbox{-}E02}
\xrightarrow{\mathrm{D\mbox{-}E03}}
\text{DLMF 复球谐、Wigner }D\text{ 与 }K_\ell
\xrightarrow{\mathrm{D\mbox{-}E04}}
\text{CG 选择定则与张量积 intertwiner}.
\]

Hamiltonian 与消息分支为

\[
\{\mathrm{D\mbox{-}E01},\mathrm{D\mbox{-}E02},
\mathrm{D\mbox{-}E03}\}
\xrightarrow{\mathrm{D\mbox{-}E05}}
\text{实/复 }s,p,d\text{ Hamiltonian 双侧协变},
\]

\[
\{\mathrm{D\mbox{-}E01},\ldots,\mathrm{D\mbox{-}E04},
\text{阶段 D 周期图}\}
\xrightarrow{\mathrm{D\mbox{-}E06}}
\text{径向—filter—CG—聚合—门控消息层},
\]

\[
\{\mathrm{D\mbox{-}E01},\mathrm{D\mbox{-}E02},
\mathrm{D\mbox{-}E05}\}
\xrightarrow{\mathrm{D\mbox{-}E07}}
\text{局部不变预测与全局回拉}.
\]

高级物理接口为

\[
\{\mathrm{D\mbox{-}E01},\mathrm{D\mbox{-}E03},
\mathrm{D\mbox{-}E04},\mathrm{D\mbox{-}E05}\}
\xrightarrow{\mathrm{D\mbox{-}E08}}
\text{SU(2)、反幺正时间反演与 Kramers 条件}.
\]

D-E09 横跨全部分支，统一维数、参数、局部 contraction、reference kernel、残差阈值、dtype、MAC/FLOP 和数组字节。前一箭头的表示或身份错误不能由后一箭头的小残差、拟合误差或同谱结果消除。

## 2. D-E01—D-E09 覆盖矩阵

| ID | 核心产物 | 强制条件 | 主要失败边界 | 推导文件 | 验证 |
|---|---|---|---|---|---|
| D-E01 | 主动/被动作用、复合、标量/极向量/轴向量/二阶张量与周期位移 | 列向量主动旋转、\(R_2R_1\)、\(R\in SO(3)\)、行晶格 \(A'=AR^{\mathsf T}\) | 转置/复合顺序错、反射混入 SO(3)、旋转时改写 shift | [15_group_actions_equivariance.md](15_group_actions_equivariance.md) | T-E01/02/07 |
| D-E02 | 实 \(s,p,d\) 表、STF 基、直和/multiplicity 和宇称 | 冻结实轨道顺序、\(B_a\) 正交归一、\(D^d_{ab}=\operatorname{tr}(B_a^TRB_bR^T)\) | d 顺序、漏归一化、错误 RBR 方向、极/轴混淆 | [16_real_spd_representations.md](16_real_spd_representations.md) | T-E03/07/12 |
| D-E03 | DLMF-CS 复球谐、Wigner D、\(C_\ell/K_\ell\)、点值/系数作用 | \(m\) 升序；点值 \(D^*\)、系数 D；完整 shell/mask/edge 同步 | 漏相位/共轭、m 逆序、函数/系数映射混用、partial shell | [17_spherical_harmonics_wigner.md](17_spherical_harmonics_wigner.md) | T-E04/06/07/12 |
| D-E04 | CG--3j、选择定则、\(1\otimes1\)、\(1\otimes2\)、intertwiner 与相位自由 | 冻结输入快轴、输出 \(L,M\)、DLMF 表、宇称乘法和整通道相位边界 | 局部/部分 M 相位、单系数、轴交换漏相位、错误 STF 比例 | [18_tensor_products_clebsch_gordan.md](18_tensor_products_clebsch_gordan.md) | T-E04/05/07/08/12 |
| D-E05 | 非方/多壳层 Hamiltonian \(H'_{ij}=D_iH_{ij}D_j^\dagger\)、逆边和实复路线 | receiver/bra 左、sender/ket 右；完整 shell/轨道/basis/edge provenance | 只左乘、漏 \(\dagger\)、左右交换、轨道行错位 | [19_equivariant_graph_hamiltonian.md](19_equivariant_graph_hamiltonian.md) | T-E06/12 |
| D-E06 | \(z^{cf}=\overline{y^{pv}}\)、CG 消息、receiver sum、同型混合和宇称门控 | 非零方向、两个 coefficient D 输入、合法 CG/宇称、完整 edge/path 身份 | 直接输入 D* 点值、错 CG/方向、高阶逐分量非线性、坏门控 | [18_tensor_products_clebsch_gordan.md](18_tensor_products_clebsch_gordan.md)、[19_equivariant_graph_hamiltonian.md](19_equivariant_graph_hamiltonian.md) | T-E07/08/12 |
| D-E07 | 唯一右手局部架、局部块不变和 \(4\times8\) 全局回拉 | 有限正尺度、两向量非零、\(\eta>\tau_{frame}\)、无后备轴 | 零/共线/阈值等号、正负有限跳变、任意后备轴、错误回拉 | [19_equivariant_graph_hamiltonian.md](19_equivariant_graph_hamiltonian.md) | T-E09/12 |
| D-E08 | SU(2) lift、\(\Theta=JK\)、\(\Theta^2=\pm I\)、H/S k-pair 与 Kramers/TRIM | 标准 Pauli、自旋顺序 \((+1/2,-1/2)\)、\(J_c=KJ_rK^T\)、H 时间反演不变 | 漏共轭、错 J/K†、k partner 错位、Zeeman 破缺、一般 k 误判 | [20_spin_time_reversal_complex.md](20_spin_time_reversal_complex.md) | T-E11/12 |
| D-E09 | 表示维数、参数/局部成本、reference kernel、残差/dtype 和 144 点扫描口径 | 冻结 A/B、G_A/G_B、PCG64、scan/config 互斥、逐数组 total/peak | 局部预算冒充端到端、MAC 冒充 FLOP、漏数组、删点、wall-time 入 hash | 本索引第 4 节及六份推导的 D-E09 子节 | T-E10/12 |

## 3. 跨推导不变量

### 3.1 群作用、复合与离散身份

- 三维对象统一使用列向量主动作用，先 \(R_1\) 后 \(R_2\) 为 \(R_2R_1\)；表示满足 \(D(R_2R_1)=D(R_2)D(R_1)\)。
- 周期行晶格为 \(A'=AR^{\mathsf T}\)，边位移行向量为 \(d'=dR^{\mathsf T}\)。旋转不改变 structure ID、receiver、sender、整数 shift、完整 edge key/ID 或 row order。
- 节点置换、换胞、空间旋转、反演和时间反演是不同作用。每个作用必须给出自己的离散身份映射，不能用一个通过结果替代另一个。

### 3.2 表示、基和 component

- 实轨道顺序固定为 \(s\)、\((p_x,p_y,p_z)\)、\((d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2})\)。复 \(m\) 顺序为 \(-\ell,\ldots,+\ell\)；自旋顺序为 \((+1/2,-1/2)\)。
- \(C_\ell\) 是函数点值映射，\(K_\ell=C_\ell^*\) 是 coefficient 映射。普通线性算符使用 \(KAK^\dagger\)，反幺正 unitary part 使用 \(KJK^T\)。
- complete irrep shell 的 component mask 只能全真或全假。basis change、CG、Hamiltonian、J、padding 切除/回填和 provenance 必须使用同一 shell/component 置换。

### 3.3 球谐、CG 与消息接口

复球谐点值满足

\[
y^{pv}(R\widehat d)=D(R)^*y^{pv}(\widehat d).
\]

进入 coefficient CG 前必须在同一 edge row 构造

\[
z^{cf}=\overline{y^{pv}},
\qquad
z^{cf}(R\widehat d)=D(R)z^{cf}(\widehat d).
\]

CG 只收缩表示 component；edge、node、multiplicity、path、shell 和 actual orbital/spin identity 均不得被隐式收缩或独立排序。整条不可约输出通道同步相位是基自由；局部 M、单系数或未同步元数据变化是规范错误。

### 3.4 Hamiltonian、逆边与时间反演

Hamiltonian 块是 \(\mathcal V_j\to\mathcal V_i\) 的映射：

\[
H'_{ij}=D_iH_{ij}D_j^\dagger,
\qquad
H_{ji,-n}=H_{ij,n}^\dagger.
\]

Bloch 时间反演另满足

\[
H(-k)=JH(k)^*J^\dagger,
\qquad
S(-k)=JS(k)^*J^\dagger.
\]

prediction、target、mask、左右 shell/component、actual orbital/spin、edge/k-partner 和 provenance 必须共享统一行映射。相同 shape、同谱或排序后数值接近不能证明身份合同。

### 3.5 宇称、反幺正与定义域

- \(SO(3)\) 正旋转不检验 \(O(3)\) 宇称。类型 \((\ell,p)\) 的 CG 输出宇称为输入宇称乘积；普通门值必须是偶标量，伪标量门控必须显式更新类型。
- 时间反演采用 \(\Theta=JK\) 和 \(\Theta^2=JJ^*\)。spin half 的平方为 -I；但 Kramers 还要求 H 时间反演不变，Bloch 同 k 简并还要求 TRIM。
- 局部架只在严格非退化定义域成立；时间反演/Kramers 也只在其 Hilbert、对称性和 k-fiber 条件成立时使用。阈值或代数对象不能消除定义域条件。

### 3.6 残差、误差和决定性失败

统一归一化残差为

\[
\rho(A,B)=
\frac{\lVert A-B\rVert_F}
{\max(1,\lVert A\rVert_F,\lVert B\rVert_F)}.
\]

float64/32 通过阈值为 \(5\times10^{-12}\)/\(5\times10^{-6}\)，等号接受。非法 dtype/rank/shape、非有限值、validator 拒绝侧、mask/provenance 冲突必须在数值 kernel 前硬拒绝。定向错误使用冻结非对称夹具并要求残差至少 \(10^{-4}\)；整体相位等合法基自由不能被误判为数学失败。

## 4. D-E09 完整维数、精度与成本口径

### 4.1 表示维数与同型参数

对 multiplicity \((n_0,n_1,n_2)\)，节点表示维数为

\[
d_{node}=n_0+3n_1+5n_2.
\]

只在同型 multiplicity 轴使用一般线性权重时，参数数为

\[
n_{param}=n_0^2+n_1^2+n_2^2.
\]

配置 A 的 \((3,2,2)\) 给 \(d_{node}=19,n_{param}=17\)；配置 B 的 \((5,4,3)\) 给 \(32,50\)。这些数不含 CG 固定系数、径向网络、偏置、Hamiltonian 输出头或自旋扩维。

### 4.2 reference kernel 与精确 MAC/FLOP

T-E10 的冻结同型逐边线性消息为

\[
m_{\ell,e,a,k}
=\sum_{b=1}^{n_\ell}
W_{\ell,e,a,b}
x_{\ell,\operatorname{sender}(e),b,k},
\]

\[
h'_{\ell,i,a,k}
=\sum_{e:\operatorname{receiver}(e)=i}m_{\ell,e,a,k},
\]

其中扫描模式 \(n_\ell=m(2,2,1)_\ell\)。数组 shape 为

\[
x_\ell:(N,n_\ell,2\ell+1),
\quad
W_\ell:(E,n_\ell,n_\ell),
\]

\[
m_\ell:(E,n_\ell,2\ell+1),
\quad
h'_\ell:(N,n_\ell,2\ell+1).
\]

精确 contraction 成本为

\[
\operatorname{mac}_{perR}
=\sum_{\ell=0}^{2}E n_\ell^2(2\ell+1),
\]

\[
\operatorname{mac}_{total}=n_R\operatorname{mac}_{perR},
\qquad
\operatorname{flop}_{total}=2\operatorname{mac}_{total}.
\]

2 FLOP/MAC 只适用于这个实 reference contraction。receiver 聚合加法另报：

\[
\operatorname{aggadd}_{perR}
=\sum_{\ell=0}^{2}
\left[\sum_i\max(\deg^-_i-1,0)\right]
n_\ell(2\ell+1).
\]

旋转生成、validator、归一化、CG、球谐、Hamiltonian 双侧乘法、局部架、自旋 complex MAC、非线性和内存移动都不在该 FLOP 字段中；实际执行时若存在，必须按独立操作图另报。

### 4.3 数组字节与 peak 定义

令目标浮点 dtype 的单元素字节数为 \(b\)，\(c_\ell=2\ell+1\)。正式逐数组合同为：

| 名称 | shape | dtype | nbytes |
|---|---|---|---:|
| coordinates | \((N,3)\) | target float | \(3Nb\) |
| receiver | \((E,)\) | int64 | \(8E\) |
| sender | \((E,)\) | int64 | \(8E\) |
| shift | \((E,3)\) | int64 | \(24E\) |
| rotations | \((n_R,3,3)\) | target float | \(9n_Rb\) |
| \(x_\ell\), each \(\ell=0,1,2\) | \((N,n_\ell,c_\ell)\) | target float | \(Nn_\ell c_\ell b\) |
| \(W_\ell\), each \(\ell=0,1,2\) | \((E,n_\ell,n_\ell)\) | target float | \(En_\ell^2b\) |
| \(m_\ell\), each \(\ell=0,1,2\) | \((E,n_\ell,c_\ell)\) | target float | \(En_\ell c_\ell b\) |
| \(h'_\ell\), each \(\ell=0,1,2\) | \((N,n_\ell,c_\ell)\) | target float | \(Nn_\ell c_\ell b\) |

这里 `rotations` 唯一指由规范单位四元数转换得到、C-order、目标 dtype、shape 严格为 \((n_R,3,3)\) 的旋转矩阵数组。PCG64 首先物化 C-order float64、shape \((n_R,4)\) 的 `quaternion_gaussian_raw`，再形成目标 dtype、同 shape 的规范单位四元数工作数组；旋转矩阵形成后，这两个四元数数组均在抽取 \(x_0\) 之前释放。它们是旋转生成预处理临时量，不属于上述命名数组，不计入 `array_bytes_total`，也不计入 reference contraction 的 `array_bytes_peak`。这一排除不改变随机数抽取顺序；若另报旋转生成阶段峰值，必须使用单独字段和操作图。

定义

\[
S_x=\sum_{\ell=0}^2 n_\ell c_\ell,
\qquad
S_W=\sum_{\ell=0}^2n_\ell^2.
\]

则

\[
\begin{aligned}
\mathrm{array\_bytes\_total}
={}&3Nb+40E+9n_Rb\\
&+2NS_xb+ES_Wb+ES_xb,
\end{aligned}
\]

而 reference 流式调度的峰值为

\[
\begin{aligned}
\mathrm{array\_bytes\_peak}
={}&3Nb+40E+9n_Rb\\
&+2NS_xb+ES_Wb
+\max_\ell(En_\ell c_\ell b).
\end{aligned}
\]

`array_bytes_total` 是表中命名数组各完整物化一次的总和；reference `array_bytes_peak` 是 coordinates、edge arrays、rotations、全部 \(x,W\) 与预分配 \(h'\) 常驻，再加单个最大 \(m_\ell\) 的流式峰值。

对 float64、\(n_R=1\)、\((n_0,n_1,n_2)=(2,2,1)\)，逐项字节为：

| 数组族 | \(G_A:(N,E)=(4,8)\) | \(G_B:(N,E)=(7,18)\) |
|---|---:|---:|
| coordinates | 96 | 168 |
| receiver | 64 | 144 |
| sender | 64 | 144 |
| shift | 192 | 432 |
| rotations \((1,3,3)\) | 72 | 72 |
| all \(x_\ell\) | 416 | 728 |
| all \(W_\ell\) | 576 | 1296 |
| all \(m_\ell\) | 832 | 1872 |
| all \(h'_\ell\) | 416 | 728 |
| **total** | **2728** | **5584** |

最大单个消息数组均为 \(m_1\)，字节分别为 384 和 864；所以 reference peak 分别为 \(2728-832+384=2280\) 与 \(5584-1872+864=4576\)。

NumPy 未暴露临时量、解释器/allocator 和 BLAS workspace 均明确排除。若实现加入 CG、Hamiltonian、J、k-partner 或其他数组，必须在对应操作图中逐名补报，不能塞入未修改定义的 reference total/peak。

### 4.4 A/B、144 点与整数锚点

固定配置为：

| 配置 | seed | dtype | \(n_R\) | multiplicity | 图 \((N,E)\) | scale |
|---|---:|---|---:|---|---|---:|
| A | 20260809 | float64 | 64 | \((3,2,2)\) | \((4,8)\) | 1 |
| B | 20260810 | float32 | 257 | \((5,4,3)\) | \((7,18)\) | \(10^3\) |

扫描模式 `stageE-scan-v1` 与 A/B 互斥，完整枚举

\[
\{\mathrm{float64},\mathrm{float32}\}
\times\{20260809,20260810\}
\times\{1,8,64,257\}
\times\{1,2,4\}
\times\{10^{-3},1,10^3\},
\]

共 144 点。seed 唯一选择冻结图 \(G_A:(4,8)\)/\(G_B:(7,18)\) 和 PCG64 draw order；scale 只缩放非零连续几何/特征，不改变 edge identity。

在 float64、\(n_R=1,m=1\) 时，独立整数锚点为：

| 图 | mac_per_rotation | aggregation_add_per_rotation | array_bytes_total | array_bytes_peak |
|---|---:|---:|---:|---:|
| \(G_A\) | 168 | 52 | 2728 | 2280 |
| \(G_B\) | 378 | 143 | 5584 | 4576 |

这些值必须从图度数、shape 和逐数组 nbytes 重算。M7-08 阶段只冻结推导；完整 A/B、144 点、双子进程规范 JSON 和失败矩阵随后已由 M7-09 执行，见 [代码说明](../../05_code_exercises/stageE_synthetic_equivariance/README.md) 与 [独立定点复核](../../08_audits/M7_stageE_code_blocking_reaudit.md)。可选 wall-time 使用 3 次 warm-up、7 次测量及 median/IQR 单独报告，绝不进入确定性 stdout/hash。

### 4.5 各章局部成本不能互换

- 第 16 章给表示维数、同型参数和节点值局部字节；
- 第 17 章给实/复 basis 数组局部字节；
- 第 18 章给 CG 乘积形成、非零缩放/零初始化 MAC 和真实累加；
- 第 19 章区分消息、聚合、Hamiltonian 双侧乘法和局部架；
- 第 20 章给显式自旋将 dense 元素数变 4 倍、`float64`→`complex128` 持久字节变 8 倍及 dense 双侧 MAC 变 8 倍的指定比较。

这些数字的操作图、dtype 和排除项不同。不得相加成“模型总成本”，也不得从解析比率推出具体软件 wall-time。

## 5. 章节、例题与练习入口

| 推导 | 正文与例题 | 问题与参考解答 |
|---|---|---|
| D-E01/D-E09 | [第 15 章](../../03_textbook/chapters/15_geometric_transformations_equivariance/) | [第 15 章练习](../../06_exercises/05-stageE/15_geometric_equivariance/) |
| D-E02/D-E09 | [第 16 章](../../03_textbook/chapters/16_groups_representations/) | [第 16 章练习](../../06_exercises/05-stageE/16_groups_representations/) |
| D-E03/D-E09 | [第 17 章](../../03_textbook/chapters/17_spherical_harmonics_wigner/) | [第 17 章练习](../../06_exercises/05-stageE/17_spherical_harmonics_wigner/) |
| D-E04/D-E06/D-E09 | [第 18 章](../../03_textbook/chapters/18_tensor_products_clebsch_gordan/) | [第 18 章练习](../../06_exercises/05-stageE/18_tensor_products_clebsch_gordan/) |
| D-E05—D-E07/D-E09 | [第 19 章](../../03_textbook/chapters/19_equivariant_graph_hamiltonian/) | [第 19 章练习](../../06_exercises/05-stageE/19_equivariant_graph_hamiltonian/) |
| D-E08/D-E09 | [第 20 章](../../03_textbook/chapters/20_spin_time_reversal_complex/) | [第 20 章练习](../../06_exercises/05-stageE/20_spin_time_reversal_complex/) |

## 6. 来源等级与证据边界

- PRIMARY_EXPLICIT：E-FND-01/02/03、E-GNN-01/02、DH-02 直接给出的复球谐、CG/3j、群/时间反演、等变张量机制和论文级 Hamiltonian 方法对象。
- DIRECT_DERIVATION：从冻结作用、基、CG、线性映射、反幺正和数组 shape 逐式推出的实/复表示、消息、回拉、Kramers 与成本公式。
- PEDAGOGICAL：固定旋转、STF/CG 数值锚点、合成图、合成 \(4\times8\)/\(2\times2\) Hamiltonian、阈值夹具和故障注入。

来源快照、hash、用途和限制见 [阶段 E 来源索引](../../01_sources/documentation/stageE/README.md) 与[工作包](../../08_audits/M7_stageE_work_package.md)。TFN/e3nn 不证明周期 Hamiltonian schema，DH-02 不选择仓库/数据/材料/DFT/SOC 实践，MIT 量子讲义不定义 DeepH 软件接口。项目阈值、图、payload/hash 和数组顺序均应标成显式教学冻结。

## 7. T-E01—T-E12 可执行映射

| T-E | 主要推导入口 | 正向对象 | 强制失败摘要 |
|---|---|---|---|
| T-E01 | D-E01 | Haar 四元数、R validator、逆/群复合/确定性 | 非有限/零四元数、反射、错顺序/seed |
| T-E02 | D-E01 | 标量、极向量、轴向量、二阶张量 | 主动/被动、只左乘、极/轴混淆 |
| T-E03 | D-E02 | \(D^p,D^d\) 正交/群律/STF | d 错序/归一化/RBR 方向 |
| T-E04 | D-E03/D-E04 | K 幺正、Wigner 相似、点值协变、实复交叉 | 相位、m 逆序、漏共轭/Euler 错口径 |
| T-E05 | D-E04 | CG 全表、锚点、正交/完整/intertwiner | 局部相位、单系数、交换漏相位；合法整通道相位不误杀 |
| T-E06 | D-E03/D-E05 | 多 shape H 双侧、逆边、实复、provenance | 只左、漏 dag、左右/轨道/edge 错位 |
| T-E07 | D-E01/02/04/06 | 反演、宇称和合法门控 | 正旋转冒充宇称、轴/极、伪标量坏门控 |
| T-E08 | D-E04/D-E06 | 复 filter、逐层/端到端消息、置换 | D* 点值直入 CG、错通道/方向、非线性 |
| T-E09 | D-E07 | 非退化架、局部不变、全局回拉 | 零/共线/等号、后备轴、正负跳变、错回拉 |
| T-E10 | D-E09 | A/B、144 点、MAC/FLOP/聚合/bytes | 模式混用、图漂移、删点、漏数组、wall-time 入 hash |
| T-E11 | D-E08 | SU(2)、反线性、Theta 平方、J/D、H/S k-pair、Kramers | 漏共轭、错 J/Kdag、partner、Zeeman、一般 k 误判 |
| T-E12 | D-E01—09 | 全 schema、mask、版本/hash、失败 rejected/total、授权扫描 | 广播、非有限、错 identity/padding、未执行失败、外部依赖 |

正式代码和全部强制失败已在 M7-09 建设并通过独立定点复核。本推导包冻结唯一 oracle、条件、阈值和失败语义；章内 NumPy 复算本身仍不冒充 [正式 CLI、双子进程或 144 点执行证据](../../05_code_exercises/stageE_synthetic_equivariance/README.md)。

## 8. M7-08 验收

M7-08 通过需要：

- D-E01—D-E09 全部可从本索引定位到逐式推导、正文、例题、问题、参考答案和 T-E 入口；
- 每项推导的对象域、rank/shape、dtype、基/component、成立条件、解析正反例和最终不变量明确；
- 主动/被动、点值/coefficient、C/K、CG 相位、Hamiltonian 左右作用、局部架定义域、反幺正基变换和 Kramers 条件无跨文件偷换；
- D-E09 的 reference kernel、A/B、144 点、MAC/FLOP、聚合、逐数组/total/peak 和 wall-time 边界唯一；
- 七个推导文件严格 Pandoc/MathML、活动链接、Raw TeX、数学节点外 TeX 和原始字符流控制字符检查通过；
- 独立子 agent 判定 `BLOCKING=0`、`NON_BLOCKING=0`，并明确允许 M7-09。

## 9. M8/M9 边界

本推导包不构成实践方案选择。M7-11 和 D-011 的 `gpt-5.6-sol`/`max` M3—M7 全量总审计通过后，才准备 M8 决策冻结。M8 冻结后，在 M9 正式安装 DeepH/e3nn、下载正式数据、生成 DFT 标签或运行复现实验前仍需明确执行授权。
