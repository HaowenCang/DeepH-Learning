# M3-07 阶段 A 独立内容与实现审计报告

## 1. 最终结论

**结论：有条件通过。当前不允许进入 M3-08。**

第 1 章正文的对象层级、原始 DeepH 的计算边界、广义厄米本征问题条件、基变换、Fourier 示例约定、旋转协变、误差传播和方法谱系总体正确；两轨道非正交模型的闭式谱、复数共轭、\(S\)-归一化、可逆基变换和等范数扰动反例也通过独立复算。固定 Python 环境中的 8 项自动测试全部通过，默认 CLI、JSON 输出、100 组多尺寸/多种子压力测试、1000 组随机复数两轨道复算及练习中的 Fourier 示例均得到预期结果。

本次审计记录 **4 项 `BLOCKING`**。其中一项是代码公开参数边界与实现不一致：`--size 2` 满足底层构造函数声明的最小维数，却因固定使用 `eigenvalue_index=2` 而崩溃；两项是编程题参考答案没有达到题面自行规定的可执行验收要求：P1 缺少闭式根与数值根的程序比较，P3 缺少相位约定不同步的失败测试及独立自动测试；另一项是进度台账在 M3-07 尚未通过时已把 M3-01—06 标为 `COMPLETED`，与主计划的统一完成定义和“不得把未审计产物标为 `COMPLETED`”规则直接冲突。这些问题均可局部修复，不要求重写正文或解析推导，因此结论为“有条件通过”而不是“不通过”；但在修复并由独立复核关闭全部 `BLOCKING` 前，不得开始 M3-08。

## 2. 审计范围与隔离声明

本次审计由独立子 agent 执行。审计直接检查：

- `03_textbook/chapters/01_deeph_problem/chapter.md`；
- `04_derivations/chapter1_two_orbital_nonorthogonal_model.md`；
- `05_code_exercises/chapter1_generalized_eigen/` 中固定依赖、实现、测试和说明；
- `06_exercises/01-deeph-problem/` 中全部 problem/solution 单元和综合门控题；
- `00_scope/master_execution_plan.md`、`03_textbook/chapters/01_deeph_problem/outline.md`、`03_textbook/notation.md`、`02_source_ledger/claims_and_sources.md`、`03_textbook/chapters/01_deeph_problem/sources.md`；
- 为核对状态纪律而读取 `08_audits/progress_tracker.md`；
- 原始 DeepH 的本地论文/补充材料哈希，以及原始论文和当前方法/软件的一手官方页面。

未把既有 M2-I 审计结论当作 M3-07 的通过证据；既有报告只用于识别历史门控结构。没有修改教材、提纲、推导、代码、测试、练习、来源账本、主计划或进度台账。工作区不是 Git 仓库，因而不能用 `git diff` 证明隔离；本次项目内容写入仅限本报告。所有数值复算均使用合成矩阵或题面内嵌样例，不安装 DeepH、不下载正式训练数据、不选择材料、DFT 后端或实践软件版本。

## 3. 输入文件 SHA-256

### 3.1 主体、计划与来源文件

| 文件 | SHA-256 |
|---|---|
| `00_scope/master_execution_plan.md` | `C2E21E678A4EDDD2F978BF3D035DC01C3D4597772D38373D3182C37108B3FA1E` |
| `03_textbook/chapters/01_deeph_problem/outline.md` | `A5DFB8EE0EECA55066DB48E35FBEFD9128C22C17631B09656470ECD5887DCC16` |
| `03_textbook/chapters/01_deeph_problem/chapter.md` | `9885BAB3EC2931DDCEBB086F81E6354E8806F136FC289BC6B3172E7F6B335539` |
| `03_textbook/notation.md` | `90FF3A130600FB68CB71FCA781B29A8D5B600D3C26219D369EA50B324426160E` |
| `02_source_ledger/claims_and_sources.md` | `1B85F724E85E178500CDB15376E7953F8E787467C0F6AF448CEFA0E2499696D5` |
| `03_textbook/chapters/01_deeph_problem/sources.md` | `ED18BF3CA57F4B19F1101FBA3936EE1E04EA8ADFA4F08D6E7ED98D4FFAEA5E62` |
| `04_derivations/chapter1_two_orbital_nonorthogonal_model.md` | `4FC6FF9A8ED922763E554063BBCB0C10C50467B98342064C3ED6F3CDD3708F8B` |
| `08_audits/progress_tracker.md` | `45D34716B7035DBE12932240861005FEF5B58CAB48D1F4EECE71C8057AD0D670` |
| `01_sources/papers/li_et_al_2022_deeph.pdf` | `92C5A783B46475634A17D2D5F6557D8DE68D2F789F8DFB66182F56862580EC61` |
| `01_sources/supplements/li_et_al_2022_deeph_supplement.pdf` | `2D561F9FA7132C2EF11615DED1CB63C84AC3AF3950985FE4A7BB363A2C54E368` |

