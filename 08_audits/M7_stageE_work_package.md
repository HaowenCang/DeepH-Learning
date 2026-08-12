# M7 阶段 E 材料建设工作包

## 1. 状态与授权边界

- 里程碑：M7 群表示与等变网络
- 当前状态：`COMPLETED`
- 当前任务：M7-11 已完成；后续进入 D-011 的 M7-I
- 进入依据：`M6_stageD_final_independent_audit.md` 判定 `PASS`、问题为 0，并明确允许 M7 启动
- 建设模式：材料完备性、可自学性与可验证性门控
- 实现范围：固定 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0；仅使用确定性合成表示、合成 Hamiltonian 块和合成图
- 禁止事项：M8 前不安装 DeepH/e3nn 本体，不下载正式训练数据，不生成 DFT 标签，不选择材料体系、DFT/数据后端、DeepH 软件对象或实践版本

学习者闭卷作答、口头解释和逐阶段自测不构成本阶段阻塞条件。每项能力必须由教材、推导、例题、练习与参考解答、代码、自动测试、强制失败样例和独立审计共同覆盖。自旋、SOC、磁性和复杂双群实现只在第 20 章建立接口；纳入首个正式实践的范围保留到 M8。

## 2. 任务分解

| ID | 任务 | 状态 | 完成证据 |
|---|---|---|---|
| M7-01 | 工作包、直接来源、统一表示约定和第 15—20 章三级提纲 | `COMPLETED` | 原独立审计员第二次定点复核关闭 B01/B02/N01，新增及剩余问题为 0，允许 M7-02 |
| M7-02 | 第 15 章几何变换、不变量与等变性 | `COMPLETED` | 第二次定点复核 `PASS`，原问题和 R1-N01 全部关闭，新增及剩余问题为 0，允许 M7-03 |
| M7-03 | 第 16 章群、表示、不可约表示与 \(s,p,d\) | `COMPLETED` | 独立内容审计 `PASS`，`BLOCKING=0`、`NON_BLOCKING=0`，允许 M7-04 |
| M7-04 | 第 17 章球谐函数与 Wigner \(D\) | `COMPLETED` | 原审计员定点复核 `PASS`，B01/B02/N01 全部关闭，新增及剩余问题为 0，允许 M7-05 |
| M7-05 | 第 18 章张量积与 Clebsch--Gordan 耦合 | `COMPLETED` | 原审计员定点复核 `PASS`，B01/B02/N01 全部关闭，新增及剩余问题为 0，允许 M7-06 |
| M7-06 | 第 19 章等变图网络与 Hamiltonian 块 | `COMPLETED` | 第二次定点复核 `PASS`；N01 关闭，B01/B02 无回归，问题总数 0，允许 M7-07 |
| M7-07 | 第 20 章自旋、时间反演与复表示接口 | `COMPLETED` | 原审计员定点复核 `PASS`；B01/N01 关闭，新增及剩余问题 0，允许 M7-08 |
| M7-08 | 阶段 E 解析推导包 | `COMPLETED` | 原审计员定点复核 `PASS`；B01/B02 关闭，新增及剩余问题 0，允许 M7-09 |
| M7-09 | 合成表示、等变层、自动测试与失败矩阵 | `COMPLETED` | 原审计员定点复核 `PASS`；B01—B05 全部关闭，新增及剩余问题 0，允许 M7-09 完成 |
| M7-10 | 自学导航、表示追踪模板与综合题解 | `COMPLETED` | 原独立审计员定点复核 `PASS`；B01—B05 全部关闭，新增及剩余问题为 0，允许 M7-11 |
| M7-11 | 阶段 E 正式独立材料总审计 | `COMPLETED` | `M7_stageE_final_independent_audit.md` 判定 `PASS`、问题为 0，明确允许 M7 完成并进入 M7-I，不授权直接进入 M8 |

M7-11 通过后仍不能直接进入 M8；须先执行 D-011 的 M7-I，由 `gpt-5.6-sol`、`max` 独立子 agent 对 M3—M7 进行全量总审计，并由主 agent 修复、原审计员复核至问题为 0。

