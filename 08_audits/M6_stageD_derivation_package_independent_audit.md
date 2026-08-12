# M6-06 阶段 D 解析推导包正式独立审计

- 审计日期：2026-08-04
- 审计角色：独立推导审计子 agent
- 审计方式：只读逐行检查、公式独立重推、独立数值复算、跨章节/Q&A/门控契约核对，以及只读链接与严格 MathML 检查
- 总结论：`PASS`
- `BLOCKING=0`
- `NON_BLOCKING=0`
- M6-06：**允许完成**
- M6-07：**允许启动**

四个推导文件及阶段 D 索引已经完整覆盖 D-D01—D-D07。公式、对象域、张量形状、统计/几何条件、失败边界和 T-D01—T-D10 映射与工作包、第 11—14 章及成对 Q/A 一致。独立复算未发现新增或剩余问题。

## 1. 审计范围与快照

核心被审材料：

- `04_derivations/stageD/README.md`
- `04_derivations/stageD/11_supervised_gradients_leakage.md`
- `04_derivations/stageD/12_permutation_aggregation.md`
- `04_derivations/stageD/13_receptive_field_complexity.md`
- `04_derivations/stageD/14_periodic_enumeration_provenance.md`

交叉核对材料包括 `08_audits/M6_stageD_work_package.md`、`03_textbook/stageD_graph_conventions.md`、第 11—14 章当前 `chapter.md`/`examples.md`/`outline.md`/`sources.md`，以及 `06_exercises/04-stageD/` 下 Q11—Q14 与 A11—A14。未审计 M6-07 尚待建设的正式代码实现。

审计开始时核心文件 SHA-256 为：

| 文件 | SHA-256 |
|---|---|
| `04_derivations/stageD/README.md` | `AD2EDD36B524363B26EB7A8CBEEB1DD7D3629D17C5896D50BD4CE74B073A2F10` |
| `11_supervised_gradients_leakage.md` | `1340AB3B01581429259BF7BC7AC13204D5CDD85854012DCC14C323099314D8CC` |
| `12_permutation_aggregation.md` | `C550F89B728822F42693597CC7EBB27550488B9C3CBAE3D020B4C3333623EFB5` |
| `13_receptive_field_complexity.md` | `94D36A0C9206D186E1D2B64AF8D3E4ED835DC2FEA2E6A9F2655F27FB67F50E93` |
| `14_periodic_enumeration_provenance.md` | `18F0D6E0CD09FD510FB048B6CB05018A130C20E34DF6E2A0F0919BF3234C130F` |
| `08_audits/M6_stageD_work_package.md` | `4D0F0B64812C98E3308729E44E33588451D0EC61B20ABD6BB959B252F4E9A50E` |
| `03_textbook/stageD_graph_conventions.md` | `BEBC75E5390E078A523331837E667DEE532919F1620F4037E11059888D05D265` |

审计未修改任何被审材料、计划、台账、README 或代码；唯一写入为本报告。

## 2. 问题清单

### BLOCKING

无。

### NON_BLOCKING

无。

## 3. D-D01—D-D07 逐项结论

### 3.1 D-D01：MSE、线性/非线性梯度与有限差分

- `11_supervised_gradients_leakage.md:5-96` 对 `X:(M,d)`、`W:(d,q)`、`b,v:(q,)`、`c:scalar` 的一层 tanh 回归给出完整 row-vector 链式法则。独立微分确认 `delta_y=2r/M`、`delta_Z=(delta_y v^T) odot (1-H odot H)`、`X^T delta_Z`、`delta_Z^T 1`、`H^T delta_y` 与 `1^T delta_y` 的公式和形状均正确。
- 工作包要求的线性回归梯度可从第 11 章 `chapter.md:177-197`、例 11-2 与 Q11-03/A11-03 直接定位，保留了同一 `1/M` MSE 口径，没有以非线性推导替换或缩减线性对象。
- `11_supervised_gradients_leakage.md:98-109` 的缩放误差分母、四点步长扫描、`1e-5` 门槛以及符号翻转/遗漏批平均失败样例与 T-D02 一致。有限差分被正确限定为解析梯度的检查手段。

### 3.2 D-D02：结构组泄漏的随机效应机制

- `11_supervised_gradients_leakage.md:113-169` 明确把 `tau_g^2` 定义为 `E[delta_g^2]`，不是隐含无偏性的方差。已见组与新组误差分别为 `delta_g-epsilon` 和 `-b_g-epsilon`；独立展开确认一般式中的协方差符号正确。
- 在冻结不相关条件下，均方分别为 `tau_g^2+sigma_epsilon^2` 与 `sigma_b^2+sigma_epsilon^2`，差为 `sigma_b^2-tau_g^2`。Q11-09/A11-09 的 `1.5`、`5.0`、差 `3.5` 均复算正确。
- `11_supervised_gradients_leakage.md:169-181` 明确该结论不是任意数据集的普遍定量界，并指出错误/过细 group ID 可绕过集合交集检查，需要母结构哈希和生成血缘。该失败边界与 T-D01 一致。

### 3.3 D-D03：求和聚合与置换

- `12_permutation_aggregation.md:3-25` 在入边多重集合上证明边行排列不变，没有把多重集合偷换为普通集合。
- `12_permutation_aggregation.md:27-96` 对节点映射 `i -> p(i)` 同步重标端点和边特征，在参数共享条件下逐层得到节点等变及边输出等变。整数 shift 保持为晶格坐标，不随节点编号置换，和统一图约定一致。
- `12_permutation_aggregation.md:98-109` 正确列出绝对节点参数、顺序敏感聚合、未同步 edge ID、错误去重和浮点归约误差边界，并明确离散置换不推出三维旋转等变。

### 3.4 D-D04：有向前驱感受野

- `13_receptive_field_complexity.md:5-32` 对 sender 到 receiver 的有向距离给出完整归纳。集合恒等式
  `N^-_L(i) union (union_{j->i} N^-_L(j)) = N^-_{L+1}(i)`
  在同步、局部、无全局回灌条件下成立。
- `13_receptive_field_complexity.md:34-42` 正确区分结构可达上界与实际非零影响；零权重、饱和和聚合碰撞可使实际影响集合更小。边头读取两端点时，其节点支持为两个端点前驱邻域之并。
- 推导正确区分局部跳连与会破坏证明条件的全局节点、全图归一化、全连接注意力及同层原地更新。索引 `README.md:87-89` 还补全无跨图边、初始节点/边特征未预编码全局结构的条件。T-D08 应采用冻结的非退化夹具验证 1—3 层支持，并以有向距离给出上界。

### 3.5 D-D05：有限镜像枚举

- `14_periodic_enumeration_provenance.md:5-39` 在 row-vector 行晶格约定下，由 `x=d A^{-1}` 和逆晶格列范数得到
  `|n_k| < r_c ||A^{-1}_{:k}||_2 + 1`，再采用向上取整的安全整数盒。证明方向、矩阵轴与严格/非严格不等号均正确；盒是完备上界而非最紧边界。
- 定义域完整冻结为 float64、有限正 cutoff、规范分数坐标、`sigma_min>0`、`kappa_2<1e8`。`14_periodic_enumeration_provenance.md:41-49` 还要求扩展一层盒比对，并保留大 cutoff/短晶格方向的候选成本边界。
- 独立对 30 个随机可逆斜晶格执行冻结盒与逐方向扩展一层盒的暴力过滤，完整 `(i,j,nx,ny,nz)` 键集合均完全相同。

### 3.6 D-D06：时间与激活内存

- `13_receptive_field_complexity.md:46-60` 的逐项成本为 receiver/sender 投影 `O(E d^2)`、边特征投影 `O(E d_e d)`、节点 self/aggregate 更新 `O(N d^2)`、segment sum `O(E d)`，边头为 `O(E(2d+d_e)P_max)`。在显式条件 `d_e=O(d)`、`P_max=O(d)` 下，`L` 层主体为 `O(L(E+N)d^2)`，没有遗漏会改变数量级的对象。
- 缓存每层 `H,Z_m,M,A,Z_u` 时，三个节点宽度数组与两个边宽度数组给出 float64 主项 `8L(3Nd+2Ed)` bytes。输入、输出、mask、索引、参数、梯度、优化器和进程开销被明确排除，未把数组估计误报为进程峰值。
- 对 `N=100,E=800,L=3,d=32` 独立复算为 `1,459,200 bytes`，与 A13-07 一致。

### 3.7 D-D07：周期代表、规范键与 provenance

- `14_periodic_enumeration_provenance.md:53-95` 对逐原子整数代表变换推得 `n'=n+q_i-q_j` 和回拉 `n_can=n'-q_i+q_j`。代回位移后整数项严格消去，`T_q` 与 `T_-q` 构成双射；公共平移退化为 `n'=n`。
- `14_periodic_enumeration_provenance.md:97-105` 冻结字段有序 JSON 数组、无空格 UTF-8 序列化和 SHA-256。独立计算例 14-8 得到 `f83e3b238ba5c1b71cc773c08afa5fab22c35c1e38c6418b629fde616f5020e3`，与文中一致。
- 离散 edge ID 不含浮点位移，但 `rtol=0, atol=1e-12` 的位移/距离回归仍独立执行。完整键、shift、块形状、连续 mask、局部下标、实际合成轨道身份和 schema 版本在排序、批处理、换胞回拉和逆置换中要求同一行映射；不同镜像不会按原子对或距离折叠。

