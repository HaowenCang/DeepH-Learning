# M5-05 第 8 章独立正式内容审计

- 审计日期：2026-08-04
- 审计对象：阶段 C 工作包 M5-05、D-C06/D-C07、T-C05—T-C08 和 `stageC-label-v1`；第 8 章资料包、提纲、正文与例题；D-C06/D-C07 推导；Q8-01—Q8-10 及参考解答；决策记录
- 审计性质：独立材料完备性、可自学性、公式条件、来源边界、数值协议、授权边界和制品可验证性审计
- 总体结论：`FAIL`
- `BLOCKING`：1 项
- `NON_BLOCKING`：2 项
- 是否允许 M5-05 标记为 `COMPLETED`：**否**
- 是否允许启动 M5-06：**否**

第 8 章已经正确覆盖 norm-conserving 条件及 transferability 边界、ultrasoft/PAW 分类边界、平面波正交与完整形式体系 `S=I` 的条件、局域非正交基与广义本征问题、多轴误差、等谱但矩阵不同、标签 schema 及 M8/M9 禁令。T-C05—T-C08 的全部冻结数值和故障判据均可独立复算，七个材料文件的严格 Pandoc、控制字符、链接和四个 Python 代码块检查也全部通过。当前唯一阻塞是非正交目标空间只给出了矩阵元、overlap 和正交投影算符，没有闭合非正交重建算符及其损失语义；这使 D-C07 的“投影/重建误差到标签语义”在正交情形完整、在非正交情形不完整。

## 1. 审计范围与 SHA-256 快照

除新增本报告外，本次审计未修改任何被审材料。审计时字节快照如下。

| 文件 | 审计时 SHA-256 |
|---|---|
| `08_audits/M5_stageC_work_package.md` | `810D80D0AC0605ECEB5B77E30D8DF72ECB6329DA7CD5E662A1AFFBF0950F3C39` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/sources.md` | `56F8B4F0333CB6BF00266670B0931BF6834B756A5350F5FC0765299266BA6F51` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/outline.md` | `F27DC48EB308F00558EAE8F5E4CFCC9C4376D580A1A2A928E1AB1CD291B29208` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/chapter.md` | `2223A3F16E2BEB36ABD196F4A90DDC8C2F1B4D6D3D2DA33176B891DA2DAA0C69` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/examples.md` | `B9E11ED1AD7DCC518874F4117F6016A5CEE54F7701B1CDB521E3C4ECE7AFA8DD` |
| `04_derivations/stageC/08_representation_and_label_error.md` | `F48F8B08BC0D5D085E51BAC039C17BA59FB618B607521F9A8A4BECB333EE0F20` |
| `06_exercises/03-stageC/08_basis_pseudopotential_errors/problem/readme.md` | `9D642EB0572444516EEF04586D6AE68C2FF92B924331FBDF9D3EF6618957A0F5` |
| `06_exercises/03-stageC/08_basis_pseudopotential_errors/solution/readme.md` | `36674867BF862793758A759F891C141B2D4EB1EF30300B1749F498960F212FD4` |
| `decisions.md` | `272AED3AD8B771EA0D80FD1C06BECEDB9694A29A994323F820C61E9B2C0CE318` |

## 2. 已通过项

### 2.1 赝势条件、transferability 与形式体系边界

正文针对固定角动量通道、参考能量和核心半径，列出了参考本征值、核心区外径向波函数、核心区范数、匹配连续性以及对数导数和能量导数等 norm-conserving 条件，并明确把这些条件限制为参考环境附近的散射 transferability 依据，而不是任意化学环境、压力、氧化态或高能未占据态的统一精确性证明。该表述与 Hamann、Schlüter、Chiang 原始论文的对象和边界相符。

ultrasoft/PAW 只作为不同形式体系接口出现，材料没有以 norm-conserving 条件替代增强电荷、投影子、变换算符或广义重叠对象的完整定义，也没有选择具体赝势族或数据集。材料还正确区分了“平面波基 Gram 矩阵为单位阵”与“完整形式体系没有广义重叠算符”两个命题。

### 2.2 平面波、局域基与多轴误差

D-C06 从 Galerkin 条件逐步得到

\[
Hc=ESc,
\qquad
H_{\mu\nu}=\langle\phi_\mu|\hat h|\phi_\nu\rangle,
\qquad
S_{\mu\nu}=\langle\phi_\mu|\phi_\nu\rangle,
\]

并给出矩阵形状、Hermitian 条件和线性无关基导致 `S` 正定的证明。局域基病态时的小 overlap 特征值、扰动放大、删除方向改变有效子空间及阈值记录要求均明确。平面波正交证明限定在固定周期胞、固定 `k`、标准 `L2` 内积和一致归一化下，未把 `S=I` 无条件外推到 ultrasoft/PAW 等广义范数形式。

cutoff、FFT/辅助网格、`k` 采样、smearing、SCF/本征求解容差和投影被明确划分为独立误差轴。材料没有把 SCF 收敛当作基组或采样收敛，也没有把两个层级的局部平台当作已知真值误差。

