# M4-01 阶段 B 工作包独立审计

## 1. 审计对象与结论

- 审计日期：2026-08-03
- 审计角色：独立子 agent
- 审计范围：`M4_stageB_work_package.md`，第 2、3、4、9 章的 `sources.md` 与 `outline.md`，以及主执行计划、学习路线、统一记号、来源台账和决策记录
- 修改边界：本次审计只新增本报告，未修改任何被审计文件
- 总结论：**不通过；存在 3 项 `BLOCKING`。**

因此，当前证据不允许将 `M4-01` 标记为 `COMPLETED`，也不允许将 `M4-02` 标记为 `READY`。范围和章节依赖已经形成，但“来源覆盖冻结、Fourier 约定闭合、验证矩阵可执行”三个 M4-01 退出条件尚未同时满足。

## 2. 审计判据

本次审计按以下问题逐项核查：

1. 第 2、3、4、9 章是否覆盖阶段 B 的全部知识与验证范围；
2. 章节依赖是否按“对象与表示 → 非正交广义本征 → 周期/Bloch/Fourier → 实空间矩阵与能带”推进，且不存在循环依赖；
3. 基变换、广义厄米本征问题、正交化、Fourier 正反变换和实空间厄米关系的方向与成立条件是否准确；
4. 来源是否能直接支持被标记为 `PRIMARY_EXPLICIT` 的内容，直接推导和教学模型是否保持证据边界；
5. 教材、推导、例题、练习与解答、代码、自动测试和失败样例是否已形成可以逐项执行和验收的建设矩阵；
6. 是否触及 D-010 规定的 M8/M9 禁令。

## 3. 已通过的检查

### 3.1 范围与依赖顺序

四章共同覆盖主计划阶段 B 的六项必要推导和六类代码验证：第 2 章建立态、算符、矩阵与一致基变换；第 3 章建立 Gram 矩阵、(S)-度量、广义本征、正交化和病态边界；第 4 章建立周期性、Bloch 和、Fourier 对及厄米关系；第 9 章把这些对象组合为实空间矩阵块到能带的完整链条。依赖方向为第 2 章 → 第 3/4 章 → 第 9 章，不存在循环依赖。

### 3.2 基变换与广义本征条件

