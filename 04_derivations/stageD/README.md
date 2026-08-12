# 阶段 D 解析推导包：监督学习、普通 MPNN 与周期图

本索引把 D-D01—D-D07 组织为一条从监督回归与无泄漏评价，到图置换、局部感受野、周期镜像完备性、复杂度和端到端边身份的可复核推导链。四个推导文件保留完整公式、条件和失败边界；本文件只建立依赖、对象接口和统一验收，不用摘要替代原推导。

阶段 D 处于材料建设模式，只使用合成分组、合成晶格、合成轨道 ID 和合成边标签。真实材料、DFT/数据后端、DeepH 软件对象、实践版本和训练预算均保留到 M8；M9 外部动作仍需用户明确授权。

## 1. 推导依赖与对象链

监督学习分支为

\[
\text{分组样本与标签}
\xrightarrow{\mathrm{D\mbox{-}D02}}
\text{无泄漏 train/validation/test 评价}
\xrightarrow{\mathrm{D\mbox{-}D01}}
\text{冻结回归目标与可核验梯度}.
\]

图网络分支为

\[
\text{属性有向多重图}
\xrightarrow{\mathrm{D\mbox{-}D03}}
\text{求和聚合与节点/边置换等变}
\xrightarrow{\mathrm{D\mbox{-}D04}}
\text{有向前驱感受野},
\]

\[
\{\mathrm{D\mbox{-}D03},\mathrm{D\mbox{-}D04}\}
\xrightarrow{\mathrm{D\mbox{-}D06}}
\text{依赖 }N,E,L,d\text{ 的时间与激活成本}.
\]

周期几何分支为

\[
\text{行晶格、规范分数坐标与 cutoff}
\xrightarrow{\mathrm{D\mbox{-}D05}}
\text{完整有限镜像集合}
\xrightarrow{\mathrm{D\mbox{-}D07}}
\text{换胞双射、规范边键与 provenance}.
\]

D-D05 先保证边集合不漏失，D-D07 再证明同一物理边在不同周期代表下如何精确配对。D-D03/D-D04 只对已经正确构造的图成立；小训练损失或置换残差不能补救漏边、组泄漏或身份错误。

## 2. D-D01—D-D07 覆盖矩阵

| ID | 核心产物 | 强制条件 | 主要失败边界 | 推导文件 | 验证 |
|---|---|---|---|---|---|
| D-D01 | MSE、一层 tanh 回归的解析梯度和中心差分口径 | 明确 \(M,d,q\) 形状、批平均 \(1/M\)、row-vector 链式法则和步长扫描 | 有限差分只作检查；符号翻转、漏批平均必须失败 | [11_supervised_gradients_leakage.md](11_supervised_gradients_leakage.md) | T-D02 |
| D-D02 | 逐帧随机划分低估新组误差的随机效应机制 | \(\tau_g^2=\mathbb E[\delta_g^2]\) 为均方；测试噪声与相应随机项不相关；组 ID 与母结构血缘可信 | 协方差非零时差值符号可变；集合无交集不排除错误 group ID | [11_supervised_gradients_leakage.md](11_supervised_gradients_leakage.md) | T-D01 |
| D-D03 | 求和聚合的边行不变性、节点和边输出的重编号等变性 | 参数共享；端点、特征、键和输出同步重标；保留多重边 | 顺序敏感聚合、错误去重、绝对节点参数；不推出旋转等变 | [12_permutation_aggregation.md](12_permutation_aggregation.md) | T-D04 |
| D-D04 | \(L\) 层同步局部 MPNN 的有向前驱感受野上界 | sender \( \to \) receiver；同步更新；局部边；无全局状态回灌 | 原地更新、全连接注意力、全局节点会改变结论；结构可达不等于实际非零影响 | [13_receptive_field_complexity.md](13_receptive_field_complexity.md) | T-D08 |
| D-D05 | 逆晶格列范数给出的有限镜像盒与完备性证明 | float64；有限 \(r_c>0\)；\(\sigma_{\min}>0\)、\(\kappa_2(A)<10^8\)；规范 \(f_i\in[0,1)^3\) | 固定小盒或通用最小镜像会漏边；大 cutoff/短晶格方向成本可很高 | [14_periodic_enumeration_provenance.md](14_periodic_enumeration_provenance.md) | T-D05、T-D06、T-D10 |
| D-D06 | 冻结 MPNN 的时间主项和 float64 激活数组主项 | 区分 \(N,E,L,d,d_e,P_{\max}\)；声明缓存集合 | 数组估计不是进程峰值；重计算改变时间—内存权衡 | [13_receptive_field_complexity.md](13_receptive_field_complexity.md) | T-D09 |
| D-D07 | 逐原子换胞双射、回拉键、规范 edge ID 与边 provenance | \(n'=n+q_i-q_j\)；完整整数键；规范 JSON 字节串；位移容差独立验证 | 按原子对或距离折叠、固定 \(n'=n\)、删除 shift 或轨道身份必须失败 | [14_periodic_enumeration_provenance.md](14_periodic_enumeration_provenance.md) | T-D05、T-D07、T-D09 |

## 3. 跨推导不变量

### 3.1 索引方向与多重边

- 周期边 \(e=(i,j,n)\) 中 \(i\) 是 receiver，\(j\) 是 sender；位移为 \(d_{ijn}=(f_j+n-f_i)A\)，消息沿 sender \( \to \) receiver 聚合。
- 同一 \((i,j)\) 的不同 \(n\) 是不同边实例；零位移自环排除，非零自镜像按 cutoff 保留。
- 节点置换只重标端点；整数 shift 是晶格坐标，不随节点编号置换。

### 3.2 损失、mask 与梯度

