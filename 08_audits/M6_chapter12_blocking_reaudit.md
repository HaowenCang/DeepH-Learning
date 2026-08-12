# M6-03 第 12 章阻塞项定点复核

- 复核日期：2026-08-04
- 复核角色：原 M6-03 独立内容审计子 agent
- 原审计：`M6_chapter12_independent_content_audit.md`
- 复核范围：原 `M6-CH12-B01`—`B03` 的修复及其直接相邻改动
- 复核方式：只读逐项核对、公式重算和确定性最小夹具
- 总结论：`FAIL`
- 原阻塞项：`CLOSED=2`，`OPEN=1`
- 新增问题：`NON_BLOCKING=1`
- 当前合计：`BLOCKING=1`，`NON_BLOCKING=1`
- M6-03：**不得完成**
- M6-04：**不得启动**

## 1. 逐项复核

### M6-CH12-B01：CLOSED

复核位置：

- `03_textbook/chapters/12_atomic_graph_representation/chapter.md:69-100`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:61-63`
- `06_exercises/04-stageD/12_atomic_graph/problem/readme.md:3-5`
- `06_exercises/04-stageD/12_atomic_graph/solution/readme.md:3-27`
- `08_audits/M6_stageD_work_package.md:162-166`
- `08_audits/M6_stageD_work_package.md:193-195`

拼接批现已冻结：

- `node_graph_id:int64[N_tot]` 与 `edge_graph_id:int64[E_tot]`；
- graph ID 取值范围、节点前缀偏移、`node_count/edge_count:int64[B]` 及总数关系；
- 逐边同图断言
  \[
  \texttt{node\_graph\_id[receiver[e]]}
  =\texttt{edge\_graph\_id[e]}
  =\texttt{node\_graph\_id[sender[e]]}.
  \]

padding 批现已冻结 \(B,N_{\max},E_{\max}\) 下节点、边、位移、距离、特征和 bool mask 的 dtype/shape，无效边端点为 \(-1\)，有效端点必须落入同图有效节点前缀；padding 行在聚合、标准化统计、归一化和损失前排除。例 12-8、Q12-01/A12-01 给出了跨图边失败夹具。独立代入 `node_graph_id=[0,0,1,1,1]`、receiver=1、sender=3、`edge_graph_id=0` 时，同图等式为假，能够按书面契约拒绝。

原关闭条件全部满足。未发现 B01 修复引入新的内容错误。

### M6-CH12-B02：CLOSED

复核位置：

- `03_textbook/chapters/12_atomic_graph_representation/chapter.md:108-127`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:57-59`
- `06_exercises/04-stageD/12_atomic_graph/problem/readme.md:31-33`
- `06_exercises/04-stageD/12_atomic_graph/solution/readme.md:79-87`
- `08_audits/M6_stageD_work_package.md:162-166`

空入边策略现已完整区分：

- sum 返回零向量；
- mean 使用 \(\sum m/\max(1,\deg_{\mathrm{in}})\)，返回零向量并同时返回 `has_incoming=false`；空入边对不存在的消息分量梯度为零；
- max 不定义空集合值，validator 必须拒绝含空入边节点的图。

正文明确指出 sum 的约定不能自动推广到 mean/max，例 12-7 和 Q12-06/A12-06 同时覆盖成功行为、伴随 mask 与拒绝行为。独立复算空的 `float64 (0,3)` 消息数组得到 sum=\((0,0,0)\)、mean=\((0,0,0)\)、`has_incoming=false`，与材料一致。

原关闭条件全部满足。未发现 B02 修复引入新的内容错误。

### M6-CH12-B03：OPEN

复核位置：

- `03_textbook/chapters/12_atomic_graph_representation/chapter.md:247-277`
- 尤其 `03_textbook/chapters/12_atomic_graph_representation/chapter.md:253-265`
- `03_textbook/chapters/12_atomic_graph_representation/examples.md:45-55`
- `06_exercises/04-stageD/12_atomic_graph/problem/readme.md:35-37`
- `06_exercises/04-stageD/12_atomic_graph/solution/readme.md:89-117`
- `08_audits/M6_stageD_work_package.md:162-166`