在列基约定 (Phi'=Phi A) 下，提纲给出的

\[
c'=A^{-1}c,\qquad H'=A^\dagger H A,\qquad S'=A^\dagger S A
\]

方向一致；第 3 章同时要求 (A) 为可逆基变换，并把谱、态范数和期望值不变性放在一致变换下讨论。广义本征问题明确限定于

\[
H=H^\dagger,\qquad S=S^\dagger\succ0,
\]

且把非正定、非厄米、维数不匹配和近线性相关列为失败边界。\(S=LL^\dagger\) 的 Cholesky 方向以及 (S^{-1/2}HS^{-1/2}) 的对称正交化对象未发现代数错误；具体变元替换仍需在正文推导中给出。

### 3.3 实空间厄米关系

第 4 章给出的

\[
H_{i\mu,j\nu}(\mathbf R)^*=H_{j\nu,i\mu}(-\mathbf R)
\]

包含原子/轨道指标交换和晶格平移反号。若后续明确采用

\[
H_{i\mu,j\nu}(\mathbf R)
=\langle\phi_{i\mu\mathbf 0}|\hat H|\phi_{j\nu\mathbf R}\rangle,
\]

该关系等价于 \(H(\mathbf R)^\dagger=H(-\mathbf R)\)，并可推出 \(H(\mathbf k)=H(\mathbf k)^\dagger\)。当前关系本身正确，但其定义前提尚未正式冻结，见 B-02。

### 3.4 授权边界

工作包只允许解析模型、随机厄米/正定矩阵和合成周期模型，并明确禁止安装 DeepH、下载正式训练数据、生成正式 DFT 标签以及选择材料体系、DFT 后端或实践软件版本。这与 D-009、D-010 以及主执行计划的 M8/M9 双重授权点一致，未发现越界安排。

## 4. `BLOCKING` 项

### M4-WP-B01：第 2 章的直接来源覆盖尚未闭合

**证据。** 第 2 章提纲要求覆盖“态矢量、射线与归一化”“线性算符及其定义域”“矩阵元、期望值”等量子力学基础内容；其资料包第 13 行又把这些标准定义统一标记为 `PRIMARY_EXPLICIT`。然而当前列出的 FND-02 明确“不替代量子力学公理来源”，FND-03 是广义厄米本征问题资料，FND-01 的已登记范围是周期固体、电子能带和局域轨道语境。现有资料包没有给出能够直接定位“射线、算符定义域、期望值”等全部所列内容的量子力学来源与页码，也没有逐项说明哪些内容实际由 FND-01 的固定页码直接陈述。

**风险。** 在此状态下，`PRIMARY_EXPLICIT` 标记的证据强度高于已登记来源能够独立复核的强度；M4-01 的“来源覆盖冻结”条件未满足。

**关闭条件。** 二者择一并保持可核验：

- 增加固定版本、章节和页码的权威量子力学来源，并把第 2 章各项标准定义映射到具体来源范围；或
- 收缩第 2 章的来源声明，只把现有固定页码确实直接支持的内容标记为 `PRIMARY_EXPLICIT`，其余内容明确标记为定义性约定或 `DIRECT_DERIVATION`，同时说明证据边界。

### M4-WP-B02：Fourier 约定尚未形成可审计的闭合公式组

**证据。** 第 4 章提纲给出了正号 Bloch 和，并在不同条目中提到有限 (N) 正变换、逆变换、(1/N) 归一化、轨道中心规范和实空间厄米关系；学习路线给出了示例正变换 \(H(\mathbf k)=\sum_{\mathbf R}e^{i\mathbf k\cdot\mathbf R}H(\mathbf R)\)。但工作包与四章提纲都没有在同一处冻结以下完整定义：\(H_{i\mu,j\nu}(\mathbf R)\) 的 bra/ket 方向、允许的离散 (mathbf R/mathbf k) 集合、正变换、逆变换、离散正交关系、(S) 的同一变换，以及“含轨道中心相位”约定与当前约定之间的显式 (k)-依赖规范矩阵方向。

**风险。** 仅凭分散的标题可以推测一套自洽约定，但不能排除后续把 \(H(\mathbf R)=\langle0|H|\mathbf R\rangle\) 与相反定义混用，或把正负相位、(1/N) 位置和轨道中心规范不同步。因而当前无法独立判定“Fourier 正反变换、归一化和相位闭合”这一 M4-01 明示审计问题已经通过。

**关闭条件。** 在工作包或单独的阶段 B 约定表中冻结至少以下闭合公式，并让第 4、9 章提纲引用同一入口：

\[
H_{ab}(\mathbf R)=\langle\phi_{a\mathbf 0}|\hat H|\phi_{b\mathbf R}\rangle,
\quad
H(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}H(\mathbf R),
\quad
H(\mathbf R)=\frac1N\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\]

并对 (S) 给出完全相同的 Fourier 对，声明有限 Born–von Karman 网格的正交关系、无限极限的测度，以及替代轨道中心约定的规范变换。若选择相反相位，应整体同步改变，不能局部替换。

### M4-WP-B03：验证矩阵尚不足以执行和验收

**证据。** 工作包第 11—18 行给出了章级“必须覆盖/必须验证”，第 25—31 行给出了后续任务和概括性退出条件；四章提纲也列出了例题、练习和测试主题。但现有文件没有把每一项必需成果映射到计划产物路径、输入构造、待检性质、自动测试名称或命令、数值容差、预期失败方式和验收证据。尤其是“残差、(S)-正交、谱不变性、条件数扫描、Fourier 逆变换、相位同步、截断误差、缺共轭块/忽略 (S)/相位错配”目前只是主题清单，尚不能据此判定未来实现是否少测、误测或把预期失败误当作测试通过。

**风险。** M4-01 的任务名称明确要求冻结“验证矩阵”。如果没有逐项可执行的建设矩阵，M4-02—M4-08 的交付边界会在实施过程中漂移，最终也无法仅凭固定命令和证据定位审计覆盖。

**关闭条件。** 增加逐项矩阵，至少包含：章节/能力、正文或推导路径、例题路径、练习与参考解答路径、代码入口、测试 ID 与命令、合成输入、应保持的不变量、通过容差、预期失败输入与失败断言、证据输出。矩阵必须覆盖主计划六项推导、六类代码验证和四章各自的失败样例；路径可以是计划路径，但命名与验收字段必须在 M4-01 冻结。

## 5. `NON_BLOCKING` 项

### M4-WP-N01：在第 2 章显式写出非幺正变换后的 overlap

第 2 章已经把非幺正变换列为第 3 章接口。为避免读者误以为一般可逆 (A) 下仍可只求解 (H'c'=Ec')，正文应当在首次出现非幺正 (A) 时写出：若旧基正交，则新基的 \(S'=A^\dagger A\)，必须进入 (H'c'=ES'c')。这属于强化说明，不改变当前基变换公式的正确性。

### M4-WP-N02：来源 ID 应逐项展开

第 9 章资料包使用 `FND-02—04` 作为合并标识。正式章节的论断映射宜分别列出 FND-02、FND-03、FND-04，避免审计时无法判断某一公式依赖的是广义问题定义、复厄米表述还是正交化约化。

### M4-WP-N03：区分截断、有限采样和混叠

第 4、9 章已计划讨论截断、采样不足、混叠和 Gibbs/振铃现象。正文与数值矩阵应分别控制实空间截断范围和 (k) 网格采样，避免把由窗函数卷积产生的振铃与离散采样混叠合并成一个误差来源。

## 6. 门控判定

| 判定项 | 结果 |
|---|---|
| 阶段 B 知识范围 | 通过 |
| 章节依赖顺序 | 通过 |
| (H/S) 条件与基变换方向 | 通过 |
| 实空间指标交换 | 条件通过；定义方向需由 B-02 冻结 |
| Fourier 正反变换与规范闭合 | **不通过：B-02** |
| 来源覆盖与证据边界 | **不通过：B-01** |
| 可执行建设/验证矩阵 | **不通过：B-03** |
| M8/M9 授权边界 | 通过 |

最终判定：`M4-01` 保持 `IN_PROGRESS`；`M4-02` 保持 `PLANNED`。B-01—B-03 修复后，应由独立子 agent 进行定点复核；仅在三项均关闭且没有新增 `BLOCKING` 时，才允许 `M4-01 COMPLETED / M4-02 READY`。

## 7. 被审计文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `08_audits/M4_stageB_work_package.md` | `861C7F626B53CB3F3CC47D17AE916C13D53665E936105AF572668CAAE1668161` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/sources.md` | `36DC992EF899F84F7E1FB282A59E500C819C52698A4F416C45CA10F4FC70F110` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/outline.md` | `8EA43D6ABA5845E9C543FA737ADEFD9AA34BCABBFD4C07060C4B06875A67410A` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/sources.md` | `6F14E670EEF5CF0DE62D2E49AD8E38D08B7B1E66034452F4A38B932FB6964610` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/outline.md` | `96A926FD0F28DD70E5969A24F75057FAFEAF8E0B574CB2E97BE2DBF259DE04BE` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/sources.md` | `E23937AAB9BBAA5A745802D879E7F300C60C8AC46009F150E246008BF79B40CE` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/outline.md` | `C628677B627B16547677D88D774E9C33F28CD54E2D7B5532442A43385B6384A7` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/sources.md` | `FD34E5EE386E7FCD9B6CBABCA826D778DEABD702FE27D8BFC9E886401EF1C0D5` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/outline.md` | `9F6B535D969393CCE8A392B8D6BA3AF9A5F30D9C38E7E6C6AAC9A3A201410183` |
| `00_scope/master_execution_plan.md` | `0227B27EFA9A2C0DC887E14190745483C0FAAEC193D515DAB8445C6D6EE3F4F6` |
| `00_scope/learning_route.md` | `352C853017F6E84F26B59023E5432D611BC18F48E6ED7E0E853AF809A531BACA` |
| `03_textbook/notation.md` | `90FF3A130600FB68CB71FCA781B29A8D5B600D3C26219D369EA50B324426160E` |
| `02_source_ledger/source_table.csv` | `7A405B996CDD8CE4A8196BDA0EA72661F6E13687EA576819EEF72F96E3469AEA` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |
