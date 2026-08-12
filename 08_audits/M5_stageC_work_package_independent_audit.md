# M5-01 阶段 C 工作包正式独立审计

## 1. 审计结论

**总判定：BLOCKING。** 当前快照有 4 项 `BLOCKING` 和 2 项非阻塞记录。五章范围、依赖顺序、主体物理边界、D-010 及 M8/M9 授权边界总体正确；但是 constrained-search 的来源归属、T-C 测试契约、标签语义最低 schema 和固定复现命令尚未达到“可直接实施并可独立判定”的工作包冻结标准。

因此：

- **不允许**将 M5-01 标记为 `COMPLETED`；
- **不允许**将 M5-02 标记为 `READY`；
- 主 agent 完成修订后，应由独立子 agent 对 M5-WP-B01—B04 执行定点复核。

本审计只新增本报告，没有修改工作包、教材资料包、提纲、计划、决策或进度台账。

## 2. 审计对象与依据

核心对象为：

- `08_audits/M5_stageC_work_package.md`；
- 第 5、6、7、8、10 章的 `sources.md` 与 `outline.md`，共 10 份 Markdown；
- `00_scope/master_execution_plan.md`、`00_scope/learning_route.md`、`decisions.md`、`08_audits/progress_tracker.md`、`00_scope/unresolved_decisions.md`；
- `08_audits/M4_stageB_final_independent_audit.md`。

M4 最终审计的当前 SHA-256 为 `534AE8085CF6BCF3B684E59C836B23B0E996E3CF01B3E184DCD62FED623A752B`，与其既有冻结记录一致。该审计明确允许 M5 在理论、教材、后端无关推导、合成数据和 Python 用户态实现范围内启动，同时维持 BLK-03、M8 集中决策和 M9 外部动作前再次授权的边界。

## 3. BLOCKING

### M5-WP-B01：constrained-search 被错误归入“直接推导”，且正式来源未闭合

`03_textbook/chapters/06_kohn_sham_dft/sources.md:15` 将 constrained-search 接口与正交约束变分、基离散一起标为 `DIRECT_DERIVATION`；`M5_stageC_work_package.md:72` 又把它列为 D-C03 的核心对象。Levy constrained-search 是对普适泛函定义域和可表示性问题的独立形式化，不应被写成由 1964 年 HK 原始定理自然逐式推出的普通教材代数。当前来源表没有列出 Levy/Lieb 原始来源，也没有把 Martin 教材中实际明确陈述 constrained search 的节页定位为二手显式来源。

这会直接影响 D-C03 中纯态/系综、`N`-representability、`v`-representability 与简并边界的写法，属于来源归属和公式适用域的阻塞项。应当采取以下任一可审计修复：

- 增加 Levy constrained-search 与必要的 Lieb 变分框架来源，分别限定其所支持的定义域、下确界/极小值和凸性边界；或
- 若只采用教材层次表述，应定位 Martin 正文的确切节页并标为教材显式陈述，不再标作 `DIRECT_DERIVATION`；同时严格限制所用密度域，不把 HK 原始论文外推为完整 constrained-search 形式。

独立抽查确认，HK 1964 的官方摘要支持“外势下相互作用电子基态、普适密度泛函和基态能量变分最小值”，但该证据本身不足以承担当前所写的完整 constrained-search 接口。

### M5-WP-B02：T-C01—T-C10 尚未形成可执行、可独立判定的定量测试契约

`M5_stageC_work_package.md:81` 要求每项测试输出真实指标、容差和预期失败；但 `:87-94` 中多项正例仍使用“最终一致性通过”“达到冻结阈值”“谱与残差闭合”“显式记录”“可复算”等未冻结口径。T-C03、T-C05—T-C08、T-C10 没有定义实际标量、范数、归一化、参考对象和数值上界；T-C04 没有定义复现一致性的比较对象。T-C02 虽给出固定点残差上界，但密度归一容差未定义。

若无这些信息，同一实现可以通过选择不同范数、参考网格或后处理口径改变结论，独立审计无法从 JSON 指标机械复判。预期失败也尚未全部操作化：例如“能量差误判”“误差不得合并归因”“只比较能带而声称矩阵等同”“不得外推到全部体系”目前是语义要求，不是带数值下界和强制断言的失败样例。

