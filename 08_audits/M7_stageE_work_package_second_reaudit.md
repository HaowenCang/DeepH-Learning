# M7-01 阶段 E 工作包第二次定点复核

## 1. 复核结论

- 复核日期：2026-08-09
- 复核对象：第一次定点复核仍为 `OPEN` 的 `M7-E-WP-B02`
- `M7-E-WP-B02`：`CLOSED`
- 新增问题：0
- 总结论：`PASS`
- `BLOCKING=0`
- `NON_BLOCKING=0`
- M7-01：**允许标记为 `COMPLETED`**
- M7-02：**允许启动**

本轮修订已把 144 点扫描从 A/B 主配置中分离为互斥的 `stageE-scan-v1` 模式，以 seed 唯一选择 (G_A/G_B)，冻结两图的节点坐标、有向边顺序、零 shift 和完整 edge identity，并固定 PCG64 抽样顺序、float64 生成后转换目标 dtype 的规则以及尺度作用对象。参考 kernel 的 shape、MAC、FLOP、receiver 聚合加法、逐数组字节、完整物化 total 和参考流式 peak 均已形成可独立复算的唯一契约。指定的两个整数锚点经本审计员逐数组复算全部精确一致。

## 2. 只读范围与送审快照

本次仅复核：

- `03_textbook/stageE_representation_conventions.md` 第 11.3 节；
- `08_audits/M7_stageE_work_package.md` 的 T-E10 及相邻 D-E09/T-E12 契约；
- 第一次定点复核报告第 4.3 节的四项剩余关闭条件；
- 15 份 M7-01 核心 Markdown 的格式、链接、控制字符及相邻 D-E/T-E/C-E 编号回归。

没有修改任何现有文件。所有数值计算、RNG 指纹、Pandoc 和链接检查均通过只读命令或标准输出完成；唯一新增文件为本报告。

两份核心修订文件实测 SHA-256 为：

| 文件 | 实测 SHA-256 | 与送审值 |
|---|---|---|
| `03_textbook/stageE_representation_conventions.md` | `F0C469F2101A90C2B68FF26481BF13AFD16C9E1D3B3AFBF9BF9C5BFBE5D17254` | 一致 |
| `08_audits/M7_stageE_work_package.md` | `5F432058E1C89A10D52604412F481098FD75A42AF152F7AD4FBB5884ACAD9CDE` | 一致 |

## 3. 144 点 scan、A/B 与图身份：通过

### 3.1 模式与字段互斥

统一约定现在明确规定：

- config A/B 是完整主配置，任何冲突显式字段均拒绝；
- `stageE-scan-v1` 是独立模式，不读取 A/B 默认值，也不接受任意字段覆盖；
- scan 只能完整枚举 dtype、seed、(n_R)、multiplicity 倍率和尺度的冻结笛卡尔积；
- 规范 case ID 只允许只读单点重放，单点结果不能替代门控网格。

因此 scan 中的交叉组合不再通过覆盖 config A/B 生成，第一次定点复核指出的字段优先级冲突已经消失。网格点数独立复算为

\[
2\times2\times4\times3\times3=144.
\]

### 3.2 seed 到固定图的唯一映射

seed 20260809 唯一选择 (G_A)，seed 20260810 唯一选择 (G_B)；图本身不由 RNG 抽样。复核重建得到：

- (G_A)：(N=4,E=8)，八条有向边严格按文中顺序，四个节点入度均为 2；
- (G_B)：(N=7,E=18)，九条无向原型均按“较小端点接收在前、反向在后”展开，节点入度依次为 ((3,2,3,3,2,3,2))；
- 两图每条 shift 均为 ((0,0,0))；完整 identity 均为 \((\mathrm{receiver},\mathrm{sender},0,0,0)\)；8/8 和 18/18 identity 各自唯一；
- α 只缩放固定节点坐标和随后按冻结顺序生成的连续 \(x_\ell,W_\ell\)，不改变 (N,E)、端点、shift、edge identity 或边顺序。

不同 seed 的图 shape、成本和字节现已由契约唯一决定，不再存在固定 (G_A)、固定 (G_B)、seed 映射或 288 点之间的多种解释。

## 4. PCG64、draw order、dtype 与尺度：通过

每个 scan case 唯一使用

```text
numpy.random.Generator(numpy.random.PCG64(seed))
```

并依次抽取：

1. float64、C-order、shape ((n_R,4)) 的标准正态四元数；
2. 按 ℓ=0,1,2 的顺序抽取节点特征 \(x_\ell\)；
3. 按 ℓ=0,1,2 的顺序抽取逐边权重 \(W_\ell\)。

所有随机数组先以 float64 生成，再转换到目标 dtype；四元数在目标 dtype 中归一化并执行第 11.1 节的唯一符号规范。图不消耗 RNG draw，故图选择不会改变连续数组的抽样偏移。以 float64、(n_R=1,m=1) 按上述顺序拼接原始 draw 字节，本轮复算得到审计用指纹：

- (G_A)/seed 20260809：`e6e23346a154e0d98a7d6d7dca9db116a030f1653c0939a1d7ea8e0fea3a1f59`；
- (G_B)/seed 20260810：`189f627dda3ecee4c617b92dfca8de771efeb674fc888f6b0a0aeb7365d563b7`。