## 3. 直接来源与证据边界

| ID | 直接用途 | 可以支持 | 不得外推 |
|---|---|---|---|
| E-FND-01 | 复球谐 | DLMF 归一化、Condon--Shortley 相位、共轭关系 | 不自动确定实轨道顺序、Wigner 数组轴或主动/被动方向 |
| E-FND-02 | CG/\(3j\) | 系数关系、选择定则、对称性和正交关系 | 不自动确定神经网络张量布局或软件 API |
| E-FND-03 | 群与量子对称性 | \(SO(3)\)/\(SU(2)\)、角动量耦合、宇称、时间反演、Kramers 条件 | 不定义 DeepH 轨道 schema、SOC 数据或软件版本 |
| E-GNN-01 | Tensor Field Networks | 按表示类型组织特征、球谐滤波和 CG 张量积的等变机制 | 点云架构不直接证明周期 Hamiltonian 块、provenance 或误差指标正确 |
| E-GNN-02 | e3nn 论文 | \(E(3)\) 表示、宇称、张量积和等变操作的统一对象 | 论文不选择 e3nn 发布版本，也不授权安装或断言与 DeepH 兼容 |
| DH-02 | DeepH-E3 论文 | \(E(3)\)-等变 Hamiltonian 表示的论文级任务联系与方法边界 | 不据此选择仓库、数据集、材料、DFT 设置、SOC 路线或复现对象 |
| 阶段 B/D 已审材料 | 基与周期图 | 轨道块、完整边键、换胞、Hermiticity、batch/mask/provenance | 不把置换或周期协变等同于旋转等变 |

来源快照、固定哈希和访问日期见 [stageE/README.md](../01_sources/documentation/stageE/README.md)。所有“实 \(d\) 张量基”“随机四元数夹具”“局部架退化反例”和归一化残差阈值均属于在直接来源对象上的显式约定或教学构造，必须据实标记。

## 4. 冻结表示契约

阶段 E 的唯一主约定见 [stageE_representation_conventions.md](../03_textbook/stageE_representation_conventions.md)，至少包括：

- 列向量主动旋转与 \(R_2R_1\) 复合顺序；
- DLMF 复球谐、\(m=-\ell,\ldots,\ell\) 顺序和 Wigner \(D\) 的操作定义；
- 实 \(p=(p_x,p_y,p_z)\) 与正交归一实 \(d=(d_{xy},d_{yz},d_{zx},d_{x^2-y^2},d_{3z^2-r^2})\)；
- \(D^d_{ab}(R)=\operatorname{tr}(B_a^{\mathsf T}RB_bR^{\mathsf T})\)；
- \(O(3)\) 宇称、极向量/轴向量区别与 CG 输出顺序；
- Hamiltonian 块 \(H_{ij}(RX)=D_iH_{ij}(X)D_j^\dagger\)；
- 无自旋 \(\Theta=K\) 与自旋 \(1/2\) 接口 \(\Theta=i\sigma_yK\)；
- 统一归一化 Frobenius 残差、float64/float32 阈值和定向错误下界。

正文、推导、代码、题面和解答出现不同约定时，应判定为阻塞，而不是在比较前静默重排。

## 5. 解析推导门控 D-E01—D-E09