修订后的 T-C 契约至少应冻结：

- 每项正例的模型参数、指标公式、范数/归一化、参考解和数值上界；
- 迭代数、分辨率或采样序列，以及“收敛”所需的连续层级或独立轴检查；
- 每项负例的故障注入、预期异常或下界，确保测试在未捕获故障时非零退出；
- T-C01 收敛率估计所用区间与零残差边界；T-C03 的“能量变化小而密度残差仍大”的双阈值；T-C08 固定表示下的矩阵差和投影丢失范数；T-C10 跨衰减族外推失败的定量残差。

`10^{-10}` 的线性固定点误差和 `10^{-9}` 的教学 SCF 残差对双精度合成模型原则上合理，但只有在上述指标定义及模型尺度冻结后才能判定容差是否实际合理。

### M5-WP-B03：标签语义最低模板缺少关键血缘/表示字段，T-C09 也未覆盖现有全部必填项

`M5_stageC_work_package.md:100` 已覆盖理论层级、交换相关、全电子/赝势、基或网格、自旋、采样、温度、阈值、输出对象、单位、轨道排序/相位和投影映射，主体分层方向正确。但是最低模板没有明确要求登记：

- 生成后端/软件对象、版本或提交，以及输入/输出原始制品的身份与校验信息；
- 晶格与结构身份、原子/轨道索引映射、实空间胞位移方向和 Fourier 相位约定；
- 赝势/PAW 数据集或全电子设置的可唯一识别信息，而不只是类别名称；
- 投影窗口、子空间维数和重建所需的定量质量指标。

这些字段可以且应当在 M5 保持 `UNRESOLVED_M8`，要求字段存在并不构成软件、后端、赝势或材料选择。相反，若模板省略这些字段，不同后端版本、轨道/胞位移约定或投影窗口产生的矩阵可能被错误登记为同一标签语义。

同时，T-C09 的正例只枚举“理论、赝势/全电子、基、自旋、采样、温度、阈值、表示”字段，没有明确验证 `:100` 已列出的结构、电子数/占据、输出单位与排序/相位、投影映射和验证记录。应当让 T-C09 对最低模板的完整必填字段集合逐项验证，并对每个必填字段至少执行一次删除后失败的参数化负例。

### M5-WP-B04：固定 Python 版本与产物路径一致，但没有冻结当前工作区的复现命令契约

`M5_stageC_work_package.md:57-64` 固定了产物路径及 Python 3.12.13、NumPy 2.3.5、SciPy 1.18.0，与 M4 最终审计一致；但没有给出已知解释器的绝对路径，也没有冻结安装、版本断言、单元测试和 JSON CLI 的具体命令。相比之下，已通过的 M4 工作包明确给出了同一解释器和完整 PowerShell 命令契约。

M5-08 尚未实施并不妨碍现在冻结入口。工作包应至少加入：固定 `$py` 绝对路径；`requirements.txt` 精确安装命令；Python/NumPy/SciPy 版本断言；`unittest discover` 命令；默认和第二配置的 `run_experiments.py --format json` 命令及固定种子/模型规模。其他机器替换 `$py` 时仍应要求同一 Python 小版本和同一精确依赖。缺少这一契约时，“固定依赖/命令一致”尚不可复核。

## 4. 非阻塞项

### M5-WP-N01：中央来源台账尚未登记新增阶段 C 基础来源

C-FND-02—04、C-NUM-01—03、C-LOC-01 在五章资料包和工作包中已有完整书目信息与明确用途，但 `02_source_ledger/source_table.csv` 和 `01_sources/bibliography.bib` 尚未登记这些新增来源。工作包本身足以定位 DOI，因此不单独构成当前概念阻塞；为保持 M1 建立的统一来源血缘，应在正文大规模写作前补入中央台账，并避免 C-FND-01 与既有 FND-01 的别名造成歧义。

### M5-WP-N02：主计划里程碑状态和进度记录哈希存在快照漂移