### 3.2 代码练习文件

| 文件 | SHA-256 |
|---|---|
| `05_code_exercises/chapter1_generalized_eigen/requirements.txt` | `CC3EFBCD187C80ADDD5DB987EE90AD17BD481814985761D7B5CFAC3F0B5E10E4` |
| `05_code_exercises/chapter1_generalized_eigen/README.md` | `BDDC68A7D3C535294E082FFFF2F560752ED51621E43445B79457F9C94BBE3526` |
| `05_code_exercises/chapter1_generalized_eigen/experiment.py` | `D84B18DD590BEBD382DEC29AD5C4ABD784997737851FB4D773D7F680444283A6` |
| `05_code_exercises/chapter1_generalized_eigen/test_experiment.py` | `B01202A8DDB23AD0F7FA58A3805449A42AE5BA217362ED2BE8602B3B595FE32B` |

### 3.3 练习与参考答案文件

| 文件 | SHA-256 |
|---|---|
| `06_exercises/01-deeph-problem/README.md` | `9B31B368376436EB8B6FF23DB8AD167A55CC6462A89EC019B3D0DC43EF592C96` |
| `01.01-object-and-workflow-basics/problem/readme.md` | `2021169AEE3CFF683C0001FB1DB66705DE4EA93394E7CEDE0A716485B3930822` |
| `01.01-object-and-workflow-basics/solution/readme.md` | `58A65E9350357430565150CDF4F2D319E5C33B9D9512375B71B70208750121FC` |
| `01.02-core-derivations/problem/readme.md` | `5B6AB1F0937ABD1FD63B949E3700D4836DC4BEBE7949F6E92EA23FD3F56DC035` |
| `01.02-core-derivations/solution/readme.md` | `BB89A65F361806D8CF6FF893A49A4010DE6B7DDA0746A8E991356EF97F9BA698` |
| `01.03-numerical-programming/problem/readme.md` | `C3C9A486D45ED0CFD588258683A615A983422A57B7525DDAA8289A9DD02762D7` |
| `01.03-numerical-programming/solution/readme.md` | `CD796BD3EB99B7F46BBD291BA7D8AA1306508B76C31E2070539163D043FEAA8E` |
| `01.04-research-comparison/problem/readme.md` | `9E83489C61E7D1D0B77E0717ADF34DE72FC65FA338E24239093A582C68A0770D` |
| `01.04-research-comparison/solution/readme.md` | `FFF397982781B45CCFF7214B926C7761C3EC2559D57D8E5BF2899ED77FC458F0` |
| `01.05-end-to-end-object-graph-gate/problem/readme.md` | `62B35C7FF40CDFDDA8A2821464023823D5EB0CCAC3B9CFEF432C140507B67CD3` |
| `01.05-end-to-end-object-graph-gate/solution/readme.md` | `63E070A3A2642EF374050B23497398AAB4492C88AE2BF83607641478BB7E9AF6` |

## 4. 复现环境、命令与输出摘要

### 4.1 固定环境

使用解释器：

```text
C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
Python 3.12.13
NumPy 2.3.5
SciPy 1.18.0
```

实际版本与 `requirements.txt` 和代码练习 README 一致。

### 4.2 自动测试、CLI 与编译检查

执行：

```powershell
$py = 'C:\Users\20659\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -m unittest discover -s 05_code_exercises/chapter1_generalized_eigen -p "test_*.py" -v
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --format json
& $py -m py_compile 05_code_exercises/chapter1_generalized_eigen/experiment.py 05_code_exercises/chapter1_generalized_eigen/test_experiment.py
```

结果：8 项测试全部 `ok`，`Ran 8 tests in 0.012s`，最终为 `OK`；JSON 可由 PowerShell `ConvertFrom-Json` 解析，元数据为 seed `20260803`、size `6`、NumPy `2.3.5`、SciPy `1.18.0`；两份 Python 文件编译检查通过。默认 CLI 的核心指标如下：

| 指标 | 输出 |
|---|---:|
| 最大归一化广义本征残差 | `2.052642e-16` |
| \(S\)-正交 Frobenius 残差 | `1.930810e-15` |
| \(\kappa_2(S)\) | `1.000000e+01` |
| 一致基变换最大谱差 | `1.110223e-16` |
| 两个扰动的 Frobenius 范数 | 均为 `2.000000e-02` |
| 低能方向目标位移 | `8.889209e-03` |
| 高能正交方向目标位移 | `-1.110223e-16` |
| 一阶余项，步长依次减半 | `6.788903e-08`、`1.697828e-08`、`4.245323e-09` |
| 只变换 \(H\) 的最大谱差 | `2.067246e+00` |
| 非正定 \(S\) | 被拒绝 |

### 4.3 独立数学复算

另写只读内存脚本，不调用项目中的闭式根实现，因为项目代码没有该实现。对 1000 组随机复数两轨道模型独立计算二次公式、`scipy.linalg.eigh`、解析本征矢残差和非幺正基变换谱差，得到：

| 检查 | 最大误差 |
|---|---:|
| 闭式根与 SciPy 广义本征值 | `1.0658141036401503e-14` |
| 解析本征矢广义残差 | `1.2045919817182948e-14` |
| 一致非幺正基变换前后谱差 | `2.2737367544323206e-13` |

对 `run_experiment` 执行 size `3,4,6,8`、每个维数 25 个种子，共 100 次压力运行，最大归一化残差为 `7.120602493819218e-16`，最大 \(S\)-正交残差为 `3.8578684877577465e-15`，最大基变换谱差为 `1.1102230246251565e-15`，一阶余项比例相对 4 的最大偏差为 `0.14270912862555374`。这些结果支持默认实现和 size 不小于 3 的当前路径。

练习 P3 的离散 Fourier 示例独立复算得到最大 \(k\) 空间厄米残差 `4.4019612280171296e-16`，最大反变换重建误差 `1.8427303745251896e-16`。

### 4.4 结构和链接检查

共扫描 16 个相关 Markdown 文件、25 个 Markdown 链接，其中 15 个为本地链接；断链数为 0。题量按标题统计为基础题 5、推导题 5、编程题 3、研究讨论题 2，并另有综合门控题 1；题量符合主计划和提纲。

### 4.5 反例命令

执行：

```powershell
& $py 05_code_exercises/chapter1_generalized_eigen/experiment.py --size 2 --format json
```

结果退出码为 1，回溯定位到 `experiment.py:385` 调用 `first_order_remainders`，随后在 `experiment.py:209` 抛出 `ValueError: eigenvalue_index is out of range`。该结果构成 B-01 的直接复现证据。

## 5. 一手来源核验与证据边界

本次于 2026-08-03 重新核对一手页面：

- [原始 DeepH 论文](https://www.nature.com/articles/s43588-022-00265-6)明确把任务定义为结构到 DFT Hamiltonian 的学习，并在 Methods 式 (7)—(9)区分 \(H\)、由基函数内积得到的 \(S\)、Fourier 变换及后续广义本征求解；正文没有把网络预测解释为省略全部下游步骤。
- [DeepH-E3](https://www.nature.com/articles/s41467-023-38468-8)支持轨道 Hamiltonian 的显式 \(E(3)\) 等变表示边界。
- [DeepH-2 预印本](https://arxiv.org/abs/2401.17015)仍支持“equivariant local-coordinate transformer”和边方向局域轴的表述；正文已明确其主要证据仍为预印本，未把报告复杂度外推为普遍实际速度。
- [现代 DeepH-pack 论文](https://www.nature.com/articles/s41524-026-02219-2)显示正式发表日期为 2026-07-09，并把软件定位为统一的第一性原理—深度学习包；正文没有用软件论文证明全部方法均已公开实现。
- [DeepH-dock 官方文档](https://docs.deeph-pack.com/deeph-dock/en/latest/)把其定位为 DFT 接口、标准化数据和独立后处理平台；[现代数据准备文档](https://docs.deeph-pack.com/deeph-pack/en/latest/core_workflows/data_preparation.html)明确现代数据布局和当前后端边界。正文把它与 Hamiltonian 学习网络区分开是正确的。
- [DeepH-R 的 PRL 页面](https://journals.aps.org/prl/abstract/10.1103/mbhs-vlby)显示 PRL 137, 046401，发表于 2026-07-20，并明确把学习目标改为旋转不变、无 AO 基依赖的实空间 Kohn–Sham 势。正文同时保留网格、势到矩阵、\(S\) 和后处理依赖，没有作“整个计算链基组无关”的错误外推。

动态软件接口在 M8 仍需冻结版本和最小样例。现有来源只支持第 1 章的角色边界，不支持推断任意后端、任意数据格式或全部论文方法已经可复现。

## 6. 逐域判定表

| 审计域 | 判定 | 主要证据与边界 |
|---|---|---|
| 正文对象层级 | 通过 | `chapter.md:15-25, 98-223` 区分 KS 算符、参考矩阵、监督标签、预测矩阵、\(S\)、本征量和进一步物理量；没有把 KS 本征值等同总能量 |
| “跳过 SCF”边界 | 通过 | `chapter.md:44-96, 261-343` 明确只近似替代新结构的 Hamiltonian 标签生成路径，保留 \(S\)、组装、Fourier、求解、占据、后处理及摊销成本 |
| 正文公式条件 | 通过 | `chapter.md:117-201, 355-412, 441-467` 给出厄米性、\(S\succ0\)、\(S\)-归一化、可逆同子空间基变换、示例 Fourier 约定、旋转约定边界、简单特征值和小扰动条件 |
| 物理适用边界 | 通过 | `chapter.md:225-259, 345-420, 422-501` 对局域性、金属性、杂化泛函、截断、数据泄漏、近简并、病态 \(S\) 和下游指标均有限定 |
| 方法与软件对象层级 | 通过 | `chapter.md:503-562` 正确区分 DeepH、DeepH-E3/2、xDeepH、hybrid、DFPT、HPRO、Zero、R、pack/dock；没有跨论文直接排序精度或速度 |
| 来源映射 | 通过，附建议 | 原始 DeepH、现代 pack/dock、DeepH-R 等关键结论均可回到一手来源或 `CLM-001`—`CLM-014`；但 `sources.md` 对部分 DH ID 的就地定义不完整，见 NB-02 |
| 两轨道解析模型 | 通过 | 二次方程、\(|s|<1\)、条件数、复数共轭、本征矢、基变换行列式和等范数投影均正确；1000 组随机复算通过 |
| 代码默认路径 | 通过 | 固定依赖与实际环境一致；8 项测试、CLI、JSON、编译、100 次压力运行通过；残差、正交性、谱不变、一阶余项和失败样例解释正确 |
| 代码输入边界 | **未通过，`BLOCKING`** | `--size 2` 可复现崩溃，见 B-01 |
| 练习题量与基础/推导/讨论答案 | 通过 | 5+5+2 题及综合门控题 problem/solution 对应，关键对象和公式答案正确；综合题覆盖训练链、推理链、方法定位和一票否决规则 |
| 编程题参考答案完整性 | **未通过，2 项 `BLOCKING`** | P1 未给可执行闭式根比较；P3 未给题面要求的相位不同步失败测试和自动测试，见 B-02、B-03 |
| 本地链接 | 通过 | 15 个本地链接全部存在，无断链 |
| 主计划与台账状态一致性 | **未通过，`BLOCKING`** | 主计划 `master_execution_plan.md:20, 297-304` 与 `progress_tracker.md:65-71` 的状态冲突，见 B-04 |

## 7. `BLOCKING` 列表

### B-01：`--size 2` 的公开输入边界与实现不一致

**位置。** `05_code_exercises/chapter1_generalized_eigen/README.md:36` 声明 `--size` 可以改变合成问题；`experiment.py:109-120` 明确允许 `size >= 2`；`experiment.py:385-391` 却固定使用 `eigenvalue_index=2`，而 `first_order_remainders` 在 `experiment.py:207-213` 对 size 2 判为越界。

**机制。** size 2 仅有索引 0、1。`run_experiment` 的其他部分可以使用 size 2，但一阶余项检查无条件访问第三个本征值，造成 CLI 在完成前异常退出。

**影响。** 当前默认 size 6 的结果仍有效，但“`--size` 可以改变”的可复现接口存在未声明的失败边界，且 8 项测试没有覆盖最小允许维数。M3-05 因而不能视为完成全部公开输入契约。

**最小修复验收标准。** 二选一：

1. 使 `run_experiment(size=2)` 和 CLI `--size 2` 正常完成，并为一阶检查选择合法、简单且间隙充分的索引；或
2. 把整个公开接口统一收紧为 `size >= 3`，在 CLI 参数校验、`make_problem`/`run_experiment` 和 README 同步说明，并以可读的参数错误拒绝 size 2，而不是运行中回溯。

无论采用哪种方案，都应新增自动测试覆盖最小支持维数和最小不支持维数，并重新运行 8 项既有测试、默认 CLI 和 JSON 契约。

### B-02：P1 参考答案缺少题面要求的闭式根—数值根可执行比较

**位置。** `06_exercises/01-deeph-problem/01.03-numerical-programming/problem/readme.md:3-14` 要求每题提交固定种子或显式矩阵、运行命令、自动测试、失败样例和结果解释，并在 P1 明确要求“比较闭式根与数值广义本征值”。`solution/readme.md:3-20` 只链接解析模型和通用随机矩阵代码；`05_code_exercises/chapter1_generalized_eigen/experiment.py` 与测试中没有两轨道闭式根实现或比较测试。

**机制。** 解析文档给出了公式与一个固定数值结果，通用代码只调用 SciPy 求解随机 \(n\times n\) 问题。二者组合仍没有一段可执行证据证明闭式根实现与广义本征求解器一致，因而不能满足 P1 自己规定的编程交付格式。

**影响。** 解析公式本身经本次独立复算正确，但学生参考答案和项目自动检查无法重建该验证；`progress_tracker.md:70` 所称“参考解答及验证通过”在 P1 上证据不足。

**最小修复验收标准。** 在 P1 参考实现或相应代码测试中加入：显式复数两轨道 \(H,S\)；\(|s|<1\) 校验；二次闭式根；`scipy.linalg.eigh(H,S)`；两组根在声明容差内一致；非幺正一致基变换谱不变；至少一个 \(|s|\ge1\) 或只变换 \(H\) 的失败测试。给出固定输入、运行命令和测试输出。

### B-03：P3 缺少题面明确要求的相位不同步失败测试和自动测试

**位置。** `01.03-numerical-programming/problem/readme.md:20-27` 要求四项测试，其中最后一项是“改变正反变换相位约定但未同步修改时，重建或定位测试必须失败”；该文件第 3 行还要求每题有自动测试。`solution/readme.md:22-67` 的参考代码只验证正确正反变换和删除 \(H(-R)=H(R)^\dagger\) 配对后的 Hermiticity 失败，没有相位不同步反例；项目测试套件也不包含 Fourier 测试。

**机制。** 现有代码证明了一个正确离散 Fourier 对和一个缺共轭块的失败情形，但没有证明测试能够捕获正、反变换指数符号未同步的常见错误。题面明确要求的第四项验收不存在。

**影响。** P3 的正确示例经本次复算成立，但参考答案与自动测试覆盖不完整；无法据此判定学习者已理解相位约定必须成对一致。

**最小修复验收标准。** 把 P3 参考实现置于可执行文件或测试中，固定 `n_k` 与显式矩阵；自动验证 \(k\) 空间 Hermiticity、反变换重建、缺共轭配对失败，以及正/反相位未同步时重建或平移定位测试失败。运行命令应能独立得到测试通过记录。

### B-04：台账把尚未通过独立审计的 M3-01—06 提前标为 `COMPLETED`

**位置。** `00_scope/master_execution_plan.md:20-27` 规定 `COMPLETED` 需要交付物、可重复验证、自测和明确通过的门控记录；`master_execution_plan.md:297-304` 明确规定不得把未审计产物标为 `COMPLETED`。`08_audits/progress_tracker.md:65-70` 在 M3-07 仍为 `IN_PROGRESS`、M3-08 尚未进行时把 M3-01—06 全部标为 `COMPLETED`。

**机制。** 台账把“交付物已形成/主 agent 自检通过”与统一状态定义中的“审计和门控通过”混为同一状态。M3-07 当前又存在 B-01—B-03，更不能把相关代码和练习任务维持为已经完成全部验收。

**影响。** 状态不能准确表达审计风险，后续 agent 可能据此跳过修复或提前开始 M3-08；这直接违反主计划的变更和完成定义。

**最小修复验收标准。** 在独立复核通过前，把受审计约束的 M3-01—06 调整为 `REVIEW`，或在主计划中经正式变更明确区分“产物完成”和“审计完成”的不同任务状态；不得静默改变统一状态含义。B-01—B-03 关闭且定点复核明确“通过”后，方可把对应任务恢复为 `COMPLETED` 并把 M3-08 置为 `READY`。

## 8. `NON_BLOCKING` 建议

| 编号 | 文件与位置 | 建议 | 理由 |
|---|---|---|---|
| NB-01 | `05_code_exercises/chapter1_generalized_eigen/README.md:15-25`、`requirements.txt` | 除包版本外，增加可重建环境文件或至少记录解释器来源/架构和依赖文件哈希 | 当前环境已经固定且可复现，但单一 `requirements.txt` 不约束 Python 小版本和平台轮子；这不影响本次默认结果 |
| NB-02 | `03_textbook/chapters/01_deeph_problem/sources.md:15-24, 38-49`；`chapter.md:517-562` | 在资料包中就地增加 DH-03、DH-04、DH-05、DH-06、DH-09 的定义，或把正文谱系段直接映射到 CLM-003、004、005、007、009 | 论断在总来源账本中有一手来源，故不构成来源缺失；但 `sources.md` 单独阅读时部分 DH ID 未定义，追溯需要跨文件猜测 |
| NB-03 | `experiment.py:81-106`、代码 README 的门槛说明 | 明确“归一化残差”的分母采用 `max(scale, 1)`，并说明这是绝对/相对混合尺度，不是唯一标准后向误差 | 当前阈值和结果充分小，不影响通过；写明定义可防止将其机械用于不同量纲或整体缩放的问题 |
| NB-04 | `06_exercises/01-deeph-problem/01.05-end-to-end-object-graph-gate/solution/readme.md:48-60` | 在实际 M3-08 门控表中恢复题面模板的“输入节点类型/输出节点类型”独立列，不只合并写“输入与输出” | 参考图和文字已覆盖类型要求，故不阻塞；独立列更便于一票否决式审查 |

## 9. M3-08 进入判定

**当前不允许进入 M3-08。** 解除限制需要同时满足：

- 修复 B-01，并以新增边界测试证明 CLI 与实现契约一致；
- 修复 B-02、B-03，使三道编程题的参考答案均满足固定输入、命令、自动测试、失败样例和结果解释要求；
- 按 B-04 恢复状态纪律；
- 由未实施修复的独立审计者执行定点复核，重新固定受影响文件哈希并明确给出“通过、无剩余 `BLOCKING`”结论；
- 在 `progress_tracker.md` 中记录复核证据后，方可把 M3-07 标为 `COMPLETED`、M3-08 标为 `READY`。

本次无需重审已通过的正文对象图和两轨道解析公式；定点复核范围可限制为受 B-01—B-04 影响的代码、测试、编程题参考答案、状态台账及其链接和命令输出。
