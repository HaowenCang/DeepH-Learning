# M7-I 阶段 A—E 全量独立总审计报告（首次审计）

- 审计日期：2026-08-11
- 审计角色：D-011 指定的 M3—M7 唯一独立跨阶段总审计员
- 审计轮次：M7-I 首次全量审计
- 当前快照基线：除本报告外 425 个文件
- 基线清单算法：相对路径升序、路径分隔符统一为 `/`、每行写入相对路径与文件 SHA-256，以 UTF-8 和 LF 汇总后再次计算 SHA-256
- 基线清单 SHA-256：`7EF59727DCD3211002071EC2948F54DE421970731F966F798D5BBE7F95917D65`
- 既有 M7 阶段 E 正式总审计报告实测 SHA-256：`82954A441DC888C56E2D0F9CB093FADE2C9D9D5247AFD880D8560A4D20D6BC51`

## 1. 最终结论

**最终判定：FAIL。**

- `BLOCKING=0`
- `NON_BLOCKING=3`
- 真实数学、物理、数值、代码或授权边界回归：0
- 新发现的跨阶段问题：3
- 既有审计已关闭事项重新打开：0
- 新增及剩余问题：3

高风险数学对象、来源血缘、固定环境、57 项自动测试、全部冻结 CLI、schema、provenance、payload、哈希、确定性、失败矩阵和 M8/M9 授权哨兵均通过独立复核。当前失败不是由数学或代码错误造成，而是由六处现行材料的 Raw TeX 渲染丢义、历史审计证据链的格式与控制字符缺陷，以及现行导航/状态叙述未随阶段完成同步更新造成。

D-011 明确要求 `BLOCKING=0`、`NON_BLOCKING=0` 且新增及剩余问题为 0 才能通过。因此本轮不允许进入 M8 决策冻结。BLK-03 必须继续保持 `UNRESOLVED_M8`；不得冻结材料体系、DFT/数据后端、DeepH 软件对象、计算资源、预算或高级物理范围；不得安装 DeepH 或正式 DFT 软件、下载正式数据、生成 DFT 标签或启动复现实验。

## 2. 独立性、范围与只读约束

本轮没有用 M3—M7 既有 `PASS` 代替当前审计。既有报告只用于重建问题关闭链；教材、推导、例题、题解、代码、来源、状态和授权边界均以当前 425 文件快照重新读取、重新解析、重新执行或独立复算。

审计覆盖以下对象：

- M3—M7 的范围、依赖顺序、工作包、阶段门控、正式总审计、定点复核和进度台账；
- 20 个章节目录中的正文、三级提纲、来源说明和 19 个例题文件；
- 阶段 A 解析模型，以及 D-B01—D-B06、D-C01—D-C08、D-D01—D-D07、D-E01—D-E09 的解析推导与总索引；
- 章末练习、参考解答、阶段综合问题、综合解答、自学导航和张量/表示追踪模板；
- 16 个 Python 文件、5 份精确版本 requirements、5 组自动测试、全部冻结 CLI、失败注入矩阵和确定性输出；
- 中央来源 CSV、BibTeX、23 个登记来源快照、各章来源边界和正文使用的来源 ID；
- D-010 材料建设模式、D-011 总门控、BLK-03、M8 决策冻结和 M9 二次执行授权边界。

工作区不是 Git 仓库，因此使用全文件内容清单作为只读边界。报告写入前再次计算同一 425 文件清单，SHA-256 仍为 `7EF59727DCD3211002071EC2948F54DE421970731F966F798D5BBE7F95917D65`。本轮未修改被审文件、代码、状态、既有报告或依赖，唯一新增文件为本报告。

## 3. 材料范围与 D-010 强度核验

M3—M7 当前材料没有因取消学习者本人闭卷作答而缩减知识范围或验收强度。结构复核结果如下：