| ID | 必须完成的推导对象 | 成立条件与强制边界 | 对应章节 |
|---|---|---|---|
| D-E01 | 主动/被动变换、群作用、标量不变与向量/张量等变 | 明确列向量、复合顺序、正旋转/反射；给出转置方向错误反例 | 15 |
| D-E02 | \(SO(3)\)/\(O(3)\) 表示、不可约分解及实 \(s,p,d\) 矩阵 | 验证维数 \(2\ell+1\)、正交/幺正、群律、宇称；区分极向量和轴向量 | 16 |
| D-E03 | DLMF 复球谐、Wigner \(D\) 操作定义和复—实相似变换 | 固定 Condon--Shortley、\(m\) 顺序、实轨道顺序；错误共轭/相位必须失败 | 17 |
| D-E04 | CG 选择定则、正交性、\(1\otimes1=0\oplus1\oplus2\)、低阶 intertwiner 与通道相位自由 | 固定输入/输出索引顺序和 DLMF 规范表；区分合法整通道相位变换与局部/相对相位错误 | 18 |
| D-E05 | \(s,p,d\) Hamiltonian 子块和多壳层块对角协变 | 实/复基分别保留转置/共轭转置；与 Hermiticity、边逆向和轨道 provenance 同步 | 19 |
| D-E06 | 最小等变消息层：径向标量、球谐方向、CG 张量积、同型线性混合、标量门控 | 逐层证明 intertwiner；禁止把逐分量高阶非线性或架构名当作证明 | 19 |
| D-E07 | 局部坐标回拉/推出与显式等变比较 | 说明唯一性、连续性、符号规则；精确拒绝零向量/共线和近退化不连续 | 19 |
| D-E08 | \(SU(2)\)、自旋 \(1/2\)、反幺正时间反演与 Kramers 接口 | 区分 \(\Theta^2=+I/-I\)；写明无磁场/时间反演不变等条件；不隐含选择 SOC 实践 | 20 |
| D-E09 | 表示维数、张量积/消息复杂度、残差归一化和精度误差预算 | 分离数学等变残差、浮点误差和模型误差；执行冻结 A/B 与 144 点网格，不得把可选 wall-time 当普遍成本结论 | 15—20 |

每项推导必须包含符号表、输入/输出维度、逐步推导、成立条件、至少一个解析例子、至少一个失败样例、T-E 映射和可独立复算的最终不变量。

## 6. 自动验证门控 T-E01—T-E12

### 6.1 共同环境与残差

固定运行时为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0。若环境再次缺包，按 D-009 使用精确 `requirements.txt` 安装并记录命令、实际版本和 `pip check`；不得借此安装 DeepH/e3nn。所有随机对象使用显式种子，CLI 相同参数的 stdout 必须字节一致。

统一残差为

\[
\rho(A,B)=\frac{\lVert A-B\rVert_F}{\max(1,\lVert A\rVert_F,\lVert B\rVert_F)}.
\]

float64 通过阈值为 \(5\times10^{-12}\)，float32 为 \(5\times10^{-6}\)。定向错误夹具须使用冻结非对称对象并达到 \(\rho\ge10^{-4}\)。所有通过率必须同时报告最大残差、最坏样例 ID、样本数、seed 和 dtype。

固定配置 A 为 seed 20260809、float64、64 个旋转、multiplicity \((3,2,2)\)、合成图 \((N,E)=(4,8)\)、尺度 1；配置 B 为 seed 20260810、float32、257 个旋转、multiplicity \((5,4,3)\)、合成图 \((7,18)\)、尺度 \(10^3\)。T-E01、T-E03—T-E10、T-E12 必须运行 A/B，并在两个独立子进程中复现不含 wall-time 的规范 JSON stdout。

旋转 validator、四元数符号规则、局部架零长度/无量纲退化阈值及边界夹具完全采用 [统一表示约定第 11 节](../03_textbook/stageE_representation_conventions.md)。T-E10 还必须执行 dtype \(\{\mathrm{float64},\mathrm{float32}\}\)、seed \(\{20260809,20260810\}\)、旋转数 \(\{1,8,64,257\}\)、multiplicity 倍率 \(\{1,2,4\}\)、尺度 \(\{10^{-3},1,10^3\}\) 的 144 点笛卡尔积。scan mode 与 config A/B 互斥，不允许任意覆盖网格字段；seed 20260809/20260810 分别映射到统一约定中显式冻结的 \(G_A:(N,E)=(4,8)\) 与 \(G_B:(7,18)\)，完整 edge identity、PCG64 抽样顺序和 dtype 转换均不得改变。

