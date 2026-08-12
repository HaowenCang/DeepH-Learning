# M3-08 阶段 A 材料完备性、可自学性与可验证性独立审计报告

## 1. 最终结论

**结论：有条件通过。存在 2 项 `BLOCKING`，当前不允许把 M3 或 M3-08 标记为 `COMPLETED`，也不允许把 M4 置为 `READY`。**

第 1 章正文、自学导航、两轨道解析模型、5+5+3+2 道分类型练习、端到端综合材料题、参考解答、广义本征代码、Fourier 参考实现、13 项自动测试和失败样例已经形成完整材料链。固定环境中的 10 项广义本征测试与 3 项 Fourier 测试全部通过；默认 Markdown、默认 JSON 和 `size=2` JSON CLI 均成功；全项目活动 Markdown 本地链接检查无断链。M3—M7 的学习者闭卷、口头说明和逐阶段自测已从当前门控中取消，原综合题的一票否决规则、公式成立条件、知识范围和来源边界仍被保留。

尚不能无条件通过的原因不是正文或数学错误，而是两项门控契约仍未满足：

1. `00_scope/learning_route.md` 的阶段 C 编程练习仍要求在 M8 前选取“任一熟悉的 DFT 后端”执行真实收敛研究，与 D-010 明确禁止在 M8 前隐含选择 DFT 后端的约束冲突；
2. 代码 README 与自学导航把环境声明为 Python 3.12.13，但复现命令使用未绑定解释器的裸 `python`。当前工作区中裸 `python` 实际解析到 Python 3.14.5、NumPy 2.4.6、SciPy 1.17.1，按 README 原样运行 10 项广义本征测试时有 1 项因固定版本断言失败。固定的 Codex Python 3.12.13 路径能通过全部测试，但这一必要环境选择没有进入面向自学者的复现命令。

两项问题均可局部修复，不要求缩减或重写阶段 A 教学内容。因此判定为“有条件通过”，而不是“不通过”。主 agent 修复后，应由独立子 agent 按第 10 节标准执行定点复核。

## 2. 独立性、权限与范围声明

本审计由未参与 D-010 模式变更实施的独立子 agent 执行。审计者没有修改计划、路线、台账、教材、推导、练习、参考解答、代码、测试、来源文件或既有审计结论；项目内容写入仅限新增本报告。

审计范围包括：

- D-010 在 `master_execution_plan.md`、`learning_route.md`、`progress_tracker.md`、`stage_gate_template.md`、`M3_stageA_gate_packet.md`、`decisions.md`、`unresolved_decisions.md` 和根 `README.md` 中的语义一致性；
- 历史闭卷模板是否被明确停用，而不是继续构成隐含阻塞；
- 第 1 章正文、自学导航、提纲、来源包和既有 M3-07 独立审计证据；
- 两轨道非正交解析模型；
- 广义本征代码、固定依赖、测试、CLI 和失败样例；
- 5 个 problem/solution 单元、Fourier 参考实现和综合对象图材料题；
- M8 前外部实践禁令、M8 决策暂停和 M9 正式外部动作前再次授权。

数值核验只使用现有 Python 用户态依赖和合成输入；没有安装 DeepH、没有下载正式训练数据、没有生成正式 DFT 标签，也没有选择材料体系、DFT 后端或实践软件版本。

## 3. 输入文件 SHA-256

下表在测试和内容检查前固定；测试后对受执行影响的源码再次计算，哈希保持一致。路径均相对于项目根目录。