| 对象 | 当前快照 | 独立判定 |
|---|---:|---|
| 章节目录 | 20 | 第 1—20 章全部存在；M3—M7 所需章节无空目录 |
| 独立例题文件 | 19 | 第 2—20 章均有 `examples.md`；第 1 章例题整合在正文、解析模型和代码练习中 |
| 带“例”标题的例题单元 | 152 | 覆盖概念、解析、数值、失败和接口例 |
| 实质推导文件 | 20 | 阶段 A 1 个；阶段 B/C/D/E 分别 4/5/4/6 个，另有 4 个阶段索引 |
| 练习 Markdown | 57 | 问题、解答和阶段入口齐全 |
| 分项问题 | 243 | 阶段 A 15；阶段 B/C/D/E 分别 46/60/50/72；另有 1 个阶段 A 端到端对象图材料题 |
| B—E 问题/解答 ID | 228/228 | 自动抽取并归一化 Q/A、C/A ID 后零缺失、零额外 |
| 阶段 A 分项题 | 15 | B1—B5、D1—D5、P1—P3、R1—R2 均有解答；P1/P2 共用一个完整解答节 |
| Python 文件 | 16 | 生产代码、CLI 和测试均在范围内 |
| 自动测试 | 57 | 全部实际通过 |

阶段 B 保留广义本征、非正交基、周期 Bloch/Fourier 与能带对象链；阶段 C 保留多电子、HK/Levy/Lieb/KS、SCF、离散与标签 provenance；阶段 D 保留监督学习、普通 MPNN、周期多重图、泄漏与完整张量追踪；阶段 E 保留 $SO(3)$、$O(3)$、实复基、CG、等变 Hamiltonian、局部架、$SU(2)$ 与时间反演。每阶段仍同时具备成立条件、失败样例、自动门控和参考解答。因此现有证据不支持“D-010 降低了知识范围或验收强度”的推断。

## 4. 来源、快照、CSV、BibTeX 与证据边界

中央来源表 `02_source_ledger/source_table.csv` 含 46 行、17 列，`source_id` 为 46 个唯一值。`source_id`、题名、作者、年份、来源类型、官方 URL、访问日期、适用范围、主要论断、局限和证据状态等必填字段缺失数为 0；年份、访问日期和 URL 的格式检查均通过。45 项为 `PRIMARY_EXPLICIT`，1 项为 `SUPPLEMENTAL_ARCHIVE`。

`01_sources/bibliography.bib` 含 46 个唯一 BibTeX 键，Pandoc citeproc 严格载入退出码为 0。阶段 D 和 E 的来源 README 显式给出来源 ID 到 BibTeX 键的映射；所需键全部存在。对 `00_scope/`、`03_textbook/` 和 `04_derivations/` 的规范来源 ID 扫描得到 39 个已使用 ID，全部能在中央 CSV 中解析，未知 ID 为 0。中央表中未被当前教材直接使用的 7 项仍属于文献地图或补充档案，没有被冒充为直接论证证据。

三个来源 README 共登记 23 个本地快照；逐文件 SHA-256 全部与登记值一致。其中 18 个 PDF 均由实际 `pdfinfo` 解析成功、无加密且页数可读，5 个 HTML 快照可严格 UTF-8 读取。对原始 DeepH 论文正文的独立文本抽取确认：论文明确区分由 DFT 或 DeepH 获得的 Hamiltonian、由基函数内积低成本获得的 overlap，以及 Fourier 后求解广义本征问题；教材没有把该原始论文对象分工无条件外推到未冻结的现代软件接口。DLMF、MIT 8.321、Deep Sets、MPNN、TFN/e3nn 和 DeepH-E3 快照亦按各自证据边界使用，没有由架构名称推出数值等变性，也没有由教材目录页替代教材正文的公式证据。

`tmp/` 中的 PDF、页面图像和文本抽取属于非规范派生检查材料，不进入中央来源链。四个重复 PDF 与 `01_sources/` 的正式快照逐字节哈希一致；其中 PDF 文本抽取的 form-feed 等控制字节不计入规范 Markdown 门控。

## 5. 教材、推导和跨阶段数学语义复核

### 5.1 广义本征、非正交基与周期表示

阶段 A/B/C 中的列基、bra/ket、矩阵元和系数方向一致：

\[
\Phi'=\Phi A,\qquad c'=A^{-1}c,\qquad H'=A^\dagger H A,\qquad S'=A^\dagger S A.
\]

Hermitian-definite 结论始终要求 $H=H^\dagger$、$S=S^\dagger\succ0$。Cholesky/对称正交化、$S$-归一化、简并子空间、后向误差和简单本征值一阶微扰的适用条件没有跨阶段漂移。独立构造的复矩阵束给出最大归一化残差 $6.50\times10^{-17}$、$S$-正交残差 $1.41\times10^{-15}$、一般可逆合同变换谱差 $4.44\times10^{-16}$；有限差分与 $c^\dagger(\delta H-E\delta S)c$ 的差为 $1.46\times10^{-11}$。

实空间块采用 $H_{ab}(R)=\langle a0\vert H\vert bR\rangle$，共轭配对为 $H_{ab}(R)^*=H_{ba}(-R)$。正变换 `exp(+ikR)`、逆变换 `exp(-ikR)/N`、cell-phase Bloch 和、轨道中心规范以及 H/S 同步变换在阶段 A、B、C 和 DeepH 接口处一致。独立有限群复算得到正逆误差 $7.40\times10^{-17}$、Hermiticity 残差 $8.78\times10^{-17}$、规范谱差 $8.88\times10^{-16}$；只改单侧相位与删除共轭配对分别产生 $4.13\times10^{-2}$ 和 $7.49\times10^{-2}$ 的定向失败。

### 5.2 DFT、标签语义、监督学习与周期图

Born—Oppenheimer、平均场、HK、Levy、Lieb、KS、SCF 和近视性材料均保留所需问题族、可表示性、函数空间、局部线性化、谱隙/温度/维数和表示依赖条件。标签链明确区分理论近似、离散/采样、数值求解、投影表示和模型误差；带相近不能推出矩阵标签同义。

阶段 C 合成记录只允许 `generation_status=SYNTHETIC_M5`，14 个实践字段保持 `UNRESOLVED_M8`。四个合成制品哈希由声明字节串独立重算并匹配。T-C09 实际执行 67/67 必填路径删除和 47/47 schema 负例，其中类型、shape、hash 和提前 M8 选择分别为 9、11、8、19 项。`validation.audit_status=PENDING_M5_INDEPENDENT_AUDIT` 被解释为记录内主实现不得自证独立通过的冻结值，阶段通过证据位于外部审计链；本轮未把该值误判为正式状态台账。

阶段 D/E 对周期边统一使用完整键 $(i,j,n)$、receiver $i$、sender $j$ 及位移

\[
d_{ij n}=(f_j+n-f_i)A.
\]

逐原子代表变换、边行重排、mask、轨道对和 provenance 同步；普通 MPNN 的节点重编号等变性没有被外推为旋转等变性。独立暴力枚举与生产周期图的 10 个边键完全相同，位移逐元素一致；独立普通消息层的置换残差为 0，规范 edge payload 哈希与冻结值相同。

### 5.3 SO(3)、O(3)、CG、Hamiltonian、局部架和时间反演

主动/被动变换、行晶格旋转、极向量/轴向量、实 $p/d$ 表、DLMF 复球谐、$m$ 递增顺序、点值到 coefficient 的共轭映射、CG 选择定则与整通道相位自由在第 15—20 章、统一约定、推导、代码和题解之间一致。

独立 STF 基和角动量生成元复算给出 Gram 误差 $2.22\times10^{-16}$、$\ell=1$ 表与矩阵指数差 $2.02\times10^{-16}$、$\ell=2$ 表差 $3.57\times10^{-16}$、球谐协变误差不超过 $3.40\times10^{-16}$。CG 表由独立总角动量 $J^2$ 分块对角化、最高权态和降算符构造，不调用项目 CG 公式；与冻结 1×1 和 1×2 表在整通道相位对齐后的最大差分别为 $5.55\times10^{-16}$ 和 $3.33\times10^{-16}$，intertwiner 残差不超过 $3.49\times10^{-16}$。

Hamiltonian 块始终采用两侧表示作用，并与 Hermiticity、逆边、周期 shift、轨道身份和实/复基同步。独立正/逆边复算残差为 $1.46\times10^{-16}$，只左作用故障残差为 $8.64\times10^{-1}$。$O(3)$ 极/轴反演正例残差为 0；归一化局部架的旋转协变误差为 $1.81\times10^{-16}$，有量纲叉积阈值故障在同一边界给出 $1.5\times10^{-8}$ 而规范无量纲量为 $7.5\times10^{-9}$，能穿透方向错误的实现。

自旋顺序、Pauli 基、$SU(2)$ 双覆盖、轨道—自旋 Kronecker、反幺正 $\Theta=JK$、$\Theta^2=JJ^*$、H/S 的 $k/-k$ partner 和 TRIM/Kramers 条件一致。独立 Pauli 旋转误差为 $1.97\times10^{-16}$，$\Theta^2$、Kramers 正交、H/S partner、广义谱配对和 $2\pi/4\pi$ 锚点均在浮点精度内为 0；没有把一般 $k$ 点冒充 TRIM，也没有把磁性破缺样例宣称为时间反演通过。

上述复算没有发现真实数学、索引、单位、dtype、shape、规范身份或阈值回归。

## 6. 固定环境、自动测试、CLI、确定性与失败矩阵