T-E10 使用统一约定冻结的同型逐边线性消息 kernel。确定性摘要必须同时给出 mac_per_rotation、mac_total、仅计 contraction 且按每 MAC=2 FLOP 换算的 flop_total，并将 receiver 聚合加法另行计数。数组字节必须逐名称给出 shape/dtype/nbytes，并按统一约定分别复算完整物化 array_bytes_total 和参考流式调度 array_bytes_peak；未暴露内部临时量和运行时开销明确排除。可选 wall-time 用 3 次 warm-up、7 次测量和 median/IQR 单独报告，不得进入 stdout hash。

### 6.2 测试矩阵

| ID | 正向测试 | 强制失败入口 |
|---|---|---|
| T-E01 | A/B 单位四元数 Haar \(SO(3)\)、正交性、\(\det=1\)、逆、群复合、规范符号与跨进程确定性 | 旋转/四元数阈值两侧、零/非有限四元数、反射、错误复合顺序、错误 seed 类型 |
| T-E02 | 标量、极向量、轴向量、二阶张量的不变/等变关系 | 主动/被动转置混淆、极/轴宇称混淆、只测单位矩阵 |
| T-E03 | \(D^p,D^d\) 的正交性、群律、\(d\) 基闭合和迹为零 | \(d\) 顺序交换、漏归一化、\(RBR^{\mathsf T}\) 写反 |
| T-E04 | \(\ell=1,2\) 复—实矩阵幺正、Wigner 相似变换、球谐点值协变 | 漏 Condon--Shortley 相位、\(m\) 逆序、漏共轭、错误 Euler 接口 |
| T-E05 | 低阶 CG 选择定则、正交性、维数、intertwiner；按 DLMF 规范表逐项比对并核对 \(1\otimes1\) 三个相位锚点 | 局部系数/部分 \(M\) 翻相位、输入轴互换未施加交换相位；整通道统一相位只在未同步规范元数据时触发“规范不一致”，不得宣称破坏等变性 |
| T-E06 | 合成 \(s/p/d\) Hamiltonian 块协变、Hermiticity、逆边和完整 provenance | 只左乘、右侧漏 \(\dagger\)、轨道行错位、旋转时改写离散 edge key |
| T-E07 | \(SO(3)\) 与含反演 \(O(3)\) 的宇称测试 | 用正旋转结果代替宇称、将轴向量按极向量处理 |
| T-E08 | 最小合成等变消息/张量积层逐层与端到端协变 | 高阶通道逐分量非线性、错误 CG 通道、消息边方向错位 |
| T-E09 | 按 \(\zeta=\lVert u\rVert/s\) 与 \(\eta=\lVert\widehat u\times\widehat v\rVert\) 的冻结阈值检查零向量、共线、阈值两侧和扰动序列 | 有量纲叉积阈值、任意后备轴、零除、等号方向错误、把单例成功外推全域 |
| T-E10 | 完整 144 点网格及 seed→固定图映射；冻结 kernel 的 MAC/FLOP、聚合加法、逐数组/total/peak 字节和可选 wall-time 分层记录 | config/scan 混用、图 shape 或 edge identity 漂移、MAC 冒充 FLOP、字节口径缺数组、删点、NaN 漏过、wall-time 混入 hash |
| T-E11 | \(\Theta=K\) 与 \(\Theta=i\sigma_yK\) 的平方、合成 \(H(-k)=JH(k)^*J^\dagger\) | 漏复共轭、\(\Theta^2\) 符号错、磁性破缺样例仍宣称时间反演通过 |
| T-E12 | dtype/rank/shape/有限性/表示标签/轨道顺序/seed/schema/旋转与局部架阈值/授权边界硬验证和全失败矩阵 | 非法对象被静默广播、阈值等号方向错误、实/复错配、重复或缺失表示块、出现正式数据/DeepH/e3nn 依赖 |

T-E12 必须实际执行所有故障注入，并报告 `rejected/total`；只列出预期异常而不运行不算通过。T-E06/T-E08 的旋转前后输出必须在同一完整边键和轨道身份下比较，不得先排序到不可追溯的纯数值数组。

## 7. 章节材料门控

每章至少具备 `sources.md`、`outline.md`、`chapter.md`、`examples.md`、解析推导、10 道分层练习和逐题参考解答。正文必须包含：概念定义、公式条件、对象维度、与前章接口、至少两个正确例子、至少两个失败例子、来源边界、数值验证入口、常见误区和章节小结。章节内容审计通过前不得进入下一章主体建设。

第 15—20 章的当前三级提纲分别位于：

- [第 15 章](../03_textbook/chapters/15_geometric_transformations_equivariance/outline.md)
- [第 16 章](../03_textbook/chapters/16_groups_representations/outline.md)
- [第 17 章](../03_textbook/chapters/17_spherical_harmonics_wigner/outline.md)
- [第 18 章](../03_textbook/chapters/18_tensor_products_clebsch_gordan/outline.md)
- [第 19 章](../03_textbook/chapters/19_equivariant_graph_hamiltonian/outline.md)
- [第 20 章](../03_textbook/chapters/20_spin_time_reversal_complex/outline.md)

## 8. 自学材料门控 C-E01—C-E12

综合题与参考解答必须一一对应并覆盖：

| ID | 能力对象 | 必须可验证的产物 |
|---|---|---|
| C-E01 | 主动/被动与群复合 | 对给定 \(R_1,R_2\) 写出唯一正确作用链和错误转置反例 |
| C-E02 | 标量、极向量、轴向量、张量 | \(SO(3)\)/\(O(3)\) 分类与宇称检查 |
| C-E03 | 实 \(s,p,d\) 表 | 从 \(B_a\) 推出 \(D^d\)，复算正交和群律 |
| C-E04 | 复球谐与 Wigner \(D\) | 复—实映射、相似变换和相位失败样例 |
| C-E05 | CG 耦合 | \(1\otimes1\) 分解、DLMF 三个相位锚点，以及合法整通道相位自由与局部相位错误的区别 |
| C-E06 | Hamiltonian 块 | \(s-p,p-p,p-d,d-d\) 子块协变和维度追踪 |
| C-E07 | Hermiticity 与边身份 | 旋转、逆边、周期 shift、轨道 provenance 的同步映射 |
| C-E08 | 等变消息层 | 逐层表示类型、张量积路径、门控与失败非线性 |
| C-E09 | 局部架 | 非退化回拉、共线拒绝和近退化不连续 |
| C-E10 | 精度与成本 | 归一化残差、float32/64 阈值和规模扫描解释 |
| C-E11 | 自旋与时间反演 | \(\Theta^2=\pm I\)、反幺正共轭和适用条件 |
| C-E12 | 端到端审计 | 来源—公式—代码—失败样例—授权边界完整追踪 |

自学导航必须建立“能力 → 教材 → 推导 → 例题 → 代码 → 失败样例 → 练习/解答”的正向矩阵和所有代码/失败入口的反向索引。表示追踪模板必须逐层记录 \((\ell,p)\)、multiplicity、dtype、shape、基顺序、作用方向、edge/provenance 和容差。

## 9. M7-01 独立审计门控

M7-01 完成本地主验后，必须由新的独立子 agent 审查且只允许其新增审计报告。审计至少回答：

1. 六章范围是否覆盖原计划且依赖顺序合理；
2. 主动/被动、复合顺序、复球谐相位、实 \(p,d\) 顺序和 Hamiltonian 左右作用是否全局唯一；
3. D-E01—D-E09 是否均有公式条件、失败边界和章节映射；
4. T-E01—T-E12 是否可执行、阈值明确并包含定向穿透；
5. 自旋/时间反演是否严格停留在 M7 理论接口，未隐含决定 M8 高级物理范围；
6. 来源快照、哈希、台账和 BibTeX 是否一致，论断是否超出证据边界；
7. M8/M9 禁令和 D-011 总审计是否完整保留。

只有独立报告给出 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0` 且明确允许 M7-02 时，M7-01 才能标记为 `COMPLETED`。若失败，主 agent 修复后交回同一审计员定点复核，主 agent 不自行关闭问题。
