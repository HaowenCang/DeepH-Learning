# M7-01 阶段 E 工作包定点复核

## 1. 复核结论

- 复核日期：2026-08-09
- 原审计报告：`M7_stageE_work_package_independent_audit.md`
- 总结论：`FAIL`
- 原问题状态：
  - `M7-E-WP-B01`：`CLOSED`
  - `M7-E-WP-B02`：`OPEN`
  - `M7-E-WP-N01`：`CLOSED`
- 新增问题：0
- 剩余 `BLOCKING=1`
- 剩余 `NON_BLOCKING=0`
- M7-01：**仍不得标记为 `COMPLETED`**
- M7-02：**仍不得启动**

主 agent 已正确修复 CG 整通道相位自由与局部相位错误的数学区分，并为 MIT 8.512 补充快照补齐作品级 provenance。旋转/四元数 validator、局部架退化阈值、A/B 主配置、144 点扫描轴和 wall-time 隔离也已显著闭合。B02 仍未完全关闭的唯一原因是：144 点网格没有规定每个组合使用哪个合成图 ((N,E))，且一方面禁止 A/B 配置字段冲突，另一方面网格又必须交叉组合 A/B 的 seed、dtype、旋转数、multiplicity 和尺度；此外“精确 FLOP”与“乘加次数”尚未给出唯一换算口径。由此，同一 144 点规范仍可产生不同 shape、数组字节和成本摘要。

## 2. 复核范围与只读约束

定点复核覆盖以下修订文件及其相邻契约：

- `08_audits/M7_stageE_work_package.md`；
- `03_textbook/stageE_representation_conventions.md`；
- `01_sources/documentation/stageE/README.md` 及 11 个固定快照；
- `02_source_ledger/source_table.csv`；
- `01_sources/bibliography.bib`；
- 第 15—20 章全部 `sources.md` 与 `outline.md`，重点复核第 18 章；
- 原审计涉及的 D-E01—D-E09、T-E01—T-E12、C-E01—C-E12 和 M8/M9 授权边界。

本次没有修改任何送审文件。数值复算、Pandoc、链接、CSV/BibTeX 和哈希检查均为只读操作；唯一新增文件为本复核报告。

送审的七个修订核心文件实测 SHA-256 分别为：

| 文件 | 实测 SHA-256 | 与送审值 |
|---|---|---|
| `M7_stageE_work_package.md` | `CB419547825C9C015903F3CB84932B56DAB8C93DEC71B3B256246130754AD109` | 一致 |
| `stageE_representation_conventions.md` | `2D823BAEC2AA2FC20E4A19C90351221173E888BDD5958EE74BA9EC89A097A40E` | 一致 |
| `stageE/README.md` | `428D005DF19C1FFB0B4010C3F5DA9931AFFD6871344C53ADDEB4B04F68CF504C` | 一致 |
| `source_table.csv` | `EC863C69AB5BAC04961528117DED9B773709D87E91B75FB220295BCFD84763D7` | 一致 |
| `bibliography.bib` | `B1C6F269B563C2205BCA1126280D7AF609CBFA7381B61A06BF1C2147FD656139` | 一致 |
| 第 18 章 `sources.md` | `167FE79D8CA4C9136E6D23AAC676CFBFDFFA4C8FE573A9045505888E1F434FD1` | 一致 |
| 第 18 章 `outline.md` | `D52AF984DE901D01020ABCFF473DA608987C4138513F53F7BB0F0B375B370608` | 一致 |

## 3. M7-E-WP-B01 定点复核：CLOSED

### 3.1 修订内容

`stageE_representation_conventions.md` 现在明确区分：

- 固定 (L) 输出通道整体乘 \(e^{i\phi_L}\) 或实基中的 ±1，是合法输出基变换；若表示基和下游映射同步改变，不破坏正交性或 intertwiner；
- 项目仍以 DLMF/Condon--Shortley 表固定唯一序列化规范，因此未同步元数据的整通道相位改变只应报告为“规范表不一致”；
- 单个非零系数、部分 (M) 行或未施加交换相位的输入轴互换，才是规范表或 intertwiner 的定向失败对象。

T-E05 已分别要求规范表逐项比对和 intertwiner 检查；D-E04、C-E05、第 18 章 `sources.md`/`outline.md` 也同步使用同一边界，没有再把基自由误写为数学等变性破坏。

### 3.2 独立复算

复核员按 DLMF 34.1.1 的 CG--(3j) 关系和整数 Racah 求和独立生成 \(1\otimes1\) 全部 CG 系数，得到三个锚点：

