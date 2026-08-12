# M4-01 阶段 B 工作包阻塞项定点复核

## 1. 复核范围与结论

- 复核日期：2026-08-03
- 复核角色：独立子 agent
- 原审计：`M4_stageB_work_package_independent_audit.md`
- 定点范围：M4-WP-B01—B03 的修复证据，以及由修复引入的潜在新增阻塞项
- 修改边界：本次复核只新增本报告；未修改工作包、约定表、章节资料包、提纲、来源台账、来源快照或原审计报告
- 总结论：**通过。M4-WP-B01—B03 全部关闭，无新增 `BLOCKING`。**

据此，允许将 `M4-01` 标记为 `COMPLETED`，并将 `M4-02` 标记为 `READY`。本结论只授权进入阶段 B 教材和合成验证材料建设，不授权安装 DeepH、下载正式训练数据、生成正式 DFT 标签，亦不授权选择材料体系、DFT 后端或实践软件版本。

## 2. 复核方法

本次执行了以下独立检查：

1. 使用 Python 标准库 `csv` 解析 `source_table.csv`，核对表头列数、全部行字段数和 FND-06 唯一性；
2. 对三份 MIT 8.04 本地 PDF 重新计算 SHA-256，并与 `01_sources/README.md` 登记值逐项比较；
3. 提取并阅读 Lecture 6 第 1—4 页、Lecture 8 第 4—5 页、Lecture 9 第 1—4 页，同时渲染全部十个相关页面，核对标题、页码、公式和正文内容；临时渲染文件已在检查后删除；
4. 逐式检查 `stageB_conventions.md` 的列基方向、实空间 bra/ket 定义、Hermiticity、离散 Fourier 对、无限晶格测度和轨道中心规范；
5. 检查第 4、9 章提纲及统一记号是否引用同一约定入口；
6. 逐项核对 D-B01—D-B06、T-B01—T-B10、固定环境命令、容差、预期失败断言和 JSON 输出契约；
7. 扫描项目 Markdown 的活动本地链接，共检查 67 个相对链接，排除 LaTeX 反斜杠表达式造成的伪匹配后，断链数为 0；
8. 核对 D-009、D-010 和 M8/M9 授权边界。

M4-01 的对象是工作包、来源、提纲和验证矩阵的冻结，而不是 M4-07 的代码交付；因此本次判断的是所列 Python 命令和测试契约是否足以约束后续实现，不把尚未建设的 `stageb_models.py` 或测试文件误当作本门控的既有产物。

## 3. M4-WP-B01 复核：第 2 章直接来源覆盖

### 3.1 CSV 结构与来源登记

`source_table.csv` 解析结果为：表头 17 列、数据 23 行、字段数异常行 0、FND-06 记录 1 行且具有完整 17 列。逗号、分号和 URL 均保留在正确字段内，没有发生未转义逗号导致的列漂移。

FND-06 固定为 Barton Zwiebach 的 MIT OpenCourseWare 8.04 Spring 2016 讲义，范围明确到 Lecture 6 第 1—4 页、Lecture 8 第 4—5 页、Lecture 9 第 1—4 页。`scope`、`primary_claims`、`limitations` 与 `evidence_status` 字段相互一致：它只支持入门量子力学中的归一化、整体非零复尺度等价、线性/厄米算符、内积、期望值、实本征值和正交本征态，不声称覆盖严格无界算符定义域或抽象射线空间理论。

### 3.2 PDF 哈希与页码内容

三份本地快照的实际哈希与登记值完全一致：

| 快照 | 实际 SHA-256 | 结果 |
|---|---|---|
| `mit_8_04_2016_lecture06.pdf` | `94BDB289652D5AD03F217F451BA144519884F0359414F1E2530E3015A54FA5DD` | 匹配 |
| `mit_8_04_2016_lecture08.pdf` | `211EC0D365577E50D59D325F8285DCBB48A364AC5C85E95D2DF607A720BF54CC` | 匹配 |
| `mit_8_04_2016_lecture09.pdf` | `CDE42766358A0AC3A2E862273522F35B1A4A9652145FE9AB563706AB9CF1C001` | 匹配 |

页内证据核对结果如下：