## 4. 跨推导契约与验证映射

- receiver/sender：全部文件统一使用 `i=receiver`、`j=sender`，位移从 receiver 指向 sender 镜像，消息沿 sender 到 receiver 聚合。
- 损失平均：D-D01 使用样本数 `M` 的 `1/M`；边块 masked MSE 使用有效分量数 `S` 的 `1/S`。padding 和 mask=false 位置的损失及梯度均为零，未发现二者混用。
- 置换/旋转：D-D03 只证明离散节点重编号；D-D04 只证明局部图可达上界；普通 MPNN 的三维旋转和轨道块协变明确保留到阶段 E。
- 周期代表：规范存储与任意整数代表测试域分离；D-D05 在规范坐标上建立完备盒，D-D07 再给出任意代表的精确边双射和回拉键。
- T-D 映射：D-D02 对应 T-D01；D-D01 对应 T-D02，并与 D-D02 共同约束 T-D03；D-D03 对应 T-D04；D-D05/D-D07 对应 T-D05；D-D05 对应 T-D06/T-D10；D-D07 对应 T-D07；D-D04 对应 T-D08；D-D06 与 D-D07 对应 T-D09。T-D01—T-D10 均有正例、失败语义或阈值冻结规则。
- 授权边界：材料只使用合成分组、晶格、轨道 ID 和标签；未隐含选择正式材料、DFT/数据后端、DeepH 对象、实践版本或训练预算。M8/M9 两个停点保持不变。

## 5. 独立复算记录

使用 Python 3.12.13、NumPy 2.3.5 和 float64，在不调用 M6-07 实现代码、不写入派生数据的条件下独立构造审计夹具。

| 对象 | 独立结果 | 审计判断 |
|---|---:|---|
| D-D01 一层 tanh 网络全部参数中心差分 | 最大缩放误差 `1.545e-10` | 解析梯度通过 |
| D-D02 两百万样本 Monte Carlo | 已见组 `1.49816`（理论 `1.5`）；新组 `5.00913`（理论 `5.0`） | 随机效应分解通过 |
| D-D03 随机节点置换与边行重排 | 节点最大残差 `2.776e-17`；边消息 `0` | 置换结论通过 |
| D-D04 非对称有向多重图 0—3 层前驱集合 | 与有向最短路径定义一致 | 感受野归纳通过 |
| D-D05 30 个随机斜晶格 | 冻结盒与扩展盒键集 30/30 一致 | 完备盒复核通过 |
| D-D07 50 个随机边/逐原子整数代表 | 回拉整数键逐项相等；位移残差在冻结容差内 | 双射与位移不变通过 |
| 例 14-8 JSON 哈希 | `f83e3b...5020e3` | 规范 ID 通过 |
| D-D06/A13-07 激活主项 | `1,459,200 bytes`，约 `1.39 MiB` | 内存计数通过 |

## 6. 文档完整性与只读解析

- 对阶段 D 索引、四个推导文件、统一约定、工作包、第 11—14 章四类 Markdown 文件及全部 Q11—Q14/A11—A14，共 31 个文件执行活动本地链接检查；断链为 0。
- 31/31 文件使用 Pandoc `markdown+tex_math_single_backslash`、MathML、`--fail-if-warnings` 只读解析通过。未使用 `-o`、`--output`、重定向覆盖或任何输入写回方式。
- 去除 MathML 与代码节点后检查数学节点外 TeX 命令残留，结果为 0；非法控制字符为 0。
- D-D01—D-D07 均可由索引定位到逐式推导、对应正文/例题、成对题目/参考解答和 T-D 验证。Q11—Q14 与 A11—A14 编号完整，未发现公式、算术、方向、条件或授权边界错误。

## 7. 最终门控结论

正式结论为 `PASS`，`BLOCKING=0`，`NON_BLOCKING=0`。阶段 D 解析推导包满足材料完备性、可自学性和可验证性门控：

- 允许将 M6-06 标记为完成；
- 允许按依赖顺序启动 M6-07；
- 本结论只授权进入合成数据、普通 MPNN、自动测试与失败样例建设，不授权安装 DeepH、获取正式训练数据、生成 DFT 标签或开始任何 M9 外部动作。
