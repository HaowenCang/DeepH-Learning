# 阶段 D 张量追踪模板：从周期边键到边级轨道块

## 1. 目的与适用范围

本模板用于审计阶段 D 合成周期图、普通 MPNN、边级轨道块输出以及 concat/padded 批处理之间的逐字段对应关系。它要求先建立完整身份和几何，再读取预测数值；数值接近不能替代键、shape、dtype、mask 与 provenance 的一致性。

模板只适用于 `stageD-synthetic-v1`、`stageD-edge-output-v1` 和 `stageD-batch-v1` 合成对象。它不证明真实 Hamiltonian 标签、DeepH 实现、材料泛化或 DFT 后端正确。M8 前材料体系、DFT/数据后端与 DeepH 软件对象仍为 `UNRESOLVED_M8`。

## 2. 冻结约定

- 晶格采用行向量矩阵 \(A\)，分数坐标与笛卡尔坐标满足 \(r=fA\)。
- 有向边 \(e=(i\leftarrow j,n)\) 的 receiver 为 \(i\)，sender 为 \(j\)，位移为

  \[
  d_e=(f_j+n-f_i)A,\qquad \rho_e=\lVert d_e\rVert_2.
  \]

- 序列化分数坐标必须规范化到 \([0,1)^3\)，核心几何使用 `float64`，端点与 shift 使用 `int64`。
- 完整边键为

  \[
  K_e=(\text{structure\_id},i,j,n_1,n_2,n_3).
  \]

  规范 ID 的输入字节是 UTF-8 紧凑 JSON 数组
  `["stageD-edge-v1",structure_id,i,j,n1,n2,n3]`，随后计算 SHA-256。
- 允许同一有向原子对具有多个 shift，也允许 \(i=j,n\ne0\) 的非零自镜像；只排除 \(\rho_e=0\) 的零位移自环。
- MPNN 使用同步更新。所有第 \(\ell\) 层消息从冻结的 \(h^{(\ell-1)}\) 读取，不能在同一层内读取刚写回的状态。

详细约定见[统一图约定](stageD_graph_conventions.md)。

## 3. 图对象总表

对每个待审计结构先填写下表。shape 中 \(N\) 为节点数，\(E\) 为保留边数。

| 字段 | 期望 dtype/shape | 实际值或 hash | 独立重算 | 判定 |
|---|---|---|---|---|
| `schema_version` | 非空字符串，固定 `stageD-synthetic-v1` |  | 与代码常量比较 |  |
| `structure_id` | 非空字符串 |  | 逐图检查非空；batch 内允许重复，须结合 batch 槽位/graph ID 定位 |  |
| `cell` | `float64[3,3]` |  | \(\det A\ne0\)，\(\kappa_2(A)<10^8\) |  |
| `fractional` | `float64[N,3]` |  | 所有分量位于 \([0,1)\) |  |
| `cutoff` | 有限正标量 |  | 检查每条 \(0<\rho_e\le r_c\) |  |
| `condition_number` | 有限标量 |  | 由 `cell` 重算 |  |
| `bounds` | `int64[3]` |  | \(M_k=\lceil r_c\lVert A^{-1}_{:k}\rVert_2+1\rceil+\text{extra\_box}\) |  |
| `candidate_count` | 非负整数 |  | \(N^2\prod_k(2M_k+1)\) |  |
| `receiver/sender` | 各为 `int64[E]` |  | 范围均为 \([0,N)\) |  |
| `shift` | `int64[E,3]` |  | 与完整键逐行绑定 |  |
| `displacement` | `float64[E,3]` |  | 由端点、shift、cell 重算 |  |
| `distance` | `float64[E]` |  | \(\lVert d_e\rVert_2\) |  |
| `edge_instance_id` | 长度 \(E\) 的字符串数组 |  | 由规范字节逐行重算 |  |

图级判定必须同时满足：完整键无重复、ID 无重复、每个 ID 与所在行完整键一致、所有几何有限、候选计数与枚举盒一致。只验证 `distance = norm(displacement)` 不足以证明几何来自相应端点与 shift。

## 4. 单边逐字段追踪卡

对可疑边或抽样边复制一张卡。任何排序、置换、换胞或批处理变换都应当填写“变换前”和“变换后”两张，并通过完整键或 \(K_q\) 显式连接。

| 项目 | 记录 |
|---|---|
| structure ID |  |
| graph row |  |
| receiver \(i\) / sender \(j\) |  |
| shift \(n\) |  |
| 完整键 \(K_e\) |  |
| 规范 JSON 字节 |  |
| 重算 SHA-256 / 存储 ID |  |
| \(f_i\) / \(f_j\) |  |
| \(f_j+n-f_i\) |  |
| 重算 \(d_e\) / 存储 displacement / 最大残差 |  |
| 重算 \(\rho_e\) / 存储 distance / 绝对残差 |  |
| cutoff 成员资格 |  |
| edge feature 契约与重算残差 |  |
| block shape \((p_i,p_j)\) |  |
| \(P_{\max}\) 与有效分量数 \(p_ip_j\) |  |
| 连续前缀 component mask |  |
| 逐分量局部下标 \((\alpha,\beta)\) |  |
| 逐分量实际轨道 ID |  |
| prediction 与 unit |  |
| 标签、损失贡献及其来源（若存在） |  |
| 失败注入与预期异常类型 |  |

轨道分量按 row-major 展平：

\[
p=\alpha p_j+\beta,\qquad
\alpha=\left\lfloor p/p_j\right\rfloor,\qquad
\beta=p\bmod p_j.
\]

因此有效 mask 必须是长度 \(p_ip_j\) 的左连续 `true` 前缀；其余位置的局部下标为 \(-1\)，实际轨道 ID 为空字符串。mask 的 true 数量正确但位置不连续仍应拒绝。

## 5. 冻结主夹具示例

主夹具为

\[
A=\begin{bmatrix}
1.4&0&0\\
0.2&1.7&0\\
0.1&0.3&1.9
\end{bmatrix},\quad
F=\begin{bmatrix}
0.05&0.10&0.15\\
0.45&0.20&0.25\\
0.80&0.65&0.40\\
0.20&0.75&0.85
\end{bmatrix},\quad r_c=1.15.
\]

结构 ID 为 `stageD-main`。解析盒为 \((2,2,2)\)，所以候选数为

\[
4^2(2\cdot2+1)^3=2000,
\]

过滤后 \(E=18\)。排序后的前两条边具有相同 receiver/sender 但不同 shift：

| row | \(i\) | \(j\) | \(n\) | \(d_e\) | \(\rho_e\) | edge ID |
|---:|---:|---:|---|---|---:|---|
| 0 | 0 | 1 | \((-1,0,0)\) | \((-0.81,0.20,0.19)\) | 0.8556868586112564 | `d54362d206f507e42d9f1b6101e590e4e837a55261f973720b5267863c0707dd` |
| 1 | 0 | 1 | \((0,0,0)\) | \((0.59,0.20,0.19)\) | 0.6513063795173513 | `38b0103093e5bd6fb440865ae7072e24e003a2d43cd50c60738ba2cc3b08e3bf` |

第一行的分数位移为

\[
(0.45,0.20,0.25)+(-1,0,0)-(0.05,0.10,0.15)
=(-0.60,0.10,0.10),
\]

右乘 \(A\) 即得 \((-0.81,0.20,0.19)\)。该例直接反驳“每个原子对只保留一个邻居”或“shift 可由端点唯一恢复”的错误假设。

默认合成轨道表为节点 \(k\) 具有 `1 + k % 2` 个有序轨道。因此上述两条边的 receiver 0 有 1 个轨道，sender 1 有 2 个轨道，block shape 为 \((1,2)\)，有效局部分量依次为 \((0,0)\)、\((0,1)\)。实际轨道 ID 必须分别从节点表解析，不能由 prediction 列号猜测。

## 6. 变换追踪

### 6.1 节点置换与边行重排

设新编号满足 \(i'=\pi(i)\)、\(j'=\pi(j)\)。填写：

| 对象 | 变换规则 | 实际映射 | 残差/判定 |
|---|---|---|---|
| node features/orbital tables | 按 \(\pi\) 重排 |  |  |
| receiver/sender | 同时应用 \(\pi\) |  |  |
| shift/displacement/distance | 随边行同步搬移 |  |  |
| edge ID | 变换契约预先冻结 structure ID 是否改变；本阶段 T-D04 保持 ID 不变，只用同一 ID、新端点和 shift 重算 |  |  |
| prediction/mask/block shape | 按完整边映射同步搬移 |  |  |
| local index/actual orbital ID | 由变换后端点表复核 |  |  |

仅比较聚合数值不够；T-D04 要求非对称夹具中完整输出 schema 形成双射。若另行研究“结构同时改名”的扩展变体，必须在输入契约中先给出唯一的新 structure ID，再由它重算 edge ID；该变体不属于当前 C-D04/T-D04。

### 6.2 周期代表变换

若序列化代表改变为 \(\widetilde f_i=f_i+q_i\)，则

\[
n'=n+q_i-q_j,\qquad
n^{\mathrm{can}}=n'-q_i+q_j=n.
\]

