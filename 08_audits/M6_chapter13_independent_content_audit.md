# M6-04 第 13 章正式独立内容审计

- 审计日期：2026-08-04
- 审计角色：独立内容审计子 agent
- 审计方式：只读逐行检查、公式重推、独立数值复算、来源快照核验与阶段授权边界核对
- 总结论：`FAIL`
- `BLOCKING=1`
- `NON_BLOCKING=0`
- M6-04：**不得完成**
- M6-05：**不得启动**

第 13 章已经正确冻结普通 MPNN 的 receiver/sender 方向、同步消息传递、全部主要张量形状、边级 masked MSE、scatter/gather 反向关系、节点与边置换一致性、有向前驱感受野、复杂度主项以及普通网络不自动具有旋转等变性的边界。八个例题与 Q13-01—Q13-10/A13-01—A13-10 的独立复算未发现公式或算术错误。当前唯一阻塞来自边输出 provenance：第 13 章只携带局部轨道下标数组，却遗漏工作包冻结的实际轨道身份或可独立解析这些身份所需的有序轨道表，因此尚不能保证每个预测分量可追溯到具体轨道对。

## 1. 审计范围与快照

送审材料包括：

- `03_textbook/chapters/13_message_passing_networks/sources.md`
- `03_textbook/chapters/13_message_passing_networks/outline.md`
- `03_textbook/chapters/13_message_passing_networks/chapter.md`
- `03_textbook/chapters/13_message_passing_networks/examples.md`
- `04_derivations/stageD/13_receptive_field_complexity.md`
- `06_exercises/04-stageD/13_mpnn/problem/readme.md`
- `06_exercises/04-stageD/13_mpnn/solution/readme.md`
- `03_textbook/stageD_graph_conventions.md`
- `08_audits/M6_stageD_work_package.md`
- 第 11 章的 MSE/梯度口径和第 12 章的图、批处理、连续 mask、轨道索引及 edge identity 冻结契约
- `00_scope/learning_route.md:108-135` 与 `00_scope/master_execution_plan.md:164-187` 的阶段 D 范围

审计开始时核心文件 SHA-256 为：

| 文件 | SHA-256 |
|---|---|
| `08_audits/M6_stageD_work_package.md` | `367B2AD67286FB89BA634A847655747C0EE837FF396A9764CB41A1A8A884E577` |
| `03_textbook/stageD_graph_conventions.md` | `BEBC75E5390E078A523331837E667DEE532919F1620F4037E11059888D05D265` |
| 第 13 章 `chapter.md` | `C58498D33C4F414EA4F9355CD96CA9AC43DC5DC05326EB2D4F3AD9EB773AE76B` |
| 第 13 章 `examples.md` | `281BFE61CFE5B35A81DEFA7DB369AD634B68AA03557FBAACE0B73D008940F248` |
| D-D04/D-D06 | `94D36A0C9206D186E1D2B64AF8D3E4ED835DC2FEA2E6A9F2655F27FB67F50E93` |
| Q13 | `420EA6C488541785E3357954D7534D92712601DF9490AE54A9967A1955B26B8D` |
| A13 | `127A6B175EE7876DFEA4F6BF74F394762FF94D7D763DAE00577A8D31AA7F84DE` |

未修改任何送审材料、计划、台账、README 或代码；唯一写入为本审计报告。

## 2. 问题清单

### M6-CH13-B01：边输出 provenance 遗漏实际轨道身份，不能把预测分量独立解析为具体轨道对

- 级别：`BLOCKING`
- 位置：
  - `03_textbook/chapters/13_message_passing_networks/chapter.md:170-180`
  - `06_exercises/04-stageD/13_mpnn/problem/readme.md:23-25`
  - `06_exercises/04-stageD/13_mpnn/solution/readme.md:70-72`
  - 对照 `08_audits/M6_stageD_work_package.md:153-160`
  - 对照 `03_textbook/chapters/12_atomic_graph_representation/chapter.md:225-237,269-299`
  - 对照 `00_scope/learning_route.md:127-131` 与 `00_scope/master_execution_plan.md:179-183`