### 2.3 正交投影、等谱反例与验证门控

正交目标子空间满足

\[
H_p=B^\dagger HB,
\qquad
H_r=B H_p B^\dagger=P_BHP_B,
\qquad
P_B=BB^\dagger,
\]

相应幂等回投残差和 Frobenius 丢失范数语义正确。unitary 相似变换的等谱关系与固定坐标中的矩阵差被清楚区分；材料没有以能带一致替代矩阵一致，也没有以矩阵接近无条件推出敏感物性接近。能带、矩阵和目标物性三类门控的对象和适用条件明确。非正交重建链的缺口另列 B01。

### 2.4 T-C05—T-C08 独立复算

使用固定解释器 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 复算得到：

| 测试 | 关键独立结果 | 判定 |
|---|---|---|
| T-C05 | 正序列误差 `(0.12,0.03,0.008,0.002,0.0005)`，相邻差 `(0.09,0.022,0.006,0.0015)`；负序列 32/64 差 `0.0005`，128 参考误差 `0.008` | 正例与局部假平台失败均符合冻结阈值 |
| T-C06 | `I0(1)=1.2660658777520084`；`N=16,32,64` 误差均 `2.220446049250313e-16`；32/64 差为 0；注入 `0.01` 后总误差大于 `0.005` | 采样轴与基轴分离成立 |
| T-C07 | 广义谱 `(-1.2,-0.1,0.8,2.0)`；`lambda_min(S')=1.2154403466447898`；归一残差最大约 `1.49e-16`；忽略 overlap 的最大谱差 `0.9674651567663939` | 正例与 `overlap_ignored` 失败均成立 |
| T-C08, seed 20260805, d=12 | `p=5,q=3`；正交误差 `1.43e-15`；回投残差 `5.77e-16`；丢失范数 `0.95985867258085`；等谱矩阵差 `0.23306075775057758` | 全部通过 |
| T-C08, seed 20260806, d=16 | `p=5,q=5`；正交误差 `7.23e-16`；回投残差 `5.64e-16`；丢失范数 `0.9833167163767138`；等谱矩阵差 `0.17451989619254055` | 全部通过 |

题目 Q8-05—Q8-08 和参考解答逐项复现同一模型、容差和失败注入。未把尚属 M5-08 的正式测试框架误写为 M5-05 已完成对象。

### 2.5 标签 schema 与 M8/M9 边界

工作包中的 `stageC-label-v1` 最低 schema 覆盖生成状态、后端版本/提交、输入输出制品与 SHA-256、合成结构及边界、理论与赝势/全电子身份、基/网格、自旋、采样、电子数与占据、收敛、矩阵单位与索引、晶格位移方向、bra/ket、Fourier 正逆约定、相位/规范、overlap、投影窗口/维数/损失、能带/矩阵验证、环境、seed 与审计状态。正文和 Q8-09 的分组摘要与该 schema 不冲突；材料明确区分“schema 完整”“数值正确”和“物理目标充分”。T-C09 的逐路径删除负例仍被正确保留到 M5-08 实现。

正文、推导、例题、题目和答案均限定为解析或合成对象，没有安装或运行 DFT/DeepH、下载正式数据、生成正式标签、选择材料、冻结后端、赝势族、基、投影软件或实践版本。M7-I 后进入 M8 集中冻结、M8 冻结后 M9 外部动作前再次取得明确授权的表述与 D-010、D-011 一致。

### 2.6 材料完备性与可自学性

正文、四个例题、D-C06/D-C07 推导、十题十解和题目—材料映射已形成主要自学路径。Q8-01—Q8-10 与答案 ID 严格一一对应；每题均给出对象、公式、数值或判断边界。除 B01 指出的非正交重建缺口外，知识范围、失败样例和验证入口完整，没有因材料建设模式取消学习者作答而降低内容或技术强度。

## 3. BLOCKING finding

### M5-C8-B01：非正交目标空间缺少完整重建算符与重建损失，D-C07 的表示转换链未闭合

**位置：** `03_textbook/chapters/08_basis_pseudopotential_errors/chapter.md:182-196`；`04_derivations/stageC/08_representation_and_label_error.md:241-267`；`06_exercises/03-stageC/08_basis_pseudopotential_errors/solution/readme.md:212-223`。对照工作包 D-C07 的“固定表示和投影映射；离散/投影/重建误差到标签语义”要求。

当前材料对列满秩的非正交 `B` 正确给出

\[
H_B=B^\dagger HB,
\qquad
S_B=B^\dagger B,
\qquad
P_B=B S_B^{-1}B^\dagger,
\]

以及广义本征问题 `H_B c = E S_B c`，但到此即止。对于固定完整空间内积，正交投影后的完整空间算符应明确为

\[
H_r^{(\mathrm{nonorth})}
=P_B H P_B
=B S_B^{-1}H_B S_B^{-1}B^\dagger.
\]