为每条边记录 \((q_i,q_j,n,n',n^{\mathrm{can}})\)，以回拉完整键配对，再比较位移、距离、预测、mask 和轨道身份。公共平移只是 \(q_i=q_j\) 的特例；不能用它代替逐原子换胞测试。

### 6.3 concat 批

对每个图 \(g\) 记录 `node_offset[g]`、`edge_offset[g]`、节点数、边数、cell 与 cutoff。全局端点应满足

\[
i_{\mathrm{global}}=i_{\mathrm{local}}+\text{node\_offset}[g],
\qquad
j_{\mathrm{global}}=j_{\mathrm{local}}+\text{node\_offset}[g].
\]

检查每条边两端 `node_graph_id` 相同并等于 `edge_graph_id`；按图切片后应恢复原始完整键、几何、特征和输出。负 graph ID、跨图边或计数与数组不一致必须拒绝。

### 6.4 padded 批

对每个图记录 \(N_g,E_g,N_{\max},E_{\max},P_{\max}\)。有效 mask 必须是左连续前缀，局部端点在有效节点范围内；inactive 端点使用冻结哨兵值。NaN 或 \(10^{300}\) 可放在 inactive 浮点 padding 中作为污染探针，但前向、统计、归一化和 loss 必须先用 count/mask 切除，不能先读取再乘零。

记录三次运行的有效 prediction 与 loss：

| padding 探针 | prediction hash | loss | 与有限 padding 的残差 |
|---|---|---:|---:|
| 有限零 padding |  |  | 基线 |
| NaN padding |  |  |  |
| \(10^{300}\) padding |  |  |  |

合格条件为有效 prediction 与 loss 的残差均为 0；把任一污染行激活时 validator 必须拒绝。

## 7. MPNN 前向与反向追踪

对第 \(\ell\) 层记录：

| 对象 | shape | 来源 | 同步/聚合检查 | 数值检查 |
|---|---|---|---|---|
| \(h^{(\ell-1)}\) | \([N,d]\) | 上一层冻结快照 | 本层只读 | finite |
| sender gather | \([E,d]\) | \(h^{(\ell-1)}_j\) | 使用 sender | 与端点复算 |
| receiver gather | \([E,d]\) | \(h^{(\ell-1)}_i\) | 使用 receiver | 与端点复算 |
| edge feature | \([E,d_e]\) | distance-displacement-prefix-zero-pad-v1 | 按完整键 | 重建残差 |
| message/preactivation | 实现定义 | 权重与三类输入 | 无跨图读取 | finite |
| aggregate | \([N,d]\) | 按 receiver scatter | sum/mean/max 策略明确 | 空入边策略 |
| \(h^{(\ell)}\) | \([N,d]\) | 同步写回 | 不在本层再读取 | 支持集 |
| edge prediction | \([E,P_{\max}]\) | 端点状态与边特征 | 行与完整键绑定 | mask 后 loss |

masked MSE 使用

\[
\mathcal L=\frac{1}{S}\sum_{e,p}m_{ep}
(\widehat y_{ep}-y_{ep})^2,\qquad
S=\sum_{e,p}m_{ep}>0.
\]

反向追踪至少记录总有效分量数 \(S\)、输出梯度、receiver/sender 两条梯度路径、scatter-add、每层 tanh 导数和所有参数块的中心差分最大相对误差。T-D02 的合格阈值为 \(10^{-5}\)，且五类故障反传必须分别产生超过阈值的检测量。

## 8. 失败注入矩阵

每次追踪至少选择一项身份故障、一项几何故障、一项 shape/mask 故障和一项批处理故障。记录变异前 hash、变异字段、期望异常类型、实际异常与是否穿透。

| 类别 | 最小变异 | 期望 |
|---|---|---|
| 身份 | 保持端点/shift 不变但伪造 ID；或只交换 prediction 行 | validator 拒绝 |
| 几何 | 独立滚动 displacement；或令 cutoff 小于某条 distance | validator 拒绝 |
| cell/坐标 | 奇异 cell；非规范 fractional | validator 拒绝 |
| provenance | 改 block shape；打乱实际轨道 ID；非连续 mask | validator 拒绝 |
| edge-output | prediction 或分量数组增删一行 | validator 拒绝 |
| concat | 跨图端点；负 graph ID；错误计数 | validator 拒绝 |
| padded | rank-4 node features；prediction 宽度与 mask 不同；激活 NaN padding | validator 拒绝 |
| 聚合 | max 遇空入边 | 明确拒绝 |
| 分组 | 同一 group ID 同时进入 train/test | validator 拒绝 |
| 周期枚举 | 固定小盒或只保留最小镜像 | 与完备边键不一致 |

## 9. 完成记录

完成一次追踪后记录：

- 代码快照 SHA-256；
- Python、NumPy、SciPy 精确版本及 `pip check`；
- 输入结构 hash、规范输出 hash 和运行 seed；
- 使用的 validator、测试 ID 和命令；
- 所有残差及其阈值；
- 失败注入总数、实际拒绝数和任何穿透；
- 尚不能由本追踪推出的结论。

可执行实现与命令见[阶段 D 代码说明](../05_code_exercises/stageD_synthetic_mpnn/README.md)，端到端练习见[综合题](../06_exercises/04-stageD/comprehensive/problem/readme.md)和[参考解答](../06_exercises/04-stageD/comprehensive/solution/readme.md)。