这些指纹不是新增门控常量，只用于证明本复核确实按文字独立执行了 draw order。当前契约已经足以使后续代码产生可重复的同一序列。

## 5. kernel、MAC/FLOP 与聚合加法：通过

参考 kernel 对每个 ℓ 固定

\[
x_\ell:(N,n_\ell,2\ell+1),\quad
W_\ell:(E,n_\ell,n_\ell),\quad
m_\ell:(E,n_\ell,2\ell+1),\quad
h'_\ell:(N,n_\ell,2\ell+1),
\]

其中 \(n_\ell=m(2,2,1)_\ell\)。成本口径现在明确区分：

- `mac_per_rotation` 为 contraction 中的乘加数；
- `mac_total=n_R*mac_per_rotation`；
- 每 MAC 固定按一次乘法加一次累加计为 2 FLOP，故 `flop_total=2*mac_total`；
- `flop_total` 不含 receiver 聚合、旋转生成、validator、归一化、非线性和内存移动；
- receiver 聚合使用独立的 `aggregation_add_per_rotation` 及其 total。

对 (m=1)，三个通道的 \(n_\ell\) 为 ((2,2,1))，故

\[
\sum_{\ell=0}^2 n_\ell^2(2\ell+1)
=4+12+5=21.
\]

于是 (G_A) 的 MAC 为 \(8\times21=168\)，(G_B) 为 \(18\times21=378\)。receiver 聚合的每分量最小加法因子分别为

\[
G_A:\sum_i\max(\deg_i^--1,0)=4,
\qquad
G_B:\sum_i\max(\deg_i^--1,0)=11,
\]

而 \(∑_ℓ n_\ell(2\ell+1)=13\)，因此聚合加法分别为 \(4\times13=52\) 与 \(11\times13=143\)。文中的 168/52 和 378/143 均精确复现。

## 6. 逐数组字节、total 与 reference peak：通过

统一约定要求规范摘要逐名称保存 shape、dtype、nbytes，包含 coordinates、receiver、sender、shift、rotations 及全部 \(x_\ell,W_\ell,m_\ell,h'_\ell\)。浮点数组使用目标 dtype，receiver/sender/shift 使用 int64。`array_bytes_total` 是所有命名数组完整物化一次的总和；`array_bytes_peak` 是冻结参考流式调度的常驻数组加单个最大 \(m_\ell\)。NumPy 未暴露临时量、解释器/allocator、BLAS workspace 明确排除，口径唯一。

### 6.1 (G_A) 锚点

float64、(n_R=1,m=1) 时，独立逐组重算为：

| 数组组 | nbytes |
|---|---:|
| coordinates | 96 |
| receiver + sender + shift | 320 |
| rotations ((1,3,3)) | 72 |
| 全部 \(x_\ell\) | 416 |
| 全部 \(W_\ell\) | 576 |
| 全部 \(m_\ell\) | 832 |
| 全部 \(h'_\ell\) | 416 |

因此

\[
\mathrm{array\_bytes\_total}=2728.
\]

参考 peak 的常驻部分为 1896 字节，最大的单个消息数组是 (m_1:(8,2,3)) 的 384 字节，故 peak 为 (1896+384=2280)。

### 6.2 (G_B) 锚点

相同 dtype、(n_R,m) 下，独立逐组重算为：

| 数组组 | nbytes |
|---|---:|
| coordinates | 168 |
| receiver + sender + shift | 720 |
| rotations ((1,3,3)) | 72 |
| 全部 \(x_\ell\) | 728 |
| 全部 \(W_\ell\) | 1296 |
| 全部 \(m_\ell\) | 1872 |
| 全部 \(h'_\ell\) | 728 |

因此 total 为 5584。参考 peak 的常驻部分为 3712 字节，最大的 (m_1:(18,2,3)) 为 864 字节，故 peak 为 (3712+864=4576)。

四个指定字节锚点 2728/2280、5584/4576 均精确复现。数组清单、total、peak 与排除项已经满足第一次定点复核第 4.3 节的最后一项关闭条件。

## 7. 相邻契约与格式回归

- `M7_stageE_work_package.md` 已同步写明 scan/config 互斥、seed→图、edge identity、PCG64、MAC/FLOP、聚合加法、逐数组/total/peak 及 wall-time 分离；T-E10 的正向和失败入口与统一约定一致。
- D-E09 仍区分数学残差、浮点误差、模型误差和成本；T-E12 仍执行 schema、阈值和授权边界硬拒绝；D-E/T-E/C-E 编号无缺失或重复。
- 本轮没有改变 B01 已关闭的 CG 相位约定、N01 已关闭的来源 provenance、主动/被动、Hamiltonian、宇称、时间反演或 M8/M9 双授权边界。
- 15/15 核心 Markdown 以 `markdown+tex_math_single_backslash` 严格 Pandoc 解析通过，共 367 个 MathML 节点；Pandoc AST 得到 46 个链接，其中 38 个本地活动链接全部存在；裸 CR 和非法控制字符为 0。

## 8. 最终门控意见

第一次定点复核第 4.3 节的四项剩余关闭条件全部满足，`M7-E-WP-B02=CLOSED`。结合第一次定点复核已经关闭的 B01/N01，M7-01 当前新增及剩余问题均为 0。允许把 M7-01 标记为 `COMPLETED`，并按依赖顺序启动 M7-02 第 15 章材料建设。