工作包已经冻结：每个边输出应携带 `orbital_i`、`orbital_j`，并使每个预测分量可追溯；阶段 D 总范围也要求每个预测轨道块能够追溯到轨道索引。第 12 章进一步区分了两种对象：节点的有序实际轨道 ID 列表 `node_orbitals[i]`/`node_orbitals[j]`，以及逐分量局部下标 `orbital_i_index`/`orbital_j_index`。局部下标 α、β 只有与相应有序轨道列表结合，才能解析为实际轨道身份。

第 13 章的输出清单只有 `mask`、`orbital_i_index` 和 `orbital_j_index`，没有 `orbital_i`/`orbital_j` 实际身份，也没有要求输出携带或以稳定引用绑定 `node_orbitals`。例如两个节点都采用局部下标 `(0,1)`，但实际列表分别为 `['s','p_x']` 与 `['p_z','s']` 时，单凭当前输出可以知道局部行列号，却不能知道该分量是哪个实际轨道对。交换节点轨道列表而保持局部下标、shape、mask、receiver/sender 和预测数组不变，现有第 13 章断言仍可能通过。A13-06 只要求 provenance 随边行重排，没有检验局部下标到实际轨道身份的解析，因此没有关闭该缺口。

这不是命名偏好问题。若代码阶段照当前第 13 章的“必须原样携带”清单实现，预测块不能满足已冻结的端到端可追溯性，且一个轨道顺序漂移可在 shape、mask 和数值均合法时静默改变语义。因此该项阻塞 M6-04。

关闭条件：

1. 冻结一种无歧义的输出 schema。可以逐分量直接携带实际 `orbital_i_id`/`orbital_j_id`，也可以携带局部 index 并同时携带或稳定引用两端点的有序 `node_orbitals`；必须明确区分“局部整数下标”和“实际轨道身份”。
2. 对所有有效位置 (a) 断言
   \[
   (\texttt{orbital\_i\_id},\texttt{orbital\_j\_id})
   =
   (\texttt{node\_orbitals}[i][\alpha],
   \texttt{node\_orbitals}[j][\beta]),
   \]
   其中 \(\alpha=\lfloor a/p_j\rfloor\)、\(\beta=a\bmod p_j\)；padding 位置采用冻结的无效哨兵，并与右侧连续 mask 一致。
3. 明确预测、完整边键、mask、局部下标、实际轨道身份与 schema 版本在排序、批处理和反置换时采用同一行映射。
4. 在例题或 Q/A 中加入非平凡轨道 ID 列表和至少一个失败样例：局部下标及数量正确，但有序轨道表被交换、遗漏或与端点不一致时必须拒绝。修复后的材料应能让自学者独立恢复一个具体预测分量的结构、端点、周期镜像和实际轨道对。

## 3. 已通过项目

### 3.1 冻结教学架构、张量形状与同步方向

- `chapter.md:11-36` 明确 (i) 为 receiver、(j) 为 sender，消息沿 sender \(\to\) receiver 流动；同层全部消息读取同一个 \(H^{(t)}\)，禁止节点原地更新。例 13-1、例 13-2 与 A13-02/A13-03 的非对称夹具能区分方向错误和同层越级传播。
- `chapter.md:55-104` 冻结 row-vector 架构。独立形状复核得到：receiver/sender 两项为 \((E,d)(d,d)\)，边特征项为 \((E,d_e)(d_e,d)\)，消息为 \((E,d)\)，分段和及节点更新为 \((N,d)\)。Q13-01/A13-01 在 \(N=5,E=12,d=4,d_e=3,P_{\max}=6\) 时的 \(G=(12,11)\)、\(W_o=(11,6)\) 等全部正确。
- 空入边节点采用 sum=0 后只经 self 项更新；padding 在 gather、聚合和更新前排除。该口径与第 12 章已冻结批处理契约一致。

### 3.2 有向前驱感受野与边头两端点并集

- `chapter.md:106-124` 和 D-D04 正确定义 sender \(\to\) receiver 的有向最短路径。归纳步
  \[
  \mathcal N^-_L(i)\cup\bigcup_{j\to i}\mathcal N^-_L(j)
  =\mathcal N^-_{L+1}(i)
  \]
  在局部消息、同步更新、无全局状态条件下成立。