`00_scope/master_execution_plan.md:58-59` 仍显示 M4=`IN_PROGRESS`、M5=`PLANNED`，而 M4 最终独立审计和 `progress_tracker.md:13-30` 已明确 M4 完成、M5 进行中。另据 `progress_tracker.md:171`，M5 工作包登记的旧快照为 `4E15F490...06D2AB`，本次当前文件哈希为 `EFAF8EDC...3F6BA1C`。这些差异不改变 M4 已通过和 M5 可以接受审计的事实，但应在主修复时同步状态，并以复核时的新完整哈希替换缩略旧记录。

## 5. 逐维度结论

| 审计维度 | 判定 | 结论 |
|---|---|---|
| 五章范围与依赖 | PASS | 第 5→6→7 章主链、第 8 章表示/赝势/采样接口和第 10 章局域性接口覆盖阶段 C；与阶段 B 的广义本征、周期 Fourier 和实空间块依赖一致。 |
| 多电子、BO、Hartree/HF/KS 对象边界 | PASS | 提纲区分多体波函数、密度、一体密度矩阵、Slater determinant、Hartree/HF 与 KS 接口，明确 BO/非绝热边界和“平均场不等于消除关联”。 |
| HK/KS/Mermin | BLOCKING | HK、KS、有限温度与 smearing 的主体边界正确；constrained-search 的来源归属和形式域未闭合，见 B01。 |
| SCF 固定点与数值算法 | BLOCKING | 依赖图、局部 Jacobian 谱半径、混合/振荡/最大迭代边界正确；测试指标尚不能独立复判，见 B02。 |
| 平面波/局域基、赝势、采样 | PASS | 明确平面波正交的条件、局域非正交 overlap、全电子/赝势、cutoff/网格/采样分离；没有把 norm-conserving 来源外推为 PAW/ultrasoft 质量证明。 |
| 投影/重建与标签语义 | BLOCKING | DH-07 被限定为表示桥接而非预测网络，也未宣称 M8 前已有可用转换器；最低 schema 仍缺少后端/制品血缘和完整表示约定，见 B03。 |
| 近视性、局域性与稀疏性 | PASS | 正确区分局部量对远处势的近视性、密度矩阵衰减和选定局域基中的 H/S 稀疏性；明确金属、温度、维数、长程相互作用、谱隙和基变换边界。 |
| D-C01—D-C08 | BLOCKING | D-C01—02、04—08 的条件和失败边界足以指导后续推导；D-C03 受 B01 阻塞。 |
| T-C01—T-C10 | BLOCKING | 模型族覆盖合理、后端无关；多项容差、指标和负例未冻结，见 B02。 |
| 标签语义最低模板 | BLOCKING | 已覆盖主要理论/数值/表示层级，但不能唯一追溯后端版本、制品和实空间/投影约定，见 B03。 |
| 固定路径、依赖与命令 | BLOCKING | 路径及版本与 M4 一致；复现命令契约缺失，见 B04。 |
| D-010、M8/M9 与 BLK-03 | PASS | 未发现安装 DeepH、真实 DFT 后端、正式训练数据、正式标签、材料体系、泛函、赝势族或实践软件版本的隐含选择。列举 LDA/GGA/meta/hybrid 与 PAW/ultrasoft 仅是分类接口。 |
| 可自学性设计 | PASS（工作包层面） | 五章能力、推导、例题/练习、代码、失败样例和自学导航路径已经规划；M5-01 只审工作包，最终材料完备性仍须由 M5-10 总审计判定。 |

## 6. 来源用途与证据边界抽查

独立抽查得到以下结论：

- C-FND-02 的官方记录支持外势下相互作用电子基态的普适密度泛函和变分最小值；不支持现成精确泛函或 KS 轨道算法。工作包的禁止外推正确。
- C-FND-03 适合支持非相互作用参考体系、KS 自洽方程和交换相关分解；工作包明确拒绝把全部 KS 本征值普遍解释为多体激发能，边界正确。
- C-FND-04 的官方摘要明确是固定温度和化学势下的巨正则有限温度扩展；把数值 smearing 与目标物理温度区分是必要边界。
- C-NUM-01 的公开摘要明确讨论 SCF 迭代的不稳定、低效、缓解方法和算法评估框架；没有支持“某一种混合器普遍最优”，工作包限制正确。
- C-NUM-02 适合支持平面波赝势总能方法与历史迭代数值背景，但不能代表任一现代后端默认实现；限制正确。
- C-NUM-03 的官方摘要支持 norm-conserving 条件、对数导数及 transferability 语境；工作包没有把它推广到 ultrasoft/PAW 或具体元素数据集质量。
- C-LOC-01 将近视性定义为固定化学势下局部电子性质对远处外势变化的有限响应；它不直接证明任意矩阵元素、所有金属或所有温度下统一指数衰减。第 10 章边界正确。
- DH-01/DH-07 的用途与既有来源台账和 M4 最终独立审计一致：前者限定原始 DeepH 的 Hamiltonian 标签/SCF 替代边界，后者只作为 PW→选定 AO 表示的投影/重建原则；二者均没有被用于冻结现代软件接口。