- Lecture 6 第 1—2 页给出归一化、可归一化波函数及整体数值因子不承载额外物理信息；第 3—4 页给出 Hermitian 算符、伴随以及实谱/正交本征态的入门表述；
- Lecture 8 第 4—5 页给出位置、动量及一般算符的期望值定义；
- Lecture 9 第 1—4 页给出内积、Hermiticity、期望值为实数、实本征值、不同本征值对应态正交以及完备展开的教学表述。

第 2 章资料包已把“复比例等价类”明确降为教材的定义性约定，把严格无界算符定义域限制为接口，不再伪装成 FND-06 的直接原文；矩阵元、有限基展开和一致基变换被标记为 `DIRECT_DERIVATION`。证据强度与来源范围现已匹配。

**判定：M4-WP-B01 关闭。**

## 4. M4-WP-B02 复核：阶段 B 统一表示与 Fourier 约定

### 4.1 列基与一般基变换

约定表采用列基 (Phi'=Phi A)。由 (Phi c=Phi'c') 得到 (c'=A^{-1}c)，矩阵元则满足

\[
H'=A^\dagger H A,\qquad S'=A^\dagger S A.
\]

当旧基正交而 (A) 非幺正时，约定表明确给出 \(S'=A^\dagger A\ne I\)，并要求求解广义本征问题。原审计 N01 已合理落实。

### 4.2 实空间定义、Hermiticity 与 Fourier 对

bra/ket 方向已冻结为

\[
H_{ab}(\mathbf R)=\langle\phi_{a\mathbf0}|\hat H|\phi_{b\mathbf R}\rangle,
\qquad
S_{ab}(\mathbf R)=\langle\phi_{a\mathbf0}|\phi_{b\mathbf R}\rangle.
\]

在平移不变和 \(hat H=hat H^\dagger\) 条件下，其复共轭正确给出

\[
H_{ab}(\mathbf R)^*=H_{ba}(-\mathbf R),
\qquad H(\mathbf R)^\dagger=H(-\mathbf R),
\]

且 (S) 的对应关系完全同步。指标交换、复共轭和晶格平移反号均未遗漏。

有限 Born—von Karman 对偶网格采用

\[
\frac1N\sum_{\mathbf k}e^{i\mathbf k\cdot(\mathbf R-\mathbf R')}
=\delta_{\mathbf R,\mathbf R'},
\]

cell-phase Bloch 和使用正号相位。由冻结的实空间定义得到

\[
H(\mathbf k)=\sum_{\mathbf R}e^{+i\mathbf k\cdot\mathbf R}H(\mathbf R),
\qquad
H(\mathbf R)=\frac1N\sum_{\mathbf k}e^{-i\mathbf k\cdot\mathbf R}H(\mathbf k),
\]

(S) 使用同一正反变换。该组公式与离散正交关系闭合，并由实空间共轭配对推出每个 (mathbf k) 上的 Hermiticity。约定表还独立声明 \(S(\mathbf k)\succ0\) 是定广义本征问题的附加要求，而不是仅由实空间 Hermiticity 自动推出。

无限极限的平均测度写为

\[
\frac1N\sum_{\mathbf k}f(\mathbf k)
\longrightarrow
\frac1{V_{\mathrm{BZ}}}\int_{\mathrm{BZ}}f(\mathbf k)d^d\mathbf k
=\frac{\Omega_c}{(2\pi)^d}\int_{\mathrm{BZ}}f(\mathbf k)d^d\mathbf k,
\]

并明确要求与有限离散恒等式区分，方向和归一化正确。

### 4.3 轨道中心规范

替代 Bloch 基满足 \(\bar\Phi_{\mathbf k}=\Phi_{\mathbf k}U(\mathbf k)\)，其中

\[
U_{ab}(\mathbf k)=\delta_{ab}e^{+i\mathbf k\cdot\boldsymbol\tau_a}.
\]

因此同步变换

\[
\bar H=U^\dagger H U,
\quad
\bar S=U^\dagger S U,
\quad
\bar c=U^{-1}c
\]

与列基方向一致，并保持广义谱。负号 Bloch 相位只允许整体同步反号，未留下局部更换相位的歧义。

第 4、9 章提纲均在正文前引用 `../../stageB_conventions.md` 作为唯一入口；`notation.md` 和 M4 工作包也引用同一文件。未发现另立相冲突约定。原审计 N03 所要求的截断、有限采样和相位错配分离已在约定表第 6 节落实。

**判定：M4-WP-B02 关闭。**

## 5. M4-WP-B03 复核：可执行建设与验证矩阵

### 5.1 产物与环境契约

工作包已冻结四章正文、四份推导、各章例题、四组练习与参考解答、代码入口、测试文件、依赖文件和自学导航的路径。Python 环境固定为 3.12.13，NumPy 固定为 2.3.5，SciPy 固定为 1.18.0；命令始终使用同一个绝对 `$py`，并依次执行解释器检查、依赖安装、包版本检查、单元测试和 JSON CLI。该命令契约符合 D-009，且没有使用会漂移到系统 Python 的裸 `python`。

### 5.2 推导矩阵

D-B01—D-B06 完整覆盖主计划六项必要推导，并为每项给出正文/推导路径、例题/练习路径、解析验收条件和失败边界：

- D-B01 明示列基、系数、矩阵方向及非幺正 overlap；
- D-B02—D-B03 覆盖投影/Rayleigh 推导、正定条件、Cholesky、对称正交化、变量逆映射和近线性相关；
- D-B04 要求以行列式或等价论证证明一般可逆基变换下的广义谱不变；
- D-B05 从冻结 bra/ket 定义推导实空间指标交换；
- D-B06 覆盖离散正交、(1/N)、(S) 同步变换和轨道中心规范。

该矩阵已具备后续正文和推导审查所需的可定位入口。

### 5.3 数值测试、失败断言与 JSON 证据

T-B01—T-B10 覆盖：广义残差、(S)-正交、一般基变换谱不变、条件数扫描、Fourier 正反变换、(k) 空间 Hermiticity、双轨道能带、轨道中心规范、截断/采样分离以及重排/相位/子空间幺正混合。每项均给出合成输入类别、代码入口或共享入口、应保持性质、数值容差和预期失败断言。

失败样例不是仅打印异常：工作包要求指定异常类型/消息或给出严格残差下界，并规定只有每个预期失败均按指定方式被捕获时退出码才为 0。JSON CLI 还必须报告运行时版本、随机种子、矩阵维数、(N_k)、各项指标、容差、失败捕获状态和 `conventions_version="stageB-v1"`。这些字段足以让后续实现和独立材料审计比较命令输出与冻结契约。

矩阵当前是建设规格而非已通过的数值结果；实际代码、测试通过记录和保存的 JSON 证据仍属于 M4-07/M4-09 的后续门控，不能由本次 M4-01 复核提前判定完成。

**判定：M4-WP-B03 关闭。**

## 6. 原审计 `NON_BLOCKING` 项落实情况

| 原项 | 复核结果 |
|---|---|
| M4-WP-N01：非幺正变换后的 overlap | 已在 `stageB_conventions.md` 和 D-B01 中明确 \(S'=A^\dagger A\ne I\) 及广义本征要求 |
| M4-WP-N02：来源 ID 逐项展开 | 第 9 章资料包已分别列出 FND-02、FND-03、FND-04 的用途和限制 |
| M4-WP-N03：区分截断、采样和混叠/相位错配 | 约定表第 6 节和 T-B09 已分别定义并设置验收 |

三项均已合理落实。

## 7. 新增 `NON_BLOCKING` 建议

### M4-WP-RN01：在 M4-07 实现时固定病态阈值

T-B04 已固定条件数族，并要求 (10^8) 档标记 `ill_conditioned`，足以作为当前建设门槛。实际实现时仍应把“最小特征值低于固定阈值”的阈值写成具名常量并输出到 JSON，避免诊断规则只存在于代码分支中。

### M4-WP-RN02：构造保证失败下界的确定性反例

T-B03、T-B08 已给出失败下界。实现时应选择固定种子且远离幺正的 (A)，以及与 \(U(\mathbf k)\) 不对易的非单位 \(S(\mathbf k)\)，以保证“只变一部分对象”的谱差下界不是依赖随机巧合。该事项属于实现细化，不影响当前验证矩阵覆盖。

### M4-WP-RN03：保存 JSON 标准输出

工作包已经冻结 JSON schema 与退出码语义。M4-07 完成时宜把 CLI 标准输出保存到 `08_audits/` 下的稳定证据文件，并记录该文件哈希；否则终端输出虽可验证，但不利于 M4-09 复核历史运行。

## 8. 最终门控判定

| 项目 | 判定 |
|---|---|
| M4-WP-B01 | **关闭** |
| M4-WP-B02 | **关闭** |
| M4-WP-B03 | **关闭** |
| 新增 `BLOCKING` | 无 |
| 活动本地 Markdown 链接 | 67 个已检查，0 断链 |
| M8/M9 授权边界 | 未越界 |

最终结论：**M4-01 可标记为 `COMPLETED`，M4-02 可标记为 `READY`。** RN01—RN03 应在 M4-07/M4-09 前落实或登记，但不阻塞 M4-02 的正文建设。

## 9. 输入文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `08_audits/M4_stageB_work_package_independent_audit.md` | `6D2FF43BBC3A9E36218D9820E8E4F59EB0F7A2DAE98918EC66667F95D1965A3D` |
| `08_audits/M4_stageB_work_package.md` | `01552C8A9803F5A43E39EB43EF19050FF06B100F156C3121B34C08BE81989782` |
| `03_textbook/stageB_conventions.md` | `F13A9E5E6FC3FC51D18E6E361B5C0CB84A2FD56FE2431915079CE2693E9F7AAE` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/sources.md` | `4CCC8273FFC9936B8BEC76F2994E0D443E3CDFCD5C29BB12AEDD210C3396220B` |
| `03_textbook/chapters/02_quantum_states_operators_matrices/outline.md` | `209405686CAB6C6742A1296E78223CD1D2DCDBB9B0BE283323D98660CB704BFD` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/sources.md` | `6F14E670EEF5CF0DE62D2E49AD8E38D08B7B1E66034452F4A38B932FB6964610` |
| `03_textbook/chapters/03_nonorthogonal_generalized_eigen/outline.md` | `96A926FD0F28DD70E5969A24F75057FAFEAF8E0B574CB2E97BE2DBF259DE04BE` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/sources.md` | `E23937AAB9BBAA5A745802D879E7F300C60C8AC46009F150E246008BF79B40CE` |
| `03_textbook/chapters/04_periodicity_bloch_reciprocal/outline.md` | `6F749FA916FE9E43AF0669C0479F98835653F88B1026F58753EE57571A04A956` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/sources.md` | `D15B8422838C9A74BE86C44E680F839476A63239AFAB926A8C8001365953F5D6` |
| `03_textbook/chapters/09_realspace_hamiltonian_bands/outline.md` | `D9048F63FBDDA81EED653E50C7380351BD9F13D2B42DDBA564AACA12290188B7` |
| `03_textbook/notation.md` | `576B5222C54206DBD1D48043E2719C6888FDE35EBBC207FA8BE5070B0CD80398` |
| `02_source_ledger/source_table.csv` | `8B856358B8A8A2D0A98E9274FF7F2C777855A2E478964620C89E2041AE09243C` |
| `01_sources/README.md` | `96CDEC62825A7C4A69F8D481AF05D09A58667B3D6EF66BDD52881EC2CD38C93A` |
| `01_sources/bibliography.bib` | `ADEF14B8AB8FC7264491B5F0A7FDF0E77C85B375F7568BE23EBCD05CDCE49BBD` |
| `01_sources/documentation/mit_8_04_2016_lecture06.pdf` | `94BDB289652D5AD03F217F451BA144519884F0359414F1E2530E3015A54FA5DD` |
| `01_sources/documentation/mit_8_04_2016_lecture08.pdf` | `211EC0D365577E50D59D325F8285DCBB48A364AC5C85E95D2DF607A720BF54CC` |
| `01_sources/documentation/mit_8_04_2016_lecture09.pdf` | `CDE42766358A0AC3A2E862273522F35B1A4A9652145FE9AB563706AB9CF1C001` |
| `00_scope/master_execution_plan.md` | `0227B27EFA9A2C0DC887E14190745483C0FAAEC193D515DAB8445C6D6EE3F4F6` |
| `00_scope/learning_route.md` | `352C853017F6E84F26B59023E5432D611BC18F48E6ED7E0E853AF809A531BACA` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |
