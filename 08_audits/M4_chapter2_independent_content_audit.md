# M4-02 第 2 章材料独立内容审计

## 1. 审计对象与结论

- 审计日期：2026-08-03
- 审计角色：独立子 agent
- 审计范围：第 2 章 `sources.md`、`outline.md`、`chapter.md`、`examples.md`，D-B01 推导，Q2-01—Q2-08 练习与解答，阶段 B 统一约定，M4 工作包与 FND-06 固定来源快照
- 修改边界：本次审计只新增本报告，未修改任何被审计材料
- 总结论：**不通过；存在 2 项 `BLOCKING`。**

因此，当前证据不允许将 `M4-02` 标记为 `COMPLETED`，也不允许将 `M4-03` 标记为 `READY`。材料的物理主线、代数推导和二能级数值结果基本正确，但公式文本完整性与工作包明示的矩阵形状契约尚未满足。

## 2. 已通过的内容检查

### 2.1 对象层级、相位与定义域边界

正文正确区分了抽象态、算符、给定有序基、系数列向量、矩阵元和广义谱。纯态按非零复比例等价类处理，且明确区分整体相位与分量相对相位；Q2-02 的两个态给出 \(\langle X\rangle=1\) 与 \(0\)，与整体相位不变性没有混淆。

Hermitian 算符的伴随关系同时保留了复共轭、bra/ket 方向和适用态集合；正文没有把有限矩阵的全空间定义域静默外推到连续空间无界算符。有限基部分也区分了同一子空间内的可逆表示变换与删除/增加基函数造成的投影子空间改变，未把基截断误差解释为纯坐标差异。

### 2.2 列基、合同变换与非正交接口

统一采用

\[
\boldsymbol\Phi'=\boldsymbol\Phi A,\qquad
c'=A^{-1}c,\qquad
H'=A^\dagger H A,\qquad
S'=A^\dagger S A.
\]