| 文件 | SHA-256 |
|---|---|
| `00_scope/learning_route.md` | `C435AFE356AB3507AA5C40294A758DB16C923406C5409D104213A0D85A73B3D1` |
| `00_scope/master_execution_plan.md` | `16C578891696E1FE1C58F4DA2D5D90D04F2D5AC0C07BB55D9AAA5FAB243F149E` |
| `00_scope/unresolved_decisions.md` | `8A76495A18D18B2D097CB6E8043C6DDFA2388D1A161873F0A235FB366F2A6310` |
| `README.md` | `A49925B0EE2479D92B5D483378488355E2924C24DD0A143819D7D61DCF30AE25` |
| `decisions.md` | `072992EFCA9474B738CB48E7C18F85342FDDC4ABA7D25F62EB572552E429455C` |
| `03_textbook/chapters/01_deeph_problem/chapter.md` | `7818EAE68376B437AA28E1159BA64F7B1EB4BB725DA1E917295A4699C9A0B1D5` |
| `03_textbook/chapters/01_deeph_problem/outline.md` | `2FBD23E301FD0A67A7EF0C0AFE2226AA59AD38D1397458313028A34F16FBBB23` |
| `03_textbook/chapters/01_deeph_problem/self_study_guide.md` | `43436227A01F2F2F32F1F5308729DE0410C40D60FEE6574159E64FC106F229A2` |
| `03_textbook/chapters/01_deeph_problem/sources.md` | `ED18BF3CA57F4B19F1101FBA3936EE1E04EA8ADFA4F08D6E7ED98D4FFAEA5E62` |
| `04_derivations/chapter1_two_orbital_nonorthogonal_model.md` | `4FC6FF9A8ED922763E554063BBCB0C10C50467B98342064C3ED6F3CDD3708F8B` |
| `05_code_exercises/chapter1_generalized_eigen/README.md` | `3C69FE018C8CB3784C94EA4DDE3EE5BFDDAA7418856210E90581FEB8E6F6904A` |
| `05_code_exercises/chapter1_generalized_eigen/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/chapter1_generalized_eigen/experiment.py` | `F27F1D32B88034CBFE543A07E27108AF80E4D86FA9FC7B927BEB60AA53AD363F` |
| `05_code_exercises/chapter1_generalized_eigen/test_experiment.py` | `F31DCB4642B5E7FAAB2A3A836E04427C183133657D4A7A0210F9078A53D5F701` |
| `06_exercises/01-deeph-problem/README.md` | `A5191F25CB071DA09BA8BE807C55939155162EA176ED0279AE7B2A5ACB2175A4` |
| `06_exercises/01-deeph-problem/01.01-object-and-workflow-basics/problem/readme.md` | `2021169AEE3CFF683C0001FB1DB66705DE4EA93394E7CEDE0A716485B3930822` |
| `06_exercises/01-deeph-problem/01.01-object-and-workflow-basics/solution/readme.md` | `58A65E9350357430565150CDF4F2D319E5C33B9D9512375B71B70208750121FC` |
| `06_exercises/01-deeph-problem/01.02-core-derivations/problem/readme.md` | `5B6AB1F0937ABD1FD63B949E3700D4836DC4BEBE7949F6E92EA23FD3F56DC035` |
| `06_exercises/01-deeph-problem/01.02-core-derivations/solution/readme.md` | `BB89A65F361806D8CF6FF893A49A4010DE6B7DDA0746A8E991356EF97F9BA698` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/problem/readme.md` | `C3C9A486D45ED0CFD588258683A615A983422A57B7525DDAA8289A9DD02762D7` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/readme.md` | `9BBAFD0941A62DE03F8C63002F70C4AFE2C4B04ECB8C794EA857B2649865F3FE` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/fourier_reference.py` | `06FDD05E8FE194D2BECA7E4DE668A2814F4AD71AF22DA4304ECC77AA35DE25E1` |
| `06_exercises/01-deeph-problem/01.03-numerical-programming/solution/test_fourier_reference.py` | `4DAD587EEA243658A048EF746EE666B4113A6F3175BB2BD9B3DF6483FB47FC30` |
| `06_exercises/01-deeph-problem/01.04-research-comparison/problem/readme.md` | `9E83489C61E7D1D0B77E0717ADF34DE72FC65FA338E24239093A582C68A0770D` |
| `06_exercises/01-deeph-problem/01.04-research-comparison/solution/readme.md` | `FFF397982781B45CCFF7214B926C7761C3EC2559D57D8E5BF2899ED77FC458F0` |
| `06_exercises/01-deeph-problem/01.05-end-to-end-object-graph-gate/problem/readme.md` | `A80C90C41C19E7BB080005FDE8815CC60B476B0582BAE900DE81A080ABFC7DF6` |
| `06_exercises/01-deeph-problem/01.05-end-to-end-object-graph-gate/solution/readme.md` | `54364C36930329F09318726207B5AB1434B7F2D9179F52E3EA20E265C41882DE` |
| `08_audits/M3_stageA_independent_audit.md` | `2075D0B8716784BF85DB82FCA1F678D150BAF2CB4B60DD5BC18E462C86FCEDA9` |
| `08_audits/M3_stageA_blocking_reaudit.md` | `372C32786B1ACE92C233E7FBFF27F846C03ECD3A6DF59DB4D434ED4FFDC4EE4C` |
| `08_audits/M3_stageA_gate_packet.md` | `A65C69D84BE7A29D7A88BCCCA1EB40E87D928988AF2AFA085378EAEB6E5D19EA` |
| `08_audits/M3_stageA_gate_evidence/first_attempt_template.md` | `C9655BFCC0D56AC16722E76588A1844CA1E65FC0BE27D6C9F2B73A43A32CCECF` |
| `08_audits/progress_tracker.md` | `C2FF4D0803415D98A166C8D6CA3018044160281CE7416A6567BB855FC0CFAD6C` |
| `08_audits/stage_gate_template.md` | `D2591764CECCEF66EA14B2A71F06D92A9221610A6B5C059FD23A24B35852A98F` |

## 4. 实际环境、命令与输出

### 4.1 固定环境路径

通过现有 Codex Python 解释器执行门控验证：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

包版本与 `requirements.txt`、代码 README 和自学导航中的目标版本一致。

### 4.2 10 项广义本征测试

执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s 05_code_exercises/chapter1_generalized_eigen -p "test_*.py" -v
```

结果为 `Ran 10 tests in 0.012s`、`OK`，退出码 0。测试覆盖：求解残差与 (S)-正交；一致基变换；等 Frobenius 范数、不同目标影响；一阶余项二阶缩放；指定条件数构造；非正定 (S) 与只变换 (H)；非厄米 (H) 拒绝；最小支持/不支持维数；固定复数两轨道闭式根与非法 overlap；完整结果模式和阈值。

### 4.3 3 项 Fourier 测试

执行：

```powershell
& $py -m unittest discover -s 06_exercises/01-deeph-problem/01.03-numerical-programming/solution -p "test_*.py" -v
```

结果为 `Ran 3 tests in 0.001s`、`OK`，退出码 0。三个测试分别覆盖正确 Hermiticity 与反变换重建、缺少共轭平移块后的 Hermiticity 失败、正反相位未同步后的重建失败。

### 4.4 默认 Markdown CLI

执行：

```powershell
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py
```

退出码为 0。核心输出：

| 指标 | 结果 |
|---|---:|
| 最大归一化广义本征残差 | `2.052642e-16` |
| (S)-正交 Frobenius 残差 | `1.930810e-15` |
| `kappa_2(S)` | `1.000000e+01` |
| 一致基变换最大谱差 | `1.110223e-16` |
| 两个扰动的 Frobenius 范数 | 均为 `2.000000e-02` |
| 目标低能方向的目标位移 | `8.889209e-03` |
| 高能正交方向的目标位移 | `-1.110223e-16` |
| 一阶余项，步长连续减半 | `6.788903e-08`、`1.697828e-08`、`4.245323e-09` |
| 只变换 (H) 的谱差 | `2.067246e+00` |
| 非正定 (S) | 被拒绝 |

### 4.5 默认 JSON 与 `size=2` JSON CLI

执行：

```powershell
$json = & $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --format json
$json | ConvertFrom-Json
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --size 2 --format json
```

两条 CLI 均退出码 0，JSON 均可解析。默认 JSON 顶层字段为 `baseline,basis_change,condition_scan,error_propagation,failure_samples,first_order_check,metadata`，元数据为 seed `20260803`、size `6`、NumPy `2.3.5`、SciPy `1.18.0`。

`size=2` JSON 的关键结果为：最大归一化残差 `9.83072588619945e-17`，(S)-正交残差 `8.11257302121669e-16`，基变换谱差 `1.11022302462516e-16`，非正定 (S) 被拒绝。最小维数路径完整运行。

### 4.6 README 裸 `python` 命令反例

当前 PowerShell 中：

```text
Get-Command python -> E:\Laptop\softwares\python\python.exe
Python 3.14.5
NumPy 2.4.6
SciPy 1.17.1
```

按代码 README 和自学导航原样执行：

```powershell
python -m unittest discover -s 05_code_exercises/chapter1_generalized_eigen -p "test_*.py" -v
```

结果为 `Ran 10 tests in 0.019s`、`FAILED (failures=1)`，退出码 1。失败定位到 `test_experiment.py:186`：实际 NumPy `2.4.6` 与断言要求 `2.3.5` 不同。Fourier 的 3 项测试在该环境仍通过，但不能抵消广义本征 README 命令失败。该反例不否定代码在固定环境中的正确性；它证明面向自学者的命令没有把声明环境与实际调用的解释器绑定起来。

## 5. 链接、题量与结构检查

### 5.1 Markdown 链接

以 UTF-8 读取全项目除 `tmp/` 外的 44 个既有 Markdown 文件，解析相对本地 Markdown 链接，排除外部 URL、页内锚点以及 2 个由 LaTeX `[...]\(\mathbf r\)` 结构触发的正则假阳性。结果：真实本地链接 54 个，断链 0。该检查包含台账所称的 24 个活动材料文件，且扫描范围更宽。

### 5.2 题量与 problem/solution 映射

按题目标题和参考答案标题检查：

| 类型 | 题目 ID | 数量 | 参考答案 |
|---|---|---:|---|
| 基础 | B1—B5 | 5 | 全部对应 |
| 推导 | D1—D5 | 5 | 全部对应 |
| 编程 | P1—P3 | 3 | 全部对应；P1/P2 共用可执行入口 |
| 研究讨论 | R1—R2 | 2 | 全部对应 |
| 综合材料题 | 端到端对象图 | 1 | 训练链、推理链、方法定位、逐箭头表和判定规则齐全 |

综合题继续采用关键错误一票否决；取消学习者提交不等于删除对象图、误差链、方法定位或错误量规。

### 5.3 自学导航结构

`self_study_guide.md` 提供 8 步建议顺序、7 行能力—材料—验证映射、三类自学检查题的答案位置、固定环境与 6 条复现命令、6 类失败现象的诊断入口，以及阶段 A 与正式复现的边界。未发现没有正文、练习/答案或验证入口的孤立阶段 A 核心能力。

## 6. 六域逐项判定

| 审计域 | 判定 | 证据与边界 |
|---|---|---|
| 3.1 知识范围与对象图 | **通过** | `chapter.md:15-223, 261-343, 503-562, 568-599` 与综合题 problem/solution 完整区分算符、参考矩阵、预测矩阵、(S)、本征量和进一步物理量；训练链、推理链、SCF 替代边界和逐箭头误差链齐全；HPRO、DeepH-dock、DeePTB、DeepH-R 的位置和证据边界明确 |
| 3.2 公式、推导与例题 | **通过** | `chapter.md:117-201, 355-412, 441-467` 与解析模型声明 `H=H†`、`S=S†≻0`、`S`-归一化、可逆一致基变换、Fourier 配对、旋转约定和简单/小扰动条件；解析模型包含闭式谱、复共轭、本征矢、条件数、基变换、等范数方向反例和失效边界；M3-07 全域审计及定点复核无剩余公式阻塞 |
| 3.3 练习与参考解答 | **通过** | 5+5+3+2+1 结构准确，problem/solution 一一对应；答案包含机制、条件、失败边界和验证入口；综合解答没有把版本相关 (S)、HPRO 或 DeepH-dock 角色外推为统一方法属性 |
| 3.4 代码、自动测试与失败样例 | **有条件通过，存在 B-02** | 固定解释器下 10+3 项测试、默认/JSON/size=2 CLI 和失败样例全部通过；NumPy/SciPy 固定版本与实现正确。但 README 与导航的裸 `python` 命令未绑定声明的 Python 3.12.13 环境，当前机器按原样执行会产生 1 项版本断言失败，因而“README 命令可复现”尚未成立 |
| 3.5 可自学性与失败诊断 | **通过** | 前置知识、8 步学习顺序、每步产物/检查、7 行能力映射、答案位置、复现命令和失败诊断均可定位；不依赖 DeepH 本体、正式训练数据、正式 DFT 标签或已冻结实践对象。环境启动命令缺口已单列为 B-02 |
| 3.6 模式与授权边界 | **未通过，存在 B-01** | 当前 M3 门控、模板、台账、决策和历史模板均明确取消本人作答阻塞，且未缩减 M3 内容；M8/M9 两次外部授权点总体清楚。但 `learning_route.md:98` 仍在 M5/M8 前要求选择一个实际 DFT 后端做收敛练习，与 D-010 的禁止隐含选择后端条款冲突 |

## 7. `BLOCKING` 列表

### B-01：阶段 C 的实际 DFT 后端练习与 M8 前禁止隐含选择后端冲突

**位置。** `00_scope/learning_route.md:86, 98-102`；对照 `00_scope/master_execution_plan.md:161, 203-216`、`decisions.md:84-93`、`00_scope/unresolved_decisions.md:14-18`。

**机制。** 阶段 C 对应 M5，位于 M8 之前。`learning_route.md:98` 不仅要求教学级一维自洽模型，还另行要求“对任一熟悉的 DFT 后端完成基组或截断能、(k) 点的最小收敛研究”。执行这一条必须实际选择某个 DFT 后端，并通常还隐含软件版本、输入语义和材料/结构。这与 D-010 的“M8 前不得隐含选择 DFT 后端和实践软件版本”直接冲突。该段最后一句只说明“不要求立即生成 DeepH 数据”，没有解除实际后端选择。

**影响。** 若按学习路线原文自主推进 M5，主 agent 可能在尚未到 M8 决策暂停前选取、安装或运行实际 DFT 后端，破坏用户规定的外部授权边界。由于 M3-08 通过标准明确要求 D-010 在全部管理文件中无冲突，该问题不能带入 M4。

**最小修复验收标准。** 在不缩减“SCF、基组/离散、(k) 点或等价采样、收敛误差”知识与验证强度的前提下，把 M5 的必做代码材料限定为后端无关的教学级/合成自洽模型和教学收敛实验；明确实际 DFT 后端、真实材料结构、后端专用输入和正式标签均留到 M8 冻结及 M9 再授权之后。若保留真实 DFT 教程，应明确标为 M8/M9 后的实践扩展而不是 M5 完成门槛。修订后应复核 `learning_route.md`、主计划、未决事项和 D-010 的语义一致性。

### B-02：复现命令没有绑定声明的 Python 3.12.13 环境

**位置。** `05_code_exercises/chapter1_generalized_eigen/README.md:15-25, 27-42`；`03_textbook/chapters/01_deeph_problem/self_study_guide.md:48-61`；`05_code_exercises/chapter1_generalized_eigen/requirements.txt:1-2`；`test_experiment.py:184-187`。

**机制。** README 与导航声明固定 Python 3.12.13、NumPy 2.3.5 和 SciPy 1.18.0，包版本也由 `requirements.txt` 固定；但安装、测试和 CLI 均调用裸 `python`，没有提供解释器选择、环境建立/激活或版本预检命令。当前工作区裸 `python` 指向 Python 3.14.5，且包版本不同，导致 README 原样测试命令实际失败。固定 Codex Python 路径全部通过，说明缺口位于复现说明而不是算法实现。

**影响。** 自学者不能仅凭当前 README 从项目根目录确定哪一个解释器满足材料所声明的固定环境；测试结果会依赖 PATH 的外部状态。门控要求“Python、NumPy、SciPy 版本和安装声明固定”“README 命令可复现”和从零复现说明，因此隐藏解释器前置条件不能作为通过证据。