- D-D04 明确该结论给出“只可能依赖”的结构上界；零参数、激活饱和或聚合碰撞可使实际影响集合更小。全局节点、全图归一化、全连接注意力和同层原地更新会破坏证明条件；跳连本身不扩大图距离上界。
- 边头同时读取 \(h_i^{(L)}\) 与 \(h_j^{(L)}\)，故结构感受野为两端点的 \(L\) 层有向前驱邻域之并。例 13-3、例 13-5 与 A13-04 均与该结论一致。

### 3.3 边级输出、连续 mask、masked MSE 与反向传播

- 边头输入顺序固定为 receiver、sender、edge feature，\(G\in\mathbb R^{E\times(2d+d_e)}\)，有向端点交换一般会改变输出。
- `chapter.md:150-168` 明确调用第 12 章右侧连续 mask，使用有效元素数 \(S>0\)，逐有效元素损失与梯度
  \[
  L=\frac1S\sum_{e,a}\texttt{mask}_{ea}(\widehat y_{ea}-y_{ea})^2,
  \qquad
  \frac{\partial L}{\partial\widehat Y}=\frac2S(\widehat Y-Y)\odot\texttt{mask}
  \]
  正确；逐元素与逐结构等权口径被明确区分。例 13-4、例 13-7、A13-05 和 A13-08 的数值均正确。
- `chapter.md:184-241` 正确给出输出头矩阵梯度、边头两端点梯度 scatter-add、分段求和伴随的 receiver gather，以及 tanh 的 \(1-Y^2\) 局部导数。漏掉 \(1/S\)、把 receiver 改为 sender、把 tanh 导数写成 \(1-H\)、padding 梯度泄漏四类强制失败样例均可定向检测。
- 当前 B01 只否定实际轨道身份 provenance 的完备性，不否定 mask、损失或反向公式。

### 3.4 节点/边置换与旋转边界

- `chapter.md:243-267` 在共享参数、边端点同步重标、边属性同步重排和 sum 聚合条件下，正确得到 \(H'^{(L)}=PH^{(L)}\) 与 \(\widehat y'_{p(e)}=\widehat y_e\)。A13-06 还要求非对称节点特征、有向多重边和随机边行重排，能避免图级 sum 掩盖端点错误。
- `chapter.md:269-289` 正确区分离散节点重编号与三维旋转。只含距离可提供标量旋转不变输入，但不能自动给出轨道块的非平凡协变律；直接把笛卡尔位移送入普通 MLP 也不产生受控旋转表示。该问题被保留到阶段 E，没有把普通 MPNN 越权声明为旋转等变网络。

### 3.5 D-D06 时间与激活内存

- 独立重推冻结层：receiver/sender 投影为 \(O(Ed^2)\)，边特征投影为 \(O(Ed_ed)\)，节点 self/aggregate 更新为 \(O(Nd^2)\)，分段和为 \(O(Ed)\)，边头为 \(O(E(2d+d_e)P_{\max})\)。在 \(d_e=O(d),P_{\max}=O(d)\) 下，\(L\) 层主体和一次边头的总主项写为 \(O(L(E+N)d^2)\) 与文中一致。
- 缓存每层 \(H^{(t)},Z_m^{(t)},M^{(t)},A^{(t)},Z_u^{(t)}\) 时，float64 数组主项为 \(8L(3Nd+2Ed)\) 字节。D-D06 明确把输入、输出、mask、索引、参数、梯度、优化器状态和 Python 进程开销排除在该主项之外，因此没有把数组估计误报为进程峰值内存。
- Q13-07/A13-07 的数值为 `1,459,200 bytes`，即约 `1.39 MiB`，复算一致。

### 3.6 来源边界与 M8/M9 授权边界

- D-GNN-01 本地 PDF第 2—3 节确实给出消息函数、节点更新和置换不变图读出的一般框架；D-GNN-02 本地 PDF 第 2.1—2.2 节区分可数域与不可数域固定集合大小条件。材料没有把求和表示外推为任意连续无限集合上的无条件定理，也没有从该来源推出旋转等变。
- 五份阶段 D 直接来源快照的实测 SHA-256 均与 `01_sources/documentation/stageD/README.md` 一致。D-GNN-01 为 `292E7AD7...A9FDD8`，D-GNN-02 为 `AE1E9A46...F163C0`，D-FND-02 为 `95F2810D...E91A1`。
- 本地 DH-01 SHA-256 为 `92C5A783...580EC61`；原文只被用于普通 MPNN、局域原子环境与局域 Hamiltonian 块之间的任务接口。章节未复用论文材料、数据、后端、超参数或软件版本，也未把案例精度外推。
- `chapter.md:318-320` 明确只使用合成图和合成边标签。M8 前不安装 DeepH、不获取正式数据、不生成 DFT 标签、不选择正式材料或软件对象；M7 与 M7-I 通过后才进入 M8，M9 外部动作仍需用户明确授权。未发现隐含实践选择。

## 4. 独立复算记录

使用固定 Python 3.12.13、NumPy 2.3.5 和 float64，在不写入派生文件的条件下独立构造两层冻结教学网络并重写完整反向传播。复算未调用送审材料中的实现代码。

| 对象 | 独立结果 | 审计判断 |
|---|---:|---|
| 两层网络：每层 `Wr/Ws/Wf/bm/Uh/Ua/bu`、输出头 `Wo/bo`、输入 `H0` 共 17 个中心差分抽查 | 最大缩放误差 `1.935e-10` | 解析链式法则通过 |
| 随机节点置换 + 随机边行重排 | 节点最大绝对残差 `0.000e+00`；边输出 `0.000e+00` | 置换结论通过 |
| 非对称有向图 1—3 层结构依赖集合 | 全部等于有向前驱距离 \(\le L\) 的集合 | D-D04 通过 |
| masked MSE padding 输出梯度 | 最大绝对值 `0.000e+00` | mask 梯度通过 |
| Q13-05 | \(S=3,L=14/3\)，梯度为 \(\frac23[(1,-2,0),(3,0,0)]\) | 与 A13-05 一致 |
| 例 13-7 | 逐元素 `1.3`；逐结构等权 `2.5` | 一致 |
| Q13-08 | 逐元素 `1.6`；逐结构等权 `2.5` | 一致 |
| Q13-07 激活主项 | `1,459,200 bytes` | 一致 |

其余 Q13-01—Q13-04、Q13-06、Q13-09—Q13-10 为形状、证明或诊断题；逐项核对未发现 receiver/sender、同步更新、置换方向、旋转边界或 M8/M9 停点错误。Q13-06/A13-06 的实际轨道身份缺口计入 B01，不重复计数。

## 5. 文档与材料完整性检查

- 第 13 章三级提纲与正文的 28 个二/三级标题逐项、逐序完全一致。
- `examples.md` 含 8 个按 13-1—13-8 连续编号的例题；题目和解答目录均非空，Q13-01—Q13-10 与 A13-01—A13-10 为 10/10 一一对应。
- 七份第 13 章核心 Markdown 使用 Pandoc `markdown+tex_math_single_backslash`、MathML 和 `--fail-if-warnings` 只读渲染，7/7 通过，合计生成 190 个 MathML 节点；未使用 `-o`、`--output` 或任何输入覆盖方式。
- 两个活动本地 Markdown 链接均解析到现存目标；非法控制字符和 Unicode replacement character 均为 0。
- B01 修复前，材料形式完整，但边输出到实际轨道身份的自学与可验证链不完整。

## 6. 最终门控结论

正式结论为 `FAIL`，`BLOCKING=1`，`NON_BLOCKING=0`。M6-CH13-B01 必须由主 agent 修复，并由本审计员执行定点复核；主 agent 的自检不能替代独立复核结论。

在 B01 关闭且复核未发现新增问题之前：

- 不允许将 M6-04 标记为完成；
- 不允许启动 M6-05；
- 已通过的前向架构、感受野、反向传播、置换、复杂度、来源与授权边界结论可以保留，无需缩减教学范围。