该式与正交情形的 `B H_B B†` 只有在 `S_B=I` 时一致。若读者把正交重建公式直接用于非正交轨道，将得到带有额外 overlap 因子的不同算符；当前正文只说“不能照搬”及“需要冻结对偶基”，却没有给出正确替代式、推导、重建一致性或损失定义。题目 Q8-08 要求修改非正交投影和本征问题，参考解答同样只给出 `P_B` 和广义本征问题，没有完成非正交重建。

该问题判为 `BLOCKING`，因为第 8 章的中心教学目标不仅是广义本征求解，还包括平面波/完整空间到固定 AO 表示的投影、重建和标签误差；缺少重建算符会使学习者无法判断非正交表示中应比较哪个完整空间对象，也无法把投影丢失与矩阵标签语义闭合。现有 T-C08 只验证正交 `B`，不能替代这一条件分支。

**最小修复要求：** 在正文和 D-C07 中，从 `P_B=B S_B^{-1}B†` 推导 `P_B H P_B=B S_B^{-1}H_B S_B^{-1}B†`，声明列满秩、固定内积和稳定求解 `S_B` 的条件，禁止数值实现显式求病态逆；定义或明确继承非正交回投一致性及丢失范数的对象。Q8-08 参考解答应同步补全该公式，并至少给出一个可复核的错误公式失败说明。修复后应由同一独立审计员定点复核本 ID。

## 4. NON_BLOCKING findings

### M5-C8-N01：章级资料包未直接登记正文使用的 Mermin 来源

**位置：** `03_textbook/chapters/08_basis_pseudopotential_errors/sources.md:5-10`；`chapter.md:145-151`；`solution/readme.md:228`。

正文和题解正确区分数值 smearing、物理有限温度、自由能/内部能和熵项，但章级 `sources.md` 的核心来源表没有列出工作包已经冻结的 C-FND-04（Mermin 1965）。中央工作包提供了可追溯来源，因此这不是当前事实错误或来源越权；为使本章资料包可独立自学和逐项追踪，应把 C-FND-04 加入章级来源表，并限定其只支持有限温度理论边界，不把数值 smearing 自动等同于目标物理温度。

### M5-C8-N02：`canonical_qr` 的通用复相位规范公式方向不稳健

**位置：** `03_textbook/chapters/08_basis_pseudopotential_errors/examples.md:189-193`。

代码令 `phases=diag(R)/abs(diag(R))`，随后返回 `Q @ diag(conj(phases))`。若一般 QR 实现返回带任意复相位的 `diag(R)`，要使变换后的 `R` 对角为非负实数，通常应取 `Q_new=Q @ diag(phases)` 和 `R_new=diag(conj(phases)) @ R`。在冻结的 NumPy 2.3.5、两个 seed 和维数下，LAPACK 返回的 `diag(R)` 相位恰为 `+1/-1`，共轭不改变结果；T-C08 的 `H`、投影、丢失范数和等谱反例也对列相位不敏感，故当前全部数值判据仍通过，不构成阻塞。为避免把环境偶然性质写成通用规范算法，建议改用标准方向并增加重构误差及 `diag(R_new)` 非负实数断言。

## 5. 制品级验证

### 5.1 严格 Pandoc 与控制字符

对七个章节材料文件逐一执行：

```text
pandoc <file> \
  --from markdown+tex_math_dollars+tex_math_single_backslash \
  --to html5 --mathml --fail-if-warnings
```

结果为 `7/7` 退出码 0。逐字符检查 C0 控制字符、DEL 和 TAB，七文件均为 0；未发现未闭合代码围栏或 MathML 转换警告。

### 5.2 四个 Python 代码块

`examples.md` 恰含 4 个 `python` 围栏。使用固定解释器 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0，把每个围栏原样解析并作为独立程序执行，结果为 `4/4` 退出码 0。该结果证明现有 T-C05—T-C08 断言可执行，但不补足 B01 未编码的非正交重建分支。

### 5.3 链接与来源入口

七个文件中的 4 个本地相对链接全部解析到现存目标：正文指向推导、例题和练习目录，题集指向阶段 C 工作包。C-NUM-02 和 C-NUM-03 的 DOI 分别解析到 APS 的 Payne et al. 1992 与 Hamann et al. 1979 期刊入口；DH-07/CLM-006 可由本地来源台账定位到同行评议论文、仓库和表示桥接论断。未发现错误相对层级、失效 DOI 标识或把版本待核验对象写成已冻结接口。

## 6. 最终门控判定

本次独立正式内容审计冻结：

- `PASS/FAIL=FAIL`；
- `BLOCKING=1`；
- `NON_BLOCKING=2`；
- 阻塞项为 `M5-C8-B01`；
- 非阻塞项为 `M5-C8-N01`、`M5-C8-N02`；
- **不允许将 M5-05 标记为 `COMPLETED`；**
- **不允许启动 M5-06。**

主 agent 应修复 M5-C8-B01，并可一并处理 N01/N02；随后交由本独立审计员定点复核。只有复核确认原阻塞关闭、新增及剩余 `BLOCKING=0`，才允许完成 M5-05 并启动 M5-06。主 agent 的自检、现有四个 Python 块退出 0 或正交 T-C08 通过均不能替代独立复核结论。