- D-D01 的 \(1/M\) 是样本批平均；第 13 章边损失的 \(1/S\) 是有效轨道块分量平均。两者不得混用。
- padding 行和 mask=false 的输出不进入损失，梯度必须为零。
- 解析梯度是主对象，中心有限差分只验证冻结实现；训练损失下降不能替代梯度、独立组误差或 schema 检查。

### 3.3 周期代表与离散身份

规范结构保存 \(f_i\in[0,1)^3\)。协变测试允许 \(\widetilde f_i=f_i+q_i\)，并以

\[
n^{\mathrm{can}}=n'-q_i+q_j
\]

回拉。只有完整离散键相等后，才以 float64、rtol=0、atol=\(10^{-12}\) 比较位移和距离。edge ID 的哈希输入不含浮点数，但这不免除数值回归。

### 3.4 输出 provenance

边输出必须同时追踪结构、receiver、sender、shift、完整边键、edge ID、块形状、连续 mask、局部轨道下标和实际合成轨道身份或稳定轨道表引用。预测、键、mask、身份和 schema 版本在排序、拼接批、换胞回拉与逆置换时使用同一行映射。

### 3.5 图可达、几何支持与旋转

D-D04 的图距离结论和第 14 章 \(Lr_c\) 几何上界都要求局部消息、同步更新、无跨图边，且初始特征未预编码全局结构、没有全局状态回灌。它们是结构可达上界，不保证数值影响非零。D-D03 的离散置换等变也不推出三维旋转不变或轨道块旋转协变；后者保留到阶段 E。

## 4. 章节、例题与练习入口

| 推导 | 正文与例题 | 问题与参考解答 |
|---|---|---|
| D-D01—D-D02 | [第 11 章](../../03_textbook/chapters/11_supervised_learning_optimization/) | [第 11 章练习](../../06_exercises/04-stageD/11_supervised_learning/) |
| D-D03 | [第 12 章](../../03_textbook/chapters/12_atomic_graph_representation/) | [第 12 章练习](../../06_exercises/04-stageD/12_atomic_graph/) |
| D-D04、D-D06 | [第 13 章](../../03_textbook/chapters/13_message_passing_networks/) | [第 13 章练习](../../06_exercises/04-stageD/13_mpnn/) |
| D-D05、D-D07 | [第 14 章](../../03_textbook/chapters/14_periodic_graph_neighbor_lists/) | [第 14 章练习](../../06_exercises/04-stageD/14_periodic_graph/) |

## 5. 来源等级与推导标签

- PRIMARY_EXPLICIT：来源直接给出的监督学习、消息传递、集合聚合或周期晶体图对象。
- DIRECT_DERIVATION：从冻结定义逐式推出的梯度、随机效应均方差、置换映射、感受野、镜像盒和换胞双射。
- PEDAGOGICAL：有限维网络、合成分组、合成晶格、合成轨道 ID、阈值夹具与故障注入。

来源边界由 [M6 阶段 D 工作包](../../08_audits/M6_stageD_work_package.md) 和各章 sources.md 冻结。Gilmer 等不定义晶格镜像枚举，Deep Sets 不推出旋转等变，CGCNN 不定义通用 cutoff，原始 DeepH 也不冻结本项目的软件 schema、真实材料或训练超参数。

## 6. 可执行验证映射

| 推导 | 正例 | 强制失败 |
|---|---|---|
| D-D01—D-D02 | 分组交集为空；解析梯度与中心差分误差不超过 \(10^{-5}\) | 相邻帧逐帧随机划分；符号翻转；漏掉批平均 |
| D-D01—D-D02 → T-D03 | 在无泄漏分组上训练冻结合成回归，训练损失下降、独立组测试误差通过预先冻结阈值且重复运行一致 | 只凭训练损失下降放行；看到结果后放宽生成式、样本数、宽度、学习率、迭代数或测试阈值 |
| D-D03 | 节点置换后状态和边输出逆映射残差不超过 \(10^{-12}\) | 边未随节点重标；顺序敏感聚合；按原子对去重 |
| D-D04 | 1、2、3 层受影响集合不越过有向前驱距离 | 同层原地更新导致越级传播；漏掉边界节点 |
| D-D05 | 冻结镜像盒与扩展一层盒过滤后的完整键相同 | 固定 \([-1,1]^3\)；最小镜像漏掉等距多重边；非有限 cutoff |
| D-D06 | 报告 \(N,E,L,d\)、构图/网络时间和数组字节 | 把 Python RSS 冒充激活内存；只写 \(O(N)\) |
| D-D07 | 公共/逐原子换胞按回拉键双射，位移残差不超过 \(10^{-12}\) | 错误保持 \(n'=n\)；按距离配对；删除 shift/轨道身份 |

正式 T-D01—T-D10 代码包在 M6-07 建设。本推导包规定对象、条件、容差和失败语义，不把章内手算或临时复算冒充正式确定性 CLI。

## 7. M6-06 验收

M6-06 通过需要：

- D-D01—D-D07 均能从本索引定位到逐式推导、正文、例题、题目、答案和对应 T-D 验证；
- 每项推导的对象域、形状/索引、统计或几何条件、失败边界无偷换；
- receiver/sender、mask 平均、置换、周期代表、edge ID 和轨道身份契约跨文件一致；
- 全部活动链接、严格 MathML、控制字符和数学节点外 TeX 残留检查通过；
- 独立子 agent 判定新增及剩余 BLOCKING 为 0，并明确允许 M6-07。

## 8. M8/M9 边界

本推导包不构成实践方案选择。M7-I 全量独立总审计通过后才准备 M8 决策冻结；M8 冻结后，在 M9 正式安装 DeepH、下载正式数据、生成 DFT 标签或运行复现实验前仍需明确执行授权。