绝大部分修复已经正确完成：\(P_{\max}\ge\max_e p_i p_j\)、右侧连续 padding、`mask[e,a]` 当且仅当 \(0\le a<p_i p_j\)、\(\alpha=\lfloor a/p_j\rfloor\)、\(\beta=a\bmod p_j\)、节点有序轨道列表、逐分量 int64 索引数组及 padding=\(-1\) 均已冻结；例 12-5 和 Q12-07/A12-07 也覆盖“真值数量正确但位置错误”与 \(P_{\max}\) 过小的失败夹具。

但是正文紧接着仍写成

\[
\sum_{a=1}^{P_{\max}}\texttt{mask}_{ea}=p_i p_j.
\]

这与同段冻结的零基索引 \(0\le a<P_{\max}\) 不一致。对 \(p_i=2,p_j=3,P_{\max}=9\)，合法 mask 在 \(a=0,\ldots,5\) 为真；正确的零基计数

\[
\sum_{a=0}^{P_{\max}-1}\texttt{mask}_{ea}
\]

等于 6，而当前显示范围若按合法数组索引取 \(a=1,\ldots,8\)，只能计得 5，并且上界 \(a=P_{\max}\) 越界。因此 B03 的位置契约与必要计数关系仍然自相矛盾，不能作为 T-D09 的无歧义 validator 规格。

剩余关闭条件：把 `chapter.md:264` 的求和范围改为与零基数组一致的 \(a=0,\ldots,P_{\max}-1\)，并复核正文、例题、练习、解答和工作包全部使用同一零基口径。

## 2. 新增问题

### M6-CH12-N01：例题编号顺序为 1—5、7、8、6

- 级别：`NON_BLOCKING`
- 位置：
  - `03_textbook/chapters/12_atomic_graph_representation/examples.md:45`（例 12-5）
  - `03_textbook/chapters/12_atomic_graph_representation/examples.md:57`（例 12-7）
  - `03_textbook/chapters/12_atomic_graph_representation/examples.md:61`（例 12-8）
  - `03_textbook/chapters/12_atomic_graph_representation/examples.md:65`（例 12-6）

B01/B02 修复新增例 12-7 与例 12-8 后，原有例 12-6 被留在其后，导致文件内标题次序为 1、2、3、4、5、7、8、6。内容本身没有错误，但编号漂移会破坏顺序导航和后续引用稳定性。

关闭条件：移动例 12-6 到例 12-7 之前，或一致地重编号后三例，使标题在文件中的顺序严格递增；不得改变其内容含义。

## 3. 直接相邻回归检查

- B01 修复没有改变 receiver/sender、反向 shift、多重边或完整 edge ID 契约。
- B02 修复没有把 mean 的默认零误称为观测均值；`has_incoming` 明确保留了二者差别。
- B03 修复没有改变行优先 \(a=\alpha p_j+\beta\) 或逐分量 provenance；当前唯一剩余实质问题是正文计数式的上下界。
- 工作包 4.5 与 T-D09 已同步加入跨图边、批 mask、空入边、连续块 mask、反解索引、padding 泄漏和 \(P_{\max}\) 过小的成功/失败要求。
- 修复后的五份直接文件均可按 UTF-8 严格解码；裸 CR 与非法控制字符均为 0，本地链接保持有效。未对源文件生成 Pandoc 派生输出。

## 4. 最终门控结论

B01、B02 已关闭；B03 因零基 mask 与一基求和范围冲突仍为 `OPEN`。另新增非阻塞编号问题 N01。当前结论为 `FAIL`，`BLOCKING=1`、`NON_BLOCKING=1`，因此不得完成 M6-03，也不得启动 M6-04。

主 agent 应修正 B03 的求和上下界并整理例题编号顺序，然后由本独立审计员再次执行定点复核。只有 B03 与 N01 均关闭、没有新增问题，且复核给出 `BLOCKING=0`、`NON_BLOCKING=0` 和明确 `PASS` 后，才允许完成 M6-03 并启动 M6-04。
