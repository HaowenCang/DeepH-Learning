# M6-03 第 12 章正式独立内容审计

- 审计日期：2026-08-04
- 审计角色：独立内容审计子 agent
- 审计方式：只读检查、公式重推、独立数值复算、来源与阶段边界核对
- 总结论：`FAIL`
- `BLOCKING=3`
- `NON_BLOCKING=0`
- M6-03：**不得完成**
- M6-04：**不得启动**

第 12 章已经正确建立 receiver/sender 方向、有向周期多重边、反向 shift、节点置换约定、邻接计数矩阵变换、节点与边输出等变、集合聚合碰撞、edge instance 离散身份、来源血缘以及旋转和 M8/M9 边界。六个例题与十组题解的独立复算未发现算术错误。当前失败来自三个会直接影响后续 T-D04/T-D09 validator 的 schema 缺口：图批处理与图级 mask 没有冻结 dtype、shape 和跨图一致性关系；空入边节点遗漏 mean 的未定义边界；轨道块 mask 只校验真值数量而没有冻结真值位置和轨道对映射。

## 1. 审计范围

送审材料包括：

- `03_textbook/chapters/12_atomic_graph_representation/sources.md`
- `03_textbook/chapters/12_atomic_graph_representation/outline.md`
- `03_textbook/chapters/12_atomic_graph_representation/chapter.md`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md`
- `04_derivations/stageD/12_permutation_aggregation.md`
- `06_exercises/04-stageD/12_atomic_graph/problem/readme.md`
- `06_exercises/04-stageD/12_atomic_graph/solution/readme.md`
- `03_textbook/stageD_graph_conventions.md` 中 receiver/sender、edge ID、数值环境与授权约定
- `08_audits/M6_stageD_work_package.md` 中 4.3—4.4、D-D03、T-D04/T-D09 与教材门控
- `00_scope/learning_route.md:108-135` 与 `00_scope/master_execution_plan.md:164-187` 的阶段 D 范围

未修改任何送审文件。唯一写入为本审计报告。

## 2. 问题清单

### M6-CH12-B01：批处理与 padding schema 没有冻结可执行的 dtype、shape 和跨图关系

- 级别：`BLOCKING`
- 位置：
  - `03_textbook/chapters/12_atomic_graph_representation/chapter.md:54-69`
  - `03_textbook/chapters/12_atomic_graph_representation/chapter.md:77-85`
  - `06_exercises/04-stageD/12_atomic_graph/problem/readme.md:3-5`
  - `06_exercises/04-stageD/12_atomic_graph/solution/readme.md:3-17`
  - 对照 `08_audits/M6_stageD_work_package.md:188-191`

正文对单图字段给出了 dtype 和 shape，但对批处理只说明“拼接并偏移节点索引，同时保存 `node_graph_id` 与 `edge_graph_id`”，或“padding 到统一大小并给出节点和边 mask”。材料没有定义这四个批字段的 dtype 和 shape，也没有给出防止跨图边的可执行关系。至少需要冻结

\[
\texttt{node\_graph\_id}\in\mathbb Z^{N_{\mathrm{tot}}},
\qquad
\texttt{edge\_graph\_id}\in\mathbb Z^{E_{\mathrm{tot}}}
\]

的 int64 口径，并逐边断言

\[
\texttt{node\_graph\_id[receiver[e]]}
=\texttt{edge\_graph\_id[e]}
=\texttt{node\_graph\_id[sender[e]]}.
\]

padding 方案同样需要给出 `node_features`、边字段、`node_mask` 和 `edge_mask` 的完整批维 shape、bool mask 口径、有效计数与索引范围。当前 Q12-01 及 A12-01 只复述单图 schema，不能使自学者或后续代码审计者从材料独立构造批处理 validator。一个 dtype 正确、第一维正确但把 sender 指向另一结构的边，按当前书面断言可能静默通过。

关闭条件：

1. 在正文冻结拼接批处理的所有新增字段 dtype/shape、节点索引偏移规则、graph ID 取值范围和上述逐边同图关系。
2. 冻结 padding 批处理的节点/边张量 shape、bool mask shape、有效计数、padding 索引约定，以及 mask 对聚合、归一化和损失的排除规则。
3. 在练习与参考解答中加入至少一个跨图边、错误 mask dtype/shape 或 padding 行进入聚合的失败夹具，使这些关系可独立验证。

### M6-CH12-B02：空入边节点的 mean 聚合边界遗漏

- 级别：`BLOCKING`
- 位置：
  - `03_textbook/chapters/12_atomic_graph_representation/chapter.md:77-85`
  - `03_textbook/chapters/12_atomic_graph_representation/chapter.md:151-164`
  - `06_exercises/04-stageD/12_atomic_graph/problem/readme.md:27-33`
  - `06_exercises/04-stageD/12_atomic_graph/solution/readme.md:58-75`

正文正确规定空入边节点的 sum 为零向量，并指出 max 的空集合没有自然有限值，必须另行定义或禁止；但是 mean 使用

\[
\frac{1}{|\mathcal M_i|}\sum_{m\in\mathcal M_i}m
\]

时，空入边节点同样出现零分母。材料没有定义 mean 的空集合值，也没有明确禁止这一输入。Q12-05/Q12-06 与答案只覆盖排列和碰撞，没有覆盖空集合。这会使按正文直接实现的 mean 聚合产生 NaN 或除零，而正文另处又要求在聚合前拒绝非有限值。

关闭条件：

1. 明确规定 mean 与 max 对空入边节点分别采用“禁止并验证”还是项目级哨兵/默认值；若定义默认值，必须说明其语义、mask 与梯度处理。
2. 说明 sum 的零向量约定不自动推广到 mean/max。
3. 在例题或练习/答案中加入空入边节点，覆盖 sum 成功以及 mean/max 的冻结行为和失败样例。

### M6-CH12-B03：轨道块 mask 只约束真值数量，不能保证展平分量与轨道对正确配对

- 级别：`BLOCKING`
- 位置：
  - `03_textbook/chapters/12_atomic_graph_representation/chapter.md:187-233`
  - `03_textbook/chapters/12_atomic_graph_representation/examples.md:45-53`
  - `06_exercises/04-stageD/12_atomic_graph/problem/readme.md:35-41`
  - `06_exercises/04-stageD/12_atomic_graph/solution/readme.md:77-106`
  - 对照 `08_audits/M6_stageD_work_package.md:188-191`

正文规定块按行优先展平并 padding 到 `(E,P_max)`，但唯一 mask 关系是

\[
\sum_a \texttt{mask}_{ea}=p_i p_j.
\]

该计数是必要条件而不是充分条件。以 \(p_i=2,p_j=3,P_{\max}=9\) 为例，mask 在索引 \(\{0,1,2,6,7,8\}\) 为真仍满足真值数为 6，却无法按

\[
a=\alpha p_j+\beta
\]

恢复原 \(2\times3\) 块。例 12-5、Q12-07 和 A12-07 均只检查真值数量和单个展平索引，没有规定右侧连续 padding、\(P_{\max}\) 下界、真值位置或每个有效分量的 \((\alpha,\beta)\) 反解。现有 provenance 列表虽然包含 `orbital_i`、`orbital_j` 和 `block_shape`，但没有消除“数量正确、位置错误”的语义漂移。

关闭条件：

1. 冻结 \(P_{\max}\ge\max_e p_i p_j\)，并在采用右侧连续 padding 时规定
   \[
   \texttt{mask}_{ea}\iff 0\le a<p_i p_j.
   \]
2. 对每个有效 \(a\) 冻结反解
   \[
   \alpha=\lfloor a/p_j\rfloor,\qquad \beta=a\bmod p_j,
   \]
   以及 `orbital_i`、`orbital_j` 是轨道列表还是逐分量索引的明确 schema，使向量能够唯一恢复为 `block_shape`。
3. 在例题或练习/答案中加入一个真值数量正确但位置错误的 mask，并要求 validator 拒绝；同时覆盖 \(P_{\max}<p_i p_j\)。

## 3. 已通过项目

### 3.1 有向多重图、方向与周期镜像身份

- `chapter.md:27-48` 明确约定 \(i\) 为 receiver/中心、\(j\) 为 sender/邻居，消息沿 \(j\to i\)，反向边为 \((j,i,-n)\)。
- 同一 \((i,j)\) 的不同 \(n\) 被保留为合法多重边；零位移自环排除、非零自镜像边允许，完整键重复被拒绝。例 12-2、例 12-3 与 A12-02/A12-03 的结论正确。
- `chapter.md:215-233` 和 A12-08 使用数组 `["stageD-edge-v1",structure_id,i,j,nx,ny,nz]`、`ensure_ascii=false`、紧凑分隔符、UTF-8 和 SHA-256，且明确不以浮点位移或距离作为身份键。与阶段 D 统一约定一致。

### 3.2 置换矩阵、邻接矩阵与节点/边等变

- 按 \(P_{p(i),i}=1\) 定义，\(X'=PX\) 与 \(A'=PAP^\mathsf T\) 的主动重编号口径一致。
- D-D03 在共享消息函数、共享更新函数、边特征同步重标、保留完整多重集合等条件下，正确证明 \(\bar m'_{p(i)}=\bar m_i\) 与 \(h_{p(i)}^{\prime+}=h_i^+\)；边头证明 \(y'_{p(e)}=y_e\) 正确。
- 材料明确区分边行置换、节点重编号与三维旋转，没有把离散置换等变误报为几何旋转等变。

### 3.3 聚合碰撞与浮点边界

- sum、mean、max 的排列语义和计数信息差异正确；\(\{1,1\}\) 与 \(\{2\}\) 的 sum 碰撞、\(\{1\}\) 与 \(\{1,1\}\) 的 mean 碰撞、\(\{1\}\) 与 \(\{0,1\}\) 的 max 碰撞均正确。
- `chapter.md:166-181` 没有把直接求和外推为所有集合上的单射；对 D-GNN-02 的可数域、固定大小扩展和嵌入条件边界表述审慎。
- 正文与 D-D03 正确区分实数精确算术和浮点非结合性，并把实现容差指向 T-D04；工作包已冻结 float64 置换残差阈值 \(10^{-12}\)。独立复算的三项 float64 序列 \((10^{16},-10^{16},1)\) 在两种顺序下得到 1 与 0，确认材料要求容差而不能要求位级等同是必要的。B02 仅涉及空集合，不否定这些已通过结论。

### 3.4 来源、自学链与授权边界

- D-GNN-01 的消息/更新/读出及 directed multigraph 扩展、D-GNN-02 的集合排列结构、D-PBC-01 的周期晶体 undirected multigraph 与多重边动机均与本地来源原文一致；三份本地快照 SHA-256 与 `01_sources/documentation/stageD/README.md` 及中央来源台账一致。
- DH-01 被限定为局域环境、原子对和 Hamiltonian 块任务接口，没有复用论文中的材料、基组、后端或软件版本。正文同时指出 provenance 不能证明标签物理正确。
- 提纲和正文的 12.1—12.7 标题顺序一致；六个例题、十道题目与十份答案一一对应且目录成对非空。修复 B01—B03 后，教材—推导—例题—练习—答案链才达到可直接编码验证的 schema 完备性。
- `chapter.md:255-267` 与 A12-10 保留旋转/轨道块协变属于阶段 E、正式标签物理验证属于 M8/M9 后续门控的边界；未发现安装 DeepH、下载正式训练数据、生成 DFT 标签或隐含选择材料/后端/版本的内容。

## 4. 独立复算记录

使用 Python 3.12.13、NumPy 2.3.5、float64，在不写入文件的条件下独立复算：

| 对象 | 独立结果 | 审计判断 |
|---|---:|---|
| 例 12-1：\(p=(2,0,1)\) 的 \(PX\) | \((x_1,x_2,x_0)^\mathsf T\) | 一致 |
| 例 12-1：边 \((0,1,n)\) 重标 | \((2,0,n)\) | 一致 |
| 例 12-3：反向位移 | \(d_{ji,-n}=-d_{ij,n}\) | 一致 |
| 例 12-5：\((p_i,p_j)=(2,3)\)、\((1,2)\) | 行优先 \(a=5\) | 一致 |
| 例 12-5：\((0,1)\) 行/列优先 | \(1/2\) | 一致 |
| Q12-04：\(p=(1,2,0)\) 的置换矩阵 | 与 A12-04 相同 | 一致 |
| Q12-04：随机非对称计数矩阵 | 逐元素重标与 \(PAP^\mathsf T\) 完全相等 | 一致 |
| Q12-07：\((p_i,p_j)=(3,2)\)、\((2,1)\) | 真值数 \(6\)，\(a=5\) | 算术一致；schema 缺口见 B03 |
| Q12-06：三类聚合碰撞 | \(2=2,\ 1=1,\ 1=1\) | 一致 |

其余 Q12-01—Q12-03、Q12-05、Q12-08—Q12-10 为定义、证明或诊断题；逐项核对未发现 receiver/sender、置换方向、完整键、来源或授权边界错误。

## 5. 文档完整性检查

- 9/9 范围文件均可按 UTF-8 严格解码；裸 CR 为 0，非法控制字符为 0。
- 七份章节主体文件中的展示公式分隔符逐文件成对，合计 47 对。
- 3/3 本地 Markdown 链接有效。
- 直接来源快照实测哈希与来源 README 一致。
- 依照审计安全约束，未对送审源文件运行带输出文件或重定向的 Pandoc 命令，也未生成任何派生文档。

## 6. 最终门控结论

当前 `BLOCKING=3`、`NON_BLOCKING=0`，结论为 `FAIL`。M6-03 不得标记为 `COMPLETED`，M6-04 不得启动。主 agent 应关闭 B01—B03；随后须由本独立审计员执行定点复核。只有复核确认三项全部关闭、没有引入新问题，并给出 `BLOCKING=0`、`NON_BLOCKING=0` 和明确放行结论后，才允许完成 M6-03 并启动 M6-04。