唯一送审解释器为 `C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。实测版本为 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0，`pip check` 输出 `No broken requirements found.`。五份 requirements 内容和 SHA-256 完全相同：`numpy==2.3.5`、`scipy==1.18.0`，文件 SHA-256 为 `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4`。本轮没有执行安装命令。

所有测试均以 `-B` 和禁写 bytecode 环境执行：

| 阶段 | 测试 | 结果 |
|---|---:|---|
| A 广义本征 | 10 | 10/10 |
| A Fourier 参考实现 | 3 | 3/3 |
| B 周期非正交 | 5 | 5/5 |
| C 教学 SCF/标签 | 9 | 9/9 |
| D 周期图/普通 MPNN | 13 | 13/13 |
| E 表示/等变性 | 17 | 17/17 |
| 合计 | 57 | 57/57 |

每个冻结 CLI 均在两个独立真实子进程中运行，返回码均为 0，同一命令的原始 stdout 字节完全相同：

| CLI | stdout 字节 | SHA-256 | 关键结果 |
|---|---:|---|---|
| A 默认 Markdown | 1,036 | `F13BEBB81BBDAC1D625B173FADBF5610DB6AC70C748B9A28FBCFB4847B68566F` | 正例、扰动、条件数和失败样例完整 |
| A 默认 JSON | 3,131 | `49ED744484E9D23E0341FA0F33E9F5BCB45BA980C1E7398643C91AEAA41EC187` | 固定 seed/shape/版本 |
| A size 2 JSON | 3,125 | `CDA2178591F94C94B0432BA05443F1799B9E1A555062A40F8730EF09868AEB39` | 最小合法维数通过 |
| B 配置 1 | 5,851 | `CDFC94EE71D5B1B2217CF7A045C882C3E302BEAAF62DB0F543834D6E1B8E987E` | T-B01—T-B10 全通过 |
| B 配置 2 | 5,847 | `DA0E815E88958B80253FF00E39B553FB7EF81A986623D0FCB2985C9BBFA261B6` | T-B01—T-B10 全通过 |
| C 配置 1 | 90,083 | `B8470284AD0CE79068DA8F75FB30712ABAF9FFE916A6671ED6C079277A0C1376` | T-C01—T-C10 全通过 |
| C 配置 2 | 90,125 | `6893201DE85F5718E9346A482750977A172F36D9F33523479F38667C6E852E3D` | T-C01—T-C10 全通过 |
| D 配置 A | 12,316 | `2F45DC8C53C1E1D968B3F4633CCC8590540AB8E08667A340054F15F9F3CCA6EE` | T-D01—T-D10；36+16 项故障全拒绝 |
| D 配置 B | 12,373 | `88BF70A4218E2B10C8410644B7B899ECF50A6F6993E83E93C496450069693BD6` | T-D01—T-D10；36+16 项故障全拒绝 |
| E 配置 A | 21,247 | `6A656A18BBFEF042CBCD3049278C15FD0644F4B593D06E44A2B63C5FC78BE856` | T-E01—T-E12；63/63 故障全拒绝 |
| E 配置 B | 21,301 | `B9E4CA3DE9E671F4F9B674E40B5F62068F3A91E6BA886D4640D3B90AA6FD82D1` | T-E01—T-E12；63/63 故障全拒绝 |
| E 144 点扫描 | 62,206 | `C13944029E29EF6B47919646952A5D9BDF6A018CEE3F101429FAB09967982A81` | 144/144；最大残差 $1.94687694000716\times10^{-7}$ |

E 扫描的规范 case digest 为 `5317a387bfb026e53dceb31a85074d52ff520448c2fbac9649cb8013064cca7e`，最坏 case 为 `float32-s20260809-r257-m1-a1e+03`，最坏 ℓ 为 2。Stage C 章节例题中的 15 个独立 Python fence 全部退出 0；第 3、4、9 章 PowerShell here-string 内的 Python 例题也全部退出 0；Q6-08 的独立占据数 fence 退出 0。

对 16 个 Python 文件的 AST 和导入扫描只发现标准库、NumPy、SciPy 及项目内模块。没有网络客户端、文件写入、DeepH、e3nn、ASE、pymatgen 或 DFT 软件导入。代码中出现的 `vasp`、`deeph` 等字符串只存在于授权哨兵和必须被拒绝的故障注入中，不是被选中的后端或依赖。

## 7. Markdown、MathML、链接、Raw TeX 与控制字符全域检查

对当前报告写入前的 292 个 Markdown 文件逐一执行：

1. Pandoc 3.6.4，输入格式 `markdown+tex_math_single_backslash`，输出 JSON AST；
2. Pandoc HTML5、`--mathml --fail-if-warnings`；
3. AST 本地链接解析；
4. UTF-8 严格解码、Raw TeX 节点和非法控制字符扫描。

结果为 JSON AST 292/292；HTML/MathML 严格通过 290/292；MathML 节点 11,870；活动本地链接 550 个、断链 0；Markdown UTF-8 失败 0。共发现 244 个 Raw TeX 节点，其中现行规范材料 6 个、历史审计记录 238 个。规范文本域共 315 个 UTF-8 文件，非法控制字符只有 1 个，位于历史审计报告。具体缺陷分别登记为 M7I-N01 和 M7I-N02。

## 8. 阶段审计关闭链、状态台账与授权边界

各阶段最后有效放行证据的当前内容哈希如下：

| 阶段 | 最后有效放行报告 | 当前 SHA-256 | 独立复核结论 |
|---|---|---|---|
| M3 | `M3_stageA_material_blocking_reaudit.md` | `B72215B708D5066413DACF3C136EB5BCABB745A949A717F00406A3A868B0802B` | 原 2 项阻塞关闭，无新增阻塞 |
| M4 | `M4_stageB_final_independent_audit.md` | `534AE8085CF6BCF3B684E59C836B23B0E996E3CF01B3E184DCD62FED623A752B` | `PASS`，问题为 0 |
| M5 | `M5_stageC_final_blocking_reaudit.md` | `424EE8199A68B02C7DA74B7FA1298347AFB193C4658CEAA683365777F24C60AB` | B01/N01/N02 全部关闭，问题为 0 |
| M6 | `M6_stageD_final_independent_audit.md` | `2254A958FFD5A132A68DCE9D4C1C3D79F7663EBB1A3E4C7D0013280E5E291E27` | `PASS`，问题为 0 |
| M7 | `M7_stageE_final_independent_audit.md` | `82954A441DC888C56E2D0F9CB093FADE2C9D9D5247AFD880D8560A4D20D6BC51` | `PASS`，问题为 0，只允许进入 M7-I |

进度台账的阶段总表把 M3—M7 标为 `COMPLETED`、M7-I 标为 `IN_PROGRESS`、M8/M9 标为 `PLANNED`。台账历史行中的缩写哈希前后缀均与上述实测完整哈希一致。已关闭的广义本征、Fourier、SCF Fréchet 余项、周期图、CG 相位、Hamiltonian provenance、扫描 dtype、时间反演 partner 和自学导航问题均经当前独立复算未见回归。

D-010、D-011、`00_scope/unresolved_decisions.md`、主计划阶段表、根 README 顶部状态和代码 sentinel 一致要求：M7-I 通过前不进入 M8；M8 只能由用户集中冻结；M8 完成后，M9 的安装、正式数据下载、DFT 标签生成或复现实验仍需第二次明确授权。`06_reproduction/` 和 `07_research_ideas/` 当前没有文件；未发现代码、导航或状态文件绕过该双授权边界。

## 9. BLOCKING

无。`BLOCKING=0`。

## 10. NON_BLOCKING

### M7I-N01：六处现行规范材料的 Raw TeX 导致 MathML 渲染丢义

**定位。**

- `00_scope/master_execution_plan.md:245`：`H=H^\dagger` 未放入数学定界符；
- `00_scope/master_execution_plan.md:246`：`S\succ0` 未放入数学定界符；
- `03_textbook/chapters/13_message_passing_networks/chapter.md:197`：`((E,P_{\max}))` 未放入数学定界符；
- 同文件 `:240`：`(Y=\tanh Z)` 未放入数学定界符；
- `05_code_exercises/stageD_synthetic_mpnn/README.md:28`：`(2\times10^{-2})` 未放入数学定界符；
- `06_exercises/04-stageD/13_mpnn/solution/readme.md:74`：`(2\times2)` 未放入数学定界符。

**可复现证据。** Pandoc JSON AST 在上述位置产生 6 个 `RawInline` TeX 节点。HTML5/MathML 输出分别退化为 `H=H^`、`((E,P_{}))`、`Y=Z` 和 `(2)` 等文本，`\dagger`、`\succ`、`\max`、`\tanh` 和 `\times` 被丢弃。严格命令返回 0 不能抵消 Raw TeX 节点造成的语义损失。

**技术影响。** 源 Markdown 中的意图仍可由人工辨认，相关数学和代码亦已独立通过，所以不构成数学回归；但 HTML/MathML、自学阅读器和无障碍输出会丢失算符、shape 上界、非线性名称或矩阵尺寸，不能达到跨格式教材的零缺陷门槛。

**最小关闭条件。** 仅为六个表达式补齐合法数学定界符并保持原公式不变；对四个文件重新执行严格 Pandoc/MathML，确认 Raw TeX 为 0，并在 HTML 中检查 `†`、`≻`、`max`、`tanh` 和 `×` 的目标 MathML token。随后由本审计员定点复核。

### M7I-N02：历史审计证据链存在 Raw TeX、严格 Pandoc 失败和控制字符

**定位与数量。** 15 个历史审计 Markdown 共含 238 个 Raw TeX 节点：

| 文件 | Raw TeX |
|---|---:|
| `M7_chapter19_independent_content_audit.md` | 41 |
| `M7_stageE_work_package_second_reaudit.md` | 28 |
| `M7_stageE_work_package_independent_audit.md` | 24 |
| `M4_stageB_work_package_independent_audit.md` | 22 |
| `M6_stageD_work_package_blocking_reaudit.md` | 19 |
| `M2I_chapter1_independent_content_audit.md` | 19 |
| `M7_stageE_work_package_blocking_reaudit.md` | 19 |
| `M7_stageE_self_study_independent_audit.md` | 18 |
| `M4_stageB_work_package_blocking_reaudit.md` | 14 |
| `M4_stageB_self_study_independent_audit.md` | 12 |
| `M4_stageB_code_independent_audit.md` | 6 |
| `M7_stageE_self_study_blocking_reaudit.md` | 5 |
| `M4_chapter3_independent_content_audit.md` | 5 |
| `M5_stageC_final_blocking_reaudit.md` | 3 |
| `M6_stageD_work_package_independent_audit.md` | 3 |

其中两文件在 `--mathml --fail-if-warnings` 下退出码为 3：

- `08_audits/M6_chapter12_blocking_reaudit.md:56` 的 `\deg_{\rm in}` 触发 `\rm` 无法转换；
- `08_audits/M6_chapter12_independent_content_audit.md:46,48` 的 `N_{\rm tot}`、`E_{\rm tot}` 触发同类警告。

另有 `08_audits/M4_stageB_work_package_blocking_reaudit.md` 字节偏移 6,279、行 118 列 15 的 U+0008，将应为 `\bar\Phi` 的公式破坏为控制字符加 `ar\Phi`。

**可复现证据。** 全域 Pandoc 结果为 290/292；规范文本非法控制字符扫描唯一命中上述 U+0008；Raw TeX AST 逐文件计数之和为 238。许多 Raw TeX 命令在 HTML 中被删除而不是转换为 MathML。

**技术影响。** 当前全量复算确认这些表现层缺陷没有改变既有问题的关闭事实，也没有形成数学回归；但历史审计文件是状态台账引用的证据，公式丢义、严格构建失败和不可见控制字符会削弱审计链的可读性与可重放性。M2-I 报告虽早于 M3，仍属于 M3 的直接依赖证据，因此纳入数量。

**最小关闭条件。** 在不静默改写审计历史的前提下，使活动审计证据链对严格 Pandoc/MathML、Raw TeX 和控制字符检查全部为 0。若原位修复历史报告，必须同时登记旧/新 SHA-256 并更新所有状态引用；若采用不可变归档加经审计勘误/规范副本，必须明确原件只作历史字节证据、活动结论指向严格通过的规范证据。无论采用哪一路径，都须由本审计员验证公式语义、关闭链哈希和零缺陷计数。

### M7I-N03：现行导航与状态叙述没有随 M3—M7 完成同步归一

**定位。** 强证据包括：

- `README.md:7` 仍称中央来源只有 22 条，而当前 CSV/Bib 均为 46 条；
- `00_scope/master_execution_plan.md:80,187` 分别仍称“当前进入 M5”和“M6 当前推进”，与同文件 `:57-64` 的 M3—M7 `COMPLETED`、M7-I `IN_PROGRESS` 相冲突；
- `03_textbook/chapters/01_deeph_problem/chapter.md:615` 仍称 M3-08 独立结论待定，但 M3-08 已关闭两项阻塞并完成；
- `05_code_exercises/stageE_synthetic_equivariance/README.md:99,107` 仍把当前包描述为 B01—B05 修订后等待原审计员复核，并称 M7-09 只有未来独立 `PASS` 后才能完成；实际 M7-09 已由 `M7_stageE_code_blocking_reaudit.md` 放行；
- `03_textbook/chapters/20_spin_time_reversal_complex/chapter.md:512` 明称 A/B 尚未执行，但当前 T-E11/T-E12、A/B/scan 均已执行并审计；
- 阶段 E 另有 28 处“执行证据留待 M7-09”或同义未来时态，集中在第 15—20 章来源/正文及 `04_derivations/stageE/15_group_actions_equivariance.md:426-431`、`16_real_spd_representations.md:530-533`、`17_spherical_harmonics_wigner.md:649-655`、`20_spin_time_reversal_complex.md:13`。这些语句原先是合法的分阶段边界，但 M7-09 完成后没有改为静态证据定位。

**可复现证据。** 当前状态台账 `08_audits/progress_tracker.md:28-35` 和根 README 顶部明确 M3—M7 已完成、M7-I 正在进行；M3、M7-09 和 M7 最后放行报告的实测哈希与台账一致。上述现行教材/代码说明却仍使用“当前修订”“仍待”“尚未执行”等现在时或未来时表述。

**技术影响。** 漂移方向是保守的：它不会提前选择 M8 对象或授权 M9，因此不构成授权边界阻塞；但学习者和后续审计无法仅依靠现行导航确定执行证据是否存在，会把已关闭问题误读为当前未关闭状态，也使中央来源数量与真实台账不一致。

**最小关闭条件。** 将现行导航中的动态状态改为与台账一致的完成状态或明确标记为历史阶段说明；把 M7-09 未来时态改为指向当前代码 README、冻结 CLI 和 `M7_stageE_code_blocking_reaudit.md` 的静态证据位置，同时保留“主 agent 自检不替代独立审计”的治理边界；把根 README 的 22 条改为当前 46 条，或明确 22 只是 M1 当时基线；补充 M4、M6、M7 最终放行报告的直接导航。完成后对上述关键词和阶段状态执行交叉扫描，并由本审计员定点复核。

## 11. 既有关闭事项、真实回归与新问题的区分

M3—M7 既有审计中出现过的内容问题均保持关闭。当前独立复算没有重现非正交合同变换、Fréchet 余项阶数、周期代表双射、CG 相位、复球谐 coefficient 映射、Hamiltonian 双侧作用、scan dtype、时间反演 partner、局部架阈值或自学导航对象错位等旧缺陷。因此：

- 既有关闭事项：仍为 `CLOSED`；
- 真实回归：0；
- M7I-N01：以前分项审计未覆盖到的全域现行格式问题；
- M7I-N02：以前存在但未被跨阶段全域严格格式扫描登记的历史证据问题；
- M7I-N03：阶段完成后形成或暴露的跨阶段状态/导航漂移。

三项均为本轮新稳定 ID，不得用既有 `PASS` 抵消。后续修复不得顺带改变已通过的数学、代码、schema、payload、阈值或授权边界。

## 12. 门控与后续动作

本轮结论不允许进入 M8。主 agent 应只修复 M7I-N01—N03，然后将新快照交回同一 M7-I 审计员定点复核。定点复核必须同时验证：三项原问题关闭、相邻对象无回归、全域重新扫描无新增问题、`BLOCKING=0`、`NON_BLOCKING=0`、新增及剩余问题为 0。未满足全部条件时继续保留 `FAIL` 和相同稳定 ID。

即使未来定点复核达到 `PASS`，其许可也只允许进入 M8 候选方案的集中提交与用户冻结，不替用户冻结任何 M8 选择，更不授权 M9 的安装、正式数据下载、DFT 标签生成或复现实验。

## 13. 报告自身终检

本报告写入后单独执行以下终检：

- Pandoc JSON AST：1/1，退出码 0；
- HTML5 `--mathml --fail-if-warnings`：1/1，退出码 0；
- MathML 节点：51；
- Raw TeX 节点：0；
- UTF-8 与非法控制字符：严格 UTF-8 通过，非法控制字符 0；
- AST 本地链接：0，断链 0；
- 必需结构、稳定问题 ID 和计数一致性：13 个编号主节齐全；M7I-N01—N03 各有唯一问题标题；结论、问题清单和门控计数一致；
- 除本报告外 425 文件基线清单 SHA-256：`7EF59727DCD3211002071EC2948F54DE421970731F966F798D5BBE7F95917D65`，与写入前一致；
- 报告最终 SHA-256：在最终写入和全部终检后于外部回报中给出，避免自引用改变文件哈希。
