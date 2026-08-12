# 阶段 D 自学导航：监督学习、周期图与普通 MPNN

## 1. 使用方式与完成口径

阶段 D 把结构分组、监督回归、周期有向多重图、普通消息传递网络和边级轨道块输出连接为一条可审计对象链。依据材料建设模式，检查题、章节练习和综合题均保留参考解答与失败分析，但不要求学习者提交闭卷作答、口头解释或阶段自测。阶段完成证据来自来源受控的教材、D-D01—D-D07 推导、例题、逐题解答、T-D01—T-D10 自动测试、故障注入、张量追踪模板和独立审计。

本阶段只使用确定性合成晶胞、合成结构组、合成轨道身份和合成监督目标。M8 前不安装 DeepH，不下载正式训练数据，不生成 DFT 标签，也不选择材料体系、DFT/数据后端或 DeepH 软件对象；相应状态保持 `UNRESOLVED_M8`。

## 2. 前置条件与建议顺序

前置知识包括阶段 B 的行晶格、分数坐标、周期代表与广义本征对象，以及阶段 C 的标签语义、固定表示、误差分层和局域性边界。建议按下表顺序完成。

| 单元 | 核心问题 | 教材与推导 | 例题、练习与验证 |
|---|---|---|---|
| D1 监督学习与评价 | 样本、结构组、损失、梯度和测试集分别证明什么？ | [第 11 章](11_supervised_learning_optimization/chapter.md)；[D-D01/D-D02](../../04_derivations/stageD/11_supervised_gradients_leakage.md) | [例题](11_supervised_learning_optimization/examples.md)；[问题](../../06_exercises/04-stageD/11_supervised_learning/problem/readme.md)与[解答](../../06_exercises/04-stageD/11_supervised_learning/solution/readme.md)；T-D01—T-D03 |
| D2 原子图与置换 | receiver/sender、多重边、聚合与轨道块 schema 如何保持一致？ | [第 12 章](12_atomic_graph_representation/chapter.md)；[D-D03](../../04_derivations/stageD/12_permutation_aggregation.md) | [例题](12_atomic_graph_representation/examples.md)；[问题](../../06_exercises/04-stageD/12_atomic_graph/problem/readme.md)与[解答](../../06_exercises/04-stageD/12_atomic_graph/solution/readme.md)；T-D04/T-D07/T-D09 |
| D3 普通 MPNN | 同步消息、感受野、解析反传、mask 和复杂度如何验证？ | [第 13 章](13_message_passing_networks/chapter.md)；[D-D04/D-D06](../../04_derivations/stageD/13_receptive_field_complexity.md) | [例题](13_message_passing_networks/examples.md)；[问题](../../06_exercises/04-stageD/13_mpnn/problem/readme.md)与[解答](../../06_exercises/04-stageD/13_mpnn/solution/readme.md)；T-D02/T-D04/T-D08/T-D09 |
| D4 周期邻居表 | 有限镜像界、换胞协变、edge ID 和 provenance 如何闭合？ | [第 14 章](14_periodic_graph_neighbor_lists/chapter.md)；[D-D05/D-D07](../../04_derivations/stageD/14_periodic_enumeration_provenance.md) | [例题](14_periodic_graph_neighbor_lists/examples.md)；[问题](../../06_exercises/04-stageD/14_periodic_graph/problem/readme.md)与[解答](../../06_exercises/04-stageD/14_periodic_graph/solution/readme.md)；T-D05—T-D07/T-D10 |

每个单元按“对象和条件—逐式推导—例题—章节练习—代码正例—故障注入—综合题”核对。查看参考解答不使材料门控失效；关键数值和边键必须仍能从冻结输入、公式或代码独立复算。

### 2.1 能力到六类材料的正向映射

下表中的“代码”均指[阶段 D 合成实现](../../05_code_exercises/stageD_synthetic_mpnn/staged_models.py)与[验收驱动](../../05_code_exercises/stageD_synthetic_mpnn/run_experiments.py)。每项能力都必须能够从教材进入推导，再通过代码、练习和失败样例验证。

| 能力 | 教材 | 推导 | 代码入口 | 综合练习 | 必须观察的失败样例 |
|---|---|---|---|---|---|
| 按结构组无泄漏划分并解释评价对象 | 第 11 章 11.2/11.6 | D-D02 | `validate_group_split`、`group_split_evidence`，T-D01 | C-D01 | 逐帧划分产生组交集；分组污染被拒绝 |
| 推导 masked MSE 与多层解析梯度 | 第 11 章 11.3；第 13 章 13.4 | D-D01 | `masked_mse`、`backward_mpnn`、`finite_difference_gradient_error`，T-D02 | C-D02 | 五类错误反传分别超过 \(10^{-5}\) |
| 冻结生成式并评价未见结构组 | 第 11 章 11.4—11.6 | D-D02 | `grouped_regression`，T-D03 | C-D03 | 损坏 test 目标失败；逐帧表观误差不得替代新组 test |
| 证明节点置换、边行重排与聚合协变 | 第 12 章 12.3—12.5 | D-D03 | `make_edge_output`、`validate_edge_output`，T-D04 | C-D04 | 端点、prediction、mask 或轨道行任一错位被拒绝 |
| 建立周期代表变换的 \(K_q\) 双射 | 第 14 章 14.5 | D-D07 | `transformed_representatives`、`representative_residuals`，T-D05 | C-D05 | 固定 shift、按原行号或仅按原子对配对失败 |
| 推导有限镜像盒并验证枚举完备性 | 第 14 章 14.3 | D-D05 | `mirror_bounds`、`build_periodic_graph`，T-D06 | C-D06 | 固定小盒和最小镜像漏边 |
| 保留多重边和非零自镜像并冻结完整身份 | 第 12 章 12.1.3、12.5.3、12.6.2；第 14 章 14.4.2—14.4.3 | D-D05/D-D07 | `canonical_edge_payload`、`edge_instance_id`、`validate_graph`，T-D07 | C-D07 | 按 \((i,j)\) 或距离去重减少物理边 |
| 证明同步 \(L\) 层有向前驱感受野 | 第 13 章 13.2 | D-D04 | `predecessor_sets`、`linear_support_propagation`，T-D08 | C-D08 | 原地异步更新一层穿透多条边 |
| 从完整边键追踪到轨道块与两种 batch | 第 12 章 12.2.2—12.2.3、12.5.1—12.5.3；第 13 章 13.3 | D-D03/D-D07 | `make_orbital_provenance`、`make_concat_batch`、`make_padded_batch`，T-D09 | C-D09 | 36 类 shape、几何、padding、graph-ID 与 provenance 变异 |
| 分离复杂度、硬验证、证据边界与授权停点 | 第 11—14 章失败边界 | D-D06 | `activation_bytes`、`validate_cell`、`validate_cutoff`，T-D09/T-D10 | C-D10 | 病态/非有限对象、分组污染、非法 schema 和提前 M8 选择被拒绝 |

### 2.2 代码、练习和失败入口的反向索引

反向查找时，不能从“某测试通过”直接跳到扩大后的物理结论；应先回到相应能力、教材条件与推导前提。

| 从此入口开始 | 回查能力与教材 | 继续核对 |
|---|---|---|
| `backward_mpnn` 或任一 gradient fault | C-D02；第 11/13 章 | D-D01、T-D02、inactive padding 梯度 |
| `grouped_regression` 或极低逐帧误差 | C-D01/C-D03；第 11 章 | D-D02、group lineage、零基线与损坏目标 |
| edge-output/provenance validator 报错 | C-D04/C-D07/C-D09；第 12 章 | D-D03/D-D07、完整键、轨道表与行双射 |
| 周期边数或 shift 异常 | C-D05—C-D07；第 14 章 | D-D05/D-D07、解析盒、\(K_q\) 与自镜像规则 |
| 感受野或空入边异常 | C-D08；第 13 章 | D-D04、同步快照、sum/mean/max 策略 |
| concat/padded、NaN 或跨图边失败 | C-D09；第 12/13 章 | 张量追踪模板、T-D09 的完整 shape/几何契约 |
| benchmark、激活字节或 validator 边界 | C-D10；第 11—14 章 | D-D06、T-D09/T-D10 与 M8/M9 停点 |

## 3. D-D01—D-D07 能力—材料—验证映射

| 推导 | 可验证能力 | 正例或入口 | 关键失败边界 |
|---|---|---|---|
| D-D01 | 从 masked MSE 推出一至三层 MPNN 全参数梯度，并用中心差分检验 | T-D02；C-D02 | 数值梯度只是检查；漏 `1/S`、scatter 端点、tanh 导数或 padding mask 都可形状正确而数值错误 |
| D-D02 | 区分逐帧评价与新结构组评价，解释组共享潜变量导致的泄漏 | T-D01/T-D03；C-D01/C-D03 | 显式 group ID 无交集不排除重复结构、全数据预处理或标签复制 |
| D-D03 | 证明 sum 聚合的边序不变性与节点重编号等变性 | T-D04；C-D04 | 节点、端点、边行、预测和 provenance 必须同步；不推出旋转等变性 |
| D-D04 | 从同步局部消息推出 L 层有向前驱感受野 | T-D08；C-D08 | 原地异步更新、全局读出、跨图边或层内跳连会改变支持集 |
| D-D05 | 推出斜晶胞有限镜像枚举界，并量化病态晶胞条件 | T-D05/T-D06/T-D10；C-D05/C-D06 | 需要 float64、有限正 cutoff、非奇异且条件数小于 \(10^8\)；固定小盒和最小镜像一般不完备 |
| D-D06 | 区分候选枚举、保留边、MPNN 计算量和显式激活字节 | T-D09；C-D10 | 不得把 Python 进程常驻内存写成模型激活，也不能隐去 \(N,E,L,d\) |
| D-D07 | 在公共/逐原子周期代表变换下建立完整键双射和 edge provenance | T-D05/T-D07/T-D09；C-D05/C-D09 | 不得按原子对、距离或原行号折叠/配对；预测、mask 和实际轨道身份必须共享完整键 |

[阶段 D 推导总索引](../../04_derivations/stageD/README.md)给出前提、依赖和失败入口。[统一图约定](../stageD_graph_conventions.md)冻结行晶格、边方向、换胞和 edge ID。[张量追踪模板](../stageD_tensor_trace_template.md)用于逐字段审计。[综合问题](../../06_exercises/04-stageD/comprehensive/problem/readme.md)与[参考解答](../../06_exercises/04-stageD/comprehensive/solution/readme.md)用于端到端复核。

## 4. T-D01—T-D10 可执行映射

| 测试 | 验证对象 | 强制失败 | 不能推出的结论 |
|---|---|---|---|
| T-D01 | 三个结构组集合两两无交集 | 逐帧划分使三组交集均非空 | 不自动识别不同 ID 的重复物理结构 |
| T-D02 | A/B 分别覆盖 132/300 个参数坐标，中心差分误差不超过 \(10^{-5}\) | 五类实际错误反传逐项超过阈值 | 不验证任意自动微分框架或任意网络 |
| T-D03 | 冻结分组生成式、MPNN 规模和预算；独立组测试 MSE 低于 0.02 且低于零基线四分之一 | 训练下降但损坏测试目标失败；逐帧表观误差不能替代新组误差 | 0.02 不是正式 Hamiltonian 精度目标 |
| T-D04 | 非对称图的节点置换、边行重排和完整输出 schema 映射 | 端点未重标、prediction 或 mask 行错位 | 普通 MPNN 不因此具有三维旋转等变性 |
| T-D05 | 公共/逐原子代表变换的完整 \(K_q\) 字典、位移和距离 | 固定 shift、原行配对或仅按原子对配对 | 不决定真实晶胞约定或材料 |
| T-D06 | 解析镜像盒与外扩一层暴力盒完整边键一致 | 固定 `[-1,1]^3` 与最小镜像漏边 | 有限枚举正确不表示 cutoff 物理上充分 |
| T-D07 | 多镜像边、非零自镜像边和零位移自环规则 | 仅按 \((i,j)\) 去重减少边数 | 多重边保留不证明标签 Hermiticity |
| T-D08 | 一至三层同步传播支持与有向图距离一致 | 原地更新在一层内越过多条边 | 有全局通道的架构不受该界约束 |
| T-D09 | edge-output、concat/padded batch、NaN padding、空入边、复杂度和 36 个 schema 失败 | 行增删、几何/特征滚动、宽度/rank、cell/cutoff、graph ID 和 provenance 变异 | schema 通过不证明预测物理正确 |
| T-D10 | 非有限、病态晶胞、非法 cutoff、越界/重复、分组污染和元数据不一致 | 任一非法对象静默接受即总测试失败 | 输入拒绝策略不选择实践后端 |

固定环境、两套 CLI 和完整阈值见[代码说明](../../05_code_exercises/stageD_synthetic_mpnn/README.md)。两套 CLI 必须报告 T-D01—T-D10 全部 `pass=true`、`overall_pass=true`，相同配置的真实 stdout 字节必须一致。

## 5. 张量追踪最短路径

遇到任一预测分量时，应当按以下顺序追踪，而不是从数值相近开始猜测对应关系：

1. 读取 `schema_version`、`structure_id` 和 `unit`；
2. 读取完整边键 `(receiver,sender,shift)`，重算规范 edge ID；
3. 由 cell、fractional 和 shift 重算 displacement、distance，并验证 cutoff；
4. 由两端 `node_orbitals`、`block_shape` 和连续 mask 反解局部轨道对；
5. 核对逐分量 `orbital_i_id/orbital_j_id` 与局部反解一致；
6. 在排序、置换、换胞、concat 或 padding 后按完整键建立双射；
7. 只在有效 component mask 上计算损失，并在读取前排除 inactive padding；
8. 最后才比较 prediction、标签及派生物理量。

张量 shape、dtype 和身份均通过，只能证明记录满足阶段 D 合成契约，不能证明真实 Hamiltonian 标签、材料泛化或下游物理量正确。

## 6. 关键检查题与答案定位

| 检查问题 | 答案定位 | 验证入口 |
|---|---|---|
| 为什么训练损失下降不能替代独立结构组测试？ | 第 11 章 11.2、11.6；D-D02 | T-D01/T-D03；C-D01/C-D03 |
| masked MSE 的分母为什么必须是有效分量数 \(S\)？ | 第 13 章 13.4；D-D01 | T-D02；C-D02 |
| 为什么边行重排时只重排 prediction 不够？ | 第 12 章 12.3—12.5；第 13 章 13.3 | T-D04/T-D09；C-D04/C-D09 |
| 为什么逐原子换胞时 shift 必须改变？ | 第 14 章 14.5；D-D07 | T-D05；C-D05 |
| 为什么斜晶胞不能固定搜索 `[-1,1]^3`？ | 第 14 章 14.3；D-D05 | T-D06；C-D06 |
| 为什么 \((i,j)\) 不是周期边实例的唯一身份？ | 第 12 章 12.1.3、12.5.3、12.6.2；第 14 章 14.4.2—14.4.3 | T-D07；C-D07 |
| 为什么一层原地更新会破坏一层感受野？ | 第 13 章 13.2；D-D04 | T-D08；C-D08 |
| 为什么 NaN padding 可以存在但不能进入前向？ | 第 12 章 12.2.2—12.2.3；第 13 章 13.1 | T-D09；C-D09 |

## 7. 诊断顺序与常见误区

| 现象 | 优先检查 | 机制边界 | 验证 |
|---|---|---|---|
| 测试误差异常低 | group lineage、交集、预处理拟合范围 | 逐帧插值不等于新组泛化 | T-D01/T-D03 |
| 梯度形状正确但训练不收敛 | loss 平均、mask、scatter 端点、激活导数 | 单个权重差分不足以覆盖全部反传 | T-D02 |
| 置换后数值似乎相同但身份错位 | 完整键、edge ID、mask、轨道 ID 同步映射 | 只比较数组顺序会掩盖错配 | T-D04/T-D09 |
| 换胞后位移改变 | \(n'=n+q_i-q_j\)、回拉键和行双射 | 固定 shift 只适用于公共平移 | T-D05 |
| 邻居数异常少 | 晶胞条件数、解析镜像界、固定小盒/最小镜像 | cutoff 有限不保证小镜像盒完备 | T-D06/T-D10 |
| padding 导致 NaN | 是否在 gather、统计、归一化和 loss 前切片 | 仅在 loss 末端乘 mask 太晚 | T-D09 |
| batch 几何自洽但与键不符 | 从 fractional、端点、shift、cell 重算 | 只检查 `distance=norm(displacement)` 不够 | T-D09 |

诊断应依次确认授权状态、schema 版本、完整身份、几何重算、轨道反解、batch 隔离、数值残差和模型误差；不能用后端结果反向掩盖上游身份错误。

## 8. 阶段边界

M6-08 材料完成后仍须由新的独立子 agent 执行自学材料审计；随后 M6-09 还需对阶段 D 当前快照做新的正式总审计。只有总审计明确 `BLOCKING=0`、`NON_BLOCKING=0` 并允许进入 M7，M6 才能完成。

M8 前继续禁止安装 DeepH、下载正式训练数据、生成 DFT 标签或隐含选择材料、后端和软件版本。M7 完成及 M3—M7 的 gpt-5.6-sol/max 全量独立审计清零后，才进入 M8 集中决策冻结；M8 冻结后，M9 的正式安装、下载或复现实验仍需一次明确执行授权。