\[
C^{00}_{1,1,1,-1}=0.5773502691896257,
\quad
C^{11}_{1,1,1,0}=0.7071067811865475,
\quad
C^{22}_{1,1,1,1}=1,
\]

分别等于 \(1/\sqrt3\)、\(1/\sqrt2\)、1。输入交换关系

\[
C^{LM}_{ell_2m_2,ell_1m_1}
=(-1)^{ell_1+ell_2-L}
C^{LM}_{ell_1m_1,ell_2m_2}
\]

在 \(1\otimes1\) 全表上的最大误差为 0。

把 CG 矩阵写成从未耦合九维空间到 (L=0,1,2) 直和空间的矩阵后，原表正交误差为 \(5.10\times10^{-16}\)，三个角动量生成元的最大 intertwiner 残差为 \(6.94\times10^{-16}\)。整个 (L=0) 通道统一翻号后残差仍为 \(6.94\times10^{-16}\)；只翻转 (L=1,M=0) 行时残差变为 (2.8284)，只翻转一个非零系数时残差为 2。该结果与修订后的分类完全一致。

### 3.3 关闭判断

B01 的四项最小关闭条件均已满足，且相邻 D-E04、T-E05、C-E05 和第 18 章没有出现相位语义回归。`M7-E-WP-B01=CLOSED`。

## 4. M7-E-WP-B02 定点复核：OPEN

### 4.1 已关闭部分

旋转矩阵 validator 已冻结

\[
\epsilon_R=\frac{\lVert R^{\mathsf T}R-I\rVert_F}{\max(1,\lVert I\rVert_F)},
\qquad
\epsilon_{\det}=|\det R-1|,
\]

四元数 validator 已冻结 εq=|||q||2-1|。float64 阈值为 \(5\times10^{-12}\)，float32 为 \(5\times10^{-6}\)，等于阈值时接受；validator 不静默归一化用户输入。唯一四元数符号以首个超过 \(32\,\mathrm{eps}(\mathrm{dtype})\) 的分量为正确定，负零也有规范化规则。

独立按实际 dtype 复算 \(R_\delta\) 与 \(q_\delta\) 边界夹具：float64/float32 下的 \(0.4\tau_R\)、\(0.5\tau_q\) 均接受，\(2\tau_R\)、\(2\tau_q\) 均拒绝。反射、零/非有限四元数、错误 rank/shape 的拒绝入口也已经明确。

局部架现在使用特征长度归一化的 ζu,ζv 和无量纲

\[
\eta=\lVert\widehat u\times\widehat v\rVert_2.
\]

float64 的 τ0/τframe 为 (10^{-12}/10^{-8})，float32 为 (10^{-5}/10^{-4})，两者等于阈值时均拒绝。对冻结 \(v_\varepsilon\) 序列逐 dtype 复算后，(0,τ/4,τ/2,τ) 落在拒绝侧，(2τ,4τ,10^{-2}) 落在接受侧；先检查长度再归一化和禁止后备轴的顺序自洽。

A/B 主配置已给出唯一 seed、dtype、旋转数、multiplicity、((N,E)) 和尺度。规范 JSON 排除了 wall-time、绝对路径、PID、NaN/Infinity，两个子进程的 stdout 字节一致要求可执行。T-E10 的五个扫描轴包含

\[
2\times2\times4\times3\times3=144
\]

个组合，3 次 warm-up、7 次 wall-time、median/IQR 及 stdout/hash 隔离规则也已冻结。这些修订关闭了原 B02 关于 validator、局部架、样本量、seed 和 wall-time 混入确定性证据的主要缺口。

### 4.2 剩余缺口

`stageE_representation_conventions.md:263-268` 把 A/B 定义为不可用冲突显式字段覆盖的完整配置：A 对应 seed 20260809、float64、64 次旋转、((N,E)=(4,8))；B 对应 seed 20260810、float32、257 次旋转、((7,18))。但 `270-282` 的 T-E10 网格把 seed、dtype、旋转数、multiplicity 和尺度重新作完全笛卡尔积，没有说明扫描点的合成图使用：

- 固定 ((4,8))；
- 固定 ((7,18))；
- 按 seed 映射到 A/B 的图；
- 两个图都运行，从而形成 288 点；
- 或其他图生成式。

这不是无关实现细节。图的 (N,E) 会改变聚合 shape、数组激活字节和 contraction 成本；例如 seed 20260809 + float32 + 257 次旋转 + multiplicity 倍率 4 的扫描点既不是 A，也不是 B，而当前没有独立规则决定其图 shape。若使用 `config=A` 再显式覆盖 dtype/旋转数，又与“冲突字段必须拒绝”发生冲突。因而 144 点可以被不同实现解释为不同对象，规范 stdout 的 FLOP/字节不能唯一比较。