矩阵元的变换被正确识别为合同变换，而不是线性映射坐标的相似变换。旧基正交、\(A\) 非幺正时，材料正确得到 \(S'=A^\dagger A\ne I\)，并要求求解 \(H'c'=ES'c'\)。期望值、范数与广义谱不变性的逐式推导正确；行列式证明

\[
\det(H'-ES')=|\det A|^2\det(H-ES)
\]

明确依赖 \(A\) 可逆，奇异变换和子空间降维被列为失效边界。

### 2.3 二能级解析与固定 Python 复算

使用工作包固定解释器

`C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

在 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0 下独立复算。结果为：

| 检查 | 复算结果 |
|---|---|
| 原始 \(H\) 谱 | \((-2.23606797749979,\ 2.23606797749979)\) |
| 原始态期望值 | \(0\) |
| 相位翻转后谱/期望值 | 与原始结果相同 / \(0\) |
| 轨道重排后谱/期望值 | 与原始结果相同 / \(0\) |
| 非幺正变换 \(H'\) | \(\begin{pmatrix}1&2.5\\2.5&1.25\end{pmatrix}\) |
| 非幺正变换 \(S'\) | \(\begin{pmatrix}1&0.5\\0.5&1.25\end{pmatrix}\) |
| \(c'^\dagger S'c'\)、\(c'^\dagger H'c'\) | \(0.9999999999999998\)、\(0\) |
| 正确广义谱 | \((-2.23606797749979,\ 2.23606797749979)\) |
| 错误普通谱 | \((-1.3781230493125982,\ 3.6281230493125984)\) |
| Q2-03 Hermiticity 残差 | \(0\) |

数值结果与例题和参考解答的实质算术一致；忽略 \(S'\) 的失败样例具有确定性，能够复现预期的错误谱。

### 2.4 练习、解答与失败诊断

Q2-01—Q2-08 与参考解答按编号一一对应，覆盖对象分类、整体/相对相位、复数 Hermitian 矩阵、列基与系数方向、非幺正 overlap、广义谱行列式证明、子空间改变以及二能级失败复算。每题均给出机制解释或常见错误；解答没有以仅给最终数值替代推导。

### 2.5 来源强度、链接与快照

FND-06 固定快照的页内内容与 `sources.md` 的用途相符：Lecture 6 第 1—4 页直接支持归一化、整体数值尺度、Hermitian/伴随定义；Lecture 8 第 4—5 页支持一般算符期望值；Lecture 9 第 1—4 页支持内积、实期望值、实本征值和正交本征态。正文把“复比例等价类”明确标为教材定义性约定，没有伪装成讲义原文术语。有限矩阵、基变换和二能级计算作为 `DIRECT_DERIVATION` 或 `PEDAGOGICAL` 的证据分层合理。

三个 FND-06 PDF 的实际 SHA-256 与 `01_sources/README.md` 登记值完全一致。对本次范围内 10 个 Markdown 文件检查了 6 个活动本地链接，断链数为 0。

## 3. `BLOCKING` 项

### M4-C2-B01：公式转义损坏，当前文本不满足可自学性和可验证性

**证据。** 第 2 章材料出现可重复的控制字符和丢失 LaTeX 命令：

- `chapter.md:144`、`04_derivations/stageB/02_basis_representation.md:5,22`、练习 `problem/readme.md:7,35` 和解答 `solution/readme.md:5` 中，预期的 `\boldsymbol` 被 U+0008 退格控制字符破坏；
- `problem/readme.md:21` 中，预期的 `\theta` 被 U+0009 制表符破坏；
- `chapter.md:18` 的 `\langle`、多处 `\hat`、`\mathcal` 等行内命令丢失反斜杠；五个核心内容文件没有形成任何成对的 `\(`、`\)` 行内数学定界符；
- `examples.md:104,122` 与 `solution/readme.md:115` 把 \(\pm\sqrt5\) 写成了字面量 `(pm\sqrt5)`。

这些不是单纯排版偏好。U+0008/U+0009 会改变原始字符流；丢失命令使 `hat H`、`mathcal V_M`、`langle...rangle` 和 `pm` 不再具有声明的数学语义，也会使 Markdown/LaTeX 渲染器无法得到预期公式。读者无法仅凭当前呈现可靠地区分普通文字、变量和数学算符，因此材料尚不满足“公式条件完整、可自学、可验证”的门控。

**关闭条件。** 清除审计范围内全部非换行控制字符；将所有行内数学恢复为项目统一的有效定界形式，并恢复 `\boldsymbol`、`\theta`、`\hat`、`\langle`、`\mathcal`、`\pm` 等命令。修复后应执行控制字符扫描、公式定界符检查和一次实际 Markdown/LaTeX 渲染检查；仅靠搜索替换部分已知实例不足以关闭此项。

### M4-C2-B02：正文没有显式给出全部矩阵形状，未达到本章自身完成条件

**证据。** `outline.md` 的完成检查明确要求“正文必须给出所有矩阵形状和复共轭方向”。正文给出了 \(c\in\mathbb C^M\) 和 \(A\in\mathbb C^{M\times M}\)，但首次定义 \(H_{\mu\nu}\)、\(S_{\mu\nu}\) 时没有显式声明 \(H,S\in\mathbb C^{M\times M}\)；谱分解中的 \(V\)、本征矢矩阵及各列的形状也未声明。例题中的二维对象可由排版推断，但不能替代一般 \(M\) 维公式的形状契约。

**风险。** 本章的核心目标正是区分抽象对象和给定基下的矩阵表示。若只允许读者从指标范围推断形状，后续合同变换、系数逆变换和广义本征问题的乘法相容性缺少正文明确检查点，也直接违反已冻结的章节完成条件。

**关闭条件。** 在首次出现处显式声明有序列基、\(c\)、\(H\)、\(S\)、\(A\)、单个本征向量和本征矢矩阵的形状，并在主要变换式旁给出乘法相容性或最小形状检查。不得只在提纲或审计报告中补充。

## 4. `NON_BLOCKING` 项

### M4-C2-N01：章节状态和自学导航仍是未完成时态

`chapter.md:3` 仍称“尚需完成分层练习、参考解答”，`chapter.md:231` 仍称参考解答“将在”对应路径形成，但 Q2-01—Q2-08 及解答已经存在。该陈述不会改变物理内容，但会误导自学者判断材料是否缺页。阻塞项修复时应同步改为当前状态，并把正文 5 道检查题分别映射到 Q2-02、Q2-03、Q2-04、Q2-05、Q2-07 的现有解答位置。

### M4-C2-N02：应把独立数值复算固化为 M4-07 的可重复测试

本次审计已用固定 Python 环境复算全部二能级算术，但当前章节解答只说明自动复算将在 T-B03 中固化。该安排与工作包任务顺序一致，不阻塞 M4-02 内容本身；M4-07 实现时应把本次指标纳入固定测试和 JSON 证据，避免正式阶段审计只依赖终端复算记录。

## 5. 门控判定

| 判定项 | 结果 |
|---|---|
| 对象层级与整体/相对相位 | 通过 |
| Hermitian 与定义域边界 | 通过 |
| 有限投影与子空间边界 | 通过 |
| 列基、系数方向与合同变换 | 通过 |
| 非幺正 overlap | 通过 |
| 期望值与广义谱不变性 | 通过 |
| 行列式证明 | 通过 |
| 二能级解析与固定 Python 复算 | 通过 |
| 8 道练习与解答一一对应 | 通过 |
| 来源强度、快照哈希与本地链接 | 通过 |
| 公式文本完整性与可渲染性 | **不通过：M4-C2-B01** |
| 全部矩阵形状 | **不通过：M4-C2-B02** |

最终判定：`M4-02` 保持 `REVIEW`；`M4-03` 保持 `PLANNED`。仅在 M4-C2-B01、M4-C2-B02 经主 agent 修复并由独立子 agent 定点复核关闭，且无新增 `BLOCKING` 后，才允许 `M4-02 COMPLETED / M4-03 READY`。

## 6. 被审计文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `03_textbook/chapters/02_quantum_states_operators_matrices/sources.md` | `4CCC8273FFC9936B8BEC76F2994E0D443E3CDFCD5C29BB12AEDD210C3396220B` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/outline.md` | `209405686CAB6C6742A1296E78223CD1D2DCDBB9B0BE283323D98660CB704BFD` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/chapter.md` | `B528DD3E576506FE3035CBF6ABEECD86DAFDC971BAB377F615FD229FDED49A09` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/examples.md` | `D92E312DE132CACE1E7F3A2728B3BBCCB3B9350A6F8A68AD97EB19CBDAC65AD0` |
| `04_derivations/stageB/02_basis_representation.md` | `4FEC4285C33A6334F22C79378EA0E37F949077842B4053A19FA0D6DBB306CA28` |
| `06_exercises/02-stageB/02_basis/problem/readme.md` | `37CA4D84C59A483B2E955009620461364C5765BC9D849CB5E975700B9D1B0107` |
| `06_exercises/02-stageB/02_basis/solution/readme.md` | `33FBCB54751334FE1A3D48E7DC6119A532FB9FEF80448BE3B6D139511ED9D28E` |
| `03_textbook/stageB_conventions.md` | `F13A9E5E6FC3FC51D18E6E361B5C0CB84A2FD56FE2431915079CE2693E9F7AAE` |
| `08_audits/M4_stageB_work_package.md` | `3DFE3F0023E77CA340089B9D06940EAD62EFEE4123FC043CFBE0C7AFA7D75462` |
| `08_audits/M4_stageB_work_package_blocking_reaudit.md` | `3AB104D6AFBCDB3BC903A18DD2E8C25CFAD1342985519C9B8C7E54FC71011409` |
| `01_sources/README.md` | `96CDEC62825A7C4A69F8D481AF05D09A58667B3D6EF66BDD52881EC2CD38C93A` |
| `01_sources/documentation/mit_8_04_2016_lecture06.pdf` | `94BDB289652D5AD03F217F451BA144519884F0359414F1E2530E3015A54FA5DD` |
| `01_sources/documentation/mit_8_04_2016_lecture08.pdf` | `211EC0D365577E50D59D325F8285DCBB48A364AC5C85E95D2DF607A720BF54CC` |
| `01_sources/documentation/mit_8_04_2016_lecture09.pdf` | `CDE42766358A0AC3A2E862273522F35B1A4A9652145FE9AB563706AB9CF1C001` |