**最小修复验收标准。** README 与自学导航应给出同一套明确的 Python 3.12.13 解释器选择或环境创建/激活方法、版本预检、固定依赖安装和后续命令；所有测试与 CLI 必须使用该同一解释器，而不是依赖未说明的 PATH。采用当前 Codex 捆绑解释器、项目级虚拟环境或其他可重复方法均可，但应明确适用范围。独立复核应从文档指定环境执行版本检查、10+3 项测试、默认/JSON/size=2 CLI，并证明命令退出码均为 0、元数据为 NumPy 2.3.5/SciPy 1.18.0。

## 8. `NON_BLOCKING` 列表

| 编号 | 位置 | 建议 | 边界 |
|---|---|---|---|
| NB-01 | `00_scope/learning_route.md:5`、`00_scope/unresolved_decisions.md:14-18` | 在语义修复 B-01 时增加 D-010 的显式编号交叉引用 | 两文件当前分别包含材料模式和 M8/M9 停点的实质内容，缺少编号本身不构成逻辑冲突；显式引用可降低后续漂移风险 |
| NB-02 | `README.md:7` | 把“也尚未安装软件”收窄为“尚未安装 DeepH/正式 DFT 实践软件” | 当前上下文可推断指实践软件，但项目已按 D-009 安装 SciPy；收窄表述可避免与已安装 Python 依赖产生字面歧义 |
| NB-03 | `03_textbook/chapters/01_deeph_problem/sources.md` 与正文 1.7 | 保留 M3-07 NB-02：可在局部资料包中补充部分 DH ID 的就地定义或直接指向总论断台账 | 现有总来源账本和 M3-07 一手核验足以追溯，故不阻塞本次材料门控；软件动态接口仍须到 M8 冻结 |

## 9. 模式变更与授权边界专项判断

- **学习者证据门槛：已取消。** 主计划、路线、台账、门控模板、M3 门控简报、D-010 和根 README 均将 M3—M7 改为材料建设模式；`first_attempt_template.md:1-3` 已明确标记为历史停用文件，后续空白字段不构成缺失证据。
- **原验收强度：M3 范围内保持。** 自学检查题、综合对象图、关键错误一票否决、公式条件、来源边界、自动测试和失败样例均保留。取消本人提交没有删除任何既有 M3 知识节点。
- **M8 前外部实践：总体已禁止，但 B-01 尚未消除。** 主计划、D-010、未决事项和台账均禁止 DeepH 本体安装、正式数据下载、正式 DFT 标签和隐含实践选择；阶段 C 的一条后端练习仍与此冲突。
- **进入 M8 的暂停：明确。** M3—M7 完成后必须集中提交计算资源、DFT/数据后端、DeepH 软件对象、首个材料、时间/训练预算和高级物理范围的候选方案与推荐，由用户冻结。
- **M9 前再次授权：明确。** M8 冻结后，在 DeepH 正式安装、正式数据下载、正式标签生成或复现实验前必须再次取得用户明确执行授权。

## 10. 定点复核与状态判定

主 agent 应只修复 B-01、B-02 及其必要的交叉文档，不应以修复为理由缩减阶段 B—E 的知识范围、公式条件、来源边界或技术验证。修复后，独立子 agent 至少应：

1. 固定全部受影响文件的新 SHA-256；
2. 核对 M5 不再要求 M8 前选择或运行真实 DFT 后端，同时保留后端无关的 SCF 与收敛教学强度；
3. 从文档指定的 Python 3.12.13 环境按文档命令运行版本检查、10 项广义本征测试、3 项 Fourier 测试、默认 CLI、默认 JSON 和 `size=2` JSON；
4. 复核所有改动后的本地 Markdown 链接；
5. 确认 D-010 在八个管理文件中的语义无冲突，并且历史闭卷模板仍明确停用；
6. 明确给出“通过、无剩余 `BLOCKING`”或继续记录未关闭项。

在完成上述修复与独立定点复核前，**M3-08 应保持 `REVIEW`，M3 应保持 `IN_PROGRESS`，M4 应保持 `PLANNED`。** 只有定点复核明确通过、无剩余 `BLOCKING` 后，才允许把 M3-08 与 M3 标记为 `COMPLETED`，并把 M4 置为 `READY`。