同一段还交替使用“由 contraction shape 直接计数的乘加次数”和“精确 FLOP”。一个 multiply-add 可报告为 1 MAC，也可按一个乘法加一个加法报告为 2 FLOP；当前没有规定规范 JSON 保存 `mac_count`、`flop_count` 还是二者，也没有规定激活字节是逐数组清单、所有中间数组总和还是峰值同时存活字节。这不影响等变残差，但会直接改变 T-E10 声称的精确成本字段。

### 4.3 剩余最小关闭条件

1. 冻结 144 点扫描的图契约：明确每个点的 ((N,E))、图生成式/edge identity 和 seed 的作用；若两个图都扫描，应更正总点数，若按 seed 映射，应明确写出映射。
2. 明确扫描模式不通过 A/B 完整配置覆盖字段，或为 scan CLI 冻结字段优先级，使 144 点交叉组合不与“config 冲突字段拒绝”矛盾。
3. 冻结成本计数名称与单位，例如同时输出 `mac_count` 和 `flop_count=2*mac_count`（若只计乘加 contraction），并说明其他操作是否计入；不得把 MAC 数值无说明地标成 FLOP。
4. 冻结数组字节口径，至少输出被计数组的名称、shape、dtype、逐数组字节和明确的 total/peak 定义，使同一扫描点可以独立复算。

因此 `M7-E-WP-B02=OPEN`。该判断不否定已经正确冻结的 validator、局部架、A/B 和 wall-time 隔离部分。

## 5. M7-E-WP-N01 定点复核：CLOSED

E-SUP-01 现在具有：

- 明确作品名 *Lecture 10: Superconductors With Disorder*；
- MIT OCW 8.512、2009 年春季、Mark Spencer Rudner 与课程教师 Patrick Lee；
- 准确官方 PDF URL、访问日期、固定版本说明；
- CSV 中唯一的 E-SUP-01 行和 `SUPPLEMENTAL_ARCHIVE` 证据状态；
- BibTeX 键 `rudner2009solids2lec10`；
- 本地 SHA-256 `426E41E4ED6BCC48DF8256572F7D969DD47024E75DC0DAB96F0B04C0C0B70BFA`。

官方 URL 的只读 HEAD 响应为 `200 OK`、`application/pdf`、`Content-Length: 450728`，与本地文件长度一致。README、CSV 和 BibTeX 均明确它只作检索留档，不进入 M7 公式或章节范围的直接证据链；E-FND-03 仍是时间反演主线来源。`M7-E-WP-N01=CLOSED`。

## 6. 格式、链接、台账、哈希与相邻回归

- 15/15 核心 Markdown 以 `markdown+tex_math_single_backslash` 严格 Pandoc 解析通过，共 330 个 MathML 数学节点。
- Pandoc AST 识别 46 个活动链接，其中 38 个为本地链接；本地缺失数为 0。
- 裸 CR 和非法控制字符均为 0。
- CSV 共 47 行（含表头），每行 17 字段，46 个来源 ID 唯一；E-SUP-01 恰有一行。
- BibTeX 共 46 个唯一键，花括号平衡为 0；`rudner2009solids2lec10` 恰有一项。
- stageE README 登记的 11 个快照哈希逐项与实体一致。
- D-E01—D-E09、T-E01—T-E12、C-E01—C-E12 编号无缺失或重复。除 B02 的成本扫描口径外，主动/被动、复—实映射、Hamiltonian、宇称、时间反演和 M8/M9 授权边界没有回归。
- 第 18 章新增的 18.2.5、18.3.4—18.3.5、18.7.3—18.7.4 与修订 CG 契约一致；没有改变第 15→16→17→18→19→20 章依赖顺序，也没有提前选择 e3nn/DeepH 软件版本。

## 7. 最终门控意见

B01 和 N01 已关闭，没有新增问题；B02 的 validator、局部架、主配置和 wall-time 分离部分已通过，但 144 点扫描的图对象及精确成本口径仍不唯一。主 agent 应只修复第 4.3 节的剩余条件，然后交回原审计员再次定点复核。只有复核确认 `M7-E-WP-B02=CLOSED`、新增问题为 0，并给出 `PASS`、`BLOCKING=0`、`NON_BLOCKING=0` 后，才允许将 M7-01 标记为 `COMPLETED` 并启动 M7-02。