## 7. 11 份 Markdown 静态、链接、渲染与哈希检查

检查对象为工作包及五章各自的 `sources.md`、`outline.md`，共 11 份。结果：

```text
files=11
external_markdown_links=9
local_links=0
broken_local_links=0
control_files=0
pandoc_exit_0=11/11
mathml_nodes=27
```

Pandoc 实际命令口径为：

```powershell
pandoc --from=markdown+tex_math_single_backslash+tex_math_double_backslash `
  --to=html5 --mathml --fail-if-warnings <file>
```

11/11 文件退出码为 0；对生成 HTML 实际统计 `<math>` 节点共 27 个。未使用“Pandoc 退出码为 0”替代 MathML 节点检查。控制字符检查覆盖 C0（保留制表、换行和回车）及 DEL。当前 11 文件没有本地相对链接；9 个外部 Markdown 链接对应 7 个唯一 DOI，核心出版方记录已抽查。

当前审计快照 SHA-256 如下；不包含本报告自身：

| 文件 | SHA-256 |
|---|---|
| `08_audits/M5_stageC_work_package.md` | `EFAF8EDC7156FC26DA73DB871E7937EDD020D5ACBC9AC5F8EF5F0D9443F6BA1C` |
| `03_textbook/chapters/05_many_electron_mean_field/sources.md` | `424441E52FE001985C9CB250913BF639625F44A98893951E20AB89923020C214` |
| `03_textbook/chapters/05_many_electron_mean_field/outline.md` | `0032025037BDCD0D1C0DC34A8692F24E588CC425A1BB732338325C5C9A38E54E` |
| `03_textbook/chapters/06_kohn_sham_dft/sources.md` | `F5E8C18E32DACD18D4EC8DB3B1914EB5F32D5B0E47C6B6A22052F9A0E68EC923` |
| `03_textbook/chapters/06_kohn_sham_dft/outline.md` | `15AA9962E90A540DCDCCF1160F8C03865ABAB11D42CF87BC6165C369B80317D3` |
| `03_textbook/chapters/07_scf_algorithms/sources.md` | `EB715A32D31A81B8442298CFB0C5F92FE0CE1CC8FDBC24DCC1A62221D96646AE` |
| `03_textbook/chapters/07_scf_algorithms/outline.md` | `D188BBEDCD8B58B0B8BD9F9526E786264E44B999F9B0B93D81B292DA36C5CC8F` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/sources.md` | `33CE39E26D73551FF693A9E32FCC8E3B1026A3713C3B30E617843C33B8233EF4` |
| `03_textbook/chapters/08_basis_pseudopotential_errors/outline.md` | `F27DC48EB308F00558EAE8F5E4CFCC9C4376D580A1A2A928E1AB1CD291B29208` |
| `03_textbook/chapters/10_nearsightedness_locality_sparsity/sources.md` | `01F26A7C5F024DF61B36D55C05A03C01E22B4BF9A2EF74043CD8FF060E5A2093` |
| `03_textbook/chapters/10_nearsightedness_locality_sparsity/outline.md` | `61EC21F214DD5285A7BA0F366CE1D3513008C93816E8A5DC647687E1722C9431` |

## 8. 最终许可

- M5-01：**不得标记 `COMPLETED`**。
- M5-02：**不得标记 `READY`**。
- 复核最低条件：M5-WP-B01—B04 全部提供可定位修订证据；11 文件重新冻结哈希；独立定点复核判定 `BLOCKING=0`。
